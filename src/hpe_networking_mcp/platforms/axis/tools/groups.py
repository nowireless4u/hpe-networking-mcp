"""Axis group read tools (``/Groups``)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def axis_get_groups(
    ctx: Context,
    group_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """Get Axis groups (Atmos IdP user groups).

    Args:
        group_id: GUID for single-item lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if group_id:
            return await client.get_json(f"/Groups/{group_id}")
        return await client.get_paged("/Groups", page_number=page_number, page_size=page_size)
    except Exception as e:
        return f"Error fetching groups: {format_http_error(e)}"
