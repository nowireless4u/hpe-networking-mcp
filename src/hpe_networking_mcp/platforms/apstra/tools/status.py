"""Apstra status read tools (anomalies, diff status, protocol sessions)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.apstra import guidelines
from hpe_networking_mcp.platforms.apstra._registry import tool
from hpe_networking_mcp.platforms.apstra.client import format_http_error, get_apstra_client


@tool(capability=Capability.READ)
async def apstra_get_anomalies(ctx: Context, blueprint_id: str) -> dict[str, Any]:
    """Get anomalies for a blueprint.

    Args:
        blueprint_id: The blueprint UUID.
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{blueprint_id}/anomalies")
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_anomaly_guidelines(),
            "data": payload,
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error fetching anomalies: {detail}"}) from e


@tool(capability=Capability.READ)
async def apstra_get_diff_status(ctx: Context, blueprint_id: str) -> dict[str, Any]:
    """Get configuration diff status (staging vs active) for a blueprint.

    Use this after changes to confirm pending work is staged correctly before
    calling ``apstra_deploy``.

    Args:
        blueprint_id: The blueprint UUID.
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{blueprint_id}/diff-status")
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_status_guidelines(),
            "data": payload,
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error fetching diff status: {detail}"}) from e


@tool(capability=Capability.READ)
async def apstra_get_protocol_sessions(ctx: Context, blueprint_id: str) -> dict[str, Any]:
    """Get all protocol (e.g. BGP) sessions in a blueprint.

    Args:
        blueprint_id: The blueprint UUID.
    """
    try:
        client = await get_apstra_client()
        payload = await client.get_json(f"/api/blueprints/{blueprint_id}/protocol-sessions")
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_status_guidelines(),
            "data": payload,
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error fetching protocol sessions: {detail}"}) from e
