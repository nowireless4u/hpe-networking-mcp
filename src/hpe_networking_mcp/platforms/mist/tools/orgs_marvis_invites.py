"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Marvis Invites``
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
    name="mist_create_org_marvis_client_invite",
    description="POST /api/v1/orgs/{org_id}/marvisinvites\n\ncreateOrgMarvisClientInvite\n\nCreate a Marvis Client onboarding invite profile for the organization, defining the enabled telemetry, location, and synthetic-test capabilities.",
    capability=Capability.WRITE,
)
async def mist_create_org_marvis_client_invite(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/marvisinvites"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/marvisinvites",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_marvis_client_invite",
    description="DELETE /api/v1/orgs/{org_id}/marvisinvites/{marvisinvite_id}\n\ndeleteOrgMarvisClientInvite\n\nDelete a Marvis Client onboarding invite profile by ID.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_marvis_client_invite(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    marvisinvite_id: Annotated[str, Field(description="path parameter 'marvisinvite_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/marvisinvites/{marvisinvite_id}",
        path_params={"org_id": org_id, "marvisinvite_id": marvisinvite_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_marvis_client_invite",
    description="GET /api/v1/orgs/{org_id}/marvisinvites/{marvisinvite_id}\n\ngetOrgMarvisClientInvite\n\nRetrieve a Marvis Client onboarding invite profile, including enrollment URL and enabled client capabilities.",
    capability=Capability.READ,
)
async def mist_get_org_marvis_client_invite(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    marvisinvite_id: Annotated[str, Field(description="path parameter 'marvisinvite_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/marvisinvites/{marvisinvite_id}",
        path_params={"org_id": org_id, "marvisinvite_id": marvisinvite_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_marvis_client_invites",
    description="GET /api/v1/orgs/{org_id}/marvisinvites\n\nlistOrgMarvisClientInvites\n\nList Marvis Client onboarding invite profiles for the organization, including enrollment URLs and enabled telemetry, location, and synthetic-test capabilities.",
    capability=Capability.READ,
)
async def mist_list_org_marvis_client_invites(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/marvisinvites",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_marvis_client_invite",
    description="PUT /api/v1/orgs/{org_id}/marvisinvites/{marvisinvite_id}\n\nupdateOrgMarvisClientInvite\n\nUpdate a Marvis Client onboarding invite profile, including enabled telemetry, location, and synthetic-test capabilities.",
    capability=Capability.WRITE,
)
async def mist_update_org_marvis_client_invite(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    marvisinvite_id: Annotated[str, Field(description="path parameter 'marvisinvite_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/marvisinvites/{marvisinvite_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/marvisinvites/{marvisinvite_id}",
        path_params={"org_id": org_id, "marvisinvite_id": marvisinvite_id},
        query_params=None,
        body=body,
    )
