"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``dhcpConfig``
Operations in this file: 21
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
    name="edgeconnect_get_dhcp_config",
    description="GET /dhcpConfig\n\ndhcpConfigGet219\n\nGet global Orchestrator DHCP configuration settings",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/dhcpConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_dhcp_config_dhcp_settings",
    description="GET /dhcpConfig/dhcpSettings\n\ngetDhcpSettings\n\nGet DHCP settings for a specific appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config_dhcp_settings(
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
            description='If "true" or omitted, returns cached data from Orchestrator. Falls back to a direct appliance query if cache is empty. Set to "false" to always query the appliance directly.',
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
        "/dhcpConfig/dhcpSettings",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_dhcp_config_leases",
    description="GET /dhcpConfig/leases\n\ndhcpdLeases221\n\nGet DHCP lease information for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config_leases(
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
            description="Data source selector. When 'true', returns cached lease data from Orchestrator. When 'false', fetches fresh data directly from the appliance.",
        ),
    ] = None,
    maxLease: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of lease records to return. Only applies when cached=false. When cached=true, returns all cached leases.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    if maxLease is not None:
        query_params["maxLease"] = maxLease
    return await edgeconnect_request(
        ctx,
        "GET",
        "/dhcpConfig/leases",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_dhcp_config_profiler",
    description="GET /dhcpConfig/profiler\n\ngetDhcpProfiler\n\nGet DHCP profiler configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config_profiler(
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
            description="Whether to retrieve data from cache or directly from the appliance. Defaults to cache with automatic fallback to appliance if cached data is empty.",
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
        "/dhcpConfig/profiler",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_dhcp_config_relay",
    description="GET /dhcpConfig/relay\n\ngetDhcpRelay\n\nGet DHCP relay configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config_relay(
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
            description="Whether to retrieve data from cache or directly from the appliance. Defaults to cache with automatic fallback to appliance if cached data is empty.",
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
        "/dhcpConfig/relay",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_dhcp_config_remote_subnets",
    description="GET /dhcpConfig/remoteSubnets\n\ngetDhcpRemoteSubnets\n\nGet DHCP remote subnets (address pools)",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config_remote_subnets(
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
            description="Whether to retrieve data from cache or directly from the appliance. Defaults to cache with automatic fallback to appliance if cached data is empty.",
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
        "/dhcpConfig/remoteSubnets",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_dhcp_config_reservation",
    description="GET /dhcpConfig/reservation\n\ngetDhcpReservation\n\nGet DHCP reservation configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config_reservation(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Appliance identifier assigned by Orchestrator (e.g., '0.NE'). Required — returns 400 if missing or empty."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="When omitted or 'true', reads from Orchestrator cache first; falls back to a direct appliance query if the cache is empty. Set to 'false' to always query the appliance directly.",
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
        "/dhcpConfig/reservation",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_dhcp_config_reservations",
    description="GET /dhcpConfig/reservations\n\ndhcpReservationsGet222\n\nGet list of reserved subnets from the DHCP pool",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config_reservations(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/dhcpConfig/reservations",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_dhcp_config_scope",
    description="GET /dhcpConfig/scope\n\ngetDhcpScope\n\nGet DHCP scope utilization",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config_scope(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Appliance identifier assigned by Orchestrator (e.g., '0.NE'). Required — returns 400 if missing or empty."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="When omitted or 'true', reads from Orchestrator cache first; falls back to a direct appliance query if the cache is empty. Set to 'false' to always query the appliance directly.",
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
        "/dhcpConfig/scope",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_dhcp_config_service",
    description="GET /dhcpConfig/service\n\ngetDhcpService\n\nGet DHCP service status",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config_service(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Appliance identifier assigned by Orchestrator (e.g., '0.NE'). Required — returns 400 if missing or empty."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="When omitted or 'true', reads from Orchestrator cache first; falls back to a direct appliance query if the cache is empty. Set to 'false' to always query the appliance directly.",
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
        "/dhcpConfig/service",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_dhcp_config_state_failover",
    description="GET /dhcpConfig/state/failover\n\ndhcpdFailoverStates226\n\nGet DHCP failover state information for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config_state_failover(
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
            description="Data source selector. When 'true' or omitted, returns cached failover state from Orchestrator. When 'false', fetches fresh data directly from the appliance.",
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
        "/dhcpConfig/state/failover",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_dhcp_config_utilization_threshold",
    description="GET /dhcpConfig/utilizationThreshold\n\ngetDhcpUtilizationThreshold\n\nGet DHCP scope utilization threshold",
    capability=Capability.READ,
)
async def edgeconnect_get_dhcp_config_utilization_threshold(
    ctx: Context,
    nePk: Annotated[str, Field(description="Appliance primary key, e.g. '0.NE'. Must not be empty.")],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="If 'true' or omitted, returns cached data with automatic fallback to live query when cache is empty. Set to 'false' to force a live query.",
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
        "/dhcpConfig/utilizationThreshold",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_dhcp_config",
    description="POST /dhcpConfig\n\ndhcpConfigPost220\n\nSave global Orchestrator DHCP configuration settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_dhcp_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/dhcpConfig",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_dhcp_config_dhcp_settings",
    description="POST /dhcpConfig/dhcpSettings\n\npostDhcpSettings\n\nUpdate DHCP settings on a specific appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_dhcp_config_dhcp_settings(
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
        "/dhcpConfig/dhcpSettings",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_dhcp_config_profiler",
    description="POST /dhcpConfig/profiler\n\npostDhcpProfiler\n\nUpdate DHCP profiler configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_dhcp_config_profiler(
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
        "/dhcpConfig/profiler",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_dhcp_config_remote_subnets",
    description="POST /dhcpConfig/remoteSubnets\n\npostDhcpRemoteSubnets\n\nUpdate DHCP remote subnets (address pools)",
    capability=Capability.WRITE,
)
async def edgeconnect_post_dhcp_config_remote_subnets(
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
        "/dhcpConfig/remoteSubnets",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_dhcp_config_reservation",
    description="POST /dhcpConfig/reservation\n\npostDhcpReservation\n\nUpdate DHCP reservation configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_dhcp_config_reservation(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Appliance identifier assigned by Orchestrator (e.g., '0.NE'). Required — returns 400 if missing or empty."
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
        "/dhcpConfig/reservation",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_dhcp_config_reservations",
    description="POST /dhcpConfig/reservations\n\ndhcpReservationsPost223\n\nReserve a subnet in the DHCP pool",
    capability=Capability.WRITE,
)
async def edgeconnect_post_dhcp_config_reservations(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
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
        "POST",
        "/dhcpConfig/reservations",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_dhcp_config_reservations_gms",
    description="POST /dhcpConfig/reservations/gms\n\ndhcpReservationsGmsPost224\n\nUpdate Orchestrator DHCP pool reservations list",
    capability=Capability.WRITE,
)
async def edgeconnect_post_dhcp_config_reservations_gms(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/dhcpConfig/reservations/gms",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_dhcp_config_reset",
    description="POST /dhcpConfig/reset\n\ndhcpConfigResetPost225\n\nReset DHCP pool reservations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_dhcp_config_reset(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/dhcpConfig/reset",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_dhcp_config_utilization_threshold",
    description="POST /dhcpConfig/utilizationThreshold\n\npostDhcpUtilizationThreshold\n\nUpdate DHCP scope utilization threshold",
    capability=Capability.WRITE,
)
async def edgeconnect_post_dhcp_config_utilization_threshold(
    ctx: Context,
    nePk: Annotated[str, Field(description="Appliance primary key, e.g. '0.NE'. Must not be empty.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/dhcpConfig/utilizationThreshold",
        query_params=query_params or None,
        body=body,
    )
