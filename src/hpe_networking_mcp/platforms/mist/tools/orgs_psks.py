"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Psks``
Operations in this file: 9
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
    name="mist_create_org_psk",
    description='POST /api/v1/orgs/{org_id}/psks\n\ncreateOrgPsk\n\nCreate an organization personal PSK for WLAN access, including SSID, passphrase, usage mode, optional client MAC binding, role, VLAN, and expiration settings.\n\n\nWhen `usage`==`macs`, corresponding "macs" field will hold a list consisting of client MAC addresses (["xx:xx:xx:xx:xx",...]) or mac patterns(["xx:xx:*","xx*",...]) or both (["xx:xx:xx:xx:xx:xx", "xx:*", ...]). This list is capped at 5000',
    capability=Capability.WRITE,
)
async def mist_create_org_psk(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    upsert: Annotated[
        bool | None, Field(description="If a key exists with the same `name`, replace it with the new one")
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/psks",
        path_params={"org_id": org_id},
        query_params={"upsert": upsert},
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_psk",
    description="DELETE /api/v1/orgs/{org_id}/psks/{psk_id}\n\ndeleteOrgPsk\n\nDelete an organization personal PSK by PSK ID so clients can no longer authenticate with that key.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_psk(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    psk_id: Annotated[str, Field(description="PSK ID")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/psks/{psk_id}",
        path_params={"org_id": org_id, "psk_id": psk_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_org_psk_list",
    description="POST /api/v1/orgs/{org_id}/psks/delete\n\ndeleteOrgPskList\n\nDelete one or more organization PSKs by ID.\n\nThe request accepts a single PSK ID string or a list of PSK ID strings.\n**Warning**: If no PSK IDs are provided in the request, all organization PSKs will be deleted and clients will no longer be able to authenticate to any SSID with a PSK.",
    capability=Capability.WRITE,
)
async def mist_delete_org_psk_list(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/psks/delete"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/psks/delete",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_psk_old_passphrase",
    description="POST /api/v1/orgs/{org_id}/psks/{psk_id}/delete_old_passphrase\n\ndeleteOrgPskOldPassphrase\n\nRemove the stored `old_passphrase` from a PSK after rotation. \nIf successful, the response returns the PSK with `old_passphrase` removed.",
    capability=Capability.WRITE,
)
async def mist_delete_org_psk_old_passphrase(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    psk_id: Annotated[str, Field(description="PSK ID")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/psks/{psk_id}/delete_old_passphrase",
        path_params={"org_id": org_id, "psk_id": psk_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_psk",
    description="GET /api/v1/orgs/{org_id}/psks/{psk_id}\n\ngetOrgPsk\n\nRetrieve details for an organization personal PSK, including SSID, usage mode, MAC binding, role, VLAN, expiration, and notification settings.",
    capability=Capability.READ,
)
async def mist_get_org_psk(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    psk_id: Annotated[str, Field(description="PSK ID")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/psks/{psk_id}",
        path_params={"org_id": org_id, "psk_id": psk_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_import_org_psks",
    description="POST /api/v1/orgs/{org_id}/psks/import\n\nimportOrgPsks\n\nImport organization PSKs from a CSV file or JSON payload.\n\n##\xa0CSV File Format\n```\nPSK Import CSV File Format:\nname,ssid,passphrase,usage,vlan_id,mac,max_usage,role,expire_time,notify_expiry,expiry_notification_time,notify_on_create_or_edit,email\nCommon,warehouse,foryoureyesonly,single,35,a31425f31278,0,student,1618594236\nJustin,reception,visible,multi,1002,200,teacher,1618594236\nCommon2,ssid,1245678-xx,single,35,a31425f31278,0,student,1618594236,true,7,true,admin@test.com\n```",
    capability=Capability.WRITE,
)
async def mist_import_org_psks(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/psks/import"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/psks/import",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_list_org_psks",
    description="GET /api/v1/orgs/{org_id}/psks\n\nlistOrgPsks\n\nList organization personal PSKs for WLAN access, optionally filtering by name, SSID, or role.",
    capability=Capability.READ,
)
async def mist_list_org_psks(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    name: Annotated[
        str | None, Field(description="Filter results by name. Accepts multiple comma-separated values.")
    ] = None,
    ssid: Annotated[
        str | None, Field(description="Filter results by SSID. Accepts multiple comma-separated values.")
    ] = None,
    role: Annotated[
        str | None, Field(description="Filter PSK results by role. Accepts multiple comma-separated values.")
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/psks",
        path_params={"org_id": org_id},
        query_params={"name": name, "ssid": ssid, "role": role, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_multiple_psks",
    description="PUT /api/v1/orgs/{org_id}/psks\n\nupdateOrgMultiplePsks\n\nUpdate multiple organization personal PSKs in one request, including passphrase, usage mode, role, VLAN, expiration, and notification settings.",
    capability=Capability.WRITE,
)
async def mist_update_org_multiple_psks(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/psks")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/psks",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_org_psk",
    description="PUT /api/v1/orgs/{org_id}/psks/{psk_id}\n\nupdateOrgPsk\n\nUpdate an organization personal PSK, including passphrase, usage mode, MAC binding, role, VLAN, expiration, and notification settings.",
    capability=Capability.WRITE,
)
async def mist_update_org_psk(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    psk_id: Annotated[str, Field(description="PSK ID")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/psks/{psk_id}",
        path_params={"org_id": org_id, "psk_id": psk_id},
        query_params=None,
        body=body,
    )
