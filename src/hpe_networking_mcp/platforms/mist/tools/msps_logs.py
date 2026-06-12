"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs Logs``
Operations in this file: 2
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
    name="mist_count_msp_audit_logs",
    description="GET /api/v1/msps/{msp_id}/logs/count\n\ncountMspAuditLogs\n\nReturn distinct counts of MSP audit log entries grouped by the requested field, such as administrator, message, or organization.",
    capability=Capability.READ,
)
async def mist_count_msp_audit_logs(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `admin_id`, `admin_name`, `message`, `org_id`"
        ),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/logs/count",
        path_params={"msp_id": msp_id},
        query_params={"distinct": distinct, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_list_msp_audit_logs",
    description="GET /api/v1/msps/{msp_id}/logs\n\nlistMspAuditLogs\n\nList audit log entries for configuration and administrative changes within this MSP, with optional filters by site, administrator, message text, and time range.",
    capability=Capability.READ,
)
async def mist_list_msp_audit_logs(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    admin_name: Annotated[str | None, Field(description="Admin name or email")] = None,
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
        "/api/v1/msps/{msp_id}/logs",
        path_params={"msp_id": msp_id},
        query_params={
            "site_id": site_id,
            "admin_name": admin_name,
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
