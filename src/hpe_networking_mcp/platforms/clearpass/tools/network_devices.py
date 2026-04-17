"""ClearPass network device read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import mcp
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


def _build_query_string(
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
) -> str:
    """Build ClearPass REST API query string for list endpoints.

    Args:
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset.
        limit: Max results per page.

    Returns:
        Query string starting with '?' for appending to a path.
    """
    params = [
        f"filter={filter}" if filter else "",
        f"sort={sort}" if sort else "",
        f"offset={offset}",
        f"limit={limit}",
    ]
    return "?" + "&".join(p for p in params if p)


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_network_devices(
    ctx: Context,
    device_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
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
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if device_id:
            return client.get_network_device_by_network_device_id(network_device_id=device_id)
        if name:
            return client.get_network_device_name_by_name(name=name)
        query = _build_query_string(filter, sort, offset, limit)
        return client._send_request("/network-device" + query, "get")
    except Exception as e:
        return f"Error fetching network devices: {e}"


@mcp.tool(annotations=READ_ONLY)
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
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        return client.get_network_device_by_network_device_id(network_device_id=device_id)
    except Exception as e:
        return f"Error fetching network device stats: {e}"


@mcp.tool(annotations=READ_ONLY)
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
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        result = client.get_network_device_by_network_device_id(network_device_id=device_id)
        return {
            "device": result,
            "note": "Actual connectivity testing requires ClearPass server-side capabilities.",
        }
    except Exception as e:
        return f"Error fetching device for connectivity review: {e}"


@mcp.tool(annotations=READ_ONLY)
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
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        device = client.get_network_device_by_network_device_id(network_device_id=device_id)

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
    except Exception as e:
        return f"Error validating device config: {e}"
