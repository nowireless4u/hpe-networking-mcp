"""ClearPass global server configuration read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import mcp
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


def _build_query_string(
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
) -> str:
    """Build ClearPass REST API query string for list endpoints.

    Args:
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset.
        limit: Max results per page.

    Returns:
        Query string starting with '?' for appending to a path.
    """
    params = [
        f"filter={filter}" if filter else "",
        f"sort={sort}" if sort else "",
        f"offset={offset}",
        f"limit={limit}",
    ]
    return "?" + "&".join(p for p in params if p)


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_admin_users(
    ctx: Context,
    admin_user_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
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
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if admin_user_id:
            return client.get_admin_user_by_admin_user_id(admin_user_id=admin_user_id)
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/admin-user" + query, "get")
    except Exception as e:
        return f"Error fetching admin users: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_admin_privileges(
    ctx: Context,
    admin_privilege_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
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
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if admin_privilege_id:
            return client.get_admin_privilege_by_admin_privilege_id(
                admin_privilege_id=admin_privilege_id,
            )
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/admin-privilege" + query, "get")
    except Exception as e:
        return f"Error fetching admin privileges: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_operator_profiles(
    ctx: Context,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
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
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/operator-profile" + query, "get")
    except Exception as e:
        return f"Error fetching operator profiles: {e}"


@mcp.tool(annotations=READ_ONLY)
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
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if license_id:
            return client.get_application_license_by_license_id(license_id=license_id)
        return client.get_application_license_summary()
    except Exception as e:
        return f"Error fetching licenses: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_cluster_params(
    ctx: Context,
) -> dict | str:
    """Get ClearPass cluster-wide configuration parameters.

    Returns global cluster settings such as zone configuration, virtual IP,
    and replication parameters.
    """
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        return client.get_cluster_parameters()
    except Exception as e:
        return f"Error fetching cluster parameters: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_password_policies(
    ctx: Context,
) -> dict | str:
    """Get ClearPass password policies.

    Returns both the admin password policy and the local user password policy.
    """
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        admin_policy = client.get_admin_password_policy()
        local_user_policy = client.get_local_user_password_policy()
        return {
            "admin_password_policy": admin_policy,
            "local_user_password_policy": local_user_policy,
        }
    except Exception as e:
        return f"Error fetching password policies: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_attributes(
    ctx: Context,
    attribute_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
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
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if attribute_id:
            return client.get_attribute_by_attribute_id(attribute_id=attribute_id)
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/attribute" + query, "get")
    except Exception as e:
        return f"Error fetching attributes: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_data_filters(
    ctx: Context,
    data_filter_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
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
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if data_filter_id:
            return client.get_data_filter_by_data_filter_id(data_filter_id=data_filter_id)
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/data-filter" + query, "get")
    except Exception as e:
        return f"Error fetching data filters: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_file_backup_servers(
    ctx: Context,
    file_backup_server_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
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
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if file_backup_server_id:
            return client.get_file_backup_server_by_file_backup_server_id(
                file_backup_server_id=file_backup_server_id,
            )
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/file-backup-server" + query, "get")
    except Exception as e:
        return f"Error fetching file backup servers: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_messaging_setup(
    ctx: Context,
) -> dict | str:
    """Get ClearPass messaging (SMTP/email) configuration.

    Returns the server-wide email/SMTP configuration used for notifications
    and guest account provisioning.
    """
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        return client.get_messaging_setup()
    except Exception as e:
        return f"Error fetching messaging setup: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_snmp_trap_receivers(
    ctx: Context,
    snmp_trap_receiver_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
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
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if snmp_trap_receiver_id:
            return client.get_snmp_trap_receiver_by_snmp_trap_receiver_id(
                snmp_trap_receiver_id=snmp_trap_receiver_id,
            )
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/snmp-trap-receiver" + query, "get")
    except Exception as e:
        return f"Error fetching SNMP trap receivers: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_policy_manager_zones(
    ctx: Context,
    policy_manager_zones_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
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
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        if policy_manager_zones_id:
            return client.get_server_policy_manager_zones_by_policy_manager_zones_id(
                policy_manager_zones_id=policy_manager_zones_id,
            )
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/server/policy-manager-zones" + query, "get")
    except Exception as e:
        return f"Error fetching Policy Manager zones: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_oauth_privileges(
    ctx: Context,
) -> dict | str:
    """Get all ClearPass OAuth2 privilege definitions.

    Returns the list of available OAuth2 privilege scopes that can be
    assigned to API clients.
    """
    try:
        from pyclearpass.api_globalserverconfiguration import ApiGlobalServerConfiguration

        client = await get_clearpass_session(ApiGlobalServerConfiguration)
        return client._send_request("/oauth/all-privileges", "get")
    except Exception as e:
        return f"Error fetching OAuth privileges: {e}"
