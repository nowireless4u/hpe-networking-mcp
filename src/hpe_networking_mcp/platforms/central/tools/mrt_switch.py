"""Aruba Central switch monitoring tools — lag, vlans, interface trends,
stack members, vsx, hardware categories, top-N interface trends.

Wraps ``network-monitoring/v1/switches`` endpoints beyond the existing
``central_get_switch_details``, ``central_get_switch_hardware_trends``,
and ``central_get_switch_poe`` hand-curated tools.
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
async def central_get_switches(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List switches (network-monitoring view).

    Returns the monitoring-side switch list. Use
    ``central_get_switch_details`` for one switch's deeper record.
    """
    conn = get_central_conn(ctx)
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/switches", params)


@tool(capability=Capability.READ)
async def central_get_switch_lag(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Switch serial number.")],
) -> dict | str:
    """Get LAG (link-aggregation) state for a switch."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/switches/{path_seg(serial_number)}/lag")


@tool(capability=Capability.READ)
async def central_get_switch_vlans(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Switch serial number.")],
) -> dict | str:
    """Get configured VLANs on a switch (runtime view)."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/switches/{path_seg(serial_number)}/vlans")


@tool(capability=Capability.READ)
async def central_get_switch_hardware_categories(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Switch serial number.")],
) -> dict | str:
    """Get available hardware-trend categories for a switch (drives the trend dimensions valid for this model)."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/switches/{path_seg(serial_number)}/hardware-categories")


@tool(capability=Capability.READ)
async def central_get_switch_interface_trends(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Switch serial number.")],
    interface_name: Annotated[
        str | None, Field(description="Specific interface name to scope the trend; omit for all interfaces.")
    ] = None,
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get per-interface throughput / utilization trends for a switch."""
    conn = get_central_conn(ctx)
    params: dict = {}
    if interface_name:
        params["interfaceName"] = interface_name
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    return await _get(conn, f"network-monitoring/v1/switches/{path_seg(serial_number)}/interface-trends", params)


@tool(capability=Capability.READ)
async def central_get_switches_topn_interface_trends(
    ctx: Context,
    top_n: Annotated[int, Field(ge=1, le=100, description="Number of top interfaces to return (default 10).")] = 10,
    filter: str | None = None,
) -> dict | str:
    """Get the top-N busiest switch interfaces across the tenant."""
    conn = get_central_conn(ctx)
    params: dict = {"topN": top_n}
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/switches/topn-interface-trends", params)


@tool(capability=Capability.READ)
async def central_get_switch_vsx(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Switch serial number.")],
) -> dict | str:
    """Get the VSX pairing state for a switch (peer / status / sync info)."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/switches/{path_seg(serial_number)}/vsx")


@tool(capability=Capability.READ)
async def central_get_switch_stack_members(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Conductor switch serial number.")],
) -> dict | str:
    """Get stack members for a stacked switch (returns members of the stack the conductor belongs to)."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/stack/{path_seg(serial_number)}/members")
