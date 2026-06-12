"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Guests``
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
    name="mist_count_site_guest_authorizations",
    description="GET /api/v1/sites/{site_id}/guests/count\n\ncountSiteGuestAuthorizations\n\nCount authorized guest records for a site, optionally grouped by the `distinct` field and filtered by time range. Use [Count Org Guest Authorizations](/#operations/countOrgGuestAuthorizations) to count authorized guest records across the organization.",
    capability=Capability.READ,
)
async def mist_count_site_guest_authorizations(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[
        Any | None, Field(description="Field used to group this count response. enum: `auth_method`, `company`, `ssid`")
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
        "/api/v1/sites/{site_id}/guests/count",
        path_params={"site_id": site_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_delete_site_guest_authorization",
    description="DELETE /api/v1/sites/{site_id}/guests/{guest_mac}\n\ndeleteSiteGuestAuthorization\n\nDelete Guest Authorization",
    capability=Capability.WRITE_DELETE,
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
    capability=Capability.READ,
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
    capability=Capability.READ,
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
    capability=Capability.READ,
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
    description="GET /api/v1/sites/{site_id}/guests/search\n\nsearchSiteGuestAuthorization\n\nSearch authorized guest records for a site with filters for WLAN, SSID, authentication method, and time range. Use [Search Org Guest Authorization](/#operations/searchOrgGuestAuthorization) to search authorized guest records across the organization.",
    capability=Capability.READ,
)
async def mist_search_site_guest_authorization(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wlan_id: Annotated[str | None, Field(description="Filter results by WLAN identifier")] = None,
    auth_method: Annotated[str | None, Field(description="Filter guest results by authentication method")] = None,
    ssid: Annotated[str | None, Field(description="Filter results by SSID")] = None,
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
    capability=Capability.WRITE,
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
