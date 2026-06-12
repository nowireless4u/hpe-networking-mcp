"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Map Stacks``
Operations in this file: 2
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
    name="mist_create_site_map_stack",
    description="POST /api/v1/sites/{site_id}/mapstacks\n\ncreateSiteMapStack\n\nCreate Site Map Stack",
    capability=Capability.WRITE,
)
async def mist_create_site_map_stack(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/mapstacks",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_list_site_map_stacks",
    description="GET /api/v1/sites/{site_id}/mapstacks\n\nlistSiteMapStacks\n\nGet List of Site Map Stacks",
    capability=Capability.READ,
)
async def mist_list_site_map_stacks(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
    name: Annotated[str | None, Field(description="Filter by map stack name")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/mapstacks",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "page": page, "name": name},
        body=None,
    )
