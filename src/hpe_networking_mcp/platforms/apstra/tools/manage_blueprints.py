"""Apstra blueprint write tools (deploy, delete, create)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.apstra import guidelines
from hpe_networking_mcp.platforms.apstra._registry import tool
from hpe_networking_mcp.platforms.apstra.client import format_http_error, get_apstra_client


@tool(capability=Capability.OPERATIONAL, enable_gated=True)
async def apstra_deploy(
    ctx: Context,
    blueprint_id: str,
    description: str,
    staging_version: int,
    confirmed: bool = False,
) -> dict[str, Any]:
    """Deploy a blueprint's staged configuration to the fabric.

    Args:
        blueprint_id: Blueprint UUID.
        description: Human-readable change description recorded in Apstra's history.
        staging_version: Staging version number to deploy (from ``apstra_get_diff_status``).
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    try:
        client = await get_apstra_client()
        response = await client.request(
            "PUT",
            f"/api/blueprints/{blueprint_id}/deploy",
            json_body={"version": staging_version, "description": description},
        )
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_change_mgmt_guidelines(),
            "data": response.json() if response.content else {"status": "accepted"},
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error deploying blueprint: {detail}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def apstra_delete_blueprint(
    ctx: Context,
    blueprint_id: str,
    confirmed: bool = False,
) -> dict[str, Any]:
    """Permanently delete an Apstra blueprint.

    Args:
        blueprint_id: Blueprint UUID to delete.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    try:
        client = await get_apstra_client()
        response = await client.request("DELETE", f"/api/blueprints/{blueprint_id}")
        body: Any
        if response.content:
            try:
                body = response.json()
            except ValueError:
                body = response.text
        else:
            body = "Blueprint deleted successfully"
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_change_mgmt_guidelines(),
            "data": body,
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error deleting blueprint: {detail}"}) from e


@tool(capability=Capability.WRITE)
async def apstra_create_datacenter_blueprint(
    ctx: Context,
    blueprint_name: str,
    template_id: str,
    confirmed: bool = False,
) -> dict[str, Any]:
    """Create a new datacenter (``two_stage_l3clos``) blueprint from a template.

    Args:
        blueprint_name: Human-readable label for the new blueprint.
        template_id: ID of the design template to instantiate (from ``apstra_get_templates``).
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    try:
        client = await get_apstra_client()
        response = await client.request(
            "POST",
            "/api/blueprints",
            json_body={
                "design": "two_stage_l3clos",
                "init_type": "template_reference",
                "template_id": template_id,
                "label": blueprint_name,
            },
        )
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_change_mgmt_guidelines(),
            "data": response.json(),
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error creating datacenter blueprint: {detail}"}) from e


@tool(capability=Capability.WRITE)
async def apstra_create_freeform_blueprint(
    ctx: Context,
    blueprint_name: str,
    confirmed: bool = False,
) -> dict[str, Any]:
    """Create a new freeform blueprint.

    Args:
        blueprint_name: Human-readable label for the new blueprint.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    try:
        client = await get_apstra_client()
        response = await client.request(
            "POST",
            "/api/blueprints",
            json_body={"design": "freeform", "init_type": "none", "label": blueprint_name},
        )
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_change_mgmt_guidelines(),
            "data": response.json(),
        }
    except Exception as e:
        detail = format_http_error(e) if hasattr(e, "response") else e
        raise ToolError({"status_code": 502, "message": f"Error creating freeform blueprint: {detail}"}) from e
