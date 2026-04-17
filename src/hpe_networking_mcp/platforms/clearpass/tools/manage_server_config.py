"""ClearPass global server configuration write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.clearpass._registry import mcp
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import WRITE_DELETE


async def _confirm_write(
    ctx: Context, action_type: str, resource: str, identifier: str | None, confirmed: bool
) -> dict | None:
    """Handle confirmation for update/delete actions.

    Args:
        ctx: FastMCP context.
        action_type: The operation being performed.
        resource: Resource type name for display.
        identifier: Resource ID or name for display.
        confirmed: Whether the user already confirmed.

    Returns:
        Error dict if declined/canceled, None if confirmed.
    """
    if action_type == "create" or confirmed:
        return None
    label = identifier or "unknown"
    elicit = await elicitation_handler(
        message=f"ClearPass: {action_type} {resource} '{label}'. Confirm?",
        ctx=ctx,
    )
    if elicit.action == "decline":
        mode = await ctx.get_state("elicitation_mode")
        if mode == "chat_confirm":
            return {
                "status": "confirmation_required",
                "message": f"Please confirm {action_type} of {resource} '{label}'. "
                "Call this tool again with confirmed=true after the user confirms.",
            }
        return {"message": "Action declined by user."}
    elif elicit.action == "cancel":
        return {"message": "Action canceled by user."}
    return None


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
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
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "admin user", admin_user_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if action_type == "create":
            return client._send_request("/admin-user", "post", query=payload)
        if not admin_user_id and not name:
            return "Either admin_user_id or name is required for update/delete."
        if action_type == "update":
            path = f"/admin-user/{admin_user_id}" if admin_user_id else f"/admin-user/name/{name}"
            return client._send_request(path, "patch", query=payload)
        if admin_user_id:
            return client.delete_admin_user_by_admin_user_id(admin_user_id=admin_user_id)
        return client._send_request(f"/admin-user/name/{name}", "delete")
    except Exception as e:
        return f"Error managing admin user: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
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
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "admin privilege", admin_privilege_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if action_type == "create":
            return client._send_request("/admin-privilege", "post", query=payload)
        if not admin_privilege_id and not name:
            return "Either admin_privilege_id or name is required for update/delete."
        if action_type == "update":
            path = f"/admin-privilege/{admin_privilege_id}" if admin_privilege_id else f"/admin-privilege/name/{name}"
            return client._send_request(path, "patch", query=payload)
        if admin_privilege_id:
            return client.delete_admin_privilege_by_admin_privilege_id(admin_privilege_id=admin_privilege_id)
        return client._send_request(f"/admin-privilege/name/{name}", "delete")
    except Exception as e:
        return f"Error managing admin privilege: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
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
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "operator profile", operator_profile_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if action_type == "create":
            return client._send_request("/operator-profile", "post", query=payload)
        if not operator_profile_id and not name:
            return "Either operator_profile_id or name is required for update/delete."
        if action_type == "update":
            path = (
                f"/operator-profile/{operator_profile_id}" if operator_profile_id else f"/operator-profile/name/{name}"
            )
            return client._send_request(path, "patch", query=payload)
        if operator_profile_id:
            return client.delete_operator_profile_by_operator_profile_id(operator_profile_id=operator_profile_id)
        return client._send_request(f"/operator-profile/name/{name}", "delete")
    except Exception as e:
        return f"Error managing operator profile: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
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
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."
    decline = await _confirm_write(ctx, action_type, "license", license_id, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if action_type == "create":
            return client._send_request("/application-license", "post", query=payload)
        if not license_id:
            return "license_id is required for delete/activate operations."
        if action_type == "delete":
            return client.delete_application_license_by_license_id(license_id=license_id)
        if action_type == "activate_online":
            return client.update_application_license_activate_online_by_license_id(license_id=license_id)
        return client.update_application_license_activate_offline_by_license_id(license_id=license_id)
    except Exception as e:
        return f"Error managing license: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
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
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        return client._send_request("/cluster/parameters", "patch", query=payload)
    except Exception as e:
        return f"Error managing cluster parameters: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_password_policy(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'update_admin' or 'update_local'.")],
    payload: Annotated[dict, Field(description="Password policy config payload.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Update ClearPass admin or local user password policy."""
    valid = ("update_admin", "update_local")
    if action_type not in valid:
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."
    decline = await _confirm_write(ctx, action_type, "password policy", action_type, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        path = "/admin-user/password-policy" if action_type == "update_admin" else "/local-user/password-policy"
        return client._send_request(path, "patch", query=payload)
    except Exception as e:
        return f"Error managing password policy: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_attribute(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Attribute config payload. Empty dict {} for delete.")],
    attribute_id: Annotated[str | None, Field(description="Attribute ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Attribute name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass attribute."""
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "attribute", attribute_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if action_type == "create":
            return client._send_request("/attribute", "post", query=payload)
        if not attribute_id and not name:
            return "Either attribute_id or name is required for update/delete."
        if action_type == "update":
            path = f"/attribute/{attribute_id}" if attribute_id else f"/attribute/name/{name}"
            return client._send_request(path, "patch", query=payload)
        if attribute_id:
            return client.delete_attribute_by_attribute_id(attribute_id=attribute_id)
        return client._send_request(f"/attribute/name/{name}", "delete")
    except Exception as e:
        return f"Error managing attribute: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
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
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "data filter", data_filter_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if action_type == "create":
            return client._send_request("/data-filter", "post", query=payload)
        if not data_filter_id and not name:
            return "Either data_filter_id or name is required for update/delete."
        if action_type == "update":
            path = f"/data-filter/{data_filter_id}" if data_filter_id else f"/data-filter/name/{name}"
            return client._send_request(path, "patch", query=payload)
        if data_filter_id:
            return client.delete_data_filter_by_data_filter_id(data_filter_id=data_filter_id)
        return client._send_request(f"/data-filter/name/{name}", "delete")
    except Exception as e:
        return f"Error managing data filter: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
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
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "file backup server", file_backup_server_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if action_type == "create":
            return client._send_request("/file-backup-server", "post", query=payload)
        if not file_backup_server_id and not name:
            return "Either file_backup_server_id or name is required for update/delete."
        if action_type == "update":
            path = (
                f"/file-backup-server/{file_backup_server_id}"
                if file_backup_server_id
                else f"/file-backup-server/name/{name}"
            )
            return client._send_request(path, "patch", query=payload)
        if file_backup_server_id:
            return client.delete_file_backup_server_by_file_backup_server_id(
                file_backup_server_id=file_backup_server_id
            )
        return client._send_request(f"/file-backup-server/name/{name}", "delete")
    except Exception as e:
        return f"Error managing file backup server: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_messaging_setup(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Messaging setup config payload. Empty dict {} for delete.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete the ClearPass messaging setup."""
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "messaging setup", "global", confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if action_type == "create":
            return client._send_request("/messaging-setup", "post", query=payload)
        if action_type == "update":
            return client._send_request("/messaging-setup", "patch", query=payload)
        return client.delete_messaging_setup()
    except Exception as e:
        return f"Error managing messaging setup: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
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
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "SNMP trap receiver", snmp_trap_receiver_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if action_type == "create":
            return client._send_request("/snmp-trap-receiver", "post", query=payload)
        if not snmp_trap_receiver_id and not name:
            return "Either snmp_trap_receiver_id or name is required for update/delete."
        if action_type == "update":
            path = (
                f"/snmp-trap-receiver/{snmp_trap_receiver_id}"
                if snmp_trap_receiver_id
                else f"/snmp-trap-receiver/name/{name}"
            )
            return client._send_request(path, "patch", query=payload)
        if snmp_trap_receiver_id:
            return client.delete_snmp_trap_receiver_by_snmp_trap_receiver_id(
                snmp_trap_receiver_id=snmp_trap_receiver_id
            )
        return client._send_request(f"/snmp-trap-receiver/name/{name}", "delete")
    except Exception as e:
        return f"Error managing SNMP trap receiver: {e}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
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
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "policy manager zone", policy_manager_zones_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if action_type == "create":
            return client._send_request("/server/policy-manager-zones", "post", query=payload)
        if not policy_manager_zones_id and not name:
            return "Either policy_manager_zones_id or name is required for update/delete."
        if action_type == "update":
            path = (
                f"/server/policy-manager-zones/{policy_manager_zones_id}"
                if policy_manager_zones_id
                else f"/server/policy-manager-zones/name/{name}"
            )
            return client._send_request(path, "patch", query=payload)
        if policy_manager_zones_id:
            return client.delete_server_policy_manager_zones_by_policy_manager_zones_id(
                policy_manager_zones_id=policy_manager_zones_id
            )
        return client._send_request(f"/server/policy-manager-zones/name/{name}", "delete")
    except Exception as e:
        return f"Error managing policy manager zone: {e}"
