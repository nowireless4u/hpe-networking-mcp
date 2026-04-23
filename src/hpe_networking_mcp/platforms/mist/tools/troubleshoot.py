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


class Troubleshoot_type(Enum):
    WAN = "wan"
    WIRED = "wired"
    WIRELESS = "wireless"


@tool(
    name="mist_troubleshoot",
    description=(
        "Troubleshoot sites, devices, clients, and wired "
        "clients for maximum of last 7 days from current "
        "time. Use the `mist_search_client` tool to find a "
        "client MAC Address. Use the `mist_search_device` "
        "tool to find device MAC Address. **NOTE**: requires "
        "Marvis subscription license"
    ),
    tags={"marvis"},
    annotations={
        "title": "Troubleshoot",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def troubleshoot(
    org_id: Annotated[UUID, Field(description="Organization ID")],
    troubleshoot_type: Annotated[
        Troubleshoot_type,
        Field(
            description=(
                "Type of troubleshooting query to run. "
                "Possible values are `wan`, `wired`, and "
                "`wireless`. If `wan` is selected, the "
                "query will troubleshoot the WAN. If "
                "`wired` is selected, the query will "
                "troubleshoot the wired network. If "
                "`wireless` is selected, the query will "
                "troubleshoot the wireless network."
            )
        ),
    ],
    site_id: Annotated[UUID, Field(description="Site ID", default=None)],
    mac: Annotated[
        str,
        Field(
            description=(
                "Used to troubleshoot a specific client or "
                "device. MAC address of the client or "
                "device to run the troubleshooting query "
                "for. Not required if troubleshooting a "
                "whole site with `site_id`"
            ),
            default=None,
        ),
    ],
    start: Annotated[
        int,
        Field(
            description="Start of time range (epoch seconds)",
            default=None,
        ),
    ],
    end: Annotated[
        int,
        Field(
            description="End of time range (epoch seconds)",
            default=None,
        ),
    ],
) -> dict | list | str:
    """Troubleshoot sites, devices, clients."""

    logger.debug("Tool troubleshoot called")
    logger.debug(
        "Input Parameters: org_id: %s, troubleshoot_type: %s, site_id: %s, mac: %s, start: %s, end: %s",
        org_id,
        troubleshoot_type,
        site_id,
        mac,
        start,
        end,
    )

    apisession, response_format = await get_apisession()

    try:
        response = mistapi.api.v1.orgs.troubleshoot.troubleshootOrg(
            apisession,
            org_id=str(org_id),
            site_id=str(site_id) if site_id else None,
            type=troubleshoot_type.value,
            mac=str(mac) if mac else None,
            start=str(start) if start else None,
            end=str(end) if end else None,
        )
        await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
