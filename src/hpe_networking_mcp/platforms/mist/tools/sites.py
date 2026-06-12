"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites``
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
    name="mist_delete_site",
    description="DELETE /api/v1/sites/{site_id}\n\ndeleteSite\n\nDelete Site",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_site(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_info",
    description="GET /api/v1/sites/{site_id}\n\ngetSiteInfo\n\nProvides information about the site, including its name, address,\ntimezone, and associated templates. This endpoint is useful for retrieving\nthe current configuration and details of a specific site.",
    capability=Capability.READ,
)
async def mist_get_site_info(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_info",
    description="PUT /api/v1/sites/{site_id}\n\nupdateSiteInfo\n\nUpdates the configuration and metadata for an existing site. \n\n\nThis endpoint allows modification of site properties including location details (address, coordinates, timezone), template associations (alarm, network, RF, security policy templates), site group memberships, and general information (name, notes).\n\n\nAll fields are optional and only provided fields will be updated.",
    capability=Capability.WRITE,
)
async def mist_update_site_info(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )
