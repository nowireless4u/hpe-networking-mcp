"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``bfd``
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
    name="edgeconnect_get_bfd_config_vrfs",
    description="GET /bfd/config/vrfs\n\nGetBfdVrfConfig138\n\nRetrieve BFD VRF configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_bfd_config_vrfs(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    vrfId: Annotated[
        int | None,
        Field(
            default=None,
            description="VRF segment identifier to retrieve specific VRF configuration. Omit to retrieve all VRF configurations.",
        ),
    ] = None,
    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, retrieves data from Orchestrator cache. When false, fetches directly from appliance and updates cache.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if vrfId is not None:
        query_params["vrfId"] = vrfId
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/bfd/config/vrfs",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_bfd_state_vrfs",
    description="GET /bfd/state/vrfs\n\nBfdSessions139\n\nRetrieve BFD session state for all VRFs",
    capability=Capability.READ,
)
async def edgeconnect_get_bfd_state_vrfs(
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
            description="When true, retrieves data from Orchestrator cache. When false, fetches directly from appliance.",
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
        "/bfd/state/vrfs",
        query_params=query_params or None,
    )
