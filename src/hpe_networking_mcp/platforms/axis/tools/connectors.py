"""Axis connector read tools (``/Connectors``).

Connectors are tunnel-endpoint devices that link the customer network
into Axis Atmos Cloud. Each carries rich telemetry (state, CPU/mem/disk,
hostname, OS, version) — fetch it via ``axis_get_status``.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def axis_get_connectors(
    ctx: Context,
    connector_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """Get Axis connectors (tunnel-endpoint devices).

    If ``connector_id`` is provided, returns a single connector record.
    Otherwise returns a paged list. For runtime telemetry on a specific
    connector (state, CPU/mem/disk, version), call ``axis_get_status``
    with ``entity_type="connector"``.

    Args:
        connector_id: GUID for single-item lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if connector_id:
            return await client.get_json(f"/Connectors/{connector_id}")
        return await client.get_paged("/Connectors", page_number=page_number, page_size=page_size)
    except Exception as e:
        return f"Error fetching connectors: {format_http_error(e)}"
