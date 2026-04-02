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
        Bounce ports on an Aruba CX edge/access switch.

        BEFORE calling this tool, you MUST:
        1. Call central_get_switch_details to verify it is an
           edge/access switch (not core/aggregation)
        2. Check that the target port has a client or AP connected
           with active PoE draw — skip ports with no PoE consumption
        3. Verify the port is an access port (not uplink/trunk/stack)

        NEVER bounce ports on core or aggregation switches — this
        will disconnect downstream switches and cause outages.

        Port format: 1/1/1 (member/slot/port).

        Parameters:
            serial_number: Edge/access CX switch serial number.
            ports: Comma-separated port list, e.g. "1/1/1,1/1/2".
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
        Cycle PoE power on Aruba CX edge/access switch ports.

        BEFORE calling this tool, you MUST:
        1. Call central_get_switch_details to verify it is an
           edge/access switch (not core/aggregation)
        2. Check that the target port has active PoE power draw
           — if PoE consumption is zero, SKIP that port
        3. Verify the port is an access port (not uplink/trunk/stack)

        NEVER use on core or aggregation switches.

        Port format: 1/1/1 (member/slot/port).

        Parameters:
            serial_number: Edge/access CX switch serial number.
            ports: Comma-separated port list, e.g. "1/1/1,1/1/2".
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

        BEFORE calling this tool, you MUST:
        1. Call central_get_gateway_details to check the port status
        2. Verify the port has a client connected — skip empty ports
        3. NEVER bounce uplink, WAN, or inter-switch ports

        Parameters:
            serial_number: Gateway serial number.
            ports: Comma-separated port list.
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
        Cycle PoE power on gateway ports to reset PoE devices.

        BEFORE calling this tool, you MUST:
        1. Call central_get_gateway_details to check port PoE status
        2. Verify the port has active PoE draw — skip if zero
        3. NEVER bounce uplink, WAN, or inter-switch ports

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
