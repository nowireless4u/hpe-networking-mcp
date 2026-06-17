"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``liveTailLogger``
Operations in this file: 1
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
    name="edgeconnect_get_live_tail_logger_get_loggers",
    description="GET /liveTailLogger/getLoggers\n\nliveTailLoggerGetLoggers\n\nRetrieve available logger names from the Orchestrator",
    capability=Capability.READ,
)
async def edgeconnect_get_live_tail_logger_get_loggers(
    ctx: Context,
    feature: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter loggers by a specific feature name. If omitted, all available non-special loggers are returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if feature is not None:
        query_params["feature"] = feature
    return await edgeconnect_request(
        ctx,
        "GET",
        "/liveTailLogger/getLoggers",
        query_params=query_params or None,
    )
