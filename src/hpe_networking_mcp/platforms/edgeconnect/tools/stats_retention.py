"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``statsRetention``
Operations in this file: 9
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
    name="edgeconnect_get_gms_stats_approximate_disk_space",
    description="GET /gms/stats/approximateDiskSpace\n\ngetApproximateDiskSpace333\n\nCalculate approximate disk space requirements for statistics storage",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_stats_approximate_disk_space(
    ctx: Context,
    applianceCount: Annotated[
        int,
        Field(
            description="Number of appliances to calculate disk space for. Used to estimate storage requirements for appliance-based statistics."
        ),
    ],
    numberOfSegments: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of DDoS segments. Used for DDoS-related statistics (ddospeakandpeakdroprate, ddostotalstats, addosbaseline). Must be between 1 and 24.",
        ),
    ] = None,
    numberOfTunnels: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of tunnels. If not provided, automatically calculated based on existing tunnel configuration and appliance count.",
        ),
    ] = None,
    numberOfOverlays: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of overlays. Used in tunnel calculation when numberOfTunnels is not specified.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if applianceCount is not None:
        query_params["applianceCount"] = applianceCount
    if numberOfSegments is not None:
        query_params["numberOfSegments"] = numberOfSegments
    if numberOfTunnels is not None:
        query_params["numberOfTunnels"] = numberOfTunnels
    if numberOfOverlays is not None:
        query_params["numberOfOverlays"] = numberOfOverlays
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/stats/approximateDiskSpace",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_stats_collection",
    description="GET /gms/stats/collection\n\nstatisticsCollection334\n\nRetrieve statistics collection enable/disable status for all stat types",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_stats_collection(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/stats/collection",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_stats_non_stats_table_retention",
    description="GET /gms/stats/nonStatsTable/retention\n\nstatisticsRetention336\n\nRetrieve retention settings for non-statistics tables",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_stats_non_stats_table_retention(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/stats/nonStatsTable/retention",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_stats_retention",
    description="GET /gms/stats/retention\n\nstatisticsRetention338\n\nRetrieve statistics retention settings for all stat types",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_stats_retention(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/stats/retention",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_stats_stats_retention_notification",
    description="GET /gms/stats/statsRetentionNotification\n\nstatsRetentionNotificationInfoGet340\n\nRetrieve stats retention notification dismissal status",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_stats_stats_retention_notification(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/stats/statsRetentionNotification",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_gms_stats_stats_retention_notification",
    description="POST /gms/stats/statsRetentionNotification\n\nStatsRetentionNotificationInfoPOST341\n\nUpdate stats retention notification dismissal status",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_stats_stats_retention_notification(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/stats/statsRetentionNotification",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_gms_stats_collection",
    description="PUT /gms/stats/collection\n\nenableDisableSC335\n\nEnable or disable statistics collection for a specific stat type",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_stats_collection(
    ctx: Context,
    statType: Annotated[
        str,
        Field(
            description="The statistics type to enable or disable collection for. Must match an existing stat type in the system."
        ),
    ],
    isEnabled: Annotated[bool, Field(description="Set to true to enable statistics collection, false to disable it.")],
) -> Any:
    query_params: dict[str, Any] = {}
    if statType is not None:
        query_params["statType"] = statType
    if isEnabled is not None:
        query_params["isEnabled"] = isEnabled
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gms/stats/collection",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_put_gms_stats_non_stats_table_retention",
    description="PUT /gms/stats/nonStatsTable/retention\n\nstatisticsRetentionUpdate337\n\nUpdate retention settings for a non-statistics table",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_stats_non_stats_table_retention(
    ctx: Context,
    statType: Annotated[
        str,
        Field(
            description="The non-statistics table type to update retention for. Must match an existing table name in nonStatsTableRetention."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if statType is not None:
        query_params["statType"] = statType
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gms/stats/nonStatsTable/retention",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_gms_stats_retention",
    description="PUT /gms/stats/retention\n\nstatisticsRetentionUpdate339\n\nUpdate statistics retention period for a specific stat type",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_stats_retention(
    ctx: Context,
    statType: Annotated[
        str,
        Field(
            description="The statistics type to update retention for. Must match an existing stat type in the system."
        ),
    ],
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if statType is not None:
        query_params["statType"] = statType
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gms/stats/retention",
        query_params=query_params or None,
        body=body,
    )
