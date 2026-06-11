"""Aruba Central client analytics — trends, top-N usage, mobility trail,
onboarding stage diagnostics, and firewall sessions.

Wraps ``network-monitoring/v1`` client-related endpoints beyond the
existing ``central_get_clients`` / ``central_find_client`` list view.
"""

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command


async def _get(conn, path: str, params: dict | None = None) -> dict | str:
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=path,
        api_params=params or {},
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# ---------------------------------------------------------------------------
# Client trends + top-N usage + mobility trail
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_clients_trend(
    ctx: Context,
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
    filter: str | None = None,
) -> dict | str:
    """Get tenant-wide client-count trend over a time window."""
    conn = get_central_conn(ctx)
    params: dict = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/clients-trend", params)


@tool(annotations=READ_ONLY)
async def central_get_clients_topn_usage(
    ctx: Context,
    top_n: Annotated[int, Field(ge=1, le=100, description="Number of top-clients to return (default 10).")] = 10,
    filter: str | None = None,
) -> dict | str:
    """Get the top-N clients by usage."""
    conn = get_central_conn(ctx)
    params: dict = {"topN": top_n}
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/clients-topn-usage", params)


@tool(annotations=READ_ONLY)
async def central_get_client_mobility_trail(
    ctx: Context,
    mac_address: Annotated[str, Field(description="Client MAC address.")],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get a client's roaming / mobility history (AP-to-AP transitions)."""
    conn = get_central_conn(ctx)
    params: dict = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    return await _get(conn, f"network-monitoring/v1/clients/{mac_address}/mobility-trail", params)


@tool(annotations=READ_ONLY)
async def central_get_client_detail(
    ctx: Context,
    mac_address: Annotated[str, Field(description="Client MAC address.")],
) -> dict | str:
    """Get one client's full record (deeper than ``central_get_clients`` list view)."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/clients/{mac_address}")


# ---------------------------------------------------------------------------
# Client onboarding diagnostics
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_client_onboarding_score(
    ctx: Context,
    filter: str | None = None,
) -> dict | str:
    """Get the aggregate client-onboarding score (success-rate KPI)."""
    conn = get_central_conn(ctx)
    params: dict = {}
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/client-onboarding-score", params)


@tool(annotations=READ_ONLY)
async def central_get_client_onboarding_stage_export(
    ctx: Context,
    filter: str | None = None,
) -> dict | str:
    """Export per-client onboarding-stage records.

    Returns the per-client breakdown of which step of the onboarding flow
    they reached / where they failed. Larger payload — use the count /
    reasons endpoints for summary views.
    """
    conn = get_central_conn(ctx)
    params: dict = {}
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/client-onboarding-stage/export", params)


@tool(annotations=READ_ONLY)
async def central_get_client_onboarding_stage_reasons(
    ctx: Context,
    filter: str | None = None,
) -> dict | str:
    """Get aggregated reasons clients failed onboarding (top failure categories)."""
    conn = get_central_conn(ctx)
    params: dict = {}
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/client-onboarding-stage/reasons", params)


@tool(annotations=READ_ONLY)
async def central_get_client_onboarding_stage_count(
    ctx: Context,
    filter: str | None = None,
) -> dict | str:
    """Get the count of clients at each onboarding stage (funnel view)."""
    conn = get_central_conn(ctx)
    params: dict = {}
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/client-onboarding-stage/count", params)


# ---------------------------------------------------------------------------
# Firewall sessions
# ---------------------------------------------------------------------------


_FirewallScope = Literal["site", "client", "firewall-clients"]


@tool(annotations=READ_ONLY)
async def central_get_firewall_sessions(
    ctx: Context,
    scope: Annotated[
        _FirewallScope,
        Field(
            description=(
                "Session-listing perspective: ``'site'`` (all sessions at a site), "
                "``'client'`` (sessions for a specific client), or "
                "``'firewall-clients'`` (clients seen by the firewall — distinct from session detail)."
            ),
        ),
    ],
    filter: Annotated[
        str | None,
        Field(description="OData filter — narrow by site / client MAC / 5-tuple / protocol / etc."),
    ] = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """Get firewall session telemetry.

    Three URI variants under one tool — pick the perspective via ``scope``:

    | scope | endpoint |
    |---|---|
    | site | /site-firewall-sessions |
    | client | /client-firewall-sessions |
    | firewall-clients | /firewall-clients |
    """
    conn = get_central_conn(ctx)
    path_map = {
        "site": "network-monitoring/v1/site-firewall-sessions",
        "client": "network-monitoring/v1/client-firewall-sessions",
        "firewall-clients": "network-monitoring/v1/firewall-clients",
    }
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return await _get(conn, path_map[scope], params)
