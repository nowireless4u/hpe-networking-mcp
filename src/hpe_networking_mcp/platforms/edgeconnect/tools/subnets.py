"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``subnets``
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
    name="edgeconnect_get_subnets",
    description="GET /subnets\n\nGetSubnets731\n\nRetrieve subnet information for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_subnets(
    ctx: Context,
    cached: Annotated[
        bool,
        Field(
            description="When true, retrieves subnet data from Orchestrator's cached database. When false, queries the appliance directly for real-time data."
        ),
    ],
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    subnet: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter routes by subnet in CIDR notation. Supports both IPv4 (e.g., '192.168.1.0/24') and IPv6 addresses.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if cached is not None:
        query_params["cached"] = cached
    if nePk is not None:
        query_params["nePk"] = nePk
    if subnet is not None:
        query_params["subnet"] = subnet
    return await edgeconnect_request(
        ctx,
        "GET",
        "/subnets",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_subnets_all",
    description="GET /subnets/all\n\nGetAllSubnets731\n\nGet appliance subnet information for all VRF segments",
    capability=Capability.READ,
)
async def edgeconnect_get_subnets_all(
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
        "/subnets/all",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_subnets_for_discovered",
    description="GET /subnets/forDiscovered\n\nGetSubnetsForDiscoveredAppliance729\n\nRetrieve subnet information from a discovered appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_subnets_for_discovered(
    ctx: Context,
    discoveredId: Annotated[
        str,
        Field(
            description="Unique numeric identifier of the discovered appliance. Obtained from the discovery process before the appliance is fully onboarded."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if discoveredId is not None:
        query_params["discoveredId"] = discoveredId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/subnets/forDiscovered",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_subnets_configured",
    description="POST /subnets/configured\n\nConfSubnets728\n\nConfigure subnets on a legacy appliance (pre-8.1.7)",
    capability=Capability.WRITE,
)
async def edgeconnect_post_subnets_configured(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/subnets/configured",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_subnets_set_subnet_sharing_options",
    description="POST /subnets/setSubnetSharingOptions\n\nsetSubnetSharingOptions730\n\nConfigure appliance subnet sharing options",
    capability=Capability.WRITE,
)
async def edgeconnect_post_subnets_set_subnet_sharing_options(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/subnets/setSubnetSharingOptions",
        query_params=query_params or None,
        body=body,
    )
