"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Spectrum Analysis``
Operations in this file: 3
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
    name="mist_get_site_running_spectrum_analysis",
    description="GET /api/v1/sites/{site_id}/analyze_spectrum\n\ngetSiteRunningSpectrumAnalysis\n\nGet the running spectrum analysis for a site",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_running_spectrum_analysis(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/analyze_spectrum",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_initiate_site_analyze_spectrum",
    description='POST /api/v1/sites/{site_id}/analyze_spectrum\n\ninitiateSiteAnalyzeSpectrum\n\nInitiate a spectrum analysis for a site\n\n\nThe output will be available through websocket. As there can be multiple command\nissued against the same device at the same time and the output all goes through\nthe same websocket stream, session is introduced for demux.\n\n\n\n#### Subscribe to Device Command outputs\n\n`WS /api-ws/v1/stream`\n\n\n```json { "subscribe": "/sites/{site_id}/analyze_spectrum" } ```\n\n#### Example output from ws stream\n\n```json\n{\n  "event": "data",\n  "channel": "/sites/4ac1dcf4-9d8b-7211-65c4-057819f0862b...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_initiate_site_analyze_spectrum(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/analyze_spectrum",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_list_site_spectrum_analysis",
    description="GET /api/v1/sites/{site_id}/stats/analyze_spectrum\n\nlistSiteSpectrumAnalysis\n\nList the past spectrum analysis for a site",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_spectrum_analysis(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
        "/api/v1/sites/{site_id}/stats/analyze_spectrum",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "start": start, "end": end, "duration": duration},
        body=None,
    )
