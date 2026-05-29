"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Stats - Assets``
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
    name="mist_count_org_assets_by_distance_field",
    description="GET /api/v1/orgs/{org_id}/stats/assets/count\n\ncountOrgAssetsByDistanceField\n\nCount by Distinct Attributes of Org Assets",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_assets_by_distance_field(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/stats/assets/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_assets_stats",
    description="GET /api/v1/orgs/{org_id}/stats/assets\n\nlistOrgAssetsStats\n\nGet List of Org Assets Stats",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_assets_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
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
        "/api/v1/orgs/{org_id}/stats/assets",
        path_params={"org_id": org_id},
        query_params={"start": start, "end": end, "duration": duration, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_assets",
    description="GET /api/v1/orgs/{org_id}/stats/assets/search\n\nsearchOrgAssets\n\nSearch for Org Assets",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_assets(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[str | None, Field(description="query parameter 'site_id'")] = None,
    mac: Annotated[str | None, Field(description="query parameter 'mac'")] = None,
    device_name: Annotated[str | None, Field(description="query parameter 'device_name'")] = None,
    name: Annotated[str | None, Field(description="query parameter 'name'")] = None,
    map_id: Annotated[str | None, Field(description="query parameter 'map_id'")] = None,
    ibeacon_uuid: Annotated[str | None, Field(description="query parameter 'ibeacon_uuid'")] = None,
    ibeacon_major: Annotated[str | None, Field(description="query parameter 'ibeacon_major'")] = None,
    ibeacon_minor: Annotated[str | None, Field(description="query parameter 'ibeacon_minor'")] = None,
    eddystone_uid_namespace: Annotated[
        str | None, Field(description="query parameter 'eddystone_uid_namespace'")
    ] = None,
    eddystone_uid_instance: Annotated[str | None, Field(description="query parameter 'eddystone_uid_instance'")] = None,
    eddystone_url: Annotated[str | None, Field(description="query parameter 'eddystone_url'")] = None,
    ap_mac: Annotated[str | None, Field(description="query parameter 'ap_mac'")] = None,
    beam: Annotated[int | None, Field(description="query parameter 'beam'")] = None,
    rssi: Annotated[int | None, Field(description="query parameter 'rssi'")] = None,
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
        "/api/v1/orgs/{org_id}/stats/assets/search",
        path_params={"org_id": org_id},
        query_params={
            "site_id": site_id,
            "mac": mac,
            "device_name": device_name,
            "name": name,
            "map_id": map_id,
            "ibeacon_uuid": ibeacon_uuid,
            "ibeacon_major": ibeacon_major,
            "ibeacon_minor": ibeacon_minor,
            "eddystone_uid_namespace": eddystone_uid_namespace,
            "eddystone_uid_instance": eddystone_uid_instance,
            "eddystone_url": eddystone_url,
            "ap_mac": ap_mac,
            "beam": beam,
            "rssi": rssi,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
