"""ClearPass endpoint write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.clearpass._registry import mcp
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import WRITE_DELETE


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_endpoint(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Endpoint config payload. For delete: empty dict {}.")],
    endpoint_id: Annotated[str | None, Field(description="Endpoint ID (required for update/delete).")] = None,
    mac_address: Annotated[
        str | None,
        Field(description="MAC address (alternative to ID for update/delete, e.g. '001122334455')."),
    ] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass endpoint in the endpoint database.

    Endpoints represent known MAC addresses tracked by ClearPass for profiling,
    posture assessment, and access control.

    Args:
        action_type: Operation — 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
            For create, must include mac_address at minimum.
        endpoint_id: Numeric ID. Required for update/delete (or use mac_address).
        mac_address: MAC address. Alternative to endpoint_id for update/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."

    if action_type != "create" and not confirmed:
        identifier = endpoint_id or mac_address or "unknown"
        elicit = await elicitation_handler(
            message=f"ClearPass: {action_type} endpoint '{identifier}'. Confirm?",
            ctx=ctx,
        )
        if elicit.action == "decline":
            mode = await ctx.get_state("elicitation_mode")
            if mode == "chat_confirm":
                return {
                    "status": "confirmation_required",
                    "message": f"Please confirm {action_type} of endpoint '{identifier}'. "
                    "Call this tool again with confirmed=true after the user confirms.",
                }
            return {"message": "Action declined by user."}
        elif elicit.action == "cancel":
            return {"message": "Action canceled by user."}

    try:
        from pyclearpass.api_identities import ApiIdentities

        client = await get_clearpass_session(ApiIdentities)

        if action_type == "create":
            return client._send_request("/endpoint", "post", query=payload)

        if not endpoint_id and not mac_address:
            return "Either endpoint_id or mac_address is required for update/delete."

        if action_type == "update":
            if endpoint_id:
                return client._send_request(f"/endpoint/{endpoint_id}", "patch", query=payload)
            return client._send_request(f"/endpoint/mac-address/{mac_address}", "patch", query=payload)

        # delete
        if endpoint_id:
            return client.delete_endpoint_by_endpoint_id(endpoint_id=endpoint_id)
        return client.delete_endpoint_mac_address_by_mac_address(mac_address=mac_address)
    except Exception as e:
        return f"Error managing endpoint: {e}"
