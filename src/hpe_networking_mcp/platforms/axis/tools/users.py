"""Axis user read tools (``/Users``)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools._manage import manage_entity


@tool(capability=Capability.READ)
async def axis_get_users(
    ctx: Context,
    user_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any]:
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
        detail = format_http_error(e)
        raise ToolError({"status_code": 502, "message": f"Error fetching users: {detail}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def axis_manage_user(
    ctx: Context,
    action_type: str,
    payload: dict | None = None,
    user_id: str | None = None,
    confirmed: bool = False,
) -> dict:
    """Create, update, or delete an Axis user.

    Writes stage in Axis. Call ``axis_commit_changes`` to apply.

    Args:
        action_type: One of ``'create'``, ``'update'``, ``'delete'``.
        payload: Body for create/update. Ignored for delete.
        user_id: GUID — required for update/delete.
        confirmed: Set true after user confirms; skips re-prompting.
    """
    return await manage_entity(
        ctx,
        base_path="/Users",
        label="user",
        action_type=action_type,
        payload=payload,
        entity_id=user_id,
        confirmed=confirmed,
    )
