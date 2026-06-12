"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Integration Cradlepoint``
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
    name="mist_delete_org_cradlepoint_connection",
    description="DELETE /api/v1/orgs/{org_id}/setting/cradlepoint/setup\n\ndeleteOrgCradlepointConnection\n\nRemove the Cradlepoint integration configuration from the organization.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_cradlepoint_connection(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/setting/cradlepoint/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_setup_org_cradlepoint_connection_to_mist",
    description="POST /api/v1/orgs/{org_id}/setting/cradlepoint/setup\n\nsetupOrgCradlepointConnectionToMist\n\nConfigure the Cradlepoint integration by storing Cradlepoint API and ECM credentials and setting up Cradlepoint webhooks to send events to Mist.",
    capability=Capability.WRITE,
)
async def mist_setup_org_cradlepoint_connection_to_mist(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/setting/cradlepoint/setup"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/setting/cradlepoint/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_sync_org_cradlepoint_routers",
    description="POST /api/v1/orgs/{org_id}/setting/cradlepoint/sync\n\nsyncOrgCradlepointRouters\n\nTrigger a Cradlepoint device synchronization with Mist. When LLDP linking is enabled, Mist also uses Cradlepoint LLDP data to associate routers with Mist sites and devices.",
    capability=Capability.WRITE,
)
async def mist_sync_org_cradlepoint_routers(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/setting/cradlepoint/sync",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_test_org_cradlepoint_connection",
    description="GET /api/v1/orgs/{org_id}/setting/cradlepoint/setup\n\ntestOrgCradlepointConnection\n\nTest the current Cradlepoint integration configuration and return whether the most recent integration status is active or inactive.",
    capability=Capability.READ,
)
async def mist_test_org_cradlepoint_connection(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/setting/cradlepoint/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_cradlepoint_connection_to_mist",
    description="PUT /api/v1/orgs/{org_id}/setting/cradlepoint/setup\n\nupdateOrgCradlepointConnectionToMist\n\nUpdate the stored Cradlepoint API and ECM credentials and the LLDP-based device linking option used by Mist.",
    capability=Capability.WRITE,
)
async def mist_update_org_cradlepoint_connection_to_mist(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/setting/cradlepoint/setup"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/setting/cradlepoint/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
