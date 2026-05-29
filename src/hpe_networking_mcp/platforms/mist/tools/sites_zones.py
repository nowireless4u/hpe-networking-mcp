"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Zones``
Operations in this file: 7
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
    name="mist_count_site_zone_sessions",
    description="GET /api/v1/sites/{site_id}/{zone_type}/count\n\ncountSiteZoneSessions\n\nCount by Distinct Attributes of Site Zone Sessions",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_zone_sessions(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    zone_type: Annotated[Any, Field(description="path parameter 'zone_type'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    user_type: Annotated[Any | None, Field(description="User type")] = None,
    user: Annotated[str | None, Field(description="Client MAC / Asset MAC / SDK UUID")] = None,
    scope_id: Annotated[str | None, Field(description="If `scope`==`map`/`zone`/`rssizone`, the scope id")] = None,
    scope: Annotated[Any | None, Field(description="Scope")] = None,
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
        "/api/v1/sites/{site_id}/{zone_type}/count",
        path_params={"site_id": site_id, "zone_type": zone_type},
        query_params={
            "distinct": distinct,
            "user_type": user_type,
            "user": user,
            "scope_id": scope_id,
            "scope": scope,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_create_site_zone",
    description="POST /api/v1/sites/{site_id}/zones\n\ncreateSiteZone\n\nCreate Site Zone",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_zone(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/zones",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_zone",
    description="DELETE /api/v1/sites/{site_id}/zones/{zone_id}\n\ndeleteSiteZone\n\nDelete Site Zone",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_zone(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    zone_id: Annotated[str, Field(description="path parameter 'zone_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/zones/{zone_id}",
        path_params={"site_id": site_id, "zone_id": zone_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_zone",
    description="GET /api/v1/sites/{site_id}/zones/{zone_id}\n\ngetSiteZone\n\nGet Site Zone Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_zone(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    zone_id: Annotated[str, Field(description="path parameter 'zone_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/zones/{zone_id}",
        path_params={"site_id": site_id, "zone_id": zone_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_zones",
    description="GET /api/v1/sites/{site_id}/zones\n\nlistSiteZones\n\nGet List of Site Zones",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_zones(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/zones",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_zone_sessions",
    description="GET /api/v1/sites/{site_id}/{zone_type}/visits/search\n\nsearchSiteZoneSessions\n\nSearch Zone Sessions",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_zone_sessions(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    zone_type: Annotated[Any, Field(description="path parameter 'zone_type'")],
    user_type: Annotated[Any | None, Field(description="User type, client (default) / sdkclient / asset")] = None,
    user: Annotated[str | None, Field(description="Client MAC / Asset MAC / SDK UUID")] = None,
    scope_id: Annotated[str | None, Field(description="If `scope`==`map`/`zone`/`rssizone`, the scope id")] = None,
    scope: Annotated[Any | None, Field(description="Scope")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/{zone_type}/visits/search",
        path_params={"site_id": site_id, "zone_type": zone_type},
        query_params={
            "user_type": user_type,
            "user": user,
            "scope_id": scope_id,
            "scope": scope,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_zone",
    description="PUT /api/v1/sites/{site_id}/zones/{zone_id}\n\nupdateSiteZone\n\nUpdate Site Zone",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_zone(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    zone_id: Annotated[str, Field(description="path parameter 'zone_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/zones/{zone_id}",
        path_params={"site_id": site_id, "zone_id": zone_id},
        query_params=None,
        body=body,
    )
