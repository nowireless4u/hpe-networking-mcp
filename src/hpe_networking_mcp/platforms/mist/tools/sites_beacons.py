"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Beacons``
Operations in this file: 5
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
    name="mist_create_site_beacon",
    description="POST /api/v1/sites/{site_id}/beacons\n\ncreateSiteBeacon\n\nCreate Site Beacon",
    capability=Capability.WRITE,
)
async def mist_create_site_beacon(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/beacons",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_beacon",
    description="DELETE /api/v1/sites/{site_id}/beacons/{beacon_id}\n\ndeleteSiteBeacon\n\nDelete Site Beacon",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_site_beacon(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    beacon_id: Annotated[str, Field(description="path parameter 'beacon_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/beacons/{beacon_id}",
        path_params={"site_id": site_id, "beacon_id": beacon_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_beacon",
    description="GET /api/v1/sites/{site_id}/beacons/{beacon_id}\n\ngetSiteBeacon\n\nGet Site Beacon Details",
    capability=Capability.READ,
)
async def mist_get_site_beacon(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    beacon_id: Annotated[str, Field(description="path parameter 'beacon_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/beacons/{beacon_id}",
        path_params={"site_id": site_id, "beacon_id": beacon_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_beacons",
    description="GET /api/v1/sites/{site_id}/beacons\n\nlistSiteBeacons\n\nGet List of Site Beacons",
    capability=Capability.READ,
)
async def mist_list_site_beacons(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/beacons",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_beacon",
    description="PUT /api/v1/sites/{site_id}/beacons/{beacon_id}\n\nupdateSiteBeacon\n\nUpdate Site Beacon",
    capability=Capability.WRITE,
)
async def mist_update_site_beacon(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    beacon_id: Annotated[str, Field(description="path parameter 'beacon_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/beacons/{beacon_id}",
        path_params={"site_id": site_id, "beacon_id": beacon_id},
        query_params=None,
        body=body,
    )
