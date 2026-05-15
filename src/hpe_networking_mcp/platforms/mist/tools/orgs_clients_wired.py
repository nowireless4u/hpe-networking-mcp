"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Clients - Wired``
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
    name="mist_count_org_wired_clients",
    description="GET /api/v1/orgs/{org_id}/wired_clients/count\n\ncountOrgWiredClients\n\nCount by Distinct Attributes of Clients\n\nNote: For list of available `type` values, please refer to [List Client Events Definitions](/#operations/listClientEventsDefinitions)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_wired_clients(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
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
        "/api/v1/orgs/{org_id}/wired_clients/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_wired_clients",
    description="GET /api/v1/orgs/{org_id}/wired_clients/search\n\nsearchOrgWiredClients\n\nSearch for Wired Clients in org\n\nNote: For list of available `type` values, please refer to [List Client Events Definitions](/#operations/listClientEventsDefinitions)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_wired_clients(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    auth_state: Annotated[str | None, Field(description="Authentication state")] = None,
    auth_method: Annotated[str | None, Field(description="Authentication method")] = None,
    source: Annotated[Any | None, Field(description="source from where the client was learned (lldp, mac)")] = None,
    site_id: Annotated[str | None, Field(description="Site ID")] = None,
    device_mac: Annotated[
        str | None, Field(description="Device mac (Gateway/Switch) where the client has connected to")
    ] = None,
    mac: Annotated[
        str | None,
        Field(
            description="Partial / full Client MAC Address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported"
        ),
    ] = None,
    port_id: Annotated[str | None, Field(description="Port id where the client has connected to")] = None,
    vlan: Annotated[int | None, Field(description="VLAN")] = None,
    ip: Annotated[str | None, Field(description="query parameter 'ip'")] = None,
    manufacture: Annotated[str | None, Field(description="Client manufacturer")] = None,
    text: Annotated[
        str | None,
        Field(
            description="Partial / full Client MAC Address, hostname or username. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*ddeeff`) are not supported"
        ),
    ] = None,
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
