"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Assets``
Operations in this file: 8
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
    name="mist_attach_site_asset_image",
    description="POST /api/v1/sites/{site_id}/assets/{asset_id}/image\n\nattachSiteAssetImage\n\nAttach Image to Site Asset",
    capability=Capability.WRITE,
)
async def mist_attach_site_asset_image(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    asset_id: Annotated[str, Field(description="path parameter 'asset_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/assets/{asset_id}/image"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/assets/{asset_id}/image",
        path_params={"site_id": site_id, "asset_id": asset_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_site_asset",
    description="POST /api/v1/sites/{site_id}/assets\n\ncreateSiteAsset\n\nCreate Site Asset",
    capability=Capability.WRITE,
)
async def mist_create_site_asset(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/assets",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_asset",
    description="DELETE /api/v1/sites/{site_id}/assets/{asset_id}\n\ndeleteSiteAsset\n\nDelete Site Asset",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_site_asset(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    asset_id: Annotated[str, Field(description="path parameter 'asset_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/assets/{asset_id}",
        path_params={"site_id": site_id, "asset_id": asset_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_site_asset_image",
    description="DELETE /api/v1/sites/{site_id}/assets/{asset_id}/image\n\ndeleteSiteAssetImage\n\nDelete Site Asset Image",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_site_asset_image(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    asset_id: Annotated[str, Field(description="path parameter 'asset_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/assets/{asset_id}/image",
        path_params={"site_id": site_id, "asset_id": asset_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_asset",
    description="GET /api/v1/sites/{site_id}/assets/{asset_id}\n\ngetSiteAsset\n\nGet Site Asset Details",
    capability=Capability.READ,
)
async def mist_get_site_asset(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    asset_id: Annotated[str, Field(description="path parameter 'asset_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/assets/{asset_id}",
        path_params={"site_id": site_id, "asset_id": asset_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_import_site_assets",
    description='POST /api/v1/sites/{site_id}/assets/import\n\nimportSiteAssets\n\nImport Site Assets. \n\nIt can be done via a CSV file or a JSON payload.\n\n## CSV File Format\n```csv\nname,mac\n"asset_name",5c5b53010101\n```',
    capability=Capability.WRITE,
)
async def mist_import_site_assets(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    upsert: Annotated[
        Any | None,
        Field(
            description="Whether to replace existing assets with the same MAC address during import. enum: `False`, `True`"
        ),
    ] = None,
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/assets/import"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/assets/import",
        path_params={"site_id": site_id},
        query_params={"upsert": upsert},
        body=body,
    )


@_mcp_tool(
    name="mist_list_site_assets",
    description="GET /api/v1/sites/{site_id}/assets\n\nlistSiteAssets\n\nList assets for a site. Use [List Org Assets](/#operations/listOrgAssets) to retrieve assets across the organization.",
    capability=Capability.READ,
)
async def mist_list_site_assets(
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
        "/api/v1/sites/{site_id}/assets",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_asset",
    description="PUT /api/v1/sites/{site_id}/assets/{asset_id}\n\nupdateSiteAsset\n\nUpdate Site Asset",
    capability=Capability.WRITE,
)
async def mist_update_site_asset(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    asset_id: Annotated[str, Field(description="path parameter 'asset_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/assets/{asset_id}",
        path_params={"site_id": site_id, "asset_id": asset_id},
        query_params=None,
        body=body,
    )
