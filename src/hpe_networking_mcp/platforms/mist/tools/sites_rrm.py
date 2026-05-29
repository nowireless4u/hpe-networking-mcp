"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites RRM``
Operations in this file: 5
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
    name="mist_get_site_channel_scores",
    description="GET /api/v1/sites/{site_id}/rrm/channel_scores/band/{band}\n\ngetSiteChannelScores\n\nGet Site Channel Scores",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_channel_scores(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    band: Annotated[Any, Field(description="802.11 Band")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/rrm/channel_scores/band/{band}",
        path_params={"site_id": site_id, "band": band},
        query_params={"start": start, "end": end},
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_current_channel_planning",
    description="GET /api/v1/sites/{site_id}/rrm/current\n\ngetSiteCurrentChannelPlanning\n\nGet Current Channel Planning",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_current_channel_planning(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/rrm/current",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_current_rrm_considerations",
    description="GET /api/v1/sites/{site_id}/rrm/current/devices/{device_id}/band/{band}\n\ngetSiteCurrentRrmConsiderations\n\nGet Current RRM Considerations for an AP on a Specific Band",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_current_rrm_considerations(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    band: Annotated[Any, Field(description="802.11 Band")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/rrm/current/devices/{device_id}/band/{band}",
        path_params={"site_id": site_id, "device_id": device_id, "band": band},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_current_rrm_neighbors",
    description="GET /api/v1/sites/{site_id}/rrm/neighbors/band/{band}\n\nlistSiteCurrentRrmNeighbors\n\nList Current RRM observed neighbors",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_current_rrm_neighbors(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    band: Annotated[Any, Field(description="802.11 Band")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/rrm/neighbors/band/{band}",
        path_params={"site_id": site_id, "band": band},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_rrm_events",
    description="GET /api/v1/sites/{site_id}/rrm/events\n\nlistSiteRrmEvents\n\nList Site RRM Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_rrm_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    band: Annotated[Any | None, Field(description="802.11 Band")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/rrm/events",
        path_params={"site_id": site_id},
        query_params={"band": band, "start": start, "end": end, "duration": duration, "limit": limit, "page": page},
        body=None,
    )
