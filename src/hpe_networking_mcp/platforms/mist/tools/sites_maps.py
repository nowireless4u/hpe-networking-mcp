"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Sites Maps``
Operations in this file: 13
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
    name="mist_add_site_map_image",
    description="POST /api/v1/sites/{site_id}/maps/{map_id}/image\n\naddSiteMapImage\n\nAdd image map is a multipart POST which has an file (Image) and an optional json parameter",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_add_site_map_image(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/{map_id}/image",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_bulk_assign_site_aps_to_map",
    description="POST /api/v1/sites/{site_id}/maps/{map_id}/set_map\n\nbulkAssignSiteApsToMap\n\nThis API can be used to assign a list of AP Macs associated with site_id to the specified map_id. Note that map_id must be associated with corresponding site_id. This API obeys the following rules \n1. if AP is unassigned to any Map, it gets associated with map_id \n2. Any moved APs are returned in the response \n3. If the AP is considered a locked AP, no action will be taken",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_bulk_assign_site_aps_to_map(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/maps/{map_id}/set_map"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/{map_id}/set_map",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_site_map",
    description="POST /api/v1/sites/{site_id}/maps\n\ncreateSiteMap\n\nCreate Site Map",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_map(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_map",
    description="DELETE /api/v1/sites/{site_id}/maps/{map_id}\n\ndeleteSiteMap\n\nDelete Site Map",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_map(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/maps/{map_id}",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_site_map_image",
    description="DELETE /api/v1/sites/{site_id}/maps/{map_id}/image\n\ndeleteSiteMapImage\n\nDelete Site Map Image",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_map_image(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/maps/{map_id}/image",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_map",
    description="GET /api/v1/sites/{site_id}/maps/{map_id}\n\ngetSiteMap\n\nGet Site Map Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_map(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/maps/{map_id}",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_import_site_maps",
    description="POST /api/v1/sites/{site_id}/maps/import\n\nimportSiteMaps\n\nImport data from files is a multipart POST which has an file, an optional json, and an optional csv, to create floorplan, assign matching inventory to specific site, place ap if name or mac matches.\n\n# Note\nThis endpoint (at the site level), the AP must be already assigned to the site to be placed on the floorplan. If you want to place APs from the Org inventory, it is required to use the endpoint at the Org level [importOrgMaps](#operation/importOrgMaps)\n\n# CSV File Format\n```csv\nVendor AP name,Mist AP Mac\nUS Office AP-2,5c:5b:35:00...",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_import_site_maps(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/maps/import"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/import",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_import_site_wayfindings",
    description="POST /api/v1/sites/{site_id}/maps/{map_id}/wayfinding/import\n\nimportSiteWayfindings\n\nThis imports the vendor map meta data into the Map JSON. This is required by the SDK and App in order to access/render the vendor Map properly.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_import_site_wayfindings(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/{map_id}/wayfinding/import",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_list_site_maps",
    description="GET /api/v1/sites/{site_id}/maps\n\nlistSiteMaps\n\nGet List of Site Maps",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_maps(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/maps",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_replace_site_map_image",
    description="POST /api/v1/sites/{site_id}/maps/{map_id}/replace\n\nreplaceSiteMapImage\n\nReplace Map Image\n\n\nThis works like an PUT where the image will be replaced. If transform is provided, all the locations of the objects on the map (AP, Zone, Vbeacon, Beacon) will be transformed as well (relative to the new Map)",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_replace_site_map_image(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/maps/{map_id}/replace"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/{map_id}/replace",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_start_site_map_auto_geofence",
    description='POST /api/v1/sites/{site_id}/maps/{map_id}/auto_geofences\n\nstartSiteMapAutoGeofence\n\nThe auto geofence service is a map parsing service that uses map image data to identify the exterior of buildings in the map image also known as "geofences". This API processes a single given MapId. This map must have an image to parse for the auto geofence service. Repeated POST requests to this endpoint while the auto geofence service is processing the map will be rejected.',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_start_site_map_auto_geofence(
    ctx: Context,
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/{map_id}/auto_geofences",
        path_params={"map_id": map_id, "site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_start_site_maps_auto_geofence",
    description='POST /api/v1/sites/{site_id}/maps/auto_geofences\n\nstartSiteMapsAutoGeofence\n\nThe auto geofence service is a map parsing service that uses map image data to identify the exterior of buildings in the map image also known as "geofences". This API processes all maps for a given SiteId. The maps must have an image to parse for the auto geofence service. Repeated POST requests to this endpoint while the auto geofence service is processing the map will be rejected.',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_start_site_maps_auto_geofence(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/auto_geofences",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_map",
    description="PUT /api/v1/sites/{site_id}/maps/{map_id}\n\nupdateSiteMap\n\nUpdate Site Map",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_map(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/maps/{map_id}",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=body,
    )
