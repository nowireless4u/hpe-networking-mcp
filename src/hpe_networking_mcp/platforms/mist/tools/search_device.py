"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from enum import Enum
from typing import Annotated
from uuid import UUID

import mistapi
from fastmcp.exceptions import ToolError
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.mist._registry import tool
from hpe_networking_mcp.platforms.mist.client import (
    format_response,
    get_apisession,
    handle_network_error,
    process_response,
)
from hpe_networking_mcp.platforms.mist.utils import as_comma_separated


class Device_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    GATEWAY = "gateway"


class Status(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


@tool(
    name="mist_search_device",
    description=(
        "Search a network device in the Organization "
        "Inventory. This tool provides a consolidated view "
        "of all devices within an organization, even those "
        "not assigned to any site. This can be used to "
        "quickly search for a device across the whole "
        "organization. It allows filtering by various "
        "attributes such as serial number, model, MAC "
        "address, firmware version, device type, and "
        "connection status. This tool is useful for quickly "
        "finding specific devices or getting an overview of "
        "the organization's inventory without needing to "
        "query each site separately."
    ),
    tags={"devices"},
    annotations={
        "title": "Search device",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_device(
    org_id: Annotated[UUID, Field(description="Organization ID")],
    site_id: Annotated[UUID, Field(description="Site ID", default=None)],
    serial: Annotated[
        str,
        Field(
            description=("Serial number of the device to filter inventory by"),
            default=None,
        ),
    ],
    model: Annotated[
        str | list[str],
        Field(
            description=(
                "Device model to filter inventory by. Accepts a single string or a list of strings. "
                "Partial match allowed with wildcard * (e.g. `AP*` will match `AP43` and `AP41`)."
            ),
            default=None,
        ),
    ],
    mac: Annotated[
        str,
        Field(
            description=(
                "MAC address. Partial match allowed with "
                "wildcard * (e.g. `*5b35*` will match "
                "`5c5b350e0001` and `5c5b35000301`)"
            ),
            default=None,
        ),
    ],
    version: Annotated[
        str | list[str],
        Field(
            description=(
                "Firmware version of the device to filter inventory by. Accepts a single string or a list of strings."
            ),
            default=None,
        ),
    ],
    device_type: Annotated[
        Device_type,
        Field(
            description=("Type of the device to filter inventory by"),
            default=None,
        ),
    ],
    status: Annotated[
        Status,
        Field(
            description=("Connection status of the device to filter inventory by"),
            default=None,
        ),
    ],
    text: Annotated[
        str,
        Field(
            description=(
                "Text to search for in device attributes "
                "(name, serial number, MAC). Use the "
                "wildcard `*` for partial matches (e.g. "
                "`london` will match `london-1`, "
                "`london-2`, `my-london-device`...)"
            ),
            default=None,
        ),
    ],
    limit: Annotated[
        int,
        Field(
            description="Max number of results per page",
            default=20,
        ),
    ] = 20,
) -> dict | list | str:
    """Search a network device in the Organization Inventory."""

    logger.debug("Tool search_device called")
    logger.debug(
        "Input Parameters: org_id: %s, site_id: %s, "
        "serial: %s, model: %s, mac: %s, version: %s, "
        "device_type: %s, status: %s, text: %s, limit: %s",
        org_id,
        site_id,
        serial,
        model,
        mac,
        version,
        device_type,
        status,
        text,
        limit,
    )

    apisession, response_format = await get_apisession()

    try:
        kwargs: dict = {
            "org_id": str(org_id),
            "limit": limit,
        }
        if serial:
            kwargs["serial"] = serial
        model_arg = as_comma_separated(model)
        if model_arg:
            kwargs["model"] = model_arg
        if device_type:
            kwargs["type"] = device_type.value
        if mac:
            kwargs["mac"] = mac
        if site_id:
            kwargs["site_id"] = str(site_id)
        version_arg = as_comma_separated(version)
        if version_arg:
            kwargs["version"] = version_arg
        if text:
            kwargs["text"] = text
        if status:
            kwargs["status"] = status.value
        response = mistapi.api.v1.orgs.inventory.searchOrgInventory(
            apisession,
            **kwargs,
        )
        await process_response(response)
        if isinstance(response.data, dict):
            for device in response.data.get("results", []):
                if device.get("vc_mac"):
                    device["device_id"] = f"00000000-0000-0000-1000-{device['vc_mac']}"
                else:
                    device["device_id"] = f"00000000-0000-0000-1000-{device['mac']}"
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
