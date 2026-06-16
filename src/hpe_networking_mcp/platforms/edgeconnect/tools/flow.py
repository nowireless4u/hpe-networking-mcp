"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``flow``
Operations in this file: 8
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
    name="edgeconnect_get_flow",
    description="GET /flow\n\nflows242\n\nRetrieve active, inactive, or all flows from an appliance with optional filtering",
    capability=Capability.READ,
)
async def edgeconnect_get_flow(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    maxFlows: Annotated[
        int,
        Field(
            description="Maximum number of flows to return. Hard limit prevents excessive data retrieval from appliances."
        ),
    ],
    ip1: Annotated[
        str | None,
        Field(
            default=None,
            description="First IP endpoint for filtering flows. Supports IPv4 and IPv6 addresses. Used with mask1 for subnet filtering.",
        ),
    ] = None,
    mask1: Annotated[
        int | None,
        Field(
            default=None,
            description="CIDR subnet mask for ip1. Defines the network prefix length for filtering (e.g., 24 for /24 subnet).",
        ),
    ] = None,
    port1: Annotated[
        int | None,
        Field(
            default=None,
            description="Port number for the first IP endpoint. Used to filter flows by source or destination port depending on portEitherFlag.",
        ),
    ] = None,
    ip2: Annotated[
        str | None,
        Field(
            default=None,
            description="Second IP endpoint for filtering flows. Supports IPv4 and IPv6 addresses. Used with mask2 for subnet filtering.",
        ),
    ] = None,
    mask2: Annotated[
        int | None,
        Field(
            default=None,
            description="CIDR subnet mask for ip2. Defines the network prefix length for filtering (e.g., 24 for /24 subnet).",
        ),
    ] = None,
    port2: Annotated[
        int | None,
        Field(
            default=None,
            description="Port number for the second IP endpoint. Used to filter flows by source or destination port depending on portEitherFlag.",
        ),
    ] = None,
    ipEitherFlag: Annotated[
        bool | None,
        Field(
            default=None,
            description="Controls IP directionality matching. When true (default), ip1/ip2 can match either source or destination. When false, ip1 is source and ip2 is destination.",
        ),
    ] = None,
    portEitherFlag: Annotated[
        bool | None,
        Field(
            default=None,
            description="Controls port directionality matching. When true (default), port1/port2 can match either source or destination. When false, port1 is source and port2 is destination.",
        ),
    ] = None,
    vrf1: Annotated[
        str | None,
        Field(
            default=None,
            description="VRF (Virtual Routing and Forwarding) ID for ip1 endpoint. Use '0' for default VRF or specify a custom VRF ID.",
        ),
    ] = None,
    vrf2: Annotated[
        str | None,
        Field(
            default=None,
            description="VRF (Virtual Routing and Forwarding) ID for ip2 endpoint. Use '0' for default VRF or specify a custom VRF ID.",
        ),
    ] = None,
    vrfEither: Annotated[
        str | None,
        Field(
            default=None,
            description="VRF ID for bidirectional matching. Matches flows with this VRF as either source or destination. Use 'any' for all VRFs, '0' for default.",
        ),
    ] = None,
    application: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by specific application traffic type. Only shows built-in applications; user-defined applications not listed in dropdown.",
        ),
    ] = None,
    applicationGroup: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by application group category. Shows subset of available application groups for classification-based filtering.",
        ),
    ] = None,
    protocol: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by network protocol. Supports common transport and tunneling protocols for granular traffic analysis.",
        ),
    ] = None,
    vlan: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by VLAN ID. Constrains results to flows associated with a specific Virtual LAN.",
        ),
    ] = None,
    dscp: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by DSCP (Differentiated Services Code Point) marking. Use 'any' for all DSCP values or specify a specific DSCP value.",
        ),
    ] = None,
    overlays: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by overlay ID(s). Multiple values separated by '|' (e.g., '1|2'). Useful for multi-overlay deployments.",
        ),
    ] = None,
    transport: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by transport type. Values: 'fabric' (SD-WAN), 'underlay', 'breakout'. Multiple values separated by '|' (e.g., 'fabric|underlay').",
        ),
    ] = None,
    services: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="Filter by service name(s). Third-party services use '*' suffix for prefix matching. Multiple services separated by '|' (e.g., 'Zscaler_*|PaloAlto').",
        ),
    ] = None,
    zone1: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter flows destined to specified zone. Use 'any' for all zones, '0' for default zone, or specific zone_id.",
        ),
    ] = None,
    zone2: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter flows originating from specified zone. Use 'any' for all zones, '0' for default zone, or specific zone_id.",
        ),
    ] = None,
    zoneEither: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter flows involving specified zone bidirectionally (either source or destination). Use 'any' for all zones, '0' for default.",
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by flow category/state. 'all' returns all flows; other values filter specific flow types based on optimization status or drop reason.",
        ),
    ] = None,
    edgeHA: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include or exclude Edge HA (High Availability) flows. Set true to include HA synchronization traffic.",
        ),
    ] = None,
    builtIn: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include or exclude built-in policy flows (system-generated flows). Set true to include internal management traffic.",
        ),
    ] = None,
    uptime: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by flow timing/activity state. Defaults to 'anytime' + 'term' if not specified. 'last' prefix = active within period; 'term' prefix = ended within period.",
        ),
    ] = None,
    bytes: Annotated[
        str | None,
        Field(
            default=None,
            description="Byte count reporting mode. 'total' = lifetime bytes; 'last5m' = bytes in last 5 minutes for active flow analysis.",
        ),
    ] = None,
    duration: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by flow duration in minutes. Use 'any' for all, or '<N' / '>N' format (e.g., '>5000' for flows lasting more than 5000 minutes).",
        ),
    ] = None,
    anytimeSlowFlows: Annotated[
        str | None,
        Field(
            default=None,
            description="When present (any value), filters to show only slow TCP flows. Useful for diagnosing performance issues.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if ip1 is not None:
        query_params["ip1"] = ip1
    if mask1 is not None:
        query_params["mask1"] = mask1
    if port1 is not None:
        query_params["port1"] = port1
    if ip2 is not None:
        query_params["ip2"] = ip2
    if mask2 is not None:
        query_params["mask2"] = mask2
    if port2 is not None:
        query_params["port2"] = port2
    if ipEitherFlag is not None:
        query_params["ipEitherFlag"] = ipEitherFlag
    if portEitherFlag is not None:
        query_params["portEitherFlag"] = portEitherFlag
    if vrf1 is not None:
        query_params["vrf1"] = vrf1
    if vrf2 is not None:
        query_params["vrf2"] = vrf2
    if vrfEither is not None:
        query_params["vrfEither"] = vrfEither
    if application is not None:
        query_params["application"] = application
    if applicationGroup is not None:
        query_params["applicationGroup"] = applicationGroup
    if protocol is not None:
        query_params["protocol"] = protocol
    if vlan is not None:
        query_params["vlan"] = vlan
    if dscp is not None:
        query_params["dscp"] = dscp
    if overlays is not None:
        query_params["overlays"] = overlays
    if transport is not None:
        query_params["transport"] = transport
    if services is not None:
        query_params["services"] = services
    if zone1 is not None:
        query_params["zone1"] = zone1
    if zone2 is not None:
        query_params["zone2"] = zone2
    if zoneEither is not None:
        query_params["zoneEither"] = zoneEither
    if filter is not None:
        query_params["filter"] = filter
    if edgeHA is not None:
        query_params["edgeHA"] = edgeHA
    if builtIn is not None:
        query_params["builtIn"] = builtIn
    if uptime is not None:
        query_params["uptime"] = uptime
    if bytes is not None:
        query_params["bytes"] = bytes
    if duration is not None:
        query_params["duration"] = duration
    if maxFlows is not None:
        query_params["maxFlows"] = maxFlows
    if anytimeSlowFlows is not None:
        query_params["anytimeSlowFlows"] = anytimeSlowFlows
    return await edgeconnect_request(
        ctx,
        "GET",
        "/flow",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_flow_flow_bandwidth_stats",
    description="GET /flow/flowBandwidthStats\n\nflowBandwidthStats237\n\nGet flow bandwidth statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_flow_flow_bandwidth_stats(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    id: Annotated[
        int,
        Field(
            description="Flow identifier (spId) that uniquely identifies a specific flow on the appliance. Obtained from the flow list endpoint."
        ),
    ],
    seq: Annotated[
        int,
        Field(
            description="Flow sequence number used to differentiate flow instances when a flow is reset or restarted. Must match the current sequence number for the flow."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if id is not None:
        query_params["id"] = id
    if seq is not None:
        query_params["seq"] = seq
    return await edgeconnect_request(
        ctx,
        "GET",
        "/flow/flowBandwidthStats",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_flow_flow_details",
    description="GET /flow/flowDetails\n\nflowDetails238\n\nReturns detailed flow information",
    capability=Capability.READ,
)
async def edgeconnect_get_flow_flow_details(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    id: Annotated[int, Field(description="Unique flow identifier. Obtained from the flow list endpoint (/flow).")],
    seq: Annotated[
        int,
        Field(
            description="Flow sequence number used to track flow state changes. Obtained from the flow list endpoint."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if id is not None:
        query_params["id"] = id
    if seq is not None:
        query_params["seq"] = seq
    return await edgeconnect_request(
        ctx,
        "GET",
        "/flow/flowDetails",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_flow_flow_details2",
    description="GET /flow/flowDetails2\n\nflowDetails2239\n\nGet detailed flow information",
    capability=Capability.READ,
)
async def edgeconnect_get_flow_flow_details2(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    id: Annotated[
        int,
        Field(
            description="Flow ID identifying the specific network flow. Must be a positive integer uniquely identifying the flow on the appliance."
        ),
    ],
    seq: Annotated[
        int,
        Field(
            description="Flow sequence number for versioning or ordering of flow records. Must be a positive integer."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if id is not None:
        query_params["id"] = id
    if seq is not None:
        query_params["seq"] = seq
    return await edgeconnect_request(
        ctx,
        "GET",
        "/flow/flowDetails2",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_flow_flow_optimization",
    description="GET /flow/flowOptimization\n\ngetFlowOptimization\n\nGet flow optimization details",
    capability=Capability.READ,
)
async def edgeconnect_get_flow_flow_optimization(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    id: Annotated[
        int,
        Field(
            description="Flow identifier used to uniquely identify a specific flow on the appliance. Obtain this value from the /flow endpoint."
        ),
    ],
    seq: Annotated[
        int,
        Field(
            description="Flow sequence identifier distinguishing between multiple instances of the same flow. Used together with 'id' to uniquely identify a flow."
        ),
    ],
    ignore: Annotated[
        int,
        Field(
            description="Controls whether to suppress or show flow warnings. Set to 1 to ignore warnings, 0 to show warnings."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if id is not None:
        query_params["id"] = id
    if seq is not None:
        query_params["seq"] = seq
    if ignore is not None:
        query_params["ignore"] = ignore
    return await edgeconnect_request(
        ctx,
        "GET",
        "/flow/flowOptimization",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_flow_flow_re_classification",
    description="POST /flow/flowReClassification\n\nflowsReclassification240\n\nReclassify network flows",
    capability=Capability.WRITE,
)
async def edgeconnect_post_flow_flow_re_classification(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/flow/flowReClassification",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_flow_flow_reset",
    description="POST /flow/flowReset\n\nflowsReset241\n\nReset flows on an appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_flow_flow_reset(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/flow/flowReset",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_flow_flow_warning",
    description="POST /flow/flowWarning\n\nignoreFlowWarning\n\nEnable or disable flow warning alerts",
    capability=Capability.WRITE,
)
async def edgeconnect_post_flow_flow_warning(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/flow/flowWarning",
        query_params=query_params or None,
        body=body,
    )
