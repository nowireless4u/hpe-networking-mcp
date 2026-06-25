"""Shared Central call-emitter helpers for the canonical config writers.

Every non-WLAN config kind (vlan / role / net_group / policy / the AAA chain /
gateway_cluster) places a single Library object at a single Central ``scope_id``
via one of three call shapes. These helpers centralize those shapes so each
per-kind writer stays small and the config-assignment / LOCAL-override packing is
defined once (matching the validated old-engine output):

* ``create_call`` — SHARED Library create: ``POST /<type>/{name}`` (no scope query).
* ``config_assignment_call`` — make a Library object effective: ``POST
  /config-assignments`` with one array entry per device-function (packed shape).
* ``local_call`` — LOCAL override at a scope: ``POST /<type>/{name}`` with
  ``object-type=LOCAL`` + ``scope-id`` + ``device-function`` query params
  (named_vlan step-6 alias override + the gateway-cluster dual objects).

Writers receive their placement context as keyword args off ``writer_ctx``:
``scope_id`` (the resolved Central scope-id, or ``None`` when the skill couldn't
resolve it) and ``device_functions`` (defaults per kind, operator-overridable).
A ``None``/unresolved ``scope_id`` is surfaced via the call's ``unresolved`` flag
so ``orchestrator.execute`` blocks before any write — same guard the WLAN writer
uses.
"""

from __future__ import annotations

from typing import Any

_BASE = "network-config/v1alpha1"
CONFIG_ASSIGNMENTS = f"{_BASE}/config-assignments"

# Default device-function set per kind. VLANs land on both the gateway and the
# AP; every other config kind is gateway-terminated (MOBILITY_GW only). The
# validated target JSONs set these in ``target_meta.device_functions``.
DEFAULT_DEVICE_FUNCTIONS = ["MOBILITY_GW"]
VLAN_DEVICE_FUNCTIONS = ["MOBILITY_GW", "CAMPUS_AP"]


def path_for(type_path: str, name: str | int) -> str:
    """Full Central object path for ``type_path`` + object ``name``."""
    return f"{_BASE}/{type_path}/{name}"


def create_call(
    type_path: str,
    name: str | int,
    body: dict[str, Any],
    *,
    depends_on: list[int] | None = None,
    purpose: str | None = None,
    unresolved: dict[str, str] | None = None,
) -> dict[str, Any]:
    """A SHARED Library create — ``POST /<type_path>/{name}`` with no scope query.

    Central adds the named object to the Library; it broadcasts/applies nowhere
    until a matching ``config_assignment_call`` makes it effective at a scope.
    """
    call: dict[str, Any] = {
        "method": "POST",
        "path": path_for(type_path, name),
        "query": {},
        "body": body,
        "purpose": purpose or f"Create Central {type_path} '{name}' (library)",
        "depends_on": list(depends_on or []),
    }
    if unresolved is not None:
        call["unresolved"] = unresolved
    return call


def config_assignment_call(
    profile_type: str,
    profile_instance: str | int,
    scope_id: str | None,
    device_functions: list[str],
    *,
    depends_on: list[int] | None = None,
    kind: str | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """Make a Library object effective at a scope — one entry per device-function.

    All device-functions are packed into a single ``config-assignment`` array on
    one POST (the validated shape). ``scope_id`` of ``None`` (the skill could not
    resolve the scope) sets ``unresolved`` so execution blocks rather than
    posting an assignment with a null scope.
    """
    body = {
        "config-assignment": [
            {
                "scope-id": scope_id,
                "device-function": df,
                "profile-type": profile_type,
                "profile-instance": str(profile_instance),
            }
            for df in device_functions
        ]
    }
    return {
        "method": "POST",
        "path": CONFIG_ASSIGNMENTS,
        "query": {},
        "body": body,
        "purpose": f"Assign '{profile_instance}' ({profile_type}) to scope {scope_id or '<unresolved>'}",
        "depends_on": list(depends_on or []),
        "unresolved": None if scope_id else {"kind": kind or profile_type, "name": name or str(profile_instance)},
    }


def local_call(
    type_path: str,
    name: str | int,
    body: dict[str, Any],
    scope_id: str | None,
    device_function: str,
    *,
    depends_on: list[int] | None = None,
    purpose: str | None = None,
    kind: str | None = None,
) -> dict[str, Any]:
    """A LOCAL override at a scope — ``POST /<type>/{name}?object-type=LOCAL&...``.

    The scope-id + device-function ride in the query (not a config-assignment
    array) — Central's LOCAL-override path. Used by the named-VLAN alias override
    and the gateway-cluster dual objects.
    """
    return {
        "method": "POST",
        "path": path_for(type_path, name),
        "query": {
            "object-type": "LOCAL",
            "scope-id": scope_id,
            "device-function": device_function,
        },
        "body": body,
        "purpose": purpose or f"LOCAL override of {type_path} '{name}' at scope {scope_id or '<unresolved>'}",
        "depends_on": list(depends_on or []),
        "unresolved": None if scope_id else {"kind": kind or type_path, "name": str(name)},
    }
