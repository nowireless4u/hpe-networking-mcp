"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Admins``
Operations in this file: 4
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
    name="mist_get_admin_registration_info",
    description="GET /api/v1/register/recaptcha\n\ngetAdminRegistrationInfo\n\nGet Registration Information",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_admin_registration_info(
    ctx: Context,
    recaptcha_flavor: Annotated[Any | None, Field(description="query parameter 'recaptcha_flavor'")] = None,
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
    description='POST /api/v1/register\n\nregisterNewAdmin\n\nRegister a new admin and his/her org\nAn email will also be sent to the user with a link to `/verify/register?token={token}`\n\n### reCAPTCHA\nGoogle reCAPTCHA is the choice to prevent bot registration\n\nIt needs this \n\n&lt;script src=\'https://www.google.com/recaptcha/api.js\' &gt;&lt;/script&gt;\n\nand this &lt;div&gt; in the desired place\n```html\n<div class="g-recaptcha" data_sitekey="6LdAewsTAAAAAE25XKQhPEQ2FiMTft-WrZXQ5NUd"></div>\n```\n\nUse GET /api/v1/register/recaptcha to read the current setting.\nResponse example:\n```json\n{    \n  "flavor": "google",\n  ...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/invite/verify/{token}\n\nverifyAdminInvite\n\n**Note**: another call to ```GET /api/v1/self``` is required to see the new set of privileges",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/register/verify/{token}\n\nverifyRegistration\n\nVerify registration",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
