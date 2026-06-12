"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs API Tokens``
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
    name="mist_create_org_api_token",
    description="POST /api/v1/orgs/{org_id}/apitokens\n\ncreateOrgApiToken\n\nCreate an organization API token with a display name, scoped privileges, and optional source IP restrictions.\nNote that the full token key is only available at creation time.",
    capability=Capability.WRITE,
)
async def mist_create_org_api_token(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/apitokens")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/apitokens",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_api_token",
    description="DELETE /api/v1/orgs/{org_id}/apitokens/{apitoken_id}\n\ndeleteOrgApiToken\n\nDelete an organization API token so it can no longer authenticate API requests.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_api_token(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    apitoken_id: Annotated[str, Field(description="path parameter 'apitoken_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/apitokens/{apitoken_id}",
        path_params={"org_id": org_id, "apitoken_id": apitoken_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_api_token",
    description="GET /api/v1/orgs/{org_id}/apitokens/{apitoken_id}\n\ngetOrgApiToken\n\nReturn metadata for one organization API token. The full token key is only available at creation time and may only be partially shown afterward.",
    capability=Capability.READ,
)
async def mist_get_org_api_token(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    apitoken_id: Annotated[str, Field(description="path parameter 'apitoken_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/apitokens/{apitoken_id}",
        path_params={"org_id": org_id, "apitoken_id": apitoken_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_api_tokens",
    description="GET /api/v1/orgs/{org_id}/apitokens\n\nlistOrgApiTokens\n\nList organization API tokens, including display names, scoped privileges, allowed source IPs, creator, and last-use metadata.",
    capability=Capability.READ,
)
async def mist_list_org_api_tokens(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/apitokens",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_api_token",
    description="PUT /api/v1/orgs/{org_id}/apitokens/{apitoken_id}\n\nupdateOrgApiToken\n\nUpdate an organization API token's display name or scoped privileges. Source IP restrictions are defined when the token is created.",
    capability=Capability.WRITE,
)
async def mist_update_org_api_token(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    apitoken_id: Annotated[str, Field(description="path parameter 'apitoken_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/apitokens/{apitoken_id}",
        path_params={"org_id": org_id, "apitoken_id": apitoken_id},
        query_params=None,
        body=body,
    )
