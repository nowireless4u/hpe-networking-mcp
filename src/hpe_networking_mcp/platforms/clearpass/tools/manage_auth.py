"""ClearPass authentication source and method write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.clearpass._registry import mcp
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import WRITE_DELETE

_SOURCE_ACTIONS = ("create", "update", "delete", "configure_backup", "configure_filters", "configure_radius_attrs")


async def _confirm_write(ctx: Context, action: str, identifier: str | None) -> dict | None:
    """Request user confirmation for destructive auth actions.

    Args:
        ctx: FastMCP context.
        action: The operation being performed.
        identifier: Item ID or name for display.

    Returns:
        Error dict if declined/canceled, None if accepted.
    """
    label = identifier or "unknown"
    elicit = await elicitation_handler(
        message=f"ClearPass: {action} '{label}'. Confirm?",
        ctx=ctx,
    )
    if elicit.action == "decline":
        mode = await ctx.get_state("elicitation_mode")
        if mode == "chat_confirm":
            return {
                "status": "confirmation_required",
                "message": f"Please confirm {action} of '{label}'. "
                "Call this tool again with confirmed=true after the user confirms.",
            }
        return {"message": "Action declined by user."}
    elif elicit.action == "cancel":
        return {"message": "Action canceled by user."}
    return None


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_auth_source(
    ctx: Context,
    action_type: Annotated[
        str,
        Field(
            description="Action: 'create', 'update', 'delete', "
            "'configure_backup', 'configure_filters', or 'configure_radius_attrs'."
        ),
    ],
    payload: Annotated[dict, Field(description="Auth source config payload. For delete: empty dict {}.")],
    auth_source_id: Annotated[str | None, Field(description="Auth source ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Auth source name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, delete, or configure a ClearPass authentication source.

    Authentication sources define where ClearPass validates credentials (e.g. Active Directory,
    LDAP, SQL database, token server, HTTP).

    Actions:
        create: Add a new auth source. Payload requires name and type at minimum.
        update: Modify an existing auth source.
        delete: Remove an auth source.
        configure_backup: Set backup server settings via payload (e.g. backup_servers list).
        configure_filters: Set auth source filters via payload (e.g. filter rules).
        configure_radius_attrs: Set RADIUS attribute mappings via payload.

    Args:
        action_type: Operation to perform.
        payload: JSON config body. Required for create/update/configure. Empty dict for delete.
        auth_source_id: Numeric ID. Required for update/delete/configure (or use name).
        name: Auth source name. Alternative to auth_source_id for update/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in _SOURCE_ACTIONS:
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_SOURCE_ACTIONS)}."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} auth source", auth_source_id or name)
        if decline:
            return decline

    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        return _execute_auth_source_action(client, action_type, payload, auth_source_id, name)
    except Exception as e:
        return f"Error managing auth source: {e}"


def _execute_auth_source_action(
    client, action_type: str, payload: dict, auth_source_id: str | None, name: str | None
) -> dict | str:
    """Execute the resolved auth source action.

    Args:
        client: pyclearpass ApiPolicyElements instance.
        action_type: Operation to perform.
        payload: Configuration payload.
        auth_source_id: Auth source ID.
        name: Auth source name.

    Returns:
        API response dict or error string.
    """
    if action_type == "create":
        return client._send_request("/auth-source", "post", query=payload)

    if not auth_source_id and not name:
        return "Either auth_source_id or name is required for this action."

    if action_type == "delete":
        if auth_source_id:
            return client.delete_auth_source_by_auth_source_id(auth_source_id=auth_source_id)
        return client.delete_auth_source_name_by_name(name=name)

    # update, configure_backup, configure_filters, configure_radius_attrs — all PATCH
    if auth_source_id:
        return client._send_request(f"/auth-source/{auth_source_id}", "patch", query=payload)
    return client._send_request(f"/auth-source/name/{name}", "patch", query=payload)


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_auth_method(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Auth method config payload. For delete: empty dict {}.")],
    auth_method_id: Annotated[str | None, Field(description="Auth method ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Auth method name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass authentication method.

    Authentication methods define how ClearPass authenticates users (e.g. PAP, CHAP,
    EAP-TLS, EAP-PEAP, MAC Auth).

    Args:
        action_type: Operation — 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        auth_method_id: Numeric ID. Required for update/delete (or use name).
        name: Auth method name. Alternative to auth_method_id for update/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} auth method", auth_method_id or name)
        if decline:
            return decline

    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)

        if action_type == "create":
            return client._send_request("/auth-method", "post", query=payload)
        if not auth_method_id and not name:
            return "Either auth_method_id or name is required for update/delete."
        if action_type == "update":
            if auth_method_id:
                return client._send_request(f"/auth-method/{auth_method_id}", "patch", query=payload)
            return client._send_request(f"/auth-method/name/{name}", "patch", query=payload)
        # delete
        if auth_method_id:
            return client.delete_auth_method_by_auth_method_id(auth_method_id=auth_method_id)
        return client.delete_auth_method_name_by_name(name=name)
    except Exception as e:
        return f"Error managing auth method: {e}"
