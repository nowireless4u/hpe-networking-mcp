"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``applianceCPUstats``
Operations in this file: 5
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
    name="edgeconnect_get_appliance_cpustat_historical_cancelfetch",
    description="GET /appliance/cpustat/historical/cancelfetch\n\napplianceCPUstatsCancelFetchGet\n\nCancel an in-progress CPU statistics fetch operation",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_cpustat_historical_cancelfetch(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/cpustat/historical/cancelfetch",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_cpustat_historical_isfetchinprogress",
    description="GET /appliance/cpustat/historical/isfetchinprogress\n\napplianceCPUstatsIsFetchInProgressGet1\n\nCheck CPU statistics fetch operation status",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_cpustat_historical_isfetchinprogress(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/cpustat/historical/isfetchinprogress",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_cpustat_historical_maxtimestamp",
    description="GET /appliance/cpustat/historical/maxtimestamp\n\napplianceCPUstatsMaxtimestampGet1\n\nGet the most recent CPU statistics timestamp for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_cpustat_historical_maxtimestamp(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/cpustat/historical/maxtimestamp",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_timeseries_cpustat",
    description="GET /stats/timeseries/cpustat\n\napplianceCPUTimeseriesStatsGet1\n\nRetrieve CPU timeseries statistics for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_timeseries_cpustat(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cpuid: Annotated[
        str,
        Field(
            description="CPU identifier for the specific processor core. Use values like '0', '1', '2' for individual cores or 'all' for aggregate stats."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cpuid is not None:
        query_params["cpuid"] = cpuid
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/timeseries/cpustat",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_appliance_cpustat_historical_fetch",
    description="POST /appliance/cpustat/historical/fetch\n\napplianceCPUstatsGet1\n\nFetch CPU historical statistics from appliance and store in Orchestrator database",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_cpustat_historical_fetch(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/cpustat/historical/fetch",
        query_params=query_params or None,
    )
