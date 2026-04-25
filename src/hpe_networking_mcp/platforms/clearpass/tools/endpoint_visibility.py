"""ClearPass endpoint-visibility read tools.

Covers OnGuard posture activity + settings, network discovery scans, and
the profiler fingerprint dictionary. All standard Apigility list-style
endpoints (filter / sort / offset / limit / calculate_count).

See: https://developer.arubanetworks.com/cppm/reference (Endpoint Visibility)
"""

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
    """Build ClearPass REST API query string for list endpoints."""
    params = [
        f"filter={filter}" if filter else "",
        f"sort={sort}" if sort else "",
        f"offset={offset}",
        f"limit={limit}",
        f"calculate_count={'true' if calculate_count else 'false'}",
    ]
    return "?" + "&".join(p for p in params if p)


@tool(annotations=READ_ONLY)
async def clearpass_get_onguard_activity(
    ctx: Context,
    activity_id: str | None = None,
    mac: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass OnGuard activity records (active posture sessions).

    If activity_id or mac is provided, returns a single record.
    Otherwise returns a paginated list of all OnGuard activity entries.

    Args:
        activity_id: Numeric ID for single-item lookup.
        mac: MAC address to look up activity for a specific endpoint.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+id" or "-id"). Default server-side: "+id".
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25, max 1000).
        calculate_count: When true, include total count in response.

    See: https://developer.arubanetworks.com/cppm/reference (Endpoint Visibility → /onguard-activity)
    """
    try:
        from pyclearpass.api_endpointvisibility import ApiEndpointVisibility

        client = await get_clearpass_session(ApiEndpointVisibility)
        if activity_id:
            return client._send_request(f"/onguard-activity/{activity_id}", "get")
        if mac:
            return client._send_request(f"/onguard-activity/mac/{mac}", "get")
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/onguard-activity" + query, "get")
    except Exception as e:
        return f"Error fetching OnGuard activity: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_fingerprint_dictionary(
    ctx: Context,
    fingerprint_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass profiler fingerprint dictionary entries.

    Fingerprints are device-classification patterns (DHCP options, HTTP
    user-agent, etc.) that ClearPass uses to profile endpoints into
    categories like ``Computer/Windows``, ``SmartDevice/iOS``, etc.

    If fingerprint_id is provided, returns a single fingerprint.
    Otherwise returns a paginated list of all fingerprint dictionary entries.

    Args:
        fingerprint_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order. Default server-side: "+id".
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25, max 1000).
        calculate_count: When true, include total count in response.

    See: https://developer.arubanetworks.com/cppm/reference (Endpoint Visibility → /fingerprint-dictionary)
    """
    try:
        from pyclearpass.api_endpointvisibility import ApiEndpointVisibility

        client = await get_clearpass_session(ApiEndpointVisibility)
        if fingerprint_id:
            return client._send_request(f"/fingerprint/{fingerprint_id}", "get")
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/fingerprint" + query, "get")
    except Exception as e:
        return f"Error fetching fingerprint dictionary: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_network_scan(
    ctx: Context,
    scan_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass network discovery scan jobs.

    Network scans are configured discovery operations that probe a subnet
    or IP range for devices and feed the results into the endpoint
    profiler.

    If scan_id is provided, returns a single scan job.
    Otherwise returns a paginated list of all network scans.

    Args:
        scan_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order. Default server-side: "+id".
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25, max 1000).
        calculate_count: When true, include total count in response.

    See: https://developer.arubanetworks.com/cppm/reference (Endpoint Visibility → /network-scan)
    """
    try:
        from pyclearpass.api_endpointvisibility import ApiEndpointVisibility

        client = await get_clearpass_session(ApiEndpointVisibility)
        if scan_id:
            return client._send_request(f"/config/network-scan/{scan_id}", "get")
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/config/network-scan" + query, "get")
    except Exception as e:
        return f"Error fetching network scans: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_onguard_settings(
    ctx: Context,
    global_settings: bool = False,
) -> dict | str:
    """Get ClearPass OnGuard posture engine settings.

    Returns the posture-engine configuration: agent version requirements,
    quarantine actions, audit settings.

    Args:
        global_settings: When true, fetches /onguard/global-settings instead
            of the standard /onguard/settings record. Global settings cover
            cluster-wide posture defaults.

    See: https://developer.arubanetworks.com/cppm/reference
    (Endpoint Visibility → /onguard/settings, /onguard/global-settings)
    """
    try:
        from pyclearpass.api_endpointvisibility import ApiEndpointVisibility

        client = await get_clearpass_session(ApiEndpointVisibility)
        path = "/onguard/global-settings" if global_settings else "/onguard/settings"
        return client._send_request(path, "get")
    except Exception as e:
        return f"Error fetching OnGuard settings: {e}"
