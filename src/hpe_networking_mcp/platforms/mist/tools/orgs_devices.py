"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Devices``
Operations in this file: 10
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
    name="mist_count_org_device_events",
    description="GET /api/v1/orgs/{org_id}/devices/events/count\n\ncountOrgDeviceEvents\n\nCount device event records across the organization, optionally grouped by `distinct` and filtered by site, AP, firmware, model, event text, event type, and time range.",
    capability=Capability.READ,
)
async def mist_count_org_device_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `ap`, `apfw`, `model`, `org_id`, `site_id`, `text`, `timestamp`, `type`"
        ),
    ] = None,
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    ap: Annotated[str | None, Field(description="Filter results by AP MAC address")] = None,
    apfw: Annotated[str | None, Field(description="Filter results by AP firmware version")] = None,
    model: Annotated[str | None, Field(description="Filter results by device model")] = None,
    text: Annotated[str | None, Field(description="Filter results by event message text")] = None,
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
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
        "/api/v1/orgs/{org_id}/devices/events/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "site_id": site_id,
            "ap": ap,
            "apfw": apfw,
            "model": model,
            "text": text,
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
    description="GET /api/v1/orgs/{org_id}/devices/last_config/count\n\ncountOrgDeviceLastConfigs\n\nCount device config history records across the organization, optionally grouped by `distinct` and filtered by device type and time range.",
    capability=Capability.READ,
)
async def mist_count_org_device_last_configs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[Any | None, Field(description="Filter results by type. enum: `ap`, `gateway`, `switch`")] = None,
    distinct: Annotated[
        Any | None,
        Field(description="Field used to group this count response. enum: `mac`, `name`, `site_id`, `version`"),
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
    description="GET /api/v1/orgs/{org_id}/devices/count\n\ncountOrgDevices\n\nCount organization device records, optionally grouped by `distinct` and filtered by device identifiers, model, LLDP attributes, Mist Edge, tunnel status, device type, and time range.",
    capability=Capability.READ,
)
async def mist_count_org_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `hostname`, `ip`, `lldp_mgmt_addr`, `lldp_port_id`, `lldp_system_desc`, `lldp_system_name`, `mac`, `model`, `mxedge_id`, `mxtunnel_status`, `site_id`, `version`"
        ),
    ] = None,
    hostname: Annotated[str | None, Field(description="Partial / full hostname")] = None,
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    model: Annotated[
        str | None, Field(description="Filter results by device model. Accepts multiple comma-separated values.")
    ] = None,
    managed: Annotated[
        str | None,
        Field(
            description="for switches and gateways, to filter on managed/unmanaged devices. Deprecated in favour of mist_configured. enum: `true`, `false`"
        ),
    ] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    version: Annotated[str | None, Field(description="Filter results by software version")] = None,
    ip: Annotated[str | None, Field(description="Filter results by IPv4 address")] = None,
    mxtunnel_status: Annotated[Any | None, Field(description="MxTunnel status, enum: `up`, `down`")] = None,
    mxedge_id: Annotated[str | None, Field(description="Mist Edge id, if AP is connecting to a Mist Edge")] = None,
    lldp_system_name: Annotated[str | None, Field(description="Filter results by LLDP system name")] = None,
    lldp_system_desc: Annotated[str | None, Field(description="Filter results by LLDP system description")] = None,
    lldp_port_id: Annotated[str | None, Field(description="Filter results by LLDP port identifier")] = None,
    lldp_mgmt_addr: Annotated[str | None, Field(description="LLDP management IP address")] = None,
    type: Annotated[Any | None, Field(description="Filter results by type. enum: `ap`, `gateway`, `switch`")] = None,
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
    capability=Capability.READ,
)
async def mist_get_org_juniper_devices_command(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
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
    description="GET /api/v1/orgs/{org_id}/devices/radio_macs\n\nlistOrgApsMacs\n\nFor some scenarios like E911 or security systems, the BSSIDs are required to identify which AP the client is connecting to. Then the location of the AP can be used as the approximate location of the client.\n\nEach radio MAC can have up to 16 BSSIDs. These are derived by incrementing the least significant hexadecimal digit (last nibble) of the MAC address from 0 to F, while keeping the remaining bits unchanged.",
    capability=Capability.READ,
)
async def mist_list_org_aps_macs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
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
    description="GET /api/v1/orgs/{org_id}/devices\n\nlistOrgDevices\n\nList devices in the organization, including APs, switches and gateways managed or monitored by Mist.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/devices/summary\n\nlistOrgDevicesSummary\n\nReturn aggregate organization device counts by device category and assignment state.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/devices/events/search\n\nsearchOrgDeviceEvents\n\nSearch device event records across the organization with filters for MAC address, model, device type, event text, event type, additional event indices, and time range.",
    capability=Capability.READ,
)
async def mist_search_org_device_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mac: Annotated[
        str | None, Field(description="Filter results by MAC address. Accepts multiple comma-separated values.")
    ] = None,
    model: Annotated[
        str | None, Field(description="Filter results by device model. Accepts multiple comma-separated values.")
    ] = None,
    device_type: Annotated[
        Any | None, Field(description="Filter results by device type. Accepts multiple comma-separated values.")
    ] = None,
    text: Annotated[str | None, Field(description="Filter results by event message text")] = None,
    type: Annotated[
        str | None,
        Field(
            description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions). Accepts multiple comma-separated values."
        ),
    ] = None,
    last_by: Annotated[str | None, Field(description="Return last/recent event for passed in field")] = None,
    includes: Annotated[
        str | None,
        Field(description="Keyword to include events from additional indices (e.g. ext_tunnel for prisma events)"),
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
        "/api/v1/orgs/{org_id}/devices/events/search",
        path_params={"org_id": org_id},
        query_params={
            "mac": mac,
            "model": model,
            "device_type": device_type,
            "text": text,
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
    description="GET /api/v1/orgs/{org_id}/devices/last_config/search\n\nsearchOrgDeviceLastConfigs\n\nSearch device config history records across the organization with filters for device type, MAC address, name, software version, certificate-expiry duration, and time range.",
    capability=Capability.READ,
)
async def mist_search_org_device_last_configs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_type: Annotated[
        Any | None, Field(description="Filter results by device type. enum: `ap`, `gateway`, `switch`, `mxedge`")
    ] = None,
    mac: Annotated[
        str | None, Field(description="Filter results by MAC address. Accepts multiple comma-separated values.")
    ] = None,
    name: Annotated[
        str | None, Field(description="Filter results by name. Accepts multiple comma-separated values.")
    ] = None,
    version: Annotated[
        str | None, Field(description="Filter results by software version. Accepts multiple comma-separated values.")
    ] = None,
    cert_expiry_duration: Annotated[
        str | None, Field(description="Duration for expiring cert queries (format: 2d/3h/172800 seconds)")
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
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
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
    description="GET /api/v1/orgs/{org_id}/devices/search\n\nsearchOrgDevices\n\nSearch organization devices with filters for AP radio attributes, gateway HA attributes, switch EVPN attributes, LLDP data, MAC address, IP address, model, software version, site, Mist Edge, and time range. Set `stats=true` to include device stats in the response.",
    capability=Capability.READ,
)
async def mist_search_org_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    band_24_channel: Annotated[
        int | None,
        Field(description="When `type`==`ap`, Channel of band_24. Accepts multiple comma-separated integer values."),
    ] = None,
    band_5_channel: Annotated[
        int | None,
        Field(description="When `type`==`ap`, Channel of band_5. Accepts multiple comma-separated integer values."),
    ] = None,
    band_6_channel: Annotated[
        int | None,
        Field(description="When `type`==`ap`, Channel of band_6. Accepts multiple comma-separated integer values."),
    ] = None,
    band_24_bandwidth: Annotated[
        int | None,
        Field(description="When `type`==`ap`, Bandwidth of band_24. Accepts multiple comma-separated integer values."),
    ] = None,
    band_5_bandwidth: Annotated[
        int | None,
        Field(description="When `type`==`ap`, Bandwidth of band_5. Accepts multiple comma-separated integer values."),
    ] = None,
    band_6_bandwidth: Annotated[
        int | None,
        Field(description="When `type`==`ap`, Bandwidth of band_6. Accepts multiple comma-separated integer values."),
    ] = None,
    band_24_power: Annotated[
        int | None,
        Field(description="When `type`==`ap`, Power of band_24. Accepts multiple comma-separated integer values."),
    ] = None,
    band_5_power: Annotated[
        int | None,
        Field(description="When `type`==`ap`, Power of band_5. Accepts multiple comma-separated integer values."),
    ] = None,
    band_6_power: Annotated[
        int | None,
        Field(description="When `type`==`ap`, Power of band_6. Accepts multiple comma-separated integer values."),
    ] = None,
    clustered: Annotated[bool | None, Field(description="When `type`==`gateway`, true / false")] = None,
    eth0_port_speed: Annotated[
        int | None,
        Field(description="When `type`==`ap`, Port speed of eth0. Accepts multiple comma-separated integer values."),
    ] = None,
    evpntopo_id: Annotated[str | None, Field(description="When `type`==`switch`, EVPN topology id")] = None,
    ext_ip: Annotated[
        str | None,
        Field(
            description="Partial / full Device external ip. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `1.2.3.*` and `*.2.3.*` match `1.2.3.4`). Suffix-only wildcards (e.g. `*.2.3.4`) are not supported. Accepts multiple comma-sepa..."
        ),
    ] = None,
    hostname: Annotated[
        str | None,
        Field(
            description="Partial / full Device hostname. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `my-london*` and `*london*` match `my-london-1`). Suffix-only wildcards (e.g. `*london-1`) are not supported. Accepts multiple com..."
        ),
    ] = None,
    ip: Annotated[
        str | None,
        Field(
            description="Partial / full Device IP address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `10.100.10.*` and `*100.10.*` match `10.100.10.54`). Suffix-only wildcards (e.g. `*.54`) are not supported. Accepts multiple com..."
        ),
    ] = None,
    last_config_status: Annotated[
        str | None, Field(description="When `type`==`switch` or `type`==`gateway`, last configuration status")
    ] = None,
    last_hostname: Annotated[
        str | None, Field(description="Last hostname of the device. Accepts multiple comma-separated values.")
    ] = None,
    lldp_mgmt_addr: Annotated[
        str | None,
        Field(description="When `type`==`ap`, LLDP management IP address. Accepts multiple comma-separated values."),
    ] = None,
    lldp_port_id: Annotated[
        str | None,
        Field(
            description="When `type`==`ap`, LLDP port id. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `ge-0/0/*` and `*-0/0/*` match `ge-0/0/30`). Suffix-only wildcards (e.g. `*switch-01`) are not supported. Accepts multiple comma-..."
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
            description="When `type`==`ap`, LLDP system name. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `my-switch*` and `*switch*` match `my-switch-01`). Suffix-only wildcards (e.g. `*switch-01`) are not supported. Accepts multi..."
        ),
    ] = None,
    mac: Annotated[
        str | None,
        Field(
            description="Partial / full Device MAC address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `001122*` and `*1122*` match `001122334455`). Suffix-only wildcards (e.g. `*4455`) are not supported. Accepts multiple comma-se..."
        ),
    ] = None,
    model: Annotated[
        str | None,
        Field(
            description="Partial / full Device model. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `AP4*` and `*P4*` match `AP43`). Suffix-only wildcards (e.g. `*43`) are not supported. Accepts multiple comma-separated values."
        ),
    ] = None,
    mxedge_id: Annotated[
        str | None,
        Field(
            description="When `type`==`ap`, Mist Edge id, if AP is connecting to a Mist Edge. Accepts multiple comma-separated values."
        ),
    ] = None,
    mxedge_ids: Annotated[
        str | None,
        Field(
            description="When `type`==`ap`, Comma separated list of Mist Edge id, if AP is connecting to a Mist Edge"
        ),
    ] = None,
    mxtunnel_status: Annotated[
        Any | None,
        Field(description="When `type`==`ap`, Mist Tunnel status used to filter results. enum: `down`, `up`"),
    ] = None,
    node: Annotated[Any | None, Field(description="When `type`==`gateway`. enum: `node0`, `node1`")] = None,
    node0_mac: Annotated[str | None, Field(description="When `type`==`gateway`, node0 MAC address")] = None,
    node1_mac: Annotated[str | None, Field(description="When `type`==`gateway`, node1 MAC address")] = None,
    power_constrained: Annotated[
        bool | None, Field(description="When `type`==`ap`, whether the AP is power constrained.")
    ] = None,
    radius_stats: Annotated[
        str | None,
        Field(
            description="When `type`==`switch` or `type`==`gateway`, Key-value pairs where the key\nis the RADIUS server address and the value contains authentication statistics:\n  * <server_address> (string): IP address of the RADIUS server as the key\n  * `auth_..."
        ),
    ] = None,
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    stats: Annotated[bool, Field(description="Whether to return device stats")] = False,
    t128agent_version: Annotated[
        str | None, Field(description="When `type`==`gateway` (SSR only), version of 128T agent")
    ] = None,
    type: Annotated[
        Any | None, Field(description="Device type used to filter results. enum: `ap`, `gateway`, `switch`")
    ] = None,
    version: Annotated[
        str | None, Field(description="Filter results by software version. Accepts multiple comma-separated values.")
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
