"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Integration Cradlepoint``
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
    name="mist_delete_org_cradlepoint_connection",
    description="DELETE /api/v1/orgs/{org_id}/setting/cradlepoint/setup\n\ndeleteOrgCradlepointConnection\n\nThis deletes the Cradlepoint integration in Mist",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    description="POST /api/v1/orgs/{org_id}/setting/cradlepoint/setup\n\nsetupOrgCradlepointConnectionToMist\n\nThis sets up cradlepoint webhooks to send events to Mist",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/setting/cradlepoint/sync\n\nsyncOrgCradlepointRouters\n\nThis syncs cradlepoint devices with Mist. We’ll also attempt to use the LLDP data from cradlepoint to identify the linkage against Mist Site / Device",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/setting/cradlepoint/setup\n\ntestOrgCradlepointConnection\n\nThis tests the Cradlepoint integration in Mist",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="PUT /api/v1/orgs/{org_id}/setting/cradlepoint/setup\n\nupdateOrgCradlepointConnectionToMist\n\nThis updates the Cradlepoint integration settings in Mist",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
