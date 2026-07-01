"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/block-storage.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``block-storage``   Tag: ``storage_systems``   Operations: 7
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_application_summary",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/application-summary\n\nDeviceType4ApplicationSummaryGet\n\nGet Application Summary for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_application_summary(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/application-summary"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_capacity_forecast",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/capacity-forecast\n\nDeviceType4SystemCapacityForecastGet\n\nGet latest capacity trend data and forecasted data",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_capacity_forecast(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    start_time: Annotated[
        int | None, Field(default=None, description="Start time from which forecasted data is needed")
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/capacity-forecast"
    query_params: dict[str, Any] = {}
    if start_time is not None:
        query_params["start-time"] = start_time
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_capacity_timeuntilfull",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/capacity-timeuntilfull\n\nDeviceType4SystemCapacityTimeUntilFull\n\nGet capacity time until full data for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_capacity_timeuntilfull(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/capacity-timeuntilfull"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_headroom_contribution",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/headroom-contribution\n\nDeviceType4GetHeadroomContribution\n\nGet Top headroom contribution by volumes/Apps for device-type4",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_headroom_contribution(
    ctx: Context,
    systemId: Annotated[str, Field(description="SystemId of the HPE Alletra Storage MP B10000 storage system")],
    time_interval_min: Annotated[int, Field(description="Time interval granularity in minutes")],
    range: Annotated[
        str,
        Field(
            description="Specifies the time period for which hotspot metrics are to be calculated. Both startTime and endTime should be specified"
        ),
    ],
    resource_type: Annotated[
        str | None,
        Field(
            default=None, description="Query to select resource (volumes, volume-set) for getting Headroom Contributors"
        ),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/headroom-contribution"
    query_params: dict[str, Any] = {}
    if resource_type is not None:
        query_params["resource-type"] = resource_type
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    if range is not None:
        query_params["range"] = range
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_hotspots",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/hotspots\n\nDeviceType4GetHotspots\n\nGet hotspots for HPE Alletra Storage MP B10000 storage system based on resourceType `VOLUMES or VOLUME-SET` and metricType `LATENCY`",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_hotspots(
    ctx: Context,
    systemId: Annotated[str, Field(description="SystemId of the HPE Alletra Storage MP B10000 storage system")],
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
    resource_type: Annotated[
        str | None, Field(default=None, description="Query to select resource (volumes, volume-set) for analytics")
    ] = None,
    metric_type: Annotated[
        str | None, Field(default=None, description="Query to select metric for which hotspot is to calculated")
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/hotspots"
    query_params: dict[str, Any] = {}
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    if range is not None:
        query_params["range"] = range
    if operation_type is not None:
        query_params["operation-type"] = operation_type
    if resource_type is not None:
        query_params["resource-type"] = resource_type
    if metric_type is not None:
        query_params["metric-type"] = metric_type
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_latency_factors",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/latency-factors\n\nDevice4LatencyFactorsGet\n\nGet system level latency factors",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_latency_factors(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    time_interval_min: Annotated[int, Field(description="Time interval granularity in minutes")],
    range: Annotated[
        str | None,
        Field(default=None, description="range will define start and end time in which query has to be made."),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/latency-factors"
    query_params: dict[str, Any] = {}
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_resource_contention",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/resource-contention\n\nDeviceType4GetResourceContentionData\n\nGet resource contention data for resources `DISK and CPU` for device-type4",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_resource_contention(
    ctx: Context,
    systemId: Annotated[str, Field(description="SystemId of the HPE Alletra Storage MP B10000 storage system")],
    time_interval_min: Annotated[int, Field(description="Time interval granularity in minutes")],
    range: Annotated[
        str,
        Field(
            description="Specifies the time period for which hotspot metrics are to be calculated. Both startTime and endTime should be specified"
        ),
    ],
    resource_contention_type: Annotated[
        str | None,
        Field(
            default=None,
            description="Indicates if resource contention has to be calculated for disk, cpu or both resources. If this field is not provided, resource contention is calculated for both resources",
        ),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/resource-contention"
    query_params: dict[str, Any] = {}
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    if range is not None:
        query_params["range"] = range
    if resource_contention_type is not None:
        query_params["resource-contention-type"] = resource_contention_type
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )
