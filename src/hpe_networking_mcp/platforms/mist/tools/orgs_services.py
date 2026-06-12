"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Services``
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
    name="mist_create_org_service",
    description="POST /api/v1/orgs/{org_id}/services\n\ncreateOrgService\n\nCreate an organization service definition with the match criteria\nused by gateway and SSR policies, such as applications, URLs, hostnames,\nsubnets, or custom protocol and port rules.\n\n\nServices can be user in the service policies to allow or deny traffic matching the service or to apply specific inspection settings or steering rules.",
    capability=Capability.WRITE,
)
async def mist_create_org_service(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/services")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/services",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_service",
    description="DELETE /api/v1/orgs/{org_id}/services/{service_id}\n\ndeleteOrgService\n\nRemove an organization service definition from the available service catalog.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_service(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    service_id: Annotated[str, Field(description="path parameter 'service_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/services/{service_id}",
        path_params={"org_id": org_id, "service_id": service_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_service",
    description="GET /api/v1/orgs/{org_id}/services/{service_id}\n\ngetOrgService\n\nReturn an organization service definition, including its matching mode, match values, traffic classification, and optional SSR path-selection thresholds.",
    capability=Capability.READ,
)
async def mist_get_org_service(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    service_id: Annotated[str, Field(description="path parameter 'service_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/services/{service_id}",
        path_params={"org_id": org_id, "service_id": service_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_services",
    description="GET /api/v1/orgs/{org_id}/services\n\nlistOrgServices\n\nList organization service definitions. Services describe applications, application categories, URLs, hostnames, subnets, or custom protocol and port match criteria used by gateway and SSR policies.",
    capability=Capability.READ,
)
async def mist_list_org_services(
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
        "/api/v1/orgs/{org_id}/services",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_service",
    description="PUT /api/v1/orgs/{org_id}/services/{service_id}\n\nupdateOrgService\n\nUpdate an organization service definition, including its matching mode, match values, traffic classification, or optional SSR path-selection thresholds.",
    capability=Capability.WRITE,
)
async def mist_update_org_service(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    service_id: Annotated[str, Field(description="path parameter 'service_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/services/{service_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/services/{service_id}",
        path_params={"org_id": org_id, "service_id": service_id},
        query_params=None,
        body=body,
    )
