from typing import Literal

from fastmcp import Context
from pycentral.new_monitoring.clients import Clients

from hpe_networking_mcp.platforms.central._registry import mcp
from hpe_networking_mcp.platforms.central.models import Client
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import (
    FilterField,
    build_odata_filter,
    clean_client_data,
)

MISSING_CLIENT_RESPONSE = "Resource not found for the given input."
# API field name mappings -- Literal annotations in the function signature are
# the source of truth for allowed values; Pydantic validates them before the
# tool body runs.
CLIENT_FILTER_FIELDS: dict[str, FilterField] = {
    "status": FilterField("status"),
    "connection_type": FilterField("clientConnectionType"),
    "wlan_name": FilterField("wlanName"),
    "vlan_id": FilterField("vlanId"),
    "tunnel_type": FilterField("tunnelType"),
}


@mcp.tool(annotations=READ_ONLY)
async def central_get_clients(
    ctx: Context,
    site_id: str | None = None,
    site_name: str | None = None,
    serial_number: str | None = None,
    connection_type: Literal["Wired", "Wireless"] | None = None,
    status: Literal["Connected", "Failed"] | None = None,
    wlan_name: str | None = None,
    vlan_id: str | None = None,
    tunnel_type: Literal["Port-based", "User-based", "Overlay"] | None = None,
    start_query_time: str | None = None,
    end_query_time: str | None = None,
) -> list[Client] | str:
    """
    Returns a filtered list of clients from Central using OData v4.0 filter syntax.

    Prefer this over any full-inventory fetch for targeted queries by site, status, or
    connection type. Call central_get_site_name_id_mapping first to obtain site_id values
    for filtering.

    Parameters:
        - site_id: Exact site ID.
        - site_name: Exact site name.
        - serial_number: Serial number of the device to which the client is connected.
        - connection_type: "Wired" or "Wireless".
        - status: "Connected" or "Failed".
        - wlan_name: WLAN name filter (wireless clients only).
        - vlan_id: VLAN ID filter.
        - tunnel_type: "Port-based", "User-based", or "Overlay".
        - start_query_time: Start of the query time window (ISO 8601).
        - end_query_time: End of the query time window (ISO 8601).

    Note: Wireless-only fields (wlan_name, wireless_band, wireless_channel,
    wireless_security, key_management, bssid, radio_mac) are omitted for wired
    clients. The port field is omitted for wireless clients.
    """
    raw_pairs = [
        ("status", status),
        ("connection_type", connection_type),
        ("wlan_name", wlan_name),
        ("vlan_id", vlan_id),
        ("tunnel_type", tunnel_type),
    ]
    pairs = [(CLIENT_FILTER_FIELDS[k], v) for k, v in raw_pairs if v is not None]
    filter_str = build_odata_filter(pairs)

    try:
        clients = Clients.get_all_clients(
            central_conn=ctx.lifespan_context["central_conn"],
            site_id=site_id,
            site_name=site_name,
            serial_number=serial_number,
            start_time=start_query_time,
            end_time=end_query_time,
            filter_str=filter_str,
        )
    except Exception as e:
        return f"Error occurred while fetching clients: {e}"

    if not clients:
        return "No clients found matching the specified criteria."
    return clean_client_data(clients)


@mcp.tool(annotations=READ_ONLY)
async def central_find_client(
    ctx: Context,
    mac_address: str,
) -> Client | str:
    """
    Find a single client by MAC address. Returns the client if found,
    otherwise returns an error message.

    Parameters:
    - mac_address: MAC address of the client to find.

    Note: Wireless-only fields (wlan_name, wireless_band, wireless_channel,
    wireless_security, key_management, bssid, radio_mac) are omitted for
    wired clients. The port field is omitted for wireless clients.
    """
    try:
        result = Clients.get_client_details(
            central_conn=ctx.lifespan_context["central_conn"],
            client_mac=mac_address,
        )
    except Exception as e:
        if MISSING_CLIENT_RESPONSE in str(e):
            return f"No client found with MAC address '{mac_address}'."
        return f"Error occurred while fetching client details: {e}"

    if not result:
        return f"No client found with MAC address '{mac_address}'."

    return clean_client_data([result])[0]
