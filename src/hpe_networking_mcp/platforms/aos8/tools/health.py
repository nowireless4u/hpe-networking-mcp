"""AOS8 health and inventory read tools (READ-01..READ-08).

Each tool wraps a single ``show`` command via ``run_show`` and returns the
parsed JSON body with ``_meta`` / ``_global_result`` stripped. Conductor-root
tools (controllers, version, licenses) do not accept ``config_path`` because
those commands run only at the Mobility Conductor scope; the remaining tools
expose ``config_path`` (default ``/md``) so operators can target a specific
managed-device or AP-group node.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.aos8._registry import tool
from hpe_networking_mcp.platforms.aos8.tools import READ_ONLY
from hpe_networking_mcp.platforms.aos8.tools._helpers import (
    format_aos8_error,
    run_show,
)


@tool(name="aos8_get_controllers", annotations=READ_ONLY)
async def aos8_get_controllers(ctx: Context) -> dict[str, Any] | str:
    """Return the list of controllers known to the Mobility Conductor.

    Runs ``show switches`` at the Conductor root (no ``config_path``).

    Args:
        ctx: FastMCP request context (provides ``aos8_client``).

    Returns:
        Parsed JSON body (``_meta`` / ``_global_result`` stripped) on success;
        error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show switches")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "list controllers")


@tool(name="aos8_get_ap_database", annotations=READ_ONLY)
async def aos8_get_ap_database(ctx: Context, config_path: str = "/md") -> dict[str, Any] | str:
    """Return the AP database for a hierarchy node.

    Runs ``show ap database`` against ``config_path`` (default ``/md``).

    Args:
        ctx: FastMCP request context.
        config_path: Hierarchy node (e.g. ``/md`` or ``/md/site1``).

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show ap database", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch AP database")


@tool(name="aos8_get_active_aps", annotations=READ_ONLY)
async def aos8_get_active_aps(ctx: Context, config_path: str = "/md") -> dict[str, Any] | str:
    """Return the active AP table for a hierarchy node.

    Runs ``show ap active`` against ``config_path`` (default ``/md``).

    Args:
        ctx: FastMCP request context.
        config_path: Hierarchy node.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show ap active", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "list active APs")


@tool(name="aos8_get_ap_detail", annotations=READ_ONLY)
async def aos8_get_ap_detail(
    ctx: Context,
    ap_name: str | None = None,
    ap_mac: str | None = None,
    config_path: str = "/md",
) -> dict[str, Any] | str:
    """Return detailed AP info by name or MAC (exactly one selector required).

    Runs ``show ap details ap-name <name>`` or ``show ap details ap-mac <mac>``.

    Args:
        ctx: FastMCP request context.
        ap_name: AP display name (mutually exclusive with ``ap_mac``).
        ap_mac: AP MAC address (mutually exclusive with ``ap_name``).
        config_path: Hierarchy node (default ``/md``).

    Returns:
        Parsed JSON body on success; error string on failure or when the
        selector contract is violated.
    """
    if (ap_name is None) == (ap_mac is None):
        return "Must provide exactly one of ap_name or ap_mac"
    selector = f"ap-name {ap_name}" if ap_name else f"ap-mac {ap_mac}"
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, f"show ap details {selector}", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch AP details")


@tool(name="aos8_get_bss_table", annotations=READ_ONLY)
async def aos8_get_bss_table(ctx: Context, config_path: str = "/md") -> dict[str, Any] | str:
    """Return the BSS table for a hierarchy node.

    Runs ``show ap bss-table`` against ``config_path`` (default ``/md``).

    Args:
        ctx: FastMCP request context.
        config_path: Hierarchy node.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show ap bss-table", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch BSS table")


@tool(name="aos8_get_radio_summary", annotations=READ_ONLY)
async def aos8_get_radio_summary(ctx: Context, config_path: str = "/md") -> dict[str, Any] | str:
    """Return the radio summary for a hierarchy node.

    Runs ``show ap radio-summary`` against ``config_path`` (default ``/md``).

    Args:
        ctx: FastMCP request context.
        config_path: Hierarchy node.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show ap radio-summary", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch radio summary")


@tool(name="aos8_get_version", annotations=READ_ONLY)
async def aos8_get_version(ctx: Context) -> dict[str, Any] | str:
    """Return the running software version of the Mobility Conductor.

    Runs ``show version`` at the Conductor root (no ``config_path``).

    Args:
        ctx: FastMCP request context.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show version")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch software version")


@tool(name="aos8_get_licenses", annotations=READ_ONLY)
async def aos8_get_licenses(ctx: Context) -> dict[str, Any] | str:
    """Return installed licenses on the Mobility Conductor.

    Runs ``show license`` at the Conductor root (no ``config_path``).

    Args:
        ctx: FastMCP request context.

    Returns:
        Parsed JSON body on success; error string on failure.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show license")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch licenses")
