"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Gateway Templates``
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
    name="mist_create_org_gateway_template",
    description="POST /api/v1/orgs/{org_id}/gatewaytemplates\n\ncreateOrgGatewayTemplate\n\nCreate an organization gateway template with reusable WAN gateway networks, ports, routing, and service-policy configuration.\n\nGateway templates can be applied to multiple sites within the organization to provide consistent gateway configuration across sites.\nTo assign a gateway template to a site, use the [Update Site](/#operations/updateSiteInfo) endpoint and specify the gateway template ID in the `gatewaytemplate_id` field of the request body.",
    capability=Capability.WRITE,
)
async def mist_create_org_gateway_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Gateway Template")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/gatewaytemplates",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_gateway_template",
    description="DELETE /api/v1/orgs/{org_id}/gatewaytemplates/{gatewaytemplate_id}\n\ndeleteOrgGatewayTemplate\n\nDelete an organization gateway template and remove that reusable gateway configuration object from the organization.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_gateway_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    gatewaytemplate_id: Annotated[str, Field(description="path parameter 'gatewaytemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/gatewaytemplates/{gatewaytemplate_id}",
        path_params={"org_id": org_id, "gatewaytemplate_id": gatewaytemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_gateway_template",
    description="GET /api/v1/orgs/{org_id}/gatewaytemplates/{gatewaytemplate_id}\n\ngetOrgGatewayTemplate\n\nRetrieve the configuration stored in a specific organization gateway template.",
    capability=Capability.READ,
)
async def mist_get_org_gateway_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    gatewaytemplate_id: Annotated[str, Field(description="path parameter 'gatewaytemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/gatewaytemplates/{gatewaytemplate_id}",
        path_params={"org_id": org_id, "gatewaytemplate_id": gatewaytemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_gateway_templates",
    description="GET /api/v1/orgs/{org_id}/gatewaytemplates\n\nlistOrgGatewayTemplates\n\nList organization gateway templates, which provide reusable WAN gateway configuration that can be applied to gateways at sites.",
    capability=Capability.READ,
)
async def mist_list_org_gateway_templates(
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
        "/api/v1/orgs/{org_id}/gatewaytemplates",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_gateway_template",
    description="PUT /api/v1/orgs/{org_id}/gatewaytemplates/{gatewaytemplate_id}\n\nupdateOrgGatewayTemplate\n\nUpdate the configuration stored in an organization gateway template.",
    capability=Capability.WRITE,
)
async def mist_update_org_gateway_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    gatewaytemplate_id: Annotated[str, Field(description="path parameter 'gatewaytemplate_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Gateway Template")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/gatewaytemplates/{gatewaytemplate_id}",
        path_params={"org_id": org_id, "gatewaytemplate_id": gatewaytemplate_id},
        query_params=None,
        body=body,
    )
