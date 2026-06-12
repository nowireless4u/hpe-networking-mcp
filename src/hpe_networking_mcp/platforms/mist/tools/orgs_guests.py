"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Guests``
Operations in this file: 6
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
    name="mist_count_org_guest_authorizations",
    description="GET /api/v1/orgs/{org_id}/guests/count\n\ncountOrgGuestAuthorizations\n\nCount organization guest authorization records, optionally grouped by `distinct` and filtered by time range.",
    capability=Capability.READ,
)
async def mist_count_org_guest_authorizations(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
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
        "/api/v1/orgs/{org_id}/guests/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_delete_org_guest_authorization",
    description="DELETE /api/v1/orgs/{org_id}/guests/{guest_mac}\n\ndeleteOrgGuestAuthorization\n\nDelete a guest authorization record by guest MAC address.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_guest_authorization(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    guest_mac: Annotated[str, Field(description="path parameter 'guest_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/guests/{guest_mac}",
        path_params={"org_id": org_id, "guest_mac": guest_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_guest_authorization",
    description="GET /api/v1/orgs/{org_id}/guests/{guest_mac}\n\ngetOrgGuestAuthorization\n\nRetrieve the guest authorization record associated with a guest MAC address.",
    capability=Capability.READ,
)
async def mist_get_org_guest_authorization(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    guest_mac: Annotated[str, Field(description="path parameter 'guest_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/guests/{guest_mac}",
        path_params={"org_id": org_id, "guest_mac": guest_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_guest_authorizations",
    description="GET /api/v1/orgs/{org_id}/guests\n\nlistOrgGuestAuthorizations\n\nList guest authorization records across the organization, including WLAN, SSID, authentication method, expiration, and guest identity details.",
    capability=Capability.READ,
)
async def mist_list_org_guest_authorizations(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/guests",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_guest_authorization",
    description="GET /api/v1/orgs/{org_id}/guests/search\n\nsearchOrgGuestAuthorization\n\nSearch organization guest authorization records with filters for WLAN, SSID, authentication method, and time range.",
    capability=Capability.READ,
)
async def mist_search_org_guest_authorization(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wlan_id: Annotated[str | None, Field(description="Filter results by WLAN identifier")] = None,
    auth_method: Annotated[str | None, Field(description="Filter results by authentication method")] = None,
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
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/guests/search",
        path_params={"org_id": org_id},
        query_params={
            "wlan_id": wlan_id,
            "auth_method": auth_method,
            "ssid": ssid,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_guest_authorization",
    description="PUT /api/v1/orgs/{org_id}/guests/{guest_mac}\n\nupdateOrgGuestAuthorization\n\nUpdate the organization guest authorization record for a guest MAC address, including authorization state, duration, WLAN, and guest identity fields.",
    capability=Capability.WRITE,
)
async def mist_update_org_guest_authorization(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    guest_mac: Annotated[str, Field(description="path parameter 'guest_mac'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/guests/{guest_mac}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/guests/{guest_mac}",
        path_params={"org_id": org_id, "guest_mac": guest_mac},
        query_params=None,
        body=body,
    )
