from typing import Literal

from fastmcp import Context
from pycentral.new_monitoring.aps import MonitoringAPs
from pycentral.new_monitoring.gateways import MonitoringGateways

from hpe_networking_mcp.platforms.central.tools import READ_ONLY


def register(mcp):

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_ap_stats(
        ctx: Context,
        serial_number: str,
        start_time: str | None = None,
        end_time: str | None = None,
        duration: str | None = None,
    ) -> dict | str:
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
        conn = ctx.lifespan_context["central_conn"]
        kwargs: dict = {"central_conn": conn, "serial_number": serial_number}
        if start_time:
            kwargs["from_timestamp"] = start_time
        if end_time:
            kwargs["to_timestamp"] = end_time
        if duration:
            kwargs["duration"] = duration

        try:
            resp = MonitoringAPs.get_ap_stats(**kwargs)
        except Exception as e:
            return f"Error fetching AP stats: {e}"

        if not resp:
            return f"No stats found for AP '{serial_number}'. Verify the serial using central_find_device."
        return resp

    @mcp.tool(annotations=READ_ONLY)
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
        conn = ctx.lifespan_context["central_conn"]
        kwargs: dict = {"central_conn": conn, "serial_number": serial_number}
        if start_time:
            kwargs["from_timestamp"] = start_time
        if end_time:
            kwargs["to_timestamp"] = end_time
        if duration:
            kwargs["duration"] = duration

        method_map = {
            "cpu": MonitoringAPs.get_ap_cpu_utilization,
            "memory": MonitoringAPs.get_ap_memory_utilization,
            "poe": MonitoringAPs.get_ap_poe_utilization,
        }

        try:
            resp = method_map[metric](**kwargs)
        except Exception as e:
            return f"Error fetching AP {metric} utilization: {e}"

        if not resp:
            return (
                f"No {metric} utilization data for AP '{serial_number}'. Verify the serial using central_find_device."
            )
        return resp

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_gateway_stats(
        ctx: Context,
        serial_number: str,
        start_time: str | None = None,
        end_time: str | None = None,
        duration: str | None = None,
    ) -> dict | str:
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
        conn = ctx.lifespan_context["central_conn"]
        kwargs: dict = {"central_conn": conn, "serial_number": serial_number}
        if start_time:
            kwargs["from_timestamp"] = start_time
        if end_time:
            kwargs["to_timestamp"] = end_time
        if duration:
            kwargs["duration"] = duration

        try:
            resp = MonitoringGateways.get_gateway_stats(**kwargs)
        except Exception as e:
            return f"Error fetching gateway stats: {e}"

        if not resp:
            return f"No stats found for gateway '{serial_number}'. Verify the serial using central_find_device."
        return resp

    @mcp.tool(annotations=READ_ONLY)
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
        conn = ctx.lifespan_context["central_conn"]
        kwargs: dict = {"central_conn": conn, "serial_number": serial_number}
        if start_time:
            kwargs["from_timestamp"] = start_time
        if end_time:
            kwargs["to_timestamp"] = end_time
        if duration:
            kwargs["duration"] = duration

        method_map = {
            "cpu": MonitoringGateways.get_gateway_cpu_utilization,
            "memory": MonitoringGateways.get_gateway_memory_utilization,
        }

        try:
            resp = method_map[metric](**kwargs)
        except Exception as e:
            return f"Error fetching gateway {metric} utilization: {e}"

        if not resp:
            return (
                f"No {metric} utilization data for gateway '{serial_number}'. "
                "Verify the serial using central_find_device."
            )
        return resp

    @mcp.tool(annotations=READ_ONLY)
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
        conn = ctx.lifespan_context["central_conn"]
        kwargs: dict = {"central_conn": conn, "serial_number": serial_number}
        if start_time:
            kwargs["from_timestamp"] = start_time
        if end_time:
            kwargs["to_timestamp"] = end_time
        if duration:
            kwargs["duration"] = duration

        try:
            resp = MonitoringGateways.get_gateway_wan_availability(**kwargs)
        except Exception as e:
            return f"Error fetching gateway WAN availability: {e}"

        if not resp:
            return (
                f"No WAN availability data for gateway '{serial_number}'. Verify the serial using central_find_device."
            )
        return resp

    @mcp.tool(annotations=READ_ONLY)
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
        conn = ctx.lifespan_context["central_conn"]

        try:
            resp = MonitoringGateways.get_tunnel_health_summary(
                central_conn=conn,
                serial_number=serial_number,
            )
        except Exception as e:
            return f"Error fetching tunnel health: {e}"

        if not resp:
            return f"No tunnel health data for gateway '{serial_number}'. Verify the serial using central_find_device."
        return resp
