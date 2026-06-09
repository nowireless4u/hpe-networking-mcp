"""Aruba Central AP monitoring tools — entity lists (radios, ports,
tunnels, wlans) plus consolidated trend tools for top-level / radio /
port / tunnel / wlan time-series data.

Trend endpoints are consolidated via a ``dimension`` enum per
sub-resource rather than one tool per metric — matches existing
``central_get_switch_hardware_trends`` pattern.
"""

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import coerce_enum, retry_central_command


def _get(conn, path: str, params: dict | None = None) -> dict | str:
    response = retry_central_command(
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
# AP top-level trends + utility lists
# ---------------------------------------------------------------------------


_ApTrendDimension = Literal["throughput", "cpu", "memory", "power"]


@tool(annotations=READ_ONLY)
async def central_get_ap_trend(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
    dimension: Annotated[
        _ApTrendDimension,
        Field(
            description=(
                "Trend dimension: ``'throughput'``, ``'cpu'`` (cpu-utilization), "
                "``'memory'`` (memory-utilization), or ``'power'`` (power-consumption)."
            ),
        ),
    ],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get one of an AP's top-level time-series trends.

    Consolidates the four trend endpoints under
    ``/aps/:serial/<dim>-trends`` (throughput, cpu-utilization,
    memory-utilization, power-consumption).
    """
    suffix_map = {
        "throughput": "throughput-trends",
        "cpu": "cpu-utilization-trends",
        "memory": "memory-utilization-trends",
        "power": "power-consumption-trends",
    }
    conn = ctx.lifespan_context["central_conn"]
    return _get(
        conn,
        f"network-monitoring/v1/aps/{serial_number}/{suffix_map[dimension]}",
        _time_params(start, end),
    )


# ---------------------------------------------------------------------------
# AP radio entities + radio trends
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_ap_radios(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
) -> dict | str:
    """List the radios on an AP (2.4, 5, 6 GHz typically)."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(conn, f"network-monitoring/v1/aps/{serial_number}/radios")


_RadioTrendDimension = Literal["throughput", "channel-utilization", "channel-quality", "noise-floor", "frames"]


@tool(annotations=READ_ONLY)
async def central_get_ap_radio_trend(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
    radio_number: Annotated[int, Field(description="Radio number (0/1/2 typically).")],
    dimension: Annotated[
        _RadioTrendDimension,
        Field(
            description=(
                "Per-radio trend dimension: ``'throughput'``, ``'channel-utilization'``, "
                "``'channel-quality'``, ``'noise-floor'``, or ``'frames'``."
            ),
        ),
    ],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get one of an AP-radio's time-series trends."""
    suffix_map = {
        "throughput": "throughput-trends",
        "channel-utilization": "channel-utilization-trends",
        "channel-quality": "channel-quality-trends",
        "noise-floor": "noise-floor-trends",
        "frames": "frames-trends",
    }
    conn = ctx.lifespan_context["central_conn"]
    return _get(
        conn,
        f"network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/{suffix_map[dimension]}",
        _time_params(start, end),
    )


# ---------------------------------------------------------------------------
# AP port entities + port trends
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_ap_ports(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
) -> dict | str:
    """List the Ethernet ports on an AP."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(conn, f"network-monitoring/v1/aps/{serial_number}/ports")


_PortTrendDimension = Literal["throughput", "frames", "crc", "collisions"]


@tool(annotations=READ_ONLY)
async def central_get_ap_port_trend(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
    port_index: Annotated[int, Field(description="Port index.")],
    dimension: Annotated[
        _PortTrendDimension,
        Field(description="Per-port trend dimension: ``'throughput'``, ``'frames'``, ``'crc'``, or ``'collisions'``."),
    ],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get one of an AP-port's time-series trends."""
    suffix_map = {
        "throughput": "throughput-trends",
        "frames": "frames-trends",
        "crc": "crc-trends",
        "collisions": "collisions-trends",
    }
    conn = ctx.lifespan_context["central_conn"]
    return _get(
        conn,
        f"network-monitoring/v1/aps/{serial_number}/ports/{port_index}/{suffix_map[dimension]}",
        _time_params(start, end),
    )


# ---------------------------------------------------------------------------
# AP tunnel entities + tunnel trends
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_ap_tunnels(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
) -> dict | str:
    """List active tunnels on an AP."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(conn, f"network-monitoring/v1/aps/{serial_number}/tunnels")


@tool(annotations=READ_ONLY)
async def central_get_ap_tunnel(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
    tunnel_id: Annotated[str, Field(description="Tunnel identifier.")],
) -> dict | str:
    """Get one tunnel's detail on an AP."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(conn, f"network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}")


_TunnelTrendDimension = Literal["throughput", "packet-loss", "mos", "jitter", "latency"]


@tool(annotations=READ_ONLY)
async def central_get_ap_tunnel_trend(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
    tunnel_id: Annotated[str, Field(description="Tunnel identifier.")],
    dimension: Annotated[
        _TunnelTrendDimension,
        Field(
            description=(
                "Per-tunnel trend dimension: ``'throughput'``, ``'packet-loss'``, "
                "``'mos'`` (mean-opinion-score), ``'jitter'``, or ``'latency'``."
            ),
        ),
    ],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get one of an AP-tunnel's time-series trends."""
    suffix_map = {
        "throughput": "throughput-trends",
        "packet-loss": "packet-loss-trends",
        "mos": "mos-trends",
        "jitter": "jitter-trends",
        "latency": "latency-trends",
    }
    conn = ctx.lifespan_context["central_conn"]
    return _get(
        conn,
        f"network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/{suffix_map[dimension]}",
        _time_params(start, end),
    )


# ---------------------------------------------------------------------------
# AP WLAN entities + trend
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_ap_wlans_monitoring(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
) -> dict | str:
    """List WLANs an AP is broadcasting (monitoring view).

    Distinct from the existing ``central_get_ap_wlans`` which may route
    through a different code path; this hits the
    ``/aps/:serial/wlans`` endpoint directly.
    """
    conn = ctx.lifespan_context["central_conn"]
    return _get(conn, f"network-monitoring/v1/aps/{serial_number}/wlans")


@tool(annotations=READ_ONLY)
async def central_get_ap_wlan_throughput(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
    wlan_name: Annotated[str, Field(description="WLAN / SSID name.")],
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
) -> dict | str:
    """Get throughput trend for one WLAN as broadcast by one AP."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(
        conn,
        f"network-monitoring/v1/aps/{serial_number}/wlans/{wlan_name}/throughput-trends",
        _time_params(start, end),
    )


# ---------------------------------------------------------------------------
# Top-N APs by usage
# ---------------------------------------------------------------------------


_UsageMetric = Literal["wireless", "wired", "usage"]


@tool(annotations=READ_ONLY)
async def central_get_top_aps_by_usage(
    ctx: Context,
    metric: Annotated[
        _UsageMetric,
        coerce_enum(("wireless", "wired", "usage"), {"combined": "usage"}),
        Field(
            description=(
                "``'wireless'`` (top-aps-by-wireless-usage), ``'wired'`` "
                "(top-aps-by-wired-usage), or ``'usage'`` — the combined "
                "wired+wireless view (top-aps-by-usage). The synonym "
                "``'combined'`` is accepted as an alias for ``'usage'``, "
                "and values are matched case-insensitively."
            ),
        ),
    ],
    top_n: Annotated[int, Field(ge=1, le=100, description="Number of APs to return (default 10).")] = 10,
    filter: str | None = None,
) -> dict | str:
    """Get top-N APs by usage — metric ``'wireless'`` / ``'wired'`` / ``'usage'``
    (``'usage'`` = combined wired+wireless; ``'combined'`` is accepted as an alias).

    Consolidates the three ``/top-aps-by-{wireless,wired,}usage`` endpoints.
    """
    suffix_map = {
        "wireless": "top-aps-by-wireless-usage",
        "wired": "top-aps-by-wired-usage",
        "usage": "top-aps-by-usage",
    }
    conn = ctx.lifespan_context["central_conn"]
    params: dict = {"topN": top_n}
    if filter:
        params["filter"] = filter
    return _get(conn, f"network-monitoring/v1/{suffix_map[metric]}", params)


# ---------------------------------------------------------------------------
# Tenant-wide entity lists (radios / BSSIDs / WLANs / swarms / applications)
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_radios(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List all radios across the tenant (network-monitoring view)."""
    conn = ctx.lifespan_context["central_conn"]
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return _get(conn, "network-monitoring/v1/radios", params)


@tool(annotations=READ_ONLY)
async def central_get_bssids(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List all BSSIDs (per-radio-per-SSID broadcast records) across the tenant."""
    conn = ctx.lifespan_context["central_conn"]
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return _get(conn, "network-monitoring/v1/bssids", params)


@tool(annotations=READ_ONLY)
async def central_get_wlans_monitoring(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List WLANs across the tenant (monitoring view).

    Distinct from the existing ``central_get_wlans`` (legacy
    statistics-side view) and ``central_get_wlan_profiles`` (config-model
    view). This hits ``network-monitoring/v1/wlans``.
    """
    conn = ctx.lifespan_context["central_conn"]
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return _get(conn, "network-monitoring/v1/wlans", params)


@tool(annotations=READ_ONLY)
async def central_get_wlan_monitoring_detail(
    ctx: Context,
    wlan_name: Annotated[str, Field(description="WLAN / SSID name.")],
) -> dict | str:
    """Get one WLAN's monitoring-side detail by name."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(conn, f"network-monitoring/v1/wlans/{wlan_name}")


@tool(annotations=READ_ONLY)
async def central_get_swarms(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List IAP / Instant clusters (swarms) across the tenant."""
    conn = ctx.lifespan_context["central_conn"]
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return _get(conn, "network-monitoring/v1/swarms", params)


@tool(annotations=READ_ONLY)
async def central_get_swarm(
    ctx: Context,
    cluster_id: Annotated[str, Field(description="Swarm / cluster identifier.")],
) -> dict | str:
    """Get one swarm / IAP cluster's detail."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(conn, f"network-monitoring/v1/swarms/{cluster_id}")


@tool(annotations=READ_ONLY)
async def central_get_applications_v1(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List recognized applications (``network-monitoring/v1`` variant).

    Distinct from the existing ``central_get_applications`` which uses
    the ``v1alpha1`` path.
    """
    conn = ctx.lifespan_context["central_conn"]
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return _get(conn, "network-monitoring/v1/applications", params)
