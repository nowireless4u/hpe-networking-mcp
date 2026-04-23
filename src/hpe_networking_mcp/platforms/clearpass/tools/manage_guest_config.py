"""ClearPass guest configuration write tools (templates, weblogins, settings)."""

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
    return await confirm_write(ctx, f"ClearPass: {action} guest config '{label}'. Confirm?")


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_pass_template(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', 'replace', or 'delete'.")],
    payload: Annotated[dict, Field(description="Template config payload. For delete: empty dict {}.")],
    template_id: Annotated[str | None, Field(description="Template ID (required for update/replace/delete).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, replace, or delete a ClearPass guest pass template.

    Pass templates define the layout and content of digital passes or printed receipts
    for guest accounts.

    Args:
        action_type: Operation — 'create', 'update', 'replace', or 'delete'.
        payload: JSON config body. Required for create/update/replace. Empty dict for delete.
        template_id: Numeric ID. Required for update/replace/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "replace", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', 'replace', or 'delete'."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} pass template", template_id)
        if decline:
            return decline

    try:
        from pyclearpass.api_guestconfiguration import ApiGuestConfiguration

        client = await get_clearpass_session(ApiGuestConfiguration)

        if action_type == "create":
            return client._send_request("/template/pass", "post", query=payload)
        if not template_id:
            return "template_id is required for update/replace/delete."
        if action_type == "update":
            return client._send_request(f"/template/pass/{template_id}", "patch", query=payload)
        if action_type == "replace":
            return client._send_request(f"/template/pass/{template_id}", "put", query=payload)
        return client.delete_template_pass_by_id(id=template_id)
    except Exception as e:
        return f"Error managing pass template: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_print_template(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', 'replace', or 'delete'.")],
    payload: Annotated[dict, Field(description="Template config payload. For delete: empty dict {}.")],
    template_id: Annotated[str | None, Field(description="Template ID (required for update/replace/delete).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, replace, or delete a ClearPass guest print template.

    Print templates define the layout for printed guest credentials.

    Args:
        action_type: Operation — 'create', 'update', 'replace', or 'delete'.
        payload: JSON config body. Required for create/update/replace. Empty dict for delete.
        template_id: Numeric ID. Required for update/replace/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "replace", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', 'replace', or 'delete'."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} print template", template_id)
        if decline:
            return decline

    try:
        from pyclearpass.api_guestconfiguration import ApiGuestConfiguration

        client = await get_clearpass_session(ApiGuestConfiguration)

        if action_type == "create":
            return client._send_request("/template/print", "post", query=payload)
        if not template_id:
            return "template_id is required for update/replace/delete."
        if action_type == "update":
            return client._send_request(f"/template/print/{template_id}", "patch", query=payload)
        if action_type == "replace":
            return client._send_request(f"/template/print/{template_id}", "put", query=payload)
        return client.delete_template_print_by_id(id=template_id)
    except Exception as e:
        return f"Error managing print template: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_weblogin_page(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', 'replace', or 'delete'.")],
    payload: Annotated[dict, Field(description="Weblogin page config payload. For delete: empty dict {}.")],
    page_id: Annotated[str | None, Field(description="Weblogin page ID (for update/replace/delete).")] = None,
    page_name: Annotated[str | None, Field(description="Weblogin page name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, replace, or delete a ClearPass weblogin (captive portal) page.

    Weblogin pages define the captive portal experience for guest and BYOD users.

    Args:
        action_type: Operation — 'create', 'update', 'replace', or 'delete'.
        payload: JSON config body. Required for create/update/replace. Empty dict for delete.
        page_id: Numeric ID. Required for update/replace/delete (or use page_name).
        page_name: Page name. Alternative to page_id for update/replace/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "replace", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', 'replace', or 'delete'."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} weblogin page", page_id or page_name)
        if decline:
            return decline

    try:
        from pyclearpass.api_guestconfiguration import ApiGuestConfiguration

        client = await get_clearpass_session(ApiGuestConfiguration)

        if action_type == "create":
            return client._send_request("/weblogin", "post", query=payload)
        if not page_id and not page_name:
            return "Either page_id or page_name is required for update/replace/delete."
        if action_type == "delete":
            if page_id:
                return client.delete_weblogin_by_id(id=page_id)
            return client.delete_weblogin_page_name_by_page_name(page_name=page_name)
        # update or replace
        path_suffix = f"/{page_id}" if page_id else f"/page-name/{page_name}"
        method = "patch" if action_type == "update" else "put"
        return client._send_request(f"/weblogin{path_suffix}", method, query=payload)
    except Exception as e:
        return f"Error managing weblogin page: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_guest_settings(
    ctx: Context,
    setting_type: Annotated[str, Field(description="Setting type: 'authentication' or 'manager'.")],
    payload: Annotated[dict, Field(description="Settings payload to apply.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Update ClearPass guest authentication or guest manager settings.

    Args:
        setting_type: Which settings to update — 'authentication' or 'manager'.
        payload: JSON settings body to apply.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if setting_type not in ("authentication", "manager"):
        return f"Invalid setting_type '{setting_type}'. Must be 'authentication' or 'manager'."

    if not confirmed:
        decline = await _confirm_write(ctx, f"update guest {setting_type} settings", setting_type)
        if decline:
            return decline

    try:
        from pyclearpass.api_guestconfiguration import ApiGuestConfiguration

        client = await get_clearpass_session(ApiGuestConfiguration)

        if setting_type == "authentication":
            return client._send_request("/guest/authentication", "patch", query=payload)
        return client._send_request("/guestmanager", "patch", query=payload)
    except Exception as e:
        return f"Error managing guest settings: {e}"
