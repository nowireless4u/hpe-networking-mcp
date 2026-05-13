"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Psks``
Operations in this file: 9
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
    name="mist_create_org_psk",
    description='POST /api/v1/orgs/{org_id}/psks\n\ncreateOrgPsk\n\nCreate Org PSK\n\n\nWhen `usage`==`macs`, corresponding "macs" field will hold a list consisting of client mac addresses (["xx:xx:xx:xx:xx",...]) or mac patterns(["xx:xx:*","xx*",...]) or both (["xx:xx:xx:xx:xx:xx", "xx:*", ...]). This list is capped at 5000',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="DELETE /api/v1/orgs/{org_id}/psks/{psk_id}\n\ndeleteOrgPsk\n\nDelete Org PSK",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    description="POST /api/v1/orgs/{org_id}/psks/delete\n\ndeleteOrgPskList\n\nDelete Org PSK List\n\nDelete list of psks on the org. This API accepts single string or list of strings",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/psks/{psk_id}/delete_old_passphrase\n\ndeleteOrgPskOldPassphrase\n\nDelete `old_passphrase` from PSK. \nIf successful, response is same as GET, returns the PSK with `old_passphrase` removed.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/psks/{psk_id}\n\ngetOrgPsk\n\nGet Org PSK Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/psks/import\n\nimportOrgPsks\n\nImport PSK from CSV file or JSON\n\n##\xa0CSV File Format\n```\nPSK Import CSV File Format:\nname,ssid,passphrase,usage,vlan_id,mac,max_usage,role,expire_time,notify_expiry,expiry_notification_time,notify_on_create_or_edit,email\nCommon,warehouse,foryoureyesonly,single,35,a31425f31278,0,student,1618594236\nJustin,reception,visible,multi,1002,200,teacher,1618594236\nCommon2,ssid,1245678-xx,single,35,a31425f31278,0,student,1618594236,true,7,true,admin@test.com\n```",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/psks\n\nlistOrgPsks\n\nGet List of Org Psks",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_psks(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    name: Annotated[str | None, Field(description="query parameter 'name'")] = None,
    ssid: Annotated[str | None, Field(description="query parameter 'ssid'")] = None,
    role: Annotated[str | None, Field(description="query parameter 'role'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
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
    description="PUT /api/v1/orgs/{org_id}/psks\n\nupdateOrgMultiplePsks\n\nUpdate Multiple PSKs",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="PUT /api/v1/orgs/{org_id}/psks/{psk_id}\n\nupdateOrgPsk\n\nUpdate Org PSK",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
