"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``application``
Operations in this file: 1
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_application_trends",
    description="GET /applicationTrends\n\ngetApplicationTrends\n\nGet application bandwidth trends and statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_application_trends(
    ctx: Context,
    startDate: Annotated[
        int,
        Field(
            description="Start timestamp in milliseconds (epoch time). Used with endDate to determine the stat granularity: <=60min returns MINUTE stats, <=60hrs returns HOURLY stats, <=60 days returns DAILY stats."
        ),
    ],
    endDate: Annotated[
        int,
        Field(
            description="End timestamp in milliseconds (epoch time). The time range (endDate - startDate) must not exceed 60 days. Stats granularity is auto-determined based on range."
        ),
    ],
    traffic: Annotated[
        str,
        Field(
            description="Filter by traffic type. Determines which category of network traffic to include in bandwidth statistics."
        ),
    ],
    bound: Annotated[
        str,
        Field(
            description="Traffic direction filter. Select inbound for received traffic or outbound for transmitted traffic."
        ),
    ],
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    customRangeUsed: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, applies custom time range rounding logic for drill-down queries. Affects how start/end times are rounded based on previousStatType.",
        ),
    ] = None,
    previousStatType: Annotated[
        str | None,
        Field(
            default=None,
            description="Previous stat granularity used before drill-down. When customRangeUsed is true, this determines time rounding behavior for zooming into data.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startDate is not None:
        query_params["startDate"] = startDate
    if endDate is not None:
        query_params["endDate"] = endDate
    if traffic is not None:
        query_params["traffic"] = traffic
    if bound is not None:
        query_params["bound"] = bound
    if nePk is not None:
        query_params["nePk"] = nePk
    if customRangeUsed is not None:
        query_params["customRangeUsed"] = customRangeUsed
    if previousStatType is not None:
        query_params["previousStatType"] = previousStatType
    return await edgeconnect_request(
        ctx,
        "GET",
        "/applicationTrends",
        query_params=query_params or None,
    )
