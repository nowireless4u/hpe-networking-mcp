"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Integration JSE``
Operations in this file: 4
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
    name="mist_delete_org_jse_integration",
    description="DELETE /api/v1/orgs/{org_id}/setting/jse/setup\n\ndeleteOrgJseIntegration\n\nRemove the JSE integration configuration from the organization.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_jse_integration(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/setting/jse/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_jse_info",
    description="GET /api/v1/orgs/{org_id}/setting/jse/info\n\ngetOrgJseInfo\n\nReturn the JSE organizations associated with the configured account. Use the returned organization names when selecting JSE provider options for secure edge tunnels.",
    capability=Capability.READ,
)
async def mist_get_org_jse_info(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/setting/jse/info",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_jse_integration",
    description="GET /api/v1/orgs/{org_id}/setting/jse/setup\n\ngetOrgJseIntegration\n\nReturn the JSE integration configuration, including the cloud hostname, integration username, and associated JSE organization names.",
    capability=Capability.READ,
)
async def mist_get_org_jse_integration(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/setting/jse/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_setup_org_jse_integration",
    description="POST /api/v1/orgs/{org_id}/setting/jse/setup\n\nsetupOrgJseIntegration\n\nConfigure the JSE integration with the JSE cloud hostname and integration-user credentials. In JSE, use a custom role with read access to `service_location` and read-write access to site and IPsec profile APIs, then create and activate the integration user and service locations.",
    capability=Capability.WRITE,
)
async def mist_setup_org_jse_integration(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/setting/jse/setup"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/setting/jse/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
