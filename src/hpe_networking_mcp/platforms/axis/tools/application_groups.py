"""Axis application-group (tag) read tools (``/Tags``).

Application groups are also called "tags" in the Axis API path. They
group applications for policy reference.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools import READ_ONLY, WRITE_DELETE
from hpe_networking_mcp.platforms.axis.tools._manage import manage_entity


@tool(annotations=READ_ONLY)
async def axis_get_application_groups(
    ctx: Context,
    application_group_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """Get Axis application groups (tags).

    Args:
        application_group_id: GUID for single-item lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if application_group_id:
            return await client.get_json(f"/Tags/{application_group_id}")
        return await client.get_paged("/Tags", page_number=page_number, page_size=page_size)
    except Exception as e:
        return f"Error fetching application groups: {format_http_error(e)}"


@tool(annotations=WRITE_DELETE, tags={"axis_write_delete"})
async def axis_manage_application_group(
    ctx: Context,
    action_type: str,
    payload: dict | None = None,
    application_group_id: str | None = None,
    confirmed: bool = False,
) -> dict | str:
    """Create, update, or delete an Axis application group (tag).

    Writes stage in Axis. Call ``axis_commit_changes`` to apply.

    Args:
        action_type: One of ``'create'``, ``'update'``, ``'delete'``.
        payload: Body for create/update. Ignored for delete.
        application_group_id: GUID — required for update/delete.
        confirmed: Set true after user confirms; skips re-prompting.
    """
    return await manage_entity(
        ctx,
        base_path="/Tags",
        label="application group",
        action_type=action_type,
        payload=payload,
        entity_id=application_group_id,
        confirmed=confirmed,
    )
