"""Axis tunnel read tools (``/Tunnels``).

Tunnels carry traffic between customer locations and Axis Atmos Cloud.
For runtime status on a tunnel, call ``axis_get_status`` with
``entity_type="tunnel"``.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def axis_get_tunnels(
    ctx: Context,
    tunnel_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """Get Axis tunnels.

    If ``tunnel_id`` is provided, returns a single tunnel.
    Otherwise returns a paged list.

    Args:
        tunnel_id: GUID for single-item lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if tunnel_id:
            return await client.get_json(f"/Tunnels/{tunnel_id}")
        return await client.get_paged("/Tunnels", page_number=page_number, page_size=page_size)
    except Exception as e:
        return f"Error fetching tunnels: {format_http_error(e)}"
