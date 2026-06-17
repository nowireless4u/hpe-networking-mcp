"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``reachability``
Operations in this file: 4
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
    name="edgeconnect_get_reachability_appliance",
    description="GET /reachability/appliance\n\nreachabilityFromAppliance517\n\nGet appliance connectivity status",
    capability=Capability.READ,
)
async def edgeconnect_get_reachability_appliance(
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
        "/reachability/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_reachability_gms",
    description="GET /reachability/gms\n\nreachabilityFromGMS\n\nGet appliance reachability status from Orchestrator",
    capability=Capability.READ,
)
async def edgeconnect_get_reachability_gms(
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
        "/reachability/gms",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_reachability_gms2",
    description="GET /reachability/gms2\n\nreachabilityFromGMS518\n\nGet detailed WebSocket reachability status from Orchestrator",
    capability=Capability.READ,
)
async def edgeconnect_get_reachability_gms2(
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
        "/reachability/gms2",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_reachability_gms2_appliances_reachability",
    description="GET /reachability/gms2/appliancesReachability\n\ngetAppliancesReachability\n\nGet reachability status for all appliances from the Orchestrator",
    capability=Capability.READ,
)
async def edgeconnect_get_reachability_gms2_appliances_reachability(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/reachability/gms2/appliancesReachability",
        query_params=None,
    )
