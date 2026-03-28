from fastmcp import Context
from pycentral.new_monitoring.aps import MonitoringAPs
from pycentral.new_monitoring.gateways import MonitoringGateways

from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


def register(mcp):

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_ap_details(
        ctx: Context,
        serial_number: str,
    ) -> dict | str:
        """
        Get detailed monitoring data for a specific AP.

        Returns AP name, model, status, firmware, IP address,
        site, connected clients, radio info, and health status.
        Use central_find_device or central_get_devices to find
        the AP serial number first.

        Parameters:
            serial_number: AP serial number (required).
        """
        conn = ctx.lifespan_context["central_conn"]
        try:
            resp = MonitoringAPs.get_ap_details(
                central_conn=conn,
                serial_number=serial_number,
            )
        except Exception as e:
            return f"Error fetching AP details: {e}"

        if not resp:
            return f"No AP found with serial number '{serial_number}'. Verify the serial using central_find_device."
        return resp

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_switch_details(
        ctx: Context,
        serial_number: str,
    ) -> dict | str:
        """
        Get detailed monitoring data for a specific switch.

        Returns switch name, model, status, firmware, IP address,
        site, health, deployment mode, and health reasons. Use
        central_find_device or central_get_devices to find the
        switch serial number first.

        Parameters:
            serial_number: Switch serial number (required).
        """
        conn = ctx.lifespan_context["central_conn"]
        try:
            resp = retry_central_command(
                central_conn=conn,
                api_method="GET",
                api_path=(f"network-monitoring/v1/switches/{serial_number}"),
            )
        except Exception as e:
            return f"Error fetching switch details: {e}"

        code = resp.get("code", 0)
        if code == 404:
            return f"No switch found with serial number '{serial_number}'. Verify the serial using central_find_device."
        if not (200 <= code < 300):
            return f"Central API error (HTTP {code}): {resp.get('msg')}"
        return resp.get("msg", {})

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_gateway_details(
        ctx: Context,
        serial_number: str,
    ) -> dict | str:
        """
        Get detailed monitoring data for a specific gateway.

        Returns gateway name, model, status, firmware, IP address,
        site, interfaces, tunnels, and health status. Use
        central_find_device or central_get_devices to find the
        gateway serial number first.

        Parameters:
            serial_number: Gateway serial number (required).
        """
        conn = ctx.lifespan_context["central_conn"]
        try:
            resp = MonitoringGateways.get_gateway_details(
                central_conn=conn,
                serial_number=serial_number,
            )
        except Exception as e:
            return f"Error fetching gateway details: {e}"

        if not resp:
            return (
                f"No gateway found with serial number '{serial_number}'. Verify the serial using central_find_device."
            )
        return resp
