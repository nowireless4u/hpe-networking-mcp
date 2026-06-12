"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs SSO Roles``
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
    name="mist_create_msp_sso_role",
    description="POST /api/v1/msps/{msp_id}/ssoroles\n\ncreateMspSsoRole\n\nCreate an MSP SSO role definition with a display name and the MSP privileges granted when the role is matched during SSO.",
    capability=Capability.WRITE,
)
async def mist_create_msp_sso_role(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/msps/{msp_id}/ssoroles",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_msp_sso_role",
    description="DELETE /api/v1/msps/{msp_id}/ssoroles/{ssorole_id}\n\ndeleteMspSsoRole\n\nDelete an MSP SSO role definition so it can no longer grant MSP privileges during SSO.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_msp_sso_role(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    ssorole_id: Annotated[str, Field(description="path parameter 'ssorole_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/msps/{msp_id}/ssoroles/{ssorole_id}",
        path_params={"msp_id": msp_id, "ssorole_id": ssorole_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_msp_sso_roles",
    description="GET /api/v1/msps/{msp_id}/ssoroles\n\nlistMspSsoRoles\n\nList MSP SSO role definitions that map identity-provider role assertions to MSP privilege scopes.",
    capability=Capability.READ,
)
async def mist_list_msp_sso_roles(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/ssoroles",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_msp_sso_role",
    description="PUT /api/v1/msps/{msp_id}/ssoroles/{ssorole_id}\n\nupdateMspSsoRole\n\nUpdate an MSP SSO role definition, including its display name and granted MSP privileges.",
    capability=Capability.WRITE,
)
async def mist_update_msp_sso_role(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    ssorole_id: Annotated[str, Field(description="path parameter 'ssorole_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/msps/{msp_id}/ssoroles/{ssorole_id}",
        path_params={"msp_id": msp_id, "ssorole_id": ssorole_id},
        query_params=None,
        body=body,
    )
