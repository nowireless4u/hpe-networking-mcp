"""ClearPass audit, event, and insight read tools."""

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


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_system_events(
    ctx: Context,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
) -> dict | str:
    """Get ClearPass system events.

    Returns a paginated list of system event log entries.

    Args:
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+timestamp" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_logs import ApiLogs

        client = await get_clearpass_session(ApiLogs)
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/system-event" + query, "get")
    except Exception as e:
        return f"Error fetching system events: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_insight_alerts(
    ctx: Context,
    alert_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
) -> dict | str:
    """Get ClearPass Insight alerts.

    If alert_id or name is provided, returns a single alert.
    Otherwise returns a paginated list of all alerts.

    Args:
        alert_id: Numeric ID for single-item lookup.
        name: Alert name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_insight import ApiInsight

        client = await get_clearpass_session(ApiInsight)
        if alert_id:
            return client.get_alert_by_id(id=alert_id)
        if name:
            return client.get_alert_by_name(name=name)
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/alert" + query, "get")
    except Exception as e:
        return f"Error fetching insight alerts: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_insight_reports(
    ctx: Context,
    report_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
) -> dict | str:
    """Get ClearPass Insight reports.

    If report_id or name is provided, returns a single report.
    Otherwise returns a paginated list of all reports.

    Args:
        report_id: Numeric ID for single-item lookup.
        name: Report name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_insight import ApiInsight

        client = await get_clearpass_session(ApiInsight)
        if report_id:
            return client.get_report_by_id(id=report_id)
        if name:
            return client.get_report_by_name(name=name)
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/report" + query, "get")
    except Exception as e:
        return f"Error fetching insight reports: {e}"


@mcp.tool(annotations=READ_ONLY)
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
