"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Devices - Others``
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
    name="mist_count_site_other_device_events",
    description="GET /api/v1/sites/{site_id}/otherdevices/events/count\n\ncountSiteOtherDeviceEvents\n\nCount third-party device events for a site, optionally grouped by the `distinct` field and filtered by event type and time range. Use [Count Org Other Device Events](/#operations/countOrgOtherDeviceEvents) to count third-party device events across the organization.",
    capability=Capability.READ,
)
async def mist_count_site_other_device_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[
        Any | None,
        Field(description="Field used to group this count response. enum: `mac`, `site_id`, `type`, `vendor`"),
    ] = None,
    type: Annotated[
        str | None,
        Field(description="See [List Device Events Definitions](/#operations/listOtherDeviceEventsDefinitions)"),
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
        "/api/v1/sites/{site_id}/otherdevices/events/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "type": type,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_other_devices",
    description="GET /api/v1/sites/{site_id}/otherdevices\n\nlistSiteOtherDevices\n\nList third-party devices in a site, such as devices discovered or tracked outside the managed Mist device inventory. Use [List Org Other Devices](/#operations/listOrgOtherDevices) to retrieve third-party devices across the organization.",
    capability=Capability.READ,
)
async def mist_list_site_other_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    vendor: Annotated[str | None, Field(description="Filter results by vendor")] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    serial: Annotated[str | None, Field(description="Filter results by device serial number")] = None,
    model: Annotated[str | None, Field(description="Filter results by device model")] = None,
    name: Annotated[str | None, Field(description="Filter results by name")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/otherdevices",
        path_params={"site_id": site_id},
        query_params={
            "vendor": vendor,
            "mac": mac,
            "serial": serial,
            "model": model,
            "name": name,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_other_device_events",
    description="GET /api/v1/sites/{site_id}/otherdevices/events/search\n\nsearchSiteOtherDeviceEvents\n\nSearch third-party device events for a site with filters for device identifiers, model, vendor, event type, and time range. Use [Search Org Other Device Events](/#operations/searchOrgOtherDeviceEvents) to search third-party device events across the organization.",
    capability=Capability.READ,
)
async def mist_search_site_other_device_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    device_mac: Annotated[str | None, Field(description="MAC of attached device")] = None,
    vendor: Annotated[str | None, Field(description="Filter results by vendor")] = None,
    type: Annotated[
        str | None,
        Field(description="See [List Device Events Definitions](/#operations/listOtherDeviceEventsDefinitions)"),
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
        "/api/v1/sites/{site_id}/otherdevices/events/search",
        path_params={"site_id": site_id},
        query_params={
            "mac": mac,
            "device_mac": device_mac,
            "vendor": vendor,
            "type": type,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
