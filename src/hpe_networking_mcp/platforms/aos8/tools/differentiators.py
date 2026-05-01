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

from hpe_networking_mcp.platforms.aos8._registry import tool
from hpe_networking_mcp.platforms.aos8.tools import READ_ONLY
from hpe_networking_mcp.platforms.aos8.tools._helpers import (
    format_aos8_error,
    get_object,
    run_show,
)

__all__ = [
    "aos8_get_md_hierarchy",
    "aos8_get_effective_config",
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


@tool(name="aos8_get_md_hierarchy", annotations=READ_ONLY)
async def aos8_get_md_hierarchy(ctx: Context) -> dict[str, Any] | str:
    """Return the Conductor → Managed Device hierarchy with config_path values.

    Args:
        ctx: FastMCP request context (provides ``aos8_client``).

    Returns:
        Dict with the AOS8 ``Switch Hierarchy`` table on success; error
        string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show switch hierarchy")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch MD hierarchy")


# ---------------------------------------------------------------------------
# DIFF-02 — Effective resolved configuration for an object
# ---------------------------------------------------------------------------


@tool(name="aos8_get_effective_config", annotations=READ_ONLY)
async def aos8_get_effective_config(
    ctx: Context,
    object_name: str,
    config_path: str = "/md",
) -> dict[str, Any] | str:
    """Return the effective resolved config for ``object_name`` at ``config_path``.

    Uses the config-object endpoint with inheritance applied at the given
    ``config_path`` scope.

    Args:
        ctx: FastMCP request context.
        object_name: AOS8 object name (e.g. ``ssid_prof``, ``virtual_ap``).
        config_path: Hierarchy scope; defaults to ``/md``.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await get_object(client, object_name, config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, f"fetch effective config for {object_name}")


# ---------------------------------------------------------------------------
# DIFF-03 — Pending config changes (not yet committed via write_memory)
# ---------------------------------------------------------------------------


@tool(name="aos8_get_pending_changes", annotations=READ_ONLY)
async def aos8_get_pending_changes(ctx: Context) -> dict[str, Any] | str:
    """Return staged config changes not yet persisted via ``write_memory``.

    Args:
        ctx: FastMCP request context.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show configuration pending")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch pending changes")


# ---------------------------------------------------------------------------
# DIFF-04 — ARM RF neighbors for a single AP
# ---------------------------------------------------------------------------


@tool(name="aos8_get_rf_neighbors", annotations=READ_ONLY)
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
    client = ctx.lifespan_context["aos8_client"]
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


@tool(name="aos8_get_cluster_state", annotations=READ_ONLY)
async def aos8_get_cluster_state(ctx: Context) -> dict[str, Any] | str:
    """Return AP cluster membership and master/standby state.

    Args:
        ctx: FastMCP request context.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show lc-cluster group-membership")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch cluster state")


# ---------------------------------------------------------------------------
# DIFF-06 — APs operating in air-monitor mode
# ---------------------------------------------------------------------------


@tool(name="aos8_get_air_monitors", annotations=READ_ONLY)
async def aos8_get_air_monitors(ctx: Context) -> dict[str, Any] | str:
    """Return APs operating in air-monitor mode.

    Args:
        ctx: FastMCP request context.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show ap monitor active-laser-beams")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch air monitors")


# ---------------------------------------------------------------------------
# DIFF-07 — Wired-port configuration and state for an AP
# ---------------------------------------------------------------------------


@tool(name="aos8_get_ap_wired_ports", annotations=READ_ONLY)
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
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, f"show ap port status ap-name {ap_name}")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch AP wired ports")


# ---------------------------------------------------------------------------
# DIFF-08 — Site-to-site / Remote AP IPsec tunnel state
# ---------------------------------------------------------------------------


@tool(name="aos8_get_ipsec_tunnels", annotations=READ_ONLY)
async def aos8_get_ipsec_tunnels(ctx: Context) -> dict[str, Any] | str:
    """Return site-to-site and Remote AP IPsec tunnel state.

    Args:
        ctx: FastMCP request context.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show crypto ipsec sa")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch IPsec tunnels")


# ---------------------------------------------------------------------------
# DIFF-09 — Unified multi-call MD health check aggregator
# ---------------------------------------------------------------------------


@tool(name="aos8_get_md_health_check", annotations=READ_ONLY)
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
    client = ctx.lifespan_context["aos8_client"]
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
