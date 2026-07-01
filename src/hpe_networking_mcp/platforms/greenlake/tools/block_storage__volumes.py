"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/block-storage.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``block-storage``   Tag: ``volumes``   Operations: 36
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
    name="greenlake_delete_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id",
    description="DELETE /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}\n\nDeviceType4VolumeDelete\n\nRemove volume identified by {volumeId} from HPE Alletra Storage MP B10000",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    un_export: Annotated[
        bool | None, Field(default=None, description="UnExport Host,HostSet and delete volume")
    ] = None,
    cascade: Annotated[bool | None, Field(default=None, description="Delete snapshot and volume")] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if un_export is not None:
        query_params["un-export"] = un_export
    if cascade is not None:
        query_params["cascade"] = cascade
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_delete_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_snapshots_snapshot_id",
    description="DELETE /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/snapshots/{snapshotId}\n\nDeviceType4VolumeSnapshotGetById\n\nRemove HPE Alletra Storage MP B10000 snapshot in system identified by {snapshotId}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_snapshots_snapshot_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    volumeId: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    snapshotId: Annotated[str, Field(description="Identifier of snapshot.")],
    force: Annotated[bool | None, Field(default=None, description="Make snapshot offline and remove.")] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(volumeId)}/snapshots/{path_seg(snapshotId)}"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_delete_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_vluns_id",
    description="DELETE /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/vluns/{id}\n\nDeviceType4VlunsDelete\n\nRemove vlun idenfied by {id} form volume identified by {volumeId} from HPE Alletra Storage MP B10000",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_vluns_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    volumeId: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    id: Annotated[str, Field(description="UID of the vlun")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(volumeId)}/vluns/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_vluns",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/vluns\n\nDeviceType4GetSnapshotVlunsList\n\nGet details of vluns for Snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_vluns(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    snapshotId: Annotated[str, Field(description="UID of the snapshots")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Query to sort the response with specified key and order")
    ] = None,
) -> Any:
    path = (
        f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snapshots/{path_seg(snapshotId)}/vluns"
    )
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_vluns_id",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/vluns/{id}\n\nDeviceType4GetsnapshotVlunsById\n\nGet details of vlun identified by {id} for Snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_vluns_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    snapshotId: Annotated[str, Field(description="UID of the snapshots")],
    id: Annotated[str, Field(description="UID of the vlun")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snapshots/{path_seg(snapshotId)}/vluns/{path_seg(id)}"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes\n\nDeviceType4VolumesList\n\nGet all volumes details for HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}\n\nDeviceType4VolumeGetById\n\nGet details of HPE Alletra Storage MP B10000 Volume identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_capacity_history",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/capacity-history\n\nDeviceType4VolumeCapacityHistoryGetById\n\nGet volume capacity trend data of HPE Alletra Storage MP B10000 Volume identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_capacity_history(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    range: Annotated[
        str | None,
        Field(default=None, description="range will define start and end time in which query has to be made."),
    ] = None,
    time_interval_min: Annotated[
        int | None, Field(default=None, description="It defines granularity in minutes.")
    ] = None,
) -> Any:
    path = (
        f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}/capacity-history"
    )
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if range is not None:
        query_params["range"] = range
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_performance_histogram",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/performance-histogram\n\nDeviceType4GetPerformanceHistogram\n\nGet histogram buckets distribution of I/Os of a volume for a given duration.",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_performance_histogram(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    range: Annotated[
        str | None,
        Field(default=None, description="range will define start and end time in which query has to be made."),
    ] = None,
    time_interval_min: Annotated[
        int | None, Field(default=None, description="It defines granularity in minutes.")
    ] = None,
    io_type: Annotated[
        str | None,
        Field(default=None, description="Indicates if histogram metrics to be calculated for read or write."),
    ] = None,
    buckets: Annotated[
        str | None,
        Field(
            default=None,
            description="Comma separated buckets list. Following values are supported:  Size512B, Size1k, Size2k, Size4k, Size8k, Size16k, Size32k, Size64k, Size128k, Size256k, Size512k, Size1m, Size2m",
        ),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}/performance-histogram"
    query_params: dict[str, Any] = {}
    if range is not None:
        query_params["range"] = range
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    if io_type is not None:
        query_params["io-type"] = io_type
    if buckets is not None:
        query_params["buckets"] = buckets
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_performance_history",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/performance-history\n\nDeviceType4VolumePerformanceHistoryGetById\n\nGet performance trend data of HPE Alletra Storage MP B10000 Volume identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_performance_history(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    range: Annotated[
        str | None,
        Field(default=None, description="range will define start and end time in which query has to be made."),
    ] = None,
    time_interval_min: Annotated[
        int | None, Field(default=None, description="It defines granularity in minutes.")
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}/performance-history"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if range is not None:
        query_params["range"] = range
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_performance_statistics",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/performance-statistics\n\nDeviceType4VolumePerformanceStatisticsGetById\n\nGet performance statistics of HPE Alletra Storage MP B10000 Volume identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_performance_statistics(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}/performance-statistics"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_snapshots",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/snapshots\n\nDeviceType4VolumeSnapshotsList\n\nGet snapshot details of volume identified by {id} for HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_snapshots(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}/snapshots"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_vluns",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/vluns\n\nDeviceType4VlunsList\n\nGet details of vluns for Volume identified by {volumeId} for HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_vluns(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Query to sort the response with specified key and order")
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}/vluns"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_performance",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes-performance\n\nDeviceType4GetVolumesPerformanceHistory\n\nGet performance history of Volumes on storage system identified by {systemid}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_performance(
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
            description="groupBy will define comma separated groupBy parameters. Allowed values are: `vvName, hostName, appsetType, appsetName, portNsp, targetName`. By default, groupBy will be set to `vvName`. If groupBy is used along with filter query parameter, only following combinations are allowed: * `filter: vvId eq 179fa4a77c8497aacdee87d0fb67066b` then groupBy should be `vvName` * `filter: appsetId eq 4765171ee6d74340fca5996b90875d45` then groupBy should be `appsetName` * `filter: hostIds eq 61e2d16fb28d5e6e75198039fcb4f068` then groupBy should be `hostName` * `filter: targetName eq 08BM_s0B8X` then groupBy should be `targetName`",
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="filter will define objects to be filtered. Filterable columns are: * `hostIds` - id of the host * `appsetId` - id of the application set * `vvId` - id of the volume * `targetName` - name of the replication partner",
        ),
    ] = None,
    component: Annotated[
        str | None, Field(default=None, description="component will give information about resource to be queried")
    ] = None,
    metric_type: Annotated[
        str | None, Field(default=None, description="metricType will define comma separated metrics")
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes-performance"
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
    if filter is not None:
        query_params["filter"] = filter
    if component is not None:
        query_params["component"] = component
    if metric_type is not None:
        query_params["metric-type"] = metric_type
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_clones",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/clones\n\nDeviceType4GetClones\n\nGet the details of the clone volumes associated with a base volume identified by {volumeId} for HPE Alletra Storage MP B10000 systems.",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_clones(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    volumeId: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(volumeId)}/clones"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_latency_annotations",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/latency-annotations\n\nDeviceType4GetVolumeLatencyAnnotations\n\nGet volume latency annotations for device-type4",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_latency_annotations(
    ctx: Context,
    systemId: Annotated[str, Field(description="SystemId of the HPE Alletra Storage MP B10000 storage system")],
    volumeId: Annotated[str, Field(description="VolumeId of the device-type4 storage system")],
    time_interval_min: Annotated[int, Field(description="Time interval granularity in minutes")],
    range: Annotated[
        str,
        Field(
            description="Specifies the time period for which hotspot metrics are to be calculated. Both startTime and endTime should be specified"
        ),
    ],
    operation_type: Annotated[
        str | None,
        Field(
            default=None,
            description="Indicates if hotspots metrics to be calculated for read, write or both operations. If this field is not provided, hotspots are calculated for both operations",
        ),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(volumeId)}/latency-annotations"
    query_params: dict[str, Any] = {}
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    if range is not None:
        query_params["range"] = range
    if operation_type is not None:
        query_params["operation-type"] = operation_type
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_performance_drifts",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/performance-drifts\n\nDeviceType4GetPerformanceDrifts\n\nGet latency drifts of a volume for a give duration",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_performance_drifts(
    ctx: Context,
    systemId: Annotated[str, Field(description="SystemId of the HPE Alletra Storage MP B10000 storage system")],
    volumeId: Annotated[str, Field(description="VolumeId of the device-type4 storage system")],
    time_interval_min: Annotated[int, Field(description="Time interval granularity in minutes")],
    range: Annotated[
        str,
        Field(
            description="Specifies the time period for which hotspot metrics are to be calculated. Both startTime and endTime should be specified"
        ),
    ],
    operation_type: Annotated[
        str | None,
        Field(
            default=None,
            description="Indicates if hotspots metrics to be calculated for read, write or both operations. If this field is not provided, hotspots are calculated for both operations",
        ),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(volumeId)}/performance-drifts"
    query_params: dict[str, Any] = {}
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    if range is not None:
        query_params["range"] = range
    if operation_type is not None:
        query_params["operation-type"] = operation_type
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_snapshots_snapshot_id",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/snapshots/{snapshotId}\n\nDeviceType4SnapshotsGetById\n\nGet details of snapshot identified by {snapshotId} for Volume identified by {volumeId} for HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_snapshots_snapshot_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    volumeId: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    snapshotId: Annotated[str, Field(description="UID of the snapshots")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(volumeId)}/snapshots/{path_seg(snapshotId)}"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_vluns_id",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/vluns/{id}\n\nDeviceType4VlunsGetById\n\nGet details of vlun identified by {id} for Volume identified by {volumeId} for HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_vluns_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    volumeId: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    id: Annotated[str, Field(description="UID of the vlun")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(volumeId)}/vluns/{path_seg(id)}"
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
    name="greenlake_get_block_storage_v1alpha1_storage_systems_system_id_volumes",
    description="GET /block-storage/v1alpha1/storage-systems/{systemId}/volumes\n\nVolumeListForSystemBySystemId\n\nGet details of volumes identified with {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_storage_systems_system_id_volumes(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/storage-systems/{path_seg(systemId)}/volumes"
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
    name="greenlake_get_block_storage_v1alpha1_volumes",
    description="GET /block-storage/v1alpha1/volumes\n\nVolumesList\n\nGet all volumes",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_volumes(
    ctx: Context,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
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
        "/block-storage/v1alpha1/volumes",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_volumes_id",
    description="GET /block-storage/v1alpha1/volumes/{id}\n\nVolumeGetById\n\nGet details of Volume identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_volumes_id(
    ctx: Context,
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/volumes/{path_seg(id)}"
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
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_clone",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/clone\n\nDeviceType4SnapshotCloneCreate\n\nCreate a clone of a snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000 systems.",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_clone(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    snapshotId: Annotated[str, Field(description="UID of the snapshots")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = (
        f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snapshots/{path_seg(snapshotId)}/clone"
    )
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_export",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/export\n\nDeviceType4VlunExportForSnapshot\n\nExport vlun for snapshot identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_export(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    snapshotId: Annotated[str, Field(description="UID of the snapshots")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = (
        f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snapshots/{path_seg(snapshotId)}/export"
    )
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_snapshots",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/snapshots\n\nDeviceType4SnapshotOfSnapshotCreate\n\nCreate snapshot of snapshot identified by {snapshotId} on a HPE Alletra storage MP system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_snapshots(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    snapshotId: Annotated[str, Field(description="UID of the snapshots")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snapshots/{path_seg(snapshotId)}/snapshots"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_un_export",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/un-export\n\nDeviceType4VlunUnexportForSnapshot\n\nUnexport vlun for snapshot identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_snapshot_id_un_export(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    snapshotId: Annotated[str, Field(description="UID of the snapshots")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snapshots/{path_seg(snapshotId)}/un-export"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes\n\nDeviceType4VolumeCreate\n\nCreate a new volume for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_clone",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/clone\n\nDeviceType4VolumeCloneCreate\n\nCreate a clone volume identified by {id} for HPE Alletra Storage MP B10000 systems.",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_clone(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}/clone"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_export",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/export\n\nDeviceType4VlunExport\n\nExport vlun for volume identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_export(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}/export"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_snapshots",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/snapshots\n\nDeviceType4VolumeSnapshotCreate\n\nCreate snapshot for volumes identified by {id}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_snapshots(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}/snapshots"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_un_export",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/un-export\n\nDeviceType4VlunUnexport\n\nUnexport vlun for volume identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id_un_export(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}/un-export"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_clones_clone_id_promote",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/clones/{cloneId}/promote\n\nDeviceType4PromoteCloneVolume\n\nPromote a clone volume identified by {cloneId} of a volume identified by {volumeId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_clones_clone_id_promote(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    volumeId: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    cloneId: Annotated[str, Field(description="UID of the clone")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(volumeId)}/clones/{path_seg(cloneId)}/promote"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_clones_clone_id_resync",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/clones/{cloneId}/resync\n\nDeviceType4ResyncCloneVolume\n\nResynchronize a clone volume identified by {cloneId} of a volume identified by {volumeId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_clones_clone_id_resync(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    volumeId: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    cloneId: Annotated[str, Field(description="UID of the clone")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(volumeId)}/clones/{path_seg(cloneId)}/resync"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_snapshots_snapshot_id",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/snapshots/{snapshotId}\n\nDeviceType4PromoteSnapshot\n\nPromote a snapshot identified by {snapshotId} of a volume identified by {volumeId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_volume_id_snapshots_snapshot_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    volumeId: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    snapshotId: Annotated[str, Field(description="UID of the snapshots")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(volumeId)}/snapshots/{path_seg(snapshotId)}"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_storage_systems_provisioning_recommendations",
    description="POST /block-storage/v1alpha1/storage-systems/provisioning-recommendations\n\nProvisioningRecommendations\n\nProduce a set of provisioning recommendations based on the provided input parameters.",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_storage_systems_provisioning_recommendations(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/block-storage/v1alpha1/storage-systems/provisioning-recommendations",
        body=body,
    )


@tool(
    name="greenlake_put_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id",
    description="PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}\n\nDeviceType4VolumeEdit\n\nEdit volume identified by {volumeId} from HPE Alletra Storage MP B10000",
    capability=Capability.WRITE,
)
async def greenlake_put_block_storage_v1alpha1_devtype4_storage_systems_system_id_volumes_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID(volumeuid) of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/volumes/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
