"""ClearPass authentication source and method write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import ClearPassClient, get_clearpass_client

_SOURCE_ACTIONS = ("create", "update", "delete", "configure_backup", "configure_filters", "configure_radius_attrs")


async def _confirm_write(ctx: Context, action: str, identifier: str | None) -> dict | None:
    """Thin wrapper over :func:`middleware.elicitation.confirm_write`.

    Kept as a local helper so existing call sites don't change; the
    shared elicitation/decline/cancel logic now lives in the middleware
    (#148).
    """
    label = identifier or "unknown"
    return await confirm_write(ctx, f"ClearPass: {action} '{label}'. Confirm?")


@tool(capability=Capability.WRITE_DELETE)
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
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_SOURCE_ACTIONS)}.",
            }
        )

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} auth source", auth_source_id or name)
        if decline:
            return decline

    try:
        client = await get_clearpass_client()
        return await _execute_auth_source_action(client, action_type, payload, auth_source_id, name)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing auth source: {e}"}) from e


async def _execute_auth_source_action(
    client: ClearPassClient, action_type: str, payload: dict, auth_source_id: str | None, name: str | None
) -> dict | str:
    """Execute the resolved auth source action.

    Args:
        client: ClearPass API client.
        action_type: Operation to perform.
        payload: Configuration payload.
        auth_source_id: Auth source ID.
        name: Auth source name.

    Returns:
        API response dict or error string.
    """
    if action_type == "create":
        return await client.request("post", "/auth-source", json_body=payload)

    if not auth_source_id and not name:
        raise ToolError({"status_code": 400, "message": "Either auth_source_id or name is required for this action."})

    if action_type == "delete":
        if auth_source_id:
            return await client.request("delete", f"/auth-source/{auth_source_id}")
        return await client.request("delete", f"/auth-source/name/{name}")

    # update, configure_backup, configure_filters, configure_radius_attrs — all PATCH
    if auth_source_id:
        return await client.request("patch", f"/auth-source/{auth_source_id}", json_body=payload)
    return await client.request("patch", f"/auth-source/name/{name}", json_body=payload)


@tool(capability=Capability.WRITE_DELETE)
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
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} auth method", auth_method_id or name)
        if decline:
            return decline

    try:
        client = await get_clearpass_client()

        if action_type == "create":
            return await client.request("post", "/auth-method", json_body=payload)
        if not auth_method_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either auth_method_id or name is required for update/delete."}
            )
        if action_type == "update":
            if auth_method_id:
                return await client.request("patch", f"/auth-method/{auth_method_id}", json_body=payload)
            return await client.request("patch", f"/auth-method/name/{name}", json_body=payload)
        # delete
        if auth_method_id:
            return await client.request("delete", f"/auth-method/{auth_method_id}")
        return await client.request("delete", f"/auth-method/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing auth method: {e}"}) from e
