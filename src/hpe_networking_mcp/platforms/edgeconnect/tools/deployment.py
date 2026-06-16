"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``deployment``
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
    name="edgeconnect_get_deployment",
    description="GET /deployment\n\ngetApplianceDeployment218\n\nGet deployment configuration for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_deployment(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        bool,
        Field(
            description="When true, retrieves deployment data from Orchestrator's database cache (faster, may be stale). When false, fetches live data directly from the appliance (slower, always current)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/deployment",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_tunnels_configuration_deployment",
    description="GET /tunnelsConfiguration/deployment\n\ngetApplianceDeployment902\n\nGet tunnel-related deployment information for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_tunnels_configuration_deployment(
    ctx: Context,
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
    return await edgeconnect_request(
        ctx,
        "GET",
        "/tunnelsConfiguration/deployment",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_deployment_validate",
    description="POST /deployment/validate\n\nvalidateDeployment216\n\nValidate deployment configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_deployment_validate(
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
        "/deployment/validate",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_deployment_validate_discovered",
    description="POST /deployment/validateDiscovered\n\nvalidateDiscoveredDeployment\n\nValidate deployment configuration for a discovered appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_deployment_validate_discovered(
    ctx: Context,
    discoveredId: Annotated[
        int,
        Field(
            description="Numeric ID of the discovered appliance to validate against. Obtained from the discovered appliances list."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if discoveredId is not None:
        query_params["discoveredId"] = discoveredId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/deployment/validateDiscovered",
        query_params=query_params or None,
        body=body,
    )
