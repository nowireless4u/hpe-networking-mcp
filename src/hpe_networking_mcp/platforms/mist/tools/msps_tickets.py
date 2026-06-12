"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs Tickets``
Operations in this file: 2
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
    name="mist_count_msp_tickets",
    description="GET /api/v1/msps/{msp_id}/tickets/count\n\ncountMspTickets\n\nReturn distinct counts of MSP support tickets grouped by the requested field, such as organization, status, or ticket type.",
    capability=Capability.READ,
)
async def mist_count_msp_tickets(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    distinct: Annotated[
        Any | None, Field(description="Field used to group this count response. enum: `org_id`, `status`, `type`")
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/tickets/count",
        path_params={"msp_id": msp_id},
        query_params={"distinct": distinct, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_list_msp_tickets",
    description="GET /api/v1/msps/{msp_id}/tickets\n\nlistMspTickets\n\nList support tickets associated with this MSP for the requested time range.",
    capability=Capability.READ,
)
async def mist_list_msp_tickets(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
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
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/tickets",
        path_params={"msp_id": msp_id},
        query_params={"start": start, "end": end, "duration": duration},
        body=None,
    )
