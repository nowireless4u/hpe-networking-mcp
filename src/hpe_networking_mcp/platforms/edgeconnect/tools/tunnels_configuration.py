"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``tunnelsConfiguration``
Operations in this file: 10
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
    name="edgeconnect_get_tunnels2",
    description="GET /tunnels2\n\ngetTunnels2MetaData\n\nGet total tunnel count metadata",
    capability=Capability.READ,
)
async def edgeconnect_get_tunnels2(
    ctx: Context,
    metaData: Annotated[
        bool | None,
        Field(
            default=None,
            description="Flag to request tunnel metadata. Must be true to retrieve tunnel count data. If false or omitted, returns 204 No Content.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if metaData is not None:
        query_params["metaData"] = metaData
    return await edgeconnect_request(
        ctx,
        "GET",
        "/tunnels2",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_tunnels2_physical",
    description="GET /tunnels2/physical\n\ngetPhysicalTunnels\n\nSearch physical tunnels across appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_tunnels2_physical(
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
            description="Tunnel identifier. When combined with nePk, returns a specific tunnel. Ignored if nePk is not provided.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of tunnels to return. Applied when iterating through all appliances or a single appliance's tunnels.",
        ),
    ] = None,
    matchingAlias: Annotated[
        str | None,
        Field(
            default=None,
            description="Case-insensitive substring match on tunnel alias. Filters tunnels whose alias contains this string.",
        ),
    ] = None,
    state: Annotated[
        str | None,
        Field(
            default=None,
            description="Regex pattern to match tunnel operational status (operStatus). Case-insensitive matching is applied.",
        ),
    ] = None,
    id: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include only the 'id' field in response when true. Used for selective field retrieval.",
        ),
    ] = None,
    alias: Annotated[
        bool | None,
        Field(default=None, description="Include only the 'alias' field (tunnel display name) in response when true."),
    ] = None,
    tag: Annotated[
        bool | None,
        Field(default=None, description="Include only the 'tag' field (overlay name) in response when true."),
    ] = None,
    srcNePk: Annotated[
        bool | None,
        Field(
            default=None, description="Include only the 'srcNePk' field (source appliance nePk) in response when true."
        ),
    ] = None,
    destNePk: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include only the 'destNePk' field (destination appliance nePk) in response when true.",
        ),
    ] = None,
    destTunnelId: Annotated[
        bool | None,
        Field(
            default=None, description="Include only the 'destTunnelId' field (remote tunnel ID) in response when true."
        ),
    ] = None,
    destTunnelAlias: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include only the 'destTunnelAlias' field (remote tunnel alias) in response when true.",
        ),
    ] = None,
    operStatus: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include only the 'operStatus' field (current operational state) in response when true.",
        ),
    ] = None,
    adminStatus: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include only the 'adminStatus' field (administrative state) in response when true.",
        ),
    ] = None,
    remoteIdState: Annotated[
        bool | None, Field(default=None, description="Include only the 'remoteIdState' field in response when true.")
    ] = None,
    fecStatus: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include only the 'fecStatus' field (Forward Error Correction status) in response when true.",
        ),
    ] = None,
    fecRatio: Annotated[
        bool | None,
        Field(default=None, description="Include only the 'fecRatio' field (FEC ratio value) in response when true."),
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
    return await edgeconnect_request(
        ctx,
        "GET",
        "/tunnels2/physical",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_tunnels_physical_tunnel_ids",
    description="GET /tunnels/physical/tunnelIds\n\ngetPhysicalTunnelIds\n\nGet physical tunnel IDs for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_tunnels_physical_tunnel_ids(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    state: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter tunnels by operational state. Uses case-insensitive partial matching (e.g., 'Up' matches 'Up - Active').",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if state is not None:
        query_params["state"] = state
    return await edgeconnect_request(
        ctx,
        "GET",
        "/tunnels/physical/tunnelIds",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_tunnels2_get_tunnels_between_appliances",
    description="POST /tunnels2/getTunnelsBetweenAppliances\n\nGetTunnelsBetweenAppliances893\n\nGet tunnels between appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels2_get_tunnels_between_appliances(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of tunnels to return. Limits the result set size for pagination or performance optimization.",
        ),
    ] = None,
    matchingAlias: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter tunnels by alias using case-insensitive substring matching. Only tunnels containing this text in their alias are returned.",
        ),
    ] = None,
    overlayId: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by overlay type: '0' for physical tunnels only, 'all' for all bonded tunnels, or a specific overlay ID integer for tunnels in that overlay.",
        ),
    ] = None,
    includePassThrough: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include pass-through tunnels in results. Only effective when overlayId is null or '0'. Pass-through tunnels connect to third-party services.",
        ),
    ] = None,
    state: Annotated[
        str | None,
        Field(
            default=None,
            description="Regex pattern to filter tunnels by operational state. Matches against tunnel 'oper' status (e.g., 'Up', 'Down').",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if matchingAlias is not None:
        query_params["matchingAlias"] = matchingAlias
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    if includePassThrough is not None:
        query_params["includePassThrough"] = includePassThrough
    if state is not None:
        query_params["state"] = state
    return await edgeconnect_request(
        ctx,
        "POST",
        "/tunnels2/getTunnelsBetweenAppliances",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_tunnels2_tunnel_counts",
    description="POST /tunnels2/tunnelCounts\n\ngetTunnelCounts900\n\nGet tunnel counts by overlay type for specified appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels2_tunnel_counts(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/tunnels2/tunnelCounts",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_tunnels_physical_config_get_batch",
    description="POST /tunnels/physical/config/getBatch\n\ngetPhysicalTunnelConfigBatch\n\nRetrieve batch of physical tunnel configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels_physical_config_get_batch(
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
            description="Data source selection. When 'true', retrieves from GMS cache (faster). When 'false', queries the appliance directly (real-time data).",
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
        "/tunnels/physical/config/getBatch",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_tunnels_physical_state",
    description="POST /tunnels/physical/state\n\ngetTunnelStateFromMultipleAppliances\n\nGet physical tunnel state for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels_physical_state(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    state: Annotated[
        str | None,
        Field(
            default=None,
            description="Regex pattern to filter tunnels by operational state (e.g., 'Up', 'Down', 'Up - Active'). Case-insensitive matching is applied.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if state is not None:
        query_params["state"] = state
    return await edgeconnect_request(
        ctx,
        "POST",
        "/tunnels/physical/state",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_tunnels_physical_state_get_batch",
    description="POST /tunnels/physical/state/getBatch\n\ngetPhysicalTunnelStateBatch\n\nRetrieve batch of physical tunnel states",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels_physical_state_get_batch(
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
            description="When 'true', retrieves data from Orchestrator cache. When 'false', fetches directly from the appliance.",
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
        "/tunnels/physical/state/getBatch",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_tunnels_physical_traceroute",
    description="POST /tunnels/physical/traceroute\n\ninitiateTraceroute\n\nInitiate traceroute on a physical tunnel",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels_physical_traceroute(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="Tunnel name/identifier to perform traceroute on. Must match an existing tunnel name in the configuration."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/tunnels/physical/traceroute",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_tunnels_physical_traceroute_state",
    description="POST /tunnels/physical/tracerouteState\n\ngetTunnelTracerouteState\n\nGet traceroute state for a physical tunnel",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels_physical_traceroute_state(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="The unique identifier (name) of the physical tunnel for which to retrieve traceroute state. This corresponds to the tunnel's configured name."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/tunnels/physical/tracerouteState",
        query_params=query_params or None,
        body=body,
    )
