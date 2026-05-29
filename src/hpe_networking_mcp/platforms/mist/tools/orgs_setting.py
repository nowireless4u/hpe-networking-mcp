"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Setting``
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
    name="mist_create_org_wireless_clients_blocklist",
    description="POST /api/v1/orgs/{org_id}/setting/blacklist\n\ncreateOrgWirelessClientsBlocklist\n\nCreate Org Blacklist Client List. \n\nIf there is already a blacklist, this API will replace it with the new one. \n\nMax number of blacklist clients is 1000. \n\nRetrieve the current blacklisted clients from `blacklist_url` under Org:Setting",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="DELETE /api/v1/orgs/{org_id}/setting/blacklist\n\ndeleteOrgWirelessClientsBlocklist\n\nDelete Org Blacklist Station Clients",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    description="GET /api/v1/orgs/{org_id}/setting\n\ngetOrgSettings\n\nGet Org Settings",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/setting/pcap_bucket/setup\n\nsetOrgCustomBucket\n\nProvide Customer Bucket Name\n\nSetting up Custom PCAP Bucket Involves the following:\n* provide the bucket name\n* we’ll attempt to write a file MIST_TOKEN\n* you have to verify the ownership of the bucket by providing the content of the MIST_TOKEN",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="PUT /api/v1/orgs/{org_id}/setting\n\nupdateOrgSettings\n\nUpdate Org Settings",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description='POST /api/v1/orgs/{org_id}/setting/pcap_bucket/verify\n\nverifyOrgCustomBucket\n\nVerify Customer PCAP Bucket\n\n**Note**: If successful, a "VERIFIED" file will be created in the bucket',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
