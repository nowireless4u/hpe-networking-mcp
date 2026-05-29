"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Installer``
Operations in this file: 23
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
    name="mist_add_installer_device_image",
    description="POST /api/v1/installer/orgs/{org_id}/devices/{device_mac}/{image_name}\n\naddInstallerDeviceImage\n\nAdd image",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/installer/orgs/{org_id}/devices\n\nclaimInstallerDevices\n\nThis mirrors `POST /api/v1/orgs/{org_id}/inventory` (see Inventory API)",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/{map_id}\n\ncreateInstallerMap\n\nCreate a MAP",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_installer_virtual_chassis(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    fpc0_mac: Annotated[str, Field(description="FPC0 MAC Address")],
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
    description="PUT /api/v1/installer/orgs/{org_id}/sites/{site_name}\n\ncreateOrUpdateInstallerSites\n\nOften the Installers are asked to assign Devices to Sites. The Sites can either be pre-created or created/modified by the Installer. If this is an update, the same grace period also applies.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="DELETE /api/v1/installer/orgs/{org_id}/devices/{device_mac}/{image_name}\n\ndeleteInstallerDeviceImage\n\nDelete image",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    description="DELETE /api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/{map_id}\n\ndeleteInstallerMap\n\nDelete Map",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    description="GET /api/v1/installer/orgs/{org_id}/devices/{fpc0_mac}/vc\n\ngetInstallerDeviceVirtualChassis\n\nGet VC Status\n\nThe API returns a combined view of the VC status which includes topology and stats",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_installer_device_virtual_chassis(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    fpc0_mac: Annotated[str, Field(description="FPC0 MAC Address")],
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
    description="POST /api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/import\n\nimportInstallerMap\n\nImport data from files is a multipart POST which has an file, an optional json, and an optional csv, to create floorplan, assign & place ap if name or mac matches",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="GET /api/v1/installer/orgs/{org_id}/alarmtemplates\n\nlistInstallerAlarmTemplates\n\nGet List of alarm templates",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/installer/orgs/{org_id}/deviceprofiles\n\nlistInstallerDeviceProfiles\n\nGet List of Device Profiles",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_installer_device_profiles(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
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
    description="GET /api/v1/installer/orgs/{org_id}/devices\n\nlistInstallerListOfRecentlyClaimedDevices\n\nGet List of recently claimed devices",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_installer_list_of_recently_claimed_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    model: Annotated[str | None, Field(description="Device Model")] = None,
    site_name: Annotated[str | None, Field(description="Site Name")] = None,
    site_id: Annotated[str | None, Field(description="Site ID")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
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
    description="GET /api/v1/installer/orgs/{org_id}/sites/{site_name}/maps\n\nlistInstallerMaps\n\nGet List of Maps",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/installer/orgs/{org_id}/rftemplates\n\nlistInstallerRfTemplatesNames\n\nGet List of RF Templates",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/installer/orgs/{org_id}/sitegroups\n\nlistInstallerSiteGroups\n\nGet List of Site Groups",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/installer/orgs/{org_id}/sites\n\nlistInstallerSites\n\nGet List of Sites",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/installer/sites/{site_name}/optimize\n\noptimizeInstallerRrm\n\nAfter installation is considered complete (APs are placed on maps, all powered up), you can trigger an optimize operation where RRM will kick in (and maybe other things in the future) before it’s automatically scheduled.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="PUT /api/v1/installer/orgs/{org_id}/devices/{device_mac}\n\nprovisionInstallerDevices\n\nProvision or Replace a device \n\nIf replacing_mac is in the request payload, other attributes are ignored, we attempt to replace existing device (with mac replacing_mac) with the inventory device being configured. The replacement device must be in the inventory but not assigned, and the replacing_mac device must be assigned to a site, and satisfy grace period requirements. The Device replaced will become unassigned.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/installer/orgs/{org_id}/devices/{device_mac}/locate\n\nstartInstallerLocateDevice\n\nLocate a Device by blinking it’s LED, it’s a persisted state that has to be stopped by calling Stop Locating API",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/installer/orgs/{org_id}/devices/{device_mac}/unlocate\n\nstopInstallerLocateDevice\n\nStop it",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="DELETE /api/v1/installer/orgs/{org_id}/devices/{device_mac}\n\nunassignInstallerRecentlyClaimedDevice\n\nUnassign recently claimed devices",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    description="PUT /api/v1/installer/orgs/{org_id}/sites/{site_name}/maps/{map_id}\n\nupdateInstallerMap\n\nUpdate map",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_installer_virtual_chassis_member(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    fpc0_mac: Annotated[str, Field(description="FPC0 MAC Address")],
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
