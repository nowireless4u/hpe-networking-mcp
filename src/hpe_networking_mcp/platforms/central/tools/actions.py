from typing import Literal

from fastmcp import Context
from mcp.types import ToolAnnotations
from pycentral.troubleshooting.troubleshooting import Troubleshooting

OPERATIONAL = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


def register(mcp):

    # ── Disconnect Tools ─────────────────────────────────────────────

    @mcp.tool(annotations=OPERATIONAL)
    async def central_disconnect_users_ssid(
        ctx: Context,
        serial_number: str,
        device_type: Literal["aos-s", "cx"],
        ssid: str,
    ) -> dict | str:
        """
        Disconnect all users from a specific SSID/WLAN on an access point.

        Use central_find_device to get the serial number and
        central_get_wlans to get the SSID name.

        Parameters:
            serial_number: AP serial number (required).
            device_type: AP type — "aos-s" or "cx" (required).
            ssid: SSID/WLAN name to disconnect users from (required).
        """
        conn = ctx.lifespan_context["central_conn"]

        try:
            resp = Troubleshooting.disconnect_all_users_ssid(
                central_conn=conn,
                device_type=device_type,
                serial_number=serial_number,
                network=ssid,
            )
        except Exception as e:
            return f"Error disconnecting users from SSID: {e}"

        if not resp:
            return "Disconnect users from SSID returned no results."
        return resp

    @mcp.tool(annotations=OPERATIONAL)
    async def central_disconnect_users_ap(
        ctx: Context,
        serial_number: str,
        device_type: Literal["aos-s", "cx"],
    ) -> dict | str:
        """
        Disconnect all users from an access point.

        Use central_find_device to get the AP serial number.

        Parameters:
            serial_number: AP serial number (required).
            device_type: AP type — "aos-s" or "cx" (required).
        """
        conn = ctx.lifespan_context["central_conn"]

        try:
            resp = Troubleshooting.disconnect_all_users(
                central_conn=conn,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            return f"Error disconnecting users from AP: {e}"

        if not resp:
            return "Disconnect users from AP returned no results."
        return resp

    @mcp.tool(annotations=OPERATIONAL)
    async def central_disconnect_client_ap(
        ctx: Context,
        serial_number: str,
        device_type: Literal["aos-s", "cx"],
        mac_address: str,
    ) -> dict | str:
        """
        Disconnect a specific client by MAC address from an access point.

        Use central_find_client to get the MAC address and
        central_find_device to get the AP serial number.

        Parameters:
            serial_number: AP serial number (required).
            device_type: AP type — "aos-s" or "cx" (required).
            mac_address: Client MAC address to disconnect (required).
        """
        conn = ctx.lifespan_context["central_conn"]

        try:
            resp = Troubleshooting.disconnect_client_mac_addr(
                central_conn=conn,
                device_type=device_type,
                serial_number=serial_number,
                mac_address=mac_address,
            )
        except Exception as e:
            return f"Error disconnecting client from AP: {e}"

        if not resp:
            return "Disconnect client from AP returned no results."
        return resp

    @mcp.tool(annotations=OPERATIONAL)
    async def central_disconnect_client_gateway(
        ctx: Context,
        serial_number: str,
        mac_address: str,
    ) -> dict | str:
        """
        Disconnect a specific client by MAC address from a gateway.

        Use central_find_client to get the MAC address and
        central_find_device to get the gateway serial number.

        Parameters:
            serial_number: Gateway serial number (required).
            mac_address: Client MAC address to disconnect (required).
        """
        conn = ctx.lifespan_context["central_conn"]

        try:
            resp = Troubleshooting.disconnect_user_mac_addr(
                central_conn=conn,
                device_type="gateways",
                serial_number=serial_number,
                mac_address=mac_address,
            )
        except Exception as e:
            return f"Error disconnecting client from gateway: {e}"

        if not resp:
            return "Disconnect client from gateway returned no results."
        return resp

    @mcp.tool(annotations=OPERATIONAL)
    async def central_disconnect_clients_gateway(
        ctx: Context,
        serial_number: str,
    ) -> dict | str:
        """
        Disconnect all clients from a gateway.

        Use central_find_device to get the gateway serial number.

        Parameters:
            serial_number: Gateway serial number (required).
        """
        conn = ctx.lifespan_context["central_conn"]

        try:
            resp = Troubleshooting.disconnect_all_clients(
                central_conn=conn,
                device_type="gateways",
                serial_number=serial_number,
            )
        except Exception as e:
            return f"Error disconnecting clients from gateway: {e}"

        if not resp:
            return "Disconnect clients from gateway returned no results."
        return resp

    # ── Port / PoE Bounce Tools ──────────────────────────────────────

    @mcp.tool(annotations=OPERATIONAL)
    async def central_port_bounce_switch(
        ctx: Context,
        serial_number: str,
        ports: str,
    ) -> dict | str:
        """
        Bounce ports on an Aruba CX edge/access switch to reset link state.

        SAFETY: Only use on edge/access layer switches with end-user
        devices or APs connected. NEVER use on core or aggregation
        switches — bouncing ports on those will disconnect downstream
        switches and cause network-wide outages. Only bounce ports
        with clients or APs connected — never bounce uplink, stack,
        trunk, or inter-switch ports.

        Use central_get_switch_details to verify the switch role and
        identify safe edge ports before bouncing.
        Port format: 1/1/1 (member/slot/port).

        Parameters:
            serial_number: Edge/access CX switch serial number (required).
            ports: Comma-separated port list, e.g. "1/1/1,1/1/2" (required).
        """
        conn = ctx.lifespan_context["central_conn"]
        port_list = [p.strip() for p in ports.split(",")]

        try:
            resp = Troubleshooting.port_bounce_test(
                central_conn=conn,
                device_type="cx",
                serial_number=serial_number,
                ports=port_list,
            )
        except Exception as e:
            return f"Error bouncing switch ports: {e}"

        if not resp:
            return "Port bounce returned no results."
        return resp

    @mcp.tool(annotations=OPERATIONAL)
    async def central_poe_bounce_switch(
        ctx: Context,
        serial_number: str,
        ports: str,
    ) -> dict | str:
        """
        Cycle PoE power on Aruba CX edge/access switch ports to
        reset connected PoE devices (APs, cameras, phones).

        SAFETY: Only use on edge/access layer switches with end-user
        devices or APs connected. NEVER use on core or aggregation
        switches. Only bounce ports with PoE-powered devices — never
        bounce uplink, stack, trunk, or inter-switch ports.

        Use central_get_switch_details to verify the switch role and
        identify safe edge ports before bouncing.
        Port format: 1/1/1 (member/slot/port).

        Parameters:
            serial_number: CX switch serial number (required).
            ports: Comma-separated port list, e.g. "1/1/1,1/1/2" (required).
        """
        conn = ctx.lifespan_context["central_conn"]
        port_list = [p.strip() for p in ports.split(",")]

        try:
            resp = Troubleshooting.poe_bounce_test(
                central_conn=conn,
                device_type="cx",
                serial_number=serial_number,
                ports=port_list,
            )
        except Exception as e:
            return f"Error bouncing PoE on switch ports: {e}"

        if not resp:
            return "PoE bounce returned no results."
        return resp

    @mcp.tool(annotations=OPERATIONAL)
    async def central_port_bounce_gateway(
        ctx: Context,
        serial_number: str,
        ports: str,
    ) -> dict | str:
        """
        Bounce ports on a gateway to reset link state.

        SAFETY: Only bounce edge/access ports with end-user devices
        connected. NEVER bounce uplink, WAN, or inter-switch ports
        — this will cause connectivity loss for downstream devices.

        Use central_get_gateway_details to identify safe ports.

        Parameters:
            serial_number: Gateway serial number (required).
            ports: Comma-separated port list (required).
        """
        conn = ctx.lifespan_context["central_conn"]
        port_list = [p.strip() for p in ports.split(",")]

        try:
            resp = Troubleshooting.port_bounce_test(
                central_conn=conn,
                device_type="gateways",
                serial_number=serial_number,
                ports=port_list,
            )
        except Exception as e:
            return f"Error bouncing gateway ports: {e}"

        if not resp:
            return "Port bounce returned no results."
        return resp

    @mcp.tool(annotations=OPERATIONAL)
    async def central_poe_bounce_gateway(
        ctx: Context,
        serial_number: str,
        ports: str,
    ) -> dict | str:
        """
        Cycle PoE power on gateway ports to reset connected PoE devices.

        SAFETY: Only bounce edge/access ports with PoE-powered devices
        connected. NEVER bounce uplink, WAN, or inter-switch ports.

        Use central_get_gateway_details to identify safe ports.

        Parameters:
            serial_number: Gateway serial number (required).
            ports: Comma-separated port list (required).
        """
        conn = ctx.lifespan_context["central_conn"]
        port_list = [p.strip() for p in ports.split(",")]

        try:
            resp = Troubleshooting.poe_bounce_test(
                central_conn=conn,
                device_type="gateways",
                serial_number=serial_number,
                ports=port_list,
            )
        except Exception as e:
            return f"Error bouncing PoE on gateway ports: {e}"

        if not resp:
            return "PoE bounce returned no results."
        return resp
