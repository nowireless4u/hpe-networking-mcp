"""Apstra virtual-network and remote-gateway read tools."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.apstra import guidelines
from hpe_networking_mcp.platforms.apstra._registry import mcp
from hpe_networking_mcp.platforms.apstra.client import format_http_error, get_apstra_client
from hpe_networking_mcp.platforms.apstra.tools import READ_ONLY


@mcp.tool(annotations=READ_ONLY)
async def apstra_get_virtual_networks(ctx: Context, blueprint_id: str) -> dict[str, Any] | str:
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
        return f"Error fetching virtual networks: {format_http_error(e) if hasattr(e, 'response') else e}"


@mcp.tool(annotations=READ_ONLY)
async def apstra_get_remote_gateways(ctx: Context, blueprint_id: str) -> dict[str, Any] | str:
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
        return f"Error fetching remote gateways: {format_http_error(e) if hasattr(e, 'response') else e}"
