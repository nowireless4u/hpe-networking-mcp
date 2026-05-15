"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Devices``
Operations in this file: 16
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
    name="mist_add_site_device_image",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/image/{image_number}\n\naddSiteDeviceImage\n\nAttach up to 3 images to a device",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_add_site_device_image(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    image_number: Annotated[int, Field(description="path parameter 'image_number'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/image/{image_number}",
        path_params={"site_id": site_id, "device_id": device_id, "image_number": image_number},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_count_site_device_config_history",
    description="GET /api/v1/sites/{site_id}/devices/config_history/count\n\ncountSiteDeviceConfigHistory\n\nCounts the number of entries in device config history for distinct field with given filters",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_device_config_history(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[str | None, Field(description="query parameter 'distinct'")] = None,
    mac: Annotated[str | None, Field(description="query parameter 'mac'")] = None,
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
        "/api/v1/sites/{site_id}/devices/config_history/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "mac": mac,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_count_site_device_events",
    description="GET /api/v1/sites/{site_id}/devices/events/count\n\ncountSiteDeviceEvents\n\nCounts the number of entries in ap events history for distinct field with given filters",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_device_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    model: Annotated[str | None, Field(description="query parameter 'model'")] = None,
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
    ] = None,
    type_code: Annotated[str | None, Field(description="query parameter 'type_code'")] = None,
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
        "/api/v1/sites/{site_id}/devices/events/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "model": model,
            "type": type,
            "type_code": type_code,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_count_site_device_last_config",
    description="GET /api/v1/sites/{site_id}/devices/last_config/count\n\ncountSiteDeviceLastConfig\n\nCounts the number of entries in device config history for distinct field with given filters",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_device_last_config(
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
        "/api/v1/sites/{site_id}/devices/last_config/count",
        path_params={"site_id": site_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_count_site_devices",
    description="GET /api/v1/sites/{site_id}/devices/count\n\ncountSiteDevices\n\nCounts the number of entries in ap events history for distinct field with given filters",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    hostname: Annotated[str | None, Field(description="query parameter 'hostname'")] = None,
    model: Annotated[str | None, Field(description="query parameter 'model'")] = None,
    mac: Annotated[str | None, Field(description="query parameter 'mac'")] = None,
    version: Annotated[str | None, Field(description="query parameter 'version'")] = None,
    mxtunnel_status: Annotated[str | None, Field(description="query parameter 'mxtunnel_status'")] = None,
    mxedge_id: Annotated[str | None, Field(description="query parameter 'mxedge_id'")] = None,
    lldp_system_name: Annotated[str | None, Field(description="query parameter 'lldp_system_name'")] = None,
    lldp_system_desc: Annotated[str | None, Field(description="query parameter 'lldp_system_desc'")] = None,
    lldp_port_id: Annotated[str | None, Field(description="query parameter 'lldp_port_id'")] = None,
    lldp_mgmt_addr: Annotated[str | None, Field(description="query parameter 'lldp_mgmt_addr'")] = None,
    map_id: Annotated[str | None, Field(description="query parameter 'map_id'")] = None,
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
        "/api/v1/sites/{site_id}/devices/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "hostname": hostname,
            "model": model,
            "mac": mac,
            "version": version,
            "mxtunnel_status": mxtunnel_status,
            "mxedge_id": mxedge_id,
            "lldp_system_name": lldp_system_name,
            "lldp_system_desc": lldp_system_desc,
            "lldp_port_id": lldp_port_id,
            "lldp_mgmt_addr": lldp_mgmt_addr,
            "map_id": map_id,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_delete_site_device_image",
    description="DELETE /api/v1/sites/{site_id}/devices/{device_id}/image/{image_number}\n\ndeleteSiteDeviceImage\n\nDelete image from a device",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_device_image(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    image_number: Annotated[int, Field(description="path parameter 'image_number'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/devices/{device_id}/image/{image_number}",
        path_params={"site_id": site_id, "device_id": device_id, "image_number": image_number},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_export_site_devices",
    description="GET /api/v1/sites/{site_id}/devices/export\n\nexportSiteDevices\n\nTo download the exported device information",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_export_site_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices/export",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_device",
    description="GET /api/v1/sites/{site_id}/devices/{device_id}\n\ngetSiteDevice\n\nGet Device Configuration",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices/{device_id}",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_import_site_devices",
    description='POST /api/v1/sites/{site_id}/devices/import\n\nimportSiteDevices\n\nImport Information for Multiple Devices\n\nCSV format:\n```csv\nmac,name,map_id,x,y,height,orientation,labels,band_24.power,band_24.bandwidth,band_24.channel,band_24.disabled,band_5.power,band_5.bandwidth,band_5.channel,band_5.disabled,band_6.power,band_6.bandwidth,band_6.channel,band_6.disabled\n5c5b53010101,"AP 1",845a23bf-bed9-e43c-4c86-6fa474be7ae5,30,10,2.3,45,"guest, campus, vip",1,20,0,false,0,40,0,false,17,80,0,false\n```',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_import_site_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/import"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/import",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_list_site_devices",
    description="GET /api/v1/sites/{site_id}/devices\n\nlistSiteDevices\n\nGet list of devices on the site.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    name: Annotated[str | None, Field(description="query parameter 'name'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices",
        path_params={"site_id": site_id},
        query_params={"type": type, "name": name, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_device_config_history",
    description="GET /api/v1/sites/{site_id}/devices/config_history/search\n\nsearchSiteDeviceConfigHistory\n\nSearch for entries in device config history",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_device_config_history(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    mac: Annotated[str | None, Field(description="Device MAC Address")] = None,
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
        "/api/v1/sites/{site_id}/devices/config_history/search",
        path_params={"site_id": site_id},
        query_params={
            "type": type,
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


@_mcp_tool(
    name="mist_search_site_device_events",
    description="GET /api/v1/sites/{site_id}/devices/events/search\n\nsearchSiteDeviceEvents\n\nSearch Devices Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_device_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mac: Annotated[str | None, Field(description="Device mac")] = None,
    model: Annotated[str | None, Field(description="Device model")] = None,
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
        "/api/v1/sites/{site_id}/devices/events/search",
        path_params={"site_id": site_id},
        query_params={
            "mac": mac,
            "model": model,
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
    name="mist_search_site_device_last_configs",
    description="GET /api/v1/sites/{site_id}/devices/last_config/search\n\nsearchSiteDeviceLastConfigs\n\nSearch Device Last Configs",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_device_last_configs(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    cert_expiry_duration: Annotated[
        str | None, Field(description="Duration for expiring cert queries (format: 2d/3h/172800 seconds)")
    ] = None,
    device_type: Annotated[Any | None, Field(description="query parameter 'device_type'")] = None,
    mac: Annotated[str | None, Field(description="query parameter 'mac'")] = None,
    version: Annotated[str | None, Field(description="query parameter 'version'")] = None,
    name: Annotated[str | None, Field(description="query parameter 'name'")] = None,
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
        "/api/v1/sites/{site_id}/devices/last_config/search",
        path_params={"site_id": site_id},
        query_params={
            "cert_expiry_duration": cert_expiry_duration,
            "device_type": device_type,
            "mac": mac,
            "version": version,
            "name": name,
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
    name="mist_search_site_devices",
    description="GET /api/v1/sites/{site_id}/devices/search\n\nsearchSiteDevices\n\nSearch Device",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
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
    sort: Annotated[Any | None, Field(description="Sort options")] = None,
    desc_sort: Annotated[Any | None, Field(description="Sort options in reverse order")] = None,
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
        "/api/v1/sites/{site_id}/devices/search",
        path_params={"site_id": site_id},
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
            "stats": stats,
            "t128agent_version": t128agent_version,
            "type": type,
            "version": version,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "desc_sort": desc_sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_set_site_devices_gbp_tag",
    description="POST /api/v1/sites/{site_id}/devices/gbp_tag\n\nsetSiteDevicesGbpTag\n\nSet GBP Tag for multiple devices",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_set_site_devices_gbp_tag(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/gbp_tag",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_site_device",
    description="PUT /api/v1/sites/{site_id}/devices/{device_id}\n\nupdateSiteDevice\n\nUpdate Device Configuration",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/devices/{device_id}",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )
