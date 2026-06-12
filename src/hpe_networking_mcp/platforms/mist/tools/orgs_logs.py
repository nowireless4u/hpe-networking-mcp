"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Logs``
Operations in this file: 3
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
    name="mist_count_org_audit_logs",
    description="GET /api/v1/orgs/{org_id}/logs/count\n\ncountOrgAuditLogs\n\nCount organization audit log records, optionally grouped by `distinct` and filtered by administrator, site, message text, and time range.",
    capability=Capability.READ,
)
async def mist_count_org_audit_logs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `admin_id`, `admin_name`, `message`, `site_id`"
        ),
    ] = None,
    admin_id: Annotated[str | None, Field(description="Filter audit log results by administrator identifier")] = None,
    admin_name: Annotated[
        str | None,
        Field(
            description="Filter audit log results by one or more administrator names. Supports comma-separated values"
        ),
    ] = None,
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    message: Annotated[str | None, Field(description="Filter log results by message text")] = None,
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
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/logs/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "admin_id": admin_id,
            "admin_name": admin_name,
            "site_id": site_id,
            "message": message,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_audit_logs",
    description="GET /api/v1/orgs/{org_id}/logs/search\n\nlistOrgAuditLogs\n\nGet a list of change logs for the current Org",
    capability=Capability.READ,
)
async def mist_list_org_audit_logs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[
        str | None, Field(description="Filter results by site identifier. Accepts multiple comma-separated values.")
    ] = None,
    admin_name: Annotated[
        str | None,
        Field(
            description="Filter results by one or more administrator names or email addresses. Supports comma-separated values"
        ),
    ] = None,
    message: Annotated[
        str | None,
        Field(description="Filter results by one or more message text values. Supports comma-separated values"),
    ] = None,
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
        "/api/v1/orgs/{org_id}/logs/search",
        path_params={"org_id": org_id},
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


@_mcp_tool(
    name="mist_list_org_audit_logs_legacy",
    description="GET /api/v1/orgs/{org_id}/logs\n\nlistOrgAuditLogsLegacy\n\nGet List of change logs for the current Org",
    capability=Capability.READ,
)
async def mist_list_org_audit_logs_legacy(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[
        str | None, Field(description="Filter results by site identifier. Accepts multiple comma-separated values.")
    ] = None,
    admin_name: Annotated[
        str | None,
        Field(
            description="Filter results by one or more administrator names or email addresses. Supports comma-separated values"
        ),
    ] = None,
    message: Annotated[
        str | None,
        Field(description="Filter results by one or more message text values. Supports comma-separated values"),
    ] = None,
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
        "/api/v1/orgs/{org_id}/logs",
        path_params={"org_id": org_id},
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
