"""Apstra blueprint topology read tools (racks, routing zones, systems)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.apstra import guidelines
from hpe_networking_mcp.platforms.apstra._registry import tool
from hpe_networking_mcp.platforms.apstra.client import format_http_error, get_apstra_client
from hpe_networking_mcp.platforms.apstra.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def apstra_get_racks(ctx: Context, blueprint_id: str) -> dict[str, Any] | str:
    """Get all racks in a blueprint.

    Args:
        blueprint_id: The blueprint UUID (from ``apstra_get_blueprints``).
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{blueprint_id}/racks")
        items = payload.get("items", payload) if isinstance(payload, dict) else payload
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_device_guidelines(),
            "data": items,
        }
    except Exception as e:
        return f"Error fetching racks: {format_http_error(e) if hasattr(e, 'response') else e}"


@tool(annotations=READ_ONLY)
async def apstra_get_routing_zones(ctx: Context, blueprint_id: str) -> dict[str, Any] | str:
    """Get all routing zones (security zones) in a blueprint.

    Args:
        blueprint_id: The blueprint UUID.
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{blueprint_id}/security-zones")
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_network_guidelines(),
            "data": payload,
        }
    except Exception as e:
        return f"Error fetching routing zones: {format_http_error(e) if hasattr(e, 'response') else e}"


@tool(annotations=READ_ONLY)
async def apstra_get_system_info(ctx: Context, blueprint_id: str) -> dict[str, Any] | str:
    """Get systems (devices) inside a blueprint.

    Args:
        blueprint_id: The blueprint UUID.
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{blueprint_id}/experience/web/system-info")
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_device_guidelines(),
            "data": payload,
        }
    except Exception as e:
        return f"Error fetching system info: {format_http_error(e) if hasattr(e, 'response') else e}"
