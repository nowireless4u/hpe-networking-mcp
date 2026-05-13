"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Security Policies``
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
    name="mist_create_org_sec_policy",
    description="POST /api/v1/orgs/{org_id}/secpolicies\n\ncreateOrgSecPolicy\n\nCreate Org Security Policy",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_sec_policy(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/secpolicies"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/secpolicies",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_sec_policy",
    description="DELETE /api/v1/orgs/{org_id}/secpolicies/{secpolicy_id}\n\ndeleteOrgSecPolicy\n\nDelete Org Security Policy",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_sec_policy(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    secpolicy_id: Annotated[str, Field(description="path parameter 'secpolicy_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/secpolicies/{secpolicy_id}",
        path_params={"org_id": org_id, "secpolicy_id": secpolicy_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_sec_policy",
    description="GET /api/v1/orgs/{org_id}/secpolicies/{secpolicy_id}\n\ngetOrgSecPolicy\n\nGet Org Security Policy",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_sec_policy(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    secpolicy_id: Annotated[str, Field(description="path parameter 'secpolicy_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/secpolicies/{secpolicy_id}",
        path_params={"org_id": org_id, "secpolicy_id": secpolicy_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_sec_policies",
    description="GET /api/v1/orgs/{org_id}/secpolicies\n\nlistOrgSecPolicies\n\nGet List of Org Security Policies",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_sec_policies(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/secpolicies",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_sec_policy",
    description="PUT /api/v1/orgs/{org_id}/secpolicies/{secpolicy_id}\n\nupdateOrgSecPolicy\n\nUpdate Org Security Policy",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_sec_policy(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    secpolicy_id: Annotated[str, Field(description="path parameter 'secpolicy_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/secpolicies/{secpolicy_id}",
        path_params={"org_id": org_id, "secpolicy_id": secpolicy_id},
        query_params=None,
        body=body,
    )
