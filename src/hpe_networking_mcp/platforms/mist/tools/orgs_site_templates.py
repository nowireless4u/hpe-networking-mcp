"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Site Templates``
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
    name="mist_create_org_site_template",
    description="POST /api/v1/orgs/{org_id}/sitetemplates\n\ncreateOrgSiteTemplate\n\nCreate a site template with automatic upgrade settings and template\nvariables available to WLAN configuration.\n\nTo assign a Site template to a site, use the [Update Site](/#operations/updateSiteInfo) endpoint and specify the Site template ID in the `sitetemplate_id` field of the request body.'",
    capability=Capability.WRITE,
)
async def mist_create_org_site_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/sitetemplates"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/sitetemplates",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_site_template",
    description="DELETE /api/v1/orgs/{org_id}/sitetemplates/{sitetemplate_id}\n\ndeleteOrgSiteTemplate\n\nRemove a site template from the organization.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_site_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sitetemplate_id: Annotated[str, Field(description="path parameter 'sitetemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/sitetemplates/{sitetemplate_id}",
        path_params={"org_id": org_id, "sitetemplate_id": sitetemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_site_template",
    description="GET /api/v1/orgs/{org_id}/sitetemplates/{sitetemplate_id}\n\ngetOrgSiteTemplate\n\nReturn a site template, including automatic upgrade settings and template variables available to WLAN configuration.",
    capability=Capability.READ,
)
async def mist_get_org_site_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sitetemplate_id: Annotated[str, Field(description="path parameter 'sitetemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/sitetemplates/{sitetemplate_id}",
        path_params={"org_id": org_id, "sitetemplate_id": sitetemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_site_templates",
    description="GET /api/v1/orgs/{org_id}/sitetemplates\n\nlistOrgSiteTemplates\n\nList site templates configured in the organization. Site templates contain automatic upgrade settings and variables available to WLAN configuration.",
    capability=Capability.READ,
)
async def mist_list_org_site_templates(
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
        "/api/v1/orgs/{org_id}/sitetemplates",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_site_template",
    description="PUT /api/v1/orgs/{org_id}/sitetemplates/{sitetemplate_id}\n\nupdateOrgSiteTemplate\n\nUpdate a site template's automatic upgrade settings and template variables available to WLAN configuration.",
    capability=Capability.WRITE,
)
async def mist_update_org_site_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sitetemplate_id: Annotated[str, Field(description="path parameter 'sitetemplate_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/sitetemplates/{sitetemplate_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/sitetemplates/{sitetemplate_id}",
        path_params={"org_id": org_id, "sitetemplate_id": sitetemplate_id},
        query_params=None,
        body=body,
    )
