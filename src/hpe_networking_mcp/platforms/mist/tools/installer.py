"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Installer``
Operations in this file: 23
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
    name="mist_add_installer_device_image",
    description="POST /api/v1/installer/orgs/{org_id}/devices/{device_mac}/{image_name}\n\naddInstallerDeviceImage\n\nUpload an image associated with an installer-managed device using `multipart/form-data`.",
    capability=Capability.WRITE,
)
async def mist_add_installer_device_image(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    image_name: Annotated[str, Field(description="path parameter 'image_name'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/installer/orgs/{org_id}/devices/{device_mac}/{image_name}",
        path_params={"org_id": org_id, "image_name": image_name, "device_mac": device_mac},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_claim_installer_devices",
    description="POST /api/v1/installer/orgs/{org_id}/devices\n\nclaimInstallerDevices\n\nClaim devices into the organization inventory by activation code through the installer workflow.",
    capability=Capability.WRITE,
)
async def mist_claim_installer_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/installer/orgs/{org_id}/devices",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_installer_map",
    description="POST /api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/{map_id}\n\ncreateInstallerMap\n\nDefine a map or floorplan for an installer-managed site, including metadata used for AP placement and site visualization.",
    capability=Capability.WRITE,
)
async def mist_create_installer_map(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_name: Annotated[str, Field(description="path parameter 'site_name'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/{map_id}",
        path_params={"org_id": org_id, "site_name": site_name, "map_id": map_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_installer_virtual_chassis",
    description="POST /api/v1/installer/orgs/{org_id}/devices/{fpc0_mac}/vc\n\ncreateInstallerVirtualChassis\n\nFor models (e.g. EX3400 and up) having dedicated VC ports, it is easier to form a VC by just connecting cables with the dedicated VC ports. Cloud will detect the new VC and update the inventory.\n\nIn case that the user would like to choose the dedicated switch as a VC master or for EX2300-C-12P and EX2300-C-12T which doesn't have dedicated VC ports, below are procedures to automate the VC creation:\n\n1. Power on the switch that is chosen as the VC master first. And then powering on the other member swit...",
    capability=Capability.WRITE,
)
async def mist_create_installer_virtual_chassis(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    fpc0_mac: Annotated[str, Field(description="FPC0 MAC address")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/installer/orgs/{org_id}/devices/{fpc0_mac}/vc",
        path_params={"org_id": org_id, "fpc0_mac": fpc0_mac},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_or_update_installer_sites",
    description="PUT /api/v1/installer/orgs/{org_id}/sites/{site_name}\n\ncreateOrUpdateInstallerSites\n\nUse `site_name` to create a site when it does not exist, or to update installer-editable fields on an existing site. Installers use these sites for device assignment, and grace-period rules also apply when updating an existing site.",
    capability=Capability.WRITE,
)
async def mist_create_or_update_installer_sites(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_name: Annotated[str, Field(description="path parameter 'site_name'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/installer/orgs/{org_id}/sites/{site_name}",
        path_params={"org_id": org_id, "site_name": site_name},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_installer_device_image",
    description="DELETE /api/v1/installer/orgs/{org_id}/devices/{device_mac}/{image_name}\n\ndeleteInstallerDeviceImage\n\nRemove a previously uploaded image associated with an installer-managed device, such as an installation photo or device placement image.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_installer_device_image(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    image_name: Annotated[str, Field(description="path parameter 'image_name'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/installer/orgs/{org_id}/devices/{device_mac}/{image_name}",
        path_params={"org_id": org_id, "image_name": image_name, "device_mac": device_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_installer_map",
    description="DELETE /api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/{map_id}\n\ndeleteInstallerMap\n\nRemove a map or floorplan from an installer-managed site. This removes the map used for AP placement, but does not delete the site.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_installer_map(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_name: Annotated[str, Field(description="path parameter 'site_name'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/{map_id}",
        path_params={"org_id": org_id, "site_name": site_name, "map_id": map_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_installer_device_virtual_chassis",
    description="GET /api/v1/installer/orgs/{org_id}/devices/{fpc0_mac}/vc\n\ngetInstallerDeviceVirtualChassis\n\nReturn Virtual Chassis status for an installer-managed switch, including topology and member statistics.\n\nThe response is a combined view of the Virtual Chassis state.",
    capability=Capability.READ,
)
async def mist_get_installer_device_virtual_chassis(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    fpc0_mac: Annotated[str, Field(description="FPC0 MAC address")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/installer/orgs/{org_id}/devices/{fpc0_mac}/vc",
        path_params={"org_id": org_id, "fpc0_mac": fpc0_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_import_installer_map",
    description="POST /api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/import\n\nimportInstallerMap\n\nImport a site floorplan and optional placement data from multipart files. The request can include an image file, optional JSON, and optional CSV data to create the map and assign or place APs when names or MAC addresses match.",
    capability=Capability.WRITE,
)
async def mist_import_installer_map(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_name: Annotated[str, Field(description="path parameter 'site_name'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/import",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/import",
        path_params={"org_id": org_id, "site_name": site_name},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_list_installer_alarm_templates",
    description="GET /api/v1/installer/orgs/{org_id}/alarmtemplates\n\nlistInstallerAlarmTemplates\n\nReturn alarm templates available to installer workflows in the organization.",
    capability=Capability.READ,
)
async def mist_list_installer_alarm_templates(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/installer/orgs/{org_id}/alarmtemplates",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_installer_device_profiles",
    description="GET /api/v1/installer/orgs/{org_id}/deviceprofiles\n\nlistInstallerDeviceProfiles\n\nReturn device profiles that installers can use when provisioning recently claimed devices, optionally filtered by device type.",
    capability=Capability.READ,
)
async def mist_list_installer_device_profiles(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[Any | None, Field(description="Filter results by type. enum: `ap`, `gateway`, `switch`")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/installer/orgs/{org_id}/deviceprofiles",
        path_params={"org_id": org_id},
        query_params={"type": type},
        body=None,
    )


@_mcp_tool(
    name="mist_list_installer_list_of_recently_claimed_devices",
    description="GET /api/v1/installer/orgs/{org_id}/devices\n\nlistInstallerListOfRecentlyClaimedDevices\n\nReturn recently claimed devices visible to installer workflows, with optional filters for model, site name, or site identifier.",
    capability=Capability.READ,
)
async def mist_list_installer_list_of_recently_claimed_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    model: Annotated[str | None, Field(description="Filter results by device model")] = None,
    site_name: Annotated[str | None, Field(description="Filter results by site name")] = None,
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/installer/orgs/{org_id}/devices",
        path_params={"org_id": org_id},
        query_params={"model": model, "site_name": site_name, "site_id": site_id, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_installer_maps",
    description="GET /api/v1/installer/orgs/{org_id}/sites/{site_name}/maps\n\nlistInstallerMaps\n\nReturn maps for an installer-managed site, used for floorplan selection and AP placement during provisioning.",
    capability=Capability.READ,
)
async def mist_list_installer_maps(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_name: Annotated[str, Field(description="path parameter 'site_name'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/installer/orgs/{org_id}/sites/{site_name}/maps",
        path_params={"org_id": org_id, "site_name": site_name},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_installer_rf_templates_names",
    description="GET /api/v1/installer/orgs/{org_id}/rftemplates\n\nlistInstallerRfTemplatesNames\n\nReturn RF template names available to installer workflows for site creation or updates.",
    capability=Capability.READ,
)
async def mist_list_installer_rf_templates_names(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/installer/orgs/{org_id}/rftemplates",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_installer_site_groups",
    description="GET /api/v1/installer/orgs/{org_id}/sitegroups\n\nlistInstallerSiteGroups\n\nReturn site groups that installers can assign when creating or updating sites.",
    capability=Capability.READ,
)
async def mist_list_installer_site_groups(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/installer/orgs/{org_id}/sitegroups",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_installer_sites",
    description="GET /api/v1/installer/orgs/{org_id}/sites\n\nlistInstallerSites\n\nReturn sites visible to installer workflows for device assignment and map operations.",
    capability=Capability.READ,
)
async def mist_list_installer_sites(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/installer/orgs/{org_id}/sites",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_optimize_installer_rrm",
    description="GET /api/v1/installer/sites/{site_name}/optimize\n\noptimizeInstallerRrm\n\nTrigger RF optimization after installation is complete, such as after APs have been placed on maps and powered on. This starts RRM before the next automatic optimization schedule.",
    capability=Capability.READ,
)
async def mist_optimize_installer_rrm(
    ctx: Context,
    site_name: Annotated[str, Field(description="path parameter 'site_name'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/installer/sites/{site_name}/optimize",
        path_params={"site_name": site_name},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_provision_installer_devices",
    description="PUT /api/v1/installer/orgs/{org_id}/devices/{device_mac}\n\nprovisionInstallerDevices\n\nProvision or replace an installer-managed device. \n\nIf replacing_mac is in the request payload, other attributes are ignored, we attempt to replace existing device (with MAC address `replacing_mac`) with the inventory device being configured. The replacement device must be in the inventory but not assigned, and the replacing_mac device must be assigned to a site, and satisfy grace period requirements. The Device replaced will become unassigned.",
    capability=Capability.WRITE,
)
async def mist_provision_installer_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/installer/orgs/{org_id}/devices/{device_mac}",
        path_params={"org_id": org_id, "device_mac": device_mac},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_start_installer_locate_device",
    description="POST /api/v1/installer/orgs/{org_id}/devices/{device_mac}/locate\n\nstartInstallerLocateDevice\n\nStart locating an installer-managed device by blinking its LED. The locate state persists until [Stop Locating Installer Device](/#operations/stopInstallerLocateDevice) is called.",
    capability=Capability.WRITE,
)
async def mist_start_installer_locate_device(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/installer/orgs/{org_id}/devices/{device_mac}/locate",
        path_params={"org_id": org_id, "device_mac": device_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_stop_installer_locate_device",
    description="POST /api/v1/installer/orgs/{org_id}/devices/{device_mac}/unlocate\n\nstopInstallerLocateDevice\n\nStop the locate LED state for an installer-managed device.",
    capability=Capability.WRITE,
)
async def mist_stop_installer_locate_device(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/installer/orgs/{org_id}/devices/{device_mac}/unlocate",
        path_params={"org_id": org_id, "device_mac": device_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_unassign_installer_recently_claimed_device",
    description="DELETE /api/v1/installer/orgs/{org_id}/devices/{device_mac}\n\nunassignInstallerRecentlyClaimedDevice\n\nUnassign a recently claimed device from its current site so it can be provisioned again through the installer workflow.",
    capability=Capability.WRITE_DELETE,
)
async def mist_unassign_installer_recently_claimed_device(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/installer/orgs/{org_id}/devices/{device_mac}",
        path_params={"org_id": org_id, "device_mac": device_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_installer_map",
    description="PUT /api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/{map_id}\n\nupdateInstallerMap\n\nModify map or floorplan metadata for an installer-managed site, including dimensions, orientation, and placement-related settings.",
    capability=Capability.WRITE,
)
async def mist_update_installer_map(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_name: Annotated[str, Field(description="path parameter 'site_name'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/{map_id}",
        path_params={"org_id": org_id, "site_name": site_name, "map_id": map_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_installer_virtual_chassis_member",
    description="PUT /api/v1/installer/orgs/{org_id}/devices/{fpc0_mac}/vc\n\nupdateInstallerVirtualChassisMember\n\nThe VC creation and adding member switch API will update the device’ s virtual chassis config which is applied after VC is formed to create JUNOS pre-provisioned virtual chassis configuration.\n\n## Change to use preprovisioned VC\nTo switch the VC to use preprovisioned VC, enable preprovisioned in virtual_chassis config. Both vc_role master and backup will be matched to routing-engine role in Junos preprovisioned VC config.\n\nIn this config, fpc0 has to be the same as the mac of device_id. Use renum...",
    capability=Capability.WRITE,
)
async def mist_update_installer_virtual_chassis_member(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    fpc0_mac: Annotated[str, Field(description="FPC0 MAC address")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/installer/orgs/{org_id}/devices/{fpc0_mac}/vc",
        path_params={"org_id": org_id, "fpc0_mac": fpc0_mac},
        query_params=None,
        body=body,
    )
