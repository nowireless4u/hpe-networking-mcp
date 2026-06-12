"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Admins Lookup``
Operations in this file: 1
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
    name="mist_lookup",
    description="POST /api/v1/login/lookup\n\nlookup\n\nCheck the login method for an administrator email address. This public lookup is mainly used by UI clients to determine whether the user should continue with local login or be redirected to SSO.",
    capability=Capability.WRITE,
)
async def mist_lookup(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/login/lookup",
        path_params=None,
        query_params=None,
        body=body,
    )
