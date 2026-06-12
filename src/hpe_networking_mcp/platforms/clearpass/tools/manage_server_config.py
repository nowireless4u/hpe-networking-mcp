"""ClearPass global server configuration write tools."""

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
async def clearpass_manage_admin_user(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Admin user config payload. Empty dict {} for delete.")],
    admin_user_id: Annotated[str | None, Field(description="Admin user ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Admin username (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass admin user."""
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "admin user", admin_user_id or name, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/admin-user", json_body=payload)
        if not admin_user_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either admin_user_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = f"/admin-user/{admin_user_id}" if admin_user_id else f"/admin-user/user-id/{name}"
            return await client.request("patch", path, json_body=payload)
        if admin_user_id:
            return await client.request("delete", f"/admin-user/{admin_user_id}")
        return await client.request("delete", f"/admin-user/user-id/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing admin user: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_admin_privilege(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Admin privilege config payload. Empty dict {} for delete.")],
    admin_privilege_id: Annotated[str | None, Field(description="Privilege ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Privilege name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass admin privilege."""
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "admin privilege", admin_privilege_id or name, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/admin-privilege", json_body=payload)
        if not admin_privilege_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either admin_privilege_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = f"/admin-privilege/{admin_privilege_id}" if admin_privilege_id else f"/admin-privilege/name/{name}"
            return await client.request("patch", path, json_body=payload)
        if admin_privilege_id:
            return await client.request("delete", f"/admin-privilege/{admin_privilege_id}")
        return await client.request("delete", f"/admin-privilege/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing admin privilege: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_operator_profile(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Operator profile config payload. Empty dict {} for delete.")],
    operator_profile_id: Annotated[
        str | None, Field(description="Operator profile ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Profile name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass operator profile."""
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "operator profile", operator_profile_id or name, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/operator-profile", json_body=payload)
        if not operator_profile_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either operator_profile_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = (
                f"/operator-profile/{operator_profile_id}" if operator_profile_id else f"/operator-profile/name/{name}"
            )
            return await client.request("patch", path, json_body=payload)
        if operator_profile_id:
            return await client.request("delete", f"/operator-profile/{operator_profile_id}")
        return await client.request("delete", f"/operator-profile/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing operator profile: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_license(
    ctx: Context,
    action_type: Annotated[
        str, Field(description="Action: 'create', 'delete', 'activate_online', or 'activate_offline'.")
    ],
    payload: Annotated[dict, Field(description="License config payload. Empty dict {} for delete.")],
    license_id: Annotated[str | None, Field(description="License ID (required for delete/activate).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, delete, or activate a ClearPass application license."""
    valid = ("create", "delete", "activate_online", "activate_offline")
    if action_type not in valid:
        raise ToolError(
            {"status_code": 400, "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."}
        )
    decline = await _confirm_write(ctx, action_type, "license", license_id, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/application-license", json_body=payload)
        if not license_id:
            raise ToolError({"status_code": 400, "message": "license_id is required for delete/activate operations."})
        if action_type == "delete":
            return await client.request("delete", f"/application-license/{license_id}")
        if action_type == "activate_online":
            return await client.request("patch", f"/application-license/activate-online/{license_id}")
        return await client.request("patch", f"/application-license/activate-offline/{license_id}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing license: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_cluster_params(
    ctx: Context,
    payload: Annotated[dict, Field(description="Cluster parameters config payload.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Update ClearPass cluster parameters."""
    decline = await _confirm_write(ctx, "update", "cluster parameters", "global", confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        return await client.request("patch", "/cluster/parameters", json_body=payload)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing cluster parameters: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_password_policy(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'update_admin' or 'update_local'.")],
    payload: Annotated[dict, Field(description="Password policy config payload.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Update ClearPass admin or local user password policy."""
    valid = ("update_admin", "update_local")
    if action_type not in valid:
        raise ToolError(
            {"status_code": 400, "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."}
        )
    decline = await _confirm_write(ctx, action_type, "password policy", action_type, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        path = "/admin-user/password-policy" if action_type == "update_admin" else "/local-user/password-policy"
        return await client.request("patch", path, json_body=payload)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing password policy: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_attribute(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Attribute config payload. Empty dict {} for delete.")],
    attribute_id: Annotated[str | None, Field(description="Attribute ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Attribute name (alternative to ID; requires entity_name).")] = None,
    entity_name: Annotated[
        str | None,
        Field(
            description=(
                "Entity the attribute belongs to (e.g. 'Endpoint', 'Device', 'GuestUser', "
                "'LocalUser', 'Onboard'). Required when selecting by name."
            )
        ),
    ] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass attribute."""
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "attribute", attribute_id or name, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/attribute", json_body=payload)
        if not attribute_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either attribute_id or name is required for update/delete."}
            )
        if name and not entity_name:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": "entity_name is required when selecting an attribute by name "
                    "(the API route is /attribute/{entity_name}/name/{name}).",
                }
            )
        if action_type == "update":
            path = f"/attribute/{attribute_id}" if attribute_id else f"/attribute/{entity_name}/name/{name}"
            return await client.request("patch", path, json_body=payload)
        if attribute_id:
            return await client.request("delete", f"/attribute/{attribute_id}")
        return await client.request("delete", f"/attribute/{entity_name}/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing attribute: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_data_filter(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Data filter config payload. Empty dict {} for delete.")],
    data_filter_id: Annotated[str | None, Field(description="Data filter ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Filter name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass data filter."""
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "data filter", data_filter_id or name, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/data-filter", json_body=payload)
        if not data_filter_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either data_filter_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = f"/data-filter/{data_filter_id}" if data_filter_id else f"/data-filter/name/{name}"
            return await client.request("patch", path, json_body=payload)
        if data_filter_id:
            return await client.request("delete", f"/data-filter/{data_filter_id}")
        return await client.request("delete", f"/data-filter/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing data filter: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_file_backup_server(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Backup server config payload. Empty dict {} for delete.")],
    file_backup_server_id: Annotated[
        str | None, Field(description="Backup server ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Server name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass file backup server."""
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "file backup server", file_backup_server_id or name, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/file-backup-server", json_body=payload)
        if not file_backup_server_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either file_backup_server_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = (
                f"/file-backup-server/{file_backup_server_id}"
                if file_backup_server_id
                else f"/file-backup-server/host-address/{name}"
            )
            return await client.request("patch", path, json_body=payload)
        if file_backup_server_id:
            return await client.request("delete", f"/file-backup-server/{file_backup_server_id}")
        return await client.request("delete", f"/file-backup-server/host-address/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing file backup server: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_messaging_setup(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Messaging setup config payload. Empty dict {} for delete.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete the ClearPass messaging setup."""
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "messaging setup", "global", confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/messaging-setup", json_body=payload)
        if action_type == "update":
            return await client.request("patch", "/messaging-setup", json_body=payload)
        return await client.request("delete", "/messaging-setup")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing messaging setup: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_snmp_trap_receiver(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="SNMP trap receiver config payload. Empty dict {} for delete.")],
    snmp_trap_receiver_id: Annotated[
        str | None, Field(description="SNMP trap receiver ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Receiver name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass SNMP trap receiver."""
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "SNMP trap receiver", snmp_trap_receiver_id or name, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/snmp-trap-receiver", json_body=payload)
        if not snmp_trap_receiver_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either snmp_trap_receiver_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = (
                f"/snmp-trap-receiver/{snmp_trap_receiver_id}"
                if snmp_trap_receiver_id
                else f"/snmp-trap-receiver/name/{name}"
            )
            return await client.request("patch", path, json_body=payload)
        if snmp_trap_receiver_id:
            return await client.request("delete", f"/snmp-trap-receiver/{snmp_trap_receiver_id}")
        return await client.request("delete", f"/snmp-trap-receiver/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing SNMP trap receiver: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_policy_manager_zone(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Policy manager zone config payload. Empty dict {} for delete.")],
    policy_manager_zones_id: Annotated[
        str | None, Field(description="Policy manager zone ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Zone name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass policy manager zone."""
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "policy manager zone", policy_manager_zones_id or name, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/server/policy-manager-zones", json_body=payload)
        if not policy_manager_zones_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either policy_manager_zones_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = (
                f"/server/policy-manager-zones/{policy_manager_zones_id}"
                if policy_manager_zones_id
                else f"/server/policy-manager-zones/name/{name}"
            )
            return await client.request("put", path, json_body=payload)
        if policy_manager_zones_id:
            return await client.request("delete", f"/server/policy-manager-zones/{policy_manager_zones_id}")
        return await client.request("delete", f"/server/policy-manager-zones/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing policy manager zone: {e}"}) from e
