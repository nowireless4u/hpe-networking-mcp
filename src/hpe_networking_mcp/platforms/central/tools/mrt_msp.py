"""Aruba Central MSP (Managed Service Provider) tools.

Wraps the ``network-msp/v1`` endpoints. MSP APIs are only meaningful
when the tenant is registered as an MSP — non-MSP tenants will see
empty / 403 responses.
"""

from fastmcp import Context

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


@tool(annotations=READ_ONLY)
async def central_list_msp_tenants(
    ctx: Context,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List tenants under the current MSP organization.

    Only meaningful when the authenticated tenant is itself registered
    as an MSP. Non-MSP tenants receive an empty list or an authorization
    error.

    Parameters:
        limit: Results per page (default 100).
        offset: Pagination offset (default 0).
    """
    conn = ctx.lifespan_context["central_conn"]
    api_params: dict = {"limit": limit, "offset": offset}
    response = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="network-msp/v1/list-tenants",
        api_params=api_params,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}
