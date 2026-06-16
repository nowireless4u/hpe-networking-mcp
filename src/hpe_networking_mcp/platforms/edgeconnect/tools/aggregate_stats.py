"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``aggregateStats``
Operations in this file: 54
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_stats_aggregate_application2",
    description="GET /stats/aggregate/application2\n\ngetApplication2AggregatedStats\n\nGet aggregate application stats by appliance, group, or all",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_application2(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (milliseconds) for the start of the data time range. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (milliseconds) for the end of the data time range. Must be >= 0 and greater than startTime."
        ),
    ],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    application: Annotated[
        str | None, Field(default=None, description="Filter results by application name. Case-sensitive match.")
    ] = None,
    top: Annotated[
        int | None, Field(default=None, description="Limit results to top N applications sorted by throughput.")
    ] = None,
    groupPk: Annotated[
        str | None,
        Field(
            default=None,
            description="Internal group ID for filtering stats by appliance group. Used when nePk is not provided.",
        ),
    ] = None,
    format: Annotated[
        str | None, Field(default=None, description="Output format. Use 'csv' for CSV export. Omit for JSON response.")
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="Group results by appliance (nePk). Default is true. When true, response includes appliance identifiers in nested structure.",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, fetches data from one hour prior if no data exists in the specified time range. Useful for recent data queries.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if application is not None:
        query_params["application"] = application
    if top is not None:
        query_params["top"] = top
    if groupPk is not None:
        query_params["groupPk"] = groupPk
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/application2",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_availability_appliance",
    description="GET /stats/aggregate/availability/appliance\n\ngetApplianceReachabilityStats\n\nGet aggregated appliance reachability statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_availability_appliance(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    date: Annotated[
        str,
        Field(
            description="Query date in YYYY-MM-DD format. For 'month' granularity, use first day of month (e.g., '2024-01-01')."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time aggregation period. 'day' returns daily stats, 'week' returns weekly stats, 'month' returns monthly stats."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if date is not None:
        query_params["date"] = date
    if granularity is not None:
        query_params["granularity"] = granularity
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/availability/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_availability_interface",
    description="GET /stats/aggregate/availability/interface\n\ngetInterfaceAvailabilityStats\n\nGet aggregated interface availability statistics for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_availability_interface(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    date: Annotated[
        str,
        Field(
            description="Date for which to retrieve statistics. Format: YYYY-MM-DD. For month granularity, use first day of month (e.g., '2024-01-01')."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time period aggregation level. Determines how statistics are aggregated and which database table is queried."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if date is not None:
        query_params["date"] = date
    if granularity is not None:
        query_params["granularity"] = granularity
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/availability/interface",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_availability_network_role",
    description="GET /stats/aggregate/availability/networkRole\n\ngetNetworkRoleAvailabilityAggregateStats\n\nGet network role availability aggregate stats",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_availability_network_role(
    ctx: Context,
    granularity: Annotated[
        str,
        Field(
            description="Data granularity filter. Use 'day' for daily stats, 'week' for weekly aggregation, or 'month' for monthly stats."
        ),
    ],
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    date: Annotated[
        str,
        Field(
            description="Date in YYYY-MM-DD format. For 'month' granularity, use the first day of the month (e.g., 2024-01-01)."
        ),
    ],
    overlayId: Annotated[
        str,
        Field(
            description="Overlay/tunnel filter. Use '0' for underlay (physical) tunnels, 'all' for all bonded (overlay) tunnels, or a specific numeric overlay ID."
        ),
    ],
    isGroupByNe: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups statistics by appliance (nePk). When false, filters stats for the specified nePk only. Default is false.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if granularity is not None:
        query_params["granularity"] = granularity
    if nePk is not None:
        query_params["nePk"] = nePk
    if date is not None:
        query_params["date"] = date
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    if isGroupByNe is not None:
        query_params["isGroupByNe"] = isGroupByNe
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/availability/networkRole",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_availability_tunnel",
    description="GET /stats/aggregate/availability/tunnel\n\ngetTunnelAvailabilityStats\n\nGet tunnel availability aggregate stats for a single appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_availability_tunnel(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    date: Annotated[
        str,
        Field(
            description="Date for statistics retrieval. Format: YYYY-MM-DD. For month granularity, use first day of month (e.g., '2022-12-01')."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for data aggregation. Use 'day' for daily stats, 'week' for weekly stats, or 'month' for monthly stats."
        ),
    ],
    overlayId: Annotated[
        str,
        Field(
            description="Overlay filter for tunnel types. Use '0' for all physical/underlay tunnels, 'all' for all bonded/overlay tunnels, or a specific overlay ID for a particular overlay."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if date is not None:
        query_params["date"] = date
    if granularity is not None:
        query_params["granularity"] = granularity
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/availability/tunnel",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_availability_tunnel_service",
    description="GET /stats/aggregate/availability/tunnel/service\n\ngetTunnelServiceAvailabilityAggregatedStats\n\nGet aggregated tunnel availability statistics for third-party services",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_availability_tunnel_service(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    date: Annotated[
        str,
        Field(
            description="Date for statistics retrieval in YYYY-MM-DD format. For 'month' granularity, use the first day of the month (e.g., 2024-01-01)."
        ),
    ],
    tunType: Annotated[
        int,
        Field(
            description="Tunnel type filter. Use 3 for third-party service tunnels. Valid values: 0 (SD-WAN), 1 (Underlay), 2 (Breakout/Pass-through), 3 (Services)."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for data aggregation. Determines which database table is queried and how data is grouped."
        ),
    ],
    overlayId: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by overlay ID. Use '0' for physical tunnels, 'all' or '-1' for all bonded tunnels, or a specific overlay ID number.",
        ),
    ] = None,
    serviceName: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by service provider name. Performs prefix matching (LIKE 'serviceName%'). Optional parameter for filtering results.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if date is not None:
        query_params["date"] = date
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    if tunType is not None:
        query_params["tunType"] = tunType
    if granularity is not None:
        query_params["granularity"] = granularity
    if serviceName is not None:
        query_params["serviceName"] = serviceName
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/availability/tunnel/service",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_boost",
    description="GET /stats/aggregate/boost\n\ngetAggregateBoostStatsSingleAppliance\n\nGet Boost stats for single appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_boost(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    startTime: Annotated[
        int, Field(description="Start time in seconds since EPOCH. Must be >= 0 and less than endTime.")
    ],
    endTime: Annotated[
        int, Field(description="End time in seconds since EPOCH. Must be >= 0 and greater than startTime.")
    ],
    granularity: Annotated[
        str, Field(description="Time-based aggregation level. Controls grouping interval for statistics.")
    ],
    format: Annotated[
        str | None, Field(default=None, description="Output format. Set to 'csv' for downloadable CSV file.")
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(default=None, description="Group results by appliance. When true, includes nePk in response."),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/boost",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_dns",
    description="GET /stats/aggregate/dns\n\ngetDnsAggregatedStatsSingleAppliance\n\nGet DNS aggregate statistics for a single appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_dns(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    startTime: Annotated[
        int,
        Field(description="Start time boundary as epoch seconds (signed 64-bit). Must be >= 0 and less than endTime."),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary as epoch seconds (signed 64-bit). Must be >= 0 and greater than startTime."
        ),
    ],
    isSource: Annotated[
        int | None, Field(default=None, description="Filter by traffic direction: 0 = destination DNS, 1 = source DNS.")
    ] = None,
    splitType: Annotated[
        int | None,
        Field(default=None, description="Filter by protocol type: 0 = HTTP, 1 = HTTPS, 2 = unassigned, 3 = others."),
    ] = None,
    top: Annotated[
        int | None, Field(default=None, description="Maximum number of results to return. Limits the result set size.")
    ] = None,
    splitByNe: Annotated[
        bool | None,
        Field(
            default=None,
            description="Split results by appliance. When true, response includes nested objects keyed by appliance ID. Default: null.",
        ),
    ] = None,
    groupBy: Annotated[
        str | None,
        Field(
            default=None,
            description="Group results by field. Use 'dns' for domain grouping or 'country' for geographic grouping. Default: 'dns'.",
        ),
    ] = None,
    groupBySubDomains: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of sub-domains to include in domain grouping (e.g., 2 = example.com, 3 = sub.example.com). Default: 2.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if isSource is not None:
        query_params["isSource"] = isSource
    if splitType is not None:
        query_params["splitType"] = splitType
    if top is not None:
        query_params["top"] = top
    if splitByNe is not None:
        query_params["splitByNe"] = splitByNe
    if groupBy is not None:
        query_params["groupBy"] = groupBy
    if groupBySubDomains is not None:
        query_params["groupBySubDomains"] = groupBySubDomains
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/dns",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_dscp",
    description="GET /stats/aggregate/dscp\n\ngetDscpAggregatedStats\n\nGet DSCP aggregate statistics for single appliance or group",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_dscp(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(description="EPOCH timestamp (signed 64-bit) for data range start. Must be >= 0 and less than endTime."),
    ],
    endTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (signed 64-bit) for data range end. Must be >= 0 and greater than startTime."
        ),
    ],
    trafficType: Annotated[
        str,
        Field(description="Traffic type classification filter. Determines which traffic category to include in stats."),
    ],
    granularity: Annotated[
        str, Field(description="Data aggregation interval. Controls the time granularity of returned statistics.")
    ],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    groupPk: Annotated[
        str | None,
        Field(
            default=None,
            description="Group primary key for filtering stats by appliance group. Used when nePk is not provided.",
        ),
    ] = None,
    dscp: Annotated[
        int | None,
        Field(
            default=None,
            description="DSCP value filter. Valid range: 0-63. When omitted, returns stats for all DSCP values.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(default=None, description="Use IP address as grouping key instead of internal appliance ID (nePk)."),
    ] = None,
    metric: Annotated[
        str | None,
        Field(default=None, description="Sort results by specified metric. Required when using 'top' parameter."),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None, description="Limit results to top N items by metric. Requires 'metric' parameter to be set."
        ),
    ] = None,
    format: Annotated[
        str | None, Field(default=None, description="Response format. Set to 'csv' for CSV file download.")
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="Group results by appliance. Default: true. When false, aggregates all appliances together.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if groupPk is not None:
        query_params["groupPk"] = groupPk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if granularity is not None:
        query_params["granularity"] = granularity
    if dscp is not None:
        query_params["dscp"] = dscp
    if ip is not None:
        query_params["ip"] = ip
    if metric is not None:
        query_params["metric"] = metric
    if top is not None:
        query_params["top"] = top
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/dscp",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_flow",
    description="GET /stats/aggregate/flow\n\ngetFlowAggregatedStats\n\nRetrieve aggregated flow statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_flow(
    ctx: Context,
    granularity: Annotated[
        str,
        Field(description="Time granularity for data aggregation. Determines the resolution of returned statistics."),
    ],
    startTime: Annotated[
        int,
        Field(
            description="Start of time range as Unix epoch timestamp in milliseconds. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of time range as Unix epoch timestamp in milliseconds. Must be >= 0 and greater than startTime."
        ),
    ],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    groupPk: Annotated[
        str | None,
        Field(
            default=None,
            description="Group primary key to filter appliances. Used when nePk is not provided to query multiple appliances in a group.",
        ),
    ] = None,
    flowType: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by flow type category. TCP_ACCELERATED=optimized TCP flows, TCP_NOT_ACCELERATED=unoptimized TCP, NON_TCP=UDP and other protocols.",
        ),
    ] = None,
    trafficType: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by traffic classification type. Controls which traffic category statistics are returned.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, uses IP address as the grouping key instead of internal appliance ID (nePk).",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None, description="Response format. Use 'csv' for CSV file download with Excel-compatible headers."
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups stats by appliance with an extra nesting level. Default is true when not specified.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if groupPk is not None:
        query_params["groupPk"] = groupPk
    if granularity is not None:
        query_params["granularity"] = granularity
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if flowType is not None:
        query_params["flowType"] = flowType
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if ip is not None:
        query_params["ip"] = ip
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/flow",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_jitter",
    description="GET /stats/aggregate/jitter\n\ngetAggregateJitterStats\n\nGet aggregate jitter stats for single appliance or group",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_jitter(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since epoch) for the start of the data time range. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since epoch) for the end of the data time range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Data aggregation interval. Determines how stats are grouped temporally.")
    ],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    tunnelName: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter results by specific tunnel name. Returns jitter stats only for the specified tunnel.",
        ),
    ] = None,
    groupPk: Annotated[
        str | None,
        Field(
            default=None,
            description="Internal group ID to filter statistics for a specific appliance group. Used when nePk is not provided.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, uses IP address as grouping key instead of internal appliance ID. Default is false.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of results to return. When nePk is empty, requires metric parameter.",
        ),
    ] = None,
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter tunnels by overlay type. Use 'all' for bonded tunnels, '0' for physical tunnels only, or specific overlay ID.",
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups results by appliance with nested stats objects. Default is true.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. Use 'csv' to download results as CSV file. Omit for JSON response.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if tunnelName is not None:
        query_params["tunnelName"] = tunnelName
    if groupPk is not None:
        query_params["groupPk"] = groupPk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if ip is not None:
        query_params["ip"] = ip
    if top is not None:
        query_params["top"] = top
    if overlay is not None:
        query_params["overlay"] = overlay
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/jitter",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_mos",
    description="GET /stats/aggregate/mos\n\ngetAggregateMosStatsSingleAppliance\n\nGet aggregated MOS statistics for a single appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_mos(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since epoch) for data range start. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since epoch) for data range end. Must be >= 0 and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Time interval for data aggregation. Determines statistical granularity.")
    ],
    tunnelName: Annotated[
        str | None, Field(default=None, description="Filter by tunnel name. Returns stats for a specific tunnel only.")
    ] = None,
    top: Annotated[int | None, Field(default=None, description="Limit results to top N tunnels by MOS value.")] = None,
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by overlay ID. Use '0' for physical tunnels only, omit for all tunnels, or specify overlay ID for bonded tunnels.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Response format. Set to 'csv' for CSV file download, omit for JSON response."),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(default=None, description="Group statistics by appliance. Adds nesting level by appliance in response."),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if tunnelName is not None:
        query_params["tunnelName"] = tunnelName
    if top is not None:
        query_params["top"] = top
    if overlay is not None:
        query_params["overlay"] = overlay
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/mos",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_ports",
    description="GET /stats/aggregate/ports\n\ngetPortAggregatedStats\n\nGet aggregated port statistics with optional filtering",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_ports(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of the time range in seconds since EPOCH (Unix timestamp). Must be less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range in seconds since EPOCH (Unix timestamp). Must be greater than startTime."
        ),
    ],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    isSource: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by port direction. 1 = source port, 0 = destination port. When omitted, returns both.",
        ),
    ] = None,
    isKnown: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by application classification. 1 = port assigned to known application, 0 = unclassified port. When omitted, returns both.",
        ),
    ] = None,
    protocol: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by IP protocol number (e.g., 6 for TCP, 17 for UDP). When omitted, returns all protocols.",
        ),
    ] = None,
    port: Annotated[
        int | None, Field(default=None, description="Filter by specific port number. When omitted, returns all ports.")
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of records to return, sorted by total LAN bytes (lanrx + lantx) descending.",
        ),
    ] = None,
    splitByNe: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups results by appliance (nePk). Each stats object includes appliance identifier. Default is null (aggregated across appliances).",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, if no data found in the specified time range, queries data from one hour prior. Useful for near-real-time dashboards.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Response format. Use 'csv' to download as CSV file. Default returns JSON."),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if isSource is not None:
        query_params["isSource"] = isSource
    if isKnown is not None:
        query_params["isKnown"] = isKnown
    if protocol is not None:
        query_params["protocol"] = protocol
    if port is not None:
        query_params["port"] = port
    if top is not None:
        query_params["top"] = top
    if splitByNe is not None:
        query_params["splitByNe"] = splitByNe
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/ports",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_security_policy",
    description="GET /stats/aggregate/securityPolicy\n\ngetAggregateSecurityPolicyStatsSingleAppliance\n\nGet aggregated security policy stats for a single appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_security_policy(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    startTime: Annotated[int, Field(description="Start time as Unix epoch (seconds). Must be >= 0 and < endTime.")],
    endTime: Annotated[int, Field(description="End time as Unix epoch (seconds). Must be >= 0 and > startTime.")],
    granularity: Annotated[str, Field(description="Data aggregation interval. Case-insensitive.")],
    fromZone: Annotated[
        str | None, Field(default=None, description="Filter by source security zone. Omit for all source zones.")
    ] = None,
    toZone: Annotated[
        str | None,
        Field(default=None, description="Filter by destination security zone. Omit for all destination zones."),
    ] = None,
    top: Annotated[int | None, Field(default=None, description="Limit results to top N zone pairs by traffic.")] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Set to 'csv' for file download (SecurityPolicyAggregateStats.csv)."),
    ] = None,
    groupByNE: Annotated[
        bool | None, Field(default=None, description="Include nePk in results. Default: true.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if fromZone is not None:
        query_params["fromZone"] = fromZone
    if toZone is not None:
        query_params["toZone"] = toZone
    if top is not None:
        query_params["top"] = top
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/securityPolicy",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_top_talkers",
    description="GET /stats/aggregate/topTalkers\n\ngetTopTalkersAggregateStats\n\nGet aggregated top talkers bandwidth statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_top_talkers(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of time range as Unix epoch timestamp in seconds. Required. Must be >= 0 and < endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of time range as Unix epoch timestamp in seconds. Required. Must be >= 0 and > startTime."
        ),
    ],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of top talker records to return per appliance. Limits results to the top N bandwidth consumers sorted by total LAN bytes.",
        ),
    ] = None,
    splitByNe: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups results by appliance. When nePk is provided, this is forced to false.",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true and no data exists for the time range, automatically queries data from one hour prior (startTime-3600, endTime-3600).",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if top is not None:
        query_params["top"] = top
    if splitByNe is not None:
        query_params["splitByNe"] = splitByNe
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/topTalkers",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_top_talkers_split",
    description="GET /stats/aggregate/topTalkers/split\n\ngetTopTalkersAggregateSplit\n\nGet top talker aggregate statistics split by source and destination for a single appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_top_talkers_split(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    startTime: Annotated[
        int, Field(description="Start of the time range in epoch seconds. Must be non-negative and less than endTime.")
    ],
    endTime: Annotated[
        int,
        Field(description="End of the time range in epoch seconds. Must be non-negative and greater than startTime."),
    ],
    sourceIp: Annotated[
        str | None,
        Field(
            default=None,
            description="Source IP address to filter traffic statistics. When provided, returns traffic split by destination for this source.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if sourceIp is not None:
        query_params["sourceIp"] = sourceIp
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/topTalkers/split",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_traffic_behavior",
    description="GET /stats/aggregate/trafficBehavior\n\ngetTrafficBehaviorAggregatedStats\n\nGet traffic behavioral stats by query parameters",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_traffic_behavior(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Start time in Unix epoch seconds. Must be non-negative and less than endTime.")
    ],
    endTime: Annotated[
        int, Field(description="End time in Unix epoch seconds. Must be non-negative and greater than startTime.")
    ],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    behavioralCate: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by behavioral category name. Common values: Business, Recreational, Streaming, General.",
        ),
    ] = None,
    application: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by application name to retrieve stats for a specific application within the category.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limit results to top N entries ranked by traffic volume. Useful for dashboard displays.",
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include appliance-level breakdown in response. Only used when nePk is provided. Default: true.",
        ),
    ] = None,
    groupPk: Annotated[
        str | None,
        Field(
            default=None,
            description="Appliance group ID to filter stats. Used when nePk is not provided to query by group.",
        ),
    ] = None,
    isAggregated: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns aggregated summary stats. When false, returns detailed per-application stats. Default: false.",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="If no data in last hour, fetch from one hour earlier. Useful for recent data queries. Default: false.",
        ),
    ] = None,
    format: Annotated[
        str | None, Field(default=None, description="Output format. Use 'csv' for downloadable CSV file.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if behavioralCate is not None:
        query_params["behavioralCate"] = behavioralCate
    if application is not None:
        query_params["application"] = application
    if top is not None:
        query_params["top"] = top
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    if groupPk is not None:
        query_params["groupPk"] = groupPk
    if isAggregated is not None:
        query_params["isAggregated"] = isAggregated
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/trafficBehavior",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_traffic_class",
    description="GET /stats/aggregate/trafficClass\n\ngetTrafficClassAggregatedStats\n\nGet aggregated traffic class statistics filtered by query parameters",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_traffic_class(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (milliseconds) for the start of the data time range. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (milliseconds) for the end of the data time range. Must be >= 0 and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval granularity for data aggregation. Determines whether stats are aggregated by minute, hour, or day."
        ),
    ],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    groupPk: Annotated[
        str | None,
        Field(
            default=None,
            description="Group primary key to filter appliances. Used when nePk is not provided to retrieve stats for all appliances in a group.",
        ),
    ] = None,
    trafficClass: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter statistics by traffic class (QoS priority level). Valid range: 1-10, where 1 is highest priority.",
        ),
    ] = None,
    trafficType: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by traffic optimization type. 'optimized_traffic' for WAN-optimized flows, 'pass_through_shaped' for shaped pass-through, 'pass_through_unshaped' for unshaped pass-through, 'all_traffic' for combined stats.",
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups statistics by appliance with nePk/IP as the key. Default is true.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, uses IP address as the grouping key instead of internal appliance ID (nePk).",
        ),
    ] = None,
    metric: Annotated[
        str | None,
        Field(
            default=None,
            description="Metric to sort results by. Required when using the 'top' parameter to limit results.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limits results to top N items sorted by the specified metric. Requires the 'metric' parameter to be set.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. When set to 'csv', returns data as a downloadable CSV file instead of JSON.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if groupPk is not None:
        query_params["groupPk"] = groupPk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if trafficClass is not None:
        query_params["trafficClass"] = trafficClass
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    if ip is not None:
        query_params["ip"] = ip
    if metric is not None:
        query_params["metric"] = metric
    if top is not None:
        query_params["top"] = top
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/trafficClass",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_aggregate_tunnel",
    description="GET /stats/aggregate/tunnel\n\ngetTunnelAggregatedStats\n\nGet aggregated tunnel statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_aggregate_tunnel(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Starting time boundary as Unix epoch timestamp in milliseconds. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Ending time boundary as Unix epoch timestamp in milliseconds. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for data aggregation. Determines the resolution of the returned statistics."
        ),
    ],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    groupPk: Annotated[
        str | None,
        Field(
            default=None,
            description="Internal group ID to filter stats for appliances within that group. Only used when nePk is not provided.",
        ),
    ] = None,
    tunnelName: Annotated[
        str | None, Field(default=None, description="Filter results to a specific tunnel by name.")
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, uses IP address as the grouping key instead of internal appliance ID (nePk).",
        ),
    ] = None,
    metric: Annotated[
        str | None, Field(default=None, description="Metric to sort results by. Required when using 'top' parameter.")
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of top results to return when sorting by metric. Requires 'metric' parameter to be specified.",
        ),
    ] = None,
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter tunnels by overlay type. 'all' returns bonded tunnels; '0' returns physical tunnels; specific ID returns tunnels for that overlay; omit to return all tunnels.",
        ),
    ] = None,
    format: Annotated[
        str | None, Field(default=None, description="Output format. Use 'csv' for CSV file download.")
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups stats by appliance with nested structure. When false, returns flat stats.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if groupPk is not None:
        query_params["groupPk"] = groupPk
    if tunnelName is not None:
        query_params["tunnelName"] = tunnelName
    if ip is not None:
        query_params["ip"] = ip
    if metric is not None:
        query_params["metric"] = metric
    if top is not None:
        query_params["top"] = top
    if overlay is not None:
        query_params["overlay"] = overlay
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/aggregate/tunnel",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_apdex",
    description="POST /stats2/aggregate/apdex\n\ngetApdexSummaryStats\n\nRetrieve APDEX summary statistics for specified appliances.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_apdex(
    ctx: Context,
    timestamp: Annotated[
        int | None,
        Field(
            default=None,
            description="EPOCH timestamp (seconds) defining the minimum time boundary for data retrieval. Only records with timestamp >= this value are returned.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if timestamp is not None:
        query_params["timestamp"] = timestamp
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/apdex",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_application",
    description="POST /stats2/aggregate/application\n\ngetApplicationAggregatedStatsByPost\n\nGet aggregated application statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_application(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of time range as Unix epoch timestamp in milliseconds. Must be less than endTime and non-negative."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of time range as Unix epoch timestamp in milliseconds. Must be greater than startTime and non-negative."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation granularity. Determines which statistics table is queried (minute, hourly, or daily)."
        ),
    ],
    application: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter results to a specific application name. When omitted, returns stats for all applications.",
        ),
    ] = None,
    trafficType: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by traffic optimization type. Values map to: optimized_traffic(1), pass_through_shaped(2), pass_through_unshaped(3), all_traffic(4).",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, includes appliance IP address in response instead of using only nePk as identifier. Default is false.",
        ),
    ] = None,
    metric: Annotated[
        str | None,
        Field(
            default=None,
            description="Metric to sort results by. Required when using 'top' parameter. Currently supports 'throughput' which sorts by total LAN bytes (LRX + LTX).",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limit results to top N applications by the specified metric. Requires 'metric' parameter. Returns top+1 results.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if application is not None:
        query_params["application"] = application
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if ip is not None:
        query_params["ip"] = ip
    if metric is not None:
        query_params["metric"] = metric
    if top is not None:
        query_params["top"] = top
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/application",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_application2",
    description="POST /stats2/aggregate/application2\n\ngetApplication2AggregatedStatsByPost\n\nGet aggregated application bandwidth statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_application2(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary for the data query as a Unix EPOCH timestamp in milliseconds. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary for the data query as a Unix EPOCH timestamp in milliseconds. Must be greater than startTime."
        ),
    ],
    application: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter results by application name. When omitted, returns statistics for all applications.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limit results to top N applications by throughput. When specified, returns only the highest bandwidth applications.",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, if no data is found in the specified time range, automatically fetches data from one hour prior. Useful for near-real-time dashboards.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if application is not None:
        query_params["application"] = application
    if top is not None:
        query_params["top"] = top
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/application2",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_application_performance",
    description="POST /stats2/aggregate/applicationPerformance\n\ngetAggregatedApplicationPerformanceStats\n\nRetrieve aggregated application performance statistics for specified appliances.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_application_performance(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Start time boundary in EPOCH milliseconds. Must be non-negative and less than endTime.")
    ],
    endTime: Annotated[
        int,
        Field(description="End time boundary in EPOCH milliseconds. Must be non-negative and greater than startTime."),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for data aggregation. Determines how statistics are bucketed and averaged."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of results to return. When not specified, all matching records are returned.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/applicationPerformance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_dns",
    description="POST /stats2/aggregate/dns\n\ngetDnsAggregatedStats\n\nGet aggregated DNS statistics filtered by appliances and query parameters",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_dns(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary for data range in seconds since EPOCH (Unix timestamp). Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary for data range in seconds since EPOCH (Unix timestamp). Must be greater than startTime."
        ),
    ],
    isSource: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter DNS records by traffic direction. 0 = destination traffic, 1 = source traffic.",
        ),
    ] = None,
    splitType: Annotated[
        int | None,
        Field(default=None, description="Filter by protocol type. 0 = HTTP, 1 = HTTPS, 2 = unassigned, 3 = others."),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of DNS records to return. Results ordered by total LAN bytes (LANRX + LANTX) descending.",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="If true and no data found in specified time range, automatically queries one hour earlier. Useful for recent data lookups.",
        ),
    ] = None,
    splitByNe: Annotated[
        bool | None,
        Field(
            default=None,
            description="If true, results are grouped by appliance (nePk) with nested stats per appliance. Default is null (no split).",
        ),
    ] = None,
    groupBy: Annotated[
        str | None,
        Field(
            default=None,
            description="Column name to group results by. Valid values: associd, timestamp, country, calc_dns, is_source, split_type, service_id, dns, ipaddr, flow_count, DOMAIN1, DOMAIN2, DOMAIN3, DOMAIN4. Use 'country' to group by geographic location.",
        ),
    ] = None,
    groupBySubDomains: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of sub-domain levels to include in grouping (1-4). Default is 2. Controls domain hierarchy depth in results.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if isSource is not None:
        query_params["isSource"] = isSource
    if splitType is not None:
        query_params["splitType"] = splitType
    if top is not None:
        query_params["top"] = top
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    if splitByNe is not None:
        query_params["splitByNe"] = splitByNe
    if groupBy is not None:
        query_params["groupBy"] = groupBy
    if groupBySubDomains is not None:
        query_params["groupBySubDomains"] = groupBySubDomains
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/dns",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_interface_overlay",
    description="POST /stats2/aggregate/interfaceOverlay\n\ngetInterfaceOverlayAggregatedStats\n\nGet aggregated interface overlay transport statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_interface_overlay(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) for the start of the data time range. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) for the end of the data time range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data granularity level determining which statistics table to query. Affects data resolution and aggregation."
        ),
    ],
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by overlay ID. Use '0' for physical tunnels only, omit for all bonded and physical tunnels, or specify an overlay ID for specific bonded tunnels.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if overlay is not None:
        query_params["overlay"] = overlay
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/interfaceOverlay",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_ipsla",
    description="POST /stats2/aggregate/ipsla\n\ngetIpSlaAggregateStats\n\nGet aggregate IP SLA statistics for monitoring probes across appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_ipsla(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Epoch time in seconds for the start of the data time range. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Epoch time in seconds for the end of the data time range. Must be >= 0 and greater than startTime."
        ),
    ],
    granularity: Annotated[str, Field(description="Time interval granularity for data aggregation. Case-insensitive.")],
    configKey: Annotated[
        str | None,
        Field(
            default=None, description="IP SLA configuration key to filter results by a specific probe configuration."
        ),
    ] = None,
    target: Annotated[
        str | None,
        Field(
            default=None,
            description="IP SLA target address defined in the operation name, used to filter results for a specific destination.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of data rows to return. Defaults to 10000 if not specified or if the value exceeds 10000.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if configKey is not None:
        query_params["configKey"] = configKey
    if target is not None:
        query_params["target"] = target
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/ipsla",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_mos",
    description="POST /stats2/aggregate/mos\n\ngetAggregateMosStats\n\nGet aggregate Mean Opinion Score (MOS) statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_mos(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of the time range as Unix epoch timestamp in seconds. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(description="End of the time range as Unix epoch timestamp in seconds. Must be greater than startTime."),
    ],
    granularity: Annotated[
        str, Field(description="Time granularity for data aggregation. Determines the rollup interval for statistics.")
    ],
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limits results to the top N items based on MOS ranking. When not provided, returns all matching records.",
        ),
    ] = None,
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filters tunnels by overlay. Use '0' for physical tunnels only, omit for all tunnels (bonded and physical), or provide overlay ID for bonded tunnels of that overlay.",
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="Groups results by network element (appliance). Default is true, adding an extra level of nesting by appliance nePk in the response.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if top is not None:
        query_params["top"] = top
    if overlay is not None:
        query_params["overlay"] = overlay
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/mos",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_overlays_bandwidth",
    description="POST /stats2/aggregate/overlays/bandwidth\n\ngetAggregatedOverlaysStats\n\nGet aggregated overlay bandwidth statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_overlays_bandwidth(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (milliseconds) marking the start of the time range for statistics retrieval. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (milliseconds) marking the end of the time range for statistics retrieval. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval granularity for data aggregation. Determines the resolution of returned statistics data points."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/overlays/bandwidth",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_ports",
    description="POST /stats2/aggregate/ports\n\ngetPortAggregateStatsByPost\n\nRetrieve aggregated port statistics filtered by appliances and query parameters",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_ports(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(description="Start of time range as Unix epoch seconds. Data is queried from the hourlytopport table."),
    ],
    endTime: Annotated[
        int, Field(description="End of time range as Unix epoch seconds (exclusive). Must be greater than startTime.")
    ],
    isSource: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by traffic direction. 0 = destination port, 1 = source port. If omitted, returns both.",
        ),
    ] = None,
    isKnown: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by port assignment status. 0 = unassigned/unknown port, 1 = assigned to a known application. If omitted, returns both.",
        ),
    ] = None,
    protocol: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by protocol number (e.g., 6 = TCP, 17 = UDP). If omitted, returns all protocols.",
        ),
    ] = None,
    port: Annotated[
        int | None, Field(default=None, description="Filter by specific port number. If omitted, returns all ports.")
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limit results to top N entries by total LAN traffic (LANRX_BYTES + LANTX_BYTES descending).",
        ),
    ] = None,
    splitByNe: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, results are grouped by appliance (nePk). When false/null, aggregates across all appliances.",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true and no data found in specified time range, automatically retries with time range shifted back by one hour.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if isSource is not None:
        query_params["isSource"] = isSource
    if isKnown is not None:
        query_params["isKnown"] = isKnown
    if protocol is not None:
        query_params["protocol"] = protocol
    if port is not None:
        query_params["port"] = port
    if top is not None:
        query_params["top"] = top
    if splitByNe is not None:
        query_params["splitByNe"] = splitByNe
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/ports",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_shaper",
    description="POST /stats2/aggregate/shaper\n\ngetShaperAggregateStats\n\nRetrieve aggregated shaper QoS statistics for appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_shaper(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Start time boundary as Unix epoch seconds. Must be >= 0 and less than endTime.")
    ],
    endTime: Annotated[
        int, Field(description="End time boundary as Unix epoch seconds. Must be >= 0 and greater than startTime.")
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation granularity determining which stats table to query (minute, hour, day, or month)."
        ),
    ],
    direction: Annotated[
        int | None,
        Field(
            default=None,
            description="Traffic direction filter. 0=Outbound (LAN to WAN), 1=Inbound (WAN to LAN). If omitted, returns both directions.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of rows to return, ordered by totalBytes descending. If omitted, returns all results.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if direction is not None:
        query_params["direction"] = direction
    if top is not None:
        query_params["top"] = top
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/shaper",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_top_talkers",
    description="POST /stats2/aggregate/topTalkers\n\ngetTopTalkersAggregateStatsByPost\n\nRetrieve aggregated top talkers statistics for specified appliances.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_top_talkers(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(description="Start of the time range in seconds since UNIX epoch. Must be >= 0 and less than endTime."),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range in seconds since UNIX epoch. Must be >= 0 and greater than startTime."
        ),
    ],
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of top talker records to return per appliance. Optional; returns all if not specified.",
        ),
    ] = None,
    splitByNe: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, adds an extra grouping level in the response to split stats by appliance (nePk). Default is null (no splitting).",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true and no data found in the specified range, automatically queries one hour earlier (startTime-3600, endTime-3600).",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if top is not None:
        query_params["top"] = top
    if splitByNe is not None:
        query_params["splitByNe"] = splitByNe
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/topTalkers",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_tunnel",
    description="POST /stats2/aggregate/tunnel\n\ngetAggregatedTunnelsStatsByPost\n\nRetrieve aggregated tunnel statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_tunnel(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (seconds) for the start of the data time range. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (seconds) for the end of the data time range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Time granularity for data aggregation. Determines which statistics table is queried.")
    ],
    metric: Annotated[
        str | None,
        Field(
            default=None,
            description="Metric to sort and filter results by. Required when using 'top' parameter. Determines which statistics columns are included in response.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limit results to top N tunnels by the specified metric. Requires 'metric' parameter to be set.",
        ),
    ] = None,
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by overlay ID. Use 'all' for all bonded tunnels, '0' for physical tunnels only, or a specific overlay ID for bonded tunnels associated with that overlay. Omit to return all tunnels.",
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="Group statistics by appliance (network element). When true, response includes nePk in each stats object. Default: true.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if metric is not None:
        query_params["metric"] = metric
    if top is not None:
        query_params["top"] = top
    if overlay is not None:
        query_params["overlay"] = overlay
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/tunnel",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats2_aggregate_user2",
    description="POST /stats2/aggregate/user2\n\ngetUser2AggregatedStatsByPost\n\nGet aggregated user bandwidth statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats2_aggregate_user2(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) for the start of the time range. Required for data retrieval."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) for the end of the time range. Must be greater than startTime."
        ),
    ],
    user2: Annotated[
        str | None,
        Field(
            default=None,
            description="Username to filter statistics. When omitted, returns aggregated stats for all users.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None, description="Limits results to top N users by throughput. When omitted, returns all users."
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true and no data is found in the specified time range, automatically fetches data from one hour prior. Default is false.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if user2 is not None:
        query_params["user2"] = user2
    if top is not None:
        query_params["top"] = top
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats2/aggregate/user2",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats3_aggregate_appliance",
    description="POST /stats3/aggregate/appliance\n\ngetApplianceAggregatedStatsByPost\n\nRetrieve aggregated appliance statistics by throughput or packet metrics.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats3_aggregate_appliance(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Start time boundary in EPOCH milliseconds. Must be >= 0 and less than endTime.")
    ],
    endTime: Annotated[
        int, Field(description="End time boundary in EPOCH milliseconds. Must be >= 0 and greater than startTime.")
    ],
    granularity: Annotated[
        str, Field(description="Data aggregation interval. Determines how stats are grouped over time.")
    ],
    metric: Annotated[
        str, Field(description="Metric type determining which stats to aggregate and sort by. Required parameter.")
    ],
    trafficType: Annotated[
        str | None,
        Field(default=None, description="Filter stats by traffic type. When omitted, returns all traffic types."),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limit results to top N appliances by the specified metric. Requires metric parameter.",
        ),
    ] = None,
    ip: Annotated[
        bool | None, Field(default=None, description="Include IP address information in the response.")
    ] = None,
    format: Annotated[
        str | None, Field(default=None, description="Response format. Use 'csv' to download as Excel-compatible file.")
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if metric is not None:
        query_params["metric"] = metric
    if top is not None:
        query_params["top"] = top
    if ip is not None:
        query_params["ip"] = ip
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats3/aggregate/appliance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats3_aggregate_interface",
    description="POST /stats3/aggregate/interface\n\ngetInterfaceAggregatedStatsByPost\n\nGet aggregated interface statistics for appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats3_aggregate_interface(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp in seconds (EPOCH) marking the start of the time range. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp in seconds (EPOCH) marking the end of the time range. Must be >= 0 and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval for data aggregation. Determines whether statistics are grouped by minute, hour, or day."
        ),
    ],
    trafficType: Annotated[
        str,
        Field(
            description="Filter statistics by traffic category. Required parameter to specify which traffic type to include in results."
        ),
    ],
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Output format for the response. When set to 'csv', returns data as downloadable CSV file instead of JSON.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats3/aggregate/interface",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats3_aggregate_tunnel",
    description="POST /stats3/aggregate/tunnel\n\ngetAggregatedTunnelsStatsByPost\n\nRetrieve aggregated tunnel statistics filtered by query parameters",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats3_aggregate_tunnel(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary for the data range as Unix epoch timestamp in seconds. Must be greater than or equal to 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary for the data range as Unix epoch timestamp in seconds. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(description="Time granularity for data aggregation. Determines the resolution of statistics returned."),
    ],
    metric: Annotated[
        str,
        Field(
            description="Metric type to sort and aggregate stats by. Required parameter that determines which statistics columns are returned."
        ),
    ],
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limits results to top N tunnels by the specified metric. Requires metric parameter to be set. Used for ranking tunnels by performance.",
        ),
    ] = None,
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter tunnels by overlay type. Use 'all' for bonded tunnels only, '0' for physical tunnels only, specific overlay ID for tunnels in that overlay, or omit for all tunnel types.",
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="Group results by network element (appliance). When true, response includes nePk field in each stats object. Default is true.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if metric is not None:
        query_params["metric"] = metric
    if top is not None:
        query_params["top"] = top
    if overlay is not None:
        query_params["overlay"] = overlay
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats3/aggregate/tunnel",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_application2",
    description="POST /stats/aggregate/application2\n\ngetApplication2AggregatedStatsByPost\n\nGet aggregate application stats for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_application2(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (milliseconds) marking the start of the query time range. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (milliseconds) marking the end of the query time range. Must be non-negative and greater than startTime."
        ),
    ],
    application: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter results to a specific application name. Case-sensitive exact match. If omitted, returns stats for all applications.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Return only the top N applications by total throughput. Useful for identifying highest bandwidth consumers.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Output format for the response. Set to 'csv' for CSV file download. Omit or use any other value for JSON response.",
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="Group results by appliance identifier. When true (default), each result includes the nePk field. When false, results are aggregated across all specified appliances.",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="Enable automatic retry with shifted time range. When true and no data found, the query retries with startTime and endTime shifted back by 3600000ms (1 hour).",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if application is not None:
        query_params["application"] = application
    if top is not None:
        query_params["top"] = top
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/application2",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_boost",
    description="POST /stats/aggregate/boost\n\ngetAggregateBoostStats\n\nGet Boost stats for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_boost(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Start time in seconds since EPOCH. Must be >= 0 and less than endTime.")
    ],
    endTime: Annotated[
        int, Field(description="End time in seconds since EPOCH. Must be >= 0 and greater than startTime.")
    ],
    granularity: Annotated[
        str, Field(description="Time-based aggregation level. Controls grouping interval for statistics.")
    ],
    format: Annotated[
        str | None, Field(default=None, description="Output format. Set to 'csv' for downloadable CSV file.")
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(default=None, description="Group results by appliance. When true, includes nePk in response."),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/boost",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_dns",
    description="POST /stats/aggregate/dns\n\ngetDnsAggregatedStats\n\nGet DNS aggregate statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_dns(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Query start time as Unix epoch seconds. Must be non-negative and less than endTime.")
    ],
    endTime: Annotated[int, Field(description="Query end time as Unix epoch seconds. Must be greater than startTime.")],
    isSource: Annotated[
        int | None,
        Field(
            default=None, description="Filter by traffic direction. 0=destination DNS queries, 1=source DNS queries."
        ),
    ] = None,
    splitType: Annotated[
        int | None,
        Field(default=None, description="Filter by protocol type. 0=HTTP, 1=HTTPS, 2=unassigned, 3=other protocols."),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None, description="Maximum number of DNS entries to return per appliance. Limits result set size."
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="Fallback mode: when true and no data found, automatically queries one hour earlier (startTime-3600 to endTime-3600).",
        ),
    ] = None,
    splitByNe: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, results are grouped by appliance ID in separate response objects. When false/null, data is aggregated.",
        ),
    ] = None,
    groupBy: Annotated[
        str | None,
        Field(
            default=None,
            description="Aggregation dimension. 'dns' groups by domain name, 'country' groups by geographic location.",
        ),
    ] = None,
    groupBySubDomains: Annotated[
        int | None,
        Field(
            default=None,
            description="Domain depth for grouping. Value 2 yields 'example.com', value 3 yields 'sub.example.com'.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if isSource is not None:
        query_params["isSource"] = isSource
    if splitType is not None:
        query_params["splitType"] = splitType
    if top is not None:
        query_params["top"] = top
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    if splitByNe is not None:
        query_params["splitByNe"] = splitByNe
    if groupBy is not None:
        query_params["groupBy"] = groupBy
    if groupBySubDomains is not None:
        query_params["groupBySubDomains"] = groupBySubDomains
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/dns",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_dscp",
    description="POST /stats/aggregate/dscp\n\ngetDscpAggregatedStatsByPost\n\nGet DSCP aggregate statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_dscp(
    ctx: Context,
    granularity: Annotated[
        str, Field(description="Data aggregation interval. Maps to database table: minute, hourly, daily, or monthly.")
    ],
    trafficType: Annotated[
        str,
        Field(
            description="Traffic type classification. Maps to: 1=Optimized, 2=Pass-through Shaped, 3=Pass-through Unshaped, 4=All Traffic."
        ),
    ],
    startTime: Annotated[
        int, Field(description="EPOCH timestamp for data range start. Must be >= 0 and less than endTime.")
    ],
    endTime: Annotated[
        int, Field(description="EPOCH timestamp for data range end. Must be >= 0 and greater than startTime.")
    ],
    dscp: Annotated[
        int | None,
        Field(default=None, description="DSCP value filter (0-63). Omit to return stats for all DSCP values."),
    ] = None,
    ip: Annotated[
        bool | None, Field(default=None, description="Use IP address as grouping key instead of nePk. Default: false.")
    ] = None,
    metric: Annotated[
        str | None,
        Field(default=None, description="Metric for sorting/filtering results. Required when 'top' is specified."),
    ] = None,
    top: Annotated[
        int | None,
        Field(default=None, description="Limit results to top N items sorted by metric. Requires 'metric' parameter."),
    ] = None,
    format: Annotated[
        str | None, Field(default=None, description="Set to 'csv' to download results as CSV file.")
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="Group results by appliance. Default: true. When false, aggregates across all appliances.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if granularity is not None:
        query_params["granularity"] = granularity
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if dscp is not None:
        query_params["dscp"] = dscp
    if ip is not None:
        query_params["ip"] = ip
    if metric is not None:
        query_params["metric"] = metric
    if top is not None:
        query_params["top"] = top
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/dscp",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_flow",
    description="POST /stats/aggregate/flow\n\ngetFlowAggregatedStatsByPost\n\nRetrieve aggregated flow statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_flow(
    ctx: Context,
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for data aggregation. Valid values: minute, hour, day, month. Case-insensitive."
        ),
    ],
    startTime: Annotated[
        int,
        Field(
            description="Start of time range as Unix epoch timestamp in milliseconds. Must be >= 0 and strictly less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of time range as Unix epoch timestamp in milliseconds. Must be >= 0 and strictly greater than startTime."
        ),
    ],
    flowType: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by flow type. TCP_ACCELERATED (1)=optimized TCP, TCP_NOT_ACCELERATED (2)=unoptimized TCP, NON_TCP (3)=UDP/other protocols. Case-sensitive.",
        ),
    ] = None,
    trafficType: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by traffic classification. OPTIMIZED_TRAFFIC (1), PASS_THROUGH_SHAPED (2), PASS_THROUGH_UNSHAPED (3), ALL_TRAFFIC (4). Case-insensitive.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, uses IP address as the grouping key instead of nePk in response. Default is false.",
        ),
    ] = None,
    metric: Annotated[
        str | None,
        Field(default=None, description="Metric name for top-N filtering. Required if 'top' parameter is provided."),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Return only top N results sorted by the specified metric. Requires 'metric' parameter.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. Use 'csv' to download as CSV file with Excel-compatible headers. Default is JSON.",
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true (default), groups stats by appliance with nested structure. When false, returns flat aggregated results.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if granularity is not None:
        query_params["granularity"] = granularity
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if flowType is not None:
        query_params["flowType"] = flowType
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if ip is not None:
        query_params["ip"] = ip
    if metric is not None:
        query_params["metric"] = metric
    if top is not None:
        query_params["top"] = top
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/flow",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_flow_active",
    description="POST /stats/aggregate/flow/active\n\ngetActiveFlowCountsByPost\n\nRetrieve active flow counts by appliance IDs",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_flow_active(
    ctx: Context,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of appliance results to return. When not specified, returns all matching appliances.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if top is not None:
        query_params["top"] = top
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/flow/active",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_interface",
    description="POST /stats/aggregate/interface\n\ngetInterfaceAggregatedStatsByPost\n\nRetrieve aggregated interface statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_interface(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of the time range as Unix epoch timestamp in seconds. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(description="End of the time range as Unix epoch timestamp in seconds. Must be greater than startTime."),
    ],
    granularity: Annotated[
        str, Field(description="Time granularity for data aggregation. Determines the time bucket size for statistics.")
    ],
    trafficType: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter statistics by traffic type. If not specified, returns data for all traffic types. Defaults to 'all_traffic' when format=csv.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. If set to 'csv', returns data as a downloadable CSV file. Otherwise returns JSON.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/interface",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_interface_overlay",
    description="POST /stats/aggregate/interfaceOverlay\n\ngetInterfaceOverlayAggregatedStats\n\nRetrieve aggregated interface overlay transport statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_interface_overlay(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of the time range as Unix epoch timestamp in seconds. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(description="End of the time range as Unix epoch timestamp in seconds. Must be greater than startTime."),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for data aggregation. Determines which stats table is queried (minute, hourly, or daily)."
        ),
    ],
    interfaceName: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional filter to retrieve stats for a specific interface by name. If not provided, returns stats for all interfaces.",
        ),
    ] = None,
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by overlay ID. Use '0' for physical tunnels only, 'all' or omit for all tunnels, or specify a numeric overlay ID for bonded tunnels.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. If set to 'csv', returns data as a downloadable CSV file. Otherwise returns JSON.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if interfaceName is not None:
        query_params["interfaceName"] = interfaceName
    if overlay is not None:
        query_params["overlay"] = overlay
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/interfaceOverlay",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_jitter",
    description="POST /stats/aggregate/jitter\n\ngetAggregateJitterStatsByPost\n\nGet aggregate jitter stats for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_jitter(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since epoch) for the start of the data time range. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since epoch) for the end of the data time range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Data aggregation interval. Determines how stats are grouped temporally.")
    ],
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, uses IP address as grouping key instead of internal appliance ID. Default is false.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None, description="Maximum number of results to return. Limits response size for large datasets."
        ),
    ] = None,
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter tunnels by overlay type. Use 'all' for bonded tunnels, '0' for physical tunnels only, or specific overlay ID.",
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups results by appliance with nested stats objects. Default is true.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. Use 'csv' to download results as CSV file. Omit for JSON response.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if ip is not None:
        query_params["ip"] = ip
    if top is not None:
        query_params["top"] = top
    if overlay is not None:
        query_params["overlay"] = overlay
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/jitter",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_mos",
    description="POST /stats/aggregate/mos\n\ngetAggregateMosStats\n\nGet aggregated MOS statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_mos(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since epoch) for data range start. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since epoch) for data range end. Must be >= 0 and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Time interval for data aggregation. Determines statistical granularity.")
    ],
    top: Annotated[int | None, Field(default=None, description="Limit results to top N tunnels by MOS value.")] = None,
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by overlay ID. Use '0' for physical tunnels only, omit for all tunnels, or specify overlay ID for bonded tunnels.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Response format. Set to 'csv' for CSV file download, omit for JSON response."),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(default=None, description="Group statistics by appliance. Adds nesting level by appliance in response."),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if top is not None:
        query_params["top"] = top
    if overlay is not None:
        query_params["overlay"] = overlay
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/mos",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_ports",
    description="POST /stats/aggregate/ports\n\ngetPortAggregatedStatsByPost\n\nGet aggregated port statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_ports(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of time range in seconds since EPOCH. Must be less than endTime. Validated by validateTime() method."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of time range in seconds since EPOCH. Must be greater than startTime. Validated by validateTime() method."
        ),
    ],
    isSource: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by port direction. 1 = source port, 0 = destination port. Omit to include both directions.",
        ),
    ] = None,
    isKnown: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by application classification. 1 = known application port, 0 = unclassified. Omit to include both.",
        ),
    ] = None,
    protocol: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by IP protocol number. Common values: 6 (TCP), 17 (UDP), 1 (ICMP). Omit to include all protocols.",
        ),
    ] = None,
    port: Annotated[
        int | None, Field(default=None, description="Filter by specific port number. Omit to include all ports.")
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limit results to top N records sorted by total LAN bytes (LANRX_BYTES + LANTX_BYTES) descending.",
        ),
    ] = None,
    splitByNe: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, results are grouped by appliance (nePk column included in GROUP BY). Each appliance returns separate stats.",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="Fallback mechanism: if true and no data found in time range, automatically queries (startTime-3600, endTime-3600). Useful for dashboards.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if isSource is not None:
        query_params["isSource"] = isSource
    if isKnown is not None:
        query_params["isKnown"] = isKnown
    if protocol is not None:
        query_params["protocol"] = protocol
    if port is not None:
        query_params["port"] = port
    if top is not None:
        query_params["top"] = top
    if splitByNe is not None:
        query_params["splitByNe"] = splitByNe
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/ports",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_security_policy",
    description="POST /stats/aggregate/securityPolicy\n\ngetAggregateSecurityPolicyStats\n\nGet aggregated security policy stats for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_security_policy(
    ctx: Context,
    startTime: Annotated[int, Field(description="Start time as Unix epoch (seconds). Must be >= 0 and < endTime.")],
    endTime: Annotated[int, Field(description="End time as Unix epoch (seconds). Must be >= 0 and > startTime.")],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation interval. Case-insensitive. Maps to database tables: minute, hourly, daily, monthly."
        ),
    ],
    top: Annotated[int | None, Field(default=None, description="Limit results to top N zone pairs by traffic.")] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Set to 'csv' for file download (SecurityPolicyAggregateStats.csv)."),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, results include nePk for per-appliance breakdown. When false or null, defaults to true.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if top is not None:
        query_params["top"] = top
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/securityPolicy",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_top_talkers",
    description="POST /stats/aggregate/topTalkers\n\ngetTopTalkersAggregateStatsByPost\n\nGet aggregated top talkers statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_top_talkers(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of time range as Unix epoch timestamp in seconds. Required. Must be >= 0 and < endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of time range as Unix epoch timestamp in seconds. Required. Must be >= 0 and > startTime."
        ),
    ],
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of top talker records to return per appliance. Limits results sorted by total LAN bytes (LANRX + LANTX).",
        ),
    ] = None,
    splitByNe: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups results by appliance with nePk field indicating which appliance the stats belong to.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. Use 'csv' for CSV file download (TopTalkersAggregateStats.csv). Default returns JSON.",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true and no data exists for the time range, automatically queries data from one hour prior (startTime-3600, endTime-3600).",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if top is not None:
        query_params["top"] = top
    if splitByNe is not None:
        query_params["splitByNe"] = splitByNe
    if format is not None:
        query_params["format"] = format
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/topTalkers",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_top_talkers_destinations",
    description="POST /stats/aggregate/topTalkers/destinations\n\ngetTopTalkerDestinations\n\nGet aggregate top talkers destination statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_top_talkers_destinations(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary in Unix epoch seconds (signed 64-bit). Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary in Unix epoch seconds (signed 64-bit). Must be >= 0 and greater than startTime."
        ),
    ],
    top: Annotated[
        int,
        Field(
            description="Maximum number of top destination results to return, ordered by total LAN bandwidth (LANRX_BYTES + LANTX_BYTES) descending."
        ),
    ],
    sourceIp: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter results by source IP address. Use 'Others' to query destinations for empty/unknown source IPs. When omitted, returns all destinations regardless of source.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if sourceIp is not None:
        query_params["sourceIp"] = sourceIp
    if top is not None:
        query_params["top"] = top
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/topTalkers/destinations",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_traffic_behavior",
    description="POST /stats/aggregate/trafficBehavior\n\ngetTrafficBehavioralAggregatedStatsByPost\n\nGet traffic behavioral stats for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_traffic_behavior(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Start time in Unix epoch seconds. Must be non-negative and less than endTime.")
    ],
    endTime: Annotated[
        int, Field(description="End time in Unix epoch seconds. Must be non-negative and greater than startTime.")
    ],
    behavioralCate: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by behavioral category name. Common values: Business, Recreational, Streaming, General.",
        ),
    ] = None,
    application: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by application name to retrieve stats for a specific application within the category.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Output format. Use 'CSV' for downloadable CSV file (case-insensitive)."),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limit results to top N entries ranked by traffic volume. Useful for dashboard displays.",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="If no data in last hour, fetch from one hour earlier. Useful for recent data queries. Default: false.",
        ),
    ] = None,
    isAggregated: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns aggregated summary stats by category. When false, returns detailed per-application stats. Default: false.",
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include appliance-level breakdown in response. Only used when nePk is provided. Default: true.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if behavioralCate is not None:
        query_params["behavioralCate"] = behavioralCate
    if application is not None:
        query_params["application"] = application
    if format is not None:
        query_params["format"] = format
    if top is not None:
        query_params["top"] = top
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    if isAggregated is not None:
        query_params["isAggregated"] = isAggregated
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/trafficBehavior",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_traffic_class",
    description="POST /stats/aggregate/trafficClass\n\ngetTrafficClassAggregatedStatsByPost\n\nGet aggregated traffic class statistics for multiple appliances via POST",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_traffic_class(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Start of data time range in EPOCH milliseconds. Must be >= 0 and less than endTime.")
    ],
    endTime: Annotated[
        int, Field(description="End of data time range in EPOCH milliseconds. Must be >= 0 and greater than startTime.")
    ],
    granularity: Annotated[
        str, Field(description="Time interval for data aggregation. Case-insensitive (e.g., 'MINUTE', 'Hour').")
    ],
    trafficClass: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by QoS traffic class priority level (1=highest). When omitted, returns all traffic classes.",
        ),
    ] = None,
    trafficType: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by traffic optimization type. Case-insensitive. When omitted, returns all traffic types.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="Use IP address as grouping key instead of nePk. Affects response structure when groupByNE=true.",
        ),
    ] = None,
    metric: Annotated[
        str | None, Field(default=None, description="Metric for sorting results. Required when 'top' is specified.")
    ] = None,
    top: Annotated[
        int | None,
        Field(default=None, description="Return only top N results sorted by metric. Requires 'metric' parameter."),
    ] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Output format. Set to 'csv' for downloadable Excel-compatible file."),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="Group statistics by appliance. When true (default), response is keyed by nePk or IP.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if trafficClass is not None:
        query_params["trafficClass"] = trafficClass
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if ip is not None:
        query_params["ip"] = ip
    if metric is not None:
        query_params["metric"] = metric
    if top is not None:
        query_params["top"] = top
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/trafficClass",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_tunnel",
    description="POST /stats/aggregate/tunnel\n\ngetTunnelAggregatedStatsByPost\n\nGet aggregated tunnel statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_tunnel(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(description="Start of time range as Unix epoch timestamp in milliseconds. Must be >= 0 and < endTime."),
    ],
    endTime: Annotated[
        int, Field(description="End of time range as Unix epoch timestamp in milliseconds. Must be > startTime.")
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for aggregation. Valid values: minute, hour, day, month. Case-insensitive."
        ),
    ],
    ip: Annotated[
        bool | None,
        Field(default=None, description="When true, uses IP address as grouping key instead of nePk. Default: false."),
    ] = None,
    metric: Annotated[
        str | None,
        Field(
            default=None,
            description="Metric for sorting and filtering top results. Required if 'top' is specified. Must be non-empty when provided.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limit results to top N entries sorted by metric. Requires 'metric' parameter. Must be >= 1.",
        ),
    ] = None,
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by overlay type. 'all' = bonded tunnels, '0' = physical tunnels, specific ID = tunnels for that overlay. Omit to include all.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. Set to 'csv' for downloadable CSV file (Content-Type: application/vnd.ms-excel).",
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups results by appliance in nested structure. When false, returns flat list. Default: true.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if ip is not None:
        query_params["ip"] = ip
    if metric is not None:
        query_params["metric"] = metric
    if top is not None:
        query_params["top"] = top
    if overlay is not None:
        query_params["overlay"] = overlay
    if format is not None:
        query_params["format"] = format
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/tunnel",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_aggregate_user2",
    description="POST /stats/aggregate/user2\n\ngetUser2AggregatedStatsByPost\n\nRetrieve aggregated user statistics for specified appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_aggregate_user2(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of the time range as Unix epoch timestamp in seconds. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range as Unix epoch timestamp in seconds. Must be >= 0 and greater than startTime."
        ),
    ],
    user: Annotated[
        str | None,
        Field(
            default=None, description="Filter results by specific user name. If omitted, returns stats for all users."
        ),
    ] = None,
    groupByNE: Annotated[
        bool | None,
        Field(
            default=None,
            description="Groups statistics by appliance (Network Element). When true, response includes an extra level with appliance identifiers as keys. Default is true.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Limits results to top N users ranked by throughput. If not specified, returns all users.",
        ),
    ] = None,
    lastHour: Annotated[
        bool | None,
        Field(
            default=None,
            description="If true and no data found in the specified time range, retries query with timestamps shifted back by 1 hour.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Response format. Use 'csv' for CSV file download, otherwise returns JSON."),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if user is not None:
        query_params["user"] = user
    if groupByNE is not None:
        query_params["groupByNE"] = groupByNE
    if top is not None:
        query_params["top"] = top
    if lastHour is not None:
        query_params["lastHour"] = lastHour
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/aggregate/user2",
        query_params=query_params or None,
        body=body,
    )
