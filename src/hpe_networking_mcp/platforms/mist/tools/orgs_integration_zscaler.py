"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Integration Zscaler``
Operations in this file: 3
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
    name="mist_delete_org_zscaler_integration",
    description="DELETE /api/v1/orgs/{org_id}/setting/zscaler/setup\n\ndeleteOrgZscalerIntegration\n\nRemove the Zscaler integration configuration from the organization.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_zscaler_integration(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/setting/zscaler/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_zscaler_integration",
    description="GET /api/v1/orgs/{org_id}/setting/zscaler/setup\n\ngetOrgZscalerIntegration\n\nReturn the Zscaler integration configuration, including Zscaler Internet Access cloud name, partner key, and partner administrator username.",
    capability=Capability.READ,
)
async def mist_get_org_zscaler_integration(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/setting/zscaler/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_setup_org_zscaler_integration",
    description="POST /api/v1/orgs/{org_id}/setting/zscaler/setup\n\nsetupOrgZscalerIntegration\n\nConfigure the Zscaler integration with the Zscaler Internet Access cloud name, partner key, and partner administrator credentials used by Mist.",
    capability=Capability.WRITE,
)
async def mist_setup_org_zscaler_integration(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/setting/zscaler/setup"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/setting/zscaler/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
