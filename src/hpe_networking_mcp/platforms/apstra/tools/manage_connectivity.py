"""Apstra connectivity-template policy write tools."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.apstra import guidelines
from hpe_networking_mcp.platforms.apstra._registry import mcp
from hpe_networking_mcp.platforms.apstra.client import format_http_error, get_apstra_client
from hpe_networking_mcp.platforms.apstra.models import normalize_application_points
from hpe_networking_mcp.platforms.apstra.tools import WRITE


async def _confirm(ctx: Context, message: str) -> dict[str, Any] | None:
    elicit = await elicitation_handler(message=message, ctx=ctx)
    if elicit.action == "decline":
        mode = await ctx.get_state("elicitation_mode")
        if mode == "chat_confirm":
            return {
                "status": "confirmation_required",
                "message": (
                    f"Please confirm: {message}. Call this tool again with confirmed=true after the user confirms."
                ),
            }
        return {"status": "declined", "message": "Action declined by user."}
    if elicit.action == "cancel":
        return {"status": "cancelled", "message": "Action cancelled by user."}
    return None


@mcp.tool(annotations=WRITE, tags={"apstra_write"})
async def apstra_apply_ct_policies(
    ctx: Context,
    blueprint_id: str,
    application_points: str | list[dict[str, Any]] | dict[str, Any],
    confirmed: bool = False,
) -> dict[str, Any] | str:
    """Apply or remove connectivity-template policies on application endpoints.

    Uses the ``obj-policy-batch-apply`` endpoint with ``async=full`` and PATCH.

    Args:
        blueprint_id: Blueprint UUID (MANDATORY).
        application_points: JSON string, single dict, or list of dicts, each with
            shape ``{"id": "<interface_id>", "policies": [{"policy": "<policy_id>", "used": true|false}]}``.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    try:
        normalized = normalize_application_points(application_points)
    except ValueError as e:
        return f"Invalid application_points: {e}"

    if not confirmed:
        decline = await _confirm(
            ctx,
            f"Apstra: apply/update {len(normalized)} connectivity-template policy binding(s) "
            f"in blueprint {blueprint_id}. Confirm?",
        )
        if decline:
            return decline

    try:
        client = await get_apstra_client()
        response = await client.request(
            "PATCH",
            f"/api/blueprints/{blueprint_id}/obj-policy-batch-apply",
            params={"async": "full"},
            json_body={"application_points": normalized},
        )
        data: Any
        try:
            data = response.json()
        except ValueError:
            data = response.text or "OK"
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_change_mgmt_guidelines(),
            "data": data,
        }
    except Exception as e:
        return f"Error applying CT policies: {format_http_error(e) if hasattr(e, 'response') else e}"
