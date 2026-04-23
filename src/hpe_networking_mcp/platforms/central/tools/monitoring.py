from typing import Literal

from fastmcp import Context
from pycentral.new_monitoring.aps import MonitoringAPs
from pycentral.new_monitoring.gateways import MonitoringGateways

from hpe_networking_mcp.platforms.central._registry import mcp
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import (
    FilterField,
    as_comma_separated,
    build_odata_filter,
    retry_central_command,
)

# Shared FilterField definitions for the AP filter surface. build_odata_filter
# consumes these and emits `eq '...'` for single values, `in (...)` for
# comma-separated ones — so accepting a list of models via as_comma_separated
# flows through naturally.
_AP_FILTER_FIELDS: dict[str, FilterField] = {
    "site_id": FilterField("siteId"),
    "site_name": FilterField("siteName"),
    "serial_number": FilterField("serialNumber"),
    "device_name": FilterField("deviceName"),
    "status": FilterField("status", ["ONLINE", "OFFLINE"]),
    "model": FilterField("model"),
    "firmware_version": FilterField("firmwareVersion"),
    "deployment": FilterField("deployment", ["Standalone", "Cluster", "Unspecified"]),
}


@mcp.tool(annotations=READ_ONLY)
async def central_get_aps(
    ctx: Context,
    site_id: str | None = None,
    site_name: str | None = None,
    serial_number: str | list[str] | None = None,
    device_name: str | list[str] | None = None,
    status: Literal["ONLINE", "OFFLINE"] | None = None,
    model: str | list[str] | None = None,
    firmware_version: str | list[str] | None = None,
    deployment: Literal["Standalone", "Cluster", "Unspecified"] | None = None,
    sort: str | None = None,
) -> list[dict] | str:
    """
    List access points with AP-specific filters.

    Returns AP name, serial, model, status, firmware, site, IP,
    radio info, and deployment type. Supports filtering by site,
    status, model, firmware, and deployment type.

    Parameters:
        site_id: Filter by site ID.
        site_name: Filter by site name.
        serial_number: AP serial number. Accepts a single string or a list of strings.
        device_name: AP name. Accepts a single string or a list of strings.
        status: ONLINE or OFFLINE.
        model: AP model. Accepts a single string or a list of strings.
        firmware_version: Firmware version. Accepts a single string or a list of strings.
        deployment: Standalone, Cluster, or Unspecified.
        sort: Sort expression (e.g. 'deviceName asc'). Supported fields:
            siteId, serialNumber, deviceName, model, status, deployment.
    """
    conn = ctx.lifespan_context["central_conn"]

    raw_pairs = [
        ("site_id", site_id),
        ("site_name", site_name),
        ("serial_number", as_comma_separated(serial_number)),
        ("device_name", as_comma_separated(device_name)),
        ("status", status),
        ("model", as_comma_separated(model)),
        ("firmware_version", as_comma_separated(firmware_version)),
        ("deployment", deployment),
    ]
    pairs = [(_AP_FILTER_FIELDS[k], v) for k, v in raw_pairs if v is not None]
    filter_str = build_odata_filter(pairs)

    try:
        kwargs: dict = {"central_conn": conn}
        if filter_str:
            kwargs["filter_str"] = filter_str
        if sort:
            kwargs["sort"] = sort
        aps = MonitoringAPs.get_all_aps(**kwargs)
    except Exception as e:
        return f"Error fetching access points: {e}"

    if not aps:
        return "No access points found matching the specified criteria."
    return aps


@mcp.tool(annotations=READ_ONLY)
async def central_get_ap_wlans(
    ctx: Context,
    serial_number: str,
    wlan_name: str | None = None,
) -> list[dict] | str:
    """
    Get WLANs currently active on a specific AP.

    Returns the WLANs being broadcast by the AP identified by serial
    number. Useful for troubleshooting — "which SSIDs is this AP
    broadcasting?" Use central_find_device to get the serial number.

    Parameters:
        serial_number: AP serial number (required).
        wlan_name: Filter by exact WLAN name (SSID). Applied client-side.
    """
    conn = ctx.lifespan_context["central_conn"]
    try:
        resp = MonitoringAPs.get_ap_wlans(
            central_conn=conn,
            serial_number=serial_number,
        )
    except Exception as e:
        return f"Error fetching AP WLANs: {e}"

    items = resp.get("items", []) if isinstance(resp, dict) else []
    if wlan_name:
        items = [w for w in items if w.get("wlanName") == wlan_name]

    if not items:
        return f"No WLANs found for AP '{serial_number}'."
    return items


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
        return f"No gateway found with serial number '{serial_number}'. Verify the serial using central_find_device."
    return resp
