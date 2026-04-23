"""ClearPass role and role mapping write tools."""

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
    return await confirm_write(ctx, f"ClearPass: {action} '{label}'. Confirm?")


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_role(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Role config payload. For delete: empty dict {}.")],
    role_id: Annotated[str | None, Field(description="Role ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Role name (alternative to ID for update/delete).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass role.

    Roles define access levels assigned to users and devices during authentication.
    They are referenced by enforcement policies and role mappings.

    Args:
        action_type: Operation — 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
            For create, must include name at minimum.
        role_id: Numeric ID. Required for update/delete (or use name).
        name: Role name. Alternative to role_id for update/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} role", role_id or name)
        if decline:
            return decline

    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)

        if action_type == "create":
            return client._send_request("/role", "post", query=payload)
        if not role_id and not name:
            return "Either role_id or name is required for update/delete."
        if action_type == "update":
            if role_id:
                return client._send_request(f"/role/{role_id}", "patch", query=payload)
            return client._send_request(f"/role/name/{name}", "patch", query=payload)
        # delete
        if role_id:
            return client.delete_role_by_role_id(role_id=role_id)
        return client.delete_role_name_by_name(name=name)
    except Exception as e:
        return f"Error managing role: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_role_mapping(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Role mapping config payload. For delete: empty dict {}.")],
    role_mapping_id: Annotated[str | None, Field(description="Role mapping ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Role mapping name (alternative to ID for update/delete).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass role mapping policy.

    Role mappings define rules that assign roles to users based on attributes
    such as authentication source, user group, or endpoint profile.

    Args:
        action_type: Operation — 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        role_mapping_id: Numeric ID. Required for update/delete (or use name).
        name: Role mapping name. Alternative to role_mapping_id for update/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} role mapping", role_mapping_id or name)
        if decline:
            return decline

    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)

        if action_type == "create":
            return client._send_request("/role-mapping", "post", query=payload)
        if not role_mapping_id and not name:
            return "Either role_mapping_id or name is required for update/delete."
        if action_type == "update":
            if role_mapping_id:
                return client._send_request(f"/role-mapping/{role_mapping_id}", "patch", query=payload)
            return client._send_request(f"/role-mapping/name/{name}", "patch", query=payload)
        # delete
        if role_mapping_id:
            return client.delete_role_mapping_by_role_mapping_id(role_mapping_id=role_mapping_id)
        return client.delete_role_mapping_name_by_name(name=name)
    except Exception as e:
        return f"Error managing role mapping: {e}"
