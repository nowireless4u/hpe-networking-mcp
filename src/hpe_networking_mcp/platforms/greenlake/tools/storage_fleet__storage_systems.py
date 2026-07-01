"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/storage-fleet.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``storage-fleet``   Tag: ``storage_systems``   Operations: 20
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems\n\nDeviceType4SystemsList\n\nGet all HPE Alletra Storage MP B10000 storage systems",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems(
    ctx: Context,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter systems by Key.")] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Query to sort the response with specified key and order")
    ] = None,
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
        "/storage-fleet/v1alpha1/devtype4-storage-systems",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{id}\n\nDeviceType4SystemGetById\n\nGet HPE Alletra Storage MP B10000 object identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_id(
    ctx: Context,
    id: Annotated[str, Field(description="Serial number of the device-type4 storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_capacity_history",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/capacity-history\n\nDeviceType4SystemCapacityHistoryGet\n\nGet capacity trend data for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_capacity_history(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
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
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/capacity-history"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_capacity_summary",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/capacity-summary\n\nDeviceType4SystemCapacitySummaryGet\n\nGet system capacity for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_capacity_summary(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/capacity-summary"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_component_performance_statistics",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/component-performance-statistics\n\nDeviceType4SystemComponentPerformanceStatisticsGet\n\nGet component performance statistics details for an HPE Alletra Storage MP B10000 storage system idenfified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_component_performance_statistics(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/component-performance-statistics"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_licenses",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/licenses\n\nDeviceType4LicensesGetById\n\nGet licenses of the storage system identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_licenses(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/licenses"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_performance_history",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/performance-history\n\nDeviceType4SystemPerformanceHistoryGet\n\nGet performance trend data for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_performance_history(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
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
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/performance-history"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_performance_statistics",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/performance-statistics\n\nDeviceType4GetSystemPerformanceStatistics\n\nGet performance statistics for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_performance_statistics(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/performance-statistics"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems\n\nDeviceType7GetStorageClusters\n\nGet all HPE Alletra Storage MP X10000 system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems(
    ctx: Context,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="Lucene query to filter systems by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="Lucene query to sort systems by Key.")] = None,
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
        "/storage-fleet/v1alpha1/devtype7-storage-systems",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}\n\nDeviceType7GetStorageClusterById\n\nGet HPE Alletra Storage MP X10000 system identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_capacity_history",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/capacity-history\n\nDeviceType7SystemCapacityHistoryGet\n\nGet capacity trend data for a HPE Alletra Storage MP X10000 system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_capacity_history(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
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
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/capacity-history"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_capacity_summary",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/capacity-summary\n\nDeviceType7SystemCapacitySummaryGet\n\nGet capacity summary for a HPE Alletra Storage MP X10000 system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_capacity_summary(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/capacity-summary"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_performance_history",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/performance-history\n\nDeviceType7SystemPerformanceHistoryGet\n\nGet performance trend data for a HPE Alletra Storage MP X10000 system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_performance_history(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
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
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/performance-history"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_smtp_settings",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/smtp-settings\n\nDeviceType7GetStorageClusterSMTPSettingsById\n\nGet SMTP settings of HPE Alletra Storage MP X10000 system identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_smtp_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/smtp-settings"
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
    name="greenlake_get_storage_fleet_v1alpha1_storage_systems",
    description="GET /storage-fleet/v1alpha1/storage-systems\n\nSystemsList\n\nGet all storage systems",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_storage_systems(
    ctx: Context,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter systems by Key.")] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Query to sort the response with specified key and order")
    ] = None,
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
        "/storage-fleet/v1alpha1/storage-systems",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_storage_systems_id",
    description="GET /storage-fleet/v1alpha1/storage-systems/{id}\n\nSystemGetById\n\nGet storage system object identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_storage_systems_id(
    ctx: Context,
    id: Annotated[str, Field(description="Serial number of the device-type4 storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/storage-systems/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_storage_types",
    description="GET /storage-fleet/v1alpha1/storage-types\n\nGetDeviceType\n\nGet all device types",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_storage_types(
    ctx: Context,
) -> Any:
    return await greenlake_request(
        ctx,
        "GET",
        "/storage-fleet/v1alpha1/storage-types",
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_id",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{id}\n\nDeviceType4SystemLocate\n\nLocate an HPE Alletra Storage MP B10000 system",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_id(
    ctx: Context,
    id: Annotated[str, Field(description="Serial number of the device-type4 storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id",
    description="PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}\n\nDeviceType7EditStorageSystemSettingsById\n\nEdit settings of HPE Alletra Storage MP X10000 system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_smtp_settings",
    description="PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/smtp-settings\n\nDeviceType7EditStorageSystemSMTPSettingsById\n\nEdit settings of HPE Alletra Storage MP X10000 system SMTP server identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_smtp_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/smtp-settings"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
