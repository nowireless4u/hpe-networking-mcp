"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Clients - Wan``
Operations in this file: 4
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
    name="mist_count_site_wan_client_events",
    description="GET /api/v1/sites/{site_id}/wan_client/events/count\n\ncountSiteWanClientEvents\n\nCount by Distinct Attributes of Site WAN Client-Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_wan_client_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
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
        "/api/v1/sites/{site_id}/wan_client/events/count",
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
    name="mist_count_site_wan_clients",
    description="GET /api/v1/sites/{site_id}/wan_clients/count\n\ncountSiteWanClients\n\nCount by Distinct Attributes of Site WAN Clients",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_wan_clients(
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
        "/api/v1/sites/{site_id}/wan_clients/count",
        path_params={"site_id": site_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_wan_client_events",
    description="GET /api/v1/sites/{site_id}/wan_clients/events/search\n\nsearchSiteWanClientEvents\n\nSearch Site WAN Client Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_wan_client_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
    ] = None,
    mac: Annotated[
        str | None,
        Field(
            description="Partial / full Client MAC Address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported"
        ),
    ] = None,
    hostname: Annotated[
        str | None,
        Field(
            description="Partial / full Client hostname. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `everest*` and `*rest*` match `my-everest-client`). Suffix-only wildcards (e.g. `*everest`) are not supported"
        ),
    ] = None,
    ip: Annotated[str | None, Field(description="Client IP")] = None,
    mfg: Annotated[str | None, Field(description="Manufacture")] = None,
    nacrule_id: Annotated[str | None, Field(description="nacrule_id")] = None,
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
        "/api/v1/sites/{site_id}/wan_clients/events/search",
        path_params={"site_id": site_id},
        query_params={
            "type": type,
            "mac": mac,
            "hostname": hostname,
            "ip": ip,
            "mfg": mfg,
            "nacrule_id": nacrule_id,
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
    name="mist_search_site_wan_clients",
    description="GET /api/v1/sites/{site_id}/wan_clients/search\n\nsearchSiteWanClients\n\nSearch Site WAN Clients",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_wan_clients(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    hostname: Annotated[
        str | None,
        Field(
            description="Partial / full Client hostname. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `everest*` and `*rest*` match `my-everest-client`). Suffix-only wildcards (e.g. `*everest`) are not supported"
        ),
    ] = None,
    ip: Annotated[
        str | None,
        Field(
            description="Partial / full Client IP Address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `10.100.10.*` and `*100.10.*` match `10.100.10.54`). Suffix-only wildcards (e.g. `*.54`) are not supported"
        ),
    ] = None,
    ip_src: Annotated[str | None, Field(description="IP source")] = None,
    mac: Annotated[str | None, Field(description="Client MAC Address.")] = None,
    mfg: Annotated[str | None, Field(description="Manufacture")] = None,
    network: Annotated[
        str | None,
        Field(
            description="Partial / full Name of the network the client is/was connected to. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `my-corp*` and `*corp*` match `my-corp-network`). Suffix-only wildcards (e.g. `*corp`) are not ..."
        ),
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
        "/api/v1/sites/{site_id}/wan_clients/search",
        path_params={"site_id": site_id},
        query_params={
            "hostname": hostname,
            "ip": ip,
            "ip_src": ip_src,
            "mac": mac,
            "mfg": mfg,
            "network": network,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
