"""ClearPass identity management read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


def _build_query_string(
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
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
        f"calculate_count={'true' if calculate_count else 'false'}",
    ]
    return "?" + "&".join(p for p in params if p)


@tool(annotations=READ_ONLY)
async def clearpass_get_api_clients(
    ctx: Context,
    client_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass API clients (OAuth2 client registrations).

    If client_id is provided, returns a single API client.
    Otherwise returns a paginated list of all API clients.

    Args:
        client_id: Client ID string for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+client_id" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_identities import ApiIdentities

        client = await get_clearpass_session(ApiIdentities)
        if client_id:
            return client.get_api_client_by_client_id(client_id=client_id)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/api-client" + query, "get")
    except Exception as e:
        return f"Error fetching API clients: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_local_users(
    ctx: Context,
    local_user_id: str | None = None,
    user_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass local user accounts.

    If local_user_id is provided, returns a single user by numeric ID.
    If user_id is provided, returns a single user by username.
    Otherwise returns a paginated list of all local users.

    Args:
        local_user_id: Numeric ID for single-item lookup.
        user_id: Username string for lookup by user ID.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+user_id" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_identities import ApiIdentities

        client = await get_clearpass_session(ApiIdentities)
        if local_user_id:
            return client.get_local_user_by_local_user_id(local_user_id=local_user_id)
        if user_id:
            return client.get_local_user_user_id_by_user_id(user_id=user_id)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/local-user" + query, "get")
    except Exception as e:
        return f"Error fetching local users: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_static_host_lists(
    ctx: Context,
    static_host_list_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass static host lists.

    If static_host_list_id or name is provided, returns a single host list.
    Otherwise returns a paginated list of all static host lists.

    Args:
        static_host_list_id: Numeric ID for single-item lookup.
        name: Host list name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_identities import ApiIdentities

        client = await get_clearpass_session(ApiIdentities)
        if static_host_list_id:
            return client.get_static_host_list_by_static_host_list_id(
                static_host_list_id=static_host_list_id,
            )
        if name:
            return client.get_static_host_list_name_by_name(name=name)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/static-host-list" + query, "get")
    except Exception as e:
        return f"Error fetching static host lists: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_devices(
    ctx: Context,
    device_id: str | None = None,
    macaddr: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass device accounts (onboarded devices).

    If device_id or macaddr is provided, returns a single device.
    Otherwise returns a paginated list of all device accounts.

    Args:
        device_id: Numeric ID for single-item lookup.
        macaddr: MAC address for lookup by MAC (e.g. "001122334455").
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_identities import ApiIdentities

        client = await get_clearpass_session(ApiIdentities)
        if device_id:
            return client.get_device_by_device_id(device_id=device_id)
        if macaddr:
            return client.get_device_mac_by_macaddr(macaddr=macaddr)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/device" + query, "get")
    except Exception as e:
        return f"Error fetching devices: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_deny_listed_users(
    ctx: Context,
    deny_listed_users_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass deny-listed (blacklisted) users.

    If deny_listed_users_id is provided, returns a single deny-listed user.
    Otherwise returns a paginated list of all deny-listed users.

    Args:
        deny_listed_users_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+user_id" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_identities import ApiIdentities

        client = await get_clearpass_session(ApiIdentities)
        if deny_listed_users_id:
            return client.get_deny_listed_users_by_deny_listed_users_id(
                deny_listed_users_id=deny_listed_users_id,
            )
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/deny-listed-users" + query, "get")
    except Exception as e:
        return f"Error fetching deny-listed users: {e}"
