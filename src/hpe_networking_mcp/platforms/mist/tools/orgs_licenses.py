"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Licenses``
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
    name="mist_claim_org_license",
    description="POST /api/v1/orgs/{org_id}/claim\n\nclaimOrgLicense\n\nClaim organization licenses or activation codes, optionally running the claim asynchronously and specifying the claim scope.",
    capability=Capability.WRITE,
)
async def mist_claim_org_license(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/claim",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_get_org_license_async_claim_status",
    description="GET /api/v1/orgs/{org_id}/claim/status\n\nGetOrgLicenseAsyncClaimStatus\n\nReturn processing status for an asynchronous organization license claim, optionally including per-device license details.",
    capability=Capability.READ,
)
async def mist_get_org_license_async_claim_status(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    detail: Annotated[
        bool | None, Field(description="Whether to include license details in the claim status response")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/claim/status",
        path_params={"org_id": org_id},
        query_params={"detail": detail},
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_licenses_by_site",
    description="GET /api/v1/orgs/{org_id}/licenses/usages\n\ngetOrgLicensesBySite\n\nGet Licenses Usage by Sites\nThis shows license usage (i.e. needed) based on the features enabled for the site.",
    capability=Capability.READ,
)
async def mist_get_org_licenses_by_site(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/licenses/usages",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_licenses_summary",
    description="GET /api/v1/orgs/{org_id}/licenses\n\ngetOrgLicensesSummary\n\nReturn the organization license entitlement, subscription, amendment, consumption, and available-license summary.",
    capability=Capability.READ,
)
async def mist_get_org_licenses_summary(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/licenses",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_move_or_delete_org_license_to_another_org",
    description="PUT /api/v1/orgs/{org_id}/licenses\n\nmoveOrDeleteOrgLicenseToAnotherOrg\n\nMove, Undo Move or Delete Org License to Another Org\nIf the admin has admin privilege against the `org_id` and `dst_org_id`, he can move some of the licenses to another Org. Given that: \n1. the specified license is currently active \n2. there’s enough licenses left in the specified license (by subscription_id) \n3. there will still be enough entitled licenses for the type of license after the amendment",
    capability=Capability.WRITE,
)
async def mist_move_or_delete_org_license_to_another_org(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/licenses",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
