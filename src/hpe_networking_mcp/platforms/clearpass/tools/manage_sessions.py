"""ClearPass session control write tools (disconnect, CoA)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.clearpass._registry import mcp
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import WRITE_DELETE

_VALID_TARGETS = ("session_id", "username", "mac", "ip", "bulk")


async def _confirm_session_action(ctx: Context, action: str, target_type: str, target: str | None) -> dict | None:
    """Request user confirmation for session control actions.

    Args:
        ctx: FastMCP context.
        action: The operation (disconnect or CoA).
        target_type: Target type (session_id, username, mac, ip, bulk).
        target: Target value for display.

    Returns:
        Error dict if declined/canceled, None if accepted.
    """
    label = f"{target_type}={target}" if target else target_type
    elicit = await elicitation_handler(
        message=f"ClearPass: {action} session for {label}. Confirm?",
        ctx=ctx,
    )
    if elicit.action == "decline":
        mode = await ctx.get_state("elicitation_mode")
        if mode == "chat_confirm":
            return {
                "status": "confirmation_required",
                "message": f"Please confirm {action} for {label}. "
                "Call this tool again with confirmed=true after the user confirms.",
            }
        return {"message": "Action declined by user."}
    elif elicit.action == "cancel":
        return {"message": "Action canceled by user."}
    return None


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_disconnect_session(
    ctx: Context,
    target_type: Annotated[str, Field(description="Target type: 'session_id', 'username', 'mac', 'ip', or 'bulk'.")],
    target_value: Annotated[
        str | None,
        Field(description="Target value (session ID, username, MAC, or IP). Not needed for bulk."),
    ] = None,
    filter: Annotated[
        dict | None,
        Field(description="Filter criteria for bulk disconnect (e.g. {'nasipaddress': '10.1.1.1'})."),
    ] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Disconnect an active ClearPass session (send RADIUS Disconnect-Request).

    Target types:
        session_id: Disconnect a single session by its ClearPass session ID.
        username: Disconnect all sessions for a username.
        mac: Disconnect all sessions for a MAC address.
        ip: Disconnect all sessions for a client IP.
        bulk: Disconnect sessions matching a filter criteria.

    Args:
        target_type: How to identify the session(s) to disconnect.
        target_value: The session ID, username, MAC, or IP. Not needed for bulk.
        filter: Filter dict for bulk operations. Used only when target_type is 'bulk'.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if target_type not in _VALID_TARGETS:
        return f"Invalid target_type '{target_type}'. Must be one of: {', '.join(_VALID_TARGETS)}."
    if target_type != "bulk" and not target_value:
        return f"target_value is required when target_type is '{target_type}'."
    if target_type == "bulk" and not filter:
        return "filter is required when target_type is 'bulk'."

    if not confirmed:
        decline = await _confirm_session_action(ctx, "disconnect", target_type, target_value)
        if decline:
            return decline

    try:
        from pyclearpass.api_sessioncontrol import ApiSessionControl

        client = await get_clearpass_session(ApiSessionControl)

        if target_type == "session_id":
            return client._send_request(f"/session/{target_value}/disconnect", "post", query={})
        if target_type == "bulk":
            return client._send_request("/session/disconnect", "post", query=filter)
        # username, mac, ip — use filtered disconnect
        filter_map = {"username": "username", "mac": "mac_address", "ip": "framedipaddress"}
        query = {filter_map[target_type]: target_value}
        return client._send_request("/session/disconnect", "post", query=query)
    except Exception as e:
        return f"Error disconnecting session: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_perform_coa(
    ctx: Context,
    target_type: Annotated[str, Field(description="Target type: 'session_id', 'username', 'mac', 'ip', or 'bulk'.")],
    target_value: Annotated[
        str | None,
        Field(description="Target value (session ID, username, MAC, or IP). Not needed for bulk."),
    ] = None,
    filter: Annotated[
        dict | None,
        Field(description="Filter criteria for bulk CoA (e.g. {'nasipaddress': '10.1.1.1'})."),
    ] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Perform a Change of Authorization (CoA) on active ClearPass sessions.

    Sends a RADIUS CoA to re-evaluate authorization for the targeted session(s),
    causing the NAS to re-authenticate the client with updated policies.

    Target types:
        session_id: CoA a single session by its ClearPass session ID.
        username: CoA all sessions for a username.
        mac: CoA all sessions for a MAC address.
        ip: CoA all sessions for a client IP.
        bulk: CoA sessions matching a filter criteria.

    Args:
        target_type: How to identify the session(s) for CoA.
        target_value: The session ID, username, MAC, or IP. Not needed for bulk.
        filter: Filter dict for bulk operations. Used only when target_type is 'bulk'.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if target_type not in _VALID_TARGETS:
        return f"Invalid target_type '{target_type}'. Must be one of: {', '.join(_VALID_TARGETS)}."
    if target_type != "bulk" and not target_value:
        return f"target_value is required when target_type is '{target_type}'."
    if target_type == "bulk" and not filter:
        return "filter is required when target_type is 'bulk'."

    if not confirmed:
        decline = await _confirm_session_action(ctx, "CoA", target_type, target_value)
        if decline:
            return decline

    try:
        from pyclearpass.api_sessioncontrol import ApiSessionControl

        client = await get_clearpass_session(ApiSessionControl)

        if target_type == "session_id":
            return client.get_session_by_id_reauthorize(id=target_value)
        if target_type == "bulk":
            return client._send_request("/session/reauthorize", "post", query=filter)
        # username, mac, ip — use filtered reauthorize
        filter_map = {"username": "username", "mac": "mac_address", "ip": "framedipaddress"}
        query = {filter_map[target_type]: target_value}
        return client._send_request("/session/reauthorize", "post", query=query)
    except Exception as e:
        return f"Error performing CoA: {e}"
