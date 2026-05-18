"""UXI sensor read tools."""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms.uxi._registry import tool
from hpe_networking_mcp.platforms.uxi.client import format_http_error, get_uxi_client
from hpe_networking_mcp.platforms.uxi.tools import READ_ONLY
from hpe_networking_mcp.platforms.uxi.tools._validators import validate_id


@tool(annotations=READ_ONLY)
async def uxi_list_sensors(
    ctx: Context,
    next_cursor: str | None = None,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """List UXI sensors with serial, name, model, MAC addresses, location coordinates, and type.

    Pass next_cursor from a prior response to paginate.
    Returns: {items: [...], count: N, next: str|null}. next=null means last page.

    Args:
        next_cursor: Cursor from the previous response 'next' field. Omit for first page.
        page_size: Max items per page (default 50, max 100).
    """
    try:
        client = await get_uxi_client()
        return await client.uxi_get("/sensors", next_cursor=next_cursor, limit=page_size)
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)


@tool(annotations=READ_ONLY)
async def uxi_get_sensor_status(
    ctx: Context,
    sensor_id: str,
) -> dict[str, Any] | str:
    """Get online/testing status and active issues for a specific UXI sensor.

    Returns: {isOnline: bool, isTesting: bool, issues: [{code, severity, status, timestamp, id, context, incidentId}]}

    Args:
        sensor_id: The sensor's UXI resource ID (from uxi_list_sensors items[].id).
    """
    validate_id(sensor_id, "sensor_id")
    try:
        client = await get_uxi_client()
        return await client.uxi_get_single(f"/sensors/{sensor_id}/status")
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)
