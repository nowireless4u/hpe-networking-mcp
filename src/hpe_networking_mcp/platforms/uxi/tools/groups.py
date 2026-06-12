"""UXI group read tools."""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.uxi._registry import tool
from hpe_networking_mcp.platforms.uxi.client import format_http_error, get_uxi_client


@tool(capability=Capability.READ)
async def uxi_list_groups(
    ctx: Context,
    next_cursor: str | None = None,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """List UXI groups with id, name, path, and parent group.

    Groups organize sensors, agents, and service tests hierarchically.
    Pass next_cursor from a prior response to paginate.
    Returns: {items: [{id, name, path, parent: {id}}], count: N, next: str|null}.

    Args:
        next_cursor: Cursor from the previous response 'next' field. Omit for first page.
        page_size: Max items per page (default 50, max 100).
    """
    try:
        client = await get_uxi_client()
        return await client.uxi_get("/groups", next_cursor=next_cursor, limit=page_size)
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)
