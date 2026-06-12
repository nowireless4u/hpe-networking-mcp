"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Stats - Discovered Switches``
Operations in this file: 4
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
    name="mist_count_site_discovered_switches",
    description="GET /api/v1/sites/{site_id}/stats/discovered_switches/count\n\ncountSiteDiscoveredSwitches\n\nCount Discovered Switches",
    capability=Capability.READ,
)
async def mist_count_site_discovered_switches(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `mgmt_addr`, `model`, `system_name`, `version`"
        ),
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
        "/api/v1/sites/{site_id}/stats/discovered_switches/count",
        path_params={"site_id": site_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_discovered_switches_metrics",
    description="GET /api/v1/sites/{site_id}/stats/discovered_switches/metrics\n\nlistSiteDiscoveredSwitchesMetrics\n\nDiscovered switches related metrics, lists related switch system names & details if not compliant",
    capability=Capability.READ,
)
async def mist_list_site_discovered_switches_metrics(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    threshold: Annotated[str | None, Field(description="Configurable # ap per switch threshold, default 12")] = None,
    system_name: Annotated[str | None, Field(description="System name for switch level metrics, optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/discovered_switches/metrics",
        path_params={"site_id": site_id},
        query_params={"threshold": threshold, "system_name": system_name},
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_discovered_switches",
    description="GET /api/v1/sites/{site_id}/stats/discovered_switches/search\n\nsearchSiteDiscoveredSwitches\n\nSearch Discovered Switches",
    capability=Capability.READ,
)
async def mist_search_site_discovered_switches(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    adopted: Annotated[bool | None, Field(description="Filter results by whether the device is adopted")] = None,
    system_name: Annotated[str | None, Field(description="Filter discovered switch results by system name")] = None,
    hostname: Annotated[str | None, Field(description="Filter results by hostname")] = None,
    vendor: Annotated[str | None, Field(description="Filter results by vendor")] = None,
    model: Annotated[str | None, Field(description="Filter results by device model")] = None,
    version: Annotated[str | None, Field(description="Filter results by software version")] = None,
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
        "/api/v1/sites/{site_id}/stats/discovered_switches/search",
        path_params={"site_id": site_id},
        query_params={
            "adopted": adopted,
            "system_name": system_name,
            "hostname": hostname,
            "vendor": vendor,
            "model": model,
            "version": version,
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
    name="mist_search_site_discovered_switches_metrics",
    description="GET /api/v1/sites/{site_id}/stats/discovered_switch_metrics/search\n\nsearchSiteDiscoveredSwitchesMetrics\n\nSearch Discovered Switch Metrics",
    capability=Capability.READ,
)
async def mist_search_site_discovered_switches_metrics(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any | None, Field(description="Filter results by scope. enum: `site`, `switch`")] = None,
    type: Annotated[
        Any | None,
        Field(
            description="Metric type. enum: `inactive_wired_vlans`, `poe_compliance`, `switch_ap_affinity`, `version_compliance`"
        ),
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
        "/api/v1/sites/{site_id}/stats/discovered_switch_metrics/search",
        path_params={"site_id": site_id},
        query_params={
            "scope": scope,
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
