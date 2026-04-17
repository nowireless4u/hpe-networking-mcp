"""ClearPass network device write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.clearpass._registry import mcp
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import WRITE_DELETE

_VALID_ACTIONS = (
    "create",
    "update",
    "delete",
    "clone",
    "configure_snmp",
    "configure_radsec",
    "configure_cli",
    "configure_onconnect",
)


async def _resolve_device_id(client, device_id: str | None, name: str | None) -> str | None:
    """Resolve a network device ID from device_id or name.

    Args:
        client: pyclearpass ApiPolicyElements instance.
        device_id: Numeric device ID (returned as-is if provided).
        name: Device name to look up.

    Returns:
        Resolved device ID string, or None if neither provided.
    """
    if device_id:
        return device_id
    if name:
        result = client.get_network_device_name_by_name(name=name)
        if isinstance(result, dict) and "id" in result:
            return str(result["id"])
    return None


async def _confirm_action(ctx: Context, action_type: str, device_id: str | None, name: str | None) -> dict | None:
    """Request user confirmation for destructive actions.

    Args:
        ctx: FastMCP context.
        action_type: The operation being performed.
        device_id: Device ID for display.
        name: Device name for display.

    Returns:
        Error dict if declined/canceled, None if accepted.
    """
    identifier = device_id or name or "unknown"
    elicit = await elicitation_handler(
        message=f"ClearPass: {action_type} network device '{identifier}'. Confirm?",
        ctx=ctx,
    )
    if elicit.action == "decline":
        mode = await ctx.get_state("elicitation_mode")
        if mode == "chat_confirm":
            return {
                "status": "confirmation_required",
                "message": f"Please confirm {action_type} of network device '{identifier}'. "
                "Call this tool again with confirmed=true after the user confirms.",
            }
        return {"message": "Action declined by user."}
    elif elicit.action == "cancel":
        return {"message": "Action canceled by user."}
    return None


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_network_device(
    ctx: Context,
    action_type: Annotated[
        str,
        Field(
            description="Action: 'create', 'update', 'delete', 'clone', "
            "'configure_snmp', 'configure_radsec', 'configure_cli', or 'configure_onconnect'."
        ),
    ],
    payload: Annotated[dict, Field(description="Configuration payload. For delete: empty dict {}.")],
    device_id: Annotated[str | None, Field(description="Device ID (required for update/delete/configure).")] = None,
    name: Annotated[str | None, Field(description="Device name (alternative to ID for update/delete).")] = None,
    source_device_id: Annotated[str | None, Field(description="Source device ID (required for clone).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, delete, clone, or configure a ClearPass network device (RADIUS/TACACS+ client).

    Actions:
        create: Add a new network device. Payload requires name and ip_address at minimum.
        update: Modify an existing device (by device_id or name).
        delete: Remove a device (by device_id or name).
        clone: Copy a device from source_device_id with payload overrides (must include new name/ip).
        configure_snmp: Set SNMP settings via payload (e.g. snmp_community_string, snmp_version).
        configure_radsec: Set RadSec settings via payload (e.g. radsec_enabled).
        configure_cli: Set CLI access settings via payload (e.g. cli_username, cli_password).
        configure_onconnect: Set OnConnect settings via payload (e.g. onConnect_enforcement_type).

    Args:
        action_type: Operation to perform.
        payload: JSON config body. Required for create/update/clone/configure. Empty dict for delete.
        device_id: Numeric ID. Required for update/delete/configure (or use name).
        name: Name lookup. Alternative to device_id for update/delete.
        source_device_id: Source device ID for clone action.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in _VALID_ACTIONS:
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_VALID_ACTIONS)}."

    if action_type != "create" and not confirmed:
        decline = await _confirm_action(ctx, action_type, device_id, name)
        if decline:
            return decline

    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        return await _execute_device_action(client, action_type, payload, device_id, name, source_device_id)
    except Exception as e:
        return f"Error managing network device: {e}"


async def _execute_device_action(
    client, action_type: str, payload: dict, device_id: str | None, name: str | None, source_device_id: str | None
) -> dict | str:
    """Execute the resolved network device action.

    Args:
        client: pyclearpass ApiPolicyElements instance.
        action_type: Operation to perform.
        payload: Configuration payload.
        device_id: Device ID for update/delete/configure.
        name: Device name for update/delete.
        source_device_id: Source device ID for clone.

    Returns:
        API response dict or error string.
    """
    if action_type == "create":
        return client._send_request("/network-device", "post", query=payload)

    if action_type == "clone":
        if not source_device_id:
            return "source_device_id is required for clone action."
        source = client.get_network_device_by_network_device_id(network_device_id=source_device_id)
        if not isinstance(source, dict):
            return f"Failed to retrieve source device {source_device_id}."
        source.pop("id", None)
        source.update(payload)
        return client._send_request("/network-device", "post", query=source)

    resolved_id = await _resolve_device_id(client, device_id, name)
    if not resolved_id and action_type == "delete" and name:
        return client.delete_network_device_name_by_name(name=name)
    if not resolved_id:
        return "Either device_id or name is required for this action."

    if action_type == "update":
        return client._send_request(f"/network-device/{resolved_id}", "patch", query=payload)
    if action_type == "delete":
        return client.delete_network_device_by_network_device_id(network_device_id=resolved_id)

    # configure_snmp, configure_radsec, configure_cli, configure_onconnect
    return client._send_request(f"/network-device/{resolved_id}", "patch", query=payload)
