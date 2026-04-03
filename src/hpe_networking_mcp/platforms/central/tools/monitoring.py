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

        result = resp.get("msg", {})

        # Enrich with hardware-trends PoE data for all stack
        # members (switchTrends only shows the conductor)
        try:
            hw_resp = retry_central_command(
                central_conn=conn,
                api_method="GET",
                api_path=(f"network-monitoring/v1/switches/{serial_number}/hardware-trends"),
            )
            hw_data = hw_resp.get("msg", {})
            hw_response = hw_data.get("response", hw_data)
            metrics = hw_response.get("switchMetrics", [])

            if metrics:
                total_poe_available = 0.0
                total_poe_consumption = 0.0
                members_poe = []

                for m in metrics:
                    member_serial = m.get("serialNumber", "?")
                    member_role = m.get("switchRole", "")
                    # Get latest non-None sample
                    for s in reversed(m.get("samples", [])):
                        vals = s.get("data", [])
                        if len(vals) >= 5 and vals[3] is not None:
                            poe_a = float(vals[3]) if vals[3] else 0
                            poe_c = float(vals[4]) if vals[4] else 0
                            total_poe_available += poe_a
                            total_poe_consumption += poe_c
                            members_poe.append(
                                {
                                    "serial": member_serial,
                                    "role": member_role,
                                    "poe_available": poe_a,
                                    "poe_consumption": poe_c,
                                }
                            )
                            break

                result["poe_summary"] = {
                    "total_poe_available_watts": total_poe_available,
                    "total_poe_consumption_watts": total_poe_consumption,
                    "member_count": len(metrics),
                    "members": members_poe,
                }
        except Exception:
            pass  # If hardware-trends fails, return base data

        return result

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
