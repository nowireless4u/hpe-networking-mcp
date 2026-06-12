from typing import Literal

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.central import monitoring_api
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.utils import get_central_conn


@tool(capability=Capability.READ)
async def central_get_ap_stats(
    ctx: Context,
    serial_number: str,
    start_time: str | None = None,
    end_time: str | None = None,
    duration: str | None = None,
) -> dict | list | str:
    """
    Get performance statistics for a specific access point.

    Returns radio stats, client counts, throughput, and connection
    metrics. Use central_find_device or central_get_devices to find
    the AP serial number first.

    Parameters:
        serial_number: AP serial number (required).
        start_time: Start of the time window in epoch seconds.
        end_time: End of the time window in epoch seconds.
        duration: Time duration shorthand (e.g. "3H", "1D", "1W").
            Ignored if both start_time and end_time are provided.
    """
    conn = get_central_conn(ctx)
    kwargs: dict = {"central_conn": conn, "serial_number": serial_number}
    if start_time:
        kwargs["start_time"] = start_time
    if end_time:
        kwargs["end_time"] = end_time
    if duration:
        kwargs["duration"] = duration

    try:
        resp = await monitoring_api.get_ap_stats(**kwargs)
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching AP stats: {e}"}) from e

    if not resp:
        return f"No stats found for AP '{serial_number}'. Verify the serial using central_find_device."
    return resp


@tool(capability=Capability.READ)
async def central_get_ap_utilization(
    ctx: Context,
    serial_number: str,
    metric: Literal["cpu", "memory", "poe"],
    start_time: str | None = None,
    end_time: str | None = None,
    duration: str | None = None,
) -> dict | str:
    """
    Get utilization data for a specific AP resource metric.

    Returns time-series utilization data for the chosen metric.
    Use central_find_device or central_get_devices to find
    the AP serial number first.

    Parameters:
        serial_number: AP serial number (required).
        metric: Resource metric to retrieve. Allowed values: cpu, memory, poe.
        start_time: Start of the time window in epoch seconds.
        end_time: End of the time window in epoch seconds.
        duration: Time duration shorthand (e.g. "3H", "1D", "1W").
            Ignored if both start_time and end_time are provided.
    """
    conn = get_central_conn(ctx)
    kwargs: dict = {"central_conn": conn, "serial_number": serial_number}
    if start_time:
        kwargs["start_time"] = start_time
    if end_time:
        kwargs["end_time"] = end_time
    if duration:
        kwargs["duration"] = duration

    method_map = {
        "cpu": monitoring_api.get_ap_cpu_utilization,
        "memory": monitoring_api.get_ap_memory_utilization,
        "poe": monitoring_api.get_ap_poe_utilization,
    }

    try:
        resp = await method_map[metric](**kwargs)
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching AP {metric} utilization: {e}"}) from e

    if not resp:
        return f"No {metric} utilization data for AP '{serial_number}'. Verify the serial using central_find_device."
    return resp


@tool(capability=Capability.READ)
async def central_get_gateway_stats(
    ctx: Context,
    serial_number: str,
    start_time: str | None = None,
    end_time: str | None = None,
    duration: str | None = None,
) -> dict | list | str:
    """
    Get performance statistics for a specific gateway.

    Returns interface stats, tunnel info, throughput, and health
    metrics. Use central_find_device or central_get_devices to find
    the gateway serial number first.

    Parameters:
        serial_number: Gateway serial number (required).
        start_time: Start of the time window in epoch seconds.
        end_time: End of the time window in epoch seconds.
        duration: Time duration shorthand (e.g. "3H", "1D", "1W").
            Ignored if both start_time and end_time are provided.
    """
    conn = get_central_conn(ctx)
    kwargs: dict = {"central_conn": conn, "serial_number": serial_number}
    if start_time:
        kwargs["start_time"] = start_time
    if end_time:
        kwargs["end_time"] = end_time
    if duration:
        kwargs["duration"] = duration

    try:
        resp = await monitoring_api.get_gateway_stats(**kwargs)
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching gateway stats: {e}"}) from e

    if not resp:
        return f"No stats found for gateway '{serial_number}'. Verify the serial using central_find_device."
    return resp


@tool(capability=Capability.READ)
async def central_get_gateway_utilization(
    ctx: Context,
    serial_number: str,
    metric: Literal["cpu", "memory"],
    start_time: str | None = None,
    end_time: str | None = None,
    duration: str | None = None,
) -> dict | str:
    """
    Get utilization data for a specific gateway resource metric.

    Returns time-series utilization data for the chosen metric.
    Use central_find_device or central_get_devices to find
    the gateway serial number first.

    Parameters:
        serial_number: Gateway serial number (required).
        metric: Resource metric to retrieve. Allowed values: cpu, memory.
        start_time: Start of the time window in epoch seconds.
        end_time: End of the time window in epoch seconds.
        duration: Time duration shorthand (e.g. "3H", "1D", "1W").
            Ignored if both start_time and end_time are provided.
    """
    conn = get_central_conn(ctx)
    kwargs: dict = {"central_conn": conn, "serial_number": serial_number}
    if start_time:
        kwargs["start_time"] = start_time
    if end_time:
        kwargs["end_time"] = end_time
    if duration:
        kwargs["duration"] = duration

    method_map = {
        "cpu": monitoring_api.get_gateway_cpu_utilization,
        "memory": monitoring_api.get_gateway_memory_utilization,
    }

    try:
        resp = await method_map[metric](**kwargs)
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching gateway {metric} utilization: {e}"}) from e

    if not resp:
        return (
            f"No {metric} utilization data for gateway '{serial_number}'. Verify the serial using central_find_device."
        )
    return resp


@tool(capability=Capability.READ)
async def central_get_gateway_wan_availability(
    ctx: Context,
    serial_number: str,
    start_time: str | None = None,
    end_time: str | None = None,
    duration: str | None = None,
) -> dict | str:
    """
    Get WAN availability data for a specific gateway.

    Returns WAN uplink availability percentages and downtime
    windows. Use central_find_device or central_get_devices to
    find the gateway serial number first.

    Parameters:
        serial_number: Gateway serial number (required).
        start_time: Start of the time window in epoch seconds.
        end_time: End of the time window in epoch seconds.
        duration: Time duration shorthand (e.g. "3H", "1D", "1W").
            Ignored if both start_time and end_time are provided.
    """
    conn = get_central_conn(ctx)
    kwargs: dict = {"central_conn": conn, "serial_number": serial_number}
    if start_time:
        kwargs["start_time"] = start_time
    if end_time:
        kwargs["end_time"] = end_time
    if duration:
        kwargs["duration"] = duration

    try:
        resp = await monitoring_api.get_gateway_wan_availability(**kwargs)
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching gateway WAN availability: {e}"}) from e

    if not resp:
        return f"No WAN availability data for gateway '{serial_number}'. Verify the serial using central_find_device."
    return resp


@tool(capability=Capability.READ)
async def central_get_tunnel_health(
    ctx: Context,
    serial_number: str,
) -> dict | str:
    """
    Get tunnel health summary for a specific gateway.

    Returns health status for all VPN/overlay tunnels on the
    gateway including up/down state and latency. Use
    central_find_device or central_get_devices to find the
    gateway serial number first.

    Parameters:
        serial_number: Gateway serial number (required).
    """
    conn = get_central_conn(ctx)

    try:
        resp = await monitoring_api.get_tunnel_health_summary(
            central_conn=conn,
            serial_number=serial_number,
        )
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching tunnel health: {e}"}) from e

    if not resp:
        return f"No tunnel health data for gateway '{serial_number}'. Verify the serial using central_find_device."
    return resp
