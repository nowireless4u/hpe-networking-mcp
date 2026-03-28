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


class Object_type(Enum):
    SITE = "site"
    CLIENT = "client"
    AP = "ap"
    GATEWAY = "gateway"
    MXEDGE = "mxedge"
    SWITCH = "switch"


@mcp.tool(
    name="mist_get_insight_metrics",
    description="Get insight metrics for a given object",
    tags={"sites_insights"},
    annotations={
        "title": "Get insight metrics",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_insight_metrics(
    site_id: Annotated[UUID, Field(description="Site ID")],
    object_type: Annotated[
        Object_type,
        Field(description=("Type of object to retrieve metrics for")),
    ],
    metric: Annotated[
        str,
        Field(
            description=(
                "Name of the metric to retrieve. Use the tool "
                "`mist_get_constants` with "
                "`object_type=insight_metrics` to see "
                "available metrics"
            )
        ),
    ],
    mac: Annotated[
        str,
        Field(
            description=(
                "MAC address of the client or device to "
                "retrieve metrics for. Required if object_type "
                "is 'client', 'ap', 'mxedge' or 'switch'"
            ),
            default=None,
        ),
    ],
    device_id: Annotated[
        UUID,
        Field(
            description=("ID of the gateway device to retrieve metrics for. Required if object_type is 'gateway'"),
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
    interval: Annotated[
        str,
        Field(
            description="Aggregation interval (e.g. 1h, 1d)",
            default=None,
        ),
    ],
    page: Annotated[
        int,
        Field(
            description="Page number for pagination",
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
    """Get insight metrics for a given object"""

    logger.debug("Tool get_insight_metrics called")
    logger.debug(
        "Input Parameters: site_id: %s, object_type: %s, "
        "metric: %s, mac: %s, device_id: %s, start: %s, "
        "end: %s, duration: %s, interval: %s, page: %s, "
        "limit: %s",
        site_id,
        object_type,
        metric,
        mac,
        device_id,
        start,
        end,
        duration,
        interval,
        page,
        limit,
    )

    apisession, response_format = await get_apisession()

    try:
        match object_type.value:
            case "site":
                response = mistapi.api.v1.sites.insights.getSiteInsightMetrics(
                    apisession,
                    site_id=str(site_id),
                    metric=str(metric),
                    start=str(start),
                    end=str(end),
                    duration=str(duration),
                    interval=str(interval),
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "client":
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForClient(
                    apisession,
                    site_id=str(site_id),
                    client_mac=str(mac),
                    metric=str(metric),
                    start=str(start),
                    end=str(end),
                    duration=str(duration),
                    interval=str(interval),
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "ap":
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForDevice(
                    apisession,
                    site_id=str(site_id),
                    device_mac=str(mac),
                    metric=str(metric),
                    start=str(start),
                    end=str(end),
                    duration=str(duration),
                    interval=str(interval),
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "gateway":
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForGateway(
                    apisession,
                    site_id=str(site_id),
                    device_id=str(device_id),
                    metric=str(metric),
                    start=str(start),
                    end=str(end),
                    duration=str(duration),
                    interval=str(interval),
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "mxedge":
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForMxEdge(
                    apisession,
                    site_id=str(site_id),
                    device_mac=str(mac),
                    metric=str(metric),
                    start=str(start),
                    end=str(end),
                    duration=str(duration),
                    interval=str(interval),
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "switch":
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForSwitch(
                    apisession,
                    site_id=str(site_id),
                    device_mac=str(mac),
                    metric=str(metric),
                    start=str(start),
                    end=str(end),
                    duration=str(duration),
                    interval=str(interval),
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
                            f"{[e.value for e in Object_type]}"
                        ),
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
