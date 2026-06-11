"""ClearPass identity management write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client


async def _confirm_write(
    ctx: Context, action_type: str, resource: str, identifier: str | None, confirmed: bool
) -> dict | None:
    """Thin wrapper over :func:`middleware.elicitation.confirm_write`.

    Kept as a local helper so existing call sites don't change; the
    shared elicitation/decline/cancel logic now lives in the middleware
    (#148).
    """
    label = identifier or "unknown"
    return await confirm_write(ctx, f"ClearPass: {action_type} {resource} '{label}'. Confirm?")


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_api_client(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="API client config payload. Empty dict {} for delete.")],
    client_id: Annotated[str | None, Field(description="API client ID (required for update/delete).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass API client.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        client_id: API client ID. Required for update/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "API client", client_id, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/api-client", json_body=payload)
        if not client_id:
            raise ToolError({"status_code": 400, "message": "client_id is required for update/delete."})
        if action_type == "update":
            return await client.request("patch", f"/api-client/{client_id}", json_body=payload)
        return await client.request("delete", f"/api-client/{client_id}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing API client: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_local_user(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Local user config payload. Empty dict {} for delete.")],
    local_user_id: Annotated[str | None, Field(description="Local user ID (required for update/delete).")] = None,
    user_id: Annotated[str | None, Field(description="Username (alternative to local_user_id).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass local user.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        local_user_id: Numeric local user ID. Required for update/delete (or use user_id).
        user_id: Username string. Alternative to local_user_id for update/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "local user", local_user_id or user_id, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/local-user", json_body=payload)
        if not local_user_id and not user_id:
            raise ToolError(
                {"status_code": 400, "message": "Either local_user_id or user_id is required for update/delete."}
            )
        if action_type == "update":
            path = f"/local-user/{local_user_id}" if local_user_id else f"/local-user/user-id/{user_id}"
            return await client.request("patch", path, json_body=payload)
        if local_user_id:
            return await client.request("delete", f"/local-user/{local_user_id}")
        return await client.request("delete", f"/local-user/user-id/{user_id}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing local user: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_static_host_list(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Static host list config payload. Empty dict {} for delete.")],
    static_host_list_id: Annotated[
        str | None, Field(description="Static host list ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Host list name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass static host list.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        static_host_list_id: Numeric ID. Required for update/delete (or use name).
        name: Host list name. Alternative to static_host_list_id.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "static host list", static_host_list_id or name, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/static-host-list", json_body=payload)
        if not static_host_list_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either static_host_list_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = (
                f"/static-host-list/{static_host_list_id}" if static_host_list_id else f"/static-host-list/name/{name}"
            )
            return await client.request("patch", path, json_body=payload)
        if static_host_list_id:
            return await client.request("delete", f"/static-host-list/{static_host_list_id}")
        return await client.request("delete", f"/static-host-list/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing static host list: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_device(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Device config payload. Empty dict {} for delete.")],
    device_id: Annotated[str | None, Field(description="Device ID (required for update/delete).")] = None,
    macaddr: Annotated[str | None, Field(description="MAC address (alternative to device_id).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass network device.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        device_id: Numeric device ID. Required for update/delete (or use macaddr).
        macaddr: Device MAC address. Alternative to device_id.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "device", device_id or macaddr, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/device", json_body=payload)
        if not device_id and not macaddr:
            raise ToolError(
                {"status_code": 400, "message": "Either device_id or macaddr is required for update/delete."}
            )
        if action_type == "update":
            path = f"/device/{device_id}" if device_id else f"/device/mac/{macaddr}"
            return await client.request("patch", path, json_body=payload)
        if device_id:
            return await client.request("delete", f"/device/{device_id}")
        return await client.request("delete", f"/device/mac/{macaddr}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing device: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_deny_listed_user(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create' or 'delete'.")],
    payload: Annotated[dict, Field(description="Deny-listed user config payload. Empty dict {} for delete.")],
    deny_listed_users_id: Annotated[str | None, Field(description="Deny-listed user ID (required for delete).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create or delete a ClearPass deny-listed user.

    Args:
        action_type: Operation -- 'create' or 'delete'.
        payload: JSON config body. Required for create. Empty dict for delete.
        deny_listed_users_id: Numeric ID. Required for delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "delete"):
        raise ToolError(
            {"status_code": 400, "message": f"Invalid action_type '{action_type}'. Must be 'create' or 'delete'."}
        )
    decline = await _confirm_write(ctx, action_type, "deny-listed user", deny_listed_users_id, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/deny-listed-users", json_body=payload)
        if not deny_listed_users_id:
            raise ToolError({"status_code": 400, "message": "deny_listed_users_id is required for delete."})
        return await client.request("delete", f"/deny-listed-users/{deny_listed_users_id}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing deny-listed user: {e}"}) from e
