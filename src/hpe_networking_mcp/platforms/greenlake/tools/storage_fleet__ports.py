"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/storage-fleet.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``storage-fleet``   Tag: ``ports``   Operations: 11
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports\n\nDeviceType4PortsList\n\nGet details of HPE Alletra Storage MP B10000 Ports",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter ports by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort ports by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/ports"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}\n\nDeviceType4PortsGetById\n\nGet details of HPE Alletra Storage MP B10000 Port identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the port")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/ports/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_performance",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports-performance\n\nDeviceType4PortsPerformanceHistoryGet\n\nGet details of performance metrics of host ports on storage system identified by {systemid}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_performance(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    report_type: Annotated[
        str | None,
        Field(
            default=None,
            description="parameter will be set to report type requested. For api users, set parameter as ApiUser",
        ),
    ] = None,
    range: Annotated[
        str | None,
        Field(default=None, description="range will define start and end time in which query has to be made."),
    ] = None,
    time_interval_min: Annotated[
        int | None, Field(default=None, description="It defines granularity in minutes.")
    ] = None,
    compare_by: Annotated[
        str | None,
        Field(
            default=None,
            description="compareBy will define top and compare metrics for which query has to be made. Allowed values: `readIops, writeIops, totalIops, readThroughput, writeThroughput, totalThroughput, readLatency, writeLatency, totalLatency, readIosize, writeIosize, totalIosize, totalQlen, avgBusy`",
        ),
    ] = None,
    group_by: Annotated[
        str | None,
        Field(
            default=None,
            description="groupBy will define comma separated groupBy parameters. By default, groupBy will be set to `nsp`. If groupBy is used along with filter query parameter, only following combination are allowed: * `filter: port_type eq host` then groupBy should be `port_type` * `filter: port_type eq peer` then groupBy should be `port_type` * `filter: nsp eq 0:3:1` then groupBy should be `nsp` * `filter: port_type eq host and nsp eq 0:3:1` then groupBy should be `port_type, nsp` * `filter: port_type eq peer and nsp eq 0:3:1` then groupBy should be `port_type, nsp`",
        ),
    ] = None,
    metric_type: Annotated[
        str | None, Field(default=None, description="metricType will define comma separated metrics")
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="filter will define objects to be filtered. Filterable columns are: * `port_type` - type of the port * `nsp` - node, slot and port of the port",
        ),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/ports-performance"
    query_params: dict[str, Any] = {}
    if report_type is not None:
        query_params["report-type"] = report_type
    if range is not None:
        query_params["range"] = range
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    if compare_by is not None:
        query_params["compare-by"] = compare_by
    if group_by is not None:
        query_params["group-by"] = group_by
    if metric_type is not None:
        query_params["metric-type"] = metric_type
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}\n\nDeviceType4PortEnable\n\nPort enable disable identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the port")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/ports/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_clear",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/clear\n\nDeviceType4PortsClear\n\nClear the details of the ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_clear(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the port")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/ports/{path_seg(id)}/clear"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_initialize",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/initialize\n\nDeviceType4initialisePorts\n\nInitialize the details of the ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_initialize(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the port")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/ports/{path_seg(id)}/initialize"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_ping_iscsi",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/ping-iscsi\n\nDeviceType4IscsiPortPing\n\nPing iscsi ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_ping_iscsi(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the port")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/ports/{path_seg(id)}/ping-iscsi"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_ping_rcip",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/ping-rcip\n\nDeviceType4RcipPortPing\n\nPing rcip ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_ping_rcip(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the port")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/ports/{path_seg(id)}/ping-rcip"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_edit_iscsi",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/edit-iscsi\n\nDeviceType4IscsiPortEdit\n\nEdit iscsi ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_edit_iscsi(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the port")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/ports/{path_seg(id)}/edit-iscsi"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_edit_rcip",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/edit-rcip\n\nDeviceType4RcipPortEdit\n\nEdit rcip ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_edit_rcip(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the port")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/ports/{path_seg(id)}/edit-rcip"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_fc",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/fc\n\nDeviceType4FcPortEdit\n\nEdit ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_ports_id_fc(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the port")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/ports/{path_seg(id)}/fc"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
