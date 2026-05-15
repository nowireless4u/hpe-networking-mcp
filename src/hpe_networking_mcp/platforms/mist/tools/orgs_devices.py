"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Devices``
Operations in this file: 10
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
    name="mist_count_org_device_events",
    description="GET /api/v1/orgs/{org_id}/devices/events/count\n\ncountOrgDeviceEvents\n\nCount by Distinct Attributes of Org Devices Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_device_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    site_id: Annotated[str | None, Field(description="Site id")] = None,
    ap: Annotated[str | None, Field(description="AP mac")] = None,
    apfw: Annotated[str | None, Field(description="AP Firmware")] = None,
    model: Annotated[str | None, Field(description="Device model")] = None,
    text: Annotated[str | None, Field(description="Event message")] = None,
    timestamp: Annotated[str | None, Field(description="Event time")] = None,
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
        "/api/v1/orgs/{org_id}/devices/events/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "site_id": site_id,
            "ap": ap,
            "apfw": apfw,
            "model": model,
            "text": text,
            "timestamp": timestamp,
            "type": type,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_count_org_device_last_configs",
    description="GET /api/v1/orgs/{org_id}/devices/last_config/count\n\ncountOrgDeviceLastConfigs\n\nCounts the number of entries in device config history for distinct field with given filters",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_device_last_configs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
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
        "/api/v1/orgs/{org_id}/devices/last_config/count",
        path_params={"org_id": org_id},
        query_params={
            "type": type,
            "distinct": distinct,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_count_org_devices",
    description="GET /api/v1/orgs/{org_id}/devices/count\n\ncountOrgDevices\n\nCount by Distinct Attributes of Org Devices",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    hostname: Annotated[str | None, Field(description="Partial / full hostname")] = None,
    site_id: Annotated[str | None, Field(description="Site id")] = None,
    model: Annotated[str | None, Field(description="Device model")] = None,
    managed: Annotated[
        str | None,
        Field(
            description="for switches and gateways, to filter on managed/unmanaged devices. Deprecated in favour of mist_configured. enum: `true`, `false`"
        ),
    ] = None,
    mac: Annotated[str | None, Field(description="AP mac")] = None,
    version: Annotated[str | None, Field(description="Version")] = None,
    ip: Annotated[str | None, Field(description="query parameter 'ip'")] = None,
    mxtunnel_status: Annotated[Any | None, Field(description="MxTunnel status, enum: `up`, `down`")] = None,
    mxedge_id: Annotated[str | None, Field(description="Mist Edge id, if AP is connecting to a Mist Edge")] = None,
    lldp_system_name: Annotated[str | None, Field(description="LLDP system name")] = None,
    lldp_system_desc: Annotated[str | None, Field(description="LLDP system description")] = None,
    lldp_port_id: Annotated[str | None, Field(description="LLDP port id")] = None,
    lldp_mgmt_addr: Annotated[str | None, Field(description="LLDP management ip address")] = None,
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
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
        "/api/v1/orgs/{org_id}/devices/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "hostname": hostname,
            "site_id": site_id,
            "model": model,
            "managed": managed,
            "mac": mac,
            "version": version,
            "ip": ip,
            "mxtunnel_status": mxtunnel_status,
            "mxedge_id": mxedge_id,
            "lldp_system_name": lldp_system_name,
            "lldp_system_desc": lldp_system_desc,
            "lldp_port_id": lldp_port_id,
            "lldp_mgmt_addr": lldp_mgmt_addr,
            "type": type,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_juniper_devices_command",
    description="GET /api/v1/orgs/{org_id}/ocdevices/outbound_ssh_cmd\n\ngetOrgJuniperDevicesCommand\n\nGet Org Juniper Devices command\n\nJuniper devices can be managed/adopted by Mist. Currently outbound-ssh + netconf is used.\nA few lines of CLI commands are generated per-Org, allowing the Juniper devices to phone home to Mist.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_juniper_devices_command(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[
        str | None,
        Field(description="Site_id would be used for proxy config check of the site and automatic site assignment"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ocdevices/outbound_ssh_cmd",
        path_params={"org_id": org_id},
        query_params={"site_id": site_id},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_aps_macs",
    description="GET /api/v1/orgs/{org_id}/devices/radio_macs\n\nlistOrgApsMacs\n\nFor some scenarios like E911 or security systems, the BSSIDs are required to identify which AP the client is connecting to. Then the location of the AP can be used as the approximate location of the client.\n\nEach radio MAC can have 16 BSSIDs (enumerate the last octet from 0-F)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_aps_macs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/devices/radio_macs",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_devices",
    description="GET /api/v1/orgs/{org_id}/devices\n\nlistOrgDevices\n\nGet List of Org Devices",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/devices",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_devices_summary",
    description="GET /api/v1/orgs/{org_id}/devices/summary\n\nlistOrgDevicesSummary\n\nGet Org Devices Summary",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_devices_summary(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/devices/summary",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_device_events",
    description="GET /api/v1/orgs/{org_id}/devices/events/search\n\nsearchOrgDeviceEvents\n\nSearch Org Devices Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_device_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mac: Annotated[str | None, Field(description="Device mac")] = None,
    model: Annotated[str | None, Field(description="Device model")] = None,
    device_type: Annotated[Any | None, Field(description="query parameter 'device_type'")] = None,
    text: Annotated[str | None, Field(description="Event message")] = None,
    timestamp: Annotated[str | None, Field(description="Event time")] = None,
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
    ] = None,
    last_by: Annotated[str | None, Field(description="Return last/recent event for passed in field")] = None,
    includes: Annotated[
        str | None,
        Field(description="Keyword to include events from additional indices (e.g. ext_tunnel for prisma events)"),
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
        "/api/v1/orgs/{org_id}/devices/events/search",
        path_params={"org_id": org_id},
        query_params={
            "mac": mac,
            "model": model,
            "device_type": device_type,
            "text": text,
            "timestamp": timestamp,
            "type": type,
            "last_by": last_by,
            "includes": includes,
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
    name="mist_search_org_device_last_configs",
    description="GET /api/v1/orgs/{org_id}/devices/last_config/search\n\nsearchOrgDeviceLastConfigs\n\nSearch Device Last Configs",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_device_last_configs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_type: Annotated[Any | None, Field(description="query parameter 'device_type'")] = None,
    mac: Annotated[str | None, Field(description="Device MAC address")] = None,
    name: Annotated[str | None, Field(description="Devices Name")] = None,
    version: Annotated[str | None, Field(description="Device Version")] = None,
    cert_expiry_duration: Annotated[
        str | None, Field(description="Duration for expiring cert queries (format: 2d/3h/172800 seconds)")
    ] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
        "/api/v1/orgs/{org_id}/devices/last_config/search",
        path_params={"org_id": org_id},
        query_params={
            "device_type": device_type,
            "mac": mac,
            "name": name,
            "version": version,
            "cert_expiry_duration": cert_expiry_duration,
            "start": start,
            "end": end,
            "limit": limit,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_devices",
    description="GET /api/v1/orgs/{org_id}/devices/search\n\nsearchOrgDevices\n\nSearch Org Devices",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    band_24_channel: Annotated[int | None, Field(description="When `type`==`ap`, Channel of band_24")] = None,
    band_5_channel: Annotated[int | None, Field(description="When `type`==`ap`, Channel of band_5")] = None,
    band_6_channel: Annotated[int | None, Field(description="When `type`==`ap`, Channel of band_6")] = None,
    band_24_bandwidth: Annotated[int | None, Field(description="When `type`==`ap`, Bandwidth of band_24")] = None,
    band_5_bandwidth: Annotated[int | None, Field(description="When `type`==`ap`, Bandwidth of band_5")] = None,
    band_6_bandwidth: Annotated[int | None, Field(description="When `type`==`ap`, Bandwidth of band_6")] = None,
    band_24_power: Annotated[int | None, Field(description="When `type`==`ap`, Power of band_24")] = None,
    band_5_power: Annotated[int | None, Field(description="When `type`==`ap`, Power of band_5")] = None,
    band_6_power: Annotated[int | None, Field(description="When `type`==`ap`, Power of band_6")] = None,
    clustered: Annotated[bool | None, Field(description="When `type`==`gateway`, true / false")] = None,
    eth0_port_speed: Annotated[int | None, Field(description="When `type`==`ap`, Port speed of eth0")] = None,
    evpntopo_id: Annotated[str | None, Field(description="When `type`==`switch`, EVPN topology id")] = None,
    ext_ip: Annotated[
        str | None,
        Field(
            description="Partial / full Device external ip. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `1.2.3.*` and `*.2.3.*` match `1.2.3.4`). Suffix-only wildcards (e.g. `*.2.3.4`) are not supported"
        ),
    ] = None,
    hostname: Annotated[
        str | None,
        Field(
            description="Partial / full Device hostname. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `my-london*` and `*london*` match `my-london-1`). Suffix-only wildcards (e.g. `*london-1`) are not supported"
        ),
    ] = None,
    ip: Annotated[
        str | None,
        Field(
            description="Partial / full Device IP Address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `10.100.10.*` and `*100.10.*` match `10.100.10.54`). Suffix-only wildcards (e.g. `*.54`) are not supported"
        ),
    ] = None,
    last_config_status: Annotated[
        str | None, Field(description="When `type`==`switch` or `type`==`gateway`, last configuration status")
    ] = None,
    last_hostname: Annotated[str | None, Field(description="Last hostname of the device.")] = None,
    lldp_mgmt_addr: Annotated[str | None, Field(description="When `type`==`ap`, LLDP management ip address")] = None,
    lldp_port_id: Annotated[
        str | None,
        Field(
            description="When `type`==`ap`, LLDP port id. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `ge-0/0/*` and `*-0/0/*` match `ge-0/0/30`). Suffix-only wildcards (e.g. `*switch-01`) are not supported"
        ),
    ] = None,
    lldp_system_desc: Annotated[
        str | None,
        Field(
            description="When `type`==`ap`, LLDP system description. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `Juniper Networks*` and `*Networks*` match `Juniper Networks, Inc.`). Suffix-only wildcards (e.g. `*switch-01`) are no..."
        ),
    ] = None,
    lldp_system_name: Annotated[
        str | None,
        Field(
            description="When `type`==`ap`, LLDP system name. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `my-switch*` and `*switch*` match `my-switch-01`). Suffix-only wildcards (e.g. `*switch-01`) are not supported"
        ),
    ] = None,
    mac: Annotated[
        str | None,
        Field(
            description="Partial / full Device MAC address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `001122*` and `*1122*` match `001122334455`). Suffix-only wildcards (e.g. `*4455`) are not supported"
        ),
    ] = None,
    model: Annotated[
        str | None,
        Field(
            description="Partial / full Device model. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `AP4*` and `*P4*` match `AP43`). Suffix-only wildcards (e.g. `*43`) are not supported"
        ),
    ] = None,
    mxedge_id: Annotated[
        str | None, Field(description="When `type`==`ap`, Mist Edge id, if AP is connecting to a Mist Edge")
    ] = None,
    mxedge_ids: Annotated[
        str | None,
        Field(
            description="When `type`==`ap`, Comma separated list of Mist Edge id, if AP is connecting to a Mist Edge"
        ),
    ] = None,
    mxtunnel_status: Annotated[Any | None, Field(description="When `type`==`ap`, MxTunnel status, up / down.")] = None,
    node: Annotated[Any | None, Field(description="When `type`==`gateway`. enum: `node0`, `node1`")] = None,
    node0_mac: Annotated[str | None, Field(description="When `type`==`gateway`, node0 MAC Address")] = None,
    node1_mac: Annotated[str | None, Field(description="When `type`==`gateway`, node1 MAC Address")] = None,
    power_constrained: Annotated[
        bool | None, Field(description="When `type`==`ap`, whether the AP is power constrained")
    ] = None,
    radius_stats: Annotated[
        str | None,
        Field(
            description="When `type`==`switch` or `type`==`gateway`, Key-value pairs where the key\nis the RADIUS server address and the value contains authentication statistics:\n  * <server_address> (string): IP address of the RADIUS server as the key\n  * `auth_..."
        ),
    ] = None,
    site_id: Annotated[str | None, Field(description="Site id")] = None,
    stats: Annotated[bool, Field(description="Whether to return device stats")] = False,
    t128agent_version: Annotated[
        str | None, Field(description="When `type`==`gateway` (SSR only), version of 128T agent")
    ] = None,
    type: Annotated[Any | None, Field(description="Type of device. enum: `ap`, `gateway`, `switch`")] = None,
    version: Annotated[str | None, Field(description="Version")] = None,
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
        "/api/v1/orgs/{org_id}/devices/search",
        path_params={"org_id": org_id},
        query_params={
            "band_24_channel": band_24_channel,
            "band_5_channel": band_5_channel,
            "band_6_channel": band_6_channel,
            "band_24_bandwidth": band_24_bandwidth,
            "band_5_bandwidth": band_5_bandwidth,
            "band_6_bandwidth": band_6_bandwidth,
            "band_24_power": band_24_power,
            "band_5_power": band_5_power,
            "band_6_power": band_6_power,
            "clustered": clustered,
            "eth0_port_speed": eth0_port_speed,
            "evpntopo_id": evpntopo_id,
            "ext_ip": ext_ip,
            "hostname": hostname,
            "ip": ip,
            "last_config_status": last_config_status,
            "last_hostname": last_hostname,
            "lldp_mgmt_addr": lldp_mgmt_addr,
            "lldp_port_id": lldp_port_id,
            "lldp_system_desc": lldp_system_desc,
            "lldp_system_name": lldp_system_name,
            "mac": mac,
            "model": model,
            "mxedge_id": mxedge_id,
            "mxedge_ids": mxedge_ids,
            "mxtunnel_status": mxtunnel_status,
            "node": node,
            "node0_mac": node0_mac,
            "node1_mac": node1_mac,
            "power_constrained": power_constrained,
            "radius_stats": radius_stats,
            "site_id": site_id,
            "stats": stats,
            "t128agent_version": t128agent_version,
            "type": type,
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
