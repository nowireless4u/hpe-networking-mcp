"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``IdleTime``
Operations in this file: 2
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_idle_clear",
    description="GET /idle/clear\n\nIdleTime415\n\nClear idle time",
    capability=Capability.READ,
)
async def edgeconnect_get_idle_clear(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/idle/clear",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_idle_increment",
    description="GET /idle/increment\n\nIdleTime416\n\nIncrement session idle counter",
    capability=Capability.READ,
)
async def edgeconnect_get_idle_increment(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/idle/increment",
        query_params=None,
    )
