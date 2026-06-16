"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``bgp``
Operations in this file: 6
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
    name="edgeconnect_get_bgp_config_all_vrfs_neighbor",
    description="GET /bgp/config/allVrfs/neighbor\n\nGetAllVrfsNeighbor140\n\nGet BGP neighbor configuration for all VRFs",
    capability=Capability.READ,
)
async def edgeconnect_get_bgp_config_all_vrfs_neighbor(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="Data source selector. When true, retrieves cached data from Orchestrator database; when false or omitted, fetches live data from the appliance.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/bgp/config/allVrfs/neighbor",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_bgp_config_all_vrfs_system",
    description="GET /bgp/config/allVrfs/system\n\nGetAllVrfBGPSystemConfig141\n\nGet BGP system configuration for all VRFs",
    capability=Capability.READ,
)
async def edgeconnect_get_bgp_config_all_vrfs_system(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="Data source selector. When true, retrieves cached data from Orchestrator database; when false or omitted, fetches live data from the appliance.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/bgp/config/allVrfs/system",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_bgp_config_neighbor",
    description="GET /bgp/config/neighbor\n\nGetNeighbor142\n\nGet BGP neighbor configuration for default VRF",
    capability=Capability.READ,
)
async def edgeconnect_get_bgp_config_neighbor(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="Data source selector. When true, retrieves cached data from Orchestrator database; when false or omitted, fetches live data from the appliance.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/bgp/config/neighbor",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_bgp_config_system",
    description="GET /bgp/config/system\n\nGetBGPSystemConfig143\n\nGet BGP system configuration for default VRF",
    capability=Capability.READ,
)
async def edgeconnect_get_bgp_config_system(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="Data source selector. When true, retrieves cached data from Orchestrator database; when false or omitted, fetches live data from the appliance.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/bgp/config/system",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_bgp_state",
    description="GET /bgp/state\n\nBGPState145\n\nGet BGP state details for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_bgp_state(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="Data source selector. When true, retrieves cached data from Orchestrator database; when false or omitted, fetches live data directly from the appliance.",
        ),
    ] = None,
    vrfId: Annotated[
        str | None,
        Field(
            default=None,
            description="VRF segment identifier. When provided, retrieves BGP state for the specified VRF; when omitted, returns state for the default VRF (segment 0).",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    if vrfId is not None:
        query_params["vrfId"] = vrfId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/bgp/state",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_bgp_state_all_vrfs",
    description="GET /bgp/state/allVrfs\n\nAllVrfsBGPState144\n\nGet BGP state details for all VRFs",
    capability=Capability.READ,
)
async def edgeconnect_get_bgp_state_all_vrfs(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="Data source selector. When true, retrieves cached data from Orchestrator database; when false or omitted, fetches live data directly from the appliance.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/bgp/state/allVrfs",
        query_params=query_params or None,
    )
