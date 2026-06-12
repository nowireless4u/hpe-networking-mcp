"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Self Audit Logs``
Operations in this file: 1
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_list_self_audit_logs",
    description="GET /api/v1/self/logs\n\nlistSelfAuditLogs\n\nGet List of change logs across all Orgs for current admin\nAudit logs records all administrative activities done by current admin across all orgs",
    capability=Capability.READ,
)
async def mist_list_self_audit_logs(
    ctx: Context,
    message: Annotated[str | None, Field(description="Filter results by message text")] = None,
    sort: Annotated[
        Any | None,
        Field(
            description="Field used to sort results; a leading `-` indicates descending order. enum: `-timestamp`, `admin_id`, `site_id`, `timestamp`"
        ),
    ] = None,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/self/logs",
        path_params=None,
        query_params={
            "message": message,
            "sort": sort,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
            "page": page,
        },
        body=None,
    )
