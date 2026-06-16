"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``nat``
Operations in this file: 3
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
    name="edgeconnect_get_nat",
    description="GET /nat\n\ngetAllNat468\n\nGet complete NAT configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_nat(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="Data source selection. When 'true', returns cached data from Orchestrator database. When 'false', fetches fresh data directly from the appliance (slower but current).",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/nat",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_nat_maps",
    description="GET /nat/maps\n\nbranchNatMapsGet469\n\nGet NAT maps configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_nat_maps(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="Data source selection. When 'true' (default), returns cached data from Orchestrator database (faster). When 'false', fetches fresh data directly from the appliance (slower but current).",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/nat/maps",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_nat_nat_pools",
    description="GET /nat/natPools\n\ngetAllNatPools470\n\nGet NAT pools configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_nat_nat_pools(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="Data source selection. 'true' (default) returns cached data from Orchestrator database (faster). 'false' fetches live data directly from appliance (slower, updates cache).",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/nat/natPools",
        query_params=query_params or None,
    )
