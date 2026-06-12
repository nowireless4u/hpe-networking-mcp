"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Stats - Assets``
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
    name="mist_count_org_assets_by_distance_field",
    description="GET /api/v1/orgs/{org_id}/stats/assets/count\n\ncountOrgAssetsByDistanceField\n\nCount organization asset statistics grouped by a distinct asset attribute, such as MAC address, site, map, iBeacon UUID, iBeacon major, or iBeacon minor.",
    capability=Capability.READ,
)
async def mist_count_org_assets_by_distance_field(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `ibeacon_major`, `ibeacon_minor`, `ibeacon_uuid`, `mac`, `map_id`, `site_id`"
        ),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
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
    description="GET /api/v1/orgs/{org_id}/stats/assets\n\nlistOrgAssetsStats\n\nList BLE asset location and advertisement statistics for the organization over an optional time window, including map coordinates, RSSI, zones, and iBeacon or Eddystone fields.",
    capability=Capability.READ,
)
async def mist_list_org_assets_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
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
        "/api/v1/orgs/{org_id}/stats/assets",
        path_params={"org_id": org_id},
        query_params={"start": start, "end": end, "duration": duration, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_assets",
    description="GET /api/v1/orgs/{org_id}/stats/assets/search\n\nsearchOrgAssets\n\nSearch BLE asset statistics with filters for site, MAC address, asset name, map, iBeacon or Eddystone identifiers, reporting AP MAC address, RSSI, beam, and time range. Supports pagination and sorting.",
    capability=Capability.READ,
)
async def mist_search_org_assets(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    mac: Annotated[
        str | None, Field(description="Filter results by MAC address. Accepts multiple comma-separated values.")
    ] = None,
    device_name: Annotated[str | None, Field(description="Filter asset results by reporting device name")] = None,
    name: Annotated[
        str | None, Field(description="Filter results by name. Accepts multiple comma-separated values.")
    ] = None,
    map_id: Annotated[str | None, Field(description="Filter results by map identifier")] = None,
    ibeacon_uuid: Annotated[
        str | None, Field(description="Filter asset results by iBeacon UUID. Accepts multiple comma-separated values.")
    ] = None,
    ibeacon_major: Annotated[
        str | None,
        Field(description="Filter asset results by iBeacon major value. Accepts multiple comma-separated values."),
    ] = None,
    ibeacon_minor: Annotated[
        str | None,
        Field(description="Filter asset results by iBeacon minor value. Accepts multiple comma-separated values."),
    ] = None,
    eddystone_uid_namespace: Annotated[
        str | None, Field(description="Filter asset results by Eddystone UID namespace")
    ] = None,
    eddystone_uid_instance: Annotated[
        str | None, Field(description="Filter asset results by Eddystone UID instance")
    ] = None,
    eddystone_url: Annotated[str | None, Field(description="Filter asset results by Eddystone URL")] = None,
    ap_mac: Annotated[
        str | None,
        Field(description="Filter asset results by reporting AP MAC address. Accepts multiple comma-separated values."),
    ] = None,
    beam: Annotated[
        int | None,
        Field(description="Filter asset results by beam value. Accepts multiple comma-separated integer values."),
    ] = None,
    rssi: Annotated[
        int | None,
        Field(description="Filter asset results by RSSI value. Accepts multiple comma-separated integer values."),
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
