from typing import Literal

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.central import monitoring_api
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.models import Device
from hpe_networking_mcp.platforms.central.utils import (
    FilterField,
    as_comma_separated,
    build_odata_filter,
    clean_device_data,
    get_central_conn,
)

# API field definitions — update allowed_values when Central adds/removes enum options
DEVICE_FILTER_FIELDS: dict[str, FilterField] = {
    "site_id": FilterField("siteId"),
    "device_type": FilterField("deviceType", ["ACCESS_POINT", "SWITCH", "GATEWAY"]),
    "device_name": FilterField("deviceName"),
    "serial_number": FilterField("serialNumber"),
    "model": FilterField("model"),
    "device_function": FilterField("deviceFunction"),
    "is_provisioned": FilterField("isProvisioned"),
}


@tool(capability=Capability.READ)
async def central_get_devices(
    ctx: Context,
    site_id: str | None = None,
    device_type: Literal["ACCESS_POINT", "SWITCH", "GATEWAY"] | None = None,
    device_name: str | list[str] | None = None,
    serial_number: str | list[str] | None = None,
    model: str | list[str] | None = None,
    device_function: str | None = None,
    is_provisioned: bool | None = None,
    site_assigned: bool | None = None,
    sort: str | None = None,
) -> list[Device] | str:
    """
    Returns a filtered list of devices from Central using OData v4.0 filter syntax.

    Prefer this over any full-inventory fetch for targeted queries by site, type, model,
    or status. Call central_get_site_name_id_mapping first to obtain site_id values
    for filtering.

    Parameters:
    - site_id: Exact site ID or comma-separated list of IDs.
    - device_type: ACCESS_POINT, SWITCH, or GATEWAY. Comma-separated for multiple.
    - device_name: Device display name. Accepts a single string or a list of strings
      (e.g. "AP-001" or ["AP-001", "AP-002"]).
    - serial_number: Device serial number. Accepts a single string or a list of strings.
    - model: Device model (e.g., AP-735-RWF1). Accepts a single string or a list of strings.
    - device_function: Device function classification. Comma-separated for multiple.
    - is_provisioned: True returns only provisioned devices (sending Monitoring
      data to New Central). False returns only unprovisioned devices.
    - site_assigned: True returns only devices assigned to a site. False returns
      only devices not assigned to a site.
    - sort: Comma-separated sort expressions (e.g., 'deviceName asc, model desc').
      Supported fields: siteId, model, siteName, serialNumber, macAddress, deviceType,
      ipv4, deviceFunction, deviceName.
    """
    raw_pairs = [
        ("site_id", site_id),
        ("device_type", device_type),
        ("device_name", as_comma_separated(device_name)),
        ("serial_number", as_comma_separated(serial_number)),
        ("model", as_comma_separated(model)),
        ("device_function", device_function),
    ]
    pairs = [(DEVICE_FILTER_FIELDS[k], v) for k, v in raw_pairs if v is not None]

    if is_provisioned is not None:
        pairs.append(
            (
                DEVICE_FILTER_FIELDS["is_provisioned"],
                "Yes" if is_provisioned else "No",
            )
        )

    try:
        filter_str = build_odata_filter(pairs)
    except ValueError as e:
        raise ToolError({"status_code": 502, "message": f"Error: {e}"}) from e

    # normalize site_assigned: True -> "ASSIGNED", False -> "UNASSIGNED"
    site_assigned_str: str | None = None if site_assigned is None else ("ASSIGNED" if site_assigned else "UNASSIGNED")

    try:
        devices = await monitoring_api.get_all_device_inventory(
            central_conn=get_central_conn(ctx),
            filter_str=filter_str,
            site_assigned=site_assigned_str,
            sort=sort,
        )
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching devices: {e}"}) from e

    if not devices:
        return "No devices found matching the specified criteria."
    return clean_device_data(devices)


@tool(capability=Capability.READ)
async def central_find_device(
    ctx: Context,
    serial_number: str | None = None,
    device_name: str | None = None,
) -> Device | str:
    """
    Find a single device by unique identifier. Returns the device if exactly
    one match is found, otherwise returns an error message.

    Parameters:
    - serial_number: Device serial number (preferred — most reliable unique
      identifier).
    - device_name: Device display name. Use only if serial number is unknown.
    """
    if not serial_number and not device_name:
        return "Please provide at least one unique identifier: serial_number or device_name."

    if serial_number and device_name:
        return "Please provide only one unique identifier: either serial_number or device_name, not both."

    pairs = [
        (DEVICE_FILTER_FIELDS[k], v)
        for k, v in [
            ("device_name", device_name),
            ("serial_number", serial_number),
        ]
        if v is not None
    ]
    try:
        filter_str = build_odata_filter(pairs)
    except ValueError as e:
        raise ToolError({"status_code": 502, "message": f"Error: {e}"}) from e
    try:
        device_resp = await monitoring_api.get_device_inventory(
            central_conn=get_central_conn(ctx),
            filter_str=filter_str,
        )
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error occurred while fetching device data: {e}"}) from e
    if "items" not in device_resp:
        raise ToolError({"status_code": 502, "message": f"Unexpected API error response: {device_resp}"})

    if len(device_resp["items"]) == 0:
        return "No device found matching the provided criteria."
    if len(device_resp["items"]) > 1:
        return "Multiple devices found matching the criteria. Use serial_number for a unique match."
    return clean_device_data(device_resp["items"])[0]
