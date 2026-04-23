from fastmcp import Context

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


@tool(annotations=READ_ONLY)
async def central_get_applications(
    ctx: Context,
    site_id: str,
    start_query_time: str,
    end_query_time: str,
    limit: int = 1000,
    offset: int = 0,
    client_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
) -> dict | str:
    """
    Get application usage data for a site within a time window.

    Returns a list of applications observed on the network with
    traffic volume, client counts, and categorization. Useful for
    understanding application mix and bandwidth consumption.

    Parameters:
        site_id: Site ID to scope the query (required).
        start_query_time: Start of the time window in epoch milliseconds (required).
        end_query_time: End of the time window in epoch milliseconds (required).
        limit: Number of records per page (default 1000).
        offset: Starting record offset for pagination (default 0).
        client_id: Filter results to a specific client ID.
        filter: OData filter expression to narrow results.
        sort: Sort order for results.
    """
    conn = ctx.lifespan_context["central_conn"]

    query_params: dict = {
        "site-id": site_id,
        "start-query-time": start_query_time,
        "end-query-time": end_query_time,
        "limit": limit,
        "offset": offset,
    }
    if client_id:
        query_params["client-id"] = client_id
    if filter:
        query_params["filter"] = filter
    if sort:
        query_params["sort"] = sort

    try:
        resp = retry_central_command(
            conn,
            api_method="GET",
            api_path="network-monitoring/v1alpha1/applications",
            api_params=query_params,
        )
    except Exception as e:
        return f"Error fetching applications: {e}"

    code = resp.get("code", 0)
    if not (200 <= code < 300):
        return f"Central API error (HTTP {code}): {resp.get('msg')}"
    return resp.get("msg", {})
