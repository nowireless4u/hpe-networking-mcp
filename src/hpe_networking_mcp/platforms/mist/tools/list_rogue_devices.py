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

from hpe_networking_mcp.platforms.mist._registry import mcp
from hpe_networking_mcp.platforms.mist.client import (
    format_response,
    get_apisession,
    handle_network_error,
    process_response,
)


class Rogue_type(Enum):
    AP = "ap"
    CLIENT = "client"


class Rogue_ap_type(Enum):
    HONEYPOT = "honeypot"
    LAN = "lan"
    OTHERS = "others"
    SPOOF = "spoof"


@mcp.tool(
    name="mist_list_rogue_devices",
    description=(
        "Retrieve a list of rogue devices (APs or clients) "
        "for a site, with optional filters for rogue AP type "
        "and time range"
    ),
    tags={"sites_rogues"},
    annotations={
        "title": "List rogue devices",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def list_rogue_devices(
    site_id: Annotated[UUID, Field(description="Site ID")],
    rogue_type: Annotated[
        Rogue_type,
        Field(description=("Type of rogue device to filter by")),
    ],
    rogue_ap_type: Annotated[
        Rogue_ap_type,
        Field(
            description=("Type of rogue AP to filter by. Only applicable when filtering for rogue APs"),
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
    limit: Annotated[
        int,
        Field(
            description="Max number of results per page",
            default=20,
        ),
    ] = 20,
) -> dict | list | str:
    """Retrieve a list of rogue devices for a site."""

    logger.debug("Tool list_rogue_devices called")
    logger.debug(
        "Input Parameters: site_id: %s, rogue_type: %s, rogue_ap_type: %s, start: %s, end: %s, limit: %s",
        site_id,
        rogue_type,
        rogue_ap_type,
        start,
        end,
        limit,
    )

    apisession, response_format = await get_apisession()

    try:
        object_type = rogue_type

        if rogue_ap_type and rogue_type.value not in ["ap"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`rogue_ap_type` parameter can only be used when `rogue_type` is "ap".'),
                }
            )

        match object_type.value:
            case "ap":
                response = mistapi.api.v1.sites.insights.listSiteRogueAPs(
                    apisession,
                    site_id=str(site_id),
                    type=(rogue_ap_type.value if rogue_ap_type else None),
                    limit=limit,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                )
                await process_response(response)
            case "client":
                response = mistapi.api.v1.sites.insights.listSiteRogueClients(
                    apisession,
                    site_id=str(site_id),
                    limit=limit,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                )
                await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": (
                            f"Invalid object_type: "
                            f"{object_type.value}. Valid values "
                            f"are: "
                            f"{[e.value for e in Rogue_type]}"
                        ),
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
