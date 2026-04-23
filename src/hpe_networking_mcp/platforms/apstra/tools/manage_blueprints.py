"""Apstra blueprint write tools (deploy, delete, create)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms.apstra import guidelines
from hpe_networking_mcp.platforms.apstra._registry import tool
from hpe_networking_mcp.platforms.apstra.client import format_http_error, get_apstra_client
from hpe_networking_mcp.platforms.apstra.tools import WRITE, WRITE_DELETE


@tool(annotations=WRITE_DELETE, tags={"apstra_write_delete"})
async def apstra_deploy(
    ctx: Context,
    blueprint_id: str,
    description: str,
    staging_version: int,
    confirmed: bool = False,
) -> dict[str, Any] | str:
    """Deploy a blueprint's staged configuration to the fabric.

    Args:
        blueprint_id: Blueprint UUID.
        description: Human-readable change description recorded in Apstra's history.
        staging_version: Staging version number to deploy (from ``apstra_get_diff_status``).
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if not confirmed:
        decline = await confirm_write(
            ctx,
            f"Apstra: deploy staging v{staging_version} to blueprint {blueprint_id}. "
            f"This applies changes to live devices. Confirm?",
        )
        if decline:
            return decline

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
        return f"Error deploying blueprint: {format_http_error(e) if hasattr(e, 'response') else e}"


@tool(annotations=WRITE_DELETE, tags={"apstra_write_delete"})
async def apstra_delete_blueprint(
    ctx: Context,
    blueprint_id: str,
    confirmed: bool = False,
) -> dict[str, Any] | str:
    """Permanently delete an Apstra blueprint.

    Args:
        blueprint_id: Blueprint UUID to delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if not confirmed:
        decline = await confirm_write(
            ctx,
            f"Apstra: permanently DELETE blueprint {blueprint_id}. This cannot be undone. Confirm?",
        )
        if decline:
            return decline

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
        return f"Error deleting blueprint: {format_http_error(e) if hasattr(e, 'response') else e}"


@tool(annotations=WRITE, tags={"apstra_write"})
async def apstra_create_datacenter_blueprint(
    ctx: Context,
    blueprint_name: str,
    template_id: str,
    confirmed: bool = False,
) -> dict[str, Any] | str:
    """Create a new datacenter (``two_stage_l3clos``) blueprint from a template.

    Args:
        blueprint_name: Human-readable label for the new blueprint.
        template_id: ID of the design template to instantiate (from ``apstra_get_templates``).
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if not confirmed:
        decline = await confirm_write(
            ctx,
            f"Apstra: create datacenter blueprint '{blueprint_name}' from template {template_id}. Confirm?",
        )
        if decline:
            return decline

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
        return f"Error creating datacenter blueprint: {format_http_error(e) if hasattr(e, 'response') else e}"


@tool(annotations=WRITE, tags={"apstra_write"})
async def apstra_create_freeform_blueprint(
    ctx: Context,
    blueprint_name: str,
    confirmed: bool = False,
) -> dict[str, Any] | str:
    """Create a new freeform blueprint.

    Args:
        blueprint_name: Human-readable label for the new blueprint.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if not confirmed:
        decline = await confirm_write(
            ctx,
            f"Apstra: create freeform blueprint '{blueprint_name}'. Confirm?",
        )
        if decline:
            return decline

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
        return f"Error creating freeform blueprint: {format_http_error(e) if hasattr(e, 'response') else e}"
