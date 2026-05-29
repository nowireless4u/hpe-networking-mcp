"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Admins Login``
Operations in this file: 2
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
    name="mist_login",
    description="POST /api/v1/login\n\nlogin\n\nLog in with email/password.\nWhen 2FA is enabled, there are two ways to login:\n1. login with two_factor token (with Google Authenticator, etc) \n2. login with email/password, generate the token, and use /login/two_factor with the token",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/login/two_factor\n\ntwoFactor\n\nSend 2FA Code",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
