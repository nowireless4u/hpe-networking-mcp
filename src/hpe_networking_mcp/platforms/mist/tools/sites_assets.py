"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Assets``
Operations in this file: 8
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
    name="mist_attach_site_asset_image",
    description="POST /api/v1/sites/{site_id}/assets/{asset_id}/image\n\nattachSiteAssetImage\n\nAttach Image to Site Asset",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_import_site_assets(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    upsert: Annotated[
        Any | None,
        Field(
            description="API will replace the assets with same mac if provided `upsert`==`True`, otherwise will report in errors in response."
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
    description="GET /api/v1/sites/{site_id}/assets\n\nlistSiteAssets\n\nGet List of Site Assets",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_assets(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
