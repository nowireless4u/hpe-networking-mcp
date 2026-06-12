"""Apstra blueprint topology read tools (racks, routing zones, systems)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.apstra import guidelines
from hpe_networking_mcp.platforms.apstra._registry import tool
from hpe_networking_mcp.platforms.apstra.client import format_http_error, get_apstra_client


@tool(capability=Capability.READ)
async def apstra_get_racks(ctx: Context, blueprint_id: str) -> dict[str, Any]:
    """Get all racks in a blueprint.

    Args:
        blueprint_id: The blueprint UUID (from ``apstra_get_blueprints``).
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{path_seg(blueprint_id)}/racks")
        items = payload.get("items", payload) if isinstance(payload, dict) else payload
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_device_guidelines(),
            "data": items,
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error fetching racks: {detail}"}) from e


@tool(capability=Capability.READ)
async def apstra_get_routing_zones(ctx: Context, blueprint_id: str) -> dict[str, Any]:
    """Get all routing zones (security zones) in a blueprint.

    Args:
        blueprint_id: The blueprint UUID.
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{path_seg(blueprint_id)}/security-zones")
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_network_guidelines(),
            "data": payload,
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error fetching routing zones: {detail}"}) from e


@tool(capability=Capability.READ)
async def apstra_get_system_info(ctx: Context, blueprint_id: str) -> dict[str, Any]:
    """Get systems (devices) inside a blueprint.

    Args:
        blueprint_id: The blueprint UUID.
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{path_seg(blueprint_id)}/experience/web/system-info")
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_device_guidelines(),
            "data": payload,
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error fetching system info: {detail}"}) from e
