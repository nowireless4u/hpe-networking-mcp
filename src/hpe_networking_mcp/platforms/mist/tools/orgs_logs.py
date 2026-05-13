"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Logs``
Operations in this file: 3
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_count_org_audit_logs",
    description="GET /api/v1/orgs/{org_id}/logs/count\n\ncountOrgAuditLogs\n\nCount by Distinct Attributes of Audit Logs",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_audit_logs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    admin_id: Annotated[str | None, Field(description="query parameter 'admin_id'")] = None,
    admin_name: Annotated[str | None, Field(description="query parameter 'admin_name'")] = None,
    site_id: Annotated[str | None, Field(description="query parameter 'site_id'")] = None,
    message: Annotated[str | None, Field(description="query parameter 'message'")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_audit_logs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[str | None, Field(description="Site id")] = None,
    admin_name: Annotated[str | None, Field(description="Admin name or email")] = None,
    message: Annotated[str | None, Field(description="Message")] = None,
    sort: Annotated[Any | None, Field(description="Sort order")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
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
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_audit_logs_legacy(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[str | None, Field(description="Site id")] = None,
    admin_name: Annotated[str | None, Field(description="Admin name or email")] = None,
    message: Annotated[str | None, Field(description="Message")] = None,
    sort: Annotated[Any | None, Field(description="Sort order")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
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
