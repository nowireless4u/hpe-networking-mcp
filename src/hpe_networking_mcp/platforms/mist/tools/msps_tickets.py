"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs Tickets``
Operations in this file: 2
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_count_msp_tickets",
    description="GET /api/v1/msps/{msp_id}/tickets/count\n\ncountMspTickets\n\nCount by Distinct Attributes of tickets",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_msp_tickets(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
    description="GET /api/v1/msps/{msp_id}/tickets\n\nlistMspTickets\n\nGet List of Tickets of a MSP",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_msp_tickets(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/tickets",
        path_params={"msp_id": msp_id},
        query_params={"start": start, "end": end, "duration": duration},
        body=None,
    )
