"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``fastWsFailover``
Operations in this file: 6
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_fast_ws_failover_failover_mode_on_appliance",
    description="GET /fastWsFailover/failoverModeOnAppliance\n\nfastWsFailoverModeOnAppliance\n\nGet WebSocket failover mode per appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_fast_ws_failover_failover_mode_on_appliance(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/fastWsFailover/failoverModeOnAppliance",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_fast_ws_failover_last_message_received",
    description="GET /fastWsFailover/lastMessageReceived\n\nfastWsFailoverLastMessageReceived1\n\nGet last message received timestamp per appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_fast_ws_failover_last_message_received(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/fastWsFailover/lastMessageReceived",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_fast_ws_failover_mode",
    description="GET /fastWsFailover/mode\n\nfastWsFailoverModeGetResponse\n\nGet all WebSocket failover modes",
    capability=Capability.READ,
)
async def edgeconnect_get_fast_ws_failover_mode(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/fastWsFailover/mode",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_fast_ws_failover_mode_active",
    description="GET /fastWsFailover/mode/active\n\nfastWsFailoverActiveGetResponse\n\nGet active WebSocket failover mode",
    capability=Capability.READ,
)
async def edgeconnect_get_fast_ws_failover_mode_active(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/fastWsFailover/mode/active",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_fast_ws_failover_portal_redirection",
    description="GET /fastWsFailover/portalRedirection\n\nfastWsFailoverRedirectionGetResponse\n\nGet appliances redirected to portal WebSocket",
    capability=Capability.READ,
)
async def edgeconnect_get_fast_ws_failover_portal_redirection(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/fastWsFailover/portalRedirection",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_fast_ws_failover_mode_active",
    description="POST /fastWsFailover/mode/active\n\nfastWsFailoverActivePost\n\nChange active WebSocket failover mode",
    capability=Capability.WRITE,
)
async def edgeconnect_post_fast_ws_failover_mode_active(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/fastWsFailover/mode/active",
        query_params=None,
        body=body,
    )
