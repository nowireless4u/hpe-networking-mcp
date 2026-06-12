"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Asset Filters``
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
    name="mist_create_org_asset_filter",
    description="POST /api/v1/orgs/{org_id}/assetfilters\n\ncreateOrgAssetFilter\n\nCreate an organization-level BLE asset filter. Any subset of filter properties can be included, and a matching asset must meet all specified conditions.",
    capability=Capability.WRITE,
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
    description="DELETE /api/v1/orgs/{org_id}/assetfilters/{assetfilter_id}\n\ndeleteOrgAssetFilter\n\nDelete an organization-level BLE asset filter by filter ID.",
    capability=Capability.WRITE_DELETE,
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
    description="GET /api/v1/orgs/{org_id}/assetfilters/{assetfilter_id}\n\ngetOrgAssetFilter\n\nReturn one organization-level BLE asset filter, including its name, disabled state, and matching criteria.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/assetfilters\n\nlistOrgAssetFilters\n\nList organization-level BLE asset filters. Each filter operates independently, and an asset must match all specified filter properties for that filter to apply.",
    capability=Capability.READ,
)
async def mist_list_org_asset_filters(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
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
    description="PUT /api/v1/orgs/{org_id}/assetfilters/{assetfilter_id}\n\nupdateOrgAssetFilter\n\nUpdate an organization-level BLE asset filter's name, disabled state, or matching criteria.",
    capability=Capability.WRITE,
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
