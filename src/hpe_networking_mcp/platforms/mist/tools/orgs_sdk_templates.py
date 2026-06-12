"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs SDK Templates``
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
    name="mist_create_sdk_template",
    description="POST /api/v1/orgs/{org_id}/sdktemplates\n\ncreateSdkTemplate\n\nCreate an SDK template that defines visual customization for the mobile SDK experience, including branding images, colors, header text, and welcome messages.",
    capability=Capability.WRITE,
)
async def mist_create_sdk_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/sdktemplates",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_sdk_template",
    description="DELETE /api/v1/orgs/{org_id}/sdktemplates/{sdktemplate_id}\n\ndeleteSdkTemplate\n\nDelete an SDK visual customization template from the organization.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_sdk_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sdktemplate_id: Annotated[str, Field(description="path parameter 'sdktemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/sdktemplates/{sdktemplate_id}",
        path_params={"org_id": org_id, "sdktemplate_id": sdktemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_sdk_template",
    description="GET /api/v1/orgs/{org_id}/sdktemplates/{sdktemplate_id}\n\ngetSdkTemplate\n\nReturn the visual customization settings for an SDK template, including branding text, image URLs, colors, default state, and site scope.",
    capability=Capability.READ,
)
async def mist_get_sdk_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sdktemplate_id: Annotated[str, Field(description="path parameter 'sdktemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/sdktemplates/{sdktemplate_id}",
        path_params={"org_id": org_id, "sdktemplate_id": sdktemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_sdk_templates",
    description="GET /api/v1/orgs/{org_id}/sdktemplates\n\nlistSdkTemplates\n\nList SDK templates configured for the organization. SDK templates define visual customization for the mobile SDK experience, including branding images, colors, header text, and welcome messages.",
    capability=Capability.READ,
)
async def mist_list_sdk_templates(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/sdktemplates",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_sdk_template",
    description="PUT /api/v1/orgs/{org_id}/sdktemplates/{sdktemplate_id}\n\nupdateSdkTemplate\n\nUpdate an SDK template's visual customization settings, such as branding images, colors, header text, welcome message, default state, or site association.",
    capability=Capability.WRITE,
)
async def mist_update_sdk_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sdktemplate_id: Annotated[str, Field(description="path parameter 'sdktemplate_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/sdktemplates/{sdktemplate_id}",
        path_params={"org_id": org_id, "sdktemplate_id": sdktemplate_id},
        query_params=None,
        body=body,
    )
