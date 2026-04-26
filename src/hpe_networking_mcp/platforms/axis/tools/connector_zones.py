"""Axis connector-zone read tools (``/ConnectorZones``)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools import READ_ONLY, WRITE_DELETE
from hpe_networking_mcp.platforms.axis.tools._manage import manage_entity


@tool(annotations=READ_ONLY)
async def axis_get_connector_zones(
    ctx: Context,
    connector_zone_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """Get Axis connector zones (groupings of connectors).

    Args:
        connector_zone_id: GUID for single-item lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if connector_zone_id:
            return await client.get_json(f"/ConnectorZones/{connector_zone_id}")
        return await client.get_paged("/ConnectorZones", page_number=page_number, page_size=page_size)
    except Exception as e:
        return f"Error fetching connector zones: {format_http_error(e)}"


@tool(annotations=WRITE_DELETE, tags={"axis_write_delete"})
async def axis_manage_connector_zone(
    ctx: Context,
    action_type: str,
    payload: dict | None = None,
    connector_zone_id: str | None = None,
    confirmed: bool = False,
) -> dict | str:
    """Create, update, or delete an Axis connector zone.

    Writes stage in Axis. Call ``axis_commit_changes`` to apply.

    Args:
        action_type: One of ``'create'``, ``'update'``, ``'delete'``.
        payload: Body for create/update. Ignored for delete.
        connector_zone_id: GUID — required for update/delete.
        confirmed: Set true after user confirms; skips re-prompting.
    """
    return await manage_entity(
        ctx,
        base_path="/ConnectorZones",
        label="connector zone",
        action_type=action_type,
        payload=payload,
        entity_id=connector_zone_id,
        confirmed=confirmed,
    )
