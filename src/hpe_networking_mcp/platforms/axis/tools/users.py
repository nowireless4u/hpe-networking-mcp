"""Axis user read tools (``/Users``)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def axis_get_users(
    ctx: Context,
    user_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """Get Axis users (Atmos IdP user records).

    Args:
        user_id: GUID for single-item lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if user_id:
            return await client.get_json(f"/Users/{user_id}")
        return await client.get_paged("/Users", page_number=page_number, page_size=page_size)
    except Exception as e:
        return f"Error fetching users: {format_http_error(e)}"
