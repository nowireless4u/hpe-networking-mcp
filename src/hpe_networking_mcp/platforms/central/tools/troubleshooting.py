from typing import Literal

from fastmcp import Context
from pycentral.troubleshooting.troubleshooting import Troubleshooting

from hpe_networking_mcp.platforms.central._registry import mcp
from hpe_networking_mcp.platforms.central.tools import READ_ONLY


def _resolve_if_switch(conn, serial_number: str, device_type: str) -> str:
    """Resolve stack ID for switches (aos-s, cx). Returns serial unchanged for other types."""
    if device_type not in ("cx", "aos-s"):
        return serial_number
    from hpe_networking_mcp.platforms.central.tools.actions import (
        _resolve_switch_id,
    )

    return _resolve_switch_id(conn, serial_number)


@mcp.tool(annotations=READ_ONLY)
async def central_ping(
    ctx: Context,
    serial_number: str,
    destination: str,
    device_type: Literal["ap", "cx", "gateway"],
    count: int | None = None,
    packet_size: int | None = None,
) -> dict | str:
    """
    Initiate a ping test from a device to a destination.

    The test runs on the device and results are returned after
    polling completes. Use central_find_device to get the serial
    number first.

    Parameters:
        serial_number: Device serial number (required).
        destination: IP address or hostname to ping (required).
        device_type: Type of device — "ap", "cx", or "gateway" (required).
        count: Number of pings to send.
        packet_size: Ping packet size in bytes.
    """
    conn = ctx.lifespan_context["central_conn"]
    resolved_id = _resolve_if_switch(conn, serial_number, device_type)

    kwargs: dict = {
        "central_conn": conn,
        "serial_number": resolved_id,
        "destination": destination,
    }
    if count is not None:
        kwargs["count"] = count
    if packet_size is not None:
        kwargs["packet_size"] = packet_size

    method_map = {
        "ap": Troubleshooting.ping_aps_test,
        "cx": Troubleshooting.ping_cx_test,
        "gateway": Troubleshooting.ping_gateways_test,
    }

    try:
        resp = method_map[device_type](**kwargs)
    except Exception as e:
        return f"Error running ping test: {e}"

    if not resp:
        return "Ping test returned no results."
    return resp


@mcp.tool(annotations=READ_ONLY)
async def central_traceroute(
    ctx: Context,
    serial_number: str,
    destination: str,
    device_type: Literal["ap", "cx", "gateway"],
) -> dict | str:
    """
    Initiate a traceroute from a device to a destination.

    Returns the hop-by-hop path. Use central_find_device to get
    the serial number first.

    Parameters:
        serial_number: Device serial number (required).
        destination: IP address or hostname to traceroute (required).
        device_type: Type of device — "ap", "cx", or "gateway" (required).
    """
    conn = ctx.lifespan_context["central_conn"]
    resolved_id = _resolve_if_switch(conn, serial_number, device_type)

    method_map = {
        "ap": Troubleshooting.traceroute_aps_test,
        "cx": Troubleshooting.traceroute_cx_test,
        "gateway": Troubleshooting.traceroute_gateways_test,
    }

    try:
        resp = method_map[device_type](
            central_conn=conn,
            serial_number=resolved_id,
            destination=destination,
        )
    except Exception as e:
        return f"Error running traceroute test: {e}"

    if not resp:
        return "Traceroute test returned no results."
    return resp


@mcp.tool(annotations=READ_ONLY)
async def central_cable_test(
    ctx: Context,
    serial_number: str,
    device_type: Literal["aos-s", "cx"],
    ports: str,
) -> dict | str:
    """
    Initiate a cable test on switch ports.

    Returns cable status and length for each port. Useful for
    diagnosing physical layer issues.

    Parameters:
        serial_number: Switch serial number (required).
        device_type: Switch type — "aos-s" or "cx" (required).
        ports: Comma-separated port list, e.g. "1/1/1,1/1/2" (required).
    """
    conn = ctx.lifespan_context["central_conn"]
    resolved_id = _resolve_if_switch(conn, serial_number, device_type)
    port_list = [p.strip() for p in ports.split(",")]

    try:
        resp = Troubleshooting.cable_test(
            central_conn=conn,
            device_type=device_type,
            serial_number=resolved_id,
            ports=port_list,
        )
    except Exception as e:
        return f"Error running cable test: {e}"

    if not resp:
        return "Cable test returned no results."
    return resp


@mcp.tool(annotations=READ_ONLY)
async def central_show_commands(
    ctx: Context,
    serial_number: str,
    device_type: Literal["aos-s", "cx", "gateways"],
    commands: str,
) -> dict | str:
    """
    Execute show commands on a device and return the output.

    Supports AP, CX switch, and gateway devices. Use for
    detailed device diagnostics.

    Parameters:
        serial_number: Device serial number (required).
        device_type: Device type — "aos-s", "cx", or "gateways" (required).
        commands: Comma-separated show commands, e.g. "show version,show interfaces" (required).
    """
    conn = ctx.lifespan_context["central_conn"]
    resolved_id = _resolve_if_switch(conn, serial_number, device_type)
    command_list = [c.strip() for c in commands.split(",")]

    try:
        resp = Troubleshooting.run_show_commands(
            central_conn=conn,
            device_type=device_type,
            serial_number=resolved_id,
            commands=command_list,
        )
    except Exception as e:
        return f"Error running show commands: {e}"

    if not resp:
        return "Show commands returned no results."
    return resp
