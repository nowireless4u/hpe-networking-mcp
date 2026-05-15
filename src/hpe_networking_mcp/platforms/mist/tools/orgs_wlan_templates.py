"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs WLAN Templates``
Operations in this file: 6
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
    name="mist_clone_org_template",
    description="POST /api/v1/orgs/{org_id}/templates/{template_id}/clone\n\ncloneOrgTemplate\n\nClone Org Template",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_clone_org_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    template_id: Annotated[str, Field(description="path parameter 'template_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/templates/{template_id}/clone",
        path_params={"org_id": org_id, "template_id": template_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_org_template",
    description="POST /api/v1/orgs/{org_id}/templates\n\ncreateOrgTemplate\n\nCreate Org Template",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/templates",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_template",
    description="DELETE /api/v1/orgs/{org_id}/templates/{template_id}\n\ndeleteOrgTemplate\n\nDelete Org Template",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    template_id: Annotated[str, Field(description="path parameter 'template_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/templates/{template_id}",
        path_params={"org_id": org_id, "template_id": template_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_template",
    description="GET /api/v1/orgs/{org_id}/templates/{template_id}\n\ngetOrgTemplate\n\nGet Org Template Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    template_id: Annotated[str, Field(description="path parameter 'template_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/templates/{template_id}",
        path_params={"org_id": org_id, "template_id": template_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_templates",
    description="GET /api/v1/orgs/{org_id}/templates\n\nlistOrgTemplates\n\nGet List of Org WLAN Templates",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_templates(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/templates",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_template",
    description="PUT /api/v1/orgs/{org_id}/templates/{template_id}\n\nupdateOrgTemplate\n\nUpdate Org Template",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    template_id: Annotated[str, Field(description="path parameter 'template_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/templates/{template_id}",
        path_params={"org_id": org_id, "template_id": template_id},
        query_params=None,
        body=body,
    )
