"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Inventory``
Operations in this file: 9
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
    name="mist_add_org_inventory",
    description="POST /api/v1/orgs/{org_id}/inventory\n\naddOrgInventory\n\nAdd Device to Org Inventory with the device claim codes",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/inventory/count\n\ncountOrgInventory\n\nCount by Distinct Attributes of in the Org Inventory",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_inventory(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    site_id: Annotated[str | None, Field(description="Site ID")] = None,
    model: Annotated[str | None, Field(description="Device model")] = None,
    version: Annotated[str | None, Field(description="Software version")] = None,
    status: Annotated[Any | None, Field(description="query parameter 'status'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
    description="POST /api/v1/orgs/{org_id}/inventory/create_ha_cluster\n\ncreateOrgGatewayHaCluster\n\nCreate HA Cluster from unassigned Gateways",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_inventory(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    serial: Annotated[str | None, Field(description="Device serial")] = None,
    model: Annotated[str | None, Field(description="Device model")] = None,
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    mac: Annotated[str | None, Field(description="MAC address")] = None,
    site_id: Annotated[str | None, Field(description="Site id if assigned, null if not assigned")] = None,
    vc_mac: Annotated[str | None, Field(description="Virtual Chassis MAC Address")] = None,
    vc: Annotated[bool, Field(description="To display Virtual Chassis members")] = False,
    unassigned: Annotated[bool, Field(description="To display Unassigned devices")] = True,
    modified_after: Annotated[int | None, Field(description="Filter on inventory last modified time, in epoch")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
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
    description="POST /api/v1/orgs/{org_id}/inventory/reevaluate_auto_assignment\n\nreevaluateOrgAutoAssignment\n\nReevaluate Auto Assignment",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/inventory/search\n\nsearchOrgInventory\n\nSearch in the Org Inventory",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_inventory(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    mac: Annotated[
        str | None,
        Field(
            description="MAC address. Partial match allowed with wildcard * (e.g. `*5b35*` will match `5c5b350e0001` and `5c5b35000301`)."
        ),
    ] = None,
    model: Annotated[
        str | None,
        Field(
            description="Partial / full Device model. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `AP4*` and `*P4*` match `AP43`). Suffix-only wildcards (e.g. `*43`) are not supported"
        ),
    ] = None,
    name: Annotated[
        str | None,
        Field(
            description="Device name. Always a partial match (e.g. `london` will match `london-1`, `london-2`, `my-london-device`...)"
        ),
    ] = None,
    site_id: Annotated[str | None, Field(description="Site id if assigned, null if not assigned")] = None,
    serial: Annotated[
        str | None,
        Field(
            description="Device serial number. Partial match allowed with wildcard * (e.g. `*123*` will match `AB123CD`, `12345`, `XY123`)"
        ),
    ] = None,
    master: Annotated[str | None, Field(description="true / false")] = None,
    sku: Annotated[
        str | None,
        Field(
            description="Device SKU. Partial match allowed with wildcard * (e.g. `*2300*` will match `EX2300-F-12P`)"
        ),
    ] = None,
    version: Annotated[
        str | None,
        Field(
            description="Device version. Partial match allowed with wildcard * (e.g. `2R3` will match `21.2R3-S3.5`)"
        ),
    ] = None,
    status: Annotated[Any | None, Field(description="Device status. enum: `connected`, `disconnected`")] = None,
    text: Annotated[str | None, Field(description="Wildcards for name, mac, serial")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
    description="PUT /api/v1/orgs/{org_id}/inventory\n\nupdateOrgInventoryAssignment\n\nUpdate Org Inventory",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
