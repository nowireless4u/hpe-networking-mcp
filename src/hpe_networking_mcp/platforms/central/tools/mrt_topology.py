"""Aruba Central topology + inventory tools.

Wraps ``network-monitoring/v1`` topology and inventory endpoints —
network graph, unmanaged-device detection, isolated-device monitoring,
device-inventory, LLDP/CDP neighbours, and the device PATCH/DELETE
write surface.
"""

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command


async def _call(conn, method: str, path: str, params: dict | None = None, data: dict | None = None) -> dict | str:
    response = await retry_central_command(
        central_conn=conn,
        api_method=method,
        api_path=path,
        api_params=params or {},
        api_data=data or {},
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(capability=Capability.READ)
async def central_get_topology(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
) -> dict | str:
    """Get the network topology graph for a site (nodes + edges)."""
    conn = get_central_conn(ctx)
    return await _call(conn, "GET", f"network-monitoring/v1/topology/{site_id}")


@tool(capability=Capability.READ)
async def central_get_neighbours(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Device serial number.")],
) -> dict | str:
    """Get LLDP / CDP neighbour records as seen by a specific device."""
    conn = get_central_conn(ctx)
    return await _call(conn, "GET", f"network-monitoring/v1/neighbours/{serial_number}")


@tool(capability=Capability.READ)
async def central_get_unmanaged_device(
    ctx: Context,
    mac_address: Annotated[str, Field(description="MAC address of the unmanaged device.")],
) -> dict | str:
    """Get details on an unmanaged device (seen on the network but not under Central management)."""
    conn = get_central_conn(ctx)
    return await _call(conn, "GET", f"network-monitoring/v1/unmanaged-device/{mac_address}")


@tool(capability=Capability.READ)
async def central_get_isolated_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
) -> dict | str:
    """List isolated devices at a site (managed devices that lost connectivity to peers)."""
    conn = get_central_conn(ctx)
    return await _call(conn, "GET", f"network-monitoring/v1/isolated-devices/{site_id}")


@tool(capability=Capability.READ)
async def central_get_device_inventory(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """Get the device inventory (all known device records — claimed + unclaimed + retired).

    Distinct from ``central_get_devices`` (which lists active managed
    devices) — this includes lifecycle states the live-device view
    filters out.
    """
    conn = get_central_conn(ctx)
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return await _call(conn, "GET", "network-monitoring/v1/device-inventory", params=params)


@tool(capability=Capability.WRITE_DELETE)
async def central_update_device(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Device serial number to update.")],
    payload: Annotated[
        dict,
        Field(description="Device-field updates (PATCH semantics — only included fields change)."),
    ],
) -> dict | str:
    """Update a device record (PATCH /devices/:serial-number).

    Requires ``ENABLE_CENTRAL_WRITE_TOOLS=true``. Typical use: rename a
    device, change its assigned site, update notes.
    """
    conn = get_central_conn(ctx)
    response = await retry_central_command(
        central_conn=conn,
        api_method="PATCH",
        api_path=f"network-monitoring/v1/devices/{serial_number}",
        api_data=payload,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "serial_number": serial_number, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(capability=Capability.WRITE_DELETE)
async def central_delete_device(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Device serial number to delete from the inventory.")],
) -> dict | str:
    """Remove a device from the inventory (DELETE /devices/:serial-number).

    Requires ``ENABLE_CENTRAL_WRITE_TOOLS=true``. Removes the device
    from Central — does not factory-reset the hardware. Use
    ``central_reboot_device`` or vendor tools to reset the hardware
    first if recommissioning.
    """
    conn = get_central_conn(ctx)
    response = await retry_central_command(
        central_conn=conn,
        api_method="DELETE",
        api_path=f"network-monitoring/v1/devices/{serial_number}",
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "serial_number": serial_number}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}
