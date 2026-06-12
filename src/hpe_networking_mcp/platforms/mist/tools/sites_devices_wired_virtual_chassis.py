"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Devices - Wired - Virtual Chassis``
Operations in this file: 7
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
    name="mist_change_site_switch_vc_port_mode",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/set_vc_port_mode\n\nchangeSiteSwitchVcPortMode\n\nChange VCP port mode\n\n\nSome switch model allows changing VCP port behaviors, e.g. - use them as regular network ports - change vcp protocol Note, this command will reboot the switch",
    capability=Capability.WRITE,
)
async def mist_change_site_switch_vc_port_mode(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/set_vc_port_mode",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_convert_site_virtual_chassis_to_virtual_mac",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/vc/convert_to_virtualmac\n\nconvertSiteVirtualChassisToVirtualMac\n\nConverts an FPC0-based VC to a Virtualmac VC, removing the limitation where the device ID must change whenever FPC0 is renumbered or removed.\n\n\nHTTP400 Error possible reasons:\n  - The device is not an OC device\n  - Virtualmac VC is disabled in the Org Knob settings\n  - The VC is already a Virtualmac VC\n  - The VC is currently disconnected\n  - The device is standalone\n  - A new FPC0 exists with its own device config, causing ambiguity.",
    capability=Capability.WRITE,
)
async def mist_convert_site_virtual_chassis_to_virtual_mac(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/vc/convert_to_virtualmac",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_create_site_virtual_chassis",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/vc\n\ncreateSiteVirtualChassis\n\nFor models (e.g. EX3400 and up) having dedicated VC ports, it is easier to form a VC by just connecting cables with the dedicated VC ports. Cloud will detect the new VC and update the inventory.  \nIn case that the user would like to choose the dedicated switch as a VC master or for EX2300-C-12P and EX2300-C-12T which doesn't have dedicated VC ports, below are procedures to automate the VC creation:\n1. Power on the switch that is chosen as the VC master first, and then powering on the other member switches.\n2. Cla...",
    capability=Capability.WRITE,
)
async def mist_create_site_virtual_chassis(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/vc",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_virtual_chassis",
    description="DELETE /api/v1/sites/{site_id}/devices/{device_id}/vc\n\ndeleteSiteVirtualChassis\n\nWhen all the member switches of VC are removed and only member ID 0 is left, the cloud would detect this situation and automatically changes the single switch to non-VC role.\n\nFor some unexpected cases that the VC is gone and disconnected, the API below could be used to change the state of VC’s switches to be standalone. After it is executed, all the switches will be shown as standalone switches under Inventory.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_site_virtual_chassis(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/devices/{device_id}/vc",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_device_virtual_chassis",
    description="GET /api/v1/sites/{site_id}/devices/{device_id}/vc\n\ngetSiteDeviceVirtualChassis\n\nGet VC Status\n\nThe API returns a combined view of the VC status which includes topology and stats_",
    capability=Capability.READ,
)
async def mist_get_site_device_virtual_chassis(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices/{device_id}/vc",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_set_site_vc_port",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/vc/vc_port\n\nsetSiteVcPort\n\nSet VC port",
    capability=Capability.WRITE,
)
async def mist_set_site_vc_port(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/vc/vc_port"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/vc/vc_port",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_site_virtual_chassis_member",
    description="PUT /api/v1/sites/{site_id}/devices/{device_id}/vc\n\nupdateSiteVirtualChassisMember\n\nThe VC creation and adding member switch API will update the device' s virtual chassis config which is applied after VC is formed to create JUNOS pre-provisioned virtual chassis configuration.\n\n**Note:** Update Device's VC config can achieve similar purpose by directly modifying current virtual_chassis config. However, it cannot fulfill requests to enabling vc_ports on new members that are yet to belong to current VC.\n\n\n## Change to use preprovisioned VC\nTo switch the VC to use preprovisioned VC, enable prep...",
    capability=Capability.WRITE,
)
async def mist_update_site_virtual_chassis_member(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/devices/{device_id}/vc",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )
