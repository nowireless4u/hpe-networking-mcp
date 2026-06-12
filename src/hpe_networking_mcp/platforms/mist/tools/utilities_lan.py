"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Utilities LAN``
Operations in this file: 18
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
    name="mist_cable_test_from_switch",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/cable_test\n\ncableTestFromSwitch\n\nTDR can be performed from the Switch. The output will be available through websocket. As there can be multiple commands issued against the same Switch at the same time and the output all goes through the same websocket stream, session is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n##### Example output from ws stream\n```json\n{\n    "event": "data",\n    "channel": "/sites/4ac1dcf4-9d8b-7211-65c4...',
    capability=Capability.WRITE,
)
async def mist_cable_test_from_switch(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/cable_test"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/cable_test",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_clear_all_learned_macs_from_port_on_switch",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/clear_macs\n\nclearAllLearnedMacsFromPortOnSwitch\n\nClear all learned MAC addresses, including persistent MAC addresses, on a port.",
    capability=Capability.WRITE,
)
async def mist_clear_all_learned_macs_from_port_on_switch(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/clear_macs"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/clear_macs",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_clear_bpdu_errors_from_ports_on_switch",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/clear_bpdu_error\n\nclearBpduErrorsFromPortsOnSwitch\n\nClear bridge protocol data unit (BPDU) error condition caused by the detection of a possible bridging loop from Spanning Tree Protocol (STP) operation that renders the port unoperational.",
    capability=Capability.WRITE,
)
async def mist_clear_bpdu_errors_from_ports_on_switch(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/clear_bpdu_error",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/clear_bpdu_error",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_clear_site_device_dot1x_session",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/clear_dot1x\n\nclearSiteDeviceDot1xSession\n\nClear Dot1x Session. The output will be available through websocket.",
    capability=Capability.WRITE,
)
async def mist_clear_site_device_dot1x_session(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/clear_dot1x",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_clear_site_device_pending_version",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/clear_pending_version\n\nclearSiteDevicePendingVersion\n\nClear device pending fw version (Available on Junos OS EX2300-, EX3400-, EX4000-, EX4100-, EX4400- devices)",
    capability=Capability.WRITE,
)
async def mist_clear_site_device_pending_version(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/clear_pending_version",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_clear_site_multiple_device_pending_version",
    description="POST /api/v1/sites/{site_id}/devices/clear_pending_version\n\nclearSiteMultipleDevicePendingVersion\n\nClear device pending fw version (Available on Junos OS EX2300-, EX3400-, EX4000-, EX4100-, EX4400- devices)",
    capability=Capability.WRITE,
)
async def mist_clear_site_multiple_device_pending_version(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/clear_pending_version",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_site_device_snapshot",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/snapshot\n\ncreateSiteDeviceSnapshot\n\nCreate recovery device snapshot (Available on Junos OS EX2300-, EX3400-, EX4400- devices)",
    capability=Capability.WRITE,
)
async def mist_create_site_device_snapshot(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/snapshot",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_poll_site_switch_stats",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/poll_stats\n\npollSiteSwitchStats\n\nThis API can be used to poll statistics from the Switch proactively once. After it is called, the statistics will be pushed back to the cloud within the statistics interval.",
    capability=Capability.WRITE,
)
async def mist_poll_site_switch_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/poll_stats",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_reauth_org_dot1x_wired_client",
    description="POST /api/v1/orgs/{org_id}/wired_clients/{client_mac}/coa\n\nreauthOrgDot1xWiredClient\n\nTrigger a CoA (change of authorization) against a Wired client",
    capability=Capability.WRITE,
)
async def mist_reauth_org_dot1x_wired_client(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    client_mac: Annotated[str, Field(description="path parameter 'client_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/wired_clients/{client_mac}/coa",
        path_params={"org_id": org_id, "client_mac": client_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_reauth_site_dot1x_wired_client",
    description="POST /api/v1/sites/{site_id}/wired_clients/{client_mac}/coa\n\nreauthSiteDot1xWiredClient\n\nTrigger a CoA (change of authorization) against a Wired client",
    capability=Capability.WRITE,
)
async def mist_reauth_site_dot1x_wired_client(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    client_mac: Annotated[str, Field(description="path parameter 'client_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/wired_clients/{client_mac}/coa",
        path_params={"site_id": site_id, "client_mac": client_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_restore_site_device_backup_version",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/restore_backup_version\n\nrestoreSiteDeviceBackupVersion\n\nRestore device backup fw version (Available on Junos OS EX4000-, EX4100-, EX4400- devices)",
    capability=Capability.WRITE,
)
async def mist_restore_site_device_backup_version(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/restore_backup_version",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_restore_site_multiple_device_backup_version",
    description="POST /api/v1/sites/{site_id}/devices/restore_backup_version\n\nrestoreSiteMultipleDeviceBackupVersion\n\nRestore device backup fw version (Available on Junos OS EX4000-, EX4100-, EX4400- devices)",
    capability=Capability.WRITE,
)
async def mist_restore_site_multiple_device_backup_version(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/restore_backup_version",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_device_arp_table",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_arp\n\nshowSiteDeviceArpTable\n\nGet ARP Table from the Device.\n\nThe output will be available through websocket. As there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```',
    capability=Capability.WRITE,
)
async def mist_show_site_device_arp_table(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_arp",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_toogle_site_device_vc_routing_engines_role",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/vc/switch_master\n\ntoogleSiteDeviceVcRoutingEnginesRole\n\nIn a pre-provisioned VC, mastership is system-determined. This command allows manual toggling between primary and backup Routing Engines.",
    capability=Capability.WRITE,
)
async def mist_toogle_site_device_vc_routing_engines_role(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/vc/switch_master",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_upgrade_device_bios",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/upgrade_bios\n\nupgradeDeviceBios\n\nUpgrade device bios",
    capability=Capability.WRITE,
)
async def mist_upgrade_device_bios(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/upgrade_bios"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/upgrade_bios",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upgrade_device_fpga",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/upgrade_fpga\n\nupgradeDeviceFPGA\n\nUpgrade device fpga",
    capability=Capability.WRITE,
)
async def mist_upgrade_device_fpga(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/upgrade_fpga"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/upgrade_fpga",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upgrade_site_devices_bios",
    description="POST /api/v1/sites/{site_id}/devices/upgrade_bios\n\nupgradeSiteDevicesBios\n\nUpgrade Bios on Multiple Device",
    capability=Capability.WRITE,
)
async def mist_upgrade_site_devices_bios(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/upgrade_bios"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/upgrade_bios",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upgrade_site_devices_fpga",
    description="POST /api/v1/sites/{site_id}/devices/upgrade_fpga\n\nupgradeSiteDevicesFpga\n\nUpgrade Bios on Multiple Device",
    capability=Capability.WRITE,
)
async def mist_upgrade_site_devices_fpga(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/upgrade_fpga"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/upgrade_fpga",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )
