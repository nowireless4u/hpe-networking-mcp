"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Admins Logout``
Operations in this file: 1
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Any

from fastmcp import Context
from mcp.types import ToolAnnotations

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_logout",
    description="POST /api/v1/logout\n\nlogout",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_logout(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/logout",
        path_params=None,
        query_params=None,
        body=None,
    )
