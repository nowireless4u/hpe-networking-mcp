"""Central tools for switch PoE and hardware trends."""

from fastmcp import Context

from hpe_networking_mcp.platforms.central._registry import mcp
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


@mcp.tool(annotations=READ_ONLY)
async def central_get_switch_hardware_trends(
    ctx: Context,
    serial_number: str,
) -> dict | str:
    """
    Get time-series hardware trends for a switch including PoE
    capacity, PoE consumption, CPU, memory, temperature, and
    power consumption.

    For stacked switches, returns data for ALL stack members
    when queried with the conductor serial or stack ID.

    Metrics per sample: cpuUtilization, memoryUtilization,
    systemTemperature, poeAvailable, poeConsumption,
    powerConsumption, totalPowerConsumption.

    Parameters:
        serial_number: Switch serial number or stack ID.
    """
    conn = ctx.lifespan_context["central_conn"]

    try:
        resp = retry_central_command(
            central_conn=conn,
            api_method="GET",
            api_path=(f"network-monitoring/v1/switches/{serial_number}/hardware-trends"),
        )
    except Exception as e:
        return f"Error fetching hardware trends: {e}"

    code = resp.get("code", 0)
    if code == 404:
        return f"Switch '{serial_number}' not found. For stacked switches, use the conductor serial or stack ID."
    if not (200 <= code < 300):
        return f"Central API error (HTTP {code}): {resp.get('msg')}"

    msg = resp.get("msg", {})
    data = msg.get("response", msg)
    keys = data.get("keys", [])
    metrics = data.get("switchMetrics", [])

    # Build a clean summary per member
    result = {
        "switch_id": data.get("id", serial_number),
        "keys": keys,
        "members": [],
    }
    total_poe_available = 0.0
    total_poe_consumption = 0.0

    for m in metrics:
        member = {
            "serial_number": m.get("serialNumber", "?"),
            "role": m.get("switchRole", ""),
            "sample_count": len(m.get("samples", [])),
        }
        # Get latest non-None sample for summary
        samples = m.get("samples", [])
        for s in reversed(samples):
            vals = s.get("data", [])
            if len(vals) >= 5 and vals[3] is not None:
                poe_avail = float(vals[3]) if vals[3] else 0
                poe_used = float(vals[4]) if vals[4] else 0
                member["latest"] = {
                    "cpu": vals[0],
                    "memory": vals[1],
                    "temperature": vals[2],
                    "poe_available_watts": poe_avail,
                    "poe_consumption_watts": poe_used,
                    "power_consumption": vals[5],
                    "total_power": vals[6],
                }
                total_poe_available += poe_avail
                total_poe_consumption += poe_used
                break

        member["samples"] = samples
        result["members"].append(member)

    result["total_poe_available_watts"] = total_poe_available
    result["total_poe_consumption_watts"] = total_poe_consumption
    result["member_count"] = len(metrics)
    return result


@mcp.tool(annotations=READ_ONLY)
async def central_get_switch_poe(
    ctx: Context,
    serial_number: str,
    limit: int = 100,
) -> dict | str:
    """
    Get per-port PoE data for a switch showing power drawn
    on each interface.

    Returns interfaceId, powerDrawnInWatts, and
    powerDeniedCount for each port with PoE activity.
    Ports with no PoE devices connected are not included.

    Parameters:
        serial_number: Switch serial number (required).
        limit: Max ports to return (default 100).
    """
    conn = ctx.lifespan_context["central_conn"]

    try:
        resp = retry_central_command(
            central_conn=conn,
            api_method="GET",
            api_path=(f"network-monitoring/v1/switches/{serial_number}/interface-poe"),
            api_params={"limit": limit},
        )
    except Exception as e:
        return f"Error fetching port PoE data: {e}"

    code = resp.get("code", 0)
    if code == 404:
        return f"Switch '{serial_number}' not found."
    if not (200 <= code < 300):
        return f"Central API error (HTTP {code}): {resp.get('msg')}"

    msg = resp.get("msg", {})
    data = msg.get("response", msg)
    items = data.get("items", [])

    if not items:
        return {
            "ports": [],
            "message": "No ports with active PoE draw.",
        }

    return {
        "ports": items,
        "count": len(items),
    }
