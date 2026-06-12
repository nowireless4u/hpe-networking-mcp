"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Clients - Wireless``
Operations in this file: 6
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
    name="mist_count_org_wireless_client_events",
    description="GET /api/v1/orgs/{org_id}/clients/events/count\n\ncountOrgWirelessClientEvents\n\nCount wireless client event records across the organization, optionally grouped by event attributes and filtered by event type, WLAN, radio, site, and time range.",
    capability=Capability.READ,
)
async def mist_count_org_wireless_client_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `band`, `channel`, `proto`, `ssid`, `type`, `wlan_id`"
        ),
    ] = None,
    type: Annotated[
        str | None,
        Field(
            description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions). Accepts multiple comma-separated values."
        ),
    ] = None,
    reason_code: Annotated[
        int | None, Field(description="Reason code filter for association and disassociation events")
    ] = None,
    ssid: Annotated[str | None, Field(description="Filter results by SSID")] = None,
    ap: Annotated[str | None, Field(description="Filter results by AP MAC address")] = None,
    proto: Annotated[
        Any | None,
        Field(description="802.11 protocol used to filter results. enum: `a`, `ac`, `ax`, `b`, `be`, `g`, `n`"),
    ] = None,
    band: Annotated[
        Any | None,
        Field(
            description="802.11 band used to filter radio results. enum: `24`, `5`, `5-dedicated`, `5-selectable`, `6`, `6-dedicated`, `6-selectable`"
        ),
    ] = None,
    wlan_id: Annotated[str | None, Field(description="Filter results by WLAN identifier")] = None,
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
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
    description="GET /api/v1/orgs/{org_id}/clients/count\n\ncountOrgWirelessClients\n\nCount wireless client records across the organization, optionally grouped by `distinct` and filtered by client identity, AP, SSID, VLAN, IP, and time range.",
    capability=Capability.READ,
)
async def mist_count_org_wireless_clients(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `ap`, `device`, `hostname`, `ip`, `mac`, `model`, `os`, `ssid`, `vlan`"
        ),
    ] = None,
    mac: Annotated[
        str | None,
        Field(
            description="Partial / full Client MAC address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported. Accepts multiple com..."
        ),
    ] = None,
    hostname: Annotated[
        str | None,
        Field(
            description="Partial / full Client hostname. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `everest*` and `*rest*` match `my-everest-client`). Suffix-only wildcards (e.g. `*everest`) are not supported. Accepts multiple co..."
        ),
    ] = None,
    device: Annotated[str | None, Field(description="Filter results by device type")] = None,
    os: Annotated[str | None, Field(description="Filter results by operating system")] = None,
    model: Annotated[str | None, Field(description="Filter results by device model")] = None,
    ap: Annotated[str | None, Field(description="Filter results by AP MAC address")] = None,
    vlan: Annotated[str | None, Field(description="Filter results by VLAN ID")] = None,
    ssid: Annotated[str | None, Field(description="Filter results by SSID")] = None,
    ip: Annotated[str | None, Field(description="Filter results by IPv4 address")] = None,
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
    description="GET /api/v1/orgs/{org_id}/clients/sessions/count\n\ncountOrgWirelessClientsSessions\n\nCount historical wireless client sessions across the organization, optionally grouped by `distinct` and filtered by AP, band, client attributes, SSID, WLAN, and time range.",
    capability=Capability.READ,
)
async def mist_count_org_wireless_clients_sessions(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `ap`, `device`, `hostname`, `ip`, `model`, `os`, `ssid`, `vlan`"
        ),
    ] = None,
    ap: Annotated[str | None, Field(description="Filter results by AP MAC address")] = None,
    band: Annotated[
        Any | None,
        Field(
            description="802.11 band used to filter radio results. enum: `24`, `5`, `5-dedicated`, `5-selectable`, `6`, `6-dedicated`, `6-selectable`"
        ),
    ] = None,
    client_family: Annotated[str | None, Field(description='E.g. "Mac", "iPhone", "Apple watch"')] = None,
    client_manufacture: Annotated[
        str | None, Field(description='Filter results by client manufacturer, e.g. "Apple"')
    ] = None,
    client_model: Annotated[str | None, Field(description='Filter results by client model, e.g. "8+", "XS"')] = None,
    client_os: Annotated[str | None, Field(description='E.g. "Mojave", "Windows 10", "Linux"')] = None,
    ssid: Annotated[str | None, Field(description="Filter results by SSID")] = None,
    wlan_id: Annotated[str | None, Field(description="Filter results by WLAN identifier")] = None,
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
    description="GET /api/v1/orgs/{org_id}/clients/events/search\n\nsearchOrgWirelessClientEvents\n\nSearch wireless client event records across the organization with filters for event type, reason code, SSID, AP, key management, protocol, band, WLAN, NAC rule, and time range.",
    capability=Capability.READ,
)
async def mist_search_org_wireless_client_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[
        str | None,
        Field(
            description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions). Accepts multiple comma-separated values."
        ),
    ] = None,
    reason_code: Annotated[
        str | None,
        Field(
            description="Reason code filter for association and disassociation events. Accepts multiple comma-separated integer values."
        ),
    ] = None,
    ssid: Annotated[
        str | None, Field(description="Filter results by SSID. Accepts multiple comma-separated values.")
    ] = None,
    ap: Annotated[
        str | None, Field(description="Filter results by AP MAC address. Accepts multiple comma-separated values.")
    ] = None,
    key_mgmt: Annotated[
        str | None,
        Field(
            description="Key management protocol used to filter client events. enum: `WPA2-PSK`, `WPA2-PSK/CCMP`, `WPA2-PSK-FT`, `WPA2-PSK-SHA256`, `WPA3-EAP-SHA256`, `WPA3-EAP-SHA256/CCMP`, `WPA3-EAP-FT/GCMP256`, `WPA3-SAE-FT`, `WPA3-SAE-PSK`. Accepts multiple ..."
        ),
    ] = None,
    proto: Annotated[
        str | None,
        Field(
            description="802.11 protocol used to filter results. enum: `a`, `ac`, `ax`, `b`, `be`, `g`, `n`. Accepts multiple comma-separated values."
        ),
    ] = None,
    band: Annotated[
        str | None,
        Field(
            description="802.11 band used to filter radio results. enum: `24`, `5`, `5-dedicated`, `5-selectable`, `6`, `6-dedicated`, `6-selectable`. Accepts multiple comma-separated values."
        ),
    ] = None,
    wlan_id: Annotated[str | None, Field(description="Filter results by WLAN identifier")] = None,
    nacrule_id: Annotated[
        str | None, Field(description="Filter results by NAC rule identifier. Accepts multiple comma-separated values.")
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
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
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
    description="GET /api/v1/orgs/{org_id}/clients/sessions/search\n\nsearchOrgWirelessClientSessions\n\nSearch historical wireless client sessions across the organization with filters for AP, band, client family, manufacturer, model, OS, username, SSID, WLAN, PPSK, and time range.",
    capability=Capability.READ,
)
async def mist_search_org_wireless_client_sessions(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ap: Annotated[str | None, Field(description="Filter results by AP MAC address")] = None,
    band: Annotated[
        str | None,
        Field(
            description="802.11 band used to filter radio results. enum: `24`, `5`, `5-dedicated`, `5-selectable`, `6`, `6-dedicated`, `6-selectable`. Accepts multiple comma-separated values."
        ),
    ] = None,
    client_family: Annotated[
        str | None, Field(description='E.g. "Mac", "iPhone", "Apple watch". Accepts multiple comma-separated values.')
    ] = None,
    client_manufacture: Annotated[
        str | None,
        Field(
            description='Filter results by client manufacturer, e.g. "Apple". Accepts multiple comma-separated values.'
        ),
    ] = None,
    client_model: Annotated[
        str | None,
        Field(description='Filter results by client model, e.g. "8+", "XS". Accepts multiple comma-separated values.'),
    ] = None,
    client_username: Annotated[
        str | None, Field(description="Filter results by client username. Accepts multiple comma-separated values.")
    ] = None,
    client_os: Annotated[
        str | None, Field(description='E.g. "Mojave", "Windows 10", "Linux". Accepts multiple comma-separated values.')
    ] = None,
    ssid: Annotated[
        str | None, Field(description="Filter results by SSID. Accepts multiple comma-separated values.")
    ] = None,
    wlan_id: Annotated[str | None, Field(description="Filter results by WLAN identifier")] = None,
    psk_id: Annotated[str | None, Field(description="PSK identifier used to filter the results")] = None,
    psk_name: Annotated[
        str | None, Field(description="Filter results by PSK name. Accepts multiple comma-separated values.")
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
    description="GET /api/v1/orgs/{org_id}/clients/search\n\nsearchOrgWirelessClients\n\nSearch wireless client records across the organization with filters for site, AP, band, device identity, hostname, IP, MAC address, username, SSID, PPSK, VLAN, and time range.",
    capability=Capability.READ,
)
async def mist_search_org_wireless_clients(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    ap: Annotated[str | None, Field(description="Filter results by AP MAC address")] = None,
    band: Annotated[
        str | None, Field(description="Comma separated list of Radio band (e.g. `24,5`). enum: `24`, `5`, `6`")
    ] = None,
    device: Annotated[
        str | None, Field(description="Comma separated list of Device type (e.g. `Mac,iPhone`). Case sensitive")
    ] = None,
    hostname: Annotated[
        str | None,
        Field(
            description="Partial / full Client hostname. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `everest*` and `*rest*` match `my-everest-client`). Suffix-only wildcards (e.g. `*everest`) are not supported. Accepts multiple co..."
        ),
    ] = None,
    ip: Annotated[
        str | None,
        Field(
            description="Partial / full Client IP address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `10.100.10.*` and `*100.10.*` match `10.100.10.54`). Suffix-only wildcards (e.g. `*.54`) are not supported. Accepts multiple com..."
        ),
    ] = None,
    mac: Annotated[
        str | None,
        Field(
            description="Partial / full Client MAC address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported. Accepts multiple com..."
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
    psk_id: Annotated[str | None, Field(description="PSK identifier used to filter the results")] = None,
    psk_name: Annotated[
        str | None, Field(description="Only available for clients using PPSK authentication, the Name of the PSK")
    ] = None,
    ssid: Annotated[str | None, Field(description="Filter results by SSID")] = None,
    text: Annotated[
        str | None,
        Field(
            description="Partial / full MAC address, hostname, username, psk_name or ip. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `everest*` and `*rest*` match `my-everest-client`). Suffix-only wildcards (e.g. `*everest`) are no..."
        ),
    ] = None,
    username: Annotated[
        str | None,
        Field(
            description="Partial / full username. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `johndoe*` and `*mycorp*` match `johndoe@mycorp.com`). Suffix-only wildcards (e.g. `*mycorp.com`) are not supported. Accepts multiple com..."
        ),
    ] = None,
    vlan: Annotated[str | None, Field(description="Filter results by VLAN ID")] = None,
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
