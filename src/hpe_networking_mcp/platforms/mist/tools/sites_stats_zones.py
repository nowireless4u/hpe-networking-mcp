"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Stats - Zones``
Operations in this file: 4
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
    name="mist_get_site_rssi_zone_stats",
    description="GET /api/v1/sites/{site_id}/stats/rssizones/{zone_id}\n\ngetSiteRssiZoneStats\n\nGet Detail RSSI Zone Stats",
    capability=Capability.READ,
)
async def mist_get_site_rssi_zone_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    zone_id: Annotated[str, Field(description="path parameter 'zone_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/rssizones/{zone_id}",
        path_params={"site_id": site_id, "zone_id": zone_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_zone_stats",
    description="GET /api/v1/sites/{site_id}/stats/zones/{zone_id}\n\ngetSiteZoneStats\n\nGet Detail Zone Stats",
    capability=Capability.READ,
)
async def mist_get_site_zone_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    zone_id: Annotated[str, Field(description="path parameter 'zone_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/zones/{zone_id}",
        path_params={"site_id": site_id, "zone_id": zone_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_rssi_zones_stats",
    description="GET /api/v1/sites/{site_id}/stats/rssizones\n\nlistSiteRssiZonesStats\n\nGet List of Site RSSI Zones Stats",
    capability=Capability.READ,
)
async def mist_list_site_rssi_zones_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/rssizones",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_zones_stats",
    description="GET /api/v1/sites/{site_id}/stats/zones\n\nlistSiteZonesStats\n\nGet List of Site Zones Stats",
    capability=Capability.READ,
)
async def mist_list_site_zones_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str | None, Field(description="Filter results by map identifier")] = None,
    min_duration: Annotated[int | None, Field(description="Filter results by minimum duration")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/zones",
        path_params={"site_id": site_id},
        query_params={"map_id": map_id, "min_duration": min_duration},
        body=None,
    )
