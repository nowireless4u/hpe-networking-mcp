"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``session``
Operations in this file: 1
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_login_sessions",
    description="GET /loginSessions\n\ngetAllLoginSessions\n\nGet all active login sessions",
    capability=Capability.READ,
)
async def edgeconnect_get_login_sessions(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/loginSessions",
        query_params=None,
    )
