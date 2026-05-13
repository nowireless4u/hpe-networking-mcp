"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Utilities Common``
Operations in this file: 24
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
    name="mist_arp_from_device",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/arp\n\narpFromDevice\n\nARP can be performed on the Device. The output will be available through websocket. As there can be multiple commands issued against the same AP at the same time and the output all goes through the same websocket stream, session is introduced for demux.\n\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n##### Example output from ws stream\n```json\n{ \n "event": "data", \n "channel": "/sites/4ac1dcf4-9d8b-7211-65c4-057819f0862b/devices/...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_arp_from_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/arp"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/arp",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_bounce_device_port",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/bounce_port\n\nbounceDevicePort\n\nPort Bounce can be performed from Switch/Gateway.\n\n **Note:** Ports starting with vme, ae, irb, and HA control ports (for SSR only) are not supported\n\nThe output will be available through websocket. As there can be multiple commands issued against the same AP at the same time and the output all goes through the same websocket stream, session is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n##### ...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_bounce_device_port(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/bounce_port",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_clear_site_device_mac_table",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/clear_mac_table\n\nclearSiteDeviceMacTable\n\nClear MAC Table from the Device.\n\nThe output will be available through websocket. As there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_clear_site_device_mac_table(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/clear_mac_table",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_clear_site_device_policy_hit_count",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/clear_policy_hit_count\n\nclearSiteDevicePolicyHitCount\n\nClear application policy hit counts for the specified policy.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_clear_site_device_policy_hit_count(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/clear_policy_hit_count",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/clear_policy_hit_count",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_site_device_shell_session",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/shell\n\ncreateSiteDeviceShellSession\n\nCreate Shell Session",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_device_shell_session(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/shell"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/shell",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_get_site_device_config_cmd",
    description="GET /api/v1/sites/{site_id}/devices/{device_id}/config_cmd\n\ngetSiteDeviceConfigCmd\n\nGet Config CLI Commands\nFor a brown-field switch deployment where we adopted the switch through Adoption Command, we do not wipe out / overwrite the existing config automatically. Instead, we generate CLI commands that we would have generated. The user can inspect, modify, and incorporate this into their existing config manually.\n\nOnce they feel comfortable about the config we generate, they can enable allow_mist_config where we will take full control of their config like a claimed switch",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_device_config_cmd(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    sort: Annotated[bool, Field(description="Make output cmds sorted (for better readability) or not.")] = False,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices/{device_id}/config_cmd",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params={"sort": sort},
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_device_ztp_password",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/request_ztp_password\n\ngetSiteDeviceZtpPassword\n\nIn the case where something happens during/after ZTP, the root-password is modified (required for ZTP to set up outbound-ssh) but the user-defined password config has not be configured. This API can be used to retrieve the temporary password.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_get_site_device_ztp_password(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/request_ztp_password",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_monitor_site_device_traffic",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/monitor_traffic\n\nmonitorSiteDeviceTraffic\n\nMonitor traffic on switches and SRX.\n  * JUNOS uses cmd "monitor interface <port>" to monitor traffic on particular <port>\n  * JUNOS uses cmd "monitor interface traffic" to monitor traffic on all ports',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_monitor_site_device_traffic(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/monitor_traffic",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/monitor_traffic",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_ping_from_device",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/ping\n\npingFromDevice\n\nPing from AP, Switch and SSR\n\nPing can be performed from the Device. The output will be available through websocket. As there can be multiple commands issued against the same AP at the same time and the output all goes through the same websocket stream, session is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n##### Example output from ws stream\n```json\n{\n    "event": "data",\n    "channel": "/sites/4ac1dcf...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_ping_from_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/ping",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_readopt_site_octerm_device",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/readopt\n\nreadoptSiteOctermDevice\n\nFor the octerm devices, the device ID must come from fpc0. However, for a VC, the users may change the original fpc0 from CLI. To fix the issue, the readopt API could be used to trigger the readopt process so the device would get the correct device ID to connect the cloud.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_readopt_site_octerm_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/readopt",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_release_site_device_dhcp_lease",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/release_dhcp_leases\n\nreleaseSiteDeviceDhcpLease\n\nReleases an active DHCP lease.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_release_site_device_dhcp_lease(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/release_dhcp_leases",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/release_dhcp_leases",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_reprovision_site_octerm_device",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/reprovision\n\nreadoptSiteOctermDevice\n\nTo force one device to reprovision itself again.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_reprovision_site_octerm_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/reprovision",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_restart_site_device",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/restart\n\nrestartSiteDevice\n\nRestart / Reboot a device",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_restart_site_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/restart"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/restart",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_restart_site_multiple_devices",
    description="POST /api/v1/sites/{site_id}/devices/restart\n\nrestartSiteMultipleDevices\n\nNote that only the devices that are connected will be restarted.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_restart_site_multiple_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/restart",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_device_bgp_summary",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_bgp_summary\n\nshowSiteDeviceBgpSummary\n\nGet BGP Summary from SSR, SRX and Switch.\n\n\nThe output will be available through websocket. As there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n\n}\n```\n\n##### Example output from ws stream\n```\nTue 2024-04-23 16:36:06 UTC\nRetrieving bgp entries.....',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_show_site_device_bgp_summary(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_bgp_summary",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_device_dhcp_leases",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/show_dhcp_leases\n\nshowSiteDeviceDhcpLeases\n\nShows DHCP leases",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_show_site_device_dhcp_leases(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/show_dhcp_leases",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_dhcp_leases",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_device_dot1x_table",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_dot1x\n\nshowSiteDeviceDot1xTable\n\nGet Dot1X Table from the Device.\n\nThe output will be available through websocket. As there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_show_site_device_dot1x_table(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_dot1x",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_device_evpn_database",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/show_evpn_database\n\nshowSiteDeviceEvpnDatabase\n\nGet EVPN Database from the Device. The output will be available through websocket.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_show_site_device_evpn_database(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_evpn_database",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_device_forwarding_table",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_forwarding_table\n\nshowSiteDeviceForwardingTable\n\nGet forwarding table from the Device. The output will be available through websocket. As there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n\n##### Example output from ws stream\n```\nMon 2024-05-20 16:47:30 UTC Retrieving fib entrie...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_show_site_device_forwarding_table(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_forwarding_table",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_device_mac_table",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_mac_table\n\nshowSiteDeviceMacTable\n\nGet MAC Table from the Device.\n\nThe output will be available through websocket. As there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n\n\n#### Subscribe to Device Command outputs\n\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n```\n\n\n#### Example output from ws stream\n\n```json \n{\n    "event": "data",\n    "channel": "/sites/d6fb4f96-xxxx-xx...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_show_site_device_mac_table(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_mac_table",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_start_site_locate_device",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/locate\n\nstartSiteLocateDevice\n\n### Access Points\nLocate an Access Point by blinking it's LED.\nIt is a persisted state that has to be stopped by calling Stop Locating API\n\n### Switches\nLocate a Switch by blinking all port LEDs. \nBy default, request is sent to `master` switch and LEDs will keep flashing for 5 minutes.\nIn case of virtual chassis (VC) the desired member mac has to be passed in the request payload. \nAt anypoint, only one VC member can be requested to flash the LED. \nTo stop LED flashing before the duration ends /unlocate API reque...",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_start_site_locate_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/locate"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/locate",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_stop_site_locate_device",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/unlocate\n\nstopSiteLocateDevice\n\nStop Locate a Device",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_stop_site_locate_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/unlocate",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_traceroute_from_device",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/traceroute\n\ntracerouteFromDevice\n\nTraceroute can be performed from the Device.\n\nThe output will be available through websocket. As there can be multiple commands issued against the same Device at the same time and the output all goes through the same websocket stream, session is introduced for demux.\n\n\n#### Subscribe to Device Command outputs\n\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n\n\n#### Example output from ws stream\n```json\n{\n  "channel": "/sites/d6fb4f96-xxxx-xxxx-xxxx-xxxxxxxxxx...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_traceroute_from_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/traceroute",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upload_site_device_support_file",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/support\n\nuploadSiteDeviceSupportFile\n\nSupport / Upload device support files\n\n#### Info Param\n| Name | Type | Description |\n| --- | --- | --- |\n| process | string | Upload 1 file with output of show system processes extensive |\n| outbound-ssh | string | Upload 1 file that concatenates all /var/log/outbound-ssh.log* files |\n| messages | string | Upload 1 to 10 /var/log/messages* files |\n| core-dumps | string | Upload all core dump files, if any. Uploads for all members of VC on switches.|\n| full | string | Upload 1 file with output of request s...",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_upload_site_device_support_file(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/support",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )
