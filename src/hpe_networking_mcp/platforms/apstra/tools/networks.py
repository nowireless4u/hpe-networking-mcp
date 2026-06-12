"""Apstra virtual-network and remote-gateway read tools."""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.apstra import guidelines
from hpe_networking_mcp.platforms.apstra._registry import tool
from hpe_networking_mcp.platforms.apstra.client import format_http_error, get_apstra_client


@tool(capability=Capability.READ)
async def apstra_get_virtual_networks(ctx: Context, blueprint_id: str) -> dict[str, Any]:
    """Get virtual networks in a blueprint, including bound systems and VLAN IDs.

    Args:
        blueprint_id: The blueprint UUID.
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{blueprint_id}/virtual-networks")
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_network_guidelines(),
            "data": payload,
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error fetching virtual networks: {detail}"}) from e


@tool(capability=Capability.READ)
async def apstra_get_remote_gateways(ctx: Context, blueprint_id: str) -> dict[str, Any]:
    """Get all remote EVPN gateways in a blueprint.

    Args:
        blueprint_id: The blueprint UUID.
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{blueprint_id}/remote_gateways")
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_network_guidelines(),
            "data": payload,
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error fetching remote gateways: {detail}"}) from e
