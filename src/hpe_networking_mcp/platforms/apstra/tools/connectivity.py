"""Apstra connectivity-template and application-endpoint read tools."""

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
async def apstra_get_connectivity_templates(ctx: Context, blueprint_id: str) -> dict[str, Any]:
    """Get connectivity templates (endpoint policies) in a blueprint.

    Policies marked ``"visible": true`` can be assigned to interfaces.

    Args:
        blueprint_id: The blueprint UUID.
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{path_seg(blueprint_id)}/obj-policy-export")
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_network_guidelines(),
            "data": payload,
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error fetching connectivity templates: {detail}"}) from e


@tool(capability=Capability.READ)
async def apstra_get_application_endpoints(ctx: Context, blueprint_id: str) -> dict[str, Any]:
    """Get all possible application endpoints for connectivity templates.

    This endpoint uses POST semantics per Apstra's API contract, returning the
    discoverable interface set that connectivity templates can be bound to.

    Args:
        blueprint_id: The blueprint UUID.
    """
    try:
        client = await get_apstra_client()
        response = await client.request(
            "POST",
            f"/api/blueprints/{path_seg(blueprint_id)}/obj-policy-application-points",
        )
        payload = response.json()
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_network_guidelines(),
            "data": payload,
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error fetching application endpoints: {detail}"}) from e
