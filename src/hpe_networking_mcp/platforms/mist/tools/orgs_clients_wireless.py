"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Clients - Wireless``
Operations in this file: 6
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
    name="mist_count_org_wireless_client_events",
    description="GET /api/v1/orgs/{org_id}/clients/events/count\n\ncountOrgWirelessClientEvents\n\nCount by Distinct Attributes of Client-Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_wireless_client_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
    ] = None,
    reason_code: Annotated[int | None, Field(description="For assoc/disassoc events")] = None,
    ssid: Annotated[str | None, Field(description="SSID Name")] = None,
    ap: Annotated[str | None, Field(description="AP MAC")] = None,
    proto: Annotated[Any | None, Field(description="a / b / g / n / ac / ax")] = None,
    band: Annotated[Any | None, Field(description="802.11 Band")] = None,
    wlan_id: Annotated[str | None, Field(description="WLAN ID")] = None,
    site_id: Annotated[str | None, Field(description="Site ID")] = None,
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
        "/api/v1/orgs/{org_id}/clients/events/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "type": type,
            "reason_code": reason_code,
            "ssid": ssid,
            "ap": ap,
            "proto": proto,
            "band": band,
            "wlan_id": wlan_id,
            "site_id": site_id,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_count_org_wireless_clients",
    description="GET /api/v1/orgs/{org_id}/clients/count\n\ncountOrgWirelessClients\n\nCount by Distinct Attributes of Org Wireless Clients",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_wireless_clients(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
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
    device: Annotated[str | None, Field(description="Device type, e.g. Mac, Nvidia, iPhone")] = None,
    os: Annotated[str | None, Field(description="OS, e.g. Sierra, Yosemite, Windows 10")] = None,
    model: Annotated[str | None, Field(description='Model, e.g. "MBP 15 late 2013", 6, 6s, "8+ GSM"')] = None,
    ap: Annotated[str | None, Field(description="AP mac where the client has connected to")] = None,
    vlan: Annotated[str | None, Field(description="VLAN")] = None,
    ssid: Annotated[str | None, Field(description="SSID")] = None,
    ip: Annotated[str | None, Field(description="query parameter 'ip'")] = None,
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
        "/api/v1/orgs/{org_id}/clients/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "mac": mac,
            "hostname": hostname,
            "device": device,
            "os": os,
            "model": model,
            "ap": ap,
            "vlan": vlan,
            "ssid": ssid,
            "ip": ip,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_count_org_wireless_clients_sessions",
    description="GET /api/v1/orgs/{org_id}/clients/sessions/count\n\ncountOrgWirelessClientsSessions\n\nCount by Distinct Attributes of Org Wireless Clients Sessions",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_wireless_clients_sessions(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    ap: Annotated[str | None, Field(description="AP MAC")] = None,
    band: Annotated[Any | None, Field(description="802.11 Band")] = None,
    client_family: Annotated[str | None, Field(description='E.g. "Mac", "iPhone", "Apple watch"')] = None,
    client_manufacture: Annotated[str | None, Field(description='E.g. "Apple"')] = None,
    client_model: Annotated[str | None, Field(description='E.g. "8+", "XS"')] = None,
    client_os: Annotated[str | None, Field(description='E.g. "Mojave", "Windows 10", "Linux"')] = None,
    ssid: Annotated[str | None, Field(description="SSID")] = None,
    wlan_id: Annotated[str | None, Field(description="WLAN_id")] = None,
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
        "/api/v1/orgs/{org_id}/clients/sessions/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "ap": ap,
            "band": band,
            "client_family": client_family,
            "client_manufacture": client_manufacture,
            "client_model": client_model,
            "client_os": client_os,
            "ssid": ssid,
            "wlan_id": wlan_id,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_wireless_client_events",
    description="GET /api/v1/orgs/{org_id}/clients/events/search\n\nsearchOrgWirelessClientEvents\n\nGet Org Clients Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_wireless_client_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
    ] = None,
    reason_code: Annotated[int | None, Field(description="For assoc/disassoc events")] = None,
    ssid: Annotated[str | None, Field(description="SSID Name")] = None,
    ap: Annotated[str | None, Field(description="AP MAC")] = None,
    key_mgmt: Annotated[
        Any | None, Field(description="Key Management Protocol, e.g. WPA2-PSK, WPA3-SAE, WPA2-Enterprise")
    ] = None,
    proto: Annotated[Any | None, Field(description="a / b / g / n / ac / ax")] = None,
    band: Annotated[Any | None, Field(description="802.11 Band")] = None,
    wlan_id: Annotated[str | None, Field(description="WLAN_id")] = None,
    nacrule_id: Annotated[str | None, Field(description="Nacrule_id")] = None,
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
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
        "/api/v1/orgs/{org_id}/clients/events/search",
        path_params={"org_id": org_id},
        query_params={
            "type": type,
            "reason_code": reason_code,
            "ssid": ssid,
            "ap": ap,
            "key_mgmt": key_mgmt,
            "proto": proto,
            "band": band,
            "wlan_id": wlan_id,
            "nacrule_id": nacrule_id,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "limit": limit,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_wireless_client_sessions",
    description="GET /api/v1/orgs/{org_id}/clients/sessions/search\n\nsearchOrgWirelessClientSessions\n\nSearch Org Wireless Clients Sessions",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_wireless_client_sessions(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ap: Annotated[str | None, Field(description="AP MAC")] = None,
    band: Annotated[Any | None, Field(description="802.11 Band")] = None,
    client_family: Annotated[str | None, Field(description='E.g. "Mac", "iPhone", "Apple watch"')] = None,
    client_manufacture: Annotated[str | None, Field(description='E.g. "Apple"')] = None,
    client_model: Annotated[str | None, Field(description='E.g. "8+", "XS"')] = None,
    client_username: Annotated[str | None, Field(description="Username")] = None,
    client_os: Annotated[str | None, Field(description='E.g. "Mojave", "Windows 10", "Linux"')] = None,
    ssid: Annotated[str | None, Field(description="SSID")] = None,
    wlan_id: Annotated[str | None, Field(description="WLAN_id")] = None,
    psk_id: Annotated[str | None, Field(description="PSK ID")] = None,
    psk_name: Annotated[str | None, Field(description="PSK Name")] = None,
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
        "/api/v1/orgs/{org_id}/clients/sessions/search",
        path_params={"org_id": org_id},
        query_params={
            "ap": ap,
            "band": band,
            "client_family": client_family,
            "client_manufacture": client_manufacture,
            "client_model": client_model,
            "client_username": client_username,
            "client_os": client_os,
            "ssid": ssid,
            "wlan_id": wlan_id,
            "psk_id": psk_id,
            "psk_name": psk_name,
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
    name="mist_search_org_wireless_clients",
    description="GET /api/v1/orgs/{org_id}/clients/search\n\nsearchOrgWirelessClients\n\nSearch Org Wireless Clients",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_wireless_clients(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[str | None, Field(description="Site ID")] = None,
    ap: Annotated[str | None, Field(description="AP MAC address where the client has connected to")] = None,
    band: Annotated[
        str | None, Field(description="Comma separated list of Radio band (e.g. `24,5`). enum: `24`, `5`, `6`")
    ] = None,
    device: Annotated[
        str | None, Field(description="Comma separated list of Device type (e.g. `Mac,iPhone`). Case sensitive")
    ] = None,
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
    mac: Annotated[
        str | None,
        Field(
            description="Partial / full Client MAC Address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported"
        ),
    ] = None,
    model: Annotated[
        str | None,
        Field(
            description='Only available for clients running the Marvis Client app, model, e.g. "MBP 15 late 2013", 6, 6s, "8+ GSM"'
        ),
    ] = None,
    os: Annotated[
        str | None,
        Field(
            description="Only available for clients running the Marvis Client app, os, e.g. Sierra, Yosemite, Windows 10"
        ),
    ] = None,
    psk_id: Annotated[str | None, Field(description="PSK ID")] = None,
    psk_name: Annotated[
        str | None, Field(description="Only available for clients using PPSK authentication, the Name of the PSK")
    ] = None,
    ssid: Annotated[str | None, Field(description="SSID")] = None,
    text: Annotated[
        str | None,
        Field(
            description="Partial / full MAC address, hostname, username, psk_name or ip. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `everest*` and `*rest*` match `my-everest-client`). Suffix-only wildcards (e.g. `*everest`) are no..."
        ),
    ] = None,
    username: Annotated[
        str | None,
        Field(
            description="Partial / full username. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `johndoe*` and `*mycorp*` match `johndoe@mycorp.com`). Suffix-only wildcards (e.g. `*mycorp.com`) are not supported"
        ),
    ] = None,
    vlan: Annotated[str | None, Field(description="VLAN")] = None,
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
        "/api/v1/orgs/{org_id}/clients/search",
        path_params={"org_id": org_id},
        query_params={
            "site_id": site_id,
            "ap": ap,
            "band": band,
            "device": device,
            "hostname": hostname,
            "ip": ip,
            "mac": mac,
            "model": model,
            "os": os,
            "psk_id": psk_id,
            "psk_name": psk_name,
            "ssid": ssid,
            "text": text,
            "username": username,
            "vlan": vlan,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
