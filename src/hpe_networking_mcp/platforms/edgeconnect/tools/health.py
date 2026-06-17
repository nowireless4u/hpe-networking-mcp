"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``health``
Operations in this file: 8
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
    name="edgeconnect_get_health_alarm_period_summary",
    description="GET /health/alarmPeriodSummary\n\napplianceAlarmSummary407\n\nGet alarm summary for an appliance within a time period",
    capability=Capability.READ,
)
async def edgeconnect_get_health_alarm_period_summary(
    ctx: Context,
    from_: Annotated[
        int,
        Field(
            description="Start time in milliseconds since EPOCH. Defines the beginning of the time range for alarm queries."
        ),
    ],
    to: Annotated[
        int,
        Field(description="End time in milliseconds since EPOCH. Defines the end of the time range for alarm queries."),
    ],
    applianceId: Annotated[
        str,
        Field(
            description="Unique identifier of the appliance (network element primary key). Used to filter alarms for a specific appliance."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if from_ is not None:
        query_params["from"] = from_
    if to is not None:
        query_params["to"] = to
    if applianceId is not None:
        query_params["applianceId"] = applianceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/health/alarmPeriodSummary",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_health_health_threshold_config",
    description="GET /health/healthThresholdConfig\n\nhealthThresholdConfigGet408\n\nRetrieve health threshold configuration settings",
    capability=Capability.READ,
)
async def edgeconnect_get_health_health_threshold_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/health/healthThresholdConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_health_jitter_period_summary",
    description="GET /health/jitterPeriodSummary\n\nJitterPeriodSummary410\n\nGet jitter health summary for an appliance at a specific time",
    capability=Capability.READ,
)
async def edgeconnect_get_health_jitter_period_summary(
    ctx: Context,
    time: Annotated[
        int,
        Field(
            description="Hour boundary timestamp in seconds since EPOCH (Unix timestamp). Defines which hourly period to retrieve jitter data for."
        ),
    ],
    applianceId: Annotated[
        str, Field(description="Unique identifier of the appliance (network element primary key). Cannot be empty.")
    ],
    overlayId: Annotated[
        int,
        Field(
            description="Overlay network identifier to filter results. Use -1 to include all overlays (excludes underlay with overlayId=0)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if time is not None:
        query_params["time"] = time
    if applianceId is not None:
        query_params["applianceId"] = applianceId
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/health/jitterPeriodSummary",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_health_latency_period_summary",
    description="GET /health/latencyPeriodSummary\n\nLatencyPeriodSummary411\n\nGet latency health summary for an appliance at a specific time",
    capability=Capability.READ,
)
async def edgeconnect_get_health_latency_period_summary(
    ctx: Context,
    time: Annotated[
        int,
        Field(
            description="Hour boundary timestamp in seconds since EPOCH (Unix timestamp). Defines which hourly period to retrieve latency data for."
        ),
    ],
    applianceId: Annotated[
        str, Field(description="Unique identifier of the appliance (network element primary key). Cannot be empty.")
    ],
    overlayId: Annotated[
        int,
        Field(
            description="Overlay network identifier to filter results. Use -1 to include all overlays (excludes underlay with overlayId=0)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if time is not None:
        query_params["time"] = time
    if applianceId is not None:
        query_params["applianceId"] = applianceId
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/health/latencyPeriodSummary",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_health_loss_period_summary",
    description="GET /health/lossPeriodSummary\n\nLossPeriodSummary412\n\nGet packet loss health summary for an appliance at a specific time",
    capability=Capability.READ,
)
async def edgeconnect_get_health_loss_period_summary(
    ctx: Context,
    time: Annotated[
        int,
        Field(
            description="Hour boundary timestamp in seconds since EPOCH (Unix timestamp). Defines which hourly period to retrieve loss data for."
        ),
    ],
    applianceId: Annotated[
        str, Field(description="Unique identifier of the appliance (network element primary key). Cannot be empty.")
    ],
    overlayId: Annotated[
        int,
        Field(
            description="Overlay network identifier to filter results. Use -1 to include all overlays (excludes underlay with overlayId=0)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if time is not None:
        query_params["time"] = time
    if applianceId is not None:
        query_params["applianceId"] = applianceId
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/health/lossPeriodSummary",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_health_mos_period_summary",
    description="GET /health/mosPeriodSummary\n\nMosPeriodSummary413\n\nGet MOS health summary for an appliance at a specific time",
    capability=Capability.READ,
)
async def edgeconnect_get_health_mos_period_summary(
    ctx: Context,
    time: Annotated[
        int,
        Field(
            description="Hour boundary timestamp in seconds since EPOCH (Unix timestamp). Defines which hourly period to retrieve MOS data for."
        ),
    ],
    applianceId: Annotated[
        str, Field(description="Unique identifier of the appliance (network element primary key). Cannot be empty.")
    ],
    overlayId: Annotated[
        int,
        Field(
            description="Overlay network identifier to filter results. Use -1 to include all overlays (excludes underlay with overlayId=0)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if time is not None:
        query_params["time"] = time
    if applianceId is not None:
        query_params["applianceId"] = applianceId
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/health/mosPeriodSummary",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_health",
    description="POST /health\n\nHealthSummary406\n\nGet health summary for appliances over a time range",
    capability=Capability.WRITE,
)
async def edgeconnect_post_health(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/health",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_health_health_threshold_config",
    description="POST /health/healthThresholdConfig\n\nhealthThresholdConfigPost409\n\nUpdate health threshold configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_health_health_threshold_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/health/healthThresholdConfig",
        query_params=None,
        body=body,
    )
