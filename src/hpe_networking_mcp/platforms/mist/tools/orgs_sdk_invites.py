"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs SDK Invites``
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
    name="mist_activate_sdk_invite",
    description="POST /api/v1/mobile/verify/{secret}\n\nactivateSdkInvite\n\nVerify secret",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_activate_sdk_invite(
    ctx: Context,
    secret: Annotated[str, Field(description="path parameter 'secret'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/mobile/verify/{secret}")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/mobile/verify/{secret}",
        path_params={"secret": secret},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_sdk_invite",
    description="POST /api/v1/orgs/{org_id}/sdkinvites\n\ncreateSdkInvite\n\nCreate SDK Invite",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_sdk_invite(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/sdkinvites",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_get_sdk_invite",
    description="GET /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}\n\ngetSdkInvite\n\nGet SDK Invite Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_sdk_invite(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sdkinvite_id: Annotated[str, Field(description="path parameter 'sdkinvite_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}",
        path_params={"org_id": org_id, "sdkinvite_id": sdkinvite_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_sdk_invite_qr_code",
    description="GET /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}/qrcode\n\ngetSdkInviteQrCode\n\nRevoke SDK Invite",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_sdk_invite_qr_code(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sdkinvite_id: Annotated[str, Field(description="path parameter 'sdkinvite_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}/qrcode",
        path_params={"org_id": org_id, "sdkinvite_id": sdkinvite_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_sdk_invites",
    description="GET /api/v1/orgs/{org_id}/sdkinvites\n\nlistSdkInvites\n\nGet List of Org SDK Invites",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_sdk_invites(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/sdkinvites",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_revoke_sdk_invite",
    description="DELETE /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}\n\nrevokeSdkInvite\n\nRevoke SDK Invite",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_revoke_sdk_invite(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sdkinvite_id: Annotated[str, Field(description="path parameter 'sdkinvite_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}",
        path_params={"org_id": org_id, "sdkinvite_id": sdkinvite_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_send_sdk_invite_email",
    description="POST /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}/email\n\nsendSdkInviteEmail\n\nSend SDK Invite by Email",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_send_sdk_invite_email(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sdkinvite_id: Annotated[str, Field(description="path parameter 'sdkinvite_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}/email",
        path_params={"org_id": org_id, "sdkinvite_id": sdkinvite_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_send_sdk_invite_sms",
    description="POST /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}/sms\n\nsendSdkInviteSms\n\nSend SDK Invite by SMS",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_send_sdk_invite_sms(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sdkinvite_id: Annotated[str, Field(description="path parameter 'sdkinvite_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}/sms",
        path_params={"org_id": org_id, "sdkinvite_id": sdkinvite_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_sdk_invite",
    description="PUT /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}\n\nupdateSdkInvite\n\nUpdate SDK Invite",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_sdk_invite(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sdkinvite_id: Annotated[str, Field(description="path parameter 'sdkinvite_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}",
        path_params={"org_id": org_id, "sdkinvite_id": sdkinvite_id},
        query_params=None,
        body=body,
    )
