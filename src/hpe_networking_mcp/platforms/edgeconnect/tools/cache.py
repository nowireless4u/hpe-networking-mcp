"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``cache``
Operations in this file: 2
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_cache_builtin_apps",
    description="GET /cache/builtinApps\n\nbuiltinAppGet157\n\nRetrieve cached built-in applications",
    capability=Capability.READ,
)
async def edgeconnect_get_cache_builtin_apps(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cache/builtinApps",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_cache_user_apps",
    description="GET /cache/userApps\n\nuserAppGet159\n\nRetrieve cached user-defined applications",
    capability=Capability.READ,
)
async def edgeconnect_get_cache_user_apps(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cache/userApps",
        query_params=None,
    )
