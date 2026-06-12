"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Integration SkyATP``
Operations in this file: 6
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
    name="mist_delete_org_sky_atp_integration",
    description="DELETE /api/v1/orgs/{org_id}/setting/skyatp/setup\n\ndeleteOrgSkyAtpIntegration\n\nRemove the Sky ATP integration configuration from the organization.",
    capability=Capability.WRITE_DELETE,
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
    description="GET /api/v1/orgs/{org_id}/setting/skyatp/setup\n\ngetOrgSkyAtpIntegration\n\nReturn the Sky ATP integration configuration, including linked realm information and generated SecIntel allowlist and blocklist URLs.",
    capability=Capability.READ,
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
    description="POST /api/v1/orgs/{org_id}/setting/skyatp/setup\n\nsetupOrgAtpIntegration\n\nConfigure the Sky ATP integration by linking or creating the Sky ATP realm with the supplied cloud, realm, username, and password. The integration enables Security Intelligence and Advanced Anti-Malware features, with SecIntel configuration for command-and-control, DNS feeds, infected hosts, blocklists, and allowlists.",
    capability=Capability.WRITE,
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
    description="PUT /api/v1/orgs/{org_id}/setting/skyatp/secintel_allowlist\n\nudpateOrgAtpAllowedList\n\nUpdate the Sky ATP SecIntel allowlist with domain and IP address entries for the organization.",
    capability=Capability.WRITE,
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
    description="PUT /api/v1/orgs/{org_id}/setting/skyatp/secintel_blocklist\n\nudpateOrgAtpBlockedList\n\nUpdate the Sky ATP SecIntel blocklist with domain and IP address entries for the organization.",
    capability=Capability.WRITE,
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
    description="PUT /api/v1/orgs/{org_id}/setting/skyatp/setup\n\nudpateOrgAtpIntegration\n\nUpdate Sky ATP SecIntel feed configuration, including the third-party threat feeds enabled for the organization.",
    capability=Capability.WRITE,
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
