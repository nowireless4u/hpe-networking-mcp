"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Anomaly``
Operations in this file: 3
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_get_site_anomaly_events_for_client",
    description="GET /api/v1/sites/{site_id}/anomaly/client/{client_mac}/{metric}\n\ngetSiteAnomalyEventsForClient\n\nGet Client Anomaly Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_anomaly_events_for_client(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    client_mac: Annotated[str, Field(description="path parameter 'client_mac'")],
    metric: Annotated[
        str, Field(description="See [List Insight Metrics](/#operations/listInsightMetrics) for available metrics")
    ],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/anomaly/client/{client_mac}/{metric}",
        path_params={"site_id": site_id, "client_mac": client_mac, "metric": metric},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_anomaly_events_for_device",
    description="GET /api/v1/sites/{site_id}/anomaly/device/{device_mac}/{metric}\n\ngetSiteAnomalyEventsForDevice\n\nGet Device Anomaly Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_anomaly_events_for_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    metric: Annotated[
        str, Field(description="See [List Insight Metrics](/#operations/listInsightMetrics) for available metrics")
    ],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/anomaly/device/{device_mac}/{metric}",
        path_params={"site_id": site_id, "metric": metric, "device_mac": device_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_anomaly_events",
    description="GET /api/v1/sites/{site_id}/anomaly/{metric}\n\nlistSiteAnomalyEvents\n\nList Site Anomaly Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_anomaly_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    metric: Annotated[
        str, Field(description="See [List Insight Metrics](/#operations/listInsightMetrics) for available metrics")
    ],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/anomaly/{metric}",
        path_params={"site_id": site_id, "metric": metric},
        query_params=None,
        body=None,
    )
