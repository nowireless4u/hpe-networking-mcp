"""ClearPass role and role mapping write tools."""

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
async def clearpass_manage_role(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Role config payload. For delete: empty dict {}.")],
    role_id: Annotated[str | None, Field(description="Role ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Role name (alternative to ID for update/delete).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
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
            return await client.request("post", "/role", json_body=payload)
        if not role_id and not name:
            raise ToolError({"status_code": 400, "message": "Either role_id or name is required for update/delete."})
        if action_type == "update":
            if role_id:
                return await client.request("patch", f"/role/{path_seg(role_id)}", json_body=payload)
            return await client.request("patch", f"/role/name/{path_seg(name)}", json_body=payload)
        # delete
        if role_id:
            return await client.request("delete", f"/role/{path_seg(role_id)}")
        return await client.request("delete", f"/role/name/{path_seg(name)}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing role: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_role_mapping(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Role mapping config payload. For delete: empty dict {}.")],
    role_mapping_id: Annotated[str | None, Field(description="Role mapping ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Role mapping name (alternative to ID for update/delete).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass role mapping policy.

    Role mappings define rules that assign roles to users based on attributes
    such as authentication source, user group, or endpoint profile.

    Args:
        action_type: Operation — 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        role_mapping_id: Numeric ID. Required for update/delete (or use name).
        name: Role mapping name. Alternative to role_mapping_id for update/delete.
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
            return await client.request("post", "/role-mapping", json_body=payload)
        if not role_mapping_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either role_mapping_id or name is required for update/delete."}
            )
        if action_type == "update":
            if role_mapping_id:
                return await client.request("patch", f"/role-mapping/{path_seg(role_mapping_id)}", json_body=payload)
            return await client.request("patch", f"/role-mapping/name/{path_seg(name)}", json_body=payload)
        # delete
        if role_mapping_id:
            return await client.request("delete", f"/role-mapping/{path_seg(role_mapping_id)}")
        return await client.request("delete", f"/role-mapping/name/{path_seg(name)}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing role mapping: {e}"}) from e
