"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Assets``
Operations in this file: 6
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
    name="mist_create_org_asset",
    description="POST /api/v1/orgs/{org_id}/assets\n\ncreateOrgAsset\n\nCreate Org Asset",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_asset(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/assets",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_asset",
    description="DELETE /api/v1/orgs/{org_id}/assets/{asset_id}\n\ndeleteOrgAsset\n\nDelete Org Asset",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_asset(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    asset_id: Annotated[str, Field(description="path parameter 'asset_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/assets/{asset_id}",
        path_params={"org_id": org_id, "asset_id": asset_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_asset",
    description="GET /api/v1/orgs/{org_id}/assets/{asset_id}\n\ngetOrgAsset\n\nGet Org Asset Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_asset(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    asset_id: Annotated[str, Field(description="path parameter 'asset_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/assets/{asset_id}",
        path_params={"org_id": org_id, "asset_id": asset_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_import_org_assets",
    description='POST /api/v1/orgs/{org_id}/assets/import\n\nimportOrgAssets\n\nImport Org Assets. \n\nIt can be done via a CSV file or a JSON payload.\n\n#### CSV File Format\n```csv\nname,mac\n"asset_name",5c5b53010101\n```',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_import_org_assets(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/assets/import"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/assets/import",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_list_org_assets",
    description="GET /api/v1/orgs/{org_id}/assets\n\nlistOrgAssets\n\nGet List of Org Assets",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_assets(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/assets",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_asset",
    description="PUT /api/v1/orgs/{org_id}/assets/{asset_id}\n\nupdateOrgAsset\n\nUpdate Org Asset",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_asset(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    asset_id: Annotated[str, Field(description="path parameter 'asset_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/assets/{asset_id}",
        path_params={"org_id": org_id, "asset_id": asset_id},
        query_params=None,
        body=body,
    )
