"""Axis runtime-status helper for connectors and tunnels.

The Axis API exposes ``/Connectors/{id}/status`` and ``/Tunnels/{id}/status``
with similar shapes. This single tool dispatches on ``entity_type`` to keep
the surface narrow.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def axis_get_status(
    ctx: Context,
    entity_type: Annotated[str, Field(description="Either 'connector' or 'tunnel'.")],
    entity_id: Annotated[str, Field(description="GUID of the connector or tunnel.")],
) -> dict[str, Any] | str:
    """Get runtime status for a connector or tunnel.

    Connector status returns rich telemetry (state, CPU/mem/disk/network,
    hostname, OS, version). Tunnel status returns connection state and
    last-seen metrics.

    Args:
        entity_type: ``'connector'`` or ``'tunnel'``.
        entity_id: GUID of the connector or tunnel.
    """
    if entity_type == "connector":
        path = f"/Connectors/{entity_id}/status"
    elif entity_type == "tunnel":
        path = f"/Tunnels/{entity_id}/status"
    else:
        return f"Invalid entity_type '{entity_type}'. Must be 'connector' or 'tunnel'."
    try:
        client = await get_axis_client()
        return await client.get_json(path)
    except Exception as e:
        return f"Error fetching {entity_type} status: {format_http_error(e)}"
