from fastmcp import Context

from hpe_networking_mcp.platforms.central._registry import mcp
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


@mcp.tool(annotations=READ_ONLY)
async def central_get_audit_logs(
    ctx: Context,
    start_at: str,
    end_at: str,
    filter: str | None = None,
    sort: str | None = None,
    limit: int = 200,
    offset: int = 1,
) -> dict | str:
    """
    Retrieve audit logs from Aruba Central within a time window.

    Returns a paginated list of audit log entries including user actions,
    configuration changes, and system events. Use this to investigate
    who changed what and when.

    Parameters:
        start_at: Start of the time window in epoch milliseconds (required).
        end_at: End of the time window in epoch milliseconds (required).
        filter: OData filter expression to narrow results.
        sort: Sort order for results (e.g. "+timestamp" or "-timestamp").
        limit: Number of records per page (default 200, max 200).
        offset: Page number starting at 1 (default 1).
    """
    conn = ctx.lifespan_context["central_conn"]

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
            api_path="network-services/v1alpha1/audits",
            api_params=query_params,
        )
    except Exception as e:
        return f"Error fetching audit logs: {e}"

    code = resp.get("code", 0)
    if not (200 <= code < 300):
        return f"Central API error (HTTP {code}): {resp.get('msg')}"
    return resp.get("msg", {})


@mcp.tool(annotations=READ_ONLY)
async def central_get_audit_log_detail(
    ctx: Context,
    id: str,
) -> dict | str:
    """
    Get the full detail of a single audit log entry.

    Returns the complete audit record including the user, action,
    target resource, timestamp, and any associated metadata.
    Use central_get_audit_logs first to find the audit log ID.

    Parameters:
        id: Audit log entry ID (required).
    """
    conn = ctx.lifespan_context["central_conn"]

    try:
        resp = retry_central_command(
            conn,
            api_method="GET",
            api_path=f"network-services/v1alpha1/audit/{id}",
            api_params={},
        )
    except Exception as e:
        return f"Error fetching audit log detail: {e}"

    code = resp.get("code", 0)
    if not (200 <= code < 300):
        return f"Central API error (HTTP {code}): {resp.get('msg')}"
    return resp.get("msg", {})
