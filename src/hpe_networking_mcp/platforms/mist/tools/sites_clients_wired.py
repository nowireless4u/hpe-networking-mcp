"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Clients - Wired``
Operations in this file: 2
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
    name="mist_count_site_wired_clients",
    description="GET /api/v1/sites/{site_id}/wired_clients/count\n\ncountSiteWiredClients\n\nCount by Distinct Attributes of Clients",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_wired_clients(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    mac: Annotated[str | None, Field(description="Client mac")] = None,
    device_mac: Annotated[str | None, Field(description="Device mac")] = None,
    port_id: Annotated[str | None, Field(description="Port id")] = None,
    vlan: Annotated[str | None, Field(description="VLAN")] = None,
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
        "/api/v1/sites/{site_id}/wired_clients/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "mac": mac,
            "device_mac": device_mac,
            "port_id": port_id,
            "vlan": vlan,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_wired_clients",
    description="GET /api/v1/sites/{site_id}/wired_clients/search\n\nsearchSiteWiredClients\n\nSearch Wired Clients",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_wired_clients(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_mac: Annotated[str | None, Field(description="Device mac")] = None,
    mac: Annotated[str | None, Field(description="Client mac")] = None,
    ip: Annotated[str | None, Field(description="Client ip")] = None,
    port_id: Annotated[str | None, Field(description="Port id")] = None,
    source: Annotated[Any | None, Field(description="source from where the client was learned (lldp, mac)")] = None,
    vlan: Annotated[str | None, Field(description="VLAN")] = None,
    manufacture: Annotated[str | None, Field(description="Manufacture")] = None,
    text: Annotated[str | None, Field(description="Single entry of hostname/mac")] = None,
    nacrule_id: Annotated[str | None, Field(description="nacrule_id")] = None,
    dhcp_hostname: Annotated[str | None, Field(description="DHCP Hostname")] = None,
    dhcp_fqdn: Annotated[str | None, Field(description="DHCP FQDN")] = None,
    dhcp_client_identifier: Annotated[str | None, Field(description="DHCP Client Identifier")] = None,
    dhcp_vendor_class_identifier: Annotated[str | None, Field(description="DHCP Vendor Class Identifier")] = None,
    dhcp_request_params: Annotated[str | None, Field(description="DHCP Request Parameters")] = None,
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
        "/api/v1/sites/{site_id}/wired_clients/search",
        path_params={"site_id": site_id},
        query_params={
            "device_mac": device_mac,
            "mac": mac,
            "ip": ip,
            "port_id": port_id,
            "source": source,
            "vlan": vlan,
            "manufacture": manufacture,
            "text": text,
            "nacrule_id": nacrule_id,
            "dhcp_hostname": dhcp_hostname,
            "dhcp_fqdn": dhcp_fqdn,
            "dhcp_client_identifier": dhcp_client_identifier,
            "dhcp_vendor_class_identifier": dhcp_vendor_class_identifier,
            "dhcp_request_params": dhcp_request_params,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
