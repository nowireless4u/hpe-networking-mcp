"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs SLEs``
Operations in this file: 1
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_get_msp_sle",
    description="GET /api/v1/msps/{msp_id}/insights/{metric}\n\ngetMspSle\n\nReturn MSP-level SLE insight metrics for the selected metric and time range. Depending on the metric, the response can include all organizations or the worst-performing organizations in the MSP.",
    capability=Capability.READ,
)
async def mist_get_msp_sle(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    metric: Annotated[
        str, Field(description="See [List Insight Metrics](/#operations/listInsightMetrics) for available metrics")
    ],
    sle: Annotated[
        str | None, Field(description="See [List Insight Metrics](/#operations/listInsightMetrics) for more details")
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/insights/{metric}",
        path_params={"msp_id": msp_id, "metric": metric},
        query_params={"sle": sle, "duration": duration, "interval": interval, "start": start, "end": end},
        body=None,
    )
