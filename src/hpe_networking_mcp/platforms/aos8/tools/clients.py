"""AOS8 client visibility read tools (READ-09..12).

Implements four MCP tools wrapping AOS8 ``showcommand`` queries that surface
wireless/wired client state:

* ``aos8_get_clients`` — full user-table snapshot at a config_path.
* ``aos8_find_client`` — target lookup by exactly one of MAC, IP, or username.
* ``aos8_get_client_detail`` — verbose per-MAC client record.
* ``aos8_get_client_history`` — AP association history (no config_path).

All tools delegate to ``_helpers.run_show`` so showcommand calls share a single
HTTP shape and ``_meta`` / ``_global_result`` stripping path. Errors at the
tool boundary are rendered via ``format_aos8_error`` for AI-friendly strings.
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


@tool(name="aos8_get_clients", annotations=READ_ONLY)
async def aos8_get_clients(ctx: Context, config_path: str = "/md") -> dict[str, Any] | str:
    """List all clients in the AOS8 user-table.

    Args:
        ctx: FastMCP context exposing the AOS8 client via lifespan_context.
        config_path: Hierarchy node to scope the query against (default ``"/md"``).

    Returns:
        Cleaned showcommand body, or an error string when the request fails.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show user-table", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "list clients")


@tool(name="aos8_find_client", annotations=READ_ONLY)
async def aos8_find_client(
    ctx: Context,
    mac: str | None = None,
    ip: str | None = None,
    username: str | None = None,
    config_path: str = "/md",
) -> dict[str, Any] | str:
    """Find a single client in the user-table by MAC, IP, or username.

    Exactly one of ``mac``, ``ip``, or ``username`` must be provided. The tool
    returns an error string (without making an API call) when zero or multiple
    selectors are set.

    Args:
        ctx: FastMCP context exposing the AOS8 client via lifespan_context.
        mac: Client MAC address (e.g. ``"aa:bb:cc:dd:ee:01"``).
        ip: Client IP address (e.g. ``"10.1.10.5"``).
        username: Client username (e.g. ``"alice"``).
        config_path: Hierarchy node to scope the query against (default ``"/md"``).

    Returns:
        Cleaned showcommand body, or an error string when the request fails or
        the selector contract is violated.
    """
    if sum(s is not None for s in (mac, ip, username)) != 1:
        return "Must provide exactly one of mac, ip, or username"

    if mac is not None:
        command = f"show user-table mac {mac}"
    elif ip is not None:
        command = f"show user-table ip {ip}"
    else:
        # username is not None by elimination
        command = f"show user-table name {username}"

    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, command, config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "find client")


@tool(name="aos8_get_client_detail", annotations=READ_ONLY)
async def aos8_get_client_detail(
    ctx: Context,
    mac: str,
    config_path: str = "/md",
) -> dict[str, Any] | str:
    """Fetch verbose detail for a single client by MAC.

    Args:
        ctx: FastMCP context exposing the AOS8 client via lifespan_context.
        mac: Client MAC address.
        config_path: Hierarchy node to scope the query against (default ``"/md"``).

    Returns:
        Cleaned showcommand body, or an error string when the request fails.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(
            client,
            f"show user-table verbose mac {mac}",
            config_path=config_path,
        )
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch client detail")


@tool(name="aos8_get_client_history", annotations=READ_ONLY)
async def aos8_get_client_history(ctx: Context, mac: str) -> dict[str, Any] | str:
    """Fetch AP association history for a client by MAC.

    AP association history is a controller-wide query and does not accept a
    ``config_path`` parameter (per phase context decision D-05).

    Args:
        ctx: FastMCP context exposing the AOS8 client via lifespan_context.
        mac: Client MAC address.

    Returns:
        Cleaned showcommand body, or an error string when the request fails.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, f"show ap association history client-mac {mac}")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch client history")
