"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``vxlan``
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
    name="edgeconnect_get_vxlan_config",
    description="GET /vxlan/config\n\ngetVxlanConfig\n\nGet VXLAN Configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_vxlan_config(
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
            description="Data source selector. When true, returns cached data from Orchestrator database. When false or omitted, fetches live data directly from the appliance.",
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
        "/vxlan/config",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_vxlan_seg_vni_map",
    description="GET /vxlan/segVniMap\n\ngetVNIMappings\n\nGet VRF to VNI Segment Mappings",
    capability=Capability.READ,
)
async def edgeconnect_get_vxlan_seg_vni_map(
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
            description="Data source selector. When true, returns cached data from Orchestrator database. When false or omitted, fetches live data directly from the appliance.",
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
        "/vxlan/segVniMap",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_vxlan_state",
    description="GET /vxlan/state\n\ngetVxlanStateDetails\n\nGet VXLAN State Details",
    capability=Capability.READ,
)
async def edgeconnect_get_vxlan_state(
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
            description="Data source selector. When true, returns cached data from Orchestrator database. When false or omitted, fetches live data directly from the appliance.",
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
        "/vxlan/state",
        query_params=query_params or None,
    )
