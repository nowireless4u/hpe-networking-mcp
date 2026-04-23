"""ClearPass endpoint read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def clearpass_get_endpoints(
    ctx: Context,
    endpoint_id: str | None = None,
    mac_address: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
) -> dict | str:
    """Get ClearPass endpoints (known MAC addresses in the endpoint database).

    If endpoint_id or mac_address is provided, returns a single endpoint.
    Otherwise returns a paginated list of all endpoints.

    Args:
        endpoint_id: Numeric ID for single-item lookup.
        mac_address: MAC address for lookup (e.g. "001122334455" or "00:11:22:33:44:55").
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+mac_address" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_identities import ApiIdentities

        client = await get_clearpass_session(ApiIdentities)
        if endpoint_id:
            return client.get_endpoint_by_endpoint_id(endpoint_id=endpoint_id)
        if mac_address:
            return client.get_endpoint_mac_address_by_mac_address(mac_address=mac_address)
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return client._send_request("/endpoint" + query, "get")
    except Exception as e:
        return f"Error fetching endpoints: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_endpoint_profiler(
    ctx: Context,
    mac_or_ip: str,
) -> dict | str:
    """Get ClearPass endpoint profiler fingerprint data.

    Returns profiling and fingerprint information collected for a device,
    including DHCP fingerprint, HTTP user-agent, and device category.

    Args:
        mac_or_ip: MAC address or IP address of the endpoint to profile.
    """
    try:
        from pyclearpass.api_endpointvisibility import ApiEndpointVisibility

        client = await get_clearpass_session(ApiEndpointVisibility)
        return client.get_device_profiler_device_fingerprint_by_mac_or_ip(mac_or_ip=mac_or_ip)
    except Exception as e:
        return f"Error fetching endpoint profiler data: {e}"
