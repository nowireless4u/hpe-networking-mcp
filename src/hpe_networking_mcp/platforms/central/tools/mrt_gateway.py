"""Aruba Central gateway + cluster monitoring tools.

Wraps ``network-monitoring/v1`` gateway and cluster endpoints beyond the
existing ``central_get_gateway_details`` and ``central_get_gateway_*``
stats wrappers. Trend endpoints are consolidated via ``dimension``
enums per sub-resource (top-level, port, tunnel, uplink) — matches
the pattern used in ``mrt_ap.py``.
"""

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command


async def _get(conn, path: str, params: dict | None = None) -> dict | str:
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=path,
        api_params=params or {},
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


def _time_params(start: str | None, end: str | None) -> dict:
    params: dict = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    return params


# ---------------------------------------------------------------------------
# Gateways list + top-level trends
# ---------------------------------------------------------------------------


@tool(capability=Capability.READ)
async def central_get_gateways(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List gateways across the tenant (network-monitoring view)."""
    conn = get_central_conn(ctx)
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return await _get(conn, "network-monitoring/v1/gateways", params)


_GwTrendDimension = Literal["cpu", "memory", "hardware-temperature", "wan-availability", "vpn-availability"]


@tool(capability=Capability.READ)
async def central_get_gateway_trend(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    dimension: Annotated[
        _GwTrendDimension,
        Field(
            description=(
                "Trend dimension: ``'cpu'``, ``'memory'``, "
                "``'hardware-temperature'``, ``'wan-availability'``, or "
                "``'vpn-availability'``."
            ),
        ),
    ],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get one of a gateway's top-level time-series trends."""
    suffix_map = {
        "cpu": "cpu-utilization-trends",
        "memory": "memory-utilization-trends",
        "hardware-temperature": "hardware-temperature-trends",
        "wan-availability": "wan-availability-trends",
        "vpn-availability": "vpn-availability-trends",
    }
    conn = get_central_conn(ctx)
    return await _get(
        conn,
        f"network-monitoring/v1/gateways/{path_seg(serial_number)}/{path_seg(suffix_map[dimension])}",
        _time_params(start, end),
    )


# ---------------------------------------------------------------------------
# Ports + port trends
# ---------------------------------------------------------------------------


@tool(capability=Capability.READ)
async def central_get_gateway_ports(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
) -> dict | str:
    """List ports on a gateway."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/gateways/{path_seg(serial_number)}/ports")


@tool(capability=Capability.READ)
async def central_get_gateway_port(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    port_number: Annotated[str, Field(description="Port number / name.")],
) -> dict | str:
    """Get one gateway-port's detail."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/gateways/{path_seg(serial_number)}/ports/{path_seg(port_number)}")


_GwPortTrendDimension = Literal["throughput", "frames", "frames-errors", "frames-packets"]


@tool(capability=Capability.READ)
async def central_get_gateway_port_trend(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    port_number: Annotated[str, Field(description="Port number / name.")],
    dimension: Annotated[
        _GwPortTrendDimension,
        Field(
            description="Per-port dimension: ``'throughput'``, ``'frames'``, ``'frames-errors'``, ``'frames-packets'``."
        ),
    ],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get one of a gateway-port's time-series trends."""
    suffix_map = {
        "throughput": "throughput-trends",
        "frames": "frames-trends",
        "frames-errors": "frames-errors-trends",
        "frames-packets": "frames-packets-trends",
    }
    conn = get_central_conn(ctx)
    return await _get(
        conn,
        f"network-monitoring/v1/gateways/{path_seg(serial_number)}/ports/"
        f"{path_seg(port_number)}/{path_seg(suffix_map[dimension])}",
        _time_params(start, end),
    )


# ---------------------------------------------------------------------------
# Tunnels + tunnel trends + tunnel-health summaries
# ---------------------------------------------------------------------------


@tool(capability=Capability.READ)
async def central_get_gateway_tunnels(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
) -> dict | str:
    """List active tunnels terminating on a gateway."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/gateways/{path_seg(serial_number)}/tunnels")


@tool(capability=Capability.READ)
async def central_get_gateway_tunnel(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    tunnel_name: Annotated[str, Field(description="Tunnel identifier.")],
) -> dict | str:
    """Get one tunnel's detail on a gateway."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/gateways/{path_seg(serial_number)}/tunnels/{path_seg(tunnel_name)}")


_GwTunnelTrendDimension = Literal["throughput", "status", "dropped-packet"]


@tool(capability=Capability.READ)
async def central_get_gateway_tunnel_trend(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    tunnel_name: Annotated[str, Field(description="Tunnel identifier.")],
    dimension: Annotated[
        _GwTunnelTrendDimension,
        Field(description="Per-tunnel dimension: ``'throughput'``, ``'status'``, or ``'dropped-packet'``."),
    ],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get one of a gateway-tunnel's time-series trends."""
    suffix_map = {
        "throughput": "throughput-trends",
        "status": "status-trends",
        "dropped-packet": "dropped-packet-trends",
    }
    conn = get_central_conn(ctx)
    return await _get(
        conn,
        f"network-monitoring/v1/gateways/{path_seg(serial_number)}/tunnels/"
        f"{path_seg(tunnel_name)}/{path_seg(suffix_map[dimension])}",
        _time_params(start, end),
    )


_TunnelHealthScope = Literal["lan", "wan"]


@tool(capability=Capability.READ)
async def central_get_gateway_tunnels_health_summary(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    scope: Annotated[
        _TunnelHealthScope,
        Field(description="``'lan'`` (lan-tunnels-health-summary) or ``'wan'`` (wan-tunnels-health-summary)."),
    ],
) -> dict | str:
    """Get tunnel health summary for a gateway (LAN-side or WAN-side rollup)."""
    conn = get_central_conn(ctx)
    return await _get(
        conn,
        f"network-monitoring/v1/gateways/{path_seg(serial_number)}/{path_seg(scope)}-tunnels-health-summary",
    )


# ---------------------------------------------------------------------------
# VLANs
# ---------------------------------------------------------------------------


@tool(capability=Capability.READ)
async def central_get_gateway_vlans_runtime(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
) -> dict | str:
    """List runtime VLANs on a gateway."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/gateways/{path_seg(serial_number)}/vlans")


@tool(capability=Capability.READ)
async def central_get_gateway_vlan_runtime(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    vlan_id: Annotated[str, Field(description="VLAN ID.")],
) -> dict | str:
    """Get one runtime VLAN's detail on a gateway."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/gateways/{path_seg(serial_number)}/vlans/{path_seg(vlan_id)}")


# ---------------------------------------------------------------------------
# Uplinks + probes
# ---------------------------------------------------------------------------


@tool(capability=Capability.READ)
async def central_get_gateway_uplinks(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
) -> dict | str:
    """List uplinks (WAN links) on a gateway."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/gateways/{path_seg(serial_number)}/uplinks")


@tool(capability=Capability.READ)
async def central_get_gateway_uplink(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    link_tag: Annotated[str, Field(description="Uplink tag identifier.")],
) -> dict | str:
    """Get one gateway-uplink's detail."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/gateways/{path_seg(serial_number)}/uplinks/{path_seg(link_tag)}")


_UplinkTrendDimension = Literal["throughput", "wan-compression", "wan-availability"]


@tool(capability=Capability.READ)
async def central_get_gateway_uplink_trend(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    link_tag: Annotated[str, Field(description="Uplink tag identifier.")],
    dimension: Annotated[
        _UplinkTrendDimension,
        Field(description="Per-uplink dimension: ``'throughput'``, ``'wan-compression'``, or ``'wan-availability'``."),
    ],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get one of a gateway-uplink's time-series trends."""
    suffix_map = {
        "throughput": "throughput-trends",
        "wan-compression": "wan-compression-trends",
        "wan-availability": "wan-availability-trends",
    }
    conn = get_central_conn(ctx)
    return await _get(
        conn,
        f"network-monitoring/v1/gateways/{path_seg(serial_number)}/uplinks/"
        f"{path_seg(link_tag)}/{path_seg(suffix_map[dimension])}",
        _time_params(start, end),
    )


@tool(capability=Capability.READ)
async def central_get_gateway_uplink_probes(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    link_tag: Annotated[str, Field(description="Uplink tag identifier.")],
) -> dict | str:
    """List configured uplink probes on a gateway uplink."""
    conn = get_central_conn(ctx)
    return await _get(
        conn,
        f"network-monitoring/v1/gateways/{path_seg(serial_number)}/uplinks/{path_seg(link_tag)}/probes",
    )


@tool(capability=Capability.READ)
async def central_get_gateway_uplink_probe_performance(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    link_tag: Annotated[str, Field(description="Uplink tag identifier.")],
    probe: Annotated[str, Field(description="Probe identifier.")],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get performance trend for one specific uplink probe."""
    conn = get_central_conn(ctx)
    return await _get(
        conn,
        f"network-monitoring/v1/gateways/{path_seg(serial_number)}/uplinks/"
        f"{path_seg(link_tag)}/probes/{path_seg(probe)}/performance-trends",
        _time_params(start, end),
    )


@tool(capability=Capability.READ)
async def central_get_gateway_uplink_vpn_availability(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    vlan_id: Annotated[
        str, Field(description="VLAN ID (note: this uplink-vpn-availability variant indexes by VLAN, not link-tag).")
    ],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get VPN-availability trend for an uplink, indexed by VLAN (per Central's MRT shape).

    Note the endpoint signature differs from the other uplink trends —
    Central uses ``vlan-id`` as the path segment here rather than the
    ``link-tag`` used elsewhere.
    """
    conn = get_central_conn(ctx)
    return await _get(
        conn,
        f"network-monitoring/v1/gateways/{path_seg(serial_number)}/uplinks/{path_seg(vlan_id)}/vpn-availability-trends",
        _time_params(start, end),
    )


# ---------------------------------------------------------------------------
# DHCP (pools + clients)
# ---------------------------------------------------------------------------


_DhcpView = Literal["pools", "clients"]


@tool(capability=Capability.READ)
async def central_get_gateway_dhcp(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    view: Annotated[
        _DhcpView,
        Field(description="``'pools'`` (configured DHCP pools) or ``'clients'`` (active leases)."),
    ],
) -> dict | str:
    """Get DHCP state on a gateway (pools or active client leases)."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/gateways/{path_seg(serial_number)}/dhcp-{path_seg(view)}")


# ---------------------------------------------------------------------------
# Clusters
# ---------------------------------------------------------------------------


@tool(capability=Capability.READ)
async def central_get_cluster_members(
    ctx: Context,
    cluster_name: Annotated[str, Field(description="Cluster name.")],
) -> dict | str:
    """List member gateways of a cluster."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/clusters/{path_seg(cluster_name)}/members")


_ClusterSummaryKind = Literal[
    "vlan-mismatch",
    "connectivity-graph",
    "tunnels",
    "tunnels-health-summary",
    "tunnels-status-summary",
]


@tool(capability=Capability.READ)
async def central_get_cluster_summary(
    ctx: Context,
    cluster_name: Annotated[str, Field(description="Cluster name.")],
    kind: Annotated[
        _ClusterSummaryKind,
        Field(
            description=(
                "Summary kind: ``'vlan-mismatch'`` (cross-member VLAN config drift), "
                "``'connectivity-graph'`` (peer connectivity), ``'tunnels'`` "
                "(cluster-level tunnel list), ``'tunnels-health-summary'`` (rollup), "
                "or ``'tunnels-status-summary'`` (per-tunnel state)."
            ),
        ),
    ],
) -> dict | str:
    """Get one of the cluster-level summary endpoints."""
    conn = get_central_conn(ctx)
    return await _get(conn, f"network-monitoring/v1/clusters/{path_seg(cluster_name)}/{path_seg(kind)}")


@tool(capability=Capability.READ)
async def central_get_cluster_capacity_trends(
    ctx: Context,
    cluster_name: Annotated[str, Field(description="Cluster name.")],
    serial_number: Annotated[
        str | None,
        Field(
            description=(
                "Optional cluster-member serial number. Omit for cluster-wide "
                "rollup; pass a serial to scope the trend to one member."
            ),
        ),
    ] = None,
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get cluster capacity trends (cluster-wide or per-member)."""
    conn = get_central_conn(ctx)
    base = f"network-monitoring/v1/clusters/{path_seg(cluster_name)}/capacity-trends"
    path = f"{base}/{path_seg(serial_number)}" if serial_number else base
    return await _get(conn, path, _time_params(start, end))
