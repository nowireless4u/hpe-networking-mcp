"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Network Templates``
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
    name="mist_create_org_network_template",
    description="POST /api/v1/orgs/{org_id}/networktemplates\n\ncreateOrgNetworkTemplate\n\nCreate an organization network template with network, port usage, switch management, routing, NAC, and service  configuration at the organization level.\n\nNetwork templates can be applied to multiple sites within the organization to provide consistent network configuration across sites.\nTo assign a network template to a site, use the [Update Site](/#operations/updateSiteInfo) endpoint and specify the network template ID in the `networktemplate_id` field of the request body.",
    capability=Capability.WRITE,
)
async def mist_create_org_network_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/networktemplates",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_network_template",
    description="DELETE /api/v1/orgs/{org_id}/networktemplates/{networktemplate_id}\n\ndeleteOrgNetworkTemplate\n\nDelete an organization network template by template ID so it can no longer be applied to sites or site groups.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_network_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    networktemplate_id: Annotated[str, Field(description="path parameter 'networktemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/networktemplates/{networktemplate_id}",
        path_params={"org_id": org_id, "networktemplate_id": networktemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_network_template",
    description="GET /api/v1/orgs/{org_id}/networktemplates/{networktemplate_id}\n\ngetOrgNetworkTemplate\n\nRetrieve details for a specific organization network template, including network, port usage, switch management, routing, NAC, and service defaults.",
    capability=Capability.READ,
)
async def mist_get_org_network_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    networktemplate_id: Annotated[str, Field(description="path parameter 'networktemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/networktemplates/{networktemplate_id}",
        path_params={"org_id": org_id, "networktemplate_id": networktemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_network_templates",
    description="GET /api/v1/orgs/{org_id}/networktemplates\n\nlistOrgNetworkTemplates\n\nList organization network templates that provide switch network, port, management, routing, NAC, and service configuration at the organization level.",
    capability=Capability.READ,
)
async def mist_list_org_network_templates(
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
        "/api/v1/orgs/{org_id}/networktemplates",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_network_template",
    description="PUT /api/v1/orgs/{org_id}/networktemplates/{networktemplate_id}\n\nupdateOrgNetworkTemplate\n\nUpdate an organization network template, including network, port usage, switch management, routing, NAC, and service defaults.",
    capability=Capability.WRITE,
)
async def mist_update_org_network_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    networktemplate_id: Annotated[str, Field(description="path parameter 'networktemplate_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/networktemplates/{networktemplate_id}",
        path_params={"org_id": org_id, "networktemplate_id": networktemplate_id},
        query_params=None,
        body=body,
    )
