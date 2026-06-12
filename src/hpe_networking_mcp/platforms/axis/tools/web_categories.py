"""Axis web category read tools (``/WebCategories``)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools._manage import manage_entity


@tool(capability=Capability.READ)
async def axis_get_web_categories(
    ctx: Context,
    web_category_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any]:
    """Get Axis web categories (URL-classification categories used in policy).

    Args:
        web_category_id: GUID for single-item lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if web_category_id:
            return await client.get_json(f"/WebCategories/{path_seg(web_category_id)}")
        return await client.get_paged("/WebCategories", page_number=page_number, page_size=page_size)
    except Exception as e:
        detail = format_http_error(e)
        raise ToolError({"status_code": 502, "message": f"Error fetching web categories: {detail}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def axis_manage_web_category(
    ctx: Context,
    action_type: str,
    payload: dict | None = None,
    web_category_id: str | None = None,
    confirmed: bool = False,
) -> dict:
    """Create, update, or delete an Axis web category.

    Writes stage in Axis. Call ``axis_commit_changes`` to apply.

    Args:
        action_type: One of ``'create'``, ``'update'``, ``'delete'``.
        payload: Body for create/update. Ignored for delete.
        web_category_id: GUID — required for update/delete.
        confirmed: Set true after user confirms; skips re-prompting.
    """
    return await manage_entity(
        ctx,
        base_path="/WebCategories",
        label="web category",
        action_type=action_type,
        payload=payload,
        entity_id=web_category_id,
        confirmed=confirmed,
    )
