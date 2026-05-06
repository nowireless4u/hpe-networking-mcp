"""ClearPass audit, event, and insight read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_logs import ApiLogs

        client = await get_clearpass_session(ApiLogs)
        return client.get_login_audit_by_name(name=username)
    except Exception as e:
        return f"Error fetching audit logs: {e}"


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_logs import ApiLogs

        client = await get_clearpass_session(ApiLogs)
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return clearpass_get(client, "/system-event" + query)
    except Exception as e:
        return f"Error fetching system events: {e}"


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_insight import ApiInsight

        client = await get_clearpass_session(ApiInsight)
        if alert_id:
            return client.get_alert_by_id(id=alert_id)
        if name:
            return client.get_alert_by_name(name=name)
        query = f"?offset={offset}&limit={limit}&calculate_count={'true' if calculate_count else 'false'}"
        return clearpass_get(client, "/alert" + query)
    except Exception as e:
        return f"Error fetching insight alerts: {e}"


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_insight import ApiInsight

        client = await get_clearpass_session(ApiInsight)
        if report_id:
            return client.get_report_by_id(id=report_id)
        if name:
            return client.get_report_by_name(name=name)
        query = f"?offset={offset}&limit={limit}&calculate_count={'true' if calculate_count else 'false'}"
        return clearpass_get(client, "/report" + query)
    except Exception as e:
        return f"Error fetching insight reports: {e}"


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_logs import ApiLogs

        client = await get_clearpass_session(ApiLogs)
        if mac:
            return client.get_insight_endpoint_mac_by_mac(mac=mac)
        if ip:
            return client.get_insight_endpoint_ip_by_ip(ip=ip)
        if ip_range:
            return client.get_insight_endpoint_ip_range_by_ip_range(ip_range=ip_range)
        if from_time and to_time:
            return client.get_insight_endpoint_time_range_by_from_time_to_time(
                from_time=from_time,
                to_time=to_time,
            )
        return "Error: at least one parameter (mac, ip, ip_range, or from_time+to_time) is required."
    except Exception as e:
        return f"Error fetching endpoint insights: {e}"
