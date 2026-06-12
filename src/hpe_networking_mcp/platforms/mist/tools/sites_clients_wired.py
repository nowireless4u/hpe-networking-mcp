"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Clients - Wired``
Operations in this file: 2
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
    name="mist_count_site_wired_clients",
    description="GET /api/v1/sites/{site_id}/wired_clients/count\n\ncountSiteWiredClients\n\nCount wired clients for a site, optionally grouped by the `distinct` field and filtered by MAC address, switch port, VLAN, and time range. Use [Count Org Wired Clients](/#operations/countOrgWiredClients) to count wired clients across the organization.",
    capability=Capability.READ,
)
async def mist_count_site_wired_clients(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[
        Any | None, Field(description="Field used to group this count response. enum: `mac`, `port_id`, `vlan`")
    ] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    device_mac: Annotated[str | None, Field(description="Filter results by device MAC address")] = None,
    port_id: Annotated[str | None, Field(description="Filter results by port identifier")] = None,
    vlan: Annotated[str | None, Field(description="Filter results by VLAN ID")] = None,
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
    description="GET /api/v1/sites/{site_id}/wired_clients/search\n\nsearchSiteWiredClients\n\nSearch wired clients for a site with filters for device MAC address, client MAC address, IP address, switch port, VLAN, manufacturer, DHCP attributes, NAC rule, and time range. Use [Search Org Wired Clients](/#operations/searchOrgWiredClients) to search wired clients across the organization.",
    capability=Capability.READ,
)
async def mist_search_site_wired_clients(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_mac: Annotated[str | None, Field(description="Filter results by device MAC address")] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    ip: Annotated[str | None, Field(description="Filter results by IP address")] = None,
    port_id: Annotated[str | None, Field(description="Filter results by port identifier")] = None,
    source: Annotated[
        Any | None, Field(description="Filter results by client learning source. enum: `lldp`, `mac`")
    ] = None,
    vlan: Annotated[str | None, Field(description="Filter results by VLAN ID")] = None,
    manufacture: Annotated[str | None, Field(description="Filter results by manufacturer")] = None,
    text: Annotated[str | None, Field(description="Single entry of hostname/mac")] = None,
    nacrule_id: Annotated[str | None, Field(description="Filter results by NAC rule identifier")] = None,
    dhcp_hostname: Annotated[str | None, Field(description="Filter results by DHCP hostname")] = None,
    dhcp_fqdn: Annotated[str | None, Field(description="Filter results by DHCP FQDN")] = None,
    dhcp_client_identifier: Annotated[str | None, Field(description="Filter results by DHCP client identifier")] = None,
    dhcp_vendor_class_identifier: Annotated[str | None, Field(description="DHCP Vendor Class Identifier")] = None,
    dhcp_request_params: Annotated[str | None, Field(description="Filter results by DHCP request parameters")] = None,
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
