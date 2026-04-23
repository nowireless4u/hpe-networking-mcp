"""Apstra blueprint and template read tools."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.apstra import guidelines
from hpe_networking_mcp.platforms.apstra._registry import tool
from hpe_networking_mcp.platforms.apstra.client import format_http_error, get_apstra_client
from hpe_networking_mcp.platforms.apstra.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def apstra_get_blueprints(ctx: Context) -> dict[str, Any] | str:
    """Get list of all Apstra blueprints.

    Returns the blueprint summary records (including id, label, design, status)
    along with base + blueprint formatting guidelines.
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json("/api/blueprints")
        items = payload.get("items", payload) if isinstance(payload, dict) else payload
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_blueprint_guidelines(),
            "data": items,
        }
    except Exception as e:
        return f"Error fetching blueprints: {format_http_error(e) if hasattr(e, 'response') else e}"


@tool(annotations=READ_ONLY)
async def apstra_get_templates(ctx: Context) -> dict[str, Any] | str:
    """Get list of available design templates for blueprint creation."""
    try:
        client = await get_apstra_client()
        payload = await client.get_json("/api/design/templates")
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_blueprint_guidelines(),
            "data": payload,
        }
    except Exception as e:
        return f"Error fetching templates: {format_http_error(e) if hasattr(e, 'response') else e}"
