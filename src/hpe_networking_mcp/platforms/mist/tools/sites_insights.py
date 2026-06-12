"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Insights``
Operations in this file: 7
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
    name="mist_get_site_insight_metrics",
    description="GET /api/v1/sites/{site_id}/insights\n\ngetSiteInsightMetrics\n\nGet Site Insight Metrics",
    capability=Capability.READ,
)
async def mist_get_site_insight_metrics(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    metrics: Annotated[
        str,
        Field(
            description="Comma separated Metric names, e.g. `num_clients,num_aps`. See possible values at [List Insight Metrics](/#operations/listInsightMetrics)"
        ),
    ],
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/insights",
        path_params={"site_id": site_id},
        query_params={
            "metrics": metrics,
            "start": start,
            "end": end,
            "duration": duration,
            "interval": interval,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_insight_metrics_for_ap",
    description="GET /api/v1/sites/{site_id}/insights/ap/{device_id}/stats\n\ngetSiteInsightMetricsForAP\n\nGet AP Insight Metrics",
    capability=Capability.READ,
)
async def mist_get_site_insight_metrics_for_ap(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    metrics: Annotated[
        str,
        Field(
            description="Comma separated Metric names, e.g. `num_clients,num_stressed_clients`. See possible values at [List Insight Metrics](/#operations/listInsightMetrics)"
        ),
    ],
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/insights/ap/{device_id}/stats",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params={
            "metrics": metrics,
            "start": start,
            "end": end,
            "duration": duration,
            "interval": interval,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_insight_metrics_for_client",
    description="GET /api/v1/sites/{site_id}/insights/client/{client_mac}\n\ngetSiteInsightMetricsForClient\n\nGet Client Insight Metrics",
    capability=Capability.READ,
)
async def mist_get_site_insight_metrics_for_client(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    client_mac: Annotated[str, Field(description="path parameter 'client_mac'")],
    metrics: Annotated[
        str,
        Field(
            description="Comma separated Metric names, e.g. `top-app-by-num_client,top-app-by-bytes`. See possible values at [List Insight Metrics](/#operations/listInsightMetrics)"
        ),
    ],
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/insights/client/{client_mac}",
        path_params={"site_id": site_id, "client_mac": client_mac},
        query_params={
            "metrics": metrics,
            "start": start,
            "end": end,
            "duration": duration,
            "interval": interval,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_insight_metrics_for_device",
    description="GET /api/v1/sites/{site_id}/insights/device/{device_mac}/{metric}\n\ngetSiteInsightMetricsForDevice\n\nGet AP Insight Metrics\nSee metrics possibilities at [List Insight Metrics](/#operations/listInsightMetrics)",
    capability=Capability.READ,
)
async def mist_get_site_insight_metrics_for_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    metric: Annotated[
        str, Field(description="See [List Insight Metrics](/#operations/listInsightMetrics) for available metrics")
    ],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
    port_id: Annotated[
        str | None,
        Field(
            description="Port ID of the device, e.g. `ge-0/0/1`. Can be used with metrics related to interfaces, e.g. `rx_bytes`."
        ),
    ] = None,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/insights/device/{device_mac}/{metric}",
        path_params={"site_id": site_id, "metric": metric, "device_mac": device_mac},
        query_params={
            "port_id": port_id,
            "start": start,
            "end": end,
            "duration": duration,
            "interval": interval,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_insight_metrics_for_gateway",
    description="GET /api/v1/sites/{site_id}/insights/gateway/{device_id}/stats\n\ngetSiteInsightMetricsForGateway\n\nGet Gateway Insight Metrics",
    capability=Capability.READ,
)
async def mist_get_site_insight_metrics_for_gateway(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    metrics: Annotated[
        str,
        Field(
            description="Comma separated Metric names, e.g. `tx_bps,rx_bps`. See possible values at [List Insight Metrics](/#operations/listInsightMetrics)"
        ),
    ],
    port_id: Annotated[str | None, Field(description="Port ID of the gateway device, e.g. `ge-0/0/1`")] = None,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/insights/gateway/{device_id}/stats",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params={
            "metrics": metrics,
            "port_id": port_id,
            "start": start,
            "end": end,
            "duration": duration,
            "interval": interval,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_insight_metrics_for_mx_edge",
    description="GET /api/v1/sites/{site_id}/insights/mxedge/{device_mac}/{metric}\n\ngetSiteInsightMetricsForMxEdge\n\nGet MxEdge Insight Metrics\nSee metrics possibilities at [List Insight Metrics](/#operations/listInsightMetrics)",
    capability=Capability.READ,
)
async def mist_get_site_insight_metrics_for_mx_edge(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    metric: Annotated[
        str, Field(description="See [List Insight Metrics](/#operations/listInsightMetrics) for available metrics")
    ],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
    port_id: Annotated[
        str | None,
        Field(
            description="Port ID of the MxEdge device, e.g. `port0`. Can be used with metrics related to interfaces, e.g. `rx_bytes`."
        ),
    ] = None,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/insights/mxedge/{device_mac}/{metric}",
        path_params={"site_id": site_id, "metric": metric, "device_mac": device_mac},
        query_params={
            "port_id": port_id,
            "start": start,
            "end": end,
            "duration": duration,
            "interval": interval,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_insight_metrics_for_switch",
    description="GET /api/v1/sites/{site_id}/insights/switch/{device_mac}/{metric}\n\ngetSiteInsightMetricsForSwitch\n\nGet Switch Insight Metrics\nSee metrics possibilities at [List Insight Metrics](/#operations/listInsightMetrics)",
    capability=Capability.READ,
)
async def mist_get_site_insight_metrics_for_switch(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    metric: Annotated[
        str, Field(description="See [List Insight Metrics](/#operations/listInsightMetrics) for available metrics")
    ],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
    port_id: Annotated[
        str | None,
        Field(
            description="Port ID of the switch device, e.g. `ge-0/0/1`. Can be used with metrics related to interfaces, e.g. `rx_bytes`."
        ),
    ] = None,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/insights/switch/{device_mac}/{metric}",
        path_params={"site_id": site_id, "metric": metric, "device_mac": device_mac},
        query_params={
            "port_id": port_id,
            "start": start,
            "end": end,
            "duration": duration,
            "interval": interval,
            "limit": limit,
            "page": page,
        },
        body=None,
    )
