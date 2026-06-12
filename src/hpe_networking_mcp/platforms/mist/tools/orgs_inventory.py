"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Inventory``
Operations in this file: 9
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
    name="mist_add_org_inventory",
    description="POST /api/v1/orgs/{org_id}/inventory\n\naddOrgInventory\n\nClaim devices into the organization inventory using order activation codes or device claim codes.",
    capability=Capability.WRITE,
)
async def mist_add_org_inventory(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/inventory",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_count_org_inventory",
    description="GET /api/v1/orgs/{org_id}/inventory/count\n\ncountOrgInventory\n\nCount organization inventory records, optionally grouped by `distinct` and filtered by device type, site, model, version, and status.",
    capability=Capability.READ,
)
async def mist_count_org_inventory(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `model`, `status`, `site_id`, `sku`, `version`"
        ),
    ] = None,
    type: Annotated[Any | None, Field(description="Filter results by type. enum: `ap`, `gateway`, `switch`")] = None,
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    model: Annotated[
        str | None, Field(description="Filter results by device model. Accepts multiple comma-separated values.")
    ] = None,
    version: Annotated[str | None, Field(description="Filter results by software version")] = None,
    status: Annotated[
        Any | None, Field(description="Filter results by status. enum: `connected`, `disconnected`")
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/inventory/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "type": type,
            "site_id": site_id,
            "model": model,
            "version": version,
            "status": status,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_create_org_gateway_ha_cluster",
    description="POST /api/v1/orgs/{org_id}/inventory/create_ha_cluster\n\ncreateOrgGatewayHaCluster\n\nCreate a gateway HA cluster from unassigned gateway inventory nodes and assign the cluster to the specified site.",
    capability=Capability.WRITE,
)
async def mist_create_org_gateway_ha_cluster(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/inventory/create_ha_cluster"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/inventory/create_ha_cluster",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_gateway_ha_cluster",
    description="POST /api/v1/orgs/{org_id}/inventory/delete_ha_cluster\n\ndeleteOrgGatewayHaCluster\n\nDelete HA Cluster\n\nAfter HA cluster deleted, both of the nodes will be unassigned.",
    capability=Capability.WRITE,
)
async def mist_delete_org_gateway_ha_cluster(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/inventory/delete_ha_cluster"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/inventory/delete_ha_cluster",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_get_org_inventory",
    description="GET /api/v1/orgs/{org_id}/inventory\n\ngetOrgInventory\n\nGet Org Inventory\n\n### VC (Virtual-Chassis) Management \n\nStarting with the April release, Virtual Chassis devices in Mist will now use\na cloud-assigned virtual MAC address as the device ID, instead of the physical\nMAC address of the FPC0 member.\n\n\n**Retrieving the device ID or Site ID of a Virtual Chassis:**\n\n1. Use this API call with the query parameters `vc=true` and `mac` set to the MAC address of the VC member.\n\n2. In the response, check the `vc_mac` and `mac` fields:\n\n    - If `vc_mac` is empty or not present, the device is not part...",
    capability=Capability.READ,
)
async def mist_get_org_inventory(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    serial: Annotated[
        str | None,
        Field(description="Filter results by device serial number. Accepts multiple comma-separated values."),
    ] = None,
    model: Annotated[
        str | None, Field(description="Filter results by device model. Accepts multiple comma-separated values.")
    ] = None,
    type: Annotated[
        str | None,
        Field(
            description="Filter results by type. enum: `ap`, `gateway`, `switch`. Accepts multiple comma-separated values."
        ),
    ] = None,
    mac: Annotated[
        str | None, Field(description="Filter results by MAC address. Accepts multiple comma-separated values.")
    ] = None,
    site_id: Annotated[
        str | None,
        Field(
            description="Filter results by one site identifier. Use a single value; comma-separated values are not supported"
        ),
    ] = None,
    vc_mac: Annotated[
        str | None, Field(description="Virtual Chassis MAC address. Accepts multiple comma-separated values.")
    ] = None,
    vc: Annotated[bool, Field(description="To display Virtual Chassis members")] = False,
    unassigned: Annotated[bool, Field(description="To display Unassigned devices")] = True,
    modified_after: Annotated[int | None, Field(description="Filter on inventory last modified time, in epoch")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/inventory",
        path_params={"org_id": org_id},
        query_params={
            "serial": serial,
            "model": model,
            "type": type,
            "mac": mac,
            "site_id": site_id,
            "vc_mac": vc_mac,
            "vc": vc,
            "unassigned": unassigned,
            "modified_after": modified_after,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_reevaluate_org_auto_assignment",
    description="POST /api/v1/orgs/{org_id}/inventory/reevaluate_auto_assignment\n\nreevaluateOrgAutoAssignment\n\nRe-run organization inventory auto-assignment rules against devices that are eligible for automatic site assignment.",
    capability=Capability.WRITE,
)
async def mist_reevaluate_org_auto_assignment(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/inventory/reevaluate_auto_assignment",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_replace_org_devices",
    description="POST /api/v1/orgs/{org_id}/inventory/replace\n\nreplaceOrgDevices\n\nIt’s a common request we get from the customers. When a AP HW has problem and need a replacement, they would want to copy the existing attributes (Device Config) of this old AP to the new one. It can be done by providing the MAC of a device that’s currently in the inventory but not assigned. The Device replaced will become unassigned.\n\nThis API also supports replacement of Mist Edges. This API copies device agnostic attributes from old Mist edge to new one.\nMist manufactured Mist Edges will be reset to factory settings but wil...",
    capability=Capability.WRITE,
)
async def mist_replace_org_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/inventory/replace",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_search_org_inventory",
    description="GET /api/v1/orgs/{org_id}/inventory/search\n\nsearchOrgInventory\n\nSearch organization inventory records with filters for type, MAC address, model, name, site, serial number, Virtual Chassis master state, SKU, version, status, and text.",
    capability=Capability.READ,
)
async def mist_search_org_inventory(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[Any | None, Field(description="Filter results by type. enum: `ap`, `gateway`, `switch`")] = None,
    mac: Annotated[
        str | None,
        Field(
            description="Filter by MAC address. Partial matches may use `*` wildcards (e.g. `*5b35*` matches `5c5b350e0001` and `5c5b35000301`). Accepts multiple comma-separated values."
        ),
    ] = None,
    model: Annotated[
        str | None,
        Field(
            description="Partial / full Device model. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `AP4*` and `*P4*` match `AP43`). Suffix-only wildcards (e.g. `*43`) are not supported. Accepts multiple comma-separated values."
        ),
    ] = None,
    name: Annotated[
        str | None,
        Field(
            description="Device name. Always a partial match (e.g. `london` will match `london-1`, `london-2`, `my-london-device`...). Accepts multiple comma-separated values."
        ),
    ] = None,
    site_id: Annotated[
        str | None,
        Field(description="Filter inventory results by site identifier. Accepts multiple comma-separated values."),
    ] = None,
    serial: Annotated[
        str | None,
        Field(
            description="Device serial number. Partial match allowed with wildcard * (e.g. `*123*` will match `AB123CD`, `12345`, `XY123`). Accepts multiple comma-separated values."
        ),
    ] = None,
    master: Annotated[
        str | None, Field(description="Filter inventory results by whether the device is the Virtual Chassis master")
    ] = None,
    sku: Annotated[
        str | None,
        Field(
            description="Device SKU. Partial match allowed with wildcard * (e.g. `*2300*` will match `EX2300-F-12P`). Accepts multiple comma-separated values."
        ),
    ] = None,
    version: Annotated[
        str | None,
        Field(
            description="Device version. Partial match allowed with wildcard * (e.g. `2R3` will match `21.2R3-S3.5`). Accepts multiple comma-separated values."
        ),
    ] = None,
    status: Annotated[
        str | None,
        Field(description="Device status. enum: `connected`, `disconnected`. Accepts multiple comma-separated values."),
    ] = None,
    text: Annotated[str | None, Field(description="Wildcards for name, mac, serial")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
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
        "/api/v1/orgs/{org_id}/inventory/search",
        path_params={"org_id": org_id},
        query_params={
            "type": type,
            "mac": mac,
            "model": model,
            "name": name,
            "site_id": site_id,
            "serial": serial,
            "master": master,
            "sku": sku,
            "version": version,
            "status": status,
            "text": text,
            "limit": limit,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_inventory_assignment",
    description="PUT /api/v1/orgs/{org_id}/inventory\n\nupdateOrgInventoryAssignment\n\nUpdate inventory assignment for one or more devices, such as assigning them to a site, unassigning them, or deleting inventory records by MAC address or serial number.",
    capability=Capability.WRITE,
)
async def mist_update_org_inventory_assignment(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/inventory")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/inventory",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
