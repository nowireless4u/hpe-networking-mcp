"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Clients - Wired``
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
    name="mist_count_org_wired_clients",
    description="GET /api/v1/orgs/{org_id}/wired_clients/count\n\ncountOrgWiredClients\n\nCount by Distinct Attributes of Clients\n\nNote: For list of available `type` values, please refer to [List Client Events Definitions](/#operations/listClientEventsDefinitions)",
    capability=Capability.READ,
)
async def mist_count_org_wired_clients(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `device_mac`, `mac`, `port_id`, `site_id`, `type`, `vlan`"
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
        "/api/v1/orgs/{org_id}/wired_clients/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_wired_clients",
    description="GET /api/v1/orgs/{org_id}/wired_clients/search\n\nsearchOrgWiredClients\n\nSearch for Wired Clients in org\n\nNote: For list of available `type` values, please refer to [List Client Events Definitions](/#operations/listClientEventsDefinitions)",
    capability=Capability.READ,
)
async def mist_search_org_wired_clients(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    auth_state: Annotated[str | None, Field(description="Filter results by auth state")] = None,
    auth_method: Annotated[
        str | None,
        Field(description="Filter results by authentication method. Accepts multiple comma-separated values."),
    ] = None,
    source: Annotated[
        str | None,
        Field(
            description="Filter results by client learning source. enum: `lldp`, `mac`. Accepts multiple comma-separated values."
        ),
    ] = None,
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    device_mac: Annotated[
        str | None,
        Field(
            description="Filter results by one or more gateway or switch MAC addresses where the client has connected. Supports comma-separated values"
        ),
    ] = None,
    mac: Annotated[
        str | None,
        Field(
            description="Partial / full Client MAC address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported. Accepts multiple com..."
        ),
    ] = None,
    port_id: Annotated[
        str | None,
        Field(
            description="Filter results by one or more port identifiers where the client has connected. Supports comma-separated values"
        ),
    ] = None,
    vlan: Annotated[
        str | None, Field(description="Filter results by one or more VLAN IDs. Supports comma-separated values")
    ] = None,
    ip: Annotated[
        str | None, Field(description="Filter results by one or more IPv4 addresses. Supports comma-separated values")
    ] = None,
    manufacture: Annotated[
        str | None, Field(description="Filter results by manufacturer. Accepts multiple comma-separated values.")
    ] = None,
    text: Annotated[
        str | None,
        Field(
            description="Partial / full Client MAC address, hostname or username. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*ddeeff`) are not supported"
        ),
    ] = None,
    nacrule_id: Annotated[str | None, Field(description="Filter results by NAC rule identifier")] = None,
    dhcp_hostname: Annotated[
        str | None, Field(description="Filter results by DHCP hostname. Accepts multiple comma-separated values.")
    ] = None,
    dhcp_fqdn: Annotated[str | None, Field(description="Filter results by DHCP FQDN")] = None,
    dhcp_client_identifier: Annotated[
        str | None,
        Field(description="Filter results by DHCP client identifier. Accepts multiple comma-separated values."),
    ] = None,
    dhcp_vendor_class_identifier: Annotated[
        str | None, Field(description="DHCP Vendor Class Identifier. Accepts multiple comma-separated values.")
    ] = None,
    dhcp_request_params: Annotated[
        str | None,
        Field(description="Filter results by DHCP request parameters. Accepts multiple comma-separated values."),
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
        "/api/v1/orgs/{org_id}/wired_clients/search",
        path_params={"org_id": org_id},
        query_params={
            "auth_state": auth_state,
            "auth_method": auth_method,
            "source": source,
            "site_id": site_id,
            "device_mac": device_mac,
            "mac": mac,
            "port_id": port_id,
            "vlan": vlan,
            "ip": ip,
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
