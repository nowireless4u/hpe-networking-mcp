"""ClearPass global server configuration read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get


@tool(capability=Capability.READ)
async def clearpass_get_admin_users(
    ctx: Context,
    admin_user_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass admin user accounts.

    If admin_user_id is provided, returns a single admin user.
    Otherwise returns a paginated list of all admin users.

    Args:
        admin_user_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if admin_user_id:
            return await client.request("get", f"/admin-user/{admin_user_id}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/admin-user" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching admin users: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_admin_privileges(
    ctx: Context,
    admin_privilege_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass admin privilege definitions.

    If admin_privilege_id is provided, returns a single privilege definition.
    Otherwise returns a paginated list of all admin privileges.

    Args:
        admin_privilege_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if admin_privilege_id:
            return await client.request("get", f"/admin-privilege/{admin_privilege_id}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/admin-privilege" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching admin privileges: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_operator_profiles(
    ctx: Context,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass operator profiles (guest operator login profiles).

    Returns a paginated list of operator profiles used for guest management.

    Args:
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/operator-profile" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching operator profiles: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_licenses(
    ctx: Context,
    license_id: str | None = None,
) -> dict | str:
    """Get ClearPass application licenses.

    If license_id is provided, returns a single license entry.
    Otherwise returns the license summary for all installed licenses.

    Args:
        license_id: Numeric ID for single license lookup.
    """
    try:
        client = await get_clearpass_client()
        if license_id:
            return await client.request("get", f"/application-license/{license_id}")
        return await client.request("get", "/application-license/summary")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching licenses: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_cluster_params(
    ctx: Context,
) -> dict | str:
    """Get ClearPass cluster-wide configuration parameters.

    Returns global cluster settings such as zone configuration, virtual IP,
    and replication parameters.
    """
    try:
        client = await get_clearpass_client()
        return await client.request("get", "/cluster/parameters")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching cluster parameters: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_password_policies(
    ctx: Context,
) -> dict | str:
    """Get ClearPass password policies.

    Returns both the admin password policy and the local user password policy.
    """
    try:
        client = await get_clearpass_client()
        admin_policy = await client.request("get", "/admin-user/password-policy")
        local_user_policy = await client.request("get", "/local-user/password-policy")
        return {
            "admin_password_policy": admin_policy,
            "local_user_password_policy": local_user_policy,
        }
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching password policies: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_attributes(
    ctx: Context,
    attribute_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass custom attributes (dictionary attributes).

    If attribute_id is provided, returns a single attribute definition.
    Otherwise returns a paginated list of all attributes.

    Args:
        attribute_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if attribute_id:
            return await client.request("get", f"/attribute/{attribute_id}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/attribute" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching attributes: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_data_filters(
    ctx: Context,
    data_filter_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass data filters (role-based data visibility filters).

    If data_filter_id is provided, returns a single data filter.
    Otherwise returns a paginated list of all data filters.

    Args:
        data_filter_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if data_filter_id:
            return await client.request("get", f"/data-filter/{data_filter_id}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/data-filter" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching data filters: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_file_backup_servers(
    ctx: Context,
    file_backup_server_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass file backup server configurations.

    If file_backup_server_id is provided, returns a single backup server.
    Otherwise returns a paginated list of all configured backup servers.

    Args:
        file_backup_server_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if file_backup_server_id:
            return await client.request("get", f"/file-backup-server/{file_backup_server_id}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/file-backup-server" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching file backup servers: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_messaging_setup(
    ctx: Context,
) -> dict | str:
    """Get ClearPass messaging (SMTP/email) configuration.

    Returns the server-wide email/SMTP configuration used for notifications
    and guest account provisioning.
    """
    try:
        client = await get_clearpass_client()
        return await client.request("get", "/messaging-setup")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching messaging setup: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_snmp_trap_receivers(
    ctx: Context,
    snmp_trap_receiver_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass SNMP trap receiver configurations.

    If snmp_trap_receiver_id is provided, returns a single receiver.
    Otherwise returns a paginated list of all SNMP trap receivers.

    Args:
        snmp_trap_receiver_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if snmp_trap_receiver_id:
            return await client.request("get", f"/snmp-trap-receiver/{snmp_trap_receiver_id}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/snmp-trap-receiver" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching SNMP trap receivers: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_policy_manager_zones(
    ctx: Context,
    policy_manager_zones_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass Policy Manager zones.

    If policy_manager_zones_id is provided, returns a single zone.
    Otherwise returns a paginated list of all Policy Manager zones.

    Args:
        policy_manager_zones_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if policy_manager_zones_id:
            return await client.request("get", f"/server/policy-manager-zones/{policy_manager_zones_id}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/server/policy-manager-zones" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching Policy Manager zones: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_oauth_privileges(
    ctx: Context,
) -> dict | str:
    """Get all ClearPass OAuth2 privilege definitions.

    Returns the list of available OAuth2 privilege scopes that can be
    assigned to API clients.
    """
    try:
        client = await get_clearpass_client()
        return await clearpass_get(client, "/oauth/all-privileges")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching OAuth privileges: {e}"}) from e
