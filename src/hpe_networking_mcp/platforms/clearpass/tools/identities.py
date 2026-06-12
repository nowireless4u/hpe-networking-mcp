"""ClearPass identity management read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if client_id:
            return await client.request("get", f"/api-client/{path_seg(client_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/api-client" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching API clients: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if local_user_id:
            return await client.request("get", f"/local-user/{path_seg(local_user_id)}")
        if user_id:
            return await client.request("get", f"/local-user/user-id/{path_seg(user_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/local-user" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching local users: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if static_host_list_id:
            return await client.request("get", f"/static-host-list/{path_seg(static_host_list_id)}")
        if name:
            return await client.request("get", f"/static-host-list/name/{path_seg(name)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/static-host-list" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching static host lists: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if device_id:
            return await client.request("get", f"/device/{path_seg(device_id)}")
        if macaddr:
            return await client.request("get", f"/device/mac/{path_seg(macaddr)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/device" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching devices: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if deny_listed_users_id:
            return await client.request("get", f"/deny-listed-users/{path_seg(deny_listed_users_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/deny-listed-users" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching deny-listed users: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_external_accounts(
    ctx: Context,
    external_account_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass external account configurations.

    External accounts are credentials ClearPass uses to talk to outside
    services — e.g. Azure AD or Okta for federated authentication, MDM
    APIs for device-context lookups. Returns the configuration record,
    NOT the live session state.

    If external_account_id or name is provided, returns a single record.
    Otherwise returns a paginated list of all external accounts.

    Args:
        external_account_id: Numeric ID for single-item lookup.
        name: External account name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order. Default server-side: "+id".
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25, max 1000).
        calculate_count: When true, include total count in response.

    See: https://developer.arubanetworks.com/cppm/reference (Identities → /external-account)
    """
    try:
        client = await get_clearpass_client()
        if external_account_id:
            return await clearpass_get(client, f"/external-account/{path_seg(external_account_id)}")
        if name:
            return await clearpass_get(client, f"/external-account/name/{path_seg(name)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/external-account" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching external accounts: {e}"}) from e
