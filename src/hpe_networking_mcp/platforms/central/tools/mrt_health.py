"""Aruba Central tenant- and site-level health summaries.

Wraps the ``network-monitoring/v1/{tenant,sites,site}-{device,client}-health``
endpoints. Distinct from the existing ``central_get_site_health``
(network-monitoring/v1/sites-health) which is the multi-site dashboard
view — these wrap the deeper per-tenant / per-site / per-client variants
the MRT collection surfaces.
"""

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.central._registry import tool
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


@tool(capability=Capability.READ)
async def central_get_site_health_detail(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
) -> dict | str:
    """Get a single site's detailed health record.

    Distinct from ``central_get_site_health`` (which takes ``site_name``
    and queries the dashboard view) — this hits the ``/site-health/:site-id``
    endpoint directly for one site's full health detail.
    """
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/site-health/{path_seg(site_id)}")


@tool(capability=Capability.READ)
async def central_get_sites_client_health(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """Get per-site client-health summaries across the tenant."""
    conn = get_central_conn(ctx)
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/sites-client-health", params)


@tool(capability=Capability.READ)
async def central_get_tenant_device_health(
    ctx: Context,
    filter: str | None = None,
) -> dict | str:
    """Get tenant-wide device health rollup (single record, tenant scope)."""
    conn = get_central_conn(ctx)
    params: dict = {}
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/tenant-device-health", params)


@tool(capability=Capability.READ)
async def central_get_tenant_client_health(
    ctx: Context,
    filter: str | None = None,
) -> dict | str:
    """Get tenant-wide client health rollup (single record, tenant scope)."""
    conn = get_central_conn(ctx)
    params: dict = {}
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/tenant-client-health", params)
