"""ClearPass audit, event, and insight read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get


@tool(capability=Capability.READ)
async def clearpass_get_audit_logs(
    ctx: Context,
    username: str,
) -> dict | str:
    """Get ClearPass login audit records for a specific admin username.

    Returns audit trail entries showing login activity for the given admin user.

    Args:
        username: Admin username to retrieve audit logs for.
    """
    try:
        client = await get_clearpass_client()
        return await client.request("get", f"/login-audit/{username}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching audit logs: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_system_events(
    ctx: Context,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass system events.

    Returns a paginated list of system event log entries.

    Args:
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+timestamp" or "-id"). Default server-side: "+source".
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25, max 1000).
        calculate_count: When true, include total count in response (default false).

    See: https://developer.arubanetworks.com/cppm/reference (Logs → /system-events)
    """
    try:
        client = await get_clearpass_client()
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/system-event" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching system events: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_insight_alerts(
    ctx: Context,
    alert_id: str | None = None,
    name: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass Insight alerts.

    If alert_id or name is provided, returns a single alert.
    Otherwise returns a paginated list of all alerts.

    Args:
        alert_id: Numeric ID for single-item lookup.
        name: Alert name for lookup by name.
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25, max 1000).
        calculate_count: When true, include total count in response (default false).

    Note: /alert does not accept ``filter`` or ``sort`` (per ClearPass API
    spec — only pagination + count). See:
    https://developer.arubanetworks.com/cppm/reference (Insight → /alert)
    """
    try:
        client = await get_clearpass_client()
        if alert_id:
            return await client.request("get", f"/alert/{alert_id}")
        if name:
            return await client.request("get", f"/alert/{name}")
        query = f"?offset={offset}&limit={limit}&calculate_count={'true' if calculate_count else 'false'}"
        return await clearpass_get(client, "/alert" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching insight alerts: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_insight_reports(
    ctx: Context,
    report_id: str | None = None,
    name: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass Insight reports.

    If report_id or name is provided, returns a single report.
    Otherwise returns a paginated list of all reports.

    Args:
        report_id: Numeric ID for single-item lookup.
        name: Report name for lookup by name.
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25, max 1000).
        calculate_count: When true, include total count in response (default false).

    Note: /report does not accept ``filter`` or ``sort`` (per ClearPass API
    spec — only pagination + count). See:
    https://developer.arubanetworks.com/cppm/reference (Insight → /report)
    """
    try:
        client = await get_clearpass_client()
        if report_id:
            return await client.request("get", f"/report/{report_id}")
        if name:
            return await client.request("get", f"/report/{name}")
        query = f"?offset={offset}&limit={limit}&calculate_count={'true' if calculate_count else 'false'}"
        return await clearpass_get(client, "/report" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching insight reports: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_endpoint_insights(
    ctx: Context,
    mac: str | None = None,
    ip: str | None = None,
    ip_range: str | None = None,
    from_time: str | None = None,
    to_time: str | None = None,
) -> dict | str:
    """Get ClearPass endpoint insight data.

    Queries Insight endpoint data by MAC address, IP address, IP range, or time range.
    At least one parameter must be provided.

    Args:
        mac: Endpoint MAC address (e.g. "00:11:22:33:44:55").
        ip: Endpoint IP address.
        ip_range: IP address range (e.g. "10.0.0.0/24").
        from_time: Start time for time-range query (ISO 8601 format).
        to_time: End time for time-range query (ISO 8601 format, required with from_time).
    """
    try:
        client = await get_clearpass_client()
        if mac:
            return await client.request("get", f"/insight/endpoint/mac/{mac}")
        if ip:
            return await client.request("get", f"/insight/endpoint/ip/{ip}")
        if ip_range:
            return await client.request("get", f"/insight/endpoint/ip-range/{ip_range}")
        if from_time and to_time:
            return await client.request("get", f"/insight/endpoint/time-range/{from_time}/{to_time}")
        raise ToolError(
            {
                "status_code": 400,
                "message": "Error: at least one parameter (mac, ip, ip_range, or from_time+to_time) is required.",
            }
        )
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching endpoint insights: {e}"}) from e
