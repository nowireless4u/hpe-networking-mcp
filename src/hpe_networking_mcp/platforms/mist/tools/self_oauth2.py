"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Self OAuth2``
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
    name="mist_get_oauth2_url_for_linking",
    description="GET /api/v1/self/oauth/{provider}\n\ngetOauth2UrlForLinking\n\nObtain Authorization URL for Linking",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_oauth2_url_for_linking(
    ctx: Context,
    provider: Annotated[str, Field(description="path parameter 'provider'")],
    forward: Annotated[str | None, Field(description="query parameter 'forward'")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/self/oauth/{provider}",
        path_params={"provider": provider},
        query_params={"forward": forward},
        body=None,
    )


@_mcp_tool(
    name="mist_link_oauth2_mist_account",
    description="POST /api/v1/self/oauth/{provider}\n\nlinkOauth2MistAccount\n\nLink Mist account with an OAuth2 Provider",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_link_oauth2_mist_account(
    ctx: Context,
    provider: Annotated[str, Field(description="path parameter 'provider'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/self/oauth/{provider}",
        path_params={"provider": provider},
        query_params=None,
        body=body,
    )
