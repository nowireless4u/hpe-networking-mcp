"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Admins Recover Password``
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
    name="mist_recover_password",
    description="POST /api/v1/recover\n\nrecoverPassword\n\nRecover Password\nAn email will also be sent to the user with a link to https://manage.mist.com/verify/recover?token=:token",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/recover/verify/{token}\n\nverifyRecoverPassword\n\nVerify Recover Password\nWith correct verification, the user will be authenticated. UI can then prompt for new password",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
