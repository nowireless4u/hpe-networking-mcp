"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs``
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
    name="mist_clone_org",
    description="POST /api/v1/orgs/{org_id}/clone\n\ncloneOrg\n\nCreate an Org by cloning from another one. Org Settings, Templates, Wxlan Tags, Wxlan Tunnels, Wxlan Rules, Org Wlans will be copied. Sites and Site Groups will not be copied, and therefore, the copied template will not be applied to any site/sitegroups.",
    capability=Capability.WRITE,
)
async def mist_clone_org(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/clone",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_org",
    description="POST /api/v1/orgs\n\ncreateOrg\n\nCreate a Mist organization with organization-level defaults such as display name, support-access setting, default alarm template, and admin session lifetime.",
    capability=Capability.WRITE,
)
async def mist_create_org(
    ctx: Context,
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/orgs")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs",
        path_params=None,
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org",
    description="DELETE /api/v1/orgs/{org_id}\n\ndeleteOrg\n\nDelete an organization and its organization-level resources. Use MSP organization assignment endpoints when only changing MSP ownership or association. This action is only allowed when the Organization Inventory is empty.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org",
    description="GET /api/v1/orgs/{org_id}\n\ngetOrg\n\nReturn organization details, including name, MSP ownership, organization group membership, support-access setting, and session settings.",
    capability=Capability.READ,
)
async def mist_get_org(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_org",
    description="PUT /api/v1/orgs/{org_id}\n\nupdateOrg\n\nUpdate organization-level settings such as display name, support-access setting, organization groups, default alarm template, or admin session lifetime.",
    capability=Capability.WRITE,
)
async def mist_update_org(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
