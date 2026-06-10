"""Aruba Central Insights tools.

Wraps the ``network-notifications/v1/insights`` endpoint. Distinct from
the alerts surface (``central_get_alerts``) — Insights are
recommendation-style observations Central surfaces alongside hard alerts.
"""

from fastmcp import Context

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command


@tool(annotations=READ_ONLY)
async def central_get_insights(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """Get Central Insights — recommendation-style observations.

    Distinct from the alerts surface (``central_get_alerts``). Insights
    are non-acute observations Central surfaces alongside hard alerts —
    e.g. configuration suggestions, capacity warnings, optimization
    recommendations.

    Parameters:
        filter: Optional OData 4.0 filter on Insights fields.
        limit: Results per page (default 100).
        offset: Pagination offset (default 0).
    """
    conn = get_central_conn(ctx)
    api_params: dict = {"limit": limit, "offset": offset}
    if filter:
        api_params["filter"] = filter
    response = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="network-notifications/v1/insights",
        api_params=api_params,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}
