"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``bondedTunnelsConfiguration``
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
    name="edgeconnect_get_tunnels2_bonded",
    description="GET /tunnels2/bonded\n\nsearchAllBondedTunnels889\n\nGet bonded tunnels configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_tunnels2_bonded(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    tunnelId: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by specific tunnel ID. Must be used with nePk to retrieve a single tunnel.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of bonded tunnels to return. Use this to limit results as networks may have many tunnels.",
        ),
    ] = None,
    matchingAlias: Annotated[
        str | None, Field(default=None, description="Case-insensitive partial match filter for tunnel alias names.")
    ] = None,
    overlayId: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by overlay ID. Use 'all' to return tunnels from all overlays, or a specific numeric ID.",
        ),
    ] = None,
    state: Annotated[
        str | None,
        Field(
            default=None,
            description="Regex pattern to filter tunnels by operational status (e.g., 'Up', 'Down'). Case-insensitive.",
        ),
    ] = None,
    id: Annotated[
        bool | None, Field(default=None, description="When true, includes only the 'id' field in response objects.")
    ] = None,
    alias: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, includes only the 'alias' field (tunnel display name) in response objects.",
        ),
    ] = None,
    tag: Annotated[
        bool | None,
        Field(default=None, description="When true, includes only the 'tag' field (overlay name) in response objects."),
    ] = None,
    srcNePk: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, includes only the 'srcNePk' field (source appliance ID) in response objects.",
        ),
    ] = None,
    destNePk: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, includes only the 'destNePk' field (destination appliance ID) in response objects.",
        ),
    ] = None,
    destTunnelId: Annotated[
        bool | None,
        Field(default=None, description="When true, includes only the 'destTunnelId' field in response objects."),
    ] = None,
    destTunnelAlias: Annotated[
        bool | None,
        Field(default=None, description="When true, includes only the 'destTunnelAlias' field in response objects."),
    ] = None,
    operStatus: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, includes only the 'operStatus' field (operational status like Up/Down) in response objects.",
        ),
    ] = None,
    adminStatus: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, includes only the 'adminStatus' field (administrative status) in response objects.",
        ),
    ] = None,
    remoteIdState: Annotated[
        bool | None,
        Field(default=None, description="When true, includes only the 'remoteIdState' field in response objects."),
    ] = None,
    fecStatus: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, includes only the 'fecStatus' field (Forward Error Correction status) in response objects.",
        ),
    ] = None,
    fecRatio: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, includes only the 'fecRatio' field (FEC ratio value) in response objects.",
        ),
    ] = None,
    children: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, includes 'children' array with physical tunnel id/alias pairs for each bonded tunnel.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if tunnelId is not None:
        query_params["tunnelId"] = tunnelId
    if limit is not None:
        query_params["limit"] = limit
    if matchingAlias is not None:
        query_params["matchingAlias"] = matchingAlias
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    if state is not None:
        query_params["state"] = state
    if id is not None:
        query_params["id"] = id
    if alias is not None:
        query_params["alias"] = alias
    if tag is not None:
        query_params["tag"] = tag
    if srcNePk is not None:
        query_params["srcNePk"] = srcNePk
    if destNePk is not None:
        query_params["destNePk"] = destNePk
    if destTunnelId is not None:
        query_params["destTunnelId"] = destTunnelId
    if destTunnelAlias is not None:
        query_params["destTunnelAlias"] = destTunnelAlias
    if operStatus is not None:
        query_params["operStatus"] = operStatus
    if adminStatus is not None:
        query_params["adminStatus"] = adminStatus
    if remoteIdState is not None:
        query_params["remoteIdState"] = remoteIdState
    if fecStatus is not None:
        query_params["fecStatus"] = fecStatus
    if fecRatio is not None:
        query_params["fecRatio"] = fecRatio
    if children is not None:
        query_params["children"] = children
    return await edgeconnect_request(
        ctx,
        "GET",
        "/tunnels2/bonded",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_tunnels2_bonded_tunnels_with_physical_tunnel",
    description="GET /tunnels2/bondedTunnelsWithPhysicalTunnel\n\ngetBondedTunnelsWithPhysicalTunnels892\n\nGet bonded tunnels containing a specific physical tunnel",
    capability=Capability.READ,
)
async def edgeconnect_get_tunnels2_bonded_tunnels_with_physical_tunnel(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    physicalTunnelId: Annotated[
        str,
        Field(
            description="Physical tunnel ID to search for. Returns all bonded tunnels containing this physical tunnel as a child."
        ),
    ],
    state: Annotated[
        str | None,
        Field(
            default=None,
            description="Regular expression to filter results by tunnel operational state. Case-insensitive partial match against operStatus field.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if physicalTunnelId is not None:
        query_params["physicalTunnelId"] = physicalTunnelId
    if state is not None:
        query_params["state"] = state
    return await edgeconnect_request(
        ctx,
        "GET",
        "/tunnels2/bondedTunnelsWithPhysicalTunnel",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_tunnels_bonded_config_get_batch",
    description="POST /tunnels/bonded/config/getBatch\n\ngetBondedTunnelConfigBatch\n\nRetrieve batch of bonded tunnel configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels_bonded_config_get_batch(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[list[Any], Field(description="Request body (required)")],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="Data source selector. When 'true', retrieves data from Orchestrator cache. When 'false', fetches directly from the appliance.",
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
        "POST",
        "/tunnels/bonded/config/getBatch",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_tunnels_bonded_state",
    description="POST /tunnels/bonded/state\n\ngetBondedTunnelsStates880\n\nGet bonded tunnel state from multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels_bonded_state(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    state: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter tunnels by operational state. Uses case-insensitive regex pattern matching against the 'oper' field. Common values: 'Up', 'Down', 'Active'.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if state is not None:
        query_params["state"] = state
    return await edgeconnect_request(
        ctx,
        "POST",
        "/tunnels/bonded/state",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_tunnels_bonded_state_get_batch",
    description="POST /tunnels/bonded/state/getBatch\n\ngetBondedTunnelStateBatch\n\nRetrieve bonded tunnel states in batch",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels_bonded_state_get_batch(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[list[Any], Field(description="Request body (required)")],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="Data source flag. When 'true', retrieves from GMS cache. When 'false' or omitted, retrieves directly from the appliance.",
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
        "POST",
        "/tunnels/bonded/state/getBatch",
        query_params=query_params or None,
        body=body,
    )
