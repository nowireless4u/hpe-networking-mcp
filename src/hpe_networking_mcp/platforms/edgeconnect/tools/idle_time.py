"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

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
    capability=Capability.OPERATIONAL,
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
    capability=Capability.OPERATIONAL,
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
