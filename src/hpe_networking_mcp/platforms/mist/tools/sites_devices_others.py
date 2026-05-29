"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Devices - Others``
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
    name="mist_count_site_other_device_events",
    description="GET /api/v1/sites/{site_id}/otherdevices/events/count\n\ncountSiteOtherDeviceEvents\n\nCount by Distinct Attributes of Site OtherDevices Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_other_device_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    type: Annotated[
        str | None,
        Field(description="See [List Device Events Definitions](/#operations/listOtherDeviceEventsDefinitions)"),
    ] = None,
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
    description="GET /api/v1/sites/{site_id}/otherdevices\n\nlistSiteOtherDevices\n\nGet List of Site other devices (3rd party devices)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_other_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    vendor: Annotated[str | None, Field(description="query parameter 'vendor'")] = None,
    mac: Annotated[str | None, Field(description="query parameter 'mac'")] = None,
    serial: Annotated[str | None, Field(description="query parameter 'serial'")] = None,
    model: Annotated[str | None, Field(description="query parameter 'model'")] = None,
    name: Annotated[str | None, Field(description="query parameter 'name'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
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
    description="GET /api/v1/sites/{site_id}/otherdevices/events/search\n\nsearchSiteOtherDeviceEvents\n\nSearch Site OtherDevices Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_other_device_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mac: Annotated[str | None, Field(description="MAC")] = None,
    device_mac: Annotated[str | None, Field(description="MAC of attached device")] = None,
    vendor: Annotated[str | None, Field(description="Vendor name")] = None,
    type: Annotated[
        str | None,
        Field(description="See [List Device Events Definitions](/#operations/listOtherDeviceEventsDefinitions)"),
    ] = None,
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
