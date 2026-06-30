"""AOS8 differentiator read tools (DIFF-01..09).

Exposes capabilities beyond Aruba Central parity: Conductor hierarchy,
effective config inheritance, pending config changes, RF neighbors, cluster
state, air-monitor APs, AP wired ports, IPsec tunnels, and a unified
multi-call MD health check aggregator.

All tools are READ_ONLY. Each tool issues a single ``client.request`` call
(or several, in the case of ``aos8_get_md_health_check``) and strips the
AOS8 ``_meta`` / ``_global_result`` envelope keys from the response body
before returning it to the AI client. ``format_aos8_error`` provides
consistent error responses.
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.aos8._registry import tool
from hpe_networking_mcp.platforms.aos8.cli_parser import parse_aos8_cli
from hpe_networking_mcp.platforms.aos8.client import get_aos8_client
from hpe_networking_mcp.platforms.aos8.tools._helpers import (
    format_aos8_error,
    get_object,
    run_show,
)
from hpe_networking_mcp.utils.uploads import read_uploaded_text

__all__ = [
    "aos8_get_md_hierarchy",
    "aos8_get_effective_config",
    "aos8_parse_config",
    "aos8_get_pending_changes",
    "aos8_get_rf_neighbors",
    "aos8_get_cluster_state",
    "aos8_get_air_monitors",
    "aos8_get_ap_wired_ports",
    "aos8_get_ipsec_tunnels",
    "aos8_get_md_health_check",
]


# ---------------------------------------------------------------------------
# DIFF-01 — Conductor → Managed Device hierarchy
# ---------------------------------------------------------------------------


@tool(name="aos8_get_md_hierarchy", capability=Capability.READ)
async def aos8_get_md_hierarchy(ctx: Context) -> dict[str, Any] | str:
    """Return the Conductor → Managed Device hierarchy with config_path values.

    Args:
        ctx: FastMCP request context (provides ``aos8_client``).

    Returns:
        Dict with the AOS8 ``Configuration node hierarchy`` table on success;
        error string on failure.
    """
    client = get_aos8_client(ctx)
    try:
        return await run_show(client, "show configuration node-hierarchy")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch MD hierarchy")


# ---------------------------------------------------------------------------
# DIFF-02 — Effective resolved configuration for an object
# ---------------------------------------------------------------------------


@tool(name="aos8_get_effective_config", capability=Capability.READ)
async def aos8_get_effective_config(
    ctx: Context,
    object_name: str,
    config_path: str = "/md",
    entry_type: str | None = None,
) -> dict[str, Any] | str:
    """Return the effective resolved config for ``object_name`` at ``config_path``.

    Uses the config-object endpoint with inheritance applied at the given
    ``config_path`` scope.

    Args:
        ctx: FastMCP request context.
        object_name: AOS8 object name (e.g. ``ssid_prof``, ``virtual_ap``).
        config_path: Hierarchy scope; defaults to ``/md``.
        entry_type: Optional ``type`` filter (``"user"``, ``"local"``,
            ``"default"``, ``"inherited"``). Pass ``"user"`` to strip
            factory defaults and return only customer-defined entries —
            useful for migration audits where defaults are noise.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = get_aos8_client(ctx)
    try:
        return await get_object(
            client,
            object_name,
            config_path=config_path,
            entry_type=entry_type,
        )
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, f"fetch effective config for {object_name}")


# ---------------------------------------------------------------------------
# DIFF-02b — Offline AOS 8 CLI → canonical translation records
# ---------------------------------------------------------------------------


@tool(name="aos8_parse_config", capability=Capability.READ)
async def aos8_parse_config(
    ctx: Context,
    cli_text: str | None = None,
    filename: str | None = None,
) -> dict[str, Any]:
    """Parse AOS 8 running-config CLI into canonical translation records.

    The offline counterpart to ``aos8_get_effective_config``: instead of pulling
    config records from a live Conductor, it turns AOS 8 CLI **text** — the kind
    an operator copies out of ``show running-config`` or a captured config file —
    into the **same record shapes the translation engine consumes**.

    Provide the config via EXACTLY ONE source:

    * ``filename`` — an operator-uploaded config file (via the ``file_manager``
      widget). Read **server-side** so the raw config — including PSKs and
      RADIUS/TACACS secrets — **never enters the model context**. This is the
      right choice for real configs; prefer it over paste.
    * ``cli_text`` — pasted CLI text. The operator chose to paste it, so it is
      already in context; fine for small snippets, but a full config contains
      secrets, so upload is preferred.

    It recognises ``netdestination`` / ``netdestination6``,
    ``ip access-list session`` / ``ipv6 access-list session``, and
    ``user-role`` stanzas, producing:

    * ``netdst`` — netdestination records (feed ``central:net_group``)
    * ``acl_sess`` — session-ACL records (feed ``central:policy``)
    * ``role`` — user-role records (feed ``central:role``)
    * ``_warnings`` — human-readable notes for clauses that weren't fully
      modelled (nothing is silently dropped; unparseable rules are also
      captured under an ``_unparsed`` marker on the record).

    The result is interchangeable with the output of
    ``aos8_get_effective_config``: hand it straight to the ``central:*``
    translations exactly the same way.

    Args:
        ctx: FastMCP request context (used to read an uploaded file server-side
            when ``filename`` is given).
        cli_text: AOS 8 running-config CLI text (``!``-delimited stanzas).
            Mutually exclusive with ``filename``.
        filename: Name of an operator-uploaded config file, read server-side.
            Mutually exclusive with ``cli_text``.

    Returns:
        ``{"netdst": [...], "acl_sess": [...], "role": [...],
        "_warnings": [...]}`` — translation-ready records plus warnings.

    Raises:
        ToolError: 400 if neither or both sources are given (the server-side
            read may also raise 400/404/502 — see ``read_uploaded_text``).
    """
    provided = [s for s in (cli_text, filename) if s is not None]
    if not provided:
        raise ToolError({"status_code": 400, "message": "provide exactly one of filename (upload) or cli_text (paste)"})
    if len(provided) > 1:
        raise ToolError({"status_code": 400, "message": "provide exactly ONE of filename / cli_text, not both"})
    # File-upload path: read the config server-side so its contents (PSKs,
    # RADIUS/TACACS secrets, ...) never enter the model context.
    text = read_uploaded_text(ctx, filename) if filename is not None else cli_text
    assert text is not None  # narrowed by the exactly-one check above
    return parse_aos8_cli(text)


# ---------------------------------------------------------------------------
# DIFF-03 — Pending config changes (not yet committed via write_memory)
# ---------------------------------------------------------------------------


@tool(name="aos8_get_pending_changes", capability=Capability.READ)
async def aos8_get_pending_changes(ctx: Context) -> dict[str, Any] | str:
    """Return staged config changes not yet persisted via ``write_memory``.

    Args:
        ctx: FastMCP request context.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = get_aos8_client(ctx)
    try:
        return await run_show(client, "show configuration pending")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch pending changes")


# ---------------------------------------------------------------------------
# DIFF-04 — ARM RF neighbors for a single AP
# ---------------------------------------------------------------------------


@tool(name="aos8_get_rf_neighbors", capability=Capability.READ)
async def aos8_get_rf_neighbors(
    ctx: Context,
    ap_name: str,
    config_path: str = "/md",
) -> dict[str, Any] | str:
    """Return ARM neighbor graph for the named AP.

    Args:
        ctx: FastMCP request context.
        ap_name: AP display name.
        config_path: Hierarchy scope; defaults to ``/md``.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = get_aos8_client(ctx)
    try:
        return await run_show(
            client,
            f"show ap arm-neighbors ap-name {ap_name}",
            config_path=config_path,
        )
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch RF neighbors")


# ---------------------------------------------------------------------------
# DIFF-05 — AP cluster (LC-cluster) membership and master/standby state
# ---------------------------------------------------------------------------


@tool(name="aos8_get_cluster_state", capability=Capability.READ)
async def aos8_get_cluster_state(ctx: Context) -> dict[str, Any] | str:
    """Return AP cluster membership and master/standby state.

    Args:
        ctx: FastMCP request context.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = get_aos8_client(ctx)
    try:
        return await run_show(client, "show lc-cluster group-membership")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch cluster state")


# ---------------------------------------------------------------------------
# DIFF-06 — APs operating in air-monitor mode
# ---------------------------------------------------------------------------


@tool(name="aos8_get_air_monitors", capability=Capability.READ)
async def aos8_get_air_monitors(ctx: Context) -> dict[str, Any] | str:
    """Return APs operating in air-monitor mode.

    Args:
        ctx: FastMCP request context.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = get_aos8_client(ctx)
    try:
        return await run_show(client, "show ap monitor active-laser-beams")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch air monitors")


# ---------------------------------------------------------------------------
# DIFF-07 — Wired-port configuration and state for an AP
# ---------------------------------------------------------------------------


@tool(name="aos8_get_ap_wired_ports", capability=Capability.READ)
async def aos8_get_ap_wired_ports(
    ctx: Context,
    ap_name: str,
) -> dict[str, Any] | str:
    """Return wired port configuration and state for the named AP.

    Args:
        ctx: FastMCP request context.
        ap_name: AP display name.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = get_aos8_client(ctx)
    try:
        return await run_show(client, f"show ap port status ap-name {ap_name}")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch AP wired ports")


# ---------------------------------------------------------------------------
# DIFF-08 — Site-to-site / Remote AP IPsec tunnel state
# ---------------------------------------------------------------------------


@tool(name="aos8_get_ipsec_tunnels", capability=Capability.READ)
async def aos8_get_ipsec_tunnels(ctx: Context) -> dict[str, Any] | str:
    """Return site-to-site and Remote AP IPsec tunnel state.

    Args:
        ctx: FastMCP request context.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = get_aos8_client(ctx)
    try:
        return await run_show(client, "show crypto ipsec sa")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch IPsec tunnels")


# ---------------------------------------------------------------------------
# DIFF-09 — Unified multi-call MD health check aggregator
# ---------------------------------------------------------------------------


@tool(name="aos8_get_md_health_check", capability=Capability.READ)
async def aos8_get_md_health_check(
    ctx: Context,
    config_path: str,
) -> dict[str, Any] | str:
    """Unified health report for an MD or ``config_path`` scope.

    Aggregates AP active/database, alarms, firmware version, and client
    counts in a single call. Each sub-call is run concurrently; partial
    failure of one sub-call does not fail the whole report — the failing
    section instead contains an ``error`` key (Pitfall 3 mitigation).

    Args:
        ctx: FastMCP request context.
        config_path: Required scope (e.g. ``/md/branch1``). No default —
            calling without it raises ``TypeError``.

    Returns:
        Dict with keys ``config_path``, ``aps``, ``clients``, ``alarms``,
        ``firmware``. On full failure returns an error string.
    """
    client = get_aos8_client(ctx)
    try:
        results: Any = await asyncio.gather(
            run_show(client, "show ap active", config_path=config_path),
            run_show(client, "show ap database", config_path=config_path),
            run_show(client, "show alarms all", config_path=config_path),
            run_show(client, "show version", config_path=config_path),
            run_show(client, "show user summary", config_path=config_path),
            return_exceptions=True,
        )
        ap_active, ap_db, alarms, version, users = results

        def _section(value: Any, label: str) -> Any:
            if isinstance(value, Exception):
                return {"error": format_aos8_error(value, f"fetch {label}")}
            return value

        # AP section combines active + database; if either sub-call failed,
        # bubble the error up to the section root so consumers can detect
        # partial failure without descending into nested keys (Pitfall 3).
        if isinstance(ap_active, Exception) or isinstance(ap_db, Exception):
            failure = ap_active if isinstance(ap_active, Exception) else ap_db
            aps_section: Any = {"error": format_aos8_error(failure, "fetch AP status")}
            if not isinstance(ap_active, Exception):
                aps_section["active"] = ap_active
            if not isinstance(ap_db, Exception):
                aps_section["database"] = ap_db
        else:
            aps_section = {"active": ap_active, "database": ap_db}

        return {
            "config_path": config_path,
            "aps": aps_section,
            "clients": _section(users, "client summary"),
            "alarms": _section(alarms, "alarms"),
            "firmware": _section(version, "version"),
        }
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "run MD health check")
