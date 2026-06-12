"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs SDK Invites``
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
    name="mist_activate_sdk_invite",
    description="POST /api/v1/mobile/verify/{secret}\n\nactivateSdkInvite\n\nActivate a mobile SDK invite by verifying the invite secret and binding it to the supplied device identifier. The response returns the device-specific secret used by the mobile SDK client.",
    capability=Capability.WRITE,
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
    description="POST /api/v1/orgs/{org_id}/sdkinvites\n\ncreateSdkInvite\n\nCreate an SDK invite that mobile SDK clients can use to onboard into the organization. The invite can be enabled or disabled, limited by usage quota, and associated with a site.",
    capability=Capability.WRITE,
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
    description="GET /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}\n\ngetSdkInvite\n\nReturn the configuration and status of an SDK invite, including enablement, expiration time, usage quota, and site scope.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}/qrcode\n\ngetSdkInviteQrCode\n\nDownload a QR code image for the SDK invite so it can be scanned by a mobile SDK client during onboarding.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/sdkinvites\n\nlistSdkInvites\n\nList SDK invites configured for the organization. SDK invites are used to onboard mobile SDK clients and can define whether an invite is enabled, limited by usage quota, or scoped to a site.",
    capability=Capability.READ,
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
    description="DELETE /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}\n\nrevokeSdkInvite\n\nRevoke an SDK invite so it can no longer be used for mobile SDK client onboarding.",
    capability=Capability.WRITE_DELETE,
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
    description="POST /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}/email\n\nsendSdkInviteEmail\n\nSend the SDK invite to a recipient email address so the recipient can onboard a mobile SDK client.",
    capability=Capability.WRITE,
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
    description="POST /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}/sms\n\nsendSdkInviteSms\n\nSend the SDK invite to a phone number by SMS so the recipient can onboard a mobile SDK client.",
    capability=Capability.WRITE,
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
    description="PUT /api/v1/orgs/{org_id}/sdkinvites/{sdkinvite_id}\n\nupdateSdkInvite\n\nUpdate an SDK invite's onboarding settings, such as its display name, enabled state, expiration time, quota, or site association.",
    capability=Capability.WRITE,
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
