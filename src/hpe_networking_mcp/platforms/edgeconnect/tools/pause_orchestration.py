"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``pauseOrchestration``
Operations in this file: 2
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_pause_orchestration",
    description="GET /pauseOrchestration\n\ngetPauseOrchestration494\n\nGet nePks of appliances paused from orchestration",
    capability=Capability.READ,
)
async def edgeconnect_get_pause_orchestration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/pauseOrchestration",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_pause_orchestration",
    description="POST /pauseOrchestration\n\nsetPauseOrchestration495\n\nSet appliances to pause from orchestration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_pause_orchestration(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/pauseOrchestration",
        query_params=None,
        body=body,
    )
