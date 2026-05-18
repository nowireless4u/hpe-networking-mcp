"""UXI agent read tools."""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms.uxi._registry import tool
from hpe_networking_mcp.platforms.uxi.client import format_http_error, get_uxi_client
from hpe_networking_mcp.platforms.uxi.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def uxi_list_agents(
    ctx: Context,
    next_cursor: str | None = None,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """List UXI agents with name, MAC addresses, model, serial, group assignment, and notes.

    Pass next_cursor from a prior response to paginate.
    Returns: {items: [...], count: N, next: str|null}.

    Args:
        next_cursor: Cursor from the previous response 'next' field. Omit for first page.
        page_size: Max items per page (default 50, max 100).
    """
    try:
        client = await get_uxi_client()
        return await client.uxi_get("/agents", next_cursor=next_cursor, limit=page_size)
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)
