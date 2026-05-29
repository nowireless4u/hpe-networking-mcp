"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Stats - Clients SDK``
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
    name="mist_get_site_sdk_stats",
    description="GET /api/v1/sites/{site_id}/stats/sdkclients/{sdkclient_id}\n\ngetSiteSdkStats\n\nGet Detail Stats of a SdkClient",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_sdk_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    sdkclient_id: Annotated[str, Field(description="path parameter 'sdkclient_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/sdkclients/{sdkclient_id}",
        path_params={"site_id": site_id, "sdkclient_id": sdkclient_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_sdk_stats_by_map",
    description="GET /api/v1/sites/{site_id}/stats/maps/{map_id}/sdkclients\n\ngetSiteSdkStatsByMap\n\nGet SdkClient Stats By Map",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_sdk_stats_by_map(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/maps/{map_id}/sdkclients",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=None,
    )
