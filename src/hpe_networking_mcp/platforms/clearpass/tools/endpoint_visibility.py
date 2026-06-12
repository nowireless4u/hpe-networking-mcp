"""ClearPass endpoint-visibility read tools.

Covers OnGuard posture activity + settings, network discovery scans, and
the profiler fingerprint dictionary. All standard Apigility list-style
endpoints (filter / sort / offset / limit / calculate_count).

See: https://developer.arubanetworks.com/cppm/reference (Endpoint Visibility)
"""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if activity_id:
            return await clearpass_get(client, f"/onguard-activity/{path_seg(activity_id)}")
        if mac:
            return await clearpass_get(client, f"/onguard-activity/mac/{path_seg(mac)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/onguard-activity" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching OnGuard activity: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if fingerprint_id:
            return await clearpass_get(client, f"/fingerprint/{path_seg(fingerprint_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/fingerprint" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching fingerprint dictionary: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if scan_id:
            return await clearpass_get(client, f"/config/network-scan/{path_seg(scan_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/config/network-scan" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching network scans: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        path = "/onguard/global-settings" if global_settings else "/onguard/settings"
        return await clearpass_get(client, path)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching OnGuard settings: {e}"}) from e
