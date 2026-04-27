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
from fastmcp import Context
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


class Object_type(Enum):
    SITE = "site"
    CLIENT = "client"
    AP = "ap"
    GATEWAY = "gateway"
    MXEDGE = "mxedge"
    SWITCH = "switch"


def _mac_to_device_id(mac: str) -> str | None:
    """Construct a Mist device_id UUID from a MAC address.

    Mist device UUIDs follow the deterministic pattern
    ``00000000-0000-0000-1000-<mac_lowercase_no_separators>``.

    Returns ``None`` if the MAC isn't 12 hex chars (with or without
    separators) — caller surfaces a tool-level error instead of letting
    a raise propagate, which would crash the code-mode sandbox.
    """
    clean = mac.lower().replace(":", "").replace("-", "")
    if len(clean) != 12 or not all(c in "0123456789abcdef" for c in clean):
        return None
    return f"00000000-0000-0000-1000-{clean}"


@tool(
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
    ctx: Context,
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
                "MAC address of the client or device to retrieve metrics for. "
                "Required if object_type is 'client', 'ap', 'mxedge' or 'switch'. "
                "Accepts 12 hex chars with or without colons. "
                "For object_type='ap' or 'gateway', this is converted to the "
                "Mist device_id UUID automatically — pass device_id directly "
                "instead if you already have it."
            ),
            default=None,
        ),
    ],
    device_id: Annotated[
        UUID,
        Field(
            description=(
                "UUID of the AP or gateway device to retrieve metrics for. "
                "Optional alternative to `mac` for object_type='ap' or 'gateway' — "
                "if not provided, it is derived from `mac` via the Mist "
                "convention 00000000-0000-0000-1000-<mac>."
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

    apisession, response_format = await get_apisession(ctx)

    try:
        start_str = str(start) if start else None
        end_str = str(end) if end else None
        duration_str = duration if duration else None
        interval_str = interval if interval else None

        match object_type.value:
            case "site":
                # Bypass mistapi.api.v1.sites.insights.getSiteInsightMetrics — that
                # SDK function builds `/insights?metrics=X`, but the real Mist
                # endpoint is `/insights/{metric}` (matching every `For*` variant).
                uri = f"/api/v1/sites/{site_id}/insights/{metric}"
                query_params: dict[str, str] = {}
                if start_str:
                    query_params["start"] = start_str
                if end_str:
                    query_params["end"] = end_str
                if duration_str:
                    query_params["duration"] = duration_str
                if interval_str:
                    query_params["interval"] = interval_str
                if limit:
                    query_params["limit"] = str(limit)
                if page:
                    query_params["page"] = str(page)
                response = apisession.mist_get(uri=uri, query=query_params)
                await process_response(response)
            case "client":
                if not mac:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`mac` is required when object_type='client'.",
                        }
                    )
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForClient(
                    apisession,
                    site_id=str(site_id),
                    client_mac=str(mac),
                    metrics=str(metric),
                    start=start_str,
                    end=end_str,
                    duration=duration_str,
                    interval=interval_str,
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "ap":
                if not device_id and not mac:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`mac` or `device_id` is required when object_type='ap'.",
                        }
                    )
                ap_device_id = str(device_id) if device_id else _mac_to_device_id(str(mac))
                if ap_device_id is None:
                    return f"Error: invalid MAC address format: {mac!r}"
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForAP(
                    apisession,
                    site_id=str(site_id),
                    device_id=ap_device_id,
                    metrics=str(metric),
                    start=start_str,
                    end=end_str,
                    duration=duration_str,
                    interval=interval_str,
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "gateway":
                if not device_id and not mac:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`mac` or `device_id` is required when object_type='gateway'.",
                        }
                    )
                gw_device_id = str(device_id) if device_id else _mac_to_device_id(str(mac))
                if gw_device_id is None:
                    return f"Error: invalid MAC address format: {mac!r}"
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForGateway(
                    apisession,
                    site_id=str(site_id),
                    device_id=gw_device_id,
                    metrics=str(metric),
                    start=start_str,
                    end=end_str,
                    duration=duration_str,
                    interval=interval_str,
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "mxedge":
                if not mac:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`mac` is required when object_type='mxedge'.",
                        }
                    )
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForMxEdge(
                    apisession,
                    site_id=str(site_id),
                    device_mac=str(mac),
                    metric=str(metric),
                    start=start_str,
                    end=end_str,
                    duration=duration_str,
                    interval=interval_str,
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "switch":
                if not mac:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`mac` is required when object_type='switch'.",
                        }
                    )
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForSwitch(
                    apisession,
                    site_id=str(site_id),
                    device_mac=str(mac),
                    metric=str(metric),
                    start=start_str,
                    end=end_str,
                    duration=duration_str,
                    interval=interval_str,
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
