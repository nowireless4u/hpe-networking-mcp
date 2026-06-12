"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Service Policies``
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
    name="mist_create_org_service_policy",
    description="POST /api/v1/orgs/{org_id}/servicepolicies\n\ncreateOrgServicePolicy\n\nCreate an organization-level service policy that matches tenants\nto services and applies an allow or deny action with optional security inspection\nsettings.\n\n\nOrganization-level service policies can be imported in the gateway templates and gateway policies.",
    capability=Capability.WRITE,
)
async def mist_create_org_service_policy(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/servicepolicies"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/servicepolicies",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_service_policy",
    description="DELETE /api/v1/orgs/{org_id}/servicepolicies/{servicepolicy_id}\n\ndeleteOrgServicePolicy\n\nRemove an organization-level service policy from the available policy set.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_service_policy(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    servicepolicy_id: Annotated[str, Field(description="path parameter 'servicepolicy_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/servicepolicies/{servicepolicy_id}",
        path_params={"org_id": org_id, "servicepolicy_id": servicepolicy_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_service_policy",
    description="GET /api/v1/orgs/{org_id}/servicepolicies/{servicepolicy_id}\n\ngetOrgServicePolicy\n\nReturn an organization-level service policy, including the matched tenants and services, action, local routing, path preference, and inspection settings.",
    capability=Capability.READ,
)
async def mist_get_org_service_policy(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    servicepolicy_id: Annotated[str, Field(description="path parameter 'servicepolicy_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/servicepolicies/{servicepolicy_id}",
        path_params={"org_id": org_id, "servicepolicy_id": servicepolicy_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_service_policies",
    description="GET /api/v1/orgs/{org_id}/servicepolicies\n\nlistOrgServicePolicies\n\nList organization-level service policies. Service policies match tenants to services or service groups and define the allow or deny action plus optional inspection controls.",
    capability=Capability.READ,
)
async def mist_list_org_service_policies(
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
        "/api/v1/orgs/{org_id}/servicepolicies",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_service_policy",
    description="PUT /api/v1/orgs/{org_id}/servicepolicies/{servicepolicy_id}\n\nupdateOrgServicePolicy\n\nUpdate an organization-level service policy, including its tenant and service matches, action, local routing, path preference, or inspection settings.",
    capability=Capability.WRITE,
)
async def mist_update_org_service_policy(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    servicepolicy_id: Annotated[str, Field(description="path parameter 'servicepolicy_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for PUT /api/v1/orgs/{org_id}/servicepolicies/{servicepolicy_id}"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/servicepolicies/{servicepolicy_id}",
        path_params={"org_id": org_id, "servicepolicy_id": servicepolicy_id},
        query_params=None,
        body=body,
    )
