"""Axis location and sub-location read tools (``/Locations``).

Locations are physical sites; sub-locations are logical subdivisions
nested under a location. The sub-location list endpoint is location-scoped.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools import READ_ONLY, WRITE_DELETE
from hpe_networking_mcp.platforms.axis.tools._manage import manage_entity


@tool(annotations=READ_ONLY)
async def axis_get_locations(
    ctx: Context,
    location_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """Get Axis locations (physical sites).

    Args:
        location_id: GUID for single-item lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if location_id:
            return await client.get_json(f"/Locations/{location_id}")
        return await client.get_paged("/Locations", page_number=page_number, page_size=page_size)
    except Exception as e:
        return f"Error fetching locations: {format_http_error(e)}"


@tool(annotations=READ_ONLY)
async def axis_get_sub_locations(
    ctx: Context,
    location_id: str,
    sub_location_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """Get sub-locations nested under a parent location.

    Args:
        location_id: GUID of the parent location (required).
        sub_location_id: GUID for single sub-location lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if sub_location_id:
            return await client.get_json(f"/Locations/{location_id}/SubLocations/{sub_location_id}")
        return await client.get_paged(
            f"/Locations/{location_id}/SubLocations",
            page_number=page_number,
            page_size=page_size,
        )
    except Exception as e:
        return f"Error fetching sub-locations: {format_http_error(e)}"


@tool(annotations=WRITE_DELETE, tags={"axis_write_delete"})
async def axis_manage_location(
    ctx: Context,
    action_type: str,
    payload: dict | None = None,
    location_id: str | None = None,
    confirmed: bool = False,
) -> dict | str:
    """Create, update, or delete an Axis location.

    Writes stage in Axis. Call ``axis_commit_changes`` to apply.

    Args:
        action_type: One of ``'create'``, ``'update'``, ``'delete'``.
        payload: Body for create/update. Ignored for delete.
        location_id: GUID — required for update/delete.
        confirmed: Set true after user confirms; skips re-prompting.
    """
    return await manage_entity(
        ctx,
        base_path="/Locations",
        label="location",
        action_type=action_type,
        payload=payload,
        entity_id=location_id,
        confirmed=confirmed,
    )


@tool(annotations=WRITE_DELETE, tags={"axis_write_delete"})
async def axis_manage_sub_location(
    ctx: Context,
    action_type: str,
    location_id: str,
    payload: dict | None = None,
    sub_location_id: str | None = None,
    confirmed: bool = False,
) -> dict | str:
    """Create, update, or delete an Axis sub-location under a parent location.

    Writes stage in Axis. Call ``axis_commit_changes`` to apply.

    Args:
        action_type: One of ``'create'``, ``'update'``, ``'delete'``.
        location_id: GUID of the parent location (required).
        payload: Body for create/update. Ignored for delete.
        sub_location_id: GUID of the sub-location — required for update/delete.
        confirmed: Set true after user confirms; skips re-prompting.
    """
    return await manage_entity(
        ctx,
        base_path=f"/Locations/{location_id}/SubLocations",
        label=f"sub-location under location {location_id}",
        action_type=action_type,
        payload=payload,
        entity_id=sub_location_id,
        confirmed=confirmed,
    )
