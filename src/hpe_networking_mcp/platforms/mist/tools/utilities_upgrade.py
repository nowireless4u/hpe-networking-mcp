"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Utilities Upgrade``
Operations in this file: 29
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
    name="mist_cancel_org_device_upgrade",
    description="POST /api/v1/orgs/{org_id}/devices/upgrade/{upgrade_id}/cancel\n\ncancelOrgDeviceUpgrade\n\nCancel an organization-level device upgrade job on a best-effort basis. Devices that have already completed the upgrade are not changed.",
    capability=Capability.WRITE,
)
async def mist_cancel_org_device_upgrade(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/devices/upgrade/{upgrade_id}/cancel",
        path_params={"org_id": org_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_cancel_org_mx_edge_upgrade",
    description="POST /api/v1/orgs/{org_id}/mxedges/upgrade/{upgrade_id}/cancel\n\ncancelOrgMxEdgeUpgrade\n\nCancel a Mist Edge upgrade request on a best-effort basis. Mist Edges that have already been upgraded are not changed.",
    capability=Capability.WRITE,
)
async def mist_cancel_org_mx_edge_upgrade(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/upgrade/{upgrade_id}/cancel",
        path_params={"org_id": org_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_cancel_org_ssr_upgrade",
    description="POST /api/v1/orgs/{org_id}/ssr/upgrade/{upgrade_id}/cancel\n\ncancelOrgSsrUpgrade\n\nCancel an SSR firmware upgrade job on a best-effort basis. Devices that have already upgraded are not changed.",
    capability=Capability.WRITE,
)
async def mist_cancel_org_ssr_upgrade(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/ssr/upgrade/{upgrade_id}/cancel",
        path_params={"org_id": org_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_cancel_site_device_upgrade",
    description="POST /api/v1/sites/{site_id}/devices/upgrade/{upgrade_id}/cancel\n\ncancelSiteDeviceUpgrade\n\nBest effort to cancel an upgrade. Devices which are already upgraded wont be touched",
    capability=Capability.WRITE,
)
async def mist_cancel_site_device_upgrade(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/upgrade/{upgrade_id}/cancel",
        path_params={"site_id": site_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_cancel_site_mx_edge_upgrade",
    description="POST /api/v1/sites/{site_id}/mxedges/upgrade/{upgrade_id}/cancel\n\ncancelSiteMxEdgeUpgrade\n\nCancel Mist Edge Upgrade. Best effort to cancel an upgrade. MxEdges which are already upgraded won't be touched.",
    capability=Capability.WRITE,
)
async def mist_cancel_site_mx_edge_upgrade(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/mxedges/upgrade/{upgrade_id}/cancel",
        path_params={"site_id": site_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_device_upgrade",
    description="GET /api/v1/orgs/{org_id}/devices/upgrade/{upgrade_id}\n\ngetOrgDeviceUpgrade\n\nRetrieve details for an organization-level device upgrade job, including per-site upgrade status and device targets.",
    capability=Capability.READ,
)
async def mist_get_org_device_upgrade(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/devices/upgrade/{upgrade_id}",
        path_params={"org_id": org_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_mx_edge_upgrade",
    description="GET /api/v1/orgs/{org_id}/mxedges/upgrade/{upgrade_id}\n\ngetOrgMxEdgeUpgrade\n\nRetrieve status, rollout strategy, target versions, and target counts for a specific Mist Edge upgrade request.",
    capability=Capability.READ,
)
async def mist_get_org_mx_edge_upgrade(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/mxedges/upgrade/{upgrade_id}",
        path_params={"org_id": org_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_ssr_upgrade",
    description="GET /api/v1/orgs/{org_id}/ssr/upgrade/{upgrade_id}/cancel\n\ngetOrgSsrUpgrade\n\nReturn detailed status for an SSR firmware upgrade job, including target device IDs grouped by upgrade status.",
    capability=Capability.READ,
)
async def mist_get_org_ssr_upgrade(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ssr/upgrade/{upgrade_id}/cancel",
        path_params={"org_id": org_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_device_upgrade",
    description="GET /api/v1/sites/{site_id}/devices/upgrade/{upgrade_id}\n\ngetSiteDeviceUpgrade\n\nGet Site Device Upgrade",
    capability=Capability.READ,
)
async def mist_get_site_device_upgrade(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices/upgrade/{upgrade_id}",
        path_params={"site_id": site_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_mx_edge_upgrade",
    description="GET /api/v1/sites/{site_id}/mxedges/upgrade/{upgrade_id}\n\ngetSiteMxEdgeUpgrade\n\nGet Mist Edge Upgrade",
    capability=Capability.READ,
)
async def mist_get_site_mx_edge_upgrade(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/mxedges/upgrade/{upgrade_id}",
        path_params={"site_id": site_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_ssr_upgrade",
    description="GET /api/v1/sites/{site_id}/ssr/upgrade/{upgrade_id}\n\ngetSiteSsrUpgrade\n\nGet Specific Site SSR Upgrade",
    capability=Capability.READ,
)
async def mist_get_site_ssr_upgrade(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/ssr/upgrade/{upgrade_id}",
        path_params={"site_id": site_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_available_device_versions",
    description="GET /api/v1/orgs/{org_id}/devices/versions\n\nlistOrgAvailableDeviceVersions\n\nList available firmware versions for organization devices, optionally filtered by device type and model.",
    capability=Capability.READ,
)
async def mist_list_org_available_device_versions(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[Any | None, Field(description="Filter results by type. enum: `ap`, `gateway`, `switch`")] = None,
    model: Annotated[
        str | None,
        Field(
            description="Fetch version for device model, use/combine with `type` as needed (for switch and gateway devices). Accepts multiple comma-separated values."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/devices/versions",
        path_params={"org_id": org_id},
        query_params={"type": type, "model": model},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_available_ssr_versions",
    description="GET /api/v1/orgs/{org_id}/ssr/versions\n\nlistOrgAvailableSsrVersions\n\nList SSR firmware versions available for upgrade, optionally filtered by release channel and one or more SSR MAC addresses.",
    capability=Capability.READ,
)
async def mist_list_org_available_ssr_versions(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    channel: Annotated[
        Any | None,
        Field(description="SSR release channel used to filter available versions. enum: `alpha`, `beta`, `stable`"),
    ] = None,
    mac: Annotated[str | None, Field(description="Optional. MAC address, or comma separated MAC address list.")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ssr/versions",
        path_params={"org_id": org_id},
        query_params={"channel": channel, "mac": mac},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_device_upgrades",
    description="GET /api/v1/orgs/{org_id}/devices/upgrade\n\nlistOrgDeviceUpgrades\n\nList organization-level device upgrade jobs, including the site-level upgrade jobs created under each organization upgrade.",
    capability=Capability.READ,
)
async def mist_list_org_device_upgrades(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/devices/upgrade",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_mx_edge_upgrades",
    description="GET /api/v1/orgs/{org_id}/mxedges/upgrade\n\nlistOrgMxEdgeUpgrades\n\nList Mist Edge upgrade requests for the organization, including status, rollout strategy, target versions, and per-status target counts.",
    capability=Capability.READ,
)
async def mist_list_org_mx_edge_upgrades(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/mxedges/upgrade",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_ssr_upgrades",
    description="GET /api/v1/orgs/{org_id}/ssr/upgrade\n\nlistOrgSsrUpgrades\n\nList SSR firmware upgrade jobs for the organization, including status, rollout strategy, target versions, release channel, and device counts.",
    capability=Capability.READ,
)
async def mist_list_org_ssr_upgrades(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ssr/upgrade",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_available_device_versions",
    description="GET /api/v1/sites/{site_id}/devices/versions\n\nlistSiteAvailableDeviceVersions\n\nList firmware versions available for devices in a site, optionally filtered by device type and model. Use [List Org Available Device Versions](/#operations/listOrgAvailableDeviceVersions) to retrieve available device versions across the organization.",
    capability=Capability.READ,
)
async def mist_list_site_available_device_versions(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[Any | None, Field(description="Filter results by type. enum: `ap`, `gateway`, `switch`")] = None,
    model: Annotated[
        str | None,
        Field(
            description="Fetch version for device model, use/combine with `type` as needed (for switch and gateway devices)"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices/versions",
        path_params={"site_id": site_id},
        query_params={"type": type, "model": model},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_device_upgrades",
    description="GET /api/v1/sites/{site_id}/devices/upgrade\n\nlistSiteDeviceUpgrades\n\nList device upgrade operations for a site, optionally filtered by upgrade status. Use [List Org Device Upgrades](/#operations/listOrgDeviceUpgrades) to retrieve device upgrade operations across the organization.",
    capability=Capability.READ,
)
async def mist_list_site_device_upgrades(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    status: Annotated[
        Any | None,
        Field(
            description="Filter results by status. enum: `cancelled`, `completed`, `created`, `downloaded`, `downloading`, `failed`, `queued`, `upgrading`"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices/upgrade",
        path_params={"site_id": site_id},
        query_params={"status": status},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_mx_edge_upgrades",
    description="GET /api/v1/sites/{site_id}/mxedges/upgrade\n\nlistSiteMxEdgeUpgrades\n\nList Mist Edge upgrade operations for a site. Use [List Org Mist Edge Upgrades](/#operations/listOrgMxEdgeUpgrades) to retrieve Mist Edge upgrade operations across the organization.",
    capability=Capability.READ,
)
async def mist_list_site_mx_edge_upgrades(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/mxedges/upgrade",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_mx_edge_upgrade",
    description="PUT /api/v1/orgs/{org_id}/mxedges/upgrade/{upgrade_id}\n\nupdateOrgMxEdgeUpgrade\n\nUpdate a queued Mist Edge upgrade request, such as target versions, rollout strategy, start time, or target Mist Edge IDs. Only upgrades in `queued` state can be updated.",
    capability=Capability.WRITE,
)
async def mist_update_org_mx_edge_upgrade(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/mxedges/upgrade/{upgrade_id}",
        path_params={"org_id": org_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_site_mx_edge_upgrade",
    description="PUT /api/v1/sites/{site_id}/mxedges/upgrade/{upgrade_id}\n\nupdateSiteMxEdgeUpgrade\n\nUpdate Mist Edge Upgrade. Only upgrades in `queued` state can be updated.",
    capability=Capability.WRITE,
)
async def mist_update_site_mx_edge_upgrade(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    upgrade_id: Annotated[str, Field(description="path parameter 'upgrade_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/mxedges/upgrade/{upgrade_id}",
        path_params={"site_id": site_id, "upgrade_id": upgrade_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upgrade_device",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/upgrade\n\nupgradeDevice\n\nDevice Upgrade",
    capability=Capability.WRITE,
)
async def mist_upgrade_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/upgrade"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/upgrade",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upgrade_org_devices",
    description="POST /api/v1/orgs/{org_id}/devices/upgrade\n\nupgradeOrgDevices\n\nStart an organization-level device upgrade job across selected sites. The request selects device type, sites, models, firmware versions, and upgrade strategy; AP-specific and Junos-specific options apply only where supported.",
    capability=Capability.WRITE,
)
async def mist_upgrade_org_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/devices/upgrade"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/devices/upgrade",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upgrade_org_jsi_device",
    description="POST /api/v1/orgs/{org_id}/jsi/devices/{device_mac}/upgrade\n\nupgradeOrgJsiDevice\n\nStart a software upgrade for a JSI-connected device identified by MAC address using the requested target version.",
    capability=Capability.WRITE,
)
async def mist_upgrade_org_jsi_device(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/jsi/devices/{device_mac}/upgrade"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/jsi/devices/{device_mac}/upgrade",
        path_params={"org_id": org_id, "device_mac": device_mac},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upgrade_org_mx_edges",
    description="POST /api/v1/orgs/{org_id}/mxedges/upgrade\n\nupgradeOrgMxEdges\n\nSchedule a Mist Edge upgrade for selected Mist Edges, using service target versions or an optional Linux distro upgrade with rollout strategy and canary settings.",
    capability=Capability.WRITE,
)
async def mist_upgrade_org_mx_edges(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/upgrade",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upgrade_org_ssrs",
    description="POST /api/v1/orgs/{org_id}/ssr/upgrade\n\nupgradeOrgSsrs\n\nCreate an SSR firmware upgrade job for selected devices, with firmware version or channel, rollout strategy, and optional download or reboot timing.",
    capability=Capability.WRITE,
)
async def mist_upgrade_org_ssrs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/ssr/upgrade"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/ssr/upgrade",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upgrade_site_devices",
    description="POST /api/v1/sites/{site_id}/devices/upgrade\n\nupgradeSiteDevices\n\nUpgrade Site Device\n\n**Note**: this call doesn’t guarantee the devices to be upgraded right away (they may be offline)",
    capability=Capability.WRITE,
)
async def mist_upgrade_site_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/upgrade",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upgrade_site_mx_edges",
    description="POST /api/v1/sites/{site_id}/mxedges/upgrade\n\nupgradeSiteMxEdges\n\nUpgrade Mist Edges in a Site.\n\nSee [Org Mist Edges](/#tag/Utilities-Upgrade/operation/upgradeOrgMxEdges) for package upgrades\n\nSee [Org Mist Edges Distro](/#tag/Utilities-Upgrade/operation/upgradeOrgMxEdges) for distro upgrades",
    capability=Capability.WRITE,
)
async def mist_upgrade_site_mx_edges(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/mxedges/upgrade",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upgrade_ssr",
    description="POST /api/v1/sites/{site_id}/ssr/{device_id}/upgrade\n\nupgradeSsr\n\nUpgrade Site SSR device",
    capability=Capability.WRITE,
)
async def mist_upgrade_ssr(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/ssr/{device_id}/upgrade"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/ssr/{device_id}/upgrade",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )
