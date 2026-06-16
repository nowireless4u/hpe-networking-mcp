"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``syncState``
Operations in this file: 2
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_cache_sync_state",
    description="GET /cache/syncState\n\ngetCacheAndDbData\n\nRetrieve cache and database synchronization state",
    capability=Capability.READ,
)
async def edgeconnect_get_cache_sync_state(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cache/syncState",
        query_params=None,
    )


@tool(
    name="edgeconnect_put_cache_sync_state",
    description="PUT /cache/syncState\n\nupdateCache\n\nSynchronize in-memory cache with database values",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cache_sync_state(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cache/syncState",
        query_params=None,
        body=body,
    )
