"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs SSO Roles``
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
    name="mist_create_org_sso_role",
    description="POST /api/v1/orgs/{org_id}/ssoroles\n\ncreateOrgSsoRole\n\nCreate Org SSO Role",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_sso_role(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/ssoroles",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_sso_role",
    description="DELETE /api/v1/orgs/{org_id}/ssoroles/{ssorole_id}\n\ndeleteOrgSsoRole\n\nDelete Org SSO Role",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_sso_role(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ssorole_id: Annotated[str, Field(description="path parameter 'ssorole_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/ssoroles/{ssorole_id}",
        path_params={"org_id": org_id, "ssorole_id": ssorole_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_sso_role",
    description="GET /api/v1/orgs/{org_id}/ssoroles/{ssorole_id}\n\ngetOrgSsoRole\n\nGet Org SSO Role Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_sso_role(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ssorole_id: Annotated[str, Field(description="path parameter 'ssorole_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ssoroles/{ssorole_id}",
        path_params={"org_id": org_id, "ssorole_id": ssorole_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_sso_roles",
    description="GET /api/v1/orgs/{org_id}/ssoroles\n\nlistOrgSsoRoles\n\nGet List of Org SSO Roles",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_sso_roles(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ssoroles",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_sso_role",
    description="PUT /api/v1/orgs/{org_id}/ssoroles/{ssorole_id}\n\nupdateOrgSsoRole\n\nUpdate Org SSO Role",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_sso_role(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ssorole_id: Annotated[str, Field(description="path parameter 'ssorole_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/ssoroles/{ssorole_id}",
        path_params={"org_id": org_id, "ssorole_id": ssorole_id},
        query_params=None,
        body=body,
    )
