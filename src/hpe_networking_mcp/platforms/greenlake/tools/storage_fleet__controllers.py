"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/storage-fleet.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``storage-fleet``   Tag: ``controllers``   Operations: 4
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_nodes",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes\n\nDeviceType4NodesList\n\nGet details of HPE Alletra Storage MP B10000 Nodes",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_nodes(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter nodes resource by key.")
    ] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort nodes resource by key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/nodes"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_nodes_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes/{id}\n\nDeviceType4NodesGetById\n\nGet details of HPE Alletra Storage MP B10000 Node identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_nodes_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the node")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/nodes/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_nodes_node_id_component_performance_statistics",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes/{nodeId}/component-performance-statistics\n\nDeviceType4NodeComponentPerformanceStatisticsGet\n\nGet component performance statistics details of HPE Alletra Storage MP B10000 node idenfified by {nodeId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_nodes_node_id_component_performance_statistics(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    nodeId: Annotated[str, Field(description="UID of the node")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/nodes/{path_seg(nodeId)}/component-performance-statistics"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_nodes_id",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes/{id}\n\nDeviceType4NodesLocateById\n\nLocate node of HPE Alletra Storage MP B10000  identified by {id}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_nodes_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the node")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/nodes/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
