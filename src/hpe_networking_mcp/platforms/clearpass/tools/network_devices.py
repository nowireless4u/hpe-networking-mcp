"""ClearPass network device read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get


@tool(capability=Capability.READ)
async def clearpass_get_network_devices(
    ctx: Context,
    device_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass network devices (RADIUS/TACACS+ clients).

    If device_id or name is provided, returns a single device.
    Otherwise returns a paginated list of all network devices.

    Args:
        device_id: Numeric ID for single-item lookup.
        name: Device name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if device_id:
            return await client.request("get", f"/network-device/{device_id}")
        if name:
            return await client.request("get", f"/network-device/name/{name}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/network-device" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching network devices: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_network_device_stats(
    ctx: Context,
    device_id: str,
) -> dict | str:
    """Get detailed stats for a specific ClearPass network device.

    Returns the full device record including IP address, vendor, RADIUS/TACACS
    settings, CoA port, and attributes.

    Args:
        device_id: Numeric ID of the network device.
    """
    try:
        client = await get_clearpass_client()
        return await client.request("get", f"/network-device/{device_id}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching network device stats: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_test_device_connectivity(
    ctx: Context,
    device_id: str,
) -> dict | str:
    """Retrieve a network device record for connectivity review.

    Returns the device configuration including IP, shared secret status, and
    protocol settings. Actual network reachability testing requires ClearPass
    server-side capabilities not available via the REST API.

    Args:
        device_id: Numeric ID of the network device to check.
    """
    try:
        client = await get_clearpass_client()
        result = await client.request("get", f"/network-device/{device_id}")
        return {
            "device": result,
            "note": "Actual connectivity testing requires ClearPass server-side capabilities.",
        }
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching device for connectivity review: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_validate_device_config(
    ctx: Context,
    device_id: str,
) -> dict | str:
    """Retrieve a network device record for configuration validation.

    Returns the device configuration for review. Validates that required fields
    (IP address, vendor, RADIUS/TACACS settings) are present and non-empty.

    Args:
        device_id: Numeric ID of the network device to validate.
    """
    try:
        client = await get_clearpass_client()
        device = await client.request("get", f"/network-device/{device_id}")

        issues: list[str] = []
        if isinstance(device, dict):
            if not device.get("ip_address"):
                issues.append("Missing IP address")
            if not device.get("vendor_name"):
                issues.append("Missing vendor name")

        return {
            "device": device,
            "validation_issues": issues if issues else "No issues found",
        }
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error validating device config: {e}"}) from e
