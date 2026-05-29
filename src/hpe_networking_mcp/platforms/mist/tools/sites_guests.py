"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Guests``
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
    name="mist_count_site_guest_authorizations",
    description="GET /api/v1/sites/{site_id}/guests/count\n\ncountSiteGuestAuthorizations\n\nCount by Distinct Attributes of Authorized Guest",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_guest_authorizations(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
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
        "/api/v1/sites/{site_id}/guests/count",
        path_params={"site_id": site_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_delete_site_guest_authorization",
    description="DELETE /api/v1/sites/{site_id}/guests/{guest_mac}\n\ndeleteSiteGuestAuthorization\n\nDelete Guest Authorization",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_guest_authorization(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    guest_mac: Annotated[str, Field(description="path parameter 'guest_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/guests/{guest_mac}",
        path_params={"site_id": site_id, "guest_mac": guest_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_guest_authorization",
    description="GET /api/v1/sites/{site_id}/guests/{guest_mac}\n\ngetSiteGuestAuthorization\n\nGet Guest Authorization",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_guest_authorization(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    guest_mac: Annotated[str, Field(description="path parameter 'guest_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/guests/{guest_mac}",
        path_params={"site_id": site_id, "guest_mac": guest_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_all_guest_authorizations",
    description="GET /api/v1/sites/{site_id}/guests\n\nlistSiteAllGuestAuthorizations\n\nGet List of Site Guest Authorizations",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_all_guest_authorizations(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wlan_id: Annotated[
        str | None,
        Field(description="UUID of single or multiple (Comma separated) WLAN under Site `site_id` (to filter by WLAN)"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/guests",
        path_params={"site_id": site_id},
        query_params={"wlan_id": wlan_id},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_all_guest_authorizations_derived",
    description="GET /api/v1/sites/{site_id}/guests/derived\n\nlistSiteAllGuestAuthorizationsDerived\n\nGet the list of derived Guest Authorizations for a site",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_all_guest_authorizations_derived(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wlan_id: Annotated[
        str | None,
        Field(description="UUID of single or multiple (Comma separated) WLAN under Site `site_id` (to filter by WLAN)"),
    ] = None,
    cross_site: Annotated[
        bool, Field(description="Whether to get org level guests, default is false i.e get site level guests")
    ] = False,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/guests/derived",
        path_params={"site_id": site_id},
        query_params={"wlan_id": wlan_id, "cross_site": cross_site},
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_guest_authorization",
    description="GET /api/v1/sites/{site_id}/guests/search\n\nsearchSiteGuestAuthorization\n\nSearch Authorized Guest",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_guest_authorization(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wlan_id: Annotated[str | None, Field(description="query parameter 'wlan_id'")] = None,
    auth_method: Annotated[str | None, Field(description="query parameter 'auth_method'")] = None,
    ssid: Annotated[str | None, Field(description="query parameter 'ssid'")] = None,
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
        "/api/v1/sites/{site_id}/guests/search",
        path_params={"site_id": site_id},
        query_params={
            "wlan_id": wlan_id,
            "auth_method": auth_method,
            "ssid": ssid,
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
    name="mist_update_site_guest_authorization",
    description="PUT /api/v1/sites/{site_id}/guests/{guest_mac}\n\nupdateSiteGuestAuthorization\n\nUpdate Guest Authorization",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_guest_authorization(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    guest_mac: Annotated[str, Field(description="path parameter 'guest_mac'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/guests/{guest_mac}",
        path_params={"site_id": site_id, "guest_mac": guest_mac},
        query_params=None,
        body=body,
    )
