"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``thirdPartyTunnelsConfiguration``
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
    name="edgeconnect_get_tunnels2_pass_through",
    description="GET /tunnels2/passThrough\n\nsearchAllPassThroughTunnels894\n\nSearch and retrieve pass-through tunnels",
    capability=Capability.READ,
)
async def edgeconnect_get_tunnels2_pass_through(
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
            description="Specific pass-through tunnel ID. Must be used with nePk to retrieve a single tunnel.",
        ),
    ] = None,
    matchingAlias: Annotated[
        str | None,
        Field(
            default=None,
            description="Case-insensitive substring filter for tunnel alias. Returns tunnels where alias contains this string.",
        ),
    ] = None,
    matchingService: Annotated[
        str | None,
        Field(
            default=None,
            description="Case-insensitive substring filter for tunnel peer/service name. Returns tunnels where peerName contains this string.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of tunnels to return. Default is 100 when nePk is provided. Use to limit response size.",
        ),
    ] = None,
    state: Annotated[
        str | None,
        Field(
            default=None,
            description="Regex pattern to filter tunnels by operational status (operStatus). Case-insensitive matching.",
        ),
    ] = None,
    id: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, include only the 'id' field in response objects. Used for field selection.",
        ),
    ] = None,
    alias: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, include only the 'alias' field in response objects. The alias is the tunnel name shown in the UI.",
        ),
    ] = None,
    tag: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, include only the 'tag' field in response objects. The tag is the internal overlay name for the tunnel.",
        ),
    ] = None,
    srcNePk: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, include only the 'srcNePk' field in response objects. Identifies the source appliance.",
        ),
    ] = None,
    destNePk: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, include only the 'destNePk' field in response objects. Identifies the destination appliance (if applicable).",
        ),
    ] = None,
    destTunnelId: Annotated[
        bool | None,
        Field(default=None, description="When true, include only the 'destTunnelId' field in response objects."),
    ] = None,
    destTunnelAlias: Annotated[
        bool | None,
        Field(default=None, description="When true, include only the 'destTunnelAlias' field in response objects."),
    ] = None,
    operStatus: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, include only the 'operStatus' field in response objects. Shows current operational state (Up/Down).",
        ),
    ] = None,
    adminStatus: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, include only the 'adminStatus' field in response objects. Shows administrative state.",
        ),
    ] = None,
    remoteIdState: Annotated[
        bool | None,
        Field(default=None, description="When true, include only the 'remoteIdState' field in response objects."),
    ] = None,
    fecStatus: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, include only the 'fecStatus' field in response objects. Shows Forward Error Correction status.",
        ),
    ] = None,
    fecRatio: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, include only the 'fecRatio' field in response objects. Shows FEC ratio value.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if tunnelId is not None:
        query_params["tunnelId"] = tunnelId
    if matchingAlias is not None:
        query_params["matchingAlias"] = matchingAlias
    if matchingService is not None:
        query_params["matchingService"] = matchingService
    if limit is not None:
        query_params["limit"] = limit
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
        "/tunnels2/passThrough",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_tunnels_pass_through_config_get_batch",
    description="POST /tunnels/passThrough/config/getBatch\n\ngetPassThroughTunnelConfigBatch\n\nRetrieve batch of pass-through tunnel configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels_pass_through_config_get_batch(
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
            description="Data retrieval mode. When 'true', retrieves data from Orchestrator cache. When 'false', fetches directly from the appliance.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "POST",
        "/tunnels/passThrough/config/getBatch",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_tunnels_pass_through_state_get_batch",
    description="POST /tunnels/passThrough/state/getBatch\n\ngetPassThroughTunnelStateBatch\n\nRetrieve batch of pass-through tunnel states",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels_pass_through_state_get_batch(
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
            description="Controls data source: 'true' retrieves from Orchestrator cache (faster), 'false' fetches real-time data from the appliance (slower but current).",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "POST",
        "/tunnels/passThrough/state/getBatch",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_tunnels_third_party_state",
    description="POST /tunnels/thirdParty/state\n\ngetThirdPartyTunnelsStates887\n\nGet third-party tunnel states from multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tunnels_third_party_state(
    ctx: Context,
    state: Annotated[
        str | None,
        Field(
            default=None,
            description="Regular expression pattern to filter tunnels by operational state. Matches against the 'oper' field using case-insensitive partial matching.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if state is not None:
        query_params["state"] = state
    return await edgeconnect_request(
        ctx,
        "POST",
        "/tunnels/thirdParty/state",
        query_params=query_params or None,
        body=body,
    )
