"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``restRequestTimeStats``
Operations in this file: 2
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
    name="edgeconnect_get_rest_request_time_stats",
    description="GET /restRequestTimeStats\n\ngetRestRequestTimeStatsDetails546\n\nGet detailed REST request timing for a specific appliance and resource",
    capability=Capability.READ,
)
async def edgeconnect_get_rest_request_time_stats(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    resource: Annotated[
        str,
        Field(
            description="Base resource path to filter (e.g., 'webconfig'). Must match the resourceBase stored in the database."
        ),
    ],
    portalWS: Annotated[
        bool,
        Field(
            description="WebSocket connection type. True for portal WebSocket (channel=2), false for direct WebSocket (channel=1)."
        ),
    ],
    method: Annotated[str, Field(description="HTTP method to filter by. Must match method of recorded requests.")],
    from_: Annotated[
        int,
        Field(
            description="Start of time range as Unix epoch timestamp in milliseconds. Only requests on or after this time are included."
        ),
    ],
    to: Annotated[
        int, Field(description="End of time range as Unix epoch timestamp in milliseconds. Use 0 for current time.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if resource is not None:
        query_params["resource"] = resource
    if portalWS is not None:
        query_params["portalWS"] = portalWS
    if method is not None:
        query_params["method"] = method
    if from_ is not None:
        query_params["from"] = from_
    if to is not None:
        query_params["to"] = to
    return await edgeconnect_request(
        ctx,
        "GET",
        "/restRequestTimeStats",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_rest_request_time_stats_summary",
    description="GET /restRequestTimeStats/summary\n\ngetRestRequestTimeStatsSummary545\n\nGet aggregated REST request timing statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_rest_request_time_stats_summary(
    ctx: Context,
    resource: Annotated[
        str,
        Field(
            description="Base resource path to filter (e.g., 'webconfig', 'stats'). Use 'all' to include all resources."
        ),
    ],
    portalWS: Annotated[
        bool,
        Field(
            description="WebSocket connection type. True for portal WebSocket (channel=2), false for direct WebSocket (channel=1)."
        ),
    ],
    timedout: Annotated[
        bool,
        Field(
            description="Filter by timeout status. True returns only timed-out requests, false returns only non-timed-out requests."
        ),
    ],
    from_: Annotated[
        int,
        Field(
            description="Start of time range as Unix epoch timestamp in milliseconds. Only requests on or after this time are included."
        ),
    ],
    to: Annotated[
        int, Field(description="End of time range as Unix epoch timestamp in milliseconds. Use 0 for current time.")
    ],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if resource is not None:
        query_params["resource"] = resource
    if portalWS is not None:
        query_params["portalWS"] = portalWS
    if timedout is not None:
        query_params["timedout"] = timedout
    if from_ is not None:
        query_params["from"] = from_
    if to is not None:
        query_params["to"] = to
    return await edgeconnect_request(
        ctx,
        "GET",
        "/restRequestTimeStats/summary",
        query_params=query_params or None,
    )
