"""Aruba Central Roles & Policy shared CRUD helpers.

This module is now **helpers-only**. The CRUD tool surface for the
security-policy stack (net-groups, net-services, object-groups,
role-ACLs, policies, policy-groups, role-GPIDs, roles) is owned by the
generated modules (``security.py``, ``roles_policy.py``, …), which all
import the shared ``_get_resource`` / ``_manage_resource`` helpers and
field constants defined here.

Keep this file import-stable: the generated modules depend on the
helper signatures and ``_*_FIELD`` constants below.

All resources use the same CRUD pattern at /network-config/v1alpha1/.
"""

from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command

# ---------------------------------------------------------------------------
# Shared config-read query parameters
#
# Every /network-config/v1alpha1/ GET endpoint documents the same eight query
# parameters. They are defined once here so each read tool advertises an
# identical, accurate schema. Descriptions come from the vendored OpenAPI spec.
#
# These are distinct from the write-side _SCOPE_ID_FIELD / _DEVICE_FUNCTION_FIELD
# below: on a write, scope_id selects where an object is *created*; on a read it
# selects which scope's configuration is *returned*.
# ---------------------------------------------------------------------------

_READ_VIEW_TYPE_FIELD = Field(
    description=(
        "'LOCAL' — configuration for a scope and one or more device functions "
        "(requires scope_id). 'LIBRARY' — shared objects in the library; for "
        "LIBRARY every other parameter except 'detailed' is ignored. "
        "Omit to use the API default."
    ),
    default=None,
)
_READ_OBJECT_TYPE_FIELD = Field(
    description=(
        "Retrieve 'LOCAL' or 'SHARED' configuration objects. Omit for both (the API default). "
        "This filters which objects come back — it does not select the scope; use scope_id for that."
    ),
    default=None,
)
_READ_SCOPE_ID_FIELD = Field(
    description=(
        "Return configuration at this scope ID. Mandatory when view_type='LOCAL'. "
        "Get scope IDs from central_get_scope_tree."
    ),
    default=None,
)
_READ_DEVICE_FUNCTION_FIELD = Field(
    description=(
        "Filter configuration to this device-function type. If omitted when "
        "view_type='LOCAL', the API defaults to all device functions. "
        "Valid: CAMPUS_AP, ACCESS_SWITCH, BRANCH_GW, MOBILITY_GW, CORE_SWITCH, AGG_SWITCH, ALL."
    ),
    default=None,
)
_READ_EFFECTIVE_FIELD = Field(
    description=(
        "True — return effective (hierarchically merged / inherited) configuration. "
        "False — return only the configuration committed at this scope."
    ),
    default=None,
)
_READ_DETAILED_FIELD = Field(
    description=(
        "True — annotate each returned object with its object type, scope, and device "
        "function. Useful when walking a scope hierarchy."
    ),
    default=None,
)
_READ_LIMIT_FIELD = Field(
    description="Pagination limit. Omit to use the API default page size.",
    default=None,
)
_READ_OFFSET_FIELD = Field(
    description="Pagination offset.",
    default=None,
)

# ---------------------------------------------------------------------------
# Factory helpers — avoid repeating the same CRUD logic across resources
# ---------------------------------------------------------------------------


def build_config_read_params(
    *,
    view_type: str | None = None,
    object_type: str | None = None,
    scope_id: str | None = None,
    device_function: str | None = None,
    effective: bool | None = None,
    detailed: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict:
    """Build the kebab-case query dict for a network-config/v1alpha1 GET.

    Shared by ``_get_resource`` and the hand-curated config readers that can't
    delegate to it (composite fetchers that collect per-resource errors instead
    of raising). Keeping the rules here means the two upstream quirks below are
    enforced once rather than re-derived per tool.

    Both quirks were confirmed against the live API, which **ignores** unknown
    or incomplete query params rather than erroring — so getting either wrong
    fails silently with plausible-looking data:

    * ``limit`` is only honored when ``offset`` is also sent. On its own it is
      ignored and the full collection comes back, so a caller who asked for a
      page silently receives everything. A ``limit`` without an ``offset``
      therefore defaults the offset to 0.
    * ``view_type='LOCAL'`` without a ``scope_id`` returns *another* scope's
      configuration instead of failing, so it is rejected.

    Returns:
        Query params with ``None`` values omitted, so the API's own defaults
        apply for anything the caller didn't ask for.

    Raises:
        ToolError: 400 when ``view_type='LOCAL'`` is given without ``scope_id``.
    """
    if view_type and view_type.upper() == "LOCAL" and not scope_id:
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    "view_type='LOCAL' requires scope_id — without it the API returns "
                    "a different scope's configuration instead of failing."
                ),
            }
        )

    if limit is not None and offset is None:
        offset = 0

    params = {
        "view-type": view_type,
        "object-type": object_type,
        "scope-id": scope_id,
        "device-function": device_function,
        "effective": effective,
        "detailed": detailed,
        "limit": limit,
        "offset": offset,
    }
    return {k: v for k, v in params.items() if v is not None}


def build_config_write_params(
    *,
    object_type: str | None = None,
    scope_id: str | None = None,
    device_function: str | None = None,
) -> dict:
    """Build the kebab-case query dict for a network-config/v1alpha1 write.

    The OAS documents three scope-selecting query params on every config
    POST/PATCH/DELETE:

    * ``object-type`` — ``LOCAL`` creates a scoped object, ``SHARED`` creates a
      library object. The API defaults to ``SHARED`` when omitted.
    * ``scope-id`` / ``device-function`` — **mandatory** for ``LOCAL`` and must
      **not** be supplied for ``SHARED``.

    Enforced here so every write tool behaves identically and the two footguns
    the old inline logic had are closed (the API silently ignores bad/partial
    query params, so both used to fail silently):

    * It hardcoded ``object-type=LOCAL`` and only sent scope params when *both*
      ``scope_id`` and ``device_function`` were present — so ``SHARED`` was
      unreachable and passing only one of the pair silently dropped both,
      landing the write at the wrong scope.

    Backward-compatible: a caller that passes ``scope_id``/``device_function``
    without an explicit ``object_type`` still gets a ``LOCAL`` write, matching
    the prior behavior.

    Returns:
        Query params with ``None`` omitted (empty dict → the API's ``SHARED``
        default applies).

    Raises:
        ToolError: 400 for ``LOCAL`` without both scope params, ``SHARED`` with
            either scope param, or an unrecognized ``object_type``.
    """
    ot = object_type.upper() if object_type else None
    # Infer LOCAL when a scope is given without an explicit object_type.
    if ot is None and (scope_id or device_function):
        ot = "LOCAL"

    if ot is None:
        return {}  # API default: SHARED (library object)

    if ot == "LOCAL":
        if not (scope_id and device_function):
            raise ToolError(
                {
                    "status_code": 400,
                    "message": (
                        "object_type='LOCAL' requires both scope_id and device_function "
                        "(supplying only one silently lands the write at the wrong scope). "
                        "Get scope IDs from central_get_scope_tree."
                    ),
                }
            )
        return {"object-type": "LOCAL", "scope-id": scope_id, "device-function": device_function}

    if ot == "SHARED":
        if scope_id or device_function:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": (
                        "object_type='SHARED' creates a library object and must not be given "
                        "with scope_id or device_function (those select a LOCAL scope)."
                    ),
                }
            )
        return {"object-type": "SHARED"}

    raise ToolError(
        {"status_code": 400, "message": f"Invalid object_type {object_type!r}: expected 'LOCAL' or 'SHARED'."}
    )


async def _get_resource(
    ctx: Context,
    api_base: str,
    name: str | None,
    *,
    view_type: str | None = None,
    object_type: str | None = None,
    scope_id: str | None = None,
    device_function: str | None = None,
    effective: bool | None = None,
    detailed: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict | list | str:
    """Generic GET for /network-config/v1alpha1/{api_base}[/{name}].

    The keyword-only arguments map to the query parameters documented on every
    ``network-config/v1alpha1`` GET endpoint; see
    :func:`build_config_read_params` for how they're normalized.

    Raises:
        ToolError: 400 when ``view_type='LOCAL'`` is requested without a
            ``scope_id``; the upstream status when the GET itself fails.
    """
    api_params = build_config_read_params(
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )

    conn = get_central_conn(ctx)
    api_path = f"network-config/v1alpha1/{api_base}/{path_seg(name)}" if name else f"network-config/v1alpha1/{api_base}"
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=api_path,
        api_params=api_params or None,
    )
    code = response.get("code", 0)
    if code and not 200 <= code < 300:
        raise ToolError(
            {"status_code": code or 502, "message": f"GET {api_path} failed: {response.get('msg', 'Unknown error')}"}
        )
    return response.get("msg", {})


async def _manage_resource(
    ctx: Context,
    api_base: str,
    resource_label: str,
    name: str | None,
    action_type: str,
    payload: dict,
    scope_id: str | None,
    device_function: str | None,
    confirmed: bool,
    *,
    object_type: str | None = None,
) -> dict | str:
    """Generic POST/PATCH/DELETE for /network-config/v1alpha1/{api_base}[/{name}].

    When ``name`` is ``None`` or empty, the URL omits the trailing
    ``/{name}`` segment so singleton config objects (e.g. ``system-info``,
    ``firmware-compliance``) can use the same helper.

    ``object_type`` / ``scope_id`` / ``device_function`` select where the object
    is written; see :func:`build_config_write_params` for the LOCAL/SHARED rules.
    ``object_type`` is keyword-only so existing positional callers keep working.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type: {action_type}. Must be 'create', 'update', or 'delete'.",
            }
        )

    method_map = {"create": "POST", "update": "PATCH", "delete": "DELETE"}
    api_method = method_map[action_type]
    api_path = f"network-config/v1alpha1/{api_base}/{path_seg(name)}" if name else f"network-config/v1alpha1/{api_base}"

    conn = get_central_conn(ctx)

    api_params = build_config_write_params(object_type=object_type, scope_id=scope_id, device_function=device_function)

    api_data = payload if action_type != "delete" else None

    logger.info("Central {}: {} '{}' — path: {}", resource_label, api_method, name, api_path)

    response = await retry_central_command(
        central_conn=conn,
        api_method=api_method,
        api_path=api_path,
        api_data=api_data,
        api_params=api_params if api_params else None,
    )

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "action": action_type, "name": name, "data": response.get("msg", {})}

    msg = response.get("msg", "Unknown error")
    raise ToolError({"status_code": code or 502, "message": f"{action_type} {resource_label} {name!r} failed: {msg}"})


async def _operation_request(
    ctx: Context,
    api_method: str,
    api_path: str,
    payload: dict | None = None,
    confirmed: bool = False,
    label: str = "",
) -> dict | str:
    """Generic single-shot request for an irregular Central operation endpoint.

    Unlike :func:`_manage_resource`, this helper targets a fully-formed
    ``api_path`` (the caller has already substituted any path params and chosen
    the version prefix) and a fixed ``api_method`` — there is no
    ``action_type``/CRUD verb mapping. Used by the generated operation tools
    (fixed-verb actions like ``revoke``/``upload``/``import``/``export``/``bulk``
    and job/status reads).

    Confirmation is handled by the universal gate at the invoke-tool dispatch
    chokepoint (``confirmed`` is the fallback flag passed through by callers).
    Returns ``{"status": "success", ...}`` on 2xx; raises :class:`ToolError`
    (``{"status_code", "message"}``) on any non-2xx so the calling AI sees a
    real failure rather than an ok-wrapped error dict.
    """
    method = api_method.upper()
    is_write = method in ("POST", "PATCH", "PUT", "DELETE")

    conn = get_central_conn(ctx)
    # Send the request body for any write method that carries one. Unlike CRUD
    # ``_manage_resource`` (which never bodies a delete), operation endpoints
    # such as ``.../bulk`` are DELETEs whose payload (``{"items": [...]}``)
    # selects the targets, so DELETE bodies must pass through when supplied.
    api_data = payload if is_write else None

    logger.info("Central operation: {} — path: {}", method, api_path)

    response = await retry_central_command(
        central_conn=conn,
        api_method=method,
        api_path=api_path,
        api_data=api_data,
    )

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "method": method, "path": api_path, "data": response.get("msg", {})}

    msg = response.get("msg", "Unknown error")
    raise ToolError({"status_code": code or 502, "message": f"{method} {api_path} failed: {msg}"})


# Common field definitions reused across write tools
_OBJECT_TYPE_FIELD = Field(
    description=(
        "Where to write the object. 'SHARED' (the API default) creates a "
        "library object; 'LOCAL' creates a scoped object and requires both "
        "scope_id and device_function. Omitting object_type while providing "
        "scope_id/device_function is treated as 'LOCAL'."
    ),
    default=None,
)
_SCOPE_ID_FIELD = Field(
    description=(
        "Scope ID for a LOCAL (scoped) object. Required when "
        "object_type='LOCAL'; must be omitted for SHARED objects. "
        "Get scope IDs from central_get_scope_tree."
    ),
    default=None,
)
_DEVICE_FUNCTION_FIELD = Field(
    description=(
        "Device function for a LOCAL (scoped) object. Required when "
        "object_type='LOCAL'; must be omitted for SHARED. Valid: CAMPUS_AP, "
        "ACCESS_SWITCH, BRANCH_GW, MOBILITY_GW, CORE_SWITCH, AGG_SWITCH, ALL."
    ),
    default=None,
)
_CONFIRMED_FIELD = Field(
    description=(
        "Fallback confirmation flag — honored only when the client cannot "
        "show a confirmation prompt (the universal gate prompts otherwise)."
    ),
    default=False,
)
