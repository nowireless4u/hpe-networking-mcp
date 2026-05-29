"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs``
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
    name="mist_clone_org",
    description="POST /api/v1/orgs/{org_id}/clone\n\ncloneOrg\n\nCreate an Org by cloning from another one. Org Settings, Templates, Wxlan Tags, Wxlan Tunnels, Wxlan Rules, Org Wlans will be copied. Sites and Site Groups will not be copied, and therefore, the copied template will not be applied to any site/sitegroups.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description='POST /api/v1/orgs\n\ncreateOrg\n\nOrg admin can invite people to manage the org. Furthermore, he can dictate the level of security those accounts are. The check is enforced when the invited admin tries to "accept" the invitation and every time the admin tries to login',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="DELETE /api/v1/orgs/{org_id}\n\ndeleteOrg\n\nDelete Org",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    description="GET /api/v1/orgs/{org_id}\n\ngetOrg\n\nGet Organization information",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="PUT /api/v1/orgs/{org_id}\n\nupdateOrg\n\nUpdate Org",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
