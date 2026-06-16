"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``timeseriesStats``
Operations in this file: 61
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
    name="edgeconnect_get_stats3_timeseries_appliance",
    description="GET /stats3/timeseries/appliance\n\ngetApplianceTimeSeriesStats\n\nGet appliance time series statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats3_timeseries_appliance(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) for the start of the data range. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int, Field(description="Unix epoch timestamp (seconds) for the end of the data range. Must be > startTime.")
    ],
    granularity: Annotated[
        str, Field(description="Data aggregation interval. Determines the time resolution of returned statistics.")
    ],
    trafficType: Annotated[
        str,
        Field(
            description="Type of traffic to filter statistics. Each type represents different WAN optimization categories."
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
            description="Internal group ID to filter appliances. When nePk is omitted, retrieves stats for all appliances in this group; if both omitted, returns stats for all appliances.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None, description="Maximum number of stats records to retrieve. Default and maximum value is 10000."
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None, description="Output format. Set to 'CSV' to download results as a CSV file instead of JSON."
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, uses appliance IP address as the key in the response data object instead of nePk. Default is false.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Shortcut to retrieve the latest N minutes of data. Overrides startTime and endTime when provided. Unit is minutes.",
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
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if latest is not None:
        query_params["latest"] = latest
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats3/timeseries/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats3_timeseries_dscp",
    description="GET /stats3/timeseries/dscp\n\ngetDscpTimeSeriesStats\n\nGet DSCP time series statistics for traffic analysis",
    capability=Capability.READ,
)
async def edgeconnect_get_stats3_timeseries_dscp(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since EPOCH) for the start of the time range. Required unless 'latest' is provided."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since EPOCH) for the end of the time range. Must be greater than startTime. Required unless 'latest' is provided."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval for data aggregation. Determines whether stats are aggregated by minute, hour, day, or month."
        ),
    ],
    trafficType: Annotated[
        str, Field(description="Traffic category filter. Specifies which type of traffic to include in the statistics.")
    ],
    dscp: Annotated[
        int, Field(description="DSCP value to filter statistics. Valid range is 0-63 representing QoS priority levels.")
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
            description="Internal group ID to filter appliances. Used when nePk is not provided to retrieve stats for all appliances in the group.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(default=None, description="Maximum number of data points to return. Default and maximum value is 10000."),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None, description="Output format. Set to 'CSV' for downloadable CSV file, otherwise returns JSON."
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="Use IP address as the grouping key instead of internal appliance ID (nePk). Default is false.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve stats for the last N minutes. Overrides startTime and endTime when provided. Unit is minutes.",
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
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if dscp is not None:
        query_params["dscp"] = dscp
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if latest is not None:
        query_params["latest"] = latest
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats3/timeseries/dscp",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats3_timeseries_tunnel",
    description="GET /stats3/timeseries/tunnel\n\ngetTunnelTimeSeriesStats\n\nGet tunnel time series statistics for a single appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats3_timeseries_tunnel(
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
            description="Start time boundary as Unix epoch seconds (signed 64-bit). Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary as Unix epoch seconds (signed 64-bit). Must be >= 0 and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation interval. Determines which database table is queried (minute, hourly, or daily)."
        ),
    ],
    tunnelAlias: Annotated[str, Field(description="Tunnel name/alias to filter statistics. Cannot be empty.")],
    metric: Annotated[
        str,
        Field(
            description="Metric type determining which statistics columns are returned. Each metric returns different column definitions."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(default=None, description="Maximum number of stats records to retrieve. Default: 10000, Maximum: 10000."),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. Use 'CSV' for downloadable Excel-compatible file. Default: JSON.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(default=None, description="Use IP address as key for grouping stats instead of nePk. Default: false."),
    ] = None,
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Overlay filter for bonded tunnels. Required when metric is 'throughput'. Values: '0' returns physical tunnels only; omitted returns all tunnels; other values return bonded tunnels for that overlay ID.",
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
    if tunnelAlias is not None:
        query_params["tunnelAlias"] = tunnelAlias
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if overlay is not None:
        query_params["overlay"] = overlay
    if metric is not None:
        query_params["metric"] = metric
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats3/timeseries/tunnel",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_appliance",
    description="GET /stats/timeseries/appliance\n\ngetApplianceTimeSeriesStats\n\nGet appliance time series statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_appliance(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since epoch) for the start of the time range. Required unless 'latest' parameter is provided."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since epoch) for the end of the time range. Must be greater than startTime. Required unless 'latest' parameter is provided."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval granularity for aggregating stats data. Determines the resolution of returned data points."
        ),
    ],
    trafficType: Annotated[
        str,
        Field(description="Traffic category to filter statistics. Determines which type of traffic data is returned."),
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
            description="Internal group identifier. When specified without nePk, retrieves stats for all appliances in the group.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None, description="Maximum number of stat records to return. Default and maximum value is 10000."
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Output format. When set to 'CSV', returns data as downloadable CSV file instead of JSON.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, uses appliance IP address as the key in response data instead of internal appliance ID (nePk). Default is false.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieves stats for the most recent N minutes. When provided, overrides startTime and endTime (endTime becomes current time, startTime becomes current time minus N minutes).",
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
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if latest is not None:
        query_params["latest"] = latest
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_appliance_process_state",
    description="GET /stats/timeseries/applianceProcessState\n\ngetApplianceProcessState\n\nGet appliance process state time-series statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_appliance_process_state(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    startTime: Annotated[
        int,
        Field(description="Start of the time range in Unix epoch seconds (signed 64-bit). Must be less than endTime."),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range in Unix epoch seconds (signed 64-bit). Must be greater than startTime."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/applianceProcessState",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_application2",
    description="GET /stats/timeseries/application2\n\ngetApplicationTimeSeriesStats\n\nGet application time series statistics filtered by appliance or group",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_application2(
    ctx: Context,
    application: Annotated[
        str,
        Field(
            description="Name of the application to filter statistics for. This parameter is required and cannot be empty."
        ),
    ],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    startTime: Annotated[
        int | None,
        Field(
            default=None,
            description="Start of the time range in Unix epoch seconds (signed 64-bit). Required unless 'latest' parameter is provided. Must be less than endTime and greater than or equal to 0.",
        ),
    ] = None,
    endTime: Annotated[
        int | None,
        Field(
            default=None,
            description="End of the time range in Unix epoch seconds (signed 64-bit). Required unless 'latest' parameter is provided. Must be greater than startTime and greater than or equal to 0.",
        ),
    ] = None,
    groupPk: Annotated[
        str | None,
        Field(
            default=None,
            description="Internal unique identifier of an appliance group. Used to retrieve aggregated stats for all appliances in the group when nePk is not provided.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Output format for the response. When set to 'CSV', returns data as a downloadable CSV file instead of JSON.",
        ),
    ] = None,
    total: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns aggregated total values for the application across all matching appliances. Default behavior returns per-appliance breakdown.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve stats for the last N minutes from current time. When provided, overrides startTime and endTime parameters. Value represents minutes.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of data points to return in the response. Used for pagination or limiting large result sets.",
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
    if groupPk is not None:
        query_params["groupPk"] = groupPk
    if format is not None:
        query_params["format"] = format
    if total is not None:
        query_params["total"] = total
    if latest is not None:
        query_params["latest"] = latest
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/application2",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_availability_appliance",
    description="GET /stats/timeseries/availability/appliance\n\ngetApplianceAvailabilityTimeSeriesStats\n\nGet appliance reachability time series data",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_availability_appliance(
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
            description="Date for which to retrieve availability data. For 'day' granularity, provides minute-level data for this specific date. For 'month' granularity, provides daily data starting from this date's month."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for aggregating reachability data. 'day' returns minute-level samples from minuteappliancereachability table. 'month' returns daily aggregated samples from dailyappliancereachability table."
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
        "/stats/timeseries/availability/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_availability_interface",
    description="GET /stats/timeseries/availability/interface\n\ngetInterfaceAvailabilityTimeSeriesStats\n\nGet interface availability timeseries data",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_availability_interface(
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
            description="Query date in YYYY-MM-DD format. For 'day' granularity, specifies the exact day. For 'month' granularity, use start of month (e.g., '2024-01-01')."
        ),
    ],
    ifName: Annotated[
        str, Field(description="Interface name identifier to filter statistics for a specific network interface.")
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation granularity. 'day' returns minute-level data points for a single day. 'month' returns daily aggregated data points for the entire month."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if date is not None:
        query_params["date"] = date
    if ifName is not None:
        query_params["ifName"] = ifName
    if granularity is not None:
        query_params["granularity"] = granularity
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/availability/interface",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_availability_tunnel",
    description="GET /stats/timeseries/availability/tunnel\n\ngetTunnelAvailabilityTimeseriesStats\n\nGet tunnel availability timeseries data for monitoring tunnel health metrics over time.",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_availability_tunnel(
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
            description="Date for which to retrieve availability data. For 'month' granularity, use the first day of the month."
        ),
    ],
    overlayId: Annotated[
        str,
        Field(
            description="Overlay identifier for tunnel filtering. Use '0' for physical (underlay) tunnels, 'all' for all bonded (overlay) tunnels, or a specific overlay ID."
        ),
    ],
    tunType: Annotated[
        str,
        Field(
            description="Tunnel type filter. For overlays: 0=SD-WAN, 2=Breakout, 3=Services. For underlays: 1=Underlay, 2=Pass-through, 3=Services."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for data aggregation. 'day' returns minute-level data, 'week' and 'month' return daily aggregates."
        ),
    ],
    tunnelName: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by specific tunnel name. Optional parameter to narrow results to a single tunnel.",
        ),
    ] = None,
    serviceName: Annotated[
        str | None,
        Field(default=None, description="Filter by service name. Supports partial matching (prefix search). Optional."),
    ] = None,
    label: Annotated[
        str | None,
        Field(default=None, description="Filter by tunnel label/tag. Optional parameter for categorized filtering."),
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
    if tunnelName is not None:
        query_params["tunnelName"] = tunnelName
    if serviceName is not None:
        query_params["serviceName"] = serviceName
    if label is not None:
        query_params["label"] = label
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/availability/tunnel",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_boost",
    description="GET /stats/timeseries/boost\n\ngetBoostTimeSeriesStats\n\nGet WAN Optimization (Boost) time series statistics for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_boost(
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
            description="Unix epoch timestamp (seconds) for the start of the data range. Must be ≥0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) for the end of the data range. Must be ≥0 and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation interval. Determines which stats table to query (minute, hourly, or daily)."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of records to return. If not provided or exceeds 10000, defaults to 10000.",
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
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/boost",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_dscp",
    description="GET /stats/timeseries/dscp\n\ngetDscpTimeSeriesStats\n\nGet DSCP time series statistics filtered by query parameters",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_dscp(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp in seconds since EPOCH indicating the start of the data time range. Must be less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp in seconds since EPOCH indicating the end of the data time range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Data aggregation interval determining the resolution of time series data points.")
    ],
    trafficType: Annotated[
        str, Field(description="Traffic category filter to specify which type of traffic statistics to retrieve.")
    ],
    dscp: Annotated[
        int,
        Field(
            description="DSCP value to filter statistics. Valid range: 0-63. DSCP is used for QoS classification in IP packets."
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
            description="Internal group identifier to retrieve stats for all appliances within that group. Used when nePk is not provided.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None, description="Maximum number of stats records to retrieve. Default and maximum value is 10000."
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Output format for the response. When set to 'CSV', returns data as downloadable CSV file.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups stats by IP address instead of internal appliance ID. Default is false.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve stats for the last N minutes from current time. Overrides startTime and endTime when provided.",
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
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if dscp is not None:
        query_params["dscp"] = dscp
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if latest is not None:
        query_params["latest"] = latest
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/dscp",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_flow",
    description="GET /stats/timeseries/flow\n\ngetFlowTimeSeriesStats\n\nGet flow time series statistics filtered by traffic type, flow type, and time range",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_flow(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since EPOCH) for the start of the time range. Required unless 'latest' is specified."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since EPOCH) for the end of the time range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Data aggregation interval. Determines the time bucket size for statistics.")
    ],
    trafficType: Annotated[
        str,
        Field(
            description="Filter by traffic optimization category. Maps to internal values: OPTIMIZED_TRAFFIC=1, PASS_THROUGH_SHAPED=2, PASS_THROUGH_UNSHAPED=3, ALL_TRAFFIC=4."
        ),
    ],
    flowType: Annotated[
        str,
        Field(description="Filter by TCP acceleration status. TCP_ACCELERATED=1, TCP_NOT_ACCELERATED=2, NON_TCP=3."),
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
            description="Internal group ID to retrieve stats for all appliances in a group. Used when nePk is not provided.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of statistics records to return. Default and maximum are both 10000.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Output format. Use 'csv' for CSV download with Excel-compatible format."),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups stats by IP address instead of internal appliance ID. Default is false.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve stats for the last N minutes. Overrides startTime and endTime when provided.",
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
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if flowType is not None:
        query_params["flowType"] = flowType
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if latest is not None:
        query_params["latest"] = latest
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/flow",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_flow_all",
    description="GET /stats/timeseries/flow/all\n\ngetTimeSeriesStatsAllFlows\n\nGet flow time series statistics for all flow types from a single appliance.",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_flow_all(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    granularity: Annotated[str, Field(description="Data aggregation interval. Determines time bucket size for stats.")],
    startTime: Annotated[
        int,
        Field(description="Start of time range as Unix timestamp (seconds since epoch). Must be less than endTime."),
    ],
    endTime: Annotated[
        int,
        Field(description="End of time range as Unix timestamp (seconds since epoch). Must be greater than startTime."),
    ],
    trafficType: Annotated[
        str,
        Field(
            description="Traffic classification type to filter. Maps to internal traffic type number (1=Optimized, 2=Pass-through Shaped, 3=Pass-through Unshaped, 4=All Traffic)."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(
            default=None, description="Maximum number of records to return. Optional parameter to limit response size."
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if granularity is not None:
        query_params["granularity"] = granularity
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if limit is not None:
        query_params["limit"] = limit
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/flow/all",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_interface",
    description="GET /stats/timeseries/interface\n\ngetInterfaceTimeSeriesStats\n\nGet interface time series statistics for a single appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_interface(
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
            description="Start of the time range in Unix epoch seconds (signed 64-bit integer). Must be less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range in Unix epoch seconds (signed 64-bit integer). Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Data aggregation interval. Determines the time resolution of returned statistics.")
    ],
    trafficType: Annotated[
        str,
        Field(description="Traffic category to filter statistics. Determines which type of traffic data is returned."),
    ],
    interfaceName: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter results to a specific interface by name. If omitted, returns stats for all interfaces.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of records to return. If not provided or exceeds 10000, defaults to 10000.",
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
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if interfaceName is not None:
        query_params["interfaceName"] = interfaceName
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/interface",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_interface_overlay",
    description="GET /stats/timeseries/interfaceOverlay\n\ngetInterfaceOverlayTimeSeriesStats\n\nGet interface overlay transport time series statistics for a single appliance.",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_interface_overlay(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    startTime: Annotated[
        int, Field(description="Start time boundary in seconds since EPOCH. Must be less than endTime.")
    ],
    endTime: Annotated[
        int, Field(description="End time boundary in seconds since EPOCH. Must be greater than startTime.")
    ],
    granularity: Annotated[
        str, Field(description="Data granularity level. Determines time interval aggregation for statistics.")
    ],
    overlay: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by overlay ID. Use '0' for physical tunnels only, 'all' or omit for all tunnels, or specific ID for bonded tunnels.",
        ),
    ] = None,
    tunnelType: Annotated[
        int | None,
        Field(
            default=None,
            description="Tunnel type filter. Overlay types: 0=SD-WAN, 2=Breakout, 3=Services. Underlay types: 1=Underlay, 2=Pass-through, 3=Services.",
        ),
    ] = None,
    labelId: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by label internal ID. Used to retrieve stats for a specific interface label.",
        ),
    ] = None,
    isWanSide: Annotated[
        bool | None,
        Field(
            default=None,
            description="Filter by WAN side (true) or LAN side (false) data. Defaults to false if not specified.",
        ),
    ] = None,
    interfaceName: Annotated[
        str | None, Field(default=None, description="Filter by specific interface name (e.g., 'wan0', 'lan0').")
    ] = None,
    limit: Annotated[
        int | None,
        Field(default=None, description="Maximum number of records to return. Default and maximum are both 10000."),
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
    if overlay is not None:
        query_params["overlay"] = overlay
    if tunnelType is not None:
        query_params["tunnelType"] = tunnelType
    if labelId is not None:
        query_params["labelId"] = labelId
    if isWanSide is not None:
        query_params["isWanSide"] = isWanSide
    if interfaceName is not None:
        query_params["interfaceName"] = interfaceName
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/interfaceOverlay",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_internal_drops",
    description="GET /stats/timeseries/internalDrops\n\ngetInternalDropsTimeSeriesStats\n\nGet internal drops time series statistics for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_internal_drops(
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
            description="Start of the time range in seconds since UNIX epoch (January 1, 1970 UTC). Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range in seconds since UNIX epoch. Must be non-negative and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval granularity for data aggregation. Determines whether stats are returned at minute, hour, or day intervals."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of records to return. If not specified or exceeds maximum, defaults to 10000.",
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
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/internalDrops",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_internet_breakout",
    description="GET /stats/timeseries/internetBreakout\n\ngetBreakoutInternetTimeSeriesStats\n\nGet internet breakout time series statistics for an appliance.",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_internet_breakout(
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
            description="Start of the time range in Unix epoch seconds (signed 64-bit). Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range in Unix epoch seconds (signed 64-bit). Must be non-negative and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time aggregation granularity for the statistics data. Determines the data resolution returned."
        ),
    ],
    overlayName: Annotated[
        str | None,
        Field(
            default=None,
            description="Name of the overlay network to filter results. When omitted, returns data for all overlays.",
        ),
    ] = None,
    ifName: Annotated[
        str | None,
        Field(
            default=None,
            description="Network interface name to filter results. When omitted, returns data for all interfaces.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of data rows to return. Useful for limiting response size when querying large time ranges.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format type. Set to 'csv' to download data as CSV file, otherwise returns JSON.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if overlayName is not None:
        query_params["overlayName"] = overlayName
    if ifName is not None:
        query_params["ifName"] = ifName
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/internetBreakout",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_ipsla",
    description="GET /stats/timeseries/ipsla\n\ngetIpSlaTimeSeriesStats\n\nGet IPSLA time series statistics for network performance monitoring.",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_ipsla(
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
            description="Start of the time range as Unix epoch timestamp in seconds. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range as Unix epoch timestamp in seconds. Must be non-negative and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation interval determining the resolution of returned statistics. Case-insensitive."
        ),
    ],
    configKey: Annotated[
        str | None,
        Field(
            default=None,
            description="Configuration key identifying the IPSLA monitor. Format: 'type=$monitorType;tunnel-name=$tunnelName;src-port-label=$portLabel'.",
        ),
    ] = None,
    target: Annotated[
        str | None,
        Field(
            default=None,
            description="Target URL or IP address specified in the IPSLA monitor configuration. Leading/trailing whitespace is automatically trimmed.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of statistics records to return. Default and maximum value is 10000.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format type. When set to 'csv', returns data as CSV file download. Default is JSON.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if configKey is not None:
        query_params["configKey"] = configKey
    if target is not None:
        query_params["target"] = target
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/ipsla",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_jitter",
    description="GET /stats/timeseries/jitter\n\ngetJitterTimeSeriesStats\n\nRetrieve time series jitter statistics for a tunnel",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_jitter(
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
            description="Start of time range as Unix timestamp (seconds since EPOCH). Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(description="End of time range as Unix timestamp (seconds since EPOCH). Must be greater than startTime."),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval granularity for data aggregation. Determines whether data points represent minute, hour, or day intervals."
        ),
    ],
    tunnelAlias: Annotated[
        str,
        Field(
            description="Tunnel display name/alias (e.g., 'to_datacenter_DefaultOverlay'). Maps to tunnelname in database. Required when tunnel is not provided."
        ),
    ],
    tunnel: Annotated[
        str | None,
        Field(
            default=None,
            description="Tunnel internal ID (e.g., 'bondedTunnel_33'). Maps to tunnelid in database. Deprecated: use tunnelAlias instead.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. If 'csv', returns data as downloadable CSV file instead of JSON.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(default=None, description="Maximum number of data points to return. Default and maximum is 10000."),
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
    if tunnel is not None:
        query_params["tunnel"] = tunnel
    if tunnelAlias is not None:
        query_params["tunnelAlias"] = tunnelAlias
    if format is not None:
        query_params["format"] = format
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/jitter",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_metrics",
    description="GET /stats/timeseries/metrics\n\ngetMetricsStats\n\nGet Orchestrator server metrics (memory, heap, appliance count) in time range",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_metrics(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of the time range as Unix epoch timestamp in seconds. Must be >= 0 and less than endTime. Internally converted to milliseconds for database queries."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range as Unix epoch timestamp in seconds. Must be >= 0 and greater than startTime. Internally converted to milliseconds for database queries."
        ),
    ],
    key: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional filter key for metrics. Reserved for future use; currently not utilized in filtering.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if key is not None:
        query_params["key"] = key
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/metrics",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_mos",
    description="GET /stats/timeseries/mos\n\ngetMosTimeSeriesStats\n\nGet MOS time series statistics for tunnel quality monitoring",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_mos(
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
            description="Unix epoch time in seconds for the start of the time range. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix epoch time in seconds for the end of the time range. Must be >= 0 and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Data aggregation interval determining which statistics table to query from.")
    ],
    tunnel: Annotated[
        str,
        Field(
            description="Tunnel identifier (e.g., 'bondedTunnel_33'). Maps to tunnelid in database. Deprecated: use tunnelAlias instead."
        ),
    ],
    tunnelAlias: Annotated[
        str | None,
        Field(
            default=None,
            description="Tunnel alias name (e.g., 'to_xxx-ecva_DefaultOverlay'). Maps to tunnelname in database. Preferred over tunnel parameter.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(default=None, description="Maximum number of records to return. Default and maximum value is 10000."),
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
    if tunnel is not None:
        query_params["tunnel"] = tunnel
    if tunnelAlias is not None:
        query_params["tunnelAlias"] = tunnelAlias
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/mos",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_power_supply_stats",
    description="GET /stats/timeseries/powerSupplyStats\n\ngetPowerSupplyTimeSeriesStatsSingleAppliance\n\nGet power supply time series statistics for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_power_supply_stats(
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
            description="Unix timestamp (seconds since epoch) for the start of the time range. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since epoch) for the end of the time range. Must be >= 0 and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Data aggregation granularity. Determines how data points are grouped over time.")
    ],
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of stats records to retrieve. Optional parameter for limiting results.",
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
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/powerSupplyStats",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_security_policy",
    description="GET /stats/timeseries/securityPolicy\n\ngetSecurityPolicyTimeSeriesStats\n\nGet security policy time series statistics for an appliance filtered by zone pair and time range.",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_security_policy(
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
            description="Start of time range as Unix epoch timestamp in seconds. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of time range as Unix epoch timestamp in seconds. Must be non-negative and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation interval. Determines time bucket size for statistics. Case-insensitive input converted to uppercase."
        ),
    ],
    fromZone: Annotated[
        str, Field(description="Source zone identifier for filtering traffic. Specifies the originating security zone.")
    ],
    toZone: Annotated[
        str, Field(description="Destination zone identifier for filtering traffic. Specifies the target security zone.")
    ],
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
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/securityPolicy",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_shaper",
    description="GET /stats/timeseries/shaper\n\ngetShaperTimeSeriesStats\n\nRetrieve shaper time series statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_shaper(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Start of time range in Unix epoch seconds (must be >= 0 and < endTime).")
    ],
    endTime: Annotated[int, Field(description="End of time range in Unix epoch seconds (must be > startTime).")],
    granularity: Annotated[
        str,
        Field(
            description="Time interval granularity for data aggregation. Determines whether stats are grouped by minute, hour, or day."
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
            description="Internal group ID for filtering stats. Used when nePk is not provided to retrieve stats for all appliances in the group.",
        ),
    ] = None,
    trafficClass: Annotated[
        int | None,
        Field(
            default=None,
            description="QoS traffic class to filter (1-10). Class 1 is highest priority, class 10 is lowest.",
        ),
    ] = None,
    direction: Annotated[
        int | None,
        Field(
            default=None, description="Traffic direction filter: 0 for outbound (WAN-bound), 1 for inbound (LAN-bound)."
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups stats by appliance IP address instead of internal appliance ID. Default is false.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Response format. Use 'csv' to download as CSV file. Omit for JSON response."),
    ] = None,
    limit: Annotated[
        int | None,
        Field(default=None, description="Maximum number of data points to return. Default and maximum is 10000."),
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
    if direction is not None:
        query_params["direction"] = direction
    if ip is not None:
        query_params["ip"] = ip
    if format is not None:
        query_params["format"] = format
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/shaper",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_traffic_behavioral",
    description="GET /stats/timeseries/trafficBehavioral\n\ngetTrafficBehavioralTimeseriesStats\n\nGet Traffic Behavioral Timeseries Statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_traffic_behavioral(
    ctx: Context,
    application: Annotated[
        str,
        Field(
            description="Application name to filter statistics. Must be a valid application name configured in the system."
        ),
    ],
    startTime: Annotated[
        int | None,
        Field(
            default=None,
            description="Start of the time range as Unix epoch timestamp in seconds. Required unless 'latest' parameter is provided. Must be less than endTime and greater than or equal to 0.",
        ),
    ] = None,
    endTime: Annotated[
        int | None,
        Field(
            default=None,
            description="End of the time range as Unix epoch timestamp in seconds. Required unless 'latest' parameter is provided. Must be greater than startTime and greater than or equal to 0.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve stats for the latest N minutes. When provided, overrides startTime and endTime parameters. Calculates time range as (current_time - latest*60) to current_time.",
        ),
    ] = None,
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
            description="Internal group ID to filter statistics by appliance group. Used when nePk is not provided. Returns aggregated stats for all appliances in the specified group.",
        ),
    ] = None,
    behavior: Annotated[
        str | None,
        Field(
            default=None,
            description="Behavioral category filter to retrieve stats for a specific traffic behavior classification.",
        ),
    ] = None,
    total: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns aggregated totals across the time range instead of individual time-series data points.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of statistics records to return. Default and maximum value is 10000.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Output format for the response. Use 'csv' to export data as a CSV file download instead of JSON.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if application is not None:
        query_params["application"] = application
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if latest is not None:
        query_params["latest"] = latest
    if nePk is not None:
        query_params["nePk"] = nePk
    if groupPk is not None:
        query_params["groupPk"] = groupPk
    if behavior is not None:
        query_params["behavior"] = behavior
    if total is not None:
        query_params["total"] = total
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/trafficBehavioral",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_traffic_class",
    description="GET /stats/timeseries/trafficClass\n\ngetTrafficClassTimeSeriesStats\n\nGet traffic class time series statistics for single appliance or group",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_traffic_class(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since EPOCH) for the start of the time range. Required unless 'latest' is specified."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since EPOCH) for the end of the time range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval granularity for data aggregation. Determines the resolution of returned data points."
        ),
    ],
    trafficType: Annotated[
        str, Field(description="Traffic type filter to select specific traffic category for statistics.")
    ],
    trafficClass: Annotated[
        int,
        Field(
            description="Traffic class identifier (QoS priority level). Values 1-10 represent different priority levels."
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
            description="Internal group identifier to retrieve stats for all appliances in a group. Use when nePk is not provided.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None, description="Maximum number of stats records to retrieve. Default and maximum value is 10000."
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. When set to 'CSV', returns downloadable CSV file instead of JSON.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups stats by appliance IP address instead of internal nePk identifier. Default is false.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve stats for the latest N minutes. Overrides startTime and endTime when provided.",
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
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if trafficClass is not None:
        query_params["trafficClass"] = trafficClass
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if latest is not None:
        query_params["latest"] = latest
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/trafficClass",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_tunnel",
    description="GET /stats/timeseries/tunnel\n\ngetTunnelTimeSeriesStatsSingleAppliance\n\nGet tunnel time series stats for a single appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_tunnel(
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
            description="Start of the time range as Unix epoch timestamp in seconds. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range as Unix epoch timestamp in seconds. Must be non-negative and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation interval determining time resolution. 'minute' for minutely data, 'hour' for hourly aggregates, 'day' for daily aggregates."
        ),
    ],
    tunnelName: Annotated[
        str,
        Field(
            description="Internal tunnel identifier (maps to tunnelId in database). Example: 'bondedTunnel_5'. This parameter is being deprecated; use tunnelAlias instead when possible."
        ),
    ],
    tunnelAlias: Annotated[
        str | None,
        Field(
            default=None,
            description="Human-readable tunnel name/alias (maps to tunnelName in database). Example: 'to_ecva_DefaultOverlay'. Preferred over tunnelName parameter.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(default=None, description="Maximum number of data points to return. Default and maximum value is 10000."),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. When set to 'CSV', returns data as a downloadable CSV file instead of JSON.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, uses IP address as the grouping key instead of internal appliance ID. Default is false.",
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
    if tunnelName is not None:
        query_params["tunnelName"] = tunnelName
    if tunnelAlias is not None:
        query_params["tunnelAlias"] = tunnelAlias
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/tunnel",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_stats3_timeseries_appliance",
    description="POST /stats3/timeseries/appliance\n\ngetApplianceTimeSeriesStatsByPost\n\nGet appliance time series statistics for multiple appliances (batch query)",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats3_timeseries_appliance(
    ctx: Context,
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation interval determining time resolution. Use 'minute' for real-time monitoring, 'hour' for daily trends, 'day' for long-term analysis."
        ),
    ],
    trafficType: Annotated[
        str,
        Field(
            description="Traffic category filter. optimized_traffic (1): WAN optimized traffic. pass_through_shaped (2): Shaped but not optimized. pass_through_unshaped (3): Unshaped passthrough. all_traffic (4): Combined total."
        ),
    ],
    startTime: Annotated[
        int | None,
        Field(
            default=None,
            description="Unix epoch timestamp (seconds) for data range start. Ignored when 'latest' is provided. Value is rounded down to the nearest minute boundary.",
        ),
    ] = None,
    endTime: Annotated[
        int | None,
        Field(
            default=None,
            description="Unix epoch timestamp (seconds) for data range end. Must be greater than startTime. Ignored when 'latest' is provided. Value is rounded up to the next minute boundary.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum records to return per appliance. If omitted or exceeds 10000, defaults to 10000.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. When 'CSV', returns downloadable CSV file with filename 'ApplianceTimeSeriesStats.csv'.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="Use appliance IP address instead of nePk as key in response data object. Defaults to false if not provided.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve last N minutes of data. When provided, calculates endTime as current time and startTime as (current - latest*60). Overrides startTime/endTime parameters.",
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
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if latest is not None:
        query_params["latest"] = latest
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats3/timeseries/appliance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats3_timeseries_dscp",
    description="POST /stats3/timeseries/dscp\n\ngetDscpTimeSeriesStatsByPost\n\nRetrieve DSCP time series bandwidth statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats3_timeseries_dscp(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since EPOCH) for query start. Automatically rounded down to nearest minute. Required unless 'latest' is provided."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since EPOCH) for query end. Automatically rounded up to nearest minute. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Time interval for data aggregation. Case-insensitive (e.g., 'hour' or 'HOUR').")
    ],
    trafficType: Annotated[
        str,
        Field(description="Traffic category filter. Case-insensitive. Maps to internal traffic type numbers (1-4)."),
    ],
    dscp: Annotated[
        int, Field(description="DSCP (Differentiated Services Code Point) value for QoS filtering. Valid range: 0-63.")
    ],
    limit: Annotated[
        int | None,
        Field(
            default=None, description="Maximum data points per appliance. Values exceeding 10000 are capped to 10000."
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None, description="Output format. Set to 'CSV' for file download with Content-Disposition header."
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(default=None, description="Use appliance IP address as response key instead of nePk identifier."),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve stats for last N minutes from current time. When provided, overrides startTime/endTime.",
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
    if dscp is not None:
        query_params["dscp"] = dscp
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if latest is not None:
        query_params["latest"] = latest
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats3/timeseries/dscp",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_addos_max_timestamp",
    description="POST /stats/timeseries/addos/maxTimestamp\n\ngetADdosBaseLineMaxTimestamp\n\nGet ADDoS baseline maximum timestamp for an appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_addos_max_timestamp(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/addos/maxTimestamp",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_addos_segment_flow_utilization",
    description="POST /stats/timeseries/addos/segmentFlowUtilization\n\ngetADdosSegmentFlowUtilization\n\nGet ADDoS segment flow utilization statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_addos_segment_flow_utilization(
    ctx: Context,
    timestamp: Annotated[
        int,
        Field(
            description="UNIX epoch timestamp in milliseconds indicating the starting time boundary for data retrieval. Must be a valid positive integer."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if timestamp is not None:
        query_params["timestamp"] = timestamp
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/addos/segmentFlowUtilization",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_addos_segment_zone_flow_utilization",
    description="POST /stats/timeseries/addos/segmentZoneFlowUtilization\n\ngetADdosSegmentZoneFlowUtilization\n\nGet ADDoS baseline segment zone flow utilization timeseries statistics for a specific appliance and timestamp.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_addos_segment_zone_flow_utilization(
    ctx: Context,
    timestamp: Annotated[
        int,
        Field(
            description="EPOCH timestamp (signed 64-bit) in seconds indicating the time boundary for data retrieval. Use the value from /stats/timeseries/addos/maxTimestamp API to get the latest available timestamp."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if timestamp is not None:
        query_params["timestamp"] = timestamp
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/addos/segmentZoneFlowUtilization",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_addos_segment_zone_protocol",
    description="POST /stats/timeseries/addos/segmentZoneProtocol\n\ngetADdosSegmentZoneProtocol\n\nRetrieve ADDoS baseline segment zone protocol statistics by appliance, timestamp, metric type, and classification.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_addos_segment_zone_protocol(
    ctx: Context,
    timestamp: Annotated[
        int,
        Field(
            description="EPOCH timestamp (signed 64-bit) specifying the point-in-time for baseline data retrieval. Must be a valid positive EPOCH timestamp in seconds."
        ),
    ],
    metric: Annotated[
        int,
        Field(
            description="Flow metric type to filter baseline statistics. Determines which flow measurement category is returned."
        ),
    ],
    classification: Annotated[
        int,
        Field(
            description="Classification type for grouping baseline data. Specifies whether to group by zone or source."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if timestamp is not None:
        query_params["timestamp"] = timestamp
    if metric is not None:
        query_params["metric"] = metric
    if classification is not None:
        query_params["classification"] = classification
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/addos/segmentZoneProtocol",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_addos_segment_zone_view",
    description="POST /stats/timeseries/addos/segmentZoneView\n\ngetADdosSegmentZoneView\n\nGet ADDoS baseline segment zone view statistics.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_addos_segment_zone_view(
    ctx: Context,
    timestamp: Annotated[
        int,
        Field(
            description="UNIX epoch timestamp (seconds) for the baseline data snapshot. Use the /stats/timeseries/addos/maxTimestamp endpoint to get the latest available timestamp."
        ),
    ],
    zoneId: Annotated[
        int | None,
        Field(
            default=None,
            description="Zone identifier for filtering results. If not provided or set to -1, returns data for all zones.",
        ),
    ] = None,
    segmentId: Annotated[
        int | None,
        Field(
            default=None,
            description="Segment identifier for filtering results. If not provided or set to -1, returns data for all segments.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if timestamp is not None:
        query_params["timestamp"] = timestamp
    if zoneId is not None:
        query_params["zoneId"] = zoneId
    if segmentId is not None:
        query_params["segmentId"] = segmentId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/addos/segmentZoneView",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_addos_total_flow_utilization",
    description="POST /stats/timeseries/addos/totalFlowUtilization\n\ngetADdosBaseLineFlowUtilization\n\nGet ADDoS baseline total flow utilization for a specific appliance and timestamp.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_addos_total_flow_utilization(
    ctx: Context,
    timestamp: Annotated[
        int,
        Field(
            description="EPOCH timestamp (seconds) indicating the time boundary for querying baseline data. Must be a valid timestamp from available hourly baseline records."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if timestamp is not None:
        query_params["timestamp"] = timestamp
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/addos/totalFlowUtilization",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_addos_trends_baseline_all_zone",
    description="POST /stats/timeseries/addos/trends/baselineAllZone\n\ngetAddosTrendsBaselineAllZone\n\nGet ADDoS trends baseline timeseries data across all zones for an appliance.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_addos_trends_baseline_all_zone(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary as Unix epoch timestamp in seconds. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary as Unix epoch timestamp in seconds. Must be >= 0 and greater than startTime."
        ),
    ],
    protocol: Annotated[int, Field(description="Network protocol filter for ADDoS statistics.")],
    metric: Annotated[int, Field(description="Flow metric type for ADDoS baseline measurement.")],
    classification: Annotated[int, Field(description="Classification type for grouping ADDoS baseline data.")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if protocol is not None:
        query_params["protocol"] = protocol
    if metric is not None:
        query_params["metric"] = metric
    if classification is not None:
        query_params["classification"] = classification
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/addos/trends/baselineAllZone",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_addos_trends_baseline_segment",
    description="POST /stats/timeseries/addos/trends/baselineSegment\n\ngetAddosTrendsBaselineSegment\n\nRetrieve ADDoS Trends Baseline Segment timeseries statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_addos_trends_baseline_segment(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary for data retrieval as Unix epoch timestamp in milliseconds. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary for data retrieval as Unix epoch timestamp in milliseconds. Must be >= 0 and greater than startTime."
        ),
    ],
    segmentId: Annotated[
        int,
        Field(
            description="Unique identifier of the network segment to filter statistics. Used to scope baseline data to a specific segment."
        ),
    ],
    protocol: Annotated[
        int,
        Field(
            description="Protocol filter for traffic analysis. Valid values: 0 (All protocols), 1 (TCP), 2 (UDP), 4 (Others)."
        ),
    ],
    metric: Annotated[
        int,
        Field(
            description="Flow metric type for baseline measurement. Valid values: 0 (Concurrent flows), 1 (Embryonic flows), 2 (Flows per second), 3 (Embryonic Two-Way flows)."
        ),
    ],
    classification: Annotated[
        int,
        Field(
            description="Classification type for grouping statistics. Valid values: 1 (Zone-based classification), 2 (Source-based classification)."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if segmentId is not None:
        query_params["segmentId"] = segmentId
    if protocol is not None:
        query_params["protocol"] = protocol
    if metric is not None:
        query_params["metric"] = metric
    if classification is not None:
        query_params["classification"] = classification
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/addos/trends/baselineSegment",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_addos_trends_baseline_segment_zone",
    description="POST /stats/timeseries/addos/trends/baselineSegmentZone\n\ngetAddosTrendsBaselineSegmentZone\n\nGet ADDoS trends baseline statistics by segment and zone",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_addos_trends_baseline_segment_zone(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary in Unix epoch seconds (64-bit signed integer). Must be less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary in Unix epoch seconds (64-bit signed integer). Must be greater than startTime."
        ),
    ],
    segmentId: Annotated[
        int, Field(description="Network segment identifier to filter baseline data. Validated to ensure it exists.")
    ],
    zoneId: Annotated[
        int, Field(description="Security zone identifier to filter baseline data. Validated to ensure it exists.")
    ],
    metric: Annotated[
        int,
        Field(
            description="Flow metric type for baseline calculation. Values: 0=Concurrent flows, 1=Embryonic flows, 2=Flows per second, 3=Embryonic Two-Way flows."
        ),
    ],
    classification: Annotated[
        int,
        Field(
            description="Classification type for baseline grouping. Values: 1=Zone-based classification, 2=Source-based classification."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if segmentId is not None:
        query_params["segmentId"] = segmentId
    if zoneId is not None:
        query_params["zoneId"] = zoneId
    if metric is not None:
        query_params["metric"] = metric
    if classification is not None:
        query_params["classification"] = classification
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/addos/trends/baselineSegmentZone",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_addos_trends_baseline_zone",
    description="POST /stats/timeseries/addos/trends/baselineZone\n\ngetAddosTrendsBaselineZone\n\nRetrieve ADDoS Trends Baseline Zone timeseries statistics.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_addos_trends_baseline_zone(
    ctx: Context,
    startTime: Annotated[int, Field(description="Start time boundary for the data range. Must be less than endTime.")],
    endTime: Annotated[int, Field(description="End time boundary for the data range. Must be greater than startTime.")],
    zoneId: Annotated[
        int, Field(description="Zone identifier to filter baseline statistics. Required for zone-level filtering.")
    ],
    protocol: Annotated[int, Field(description="Network protocol filter for baseline data.")],
    metric: Annotated[int, Field(description="Flow metric type to retrieve for baseline analysis.")],
    classification: Annotated[int, Field(description="Classification type for grouping baseline data.")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if zoneId is not None:
        query_params["zoneId"] = zoneId
    if protocol is not None:
        query_params["protocol"] = protocol
    if metric is not None:
        query_params["metric"] = metric
    if classification is not None:
        query_params["classification"] = classification
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/addos/trends/baselineZone",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_apdex",
    description="POST /stats/timeseries/apdex\n\ngetBestApdexTimeSeriesStats\n\nGet APDEX timeseries statistics for appliances and applications.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_apdex(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of time range as EPOCH timestamp in milliseconds (signed 64-bit). Must be less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of time range as EPOCH timestamp in milliseconds (signed 64-bit). Must be greater than startTime."
        ),
    ],
    includeProbes: Annotated[
        bool,
        Field(
            description="When true, returns stats for all probes/paths. When false, returns only best path stats (filtered by current_best_path=true)."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of result rows to return. Used for pagination or limiting large datasets.",
        ),
    ] = None,
    format: Annotated[
        str | None, Field(default=None, description="Response format option (reserved for future use).")
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if includeProbes is not None:
        query_params["includeProbes"] = includeProbes
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/apdex",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_appliance",
    description="POST /stats/timeseries/appliance\n\ngetApplianceTimeSeriesStatsByPost\n\nGet time series statistics for multiple appliances (batch)",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_appliance(
    ctx: Context,
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for data aggregation. Determines resolution of returned data points: minute (1-min intervals), hour (hourly), day (daily)."
        ),
    ],
    trafficType: Annotated[
        str,
        Field(
            description="Traffic category filter. OPTIMIZED_TRAFFIC(1)=WAN optimized, PASS_THROUGH_SHAPED(2)=shaped but not optimized, PASS_THROUGH_UNSHAPED(3)=neither, ALL_TRAFFIC(4)=combined."
        ),
    ],
    startTime: Annotated[
        int | None,
        Field(
            default=None,
            description="Unix timestamp (seconds since epoch) for the start of the time range. Required unless 'latest' is provided. Must be >= 0 and < endTime.",
        ),
    ] = None,
    endTime: Annotated[
        int | None,
        Field(
            default=None,
            description="Unix timestamp (seconds since epoch) for the end of the time range. Required unless 'latest' is provided. Must be > startTime.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None, description="Maximum records to return per appliance. Limits result set size for performance."
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Output format. Set to 'CSV' for downloadable CSV file (Content-Type: application/vnd.ms-excel). Omit or use any other value for JSON.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, response keys use appliance IP address instead of nePk. Default is false (uses nePk).",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve stats for most recent N minutes. When provided, overrides startTime/endTime: endTime=now, startTime=now-(latest*60).",
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
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if latest is not None:
        query_params["latest"] = latest
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/appliance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_application2",
    description="POST /stats/timeseries/application2\n\ngetApplicationTimeSeriesStatsByPost\n\nGet application time series statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_application2(
    ctx: Context,
    application: Annotated[
        str,
        Field(
            description="Application name to filter statistics. Required, cannot be empty. Examples: HTTP, DNS, SSL, SMTP."
        ),
    ],
    startTime: Annotated[
        int | None,
        Field(
            default=None,
            description="Start time in Unix epoch seconds. Required unless 'latest' is provided. Must be >= 0 and < endTime.",
        ),
    ] = None,
    endTime: Annotated[
        int | None,
        Field(
            default=None,
            description="End time in Unix epoch seconds. Required unless 'latest' is provided. Must be >= 0 and > startTime.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Get stats for last N minutes. When provided, auto-calculates startTime=(now - N*60) and endTime=now, ignoring explicit time params.",
        ),
    ] = None,
    total: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, aggregates stats across all appliances. When false (default), returns per-appliance breakdown.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. Set to 'CSV' for downloadable CSV file (application/vnd.ms-excel). Default: JSON.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None, description="Maximum number of data points to return. Useful for limiting large result sets."
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if application is not None:
        query_params["application"] = application
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if latest is not None:
        query_params["latest"] = latest
    if total is not None:
        query_params["total"] = total
    if format is not None:
        query_params["format"] = format
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/application2",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_application_performance",
    description="POST /stats/timeseries/applicationPerformance\n\ngetApplicationPerformanceTimeSeriesStats\n\nGet application performance time series statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_application_performance(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) for the start of the query time range. Must be less than endTime and greater than or equal to 0."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) for the end of the query time range. Must be greater than startTime and greater than or equal to 0."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation granularity. Determines the time interval for data points. 'minute' returns raw minute-level data, 'hour' and 'day' return aggregated data."
        ),
    ],
    tunnelName: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional tunnel name filter. When provided, returns stats only for the specified tunnel.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of records to return. When not specified, returns all matching records. Results are ordered by timestamp descending.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Response format. Currently only JSON is supported for this endpoint."),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if tunnelName is not None:
        query_params["tunnelName"] = tunnelName
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if granularity is not None:
        query_params["granularity"] = granularity
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/applicationPerformance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_ddos_peak_and_peak_drop_rate",
    description="POST /stats/timeseries/ddosPeakAndPeakDropRate\n\ngetDdosPeakAndPeakDropRateTimeSeriesStats\n\nGet DDoS peak and peak drop rate timeseries statistics filtered by appliance, zone, metric, protocol, and time range.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_ddos_peak_and_peak_drop_rate(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary for data range as UNIX epoch timestamp in milliseconds (signed 64-bit). Must be less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary for data range as UNIX epoch timestamp in milliseconds (signed 64-bit). Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for data aggregation. Determines whether data points are aggregated per minute, hour, or day."
        ),
    ],
    zoneId: Annotated[
        int, Field(description="DDoS protection zone identifier. Filters statistics for the specified zone.")
    ],
    metric: Annotated[
        int,
        Field(
            description="DDoS metric type to retrieve. 0=Concurrent flows, 1=Embryonic flows, 2=Flows per second, 3=Embryonic two-way flows."
        ),
    ],
    protocol: Annotated[int, Field(description="Network protocol filter. 0=All protocols, 1=TCP, 2=UDP, 4=Others.")],
    statIds: Annotated[
        str,
        Field(
            description="Statistics identifier(s) for filtering. Comma-separated values (e.g., '1' or '1,2'). 1=Peak, 2=Peak drop rate."
        ),
    ],
    classification: Annotated[
        int,
        Field(
            description="Classification filter for stats grouping. 1=Zone-based statistics, 2=Source-based statistics."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of records to return per statId. Limits the result set size for each statistics category.",
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
    if zoneId is not None:
        query_params["zoneId"] = zoneId
    if metric is not None:
        query_params["metric"] = metric
    if protocol is not None:
        query_params["protocol"] = protocol
    if statIds is not None:
        query_params["statIds"] = statIds
    if classification is not None:
        query_params["classification"] = classification
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/ddosPeakAndPeakDropRate",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_ddos_src_ip_sample10",
    description="POST /stats/timeseries/ddosSrcIpSample10\n\ngetDdosSrcIpSample10TimeSeriesStats\n\nGet DDoS source IP sample top 10 time-series statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_ddos_src_ip_sample10(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix epoch time in seconds indicating the start of the data time range. Must be less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix epoch time in seconds indicating the end of the data time range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data granularity determining which statistics table to query from. Affects data resolution and availability."
        ),
    ],
    zoneId: Annotated[int, Field(description="Zone identifier used to filter statistics by security zone.")],
    metric: Annotated[int, Field(description="Flow metric type for filtering DDoS statistics.")],
    statIds: Annotated[str, Field(description="Statistics identifier for data filtering. Valid values are 8 or 9.")],
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of rows to return. Default is 10000. For minute granularity with time ranges exceeding 43200 seconds (12 hours), the limit is automatically set to 43200.",
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
    if zoneId is not None:
        query_params["zoneId"] = zoneId
    if metric is not None:
        query_params["metric"] = metric
    if statIds is not None:
        query_params["statIds"] = statIds
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/ddosSrcIpSample10",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_ddos_top_talkers",
    description="POST /stats/timeseries/ddosTopTalkers\n\ngetDdosTopTalkersTimeSeriesStats\n\nGet DDoS Top Talkers timeseries statistics for an appliance.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_ddos_top_talkers(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary for the data query as Unix epoch timestamp in seconds. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary for the data query as Unix epoch timestamp in seconds. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval granularity for aggregating statistics. Determines whether data is grouped by minute, hour, day, or month."
        ),
    ],
    statIds: Annotated[
        str,
        Field(
            description="Comma-separated stat IDs to filter results. Flow Count IDs: 10, 11, 12, 15. Violation Count IDs: 13, 14."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of top talker records to return. When omitted, returns all matching records.",
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
    if statIds is not None:
        query_params["statIds"] = statIds
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/ddosTopTalkers",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_ddos_total_stats",
    description="POST /stats/timeseries/ddosTotalStats\n\ngetDdosTotalTimeSeriesStats\n\nRetrieve DDoS Total timeseries statistics filtered by zone, metric, protocol, and classification.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_ddos_total_stats(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (milliseconds) marking the start of the data range. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="EPOCH timestamp (milliseconds) marking the end of the data range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval for data aggregation. Determines whether data is grouped by minute, hour, or day."
        ),
    ],
    zoneId: Annotated[
        int,
        Field(description="DDoS zone identifier to filter statistics. Required parameter for zone-specific filtering."),
    ],
    metric: Annotated[
        int,
        Field(
            description="DDoS metric type to retrieve. 0=Concurrent flows, 1=Embryonic flows, 2=Flows per second, 3=Embryonic Two-Way flows."
        ),
    ],
    protocol: Annotated[int, Field(description="Network protocol filter. 0=All protocols, 1=TCP, 2=UDP, 4=Others.")],
    statIds: Annotated[
        str, Field(description="Comma-separated stat identifiers for filtering. Valid values: 3, 4, 5, 6, 7.")
    ],
    classification: Annotated[
        int,
        Field(
            description="Classification filter for data grouping. 1=Zone-based classification, 2=Source-based classification."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of data rows to return. Optional parameter for pagination. When omitted, returns all matching records.",
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
    if zoneId is not None:
        query_params["zoneId"] = zoneId
    if metric is not None:
        query_params["metric"] = metric
    if protocol is not None:
        query_params["protocol"] = protocol
    if statIds is not None:
        query_params["statIds"] = statIds
    if classification is not None:
        query_params["classification"] = classification
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/ddosTotalStats",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_dscp",
    description="POST /stats/timeseries/dscp\n\ngetDscpTimeSeriesStatsByPost\n\nRetrieve DSCP time series statistics for multiple appliances (batch query)",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_dscp(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since EPOCH) for query start. Required unless 'latest' is provided. Must be >= 0 and < endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix timestamp (seconds since EPOCH) for query end. Required unless 'latest' is provided. Must be >= 0 and > startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation interval for time series resolution. Maps to database table: minute, hourly, or daily."
        ),
    ],
    trafficType: Annotated[
        str,
        Field(
            description="Traffic category filter. Values map to internal codes: optimized_traffic=1, pass_through_shaped=2, pass_through_unshaped=3, all_traffic=4."
        ),
    ],
    dscp: Annotated[
        int,
        Field(
            description="DSCP (Differentiated Services Code Point) value for QoS filtering. Range: 0-63. Common values: 0=Best Effort, 46=EF (Expedited Forwarding)."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(default=None, description="Maximum records to return. Used for pagination or limiting response size."),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. Set to 'CSV' for downloadable Excel-compatible file with filename 'DscpTimeSeriesStats.csv'.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups results by appliance IP address instead of nePk identifier. Default: false.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve data for last N minutes from current time. When provided, overrides startTime and endTime (endTime=now, startTime=now-latest*60).",
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
    if dscp is not None:
        query_params["dscp"] = dscp
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if latest is not None:
        query_params["latest"] = latest
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/dscp",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_flow",
    description="POST /stats/timeseries/flow\n\ngetFlowTimeSeriesStatsByPost\n\nGet flow time series statistics for multiple appliances via POST request body",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_flow(
    ctx: Context,
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation interval determining time bucket size. Case-insensitive (converted to uppercase internally)."
        ),
    ],
    trafficType: Annotated[
        str,
        Field(
            description="Traffic optimization category filter. Case-insensitive. Maps to internal values: OPTIMIZED_TRAFFIC=1, PASS_THROUGH_SHAPED=2, PASS_THROUGH_UNSHAPED=3, ALL_TRAFFIC=4."
        ),
    ],
    flowType: Annotated[
        str,
        Field(
            description="TCP acceleration status filter. Case-insensitive. TCP_ACCELERATED=1, TCP_NOT_ACCELERATED=2, NON_TCP=3."
        ),
    ],
    startTime: Annotated[
        int | None,
        Field(
            default=None,
            description="Unix timestamp (seconds since EPOCH) for time range start. Required unless 'latest' is provided. Must be >= 0.",
        ),
    ] = None,
    endTime: Annotated[
        int | None,
        Field(
            default=None,
            description="Unix timestamp (seconds since EPOCH) for time range end. Must be greater than startTime and >= 0.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(default=None, description="Maximum statistics records to return. When null, no limit is applied."),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Output format. Use 'csv' (case-insensitive) for CSV download with Excel-compatible format. Filename: FlowTimeSeriesStats.csv.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, groups statistics by IP address instead of appliance ID. Default is false/null.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve stats for last N minutes from current time. When provided, automatically calculates: endTime=now, startTime=now-(latest*60). Overrides startTime/endTime parameters.",
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
    if flowType is not None:
        query_params["flowType"] = flowType
    if limit is not None:
        query_params["limit"] = limit
    if format is not None:
        query_params["format"] = format
    if ip is not None:
        query_params["ip"] = ip
    if latest is not None:
        query_params["latest"] = latest
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/flow",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_memory",
    description="POST /stats/timeseries/memory\n\ngetMemoryStatsByPost\n\nGet memory time-series statistics for specified appliances.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_memory(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of the time range in EPOCH seconds (Unix timestamp). Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range in EPOCH seconds (Unix timestamp). Must be non-negative and greater than startTime."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/memory",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_secure_web_services_allowed_denied_category",
    description="POST /stats/timeseries/secureWebServices/allowedDeniedCategory\n\ngetSecureWebServicesAllowedDeniedCategory\n\nGet time series statistics for allowed or denied web filtering categories.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_secure_web_services_allowed_denied_category(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) for the start of the data range. Must be a positive value less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) for the end of the data range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(description="Time interval granularity for data aggregation. Determines how data points are grouped."),
    ],
    allowed: Annotated[
        bool,
        Field(
            description="Filter by traffic disposition. Set to true for allowed categories, false for denied categories."
        ),
    ],
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of category results to return. Limits the top N categories by traffic volume.",
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
    if allowed is not None:
        query_params["allowed"] = allowed
    if top is not None:
        query_params["top"] = top
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/secureWebServices/allowedDeniedCategory",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_secure_web_services_allowed_denied_category_url",
    description="POST /stats/timeseries/secureWebServices/allowedDeniedCategoryUrl\n\ngetSecureWebServicesAllowedDeniedCategoryUrl\n\nRetrieve timeseries URL statistics for allowed or denied traffic within a web filtering category.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_secure_web_services_allowed_denied_category_url(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary for data retrieval as EPOCH timestamp in milliseconds. Must be a positive value and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary for data retrieval as EPOCH timestamp in milliseconds. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval granularity for data aggregation. Determines the resolution of timeseries data points."
        ),
    ],
    allowed: Annotated[
        bool,
        Field(
            description="Filter for traffic disposition. Set to true for allowed URLs, false for denied/blocked URLs."
        ),
    ],
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of URL results to return. Limits the response size for top talkers analysis.",
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
    if allowed is not None:
        query_params["allowed"] = allowed
    if top is not None:
        query_params["top"] = top
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/secureWebServices/allowedDeniedCategoryUrl",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_secure_web_services_allowed_denied_url",
    description="POST /stats/timeseries/secureWebServices/allowedDeniedUrl\n\ngetSecureWebServicesAllowedDeniedUrl\n\nGet timeseries allowed/denied URL statistics for Secure Web Services",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_secure_web_services_allowed_denied_url(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary for the data query as a Unix epoch timestamp in seconds. Must be non-negative and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary for the data query as a Unix epoch timestamp in seconds. Must be non-negative and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time granularity for data aggregation. Determines whether stats are grouped by hour or day."
        ),
    ],
    allowed: Annotated[
        bool,
        Field(description="Filter for URL access status. Set to true to retrieve allowed URLs, false for denied URLs."),
    ],
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of results to return. Defaults to 50 if not specified or if value exceeds 50.",
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
    if allowed is not None:
        query_params["allowed"] = allowed
    if top is not None:
        query_params["top"] = top
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/secureWebServices/allowedDeniedUrl",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_secure_web_services_allowed_denied_url_src_ip",
    description="POST /stats/timeseries/secureWebServices/allowedDeniedUrlSrcIp\n\ngetSecureWebServicesAllowedDeniedUrlSrcIP\n\nGet source IP statistics for allowed or denied URL access events.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_secure_web_services_allowed_denied_url_src_ip(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (in seconds) marking the start of the time range. Must be a positive integer less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (in seconds) marking the end of the time range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(description="Time aggregation interval for the statistics data. Determines how data points are grouped."),
    ],
    allowed: Annotated[
        bool,
        Field(description="Filter for URL access status. Set to true to retrieve allowed URLs, false for denied URLs."),
    ],
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of results to return. Limits the result set size for performance optimization.",
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
    if allowed is not None:
        query_params["allowed"] = allowed
    if top is not None:
        query_params["top"] = top
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/secureWebServices/allowedDeniedUrlSrcIp",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_secure_web_services_config_stats",
    description="POST /stats/timeseries/secureWebServices/configStats\n\ngetSecureWebServicesConfigStats\n\nGet Secure Web Services configuration statistics timeseries data for an appliance.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_secure_web_services_config_stats(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary for data retrieval as Unix epoch timestamp in seconds. Must be less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary for data retrieval as Unix epoch timestamp in seconds. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation granularity. Determines how data is grouped: 'minute' for raw data, 'hour' for hourly aggregation, 'day' for daily aggregation."
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
        "/stats/timeseries/secureWebServices/configStats",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_secure_web_services_src_ip",
    description="POST /stats/timeseries/secureWebServices/srcIp\n\ngetSecureWebServicesSrcIp\n\nGet top source IPs by flow count from Secure Web Services statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_secure_web_services_src_ip(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) indicating the start of the time range. Must be less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="Unix epoch timestamp (seconds) indicating the end of the time range. Must be greater than startTime."
        ),
    ],
    granularity: Annotated[
        str, Field(description="Data aggregation granularity specifying the time interval for statistics grouping.")
    ],
    top: Annotated[
        int | None,
        Field(default=None, description="Maximum number of source IPs to return. Default and maximum value is 50."),
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
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/secureWebServices/srcIp",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_secure_web_services_src_ip_url",
    description="POST /stats/timeseries/secureWebServices/srcIpUrl\n\ngetSecureWebServicesSrcIpUrl\n\nGet top domains/URLs accessed by a source IP from secure web services statistics.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_secure_web_services_src_ip_url(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary for the data query as Unix epoch time in seconds (signed 64-bit integer). Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary for the data query as Unix epoch time in seconds (signed 64-bit integer). Must be >= 0 and greater than startTime."
        ),
    ],
    granularity: Annotated[
        str,
        Field(
            description="Data aggregation interval determining the time granularity of statistics. Valid values: 'minute', 'hour', 'day', 'month' (case-insensitive)."
        ),
    ],
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of results to return. If not provided or exceeds 50, defaults to 50.",
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
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/secureWebServices/srcIpUrl",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_shaper",
    description="POST /stats/timeseries/shaper\n\ngetShaperTimeSeriesStatsByPost\n\nRetrieve shaper time series statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_shaper(
    ctx: Context,
    startTime: Annotated[
        int, Field(description="Start of time range in Unix epoch seconds. Must be >= 0 and less than endTime.")
    ],
    endTime: Annotated[
        int, Field(description="End of time range in Unix epoch seconds. Must be greater than startTime.")
    ],
    granularity: Annotated[
        str,
        Field(
            description="Time interval for data aggregation. Valid values: minute, hour, day, month. The value is case-insensitive."
        ),
    ],
    trafficClass: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by QoS traffic class (1-10). Class 1 is highest priority. When omitted, returns data for all traffic classes.",
        ),
    ] = None,
    direction: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by traffic direction. 0 = outbound (WAN-bound), 1 = inbound (LAN-bound). When omitted, returns data for both directions.",
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, keys response data by appliance IP address instead of nePk. Default is false (uses nePk).",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Response format. Set to 'csv' for CSV file download. Omit or use any other value for JSON response.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of data points to return per appliance. Default is 10000 if not specified.",
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
    if direction is not None:
        query_params["direction"] = direction
    if ip is not None:
        query_params["ip"] = ip
    if format is not None:
        query_params["format"] = format
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/shaper",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_syn_cookie_ip_reputation",
    description="POST /stats/timeseries/synCookie/ipReputation\n\ngetSynCookieIpReputationTimeseries\n\nGet SYN cookie IP reputation time series statistics",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_syn_cookie_ip_reputation(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary as Unix epoch timestamp in seconds. Must be >= 0 and less than endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary as Unix epoch timestamp in seconds. Must be >= 0 and greater than startTime."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/synCookie/ipReputation",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_traffic_class",
    description="POST /stats/timeseries/trafficClass\n\ngetTrafficClassTimeSeriesStatsByPost\n\nRetrieve traffic class time series statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_traffic_class(
    ctx: Context,
    granularity: Annotated[
        str,
        Field(description="Data aggregation interval. Determines time-bucket resolution for stats. Case-insensitive."),
    ],
    trafficType: Annotated[
        str,
        Field(
            description="Traffic category filter. 'optimized_traffic' (1) = WAN-optimized flows, 'pass_through_shaped' (2) = shaped but not optimized, 'pass_through_unshaped' (3) = passthrough traffic, 'all_traffic' (4) = combined total."
        ),
    ],
    trafficClass: Annotated[
        int,
        Field(
            description="QoS traffic class priority level (1-10). Class 1 is highest priority, class 10 is lowest. Must be between 1 and 10 inclusive."
        ),
    ],
    startTime: Annotated[
        int | None,
        Field(
            default=None,
            description="Unix timestamp (seconds since EPOCH) for range start. Required unless 'latest' is provided. Must be >= 0 and less than endTime.",
        ),
    ] = None,
    endTime: Annotated[
        int | None,
        Field(
            default=None,
            description="Unix timestamp (seconds since EPOCH) for range end. Required unless 'latest' is provided. Must be > startTime.",
        ),
    ] = None,
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Retrieve stats for the latest N minutes from current time. When provided, auto-calculates startTime=(now - latest*60) and endTime=now, overriding any explicit time parameters.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None, description="Maximum records per appliance to return. Limits result set size for performance."
        ),
    ] = None,
    ip: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, response data keys are appliance IP addresses instead of nePk identifiers. Useful for human-readable output.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Output format. Set to 'CSV' for downloadable spreadsheet file (application/vnd.ms-excel). Default returns JSON.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if granularity is not None:
        query_params["granularity"] = granularity
    if trafficType is not None:
        query_params["trafficType"] = trafficType
    if trafficClass is not None:
        query_params["trafficClass"] = trafficClass
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if latest is not None:
        query_params["latest"] = latest
    if limit is not None:
        query_params["limit"] = limit
    if ip is not None:
        query_params["ip"] = ip
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/trafficClass",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_timeseries_user2",
    description="POST /stats/timeseries/user2\n\ngetUserTimeSeriesStats\n\nRetrieve user time series statistics for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_timeseries_user2(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(description="Start of the time range in Unix epoch seconds. Must be non-negative and less than endTime."),
    ],
    endTime: Annotated[
        int, Field(description="End of the time range in Unix epoch seconds. Must be greater than startTime.")
    ],
    user: Annotated[str, Field(description="Username to filter statistics. Required parameter that cannot be empty.")],
    latest: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of minutes from current time to retrieve stats. When provided, overrides startTime and endTime with calculated values (endTime=now, startTime=now-latest*60).",
        ),
    ] = None,
    total: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, includes aggregate '__total__' records along with user-specific data. Default is false.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(default=None, description="Response format. Use 'csv' for CSV file download, omit for JSON response."),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of records to return. Capped at server-configured LIMIT_OF_ROW. Default applies server maximum if not specified.",
        ),
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
    if latest is not None:
        query_params["latest"] = latest
    if total is not None:
        query_params["total"] = total
    if format is not None:
        query_params["format"] = format
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/timeseries/user2",
        query_params=query_params or None,
        body=body,
    )
