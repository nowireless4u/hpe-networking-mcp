"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Integration SkyATP``
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
    name="mist_delete_org_sky_atp_integration",
    description="DELETE /api/v1/orgs/{org_id}/setting/skyatp/setup\n\ndeleteOrgSkyAtpIntegration\n\nDelete SkyATP Integration",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_sky_atp_integration(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/setting/skyatp/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_sky_atp_integration",
    description="GET /api/v1/orgs/{org_id}/setting/skyatp/setup\n\ngetOrgSkyAtpIntegration\n\nGet Org SkyATP Integration",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_sky_atp_integration(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/setting/skyatp/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_setup_org_atp_integration",
    description="POST /api/v1/orgs/{org_id}/setting/skyatp/setup\n\nsetupOrgAtpIntegration\n\n1. Login to the Sky ATP realm through the Mist UI by providing the realm, username and password.\n2. Sky ATP API is invoked which creates the realm using above details.\n3. Sky ATP by default will provide functionality for Security-Intelligence and Advanced Anti Malware.\n4. Security Intelligence will provide configuration for CC, DNS Feeds, Infected Host, Blocklists and Allowlists.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_setup_org_atp_integration(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/setting/skyatp/setup"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/setting/skyatp/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_udpate_org_atp_allowed_list",
    description="PUT /api/v1/orgs/{org_id}/setting/skyatp/secintel_allowlist\n\nudpateOrgAtpAllowedList\n\nUpdate Sky ATP Allowed List",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_udpate_org_atp_allowed_list(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/setting/skyatp/secintel_allowlist"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/setting/skyatp/secintel_allowlist",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_udpate_org_atp_blocked_list",
    description="PUT /api/v1/orgs/{org_id}/setting/skyatp/secintel_blocklist\n\nudpateOrgAtpBlockedList\n\nUpdate Sky ATP Blocked List",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_udpate_org_atp_blocked_list(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/setting/skyatp/secintel_blocklist"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/setting/skyatp/secintel_blocklist",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_udpate_org_atp_integration",
    description="PUT /api/v1/orgs/{org_id}/setting/skyatp/setup\n\nudpateOrgAtpIntegration\n\nUpdate Sky ATP config",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_udpate_org_atp_integration(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/setting/skyatp/setup"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/setting/skyatp/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
