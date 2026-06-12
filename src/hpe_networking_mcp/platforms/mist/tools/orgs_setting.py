"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Setting``
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
    name="mist_create_org_wireless_clients_blocklist",
    description="POST /api/v1/orgs/{org_id}/setting/blacklist\n\ncreateOrgWirelessClientsBlocklist\n\nReplace the organization wireless client blocklist with the supplied client MAC addresses. The list can contain up to 1000 MAC addresses; retrieve the current list from the `blacklist_url` field in organization settings.",
    capability=Capability.WRITE,
)
async def mist_create_org_wireless_clients_blocklist(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/setting/blacklist",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_wireless_clients_blocklist",
    description="DELETE /api/v1/orgs/{org_id}/setting/blacklist\n\ndeleteOrgWirelessClientsBlocklist\n\nClear the organization wireless client blocklist by removing all blocked client MAC addresses.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_wireless_clients_blocklist(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/setting/blacklist",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_settings",
    description="GET /api/v1/orgs/{org_id}/setting\n\ngetOrgSettings\n\nReturn organization-wide settings, including feature flags, automatic device assignment rules, management connectivity, packet capture, security controls, and integration configuration.",
    capability=Capability.READ,
)
async def mist_get_org_settings(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/setting",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_set_org_custom_bucket",
    description="POST /api/v1/orgs/{org_id}/setting/pcap_bucket/setup\n\nsetOrgCustomBucket\n\nStart custom packet capture bucket setup by saving the bucket name and having Mist write a `MIST_TOKEN` file to the bucket. Complete ownership verification with the verify endpoint by submitting the token contents.",
    capability=Capability.WRITE,
)
async def mist_set_org_custom_bucket(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/setting/pcap_bucket/setup",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_org_settings",
    description="PUT /api/v1/orgs/{org_id}/setting\n\nupdateOrgSettings\n\nUpdate organization-wide settings such as automatic device assignment rules, management connectivity, packet capture, password policy, security controls, tags, and integration options.",
    capability=Capability.WRITE,
)
async def mist_update_org_settings(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/setting",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_verify_org_custom_bucket",
    description="POST /api/v1/orgs/{org_id}/setting/pcap_bucket/verify\n\nverifyOrgCustomBucket\n\nVerify ownership of a custom packet capture bucket by submitting the token read from the `MIST_TOKEN` file. If verification succeeds, Mist creates a `VERIFIED` file in the bucket.",
    capability=Capability.WRITE,
)
async def mist_verify_org_custom_bucket(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/setting/pcap_bucket/verify",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
