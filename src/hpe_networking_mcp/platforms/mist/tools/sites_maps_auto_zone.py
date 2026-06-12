"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Maps - Auto-Zone``
Operations in this file: 3
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
    name="mist_delete_site_map_auto_zone",
    description="DELETE /api/v1/sites/{site_id}/maps/{map_id}/auto_zones\n\ndeleteSiteMapAutoZone\n\nThis API starts the auto zones service for a specified map. This map must have an image to parse for the auto zones service. Repeated POST requests to this endpoint while the auto zones service is processing the map or awaiting review will be rejected.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_site_map_auto_zone(
    ctx: Context,
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/maps/{map_id}/auto_zones",
        path_params={"map_id": map_id, "site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_map_auto_zone_status",
    description="GET /api/v1/sites/{site_id}/maps/{map_id}/auto_zones\n\ngetSiteMapAutoZoneStatus\n\nThis API provides the current status of the auto zones service for a given map",
    capability=Capability.READ,
)
async def mist_get_site_map_auto_zone_status(
    ctx: Context,
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/maps/{map_id}/auto_zones",
        path_params={"map_id": map_id, "site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_start_site_map_auto_zone",
    description="POST /api/v1/sites/{site_id}/maps/{map_id}/auto_zones\n\nstartSiteMapAutoZone\n\nThis API starts the auto zones service for a specified map. This map must have an image to parse for the auto zones service. Repeated POST requests to this endpoint while the auto zones service is processing the map will be rejected.",
    capability=Capability.WRITE,
)
async def mist_start_site_map_auto_zone(
    ctx: Context,
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/{map_id}/auto_zones",
        path_params={"map_id": map_id, "site_id": site_id},
        query_params=None,
        body=None,
    )
