"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Maps - Auto-placement``
Operations in this file: 9
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
    name="mist_clear_site_ap_auto_orient",
    description="POST /api/v1/sites/{site_id}/maps/{map_id}/clear_auto_orient\n\nclearSiteApAutoOrient\n\nThis API is used to destroy the autoorientations of a map or subset of APs on a map.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_clear_site_ap_auto_orient(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for POST /api/v1/sites/{site_id}/maps/{map_id}/clear_auto_orient"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/{map_id}/clear_auto_orient",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_clear_site_ap_autoplacement",
    description="POST /api/v1/sites/{site_id}/maps/{map_id}/clear_autoplacement\n\nclearSiteApAutoplacement\n\nThis API is used to destroy the cached autoplacement locations of a map or subset of APs on a map.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_clear_site_ap_autoplacement(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for POST /api/v1/sites/{site_id}/maps/{map_id}/clear_autoplacement"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/{map_id}/clear_autoplacement",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_confirm_site_ap_localization_data",
    description="POST /api/v1/sites/{site_id}/maps/{map_id}/use_auto_ap_values\n\nconfirmSiteApLocalizationData\n\nThis API is used to accept or reject the cached autoplacement and auto-orientation values of a map or subset of APs on a map. Any APs that have autoplacement values are stored in cache for up to 7 days while awaiting acceptance or rejection.\n\n```\nAccepting the autoplacement values overwrites the existing X, Y, and orientation of the accepted APs with their cached autoplacement values.\nRejecting the autoplacement values causes the APs to retain their current X, Y, and orientation.\n```\n\nOnce a decisi...",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_confirm_site_ap_localization_data(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for POST /api/v1/sites/{site_id}/maps/{map_id}/use_auto_ap_values"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/{map_id}/use_auto_ap_values",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_ap_auto_orientation",
    description="DELETE /api/v1/sites/{site_id}/maps/{map_id}/auto_orient\n\ndeleteSiteApAutoOrientation\n\nThis API is called to force stop auto placement for a given map",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_ap_auto_orientation(
    ctx: Context,
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/maps/{map_id}/auto_orient",
        path_params={"map_id": map_id, "site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_site_ap_autoplacement",
    description="DELETE /api/v1/sites/{site_id}/maps/{map_id}/auto_placement\n\ndeleteSiteApAutoplacement\n\nThis API is called to force stop auto placement for a given map",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_ap_autoplacement(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/maps/{map_id}/auto_placement",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_ap_auto_orientation",
    description="GET /api/v1/sites/{site_id}/maps/{map_id}/auto_orient\n\ngetSiteApAutoOrientation\n\nThis API is called to view the current status of auto orient for a given map.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_ap_auto_orientation(
    ctx: Context,
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/maps/{map_id}/auto_orient",
        path_params={"map_id": map_id, "site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_ap_auto_placement",
    description="GET /api/v1/sites/{site_id}/maps/{map_id}/auto_placement\n\ngetSiteApAutoplacement\n\nThis API is called to view the current status of auto placement for a given map.\n\n\n#### Status Descriptions\n\n| Status | Description |\n| --- | --- |\n| `pending` | Autoplacement has not been requested for this map |\n| `inprogress` | Autoplacement is currently processing |\n| `done` | The autoplacement process has completed |\n| `data_needed` | Additional position data is required for autoplacement. Users should verify the requested anchor APs have a position on the map |\n| `invalid_model` | Autoplacement is not su...",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_ap_auto_placement(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/maps/{map_id}/auto_placement",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_run_site_ap_autoplacement",
    description="POST /api/v1/sites/{site_id}/maps/{map_id}/auto_placement\n\nrunSiteApAutoplacement\n\nThis API is called to trigger auto placement for a map. For the auto placement feature to work, RTT-FTM data needs to be collected from the APs on the map.  \nThis scan is disruptive, and users must be notified of service disruption during the auto placement process. Repeated POST requests to this endpoint while a map is still running will be rejected.\n\n\n`force_collection` is set to `false` by default. If `force_collection` is set to `false`, the API attempts to start localization with existing data. If no dat...",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_run_site_ap_autoplacement(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/maps/{map_id}/auto_placement"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/{map_id}/auto_placement",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_start_site_ap_auto_orientation",
    description="POST /api/v1/sites/{site_id}/maps/{map_id}/auto_orient\n\nstartSiteApAutoOrientation\n\nThis API is called to trigger a map for auto orient. For auto orient feature to work, BLE data needs to be collected from the APs on the map. This precess is not disruptive unlike FTM collection. Repeated POST requests to this endpoint while a map is still running will be rejected.\n\n\n`force_collection` is set to `false` by default. If `force_collection`==`false`, the API attempts to start orientation with existing data. If no data exists, the API attempts to start collecting orientation data. If `force_colle...",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_start_site_ap_auto_orientation(
    ctx: Context,
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/maps/{map_id}/auto_orient"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/maps/{map_id}/auto_orient",
        path_params={"map_id": map_id, "site_id": site_id},
        query_params=None,
        body=body,
    )
