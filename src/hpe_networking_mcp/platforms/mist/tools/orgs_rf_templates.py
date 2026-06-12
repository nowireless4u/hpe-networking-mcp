"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs RF Templates``
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
    name="mist_create_org_rf_template",
    description="POST /api/v1/orgs/{org_id}/rftemplates\n\ncreateOrgRfTemplate\n\nCreate an organization RF template with 2.4, 5, and 6 GHz radio\nsettings, country code, scanning behavior, antenna gain, and model-specific\noverrides.\n\nTo assign a RF template to a site, use the [Update Site](/#operations/updateSiteInfo) endpoint and specify the RF template ID in the `rftemplate_id` field of the request body.",
    capability=Capability.WRITE,
)
async def mist_create_org_rf_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/rftemplates",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_rf_template",
    description="DELETE /api/v1/orgs/{org_id}/rftemplates/{rftemplate_id}\n\ndeleteOrgRfTemplate\n\nDelete an organization RF template by template ID so it can no longer be applied to sites.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_rf_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    rftemplate_id: Annotated[str, Field(description="path parameter 'rftemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/rftemplates/{rftemplate_id}",
        path_params={"org_id": org_id, "rftemplate_id": rftemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_rf_template",
    description="GET /api/v1/orgs/{org_id}/rftemplates/{rftemplate_id}\n\ngetOrgRfTemplate\n\nRetrieve details for a specific organization RF template, including radio settings, country code, scanning behavior, antenna gain, and model-specific overrides.",
    capability=Capability.READ,
)
async def mist_get_org_rf_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    rftemplate_id: Annotated[str, Field(description="path parameter 'rftemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/rftemplates/{rftemplate_id}",
        path_params={"org_id": org_id, "rftemplate_id": rftemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_rf_templates",
    description="GET /api/v1/orgs/{org_id}/rftemplates\n\nlistOrgRfTemplates\n\nList organization RF templates used by RRM to apply radio settings across sites.",
    capability=Capability.READ,
)
async def mist_list_org_rf_templates(
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
        "/api/v1/orgs/{org_id}/rftemplates",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_rf_template",
    description="PUT /api/v1/orgs/{org_id}/rftemplates/{rftemplate_id}\n\nupdateOrgRfTemplate\n\nUpdate an organization RF template, including radio settings, country code, scanning behavior, antenna gain, and model-specific overrides.",
    capability=Capability.WRITE,
)
async def mist_update_org_rf_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    rftemplate_id: Annotated[str, Field(description="path parameter 'rftemplate_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/rftemplates/{rftemplate_id}",
        path_params={"org_id": org_id, "rftemplate_id": rftemplate_id},
        query_params=None,
        body=body,
    )
