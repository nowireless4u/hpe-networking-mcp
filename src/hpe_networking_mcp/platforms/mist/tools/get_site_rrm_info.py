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


class Rrm_info_type(Enum):
    CURRENT_CHANNEL_PLANNING = "current_channel_planning"
    CURRENT_RRM_CONSIDERATIONS = "current_rrm_considerations"
    CURRENT_RRM_NEIGHBORS = "current_rrm_neighbors"
    EVENTS = "events"


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"


@mcp.tool(
    name="mist_get_site_rrm_info",
    description=(
        "Retrieve Radio Resource Management (RRM) information "
        "for a site. Use current_channel_planning to get the "
        "current channel plan, current_rrm_considerations to "
        "get RRM considerations for a specific device and "
        "band, current_rrm_neighbors to list current RRM "
        "neighbor APs for a band, or events to list RRM "
        "change events over a time range."
    ),
    tags={"sites_rrm"},
    annotations={
        "title": "Get site rrm info",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_site_rrm_info(
    site_id: Annotated[UUID, Field(description="Site ID")],
    rrm_info_type: Annotated[
        Rrm_info_type,
        Field(
            description=(
                "Type of RRM information to retrieve: "
                "current_channel_planning returns the current "
                "channel plan for the site; "
                "current_rrm_considerations returns per-AP "
                "RRM considerations (requires device_id and "
                "band); current_rrm_neighbors lists current "
                "RRM neighbor APs for a band (requires band); "
                "events lists RRM change events over a time "
                "range"
            )
        ),
    ],
    device_id: Annotated[
        UUID,
        Field(
            description=(
                "ID of the AP to retrieve RRM considerations "
                "for. Required when rrm_info_type is "
                "current_rrm_considerations"
            ),
            default=None,
        ),
    ],
    band: Annotated[
        Band,
        Field(
            description=(
                "802.11 band. Required when rrm_info_type is current_rrm_considerations or current_rrm_neighbors"
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
    duration: Annotated[
        str,
        Field(
            description="Time range duration (e.g. 1d, 1h, 10m)",
            default=None,
        ),
    ],
    limit: Annotated[
        int,
        Field(
            description="Max number of results per page",
            default=200,
        ),
    ] = 200,
    page: Annotated[
        int,
        Field(
            description="Page number for pagination",
            default=1,
        ),
    ] = 1,
) -> dict | list | str:
    """Retrieve Radio Resource Management (RRM) information."""

    logger.debug("Tool get_site_rrm_info called")
    logger.debug(
        "Input Parameters: site_id: %s, rrm_info_type: %s, "
        "device_id: %s, band: %s, start: %s, end: %s, "
        "duration: %s, limit: %s, page: %s",
        site_id,
        rrm_info_type,
        device_id,
        band,
        start,
        end,
        duration,
        limit,
        page,
    )

    apisession, response_format = await get_apisession()

    try:
        object_type = rrm_info_type

        if object_type.value == "current_rrm_considerations" and not device_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": (
                        '`device_id` parameter is required when `rrm_info_type` is "current_rrm_considerations".'
                    ),
                }
            )

        if object_type.value == "current_rrm_considerations" and not band:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`band` parameter is required when `rrm_info_type` is "current_rrm_considerations".'),
                }
            )

        if object_type.value == "current_rrm_neighbors" and not band:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`band` parameter is required when `rrm_info_type` is "current_rrm_neighbors".'),
                }
            )

        if duration and rrm_info_type.value not in ["events"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`duration` parameter can only be used when `rrm_info_type` is "events".'),
                }
            )

        if limit and rrm_info_type.value not in ["events"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`limit` parameter can only be used when `rrm_info_type` is "events".'),
                }
            )

        if page and rrm_info_type.value not in ["events"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`page` parameter can only be used when `rrm_info_type` is "events".'),
                }
            )

        match object_type.value:
            case "current_channel_planning":
                response = mistapi.api.v1.sites.rrm.getSiteCurrentChannelPlanning(apisession, site_id=str(site_id))
                await process_response(response)
            case "current_rrm_considerations":
                response = mistapi.api.v1.sites.rrm.getSiteCurrentRrmConsiderations(
                    apisession,
                    site_id=str(site_id),
                    device_id=str(device_id),
                    band=str(band.value),
                )
                await process_response(response)
            case "current_rrm_neighbors":
                response = mistapi.api.v1.sites.rrm.listSiteCurrentRrmNeighbors(
                    apisession,
                    site_id=str(site_id),
                    band=str(band.value),
                )
                await process_response(response)
            case "events":
                response = mistapi.api.v1.sites.rrm.listSiteRrmEvents(
                    apisession,
                    site_id=str(site_id),
                    band=band.value if band else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=duration if duration else None,
                    limit=limit,
                    page=page,
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
                            f"{[e.value for e in Rrm_info_type]}"
                        ),
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
