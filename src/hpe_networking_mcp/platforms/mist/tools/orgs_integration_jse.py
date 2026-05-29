"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Integration JSE``
Operations in this file: 4
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
    name="mist_delete_org_jse_integration",
    description="DELETE /api/v1/orgs/{org_id}/setting/jse/setup\n\ndeleteOrgJseIntegration\n\nDelete JSE Integration",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    description="GET /api/v1/orgs/{org_id}/setting/jse/info\n\ngetOrgJseInfo\n\nRetrieves the list of JSE orgs associated with the account.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/setting/jse/setup\n\ngetOrgJseIntegration\n\nGet Org JSE Integration",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/setting/jse/setup\n\nsetupOrgJseIntegration\n\nIn JSE UI: \n1. Create custom role with Read access to service_location and RW access to site and IPSec profile APIs. \n2. Create a user with the above custom role. - email: john@abc.com \n3. Activate the user in the JSE account. \n4. Create the service locations on the JSE account.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
