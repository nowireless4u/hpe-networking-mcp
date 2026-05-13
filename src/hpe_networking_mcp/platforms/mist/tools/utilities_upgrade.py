"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Utilities Upgrade``
Operations in this file: 29
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
    name="mist_cancel_org_device_upgrade",
    description="POST /api/v1/orgs/{org_id}/devices/upgrade/{upgrade_id}/cancel\n\ncancelOrgDeviceUpgrade\n\nBest effort to cancel an upgrade. Devices which are already upgraded wont be touched",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/mxedges/upgrade/{upgrade_id}/cancel\n\ncancelOrgMxEdgeUpgrade\n\nCancel Mist Edge Upgrade. Best effort to cancel an upgrade. Devices which are already upgraded won't be touched.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/ssr/upgrade/{upgrade_id}/cancel\n\ncancelOrgSsrUpgrade\n\nBest effort to cancel an upgrade. Devices which are already upgraded wont be touched↵",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/devices/upgrade/{upgrade_id}\n\ngetOrgDeviceUpgrade\n\nGet Multiple Devices Upgrade",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/mxedges/upgrade/{upgrade_id}\n\ngetOrgMxEdgeUpgrade\n\nGet Mist Edge Upgrade",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/ssr/upgrade/{upgrade_id}/cancel\n\ngetOrgSsrUpgrade\n\nGet Specific Org SSR Upgrade",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/devices/versions\n\nlistOrgAvailableDeviceVersions\n\nGet List of Available Device Versions",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_available_device_versions(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
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
        "/api/v1/orgs/{org_id}/devices/versions",
        path_params={"org_id": org_id},
        query_params={"type": type, "model": model},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_available_ssr_versions",
    description="GET /api/v1/orgs/{org_id}/ssr/versions\n\nlistOrgAvailableSsrVersions\n\nGet available version for SSR",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_available_ssr_versions(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    channel: Annotated[Any | None, Field(description="SSR version channel")] = None,
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
    description="GET /api/v1/orgs/{org_id}/devices/upgrade\n\nlistOrgDeviceUpgrades\n\nGet List of Org multiple devices upgrades",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/mxedges/upgrade\n\nlistOrgMxEdgeUpgrades\n\nGet List of Org Mist Edge Upgrades",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/ssr/upgrade\n\nlistOrgSsrUpgrades\n\nGet List of Org SSR Upgrades",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/sites/{site_id}/devices/versions\n\nlistSiteAvailableDeviceVersions\n\nGet List of Available Device Versions",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_available_device_versions(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
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
    description="GET /api/v1/sites/{site_id}/devices/upgrade\n\nlistSiteDeviceUpgrades\n\nGet all upgrades for site",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_device_upgrades(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    status: Annotated[Any | None, Field(description="query parameter 'status'")] = None,
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
    description="GET /api/v1/sites/{site_id}/mxedges/upgrade\n\nlistSiteMxEdgeUpgrades\n\nGet List of Site Mist Edge Upgrades",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="PUT /api/v1/orgs/{org_id}/mxedges/upgrade/{upgrade_id}\n\nupdateOrgMxEdgeUpgrade\n\nUpdate Mist Edge Upgrade. Only upgrades in `queued` state can be updated.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/devices/upgrade\n\nupgradeOrgDevices\n\nUpgrade Multiple Sites (Only supported for Access Points upgrades)",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/jsi/devices/{device_mac}/upgrade\n\nupgradeOrgJsiDevice\n\nUpgrade",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/mxedges/upgrade\n\nupgradeOrgMxEdges\n\nUpgrade Mist Edges",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/ssr/upgrade\n\nupgradeOrgSsrs\n\nUpgrade Org SSRs",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
