"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Admins``
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
    name="mist_get_admin_registration_info",
    description="GET /api/v1/register/recaptcha\n\ngetAdminRegistrationInfo\n\nReturn the public CAPTCHA settings required for administrator registration. This public endpoint does not require authentication. Use the returned `flavor`, `required`, and `sitekey` values to render the correct CAPTCHA challenge before calling [Register New Admin](/#operations/registerNewAdmin).",
    capability=Capability.READ,
)
async def mist_get_admin_registration_info(
    ctx: Context,
    recaptcha_flavor: Annotated[
        Any | None, Field(description="Filter login settings by reCAPTCHA flavor. enum: `google`, `hcaptcha`")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/register/recaptcha",
        path_params=None,
        query_params={"recaptcha_flavor": recaptcha_flavor},
        body=None,
    )


@_mcp_tool(
    name="mist_register_new_admin",
    description="POST /api/v1/register\n\nregisterNewAdmin\n\nRegister a new administrator account and initial organization. This public endpoint does not require authentication. Mist sends a verification email containing a link such as `/verify/register?token={token}`; use [Verify Registration](/#operations/verifyRegistration) to complete registration with that token.\n\nUse [Get Registration Information](/#operations/getAdminRegistrationInfo) before submitting this request to determine whether CAPTCHA is required, which CAPTCHA provider to render, and which public site key to use. If CAPTCHA is required, includ...",
    capability=Capability.WRITE,
)
async def mist_register_new_admin(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/register",
        path_params=None,
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_verify_admin_invite",
    description="POST /api/v1/invite/verify/{token}\n\nverifyAdminInvite\n\nAccept an administrator invite using the invite verification token from the invite email. This public endpoint does not require authentication. After a successful verification, call [Get Self](/#operations/getSelf) to refresh the authenticated admin profile and retrieve the newly granted privileges.",
    capability=Capability.WRITE,
)
async def mist_verify_admin_invite(
    ctx: Context,
    token: Annotated[str, Field(description="path parameter 'token'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/invite/verify/{token}",
        path_params={"token": token},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_verify_registration",
    description="POST /api/v1/register/verify/{token}\n\nverifyRegistration\n\nVerify a new administrator registration using the token from the registration email. This public endpoint does not require authentication. A successful verification creates a login session and may also apply a pending invitation; the response indicates whether an invitation could not be applied automatically.",
    capability=Capability.WRITE,
)
async def mist_verify_registration(
    ctx: Context,
    token: Annotated[str, Field(description="path parameter 'token'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/register/verify/{token}",
        path_params={"token": token},
        query_params=None,
        body=None,
    )
