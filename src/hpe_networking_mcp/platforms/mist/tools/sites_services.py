"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Services``
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
    name="mist_count_site_service_path_events",
    description="GET /api/v1/sites/{site_id}/services/events/count\n\ncountSiteServicePathEvents\n\nCount by Distinct Attributes of Service Path Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_service_path_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    type: Annotated[str | None, Field(description="Event type, e.g. GW_SERVICE_PATH_DOWN")] = None,
    text: Annotated[
        str | None, Field(description="Description of the event including the reason it is triggered")
    ] = None,
    vpn_name: Annotated[str | None, Field(description="Peer name")] = None,
    vpn_path: Annotated[str | None, Field(description="Peer path name")] = None,
    policy: Annotated[str | None, Field(description="Service policy associated with that specific path")] = None,
    port_id: Annotated[str | None, Field(description="Network interface")] = None,
    model: Annotated[str | None, Field(description="Device model")] = None,
    version: Annotated[str | None, Field(description="Device firmware version")] = None,
    timestamp: Annotated[float | None, Field(description="Start time, in epoch")] = None,
    mac: Annotated[str | None, Field(description="MAC address")] = None,
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
        "/api/v1/sites/{site_id}/services/events/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "type": type,
            "text": text,
            "vpn_name": vpn_name,
            "vpn_path": vpn_path,
            "policy": policy,
            "port_id": port_id,
            "model": model,
            "version": version,
            "timestamp": timestamp,
            "mac": mac,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_services_derived",
    description="GET /api/v1/sites/{site_id}/services/derived\n\nlistSiteServicesDerived\n\nGet the list of derived Services for a Site",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_services_derived(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    resolve: Annotated[bool, Field(description="Whether resolve the site variables")] = False,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/services/derived",
        path_params={"site_id": site_id},
        query_params={"resolve": resolve},
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_service_path_events",
    description="GET /api/v1/sites/{site_id}/services/events/search\n\nsearchSiteServicePathEvents\n\nSearch Service Path Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_service_path_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[str | None, Field(description="Event type, e.g. GW_SERVICE_PATH_DOWN")] = None,
    text: Annotated[
        str | None, Field(description="Description of the event including the reason it is triggered")
    ] = None,
    peer_port_id: Annotated[str | None, Field(description="Port ID of the peer gateway")] = None,
    peer_mac: Annotated[str | None, Field(description="MAC address of the peer gateway")] = None,
    vpn_name: Annotated[str | None, Field(description="Peer name")] = None,
    vpn_path: Annotated[str | None, Field(description="Peer path name")] = None,
    policy: Annotated[str | None, Field(description="Service policy associated with that specific path")] = None,
    port_id: Annotated[str | None, Field(description="Network interface")] = None,
    model: Annotated[str | None, Field(description="Device model")] = None,
    version: Annotated[str | None, Field(description="Device firmware version")] = None,
    timestamp: Annotated[float | None, Field(description="Start time, in epoch")] = None,
    mac: Annotated[str | None, Field(description="MAC address")] = None,
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
        "/api/v1/sites/{site_id}/services/events/search",
        path_params={"site_id": site_id},
        query_params={
            "type": type,
            "text": text,
            "peer_port_id": peer_port_id,
            "peer_mac": peer_mac,
            "vpn_name": vpn_name,
            "vpn_path": vpn_path,
            "policy": policy,
            "port_id": port_id,
            "model": model,
            "version": version,
            "timestamp": timestamp,
            "mac": mac,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
