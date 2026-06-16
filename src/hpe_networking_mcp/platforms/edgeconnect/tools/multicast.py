"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``multicast``
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
    name="edgeconnect_get_multicast_config",
    description="GET /multicast/config\n\nmulticastConfigGet463\n\nGet Multicast Configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_multicast_config(
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
            description="When true, returns cached data from Orchestrator database. When false, fetches fresh data directly from the appliance. Defaults to true if not provided.",
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
        "/multicast/config",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_multicast_enable",
    description="GET /multicast/enable\n\nmulticastEnableGet464\n\nGet Multicast Enable Status",
    capability=Capability.READ,
)
async def edgeconnect_get_multicast_enable(
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
            description="When 'true', returns cached data from Orchestrator database. When 'false', fetches fresh data directly from the appliance. Defaults to 'true' if not provided.",
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
        "/multicast/enable",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_multicast_state_interfaces",
    description="GET /multicast/state/interfaces\n\nmulticastInterfaceStateGet465\n\nGet Multicast Interface State",
    capability=Capability.READ,
)
async def edgeconnect_get_multicast_state_interfaces(
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
        "/multicast/state/interfaces",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_multicast_state_neighbors",
    description="GET /multicast/state/neighbors\n\nmulticastNeighborStateGet466\n\nGet PIM Neighbor State",
    capability=Capability.READ,
)
async def edgeconnect_get_multicast_state_neighbors(
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
        "/multicast/state/neighbors",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_multicast_state_routes",
    description="GET /multicast/state/routes\n\nmulticastRouteStateGet467\n\nGet Multicast Route State",
    capability=Capability.READ,
)
async def edgeconnect_get_multicast_state_routes(
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
        "/multicast/state/routes",
        query_params=query_params or None,
    )
