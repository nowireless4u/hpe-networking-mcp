from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import deprecation_notice, get_central_conn, retry_central_command


@tool(annotations=READ_ONLY)
async def central_get_audit_logs(
    ctx: Context,
    start_at: str,
    end_at: str,
    filter: str | None = None,
    sort: str | None = None,
    limit: int = 200,
    offset: int = 1,
) -> dict:
    """
    Retrieve audit logs from Aruba Central within a time window.

    Returns a paginated list of audit log entries including user actions,
    configuration changes, and system events. Use this to investigate
    who changed what and when.

    Parameters:
        start_at: Start of the time window. Accepts an ISO 8601 timestamp
            (e.g. "2026-02-19T00:00:00Z") or epoch milliseconds. Required.
        end_at: End of the time window, same formats as start_at. Required.
        filter: OData filter expression to narrow results.
        sort: Sort order for results (e.g. "+timestamp" or "-timestamp").
        limit: Records per page (default 200; clamped to 1..200).
        offset: 1-based page number (default 1). offset=2 is the second page,
            etc. The API returns HTTP 500 for offset 0, so values < 1 are
            clamped to 1.
    """
    conn = get_central_conn(ctx)

    # The audit API paginates by 1-based page number and returns a 500 for
    # offset 0, so clamp it; limit is capped at the documented max of 200.
    offset = max(1, offset)
    limit = max(1, min(limit, 200))

    query_params: dict = {
        "start-at": start_at,
        "end-at": end_at,
        "limit": limit,
        "offset": offset,
    }
    if filter:
        query_params["filter"] = filter
    if sort:
        query_params["sort"] = sort

    try:
        resp = retry_central_command(
            conn,
            api_method="GET",
            api_path="network-services/v1/audits",
            api_params=query_params,
        )
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching audit logs: {e}"}) from e

    code = resp.get("code", 0)
    if not (200 <= code < 300):
        raise ToolError({"status_code": code, "message": f"Central API error: {resp.get('msg')}"})
    body = resp.get("msg", {})
    notice = deprecation_notice(resp)
    if notice is not None and isinstance(body, dict):
        body = {**body, "_deprecation": notice}
    return body


@tool(annotations=READ_ONLY)
async def central_get_audit_log_detail(
    ctx: Context,
    id: str,
) -> dict:
    """
    Get the full detail of a single audit log entry.

    Returns the complete audit record including the user, action,
    target resource, timestamp, and any associated metadata.
    Use central_get_audit_logs first to find the audit log ID.

    Parameters:
        id: Audit log entry ID (required).
    """
    conn = get_central_conn(ctx)

    try:
        resp = retry_central_command(
            conn,
            api_method="GET",
            api_path=f"network-services/v1/audit/{id}",
            api_params={},
        )
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching audit log detail: {e}"}) from e

    code = resp.get("code", 0)
    if not (200 <= code < 300):
        raise ToolError({"status_code": code, "message": f"Central API error: {resp.get('msg')}"})
    body = resp.get("msg", {})
    notice = deprecation_notice(resp)
    if notice is not None and isinstance(body, dict):
        body = {**body, "_deprecation": notice}
    return body
