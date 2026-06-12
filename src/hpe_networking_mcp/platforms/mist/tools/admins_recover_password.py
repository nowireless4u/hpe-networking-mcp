"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Admins Recover Password``
Operations in this file: 2
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
    name="mist_recover_password",
    description="POST /api/v1/recover\n\nrecoverPassword\n\nStart password recovery for an administrator account. This public endpoint does not require authentication. When the request is accepted, Mist sends an email containing a recovery link such as `https://manage.mist.com/verify/recover?token=:token`. If CAPTCHA is required, include the CAPTCHA response token and provider flavor in the request body.",
    capability=Capability.WRITE,
)
async def mist_recover_password(
    ctx: Context,
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/recover")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/recover",
        path_params=None,
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_verify_recover_password",
    description="POST /api/v1/recover/verify/{token}\n\nverifyRecoverPassword\n\nVerify a password recovery token from the recovery email. This public endpoint does not require authentication. When the token is valid, the user is authenticated for the recovery flow so the client can prompt for and submit a new password.",
    capability=Capability.WRITE,
)
async def mist_verify_recover_password(
    ctx: Context,
    token: Annotated[str, Field(description="path parameter 'token'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/recover/verify/{token}",
        path_params={"token": token},
        query_params=None,
        body=None,
    )
