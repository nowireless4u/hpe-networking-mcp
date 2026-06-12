"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Zones``
Operations in this file: 7
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
    name="mist_count_site_zone_sessions",
    description="GET /api/v1/sites/{site_id}/{zone_type}/count\n\ncountSiteZoneSessions\n\nCount by Distinct Attributes of Site Zone Sessions",
    capability=Capability.READ,
)
async def mist_count_site_zone_sessions(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    zone_type: Annotated[Any, Field(description="path parameter 'zone_type'")],
    distinct: Annotated[
        Any | None,
        Field(description="Field used to group this count response. enum: `scope`, `scope_id`, `user`, `user_type`"),
    ] = None,
    user_type: Annotated[
        Any | None, Field(description="Filter results by user type. enum: `asset`, `client`, `sdkclient`")
    ] = None,
    user: Annotated[str | None, Field(description="Client MAC / Asset MAC / SDK UUID")] = None,
    scope_id: Annotated[str | None, Field(description="If `scope`==`map`/`zone`/`rssizone`, the scope id")] = None,
    scope: Annotated[
        Any | None, Field(description="Filter results by scope. enum: `map`, `rssizone`, `site`, `zone`")
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
    capability=Capability.WRITE,
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
    capability=Capability.WRITE_DELETE,
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
    capability=Capability.READ,
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
    capability=Capability.READ,
)
async def mist_list_site_zones(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
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
    capability=Capability.READ,
)
async def mist_search_site_zone_sessions(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    zone_type: Annotated[Any, Field(description="path parameter 'zone_type'")],
    user_type: Annotated[
        Any | None, Field(description="Filter results by user type. enum: `asset`, `client`, `sdkclient`")
    ] = None,
    user: Annotated[str | None, Field(description="Client MAC / Asset MAC / SDK UUID")] = None,
    scope_id: Annotated[str | None, Field(description="If `scope`==`map`/`zone`/`rssizone`, the scope id")] = None,
    scope: Annotated[
        Any | None, Field(description="Filter results by scope. enum: `map`, `rssizone`, `site`, `zone`")
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
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
    capability=Capability.WRITE,
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
