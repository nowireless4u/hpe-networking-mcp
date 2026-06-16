"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``appSystemStateInfo``
Operations in this file: 1
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
    name="edgeconnect_get_system_info",
    description="GET /systemInfo\n\nappSystemStateInfo734\n\nGet Appliance System State Information",
    capability=Capability.READ,
)
async def edgeconnect_get_system_info(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="Controls data source: 'true' fetches from Orchestrator cache (faster), 'false' fetches directly from the appliance (real-time). Default is 'true'. When cached, uptime is dynamically recalculated based on last sync time.",
        ),
    ] = None,
    discoveredId: Annotated[
        str | None,
        Field(
            default=None,
            description="ID of a discovered (unapproved) appliance. Required when using 'url' parameter and mutually exclusive with 'nePk'. Used for querying appliances in discovered state before approval.",
        ),
    ] = None,
    url: Annotated[
        str | None,
        Field(
            default=None,
            description="The API URL path after 'rest/json/' to query on the appliance. Required when using 'discoveredId' and mutually exclusive with 'nePk'. Suffix 'ForDiscovered' is automatically removed before querying.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    if discoveredId is not None:
        query_params["discoveredId"] = discoveredId
    if url is not None:
        query_params["url"] = url
    return await edgeconnect_request(
        ctx,
        "GET",
        "/systemInfo",
        query_params=query_params or None,
    )
