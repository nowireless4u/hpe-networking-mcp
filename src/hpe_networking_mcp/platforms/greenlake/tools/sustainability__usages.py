"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/sustainability.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``sustainability``   Tag: ``usages``   Operations: 6
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_sustainability_insight_ctr_v1beta1_cloud_usage_by_entity",
    description="GET /sustainability-insight-ctr/v1beta1/cloud-usage-by-entity\n\ngetCloudUsageByEntity\n\nAggregated carbon footprint usage for cloud entities",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_cloud_usage_by_entity(
    ctx: Context,
    start_time: Annotated[str, Field(description="Start of the query's time range in ISO8601 format.")],
    end_time: Annotated[str, Field(description="End of the query's time range in ISO8601 format.")],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='Limit the cloud entities operated on by this endpoint, returning only the subset of entities that match the filter. The filter grammar is a subset of OData 4.0 supporting "eq", "in", and "and" operators only.  Cloud entities can be filtered by: - entityId - serviceProvider - serviceName - serviceRegion - serviceAccount - name',
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='Odata 4.0 field to sort entities on. Allowed fields are the strings "entityId", "serviceProvider", "serviceName", "serviceRegion", "serviceAccount", "name". Must be of the format "property order".',
        ),
    ] = None,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from.")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of usages to return.")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    if start_time is not None:
        query_params["start-time"] = start_time
    if end_time is not None:
        query_params["end-time"] = end_time
    return await greenlake_request(
        ctx,
        "GET",
        "/sustainability-insight-ctr/v1beta1/cloud-usage-by-entity",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_sustainability_insight_ctr_v1beta1_cloud_usage_series",
    description="GET /sustainability-insight-ctr/v1beta1/cloud-usage-series\n\ngetCloudUsageBySeries\n\nTimeseries of cloud carbon footprint usage over time",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_cloud_usage_series(
    ctx: Context,
    interval: Annotated[
        str,
        Field(
            description='Interval of the created time series. Must be of the format "integer unit". Valid units are day(s), hour (s), week(s), month(s), and year(s). Cloud usage typically is measured in months, so the smaller time units are likely to be approximations.'
        ),
    ],
    start_time: Annotated[str, Field(description="Start of the query's time range in ISO8601 format.")],
    end_time: Annotated[str, Field(description="End of the query's time range in ISO8601 format.")],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='Limit the cloud entities operated on by this endpoint, returning only the subset of entities that match the filter. The filter grammar is a subset of OData 4.0 supporting "eq", "in", and "and" operators only.  Cloud entities can be filtered by: - entityId - serviceProvider - serviceName - serviceRegion - serviceAccount - name',
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if interval is not None:
        query_params["interval"] = interval
    if start_time is not None:
        query_params["start-time"] = start_time
    if end_time is not None:
        query_params["end-time"] = end_time
    return await greenlake_request(
        ctx,
        "GET",
        "/sustainability-insight-ctr/v1beta1/cloud-usage-series",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_sustainability_insight_ctr_v1beta1_cloud_usage_totals",
    description="GET /sustainability-insight-ctr/v1beta1/cloud-usage-totals\n\ngetCloudUsageTotals\n\nTotal aggregated cloud carbon footprint usage",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_cloud_usage_totals(
    ctx: Context,
    start_time: Annotated[str, Field(description="Start of the query's time range in ISO8601 format.")],
    end_time: Annotated[str, Field(description="End of the aggregate's time range in ISO8601 format.")],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='Limit the cloud entities operated on by this endpoint, returning only the subset of entities that match the filter. The filter grammar is a subset of OData 4.0 supporting "eq", "in", and "and" operators only.  Cloud entities can be filtered by: - entityId - serviceProvider - serviceName - serviceRegion - serviceAccount - name',
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if start_time is not None:
        query_params["start-time"] = start_time
    if end_time is not None:
        query_params["end-time"] = end_time
    return await greenlake_request(
        ctx,
        "GET",
        "/sustainability-insight-ctr/v1beta1/cloud-usage-totals",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_sustainability_insight_ctr_v1beta1_usage_by_entity",
    description="GET /sustainability-insight-ctr/v1beta1/usage-by-entity\n\ngetUsageByEntity\n\nAggregated energy use for entities",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_usage_by_entity(
    ctx: Context,
    start_time: Annotated[str, Field(description="Start of the query's time range in ISO8601 format.")],
    end_time: Annotated[str, Field(description="End of the query's time range in ISO8601 format.")],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='Limit the entities operated on by this endpoint, returning only the subset of entities that match the filter. The filter grammar is a subset of OData 4.0 supporting "eq", "in", and "and" operators only. Usage entities can be filtered by: - entityId - entityMake - entityModel - entityType - entitySerialNum - entityProductId - locationName - locationId - locationCity - locationState - locationCountry - name',
        ),
    ] = None,
    filter_tags: Annotated[
        str | None,
        Field(
            default=None,
            description='Limit the entities operated on by this endpoint, returning only the subset of entities that contain the tags. The filter grammar is a subset of OData 4.0 supporting "eq" and "or" operators only. The tag key is on the left of the operator, the value is on the right.',
        ),
    ] = None,
    currency: Annotated[
        str | None,
        Field(
            default=None,
            description="The 3 letter currency code the cost returned will be in, case insensitive. Currency calculations are done via a factor queried at the beginning of the day. Defaults to USD.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='Odata 4.0 field to sort entities on. Allowed fields are the strings "locationName", "locationCountry", "locationState", "entityId", "entityMake", "entityModel", "entityType", "entitySerialNum", "entityProductId", "name". Must be of the format "property order".',
        ),
    ] = None,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from.")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of usages to return.")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if filter_tags is not None:
        query_params["filter-tags"] = filter_tags
    if currency is not None:
        query_params["currency"] = currency
    if sort is not None:
        query_params["sort"] = sort
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    if start_time is not None:
        query_params["start-time"] = start_time
    if end_time is not None:
        query_params["end-time"] = end_time
    return await greenlake_request(
        ctx,
        "GET",
        "/sustainability-insight-ctr/v1beta1/usage-by-entity",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_sustainability_insight_ctr_v1beta1_usage_series",
    description="GET /sustainability-insight-ctr/v1beta1/usage-series\n\ngetUsageBySeries\n\nTimeseries of energy usage over time",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_usage_series(
    ctx: Context,
    interval: Annotated[
        str,
        Field(
            description='Interval of the created time series. Must be of the format "integer unit". Valid units are day(s), hour(s), week(s), month(s), and year(s).'
        ),
    ],
    start_time: Annotated[str, Field(description="Start of the query's time range in ISO8601 format.")],
    end_time: Annotated[str, Field(description="End of the query's time range in ISO8601 format.")],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='Limit the entities operated on by this endpoint, returning only the usage for entities that match the filter. The filter grammar is a subset of OData 4.0 supporting "eq", "in", and "and" operators only. Usage entities can be filtered by: - entityId - entityMake - entityModel - entityType - entitySerialNum - entityProductId - locationName - locationId - locationCity - locationState - locationCountry',
        ),
    ] = None,
    filter_tags: Annotated[
        str | None,
        Field(
            default=None,
            description='Limit the entities operated on by this endpoint, returning only the subset of entities that contain the tags. The filter grammar is a subset of OData 4.0 supporting "eq" and "or" operators only. The tag key is on the left of the operator, the value is on the right.',
        ),
    ] = None,
    currency: Annotated[
        str | None,
        Field(
            default=None,
            description="The 3 letter currency code the cost returned will be in, case insensitive. Currency calculations are done via a factor queried at the beginning of the day. Defaults to USD.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if filter_tags is not None:
        query_params["filter-tags"] = filter_tags
    if currency is not None:
        query_params["currency"] = currency
    if interval is not None:
        query_params["interval"] = interval
    if start_time is not None:
        query_params["start-time"] = start_time
    if end_time is not None:
        query_params["end-time"] = end_time
    return await greenlake_request(
        ctx,
        "GET",
        "/sustainability-insight-ctr/v1beta1/usage-series",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_sustainability_insight_ctr_v1beta1_usage_totals",
    description="GET /sustainability-insight-ctr/v1beta1/usage-totals\n\ngetUsageTotals\n\nTotal aggregated data",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_usage_totals(
    ctx: Context,
    start_time: Annotated[str, Field(description="Start of the query's time range in ISO8601 format.")],
    end_time: Annotated[str, Field(description="End of the aggregate's time range in ISO8601 format.")],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='Limit the entities operated on by this endpoint, returning only the usage for entities that match the filter. The filter grammar is a subset of OData 4.0 supporting "eq", "in", and "and" operators only. Usage entities can be filtered by: - entityId - entityMake - entityModel - entityType - entitySerialNum - entityProductId - locationName - locationId - locationCity - locationState - locationCountry',
        ),
    ] = None,
    filter_tags: Annotated[
        str | None,
        Field(
            default=None,
            description='Limit the entities operated on by this endpoint, returning only the subset of entities that contain the tags. The filter grammar is a subset of OData 4.0 supporting "eq" and "or" operators only. The tag key is on the left of the operator, the value is on the right.',
        ),
    ] = None,
    currency: Annotated[
        str | None,
        Field(
            default=None,
            description="The 3 letter currency code the cost returned will be in, case insensitive. Currency calculations are done via a factor queried at the beginning of the day. Defaults to USD.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if filter_tags is not None:
        query_params["filter-tags"] = filter_tags
    if currency is not None:
        query_params["currency"] = currency
    if start_time is not None:
        query_params["start-time"] = start_time
    if end_time is not None:
        query_params["end-time"] = end_time
    return await greenlake_request(
        ctx,
        "GET",
        "/sustainability-insight-ctr/v1beta1/usage-totals",
        query_params=query_params or None,
    )
