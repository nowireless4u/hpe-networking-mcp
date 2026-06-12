"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Admins Login``
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
    name="mist_login",
    description="POST /api/v1/login\n\nlogin\n\nAuthenticate an administrator with email and password. A successful login creates the browser session cookies, including the `csrftoken` value used with the `X-CSRFToken` header on later API requests.\n\nWhen 2FA is enabled, either include the `two_factor` code in this request or submit the first factor here and complete the login with [Two Factor](/#operations/twoFactor).",
    capability=Capability.WRITE,
)
async def mist_login(
    ctx: Context,
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/login")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/login",
        path_params=None,
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_two_factor",
    description="POST /api/v1/login/two_factor\n\ntwoFactor\n\nComplete a two-factor login by submitting the 2FA code after the initial email/password step has created a pending login session.",
    capability=Capability.WRITE,
)
async def mist_two_factor(
    ctx: Context,
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/login/two_factor")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/login/two_factor",
        path_params=None,
        query_params=None,
        body=body,
    )
