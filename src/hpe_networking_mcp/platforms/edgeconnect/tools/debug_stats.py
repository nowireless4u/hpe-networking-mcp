"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``debugStats``
Operations in this file: 5
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_stats_debug_stats_orchestrator_gc_stats",
    description="GET /stats/debugStats/orchestrator/gcStats\n\ngetGCStats\n\nGet JVM Garbage Collection statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_debug_stats_orchestrator_gc_stats(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/debugStats/orchestrator/gcStats",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_debug_stats_orchestrator_hikari_stats",
    description="GET /stats/debugStats/orchestrator/hikariStats\n\ngetHikariStats\n\nGet HikariCP database connection pool statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_debug_stats_orchestrator_hikari_stats(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/debugStats/orchestrator/hikariStats",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_debug_stats_orchestrator_jdbc_stats",
    description="GET /stats/debugStats/orchestrator/jdbcStats\n\ngetJDBCStats\n\nGet MySQL database server statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_debug_stats_orchestrator_jdbc_stats(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/debugStats/orchestrator/jdbcStats",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_debug_stats_orchestrator_request_count",
    description="GET /stats/debugStats/orchestrator/requestCount\n\ngetRequestCount\n\nGet REST API request counts within a time range",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_debug_stats_orchestrator_request_count(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Start of the time range in milliseconds since Unix epoch. Must be less than endTime.")
    ],
    endTime: Annotated[
        int,
        Field(description="End of the time range in milliseconds since Unix epoch. Must be greater than startTime."),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/debugStats/orchestrator/requestCount",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_debug_stats_orchestrator_request_stats",
    description="GET /stats/debugStats/orchestrator/requestStats\n\ngetRequestStats\n\nGet REST API request statistics by user and IP address within a time range",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_debug_stats_orchestrator_request_stats(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Start of the time range in milliseconds since Unix epoch. Must be less than endTime.")
    ],
    endTime: Annotated[
        int,
        Field(description="End of the time range in milliseconds since Unix epoch. Must be greater than startTime."),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/debugStats/orchestrator/requestStats",
        query_params=query_params or None,
    )
