"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from hpe_networking_mcp.platforms.mist.client import get_apisession
from hpe_networking_mcp.platforms.mist.client import process_response, handle_network_error
from hpe_networking_mcp.platforms.mist.client import format_response
from hpe_networking_mcp.platforms.mist._registry import mcp
from loguru import logger

from pydantic import Field
from typing import Annotated
from uuid import UUID
from enum import Enum


class Query_type(Enum):
    HISTORY = "history"
    LAST_CONFIGS = "last_configs"


class Device_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    GATEWAY = "gateway"


@mcp.tool(
    name="mist_search_device_config_history",
    description="""Search for entries in device config history.
This tool can be used to track configuration changes over time, useful for troubleshooting issues that started after a config change.""",
    tags={"configuration"},
    annotations={
        "title": "Search device config history",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_device_config_history(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    query_type: Annotated[
        Query_type,
        Field(
            description="""Whether to search for config history entries or just retrieve the last config entry for each device"""
        ),
    ],
    device_type: Annotated[
        Device_type,
        Field(description="""Type of device to search config history for"""),
    ],
    device_mac: Annotated[
        str,
        Field(
            description="""MAC address of the device to search config history for""",
            default=None,
        ),
    ],
    start: Annotated[
        int, Field(description="""Start of time range (epoch seconds)""", default=None)
    ],
    end: Annotated[
        int, Field(description="""End of time range (epoch seconds)""", default=None)
    ],
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=20)
    ] = 20,
) -> dict | list | str:
    """Search for entries in device config history.
    This tool can be used to track configuration changes over time, useful for troubleshooting issues that started after a config change."""

    logger.debug("Tool search_device_config_history called")
    logger.debug(
        "Input Parameters: site_id: %s, query_type: %s, device_type: %s, device_mac: %s, start: %s, end: %s, limit: %s",
        site_id,
        query_type,
        device_type,
        device_mac,
        start,
        end,
        limit,
    )

    apisession, response_format = await get_apisession()

    try:
        object_type = query_type
        match object_type.value:
            case "history":
                response = mistapi.api.v1.sites.devices.searchSiteDeviceConfigHistory(
                    apisession,
                    site_id=str(site_id),
                    type=device_type.value if device_type else None,
                    mac=str(device_mac) if device_mac else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "last_configs":
                response = mistapi.api.v1.sites.devices.searchSiteDeviceLastConfigs(
                    apisession,
                    site_id=str(site_id),
                    device_type=device_type.value if device_type else None,
                    mac=str(device_mac) if device_mac else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Query_type]}",
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
