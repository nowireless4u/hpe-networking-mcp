"""Axis application read tools (``/Applications``)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools import READ_ONLY, WRITE_DELETE
from hpe_networking_mcp.platforms.axis.tools._manage import manage_entity


@tool(annotations=READ_ONLY)
async def axis_get_applications(
    ctx: Context,
    application_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """Get Axis published applications.

    Args:
        application_id: GUID for single-item lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if application_id:
            return await client.get_json(f"/Applications/{application_id}")
        return await client.get_paged("/Applications", page_number=page_number, page_size=page_size)
    except Exception as e:
        return f"Error fetching applications: {format_http_error(e)}"


@tool(annotations=WRITE_DELETE, tags={"axis_write_delete"})
async def axis_manage_application(
    ctx: Context,
    action_type: str,
    payload: dict | None = None,
    application_id: str | None = None,
    confirmed: bool = False,
) -> dict | str:
    """Create, update, or delete an Axis published application.

    Writes stage in Axis. Call ``axis_commit_changes`` to apply.

    Args:
        action_type: One of ``'create'``, ``'update'``, ``'delete'``.
        payload: Body for create/update. Ignored for delete.
        application_id: GUID — required for update/delete.
        confirmed: Set true after user confirms; skips re-prompting.
    """
    return await manage_entity(
        ctx,
        base_path="/Applications",
        label="application",
        action_type=action_type,
        payload=payload,
        entity_id=application_id,
        confirmed=confirmed,
    )
