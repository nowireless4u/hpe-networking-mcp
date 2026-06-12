"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Sitegroups``
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
    name="mist_create_org_site_group",
    description="POST /api/v1/orgs/{org_id}/sitegroups\n\ncreateOrgSiteGroup\n\nCreate a site group in the organization with a display name and optional site membership.",
    capability=Capability.WRITE,
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
    description="DELETE /api/v1/orgs/{org_id}/sitegroups/{sitegroup_id}\n\ndeleteOrgSiteGroup\n\nRemove a site group from the organization.",
    capability=Capability.WRITE_DELETE,
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
    description="GET /api/v1/orgs/{org_id}/sitegroups/{sitegroup_id}\n\ngetOrgSiteGroup\n\nReturn a site group, including its display name and the site IDs included in the group.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/sitegroups\n\nlistOrgSiteGroups\n\nList site groups configured in the organization. A site group collects site IDs so sites can be managed or referenced as a group.",
    capability=Capability.READ,
)
async def mist_list_org_site_groups(
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
        "/api/v1/orgs/{org_id}/sitegroups",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_site_group",
    description="PUT /api/v1/orgs/{org_id}/sitegroups/{sitegroup_id}\n\nupdateOrgSiteGroup\n\nUpdate the display name used to identify a site group in the organization.",
    capability=Capability.WRITE,
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
