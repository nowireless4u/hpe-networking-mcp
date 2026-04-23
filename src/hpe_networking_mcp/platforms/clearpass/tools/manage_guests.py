"""ClearPass guest user write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import WRITE_DELETE


async def _confirm_write(ctx: Context, action: str, identifier: str | None) -> dict | None:
    """Thin wrapper over :func:`middleware.elicitation.confirm_write`.

    Kept as a local helper so existing call sites don't change; the
    shared elicitation/decline/cancel logic now lives in the middleware
    (#148).
    """
    label = identifier or "unknown"
    return await confirm_write(ctx, f"ClearPass: {action} guest '{label}'. Confirm?")


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_guest_user(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Guest config payload. For delete: empty dict {}.")],
    guest_id: Annotated[str | None, Field(description="Guest ID (required for update/delete).")] = None,
    username: Annotated[str | None, Field(description="Guest username (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass guest user account.

    Args:
        action_type: Operation — 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        guest_id: Numeric ID. Required for update/delete (or use username).
        username: Guest username. Alternative to guest_id for update/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, action_type, guest_id or username)
        if decline:
            return decline

    try:
        from pyclearpass.api_identities import ApiIdentities

        client = await get_clearpass_session(ApiIdentities)

        if action_type == "create":
            return client._send_request("/guest", "post", query=payload)
        if not guest_id and not username:
            return "Either guest_id or username is required for update/delete."
        if action_type == "update":
            if guest_id:
                return client._send_request(f"/guest/{guest_id}", "patch", query=payload)
            return client._send_request(f"/guest/username/{username}", "patch", query=payload)
        # delete
        if guest_id:
            return client.delete_guest_by_guest_id(guest_id=guest_id)
        return client.delete_guest_username_by_username(username=username)
    except Exception as e:
        return f"Error managing guest user: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_send_guest_credentials(
    ctx: Context,
    guest_id: Annotated[str, Field(description="Guest ID to send credentials for.")],
    delivery_method: Annotated[str, Field(description="Delivery method: 'sms' or 'email'.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Send guest account credentials via SMS or email.

    Args:
        guest_id: Numeric ID of the guest account.
        delivery_method: How to deliver credentials — 'sms' or 'email'.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if delivery_method not in ("sms", "email"):
        return f"Invalid delivery_method '{delivery_method}'. Must be 'sms' or 'email'."

    if not confirmed:
        decline = await _confirm_write(ctx, f"send credentials via {delivery_method}", guest_id)
        if decline:
            return decline

    try:
        from pyclearpass.api_guestactions import ApiGuestActions

        client = await get_clearpass_session(ApiGuestActions)
        return client._send_request(f"/guest/{guest_id}/send-{delivery_method}", "post", query={})
    except Exception as e:
        return f"Error sending guest credentials: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_generate_guest_pass(
    ctx: Context,
    guest_id: Annotated[str, Field(description="Guest ID to generate pass for.")],
    pass_type: Annotated[str, Field(description="Pass type: 'digital' or 'receipt'.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Generate a digital pass or receipt for a guest account.

    Args:
        guest_id: Numeric ID of the guest account.
        pass_type: Type of pass — 'digital' generates a digital pass, 'receipt' generates a receipt.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if pass_type not in ("digital", "receipt"):
        return f"Invalid pass_type '{pass_type}'. Must be 'digital' or 'receipt'."

    if not confirmed:
        decline = await _confirm_write(ctx, f"generate {pass_type} pass", guest_id)
        if decline:
            return decline

    try:
        from pyclearpass.api_guestactions import ApiGuestActions

        client = await get_clearpass_session(ApiGuestActions)
        endpoint = "pass" if pass_type == "digital" else "receipt"  # nosec B105 — API path, not a password
        return client._send_request(f"/guest/{guest_id}/{endpoint}", "post", query={})
    except Exception as e:
        return f"Error generating guest pass: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_process_sponsor_action(
    ctx: Context,
    guest_id: Annotated[str, Field(description="Guest ID to process sponsor action for.")],
    action: Annotated[str, Field(description="Sponsor action: 'approve' or 'reject'.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Process a sponsor approval or rejection for a guest account.

    Args:
        guest_id: Numeric ID of the guest account awaiting sponsor action.
        action: Sponsor decision — 'approve' or 'reject'.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action not in ("approve", "reject"):
        return f"Invalid action '{action}'. Must be 'approve' or 'reject'."

    if not confirmed:
        decline = await _confirm_write(ctx, f"sponsor {action}", guest_id)
        if decline:
            return decline

    try:
        from pyclearpass.api_guestactions import ApiGuestActions

        client = await get_clearpass_session(ApiGuestActions)
        return client._send_request(f"/guest/{guest_id}/sponsor/{action}", "post", query={})
    except Exception as e:
        return f"Error processing sponsor action: {e}"
