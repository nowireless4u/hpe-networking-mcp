"""ClearPass guest user write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_guest_user(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Guest config payload. For delete: empty dict {}.")],
    guest_id: Annotated[str | None, Field(description="Guest ID (required for update/delete).")] = None,
    username: Annotated[str | None, Field(description="Guest username (alternative to ID).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass guest user account.

    Args:
        action_type: Operation — 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        guest_id: Numeric ID. Required for update/delete (or use username).
        username: Guest username. Alternative to guest_id for update/delete.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )

    try:
        client = await get_clearpass_client()

        if action_type == "create":
            return await client.request("post", "/guest", json_body=payload)
        if not guest_id and not username:
            raise ToolError(
                {"status_code": 400, "message": "Either guest_id or username is required for update/delete."}
            )
        if action_type == "update":
            if guest_id:
                return await client.request("patch", f"/guest/{path_seg(guest_id)}", json_body=payload)
            return await client.request("patch", f"/guest/username/{path_seg(username)}", json_body=payload)
        # delete
        if guest_id:
            return await client.request("delete", f"/guest/{path_seg(guest_id)}")
        return await client.request("delete", f"/guest/username/{path_seg(username)}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing guest user: {e}"}) from e


@tool(capability=Capability.OPERATIONAL, enable_gated=True)
async def clearpass_send_guest_credentials(
    ctx: Context,
    guest_id: Annotated[str, Field(description="Guest ID to send credentials for.")],
    delivery_method: Annotated[str, Field(description="Delivery method: 'sms' or 'email'.")],
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Send guest account credentials via SMS or email.

    Args:
        guest_id: Numeric ID of the guest account.
        delivery_method: How to deliver credentials — 'sms' or 'email'.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if delivery_method not in ("sms", "email"):
        raise ToolError(
            {"status_code": 400, "message": f"Invalid delivery_method '{delivery_method}'. Must be 'sms' or 'email'."}
        )

    try:
        client = await get_clearpass_client()
        # Live-verified route (#469): /sendreceipt/sms|smtp with a required
        # confirm flag — the old /send-sms|send-email paths return HTTP 405.
        channel = "sms" if delivery_method == "sms" else "smtp"
        return await client.request(
            "post", f"/guest/{path_seg(guest_id)}/sendreceipt/{path_seg(channel)}", json_body={"confirm": 1}
        )
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error sending guest credentials: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_generate_guest_pass(
    ctx: Context,
    guest_id: Annotated[str, Field(description="Guest ID to render the pass for.")],
    pass_type: Annotated[str, Field(description="Pass type: 'digital' or 'receipt'.")],
    template_id: Annotated[str, Field(description="ID of the pass/receipt template to render with.")],
) -> dict | str:
    """Render a digital pass or receipt for a guest account.

    Live-verified route (#469): rendering is a GET against
    ``/guest/{id}/pass/{template_id}`` (or ``/receipt/{template_id}``) — the
    old body-less POSTs return HTTP 405. Rendering has no side effects, so
    this is a READ (no confirmation).

    Args:
        guest_id: Numeric ID of the guest account.
        pass_type: 'digital' renders a pass, 'receipt' renders a receipt.
        template_id: Pass/print template ID (see clearpass_get_pass_templates
            / clearpass_get_print_templates).
    """
    if pass_type not in ("digital", "receipt"):
        raise ToolError(
            {"status_code": 400, "message": f"Invalid pass_type '{pass_type}'. Must be 'digital' or 'receipt'."}
        )

    try:
        client = await get_clearpass_client()
        endpoint = "pass" if pass_type == "digital" else "receipt"  # nosec B105 — API path, not a password
        return await client.request("get", f"/guest/{path_seg(guest_id)}/{path_seg(endpoint)}/{path_seg(template_id)}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error rendering guest pass: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_process_sponsor_action(
    ctx: Context,
    guest_id: Annotated[str, Field(description="Guest ID to process sponsor action for.")],
    action: Annotated[str, Field(description="Sponsor action: 'approve' or 'reject'.")],
    token: Annotated[str, Field(description="Registration token from the sponsor confirmation link.")],
    register_token: Annotated[str, Field(description="Register token from the sponsor confirmation link.")],
    gsr_id: Annotated[
        str | None,
        Field(description="Optional self-registration name carrying the sponsor confirmation configuration."),
    ] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Process a sponsor approval or rejection for a guest account.

    Live-verified route (#469): one ``POST /guest/{id}/sponsor`` with the
    sponsor-confirmation tokens; rejection travels as ``register_reject`` in
    the body — the old ``/sponsor/approve|reject`` paths return HTTP 405.

    Args:
        guest_id: Numeric ID of the guest account awaiting sponsor action.
        action: Sponsor decision — 'approve' or 'reject'.
        token: Registration token (from the sponsor confirmation email/link).
        register_token: Register token paired with ``token``.
        gsr_id: Optional self-registration page name.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action not in ("approve", "reject"):
        raise ToolError({"status_code": 400, "message": f"Invalid action '{action}'. Must be 'approve' or 'reject'."})

    body: dict = {"token": token, "register_token": register_token}
    if action == "reject":
        body["register_reject"] = True

    try:
        client = await get_clearpass_client()
        return await client.request(
            "post",
            f"/guest/{path_seg(guest_id)}/sponsor",
            params={"gsr_id": gsr_id} if gsr_id else None,
            json_body=body,
        )
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error processing sponsor action: {e}"}) from e
