"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Sitegroups``
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
    name="mist_create_org_site_group",
    description="POST /api/v1/orgs/{org_id}/sitegroups\n\ncreateOrgSiteGroup\n\nCreate Org Site Group",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_site_group(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/sitegroups",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_site_group",
    description="DELETE /api/v1/orgs/{org_id}/sitegroups/{sitegroup_id}\n\ndeleteOrgSiteGroup\n\nDelete Org Site Group",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_site_group(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sitegroup_id: Annotated[str, Field(description="path parameter 'sitegroup_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/sitegroups/{sitegroup_id}",
        path_params={"org_id": org_id, "sitegroup_id": sitegroup_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_site_group",
    description="GET /api/v1/orgs/{org_id}/sitegroups/{sitegroup_id}\n\ngetOrgSiteGroup\n\nGet Org Site Group",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_site_group(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sitegroup_id: Annotated[str, Field(description="path parameter 'sitegroup_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/sitegroups/{sitegroup_id}",
        path_params={"org_id": org_id, "sitegroup_id": sitegroup_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_site_groups",
    description="GET /api/v1/orgs/{org_id}/sitegroups\n\nlistOrgSiteGroups\n\nGet List of Org Site Groups",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_site_groups(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/sitegroups",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_site_group",
    description="PUT /api/v1/orgs/{org_id}/sitegroups/{sitegroup_id}\n\nupdateOrgSiteGroup\n\nUpdate Org Site Group",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_site_group(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sitegroup_id: Annotated[str, Field(description="path parameter 'sitegroup_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/sitegroups/{sitegroup_id}",
        path_params={"org_id": org_id, "sitegroup_id": sitegroup_id},
        query_params=None,
        body=body,
    )
