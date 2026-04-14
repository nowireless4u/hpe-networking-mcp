from typing import Literal

from fastmcp import Context
from mcp.types import ToolAnnotations
from pycentral.troubleshooting.troubleshooting import Troubleshooting

from hpe_networking_mcp.platforms.central._registry import mcp

OPERATIONAL = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


def _resolve_switch_id(conn, serial_number: str) -> str:
    """Resolve a switch serial to its stack ID if stacked.

    The Central troubleshooting API returns 404 for stacked switch
    serials — it requires the stack ID instead. This checks the
    switch details and returns the stack ID if present, otherwise
    returns the original serial number.
    """
    from hpe_networking_mcp.platforms.central.utils import (
        retry_central_command,
    )

    try:
        resp = retry_central_command(
            central_conn=conn,
            api_method="GET",
            api_path=(f"network-monitoring/v1/switches/{serial_number}"),
        )
        msg = resp.get("msg", {})
        stack_id = msg.get("stackId")
        if stack_id:
            return stack_id
    except Exception:
        pass
    return serial_number


# ── Disconnect Tools ─────────────────────────────────────────────


@mcp.tool(annotations=OPERATIONAL)
async def central_disconnect_users_ssid(
    ctx: Context,
    serial_number: str,
    device_type: Literal["aos-s", "cx"],
    ssid: str,
) -> dict | str:
    """
    Disconnect all users from a specific SSID/WLAN on a switch.

    Use central_find_device to get the serial number and
    central_get_wlans to get the SSID name.

    Parameters:
        serial_number: Switch serial number (required).
        device_type: Switch type — "aos-s" or "cx" (required).
        ssid: SSID/WLAN name to disconnect users from (required).
    """
    conn = ctx.lifespan_context["central_conn"]
    resolved_id = _resolve_switch_id(conn, serial_number)

    try:
        resp = Troubleshooting.disconnect_all_users_ssid(
            central_conn=conn,
            device_type=device_type,
            serial_number=resolved_id,
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
    Disconnect all users from a switch.

    Use central_find_device to get the switch serial number.

    Parameters:
        serial_number: Switch serial number (required).
        device_type: Switch type — "aos-s" or "cx" (required).
    """
    conn = ctx.lifespan_context["central_conn"]
    resolved_id = _resolve_switch_id(conn, serial_number)

    try:
        resp = Troubleshooting.disconnect_all_users(
            central_conn=conn,
            device_type=device_type,
            serial_number=resolved_id,
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
    Disconnect a specific client by MAC address from a switch.

    Use central_find_client to get the MAC address and
    central_find_device to get the switch serial number.

    Parameters:
        serial_number: Switch serial number (required).
        device_type: Switch type — "aos-s" or "cx" (required).
        mac_address: Client MAC address to disconnect (required).
    """
    conn = ctx.lifespan_context["central_conn"]
    resolved_id = _resolve_switch_id(conn, serial_number)

    try:
        resp = Troubleshooting.disconnect_client_mac_addr(
            central_conn=conn,
            device_type=device_type,
            serial_number=resolved_id,
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


# ── Helpers ──────────────────────────────────────────────────────


def _get_switch_total_poe(conn, serial_number: str) -> float:
    """Get total PoE consumption for a switch via hardware-trends.

    Returns total watts consumed across all stack members.
    Returns 0 if no data available.
    """
    from hpe_networking_mcp.platforms.central.utils import (
        retry_central_command,
    )

    try:
        resp = retry_central_command(
            central_conn=conn,
            api_method="GET",
            api_path=(f"network-monitoring/v1/switches/{serial_number}/hardware-trends"),
        )
        msg = resp.get("msg", {})
        data = msg.get("response", msg)
        total = 0.0
        for m in data.get("switchMetrics", []):
            for s in reversed(m.get("samples", [])):
                vals = s.get("data", [])
                if len(vals) >= 5 and vals[4] is not None:
                    total += float(vals[4])
                    break
        return total
    except Exception:
        return 0.0


def _get_switch_ports(conn, serial_number: str) -> dict:
    """Fetch port status for a switch. Returns {port_id: port_info}."""
    from hpe_networking_mcp.platforms.central.utils import (
        retry_central_command,
    )

    resp = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=(f"network-monitoring/v1/switches/{serial_number}/interfaces"),
        api_params={"limit": 200},
    )
    items = resp.get("msg", {}).get("items", [])
    return {p["id"]: p for p in items if "id" in p}


# ── Port / PoE Bounce Tools ──────────────────────────────────────


@mcp.tool(annotations=OPERATIONAL)
async def central_port_bounce_switch(
    ctx: Context,
    serial_number: str,
    ports: str,
) -> dict | str:
    """
    Bounce ports on an Aruba CX switch. Safety checks are
    enforced automatically — ports that are down, uplinks,
    or trunks will be skipped.

    Port format: 1/1/1 (member/slot/port).

    Parameters:
        serial_number: CX switch serial number.
        ports: Comma-separated port list, e.g. "1/1/1,1/1/2".
    """
    conn = ctx.lifespan_context["central_conn"]
    resolved_id = _resolve_switch_id(conn, serial_number)
    port_list = [p.strip() for p in ports.split(",")]

    try:
        port_info = _get_switch_ports(conn, serial_number)
    except Exception as e:
        return f"Error checking port status: {e}"

    safe_ports = []
    skipped = []
    for port_id in port_list:
        info = port_info.get(port_id)
        if not info:
            skipped.append({"port": port_id, "reason": "port not found"})
        elif info.get("uplink"):
            skipped.append({"port": port_id, "reason": "uplink port"})
        elif info.get("vlanMode") == "Trunk":
            skipped.append({"port": port_id, "reason": "trunk port"})
        elif info.get("operStatus") == "Down":
            skipped.append({"port": port_id, "reason": "port down — nothing connected"})
        else:
            safe_ports.append(port_id)

    if not safe_ports:
        return {
            "bounced": [],
            "skipped": skipped,
            "message": "No ports qualified for bounce.",
        }

    try:
        resp = Troubleshooting.port_bounce_test(
            central_conn=conn,
            device_type="cx",
            serial_number=resolved_id,
            ports=safe_ports,
        )
    except Exception as e:
        return f"Error bouncing switch ports: {e}"

    return {
        "bounced": safe_ports,
        "skipped": skipped,
        "result": resp if resp else "bounce completed",
    }


@mcp.tool(annotations=OPERATIONAL)
async def central_poe_bounce_switch(
    ctx: Context,
    serial_number: str,
    ports: str,
) -> dict | str:
    """
    Cycle PoE power on Aruba CX switch ports. Safety checks
    are enforced automatically — ports with no PoE draw,
    uplinks, or trunks will be skipped.

    Port format: 1/1/1 (member/slot/port).

    Parameters:
        serial_number: CX switch serial number.
        ports: Comma-separated port list, e.g. "1/1/1,1/1/2".
    """
    conn = ctx.lifespan_context["central_conn"]
    resolved_id = _resolve_switch_id(conn, serial_number)
    port_list = [p.strip() for p in ports.split(",")]

    # Quick pre-check: if total switch PoE consumption is 0,
    # skip the entire switch without checking individual ports
    total_poe = _get_switch_total_poe(conn, serial_number)
    if total_poe == 0:
        return {
            "bounced": [],
            "skipped": [{"port": p, "reason": "switch has zero total PoE draw"} for p in port_list],
            "message": ("Switch has no PoE consumption — nothing powered on any port."),
            "total_poe_watts": 0,
        }

    try:
        port_info = _get_switch_ports(conn, serial_number)
    except Exception as e:
        return f"Error checking port status: {e}"

    safe_ports = []
    skipped = []
    for port_id in port_list:
        info = port_info.get(port_id)
        if not info:
            skipped.append({"port": port_id, "reason": "port not found"})
        elif info.get("uplink"):
            skipped.append({"port": port_id, "reason": "uplink port"})
        elif info.get("poeStatus") in (None, "Not Used", ""):
            skipped.append(
                {
                    "port": port_id,
                    "reason": "no PoE draw — nothing powered",
                }
            )
        else:
            safe_ports.append(port_id)

    if not safe_ports:
        return {
            "bounced": [],
            "skipped": skipped,
            "message": "No ports qualified for PoE bounce.",
            "total_poe_watts": total_poe,
        }

    try:
        resp = Troubleshooting.poe_bounce_test(
            central_conn=conn,
            device_type="cx",
            serial_number=resolved_id,
            ports=safe_ports,
        )
    except Exception as e:
        return f"Error bouncing PoE on switch ports: {e}"

    return {
        "bounced": safe_ports,
        "skipped": skipped,
        "result": resp if resp else "PoE bounce completed",
    }


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
