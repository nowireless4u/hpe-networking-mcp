"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs SSO Roles``
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
    name="mist_create_org_sso_role",
    description="POST /api/v1/orgs/{org_id}/ssoroles\n\ncreateOrgSsoRole\n\nCreate an organization SSO role definition with a display name and the privileges granted when the role is matched during SSO.",
    capability=Capability.WRITE,
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
    description="DELETE /api/v1/orgs/{org_id}/ssoroles/{ssorole_id}\n\ndeleteOrgSsoRole\n\nDelete an organization SSO role definition so it can no longer grant privileges during SSO.",
    capability=Capability.WRITE_DELETE,
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
    description="GET /api/v1/orgs/{org_id}/ssoroles/{ssorole_id}\n\ngetOrgSsoRole\n\nReturn one organization SSO role definition, including its display name and granted privileges.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/ssoroles\n\nlistOrgSsoRoles\n\nList organization SSO role definitions that map identity-provider role assertions to organization, site, or site group privilege scopes.",
    capability=Capability.READ,
)
async def mist_list_org_sso_roles(
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
        "/api/v1/orgs/{org_id}/ssoroles",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_sso_role",
    description="PUT /api/v1/orgs/{org_id}/ssoroles/{ssorole_id}\n\nupdateOrgSsoRole\n\nUpdate an organization SSO role definition, including its display name and granted privileges.",
    capability=Capability.WRITE,
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
