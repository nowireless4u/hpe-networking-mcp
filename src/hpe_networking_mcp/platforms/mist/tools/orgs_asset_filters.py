"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Asset Filters``
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
    name="mist_create_org_asset_filter",
    description="POST /api/v1/orgs/{org_id}/assetfilters\n\ncreateOrgAssetFilter\n\nCreate Asset Filter\n\nCreates a single BLE asset filter for the given site. Any subset of filter properties can be included in the filter. A matching asset must meet the conditions of all given filter properties (logical ‘AND’).",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_asset_filter(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/assetfilters"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/assetfilters",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_asset_filter",
    description="DELETE /api/v1/orgs/{org_id}/assetfilters/{assetfilter_id}\n\ndeleteOrgAssetFilter\n\nDeletes an existing BLE asset filter for the given site.",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_asset_filter(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    assetfilter_id: Annotated[str, Field(description="path parameter 'assetfilter_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/assetfilters/{assetfilter_id}",
        path_params={"org_id": org_id, "assetfilter_id": assetfilter_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_asset_filter",
    description="GET /api/v1/orgs/{org_id}/assetfilters/{assetfilter_id}\n\ngetOrgAssetFilter\n\nGet Org Asset Filter Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_asset_filter(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    assetfilter_id: Annotated[str, Field(description="path parameter 'assetfilter_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/assetfilters/{assetfilter_id}",
        path_params={"org_id": org_id, "assetfilter_id": assetfilter_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_asset_filters",
    description='GET /api/v1/orgs/{org_id}/assetfilters\n\nlistOrgAssetFilters\n\nGet List of Org BLE asset filters. \nEach asset filter in the list operates independently. For a filter object to match an asset, all of the filter properties must match (logical ‘AND’ of each filter property). For example, the "Visitor Tags" filter below will match an asset when both the "ibeacon\\_uuid" and "ibeacon_major" properties match the asset. All non-matching assets are ignored.',
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_asset_filters(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/assetfilters",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_asset_filter",
    description="PUT /api/v1/orgs/{org_id}/assetfilters/{assetfilter_id}\n\nupdateOrgAssetFilter\n\nUpdates an existing BLE asset filter for the given site.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_asset_filter(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    assetfilter_id: Annotated[str, Field(description="path parameter 'assetfilter_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/assetfilters/{assetfilter_id}",
        path_params={"org_id": org_id, "assetfilter_id": assetfilter_id},
        query_params=None,
        body=body,
    )
