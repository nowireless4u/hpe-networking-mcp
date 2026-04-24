"""Cross-platform site health aggregation tool.

One tool call that pulls health data from every enabled platform for a
given site, synthesizes an overall status, and returns a compact report.
Replaces ~8-12 separate tool calls with a single pre-aggregated response.
"""

import asyncio
import json
import time
from typing import Annotated, Any, Literal

from fastmcp import Context
from loguru import logger
from pydantic import BaseModel, Field

# Response models — kept compact to minimize token cost in Claude's context.


class AlertSummary(BaseModel):
    severity: str | None = None
    name: str | None = None
    category: str | None = None
    created_at: str | None = None


class MistSummary(BaseModel):
    found: bool = False
    site_id: str | None = None
    num_devices: int | None = None
    num_devices_connected: int | None = None
    num_clients: int | None = None
    alarms_total: int = 0
    alarms_critical: int = 0
    alarms_top: list[AlertSummary] = Field(default_factory=list)
    error: str | None = None


class CentralSummary(BaseModel):
    found: bool = False
    site_id: str | None = None
    health_score: int | None = None
    total_devices: int = 0
    total_clients: int = 0
    alerts_active: int = 0
    alerts_critical: int = 0
    alerts_top: list[AlertSummary] = Field(default_factory=list)
    error: str | None = None


class ClearPassSummary(BaseModel):
    queried: bool = False
    matched_nads: int = 0
    matched_nad_names: list[str] = Field(default_factory=list)
    active_sessions: int | None = None
    recent_auth_failures: int | None = None
    note: str | None = None
    error: str | None = None


class SiteHealthReport(BaseModel):
    site_name: str
    time_window_hours: int
    platforms_queried: list[str]
    platforms_matched: list[str]
    overall_status: Literal["healthy", "degraded", "critical", "unknown"]
    headline: str
    mist: MistSummary | None = None
    central: CentralSummary | None = None
    clearpass: ClearPassSummary | None = None
    recommendations: list[str] = Field(default_factory=list)


# Platforms that participate in cross-platform site health. Apstra and
# GreenLake are absent by design — Apstra is datacenter fabric (no site
# concept), GreenLake is platform admin (no site-scoped telemetry).
_SITE_PLATFORMS: tuple[str, ...] = ("mist", "central", "clearpass")


def _normalize_site_platform_filter(
    value: str | list[str] | None,
    enabled: list[str],
) -> list[str]:
    """Resolve the ``platform`` argument to the subset of platforms to query.

    - ``None`` -> every enabled site platform (mist/central/clearpass)
    - ``"central"`` -> ``["central"]``
    - ``["mist", "central"]`` -> those two (in canonical order)

    Unknown names (e.g. ``"apstra"``, ``"greenlake"``) are dropped with a
    warning. Names that are valid but not enabled on this server are kept
    in the wanted list so the caller can report them as ``queried`` but
    unmatched — matching the existing per-platform semantics.
    """
    if value is None:
        return [p for p in _SITE_PLATFORMS if p in enabled]
    candidates = [value] if isinstance(value, str) else [str(v) for v in value]

    wanted: list[str] = []
    for name in candidates:
        name = name.strip().lower()
        if name in _SITE_PLATFORMS and name not in wanted:
            wanted.append(name)
        elif name not in _SITE_PLATFORMS:
            logger.warning(
                "site_health_check(platform={!r}) — not a site platform, skipping (valid: mist, central, clearpass)",
                name,
            )
    return wanted


# --- Mist collection -----------------------------------------------------


async def _collect_mist(ctx: Context, site_name: str, window_hours: int) -> MistSummary:
    try:
        import mistapi
    except ImportError as e:
        return MistSummary(error=f"mistapi not available: {e}")

    session = ctx.lifespan_context.get("mist_session")
    org_id = ctx.lifespan_context.get("mist_org_id")
    if not session or not org_id:
        return MistSummary(error="Mist not initialized")

    summary = MistSummary()

    try:
        sites_resp = mistapi.api.v1.orgs.sites.listOrgSites(session, org_id=org_id)
        if sites_resp.status_code != 200 or not isinstance(sites_resp.data, list):
            summary.error = f"Mist listOrgSites HTTP {sites_resp.status_code}"
            return summary
        site_id = next(
            (s["id"] for s in sites_resp.data if s.get("name") == site_name),
            None,
        )
        if not site_id:
            return summary
        summary.found = True
        summary.site_id = site_id
    except Exception as e:
        logger.warning("site_health_check: Mist site resolve failed — {}", e)
        summary.error = f"site resolve failed: {e}"
        return summary

    start = int(time.time()) - window_hours * 3600
    end = int(time.time())

    stats_resp: Any = None
    alarms_resp: Any = None
    try:
        stats_resp, alarms_resp = await asyncio.gather(
            asyncio.to_thread(mistapi.api.v1.sites.stats.getSiteStats, session, site_id=site_id),
            asyncio.to_thread(
                mistapi.api.v1.sites.alarms.searchSiteAlarms,
                session,
                site_id=site_id,
                start=str(start),
                end=str(end),
                limit=100,
            ),
            return_exceptions=True,
        )
    except Exception as e:
        summary.error = f"Mist stats/alarms call failed: {e}"
        return summary

    if not isinstance(stats_resp, Exception) and getattr(stats_resp, "status_code", 0) == 200:
        data = stats_resp.data or {}
        summary.num_devices = data.get("num_devices")
        summary.num_devices_connected = data.get("num_devices_connected")
        summary.num_clients = data.get("num_clients")

    if not isinstance(alarms_resp, Exception) and getattr(alarms_resp, "status_code", 0) == 200:
        alarms = (alarms_resp.data or {}).get("results", [])
        summary.alarms_total = len(alarms)
        summary.alarms_critical = sum(1 for a in alarms if a.get("severity") == "critical")
        summary.alarms_top = [
            AlertSummary(
                severity=a.get("severity"),
                name=a.get("type"),
                category=a.get("group"),
                created_at=_epoch_to_iso(a.get("timestamp")),
            )
            for a in sorted(
                alarms,
                key=lambda x: _severity_rank(x.get("severity")),
            )[:5]
        ]

    return summary


# --- Central collection --------------------------------------------------


async def _collect_central(ctx: Context, site_name: str, _window_hours: int) -> CentralSummary:
    from hpe_networking_mcp.platforms.central.utils import (
        clean_alert_data,
        groups_to_map,
        retry_central_command,
    )

    conn = ctx.lifespan_context.get("central_conn")
    if not conn:
        return CentralSummary(error="Central not initialized")

    summary = CentralSummary()

    try:
        from pycentral.new_monitoring import MonitoringSites

        sites = await asyncio.to_thread(MonitoringSites.get_all_sites, central_conn=conn)
        match = next((s for s in sites if s.get("siteName") == site_name), None)
        if not match:
            return summary
        summary.found = True
        summary.site_id = str(match.get("id"))

        health_obj = groups_to_map(match.get("health", {}))
        if all(k in health_obj for k in ["Poor", "Fair", "Good"]):
            summary.health_score = round(health_obj["Fair"] * 0.5 + health_obj["Good"] * 1)
        summary.total_devices = match.get("devices", {}).get("total", 0)
        summary.total_clients = match.get("clients", {}).get("total", 0)
    except Exception as e:
        logger.warning("site_health_check: Central site resolve failed — {}", e)
        summary.error = f"site resolve failed: {e}"
        return summary

    try:
        resp = await asyncio.to_thread(
            retry_central_command,
            central_conn=conn,
            api_method="GET",
            api_path="network-notifications/v1/alerts",
            api_params={
                "filter": f"status eq 'Active' and siteId eq '{summary.site_id}'",
                "sort": "severity desc",
                "limit": 100,
            },
        )
        msg = resp.get("msg", {}) if isinstance(resp, dict) else {}
        items = msg.get("items", [])
        summary.alerts_active = msg.get("total", len(items))
        summary.alerts_critical = sum(1 for a in items if a.get("severity", "").lower() == "critical")
        cleaned = clean_alert_data(items[:5])
        summary.alerts_top = [
            AlertSummary(
                severity=getattr(a, "severity", None),
                name=getattr(a, "name", None),
                category=getattr(a, "category", None),
                created_at=getattr(a, "created_at", None),
            )
            for a in cleaned
        ]
    except Exception as e:
        logger.warning("site_health_check: Central alerts fetch failed — {}", e)
        summary.error = f"alerts fetch failed: {e}"

    return summary


def _extract_central_device_ips(ctx: Context, site_id: str) -> list[str]:
    """Fetch devices at a Central site and return their management IPs."""
    from pycentral.new_monitoring import MonitoringDevices

    conn = ctx.lifespan_context.get("central_conn")
    if not conn:
        return []
    try:
        devices = MonitoringDevices.get_all_device_inventory(
            central_conn=conn,
            filter_str=f"siteId eq '{site_id}'",
        )
    except Exception as e:
        logger.warning("site_health_check: Central device inventory failed — {}", e)
        return []

    ips: list[str] = []
    for d in devices or []:
        ip = d.get("ipv4") or d.get("ipAddress")
        if ip:
            ips.append(ip.split("/")[0])
    return ips


def _extract_mist_device_ips(ctx: Context, site_id: str) -> list[str]:
    """Fetch devices at a Mist site and return their management IPs."""
    import mistapi

    session = ctx.lifespan_context.get("mist_session")
    if not session:
        return []
    try:
        resp = mistapi.api.v1.sites.devices.listSiteDevices(session, site_id=site_id)
        if resp.status_code != 200 or not isinstance(resp.data, list):
            return []
    except Exception as e:
        logger.warning("site_health_check: Mist device list failed — {}", e)
        return []

    ips: list[str] = []
    for d in resp.data:
        ip = d.get("ip") or d.get("ip_config", {}).get("ip")
        if ip:
            ips.append(ip)
    return ips


# --- ClearPass collection ------------------------------------------------


def _parse_nad_address(raw: str) -> Any:
    """Parse a ClearPass NAD ip_address value into a containment matcher.

    ClearPass NADs can be defined as a single IP, CIDR subnet, or dashed
    IP range (e.g., "10.1.1.0/24", "10.1.1.1-10.1.1.50", "10.1.1.1").
    Returns an object with a `__contains__` method that accepts an
    IPv4Address or IPv6Address. Returns None if the value can't be parsed.
    """
    from ipaddress import AddressValueError, IPv4Address, IPv4Network, ip_network

    if not raw:
        return None
    val = raw.strip()
    try:
        if "-" in val:
            start_s, end_s = (p.strip() for p in val.split("-", 1))
            # NADs are effectively v4 in practice; constrain the range
            # matcher to IPv4 so ordered comparisons are type-consistent.
            start = IPv4Address(start_s)
            end = IPv4Address(end_s)

            class _RangeMatcher:
                def __contains__(self, candidate: Any) -> bool:
                    try:
                        c = candidate if isinstance(candidate, IPv4Address) else IPv4Address(str(candidate))
                        return start <= c <= end
                    except (ValueError, AddressValueError):
                        return False

            return _RangeMatcher()
        if "/" in val:
            return ip_network(val, strict=False)
        # Single IP — normalize to a /32 network for uniform containment check
        return IPv4Network(f"{IPv4Address(val)}/32")
    except (ValueError, AddressValueError):
        return None


def _ip_in_any(ip_str: str, matchers: list[Any]) -> bool:
    from ipaddress import AddressValueError, ip_address

    if not ip_str or not matchers:
        return False
    try:
        ip = ip_address(ip_str.split("/")[0])
    except (ValueError, AddressValueError):
        return False
    return any(ip in m for m in matchers)


async def _collect_clearpass(
    ctx: Context,
    site_device_ips: list[str],
    window_hours: int,
) -> ClearPassSummary:
    """Collect ClearPass data for a site using subnet-aware NAD matching.

    Algorithm:
      1. Fetch every ClearPass NAD once.
      2. Parse each NAD's ip_address (single, CIDR, or range) into a matcher.
      3. A NAD is a "site NAD" if its address space contains any site
         device IP — this is what the user's gateway VIP pattern requires:
         the VIP itself isn't in the device inventory, but the physical
         gateway(s) sit in the same subnet that the NAD covers.
      4. Pull recent time-bounded sessions (no NAS filter) and count those
         whose nasipaddress falls inside any site NAD's address space.
         This catches sessions sourced from the VIP that the device
         inventory doesn't surface.
      5. Same idea for system events (filtered by site NAD names in the
         event text) as a best-effort auth-failure signal.
    """
    if not site_device_ips:
        return ClearPassSummary(
            queried=False,
            note="No device IPs resolved from Mist/Central to match against NADs.",
        )

    summary = ClearPassSummary(queried=True)

    try:
        from pyclearpass.api_policyelements import ApiPolicyElements
        from pyclearpass.api_sessioncontrol import ApiSessionControl

        from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
    except ImportError as e:
        return ClearPassSummary(queried=False, error=f"pyclearpass not available: {e}")

    try:
        nad_client = await get_clearpass_session(ApiPolicyElements)
        nad_resp = await asyncio.to_thread(
            nad_client._send_request,
            "/network-device?limit=1000",
            "get",
        )
        all_nads = nad_resp.get("_embedded", {}).get("items", []) if isinstance(nad_resp, dict) else []
    except Exception as e:
        logger.warning("site_health_check: ClearPass NAD fetch failed — {}", e)
        summary.error = f"NAD fetch failed: {e}"
        return summary

    # Parse each NAD's address and find NADs whose address space contains
    # any site device IP. A single NAD can be a subnet covering the whole
    # site, a range covering a gateway cluster, or a single IP.
    site_nad_matchers: list[Any] = []
    site_nad_names: list[str] = []
    for nad in all_nads:
        matcher = _parse_nad_address(nad.get("ip_address", ""))
        if matcher is None:
            continue
        if any(_ip_in_any(ip, [matcher]) for ip in site_device_ips):
            site_nad_matchers.append(matcher)
            name = nad.get("name") or nad.get("ip_address") or f"NAD {nad.get('id')}"
            site_nad_names.append(name)

    summary.matched_nads = len(site_nad_matchers)
    summary.matched_nad_names = site_nad_names[:10]
    if not site_nad_matchers:
        summary.note = (
            "No ClearPass NADs cover any site device IPs. "
            "Sessions may still exist but can't be attributed to this site from IP alone."
        )
        return summary

    # Pull recent sessions with only a time filter, then filter client-side
    # by matching each session's nasipaddress against the site NAD address
    # space. Catches sessions sourced from gateway VIPs that aren't in the
    # device inventory.
    cutoff = int(time.time()) - window_hours * 3600
    try:
        session_client = await get_clearpass_session(ApiSessionControl)
        sess_filter = json.dumps({"acctstarttime": {"$gt": cutoff}})
        sess_resp = await asyncio.to_thread(
            session_client._send_request,
            f"/session?filter={sess_filter}&limit=500",
            "get",
        )
        items = sess_resp.get("_embedded", {}).get("items", []) if isinstance(sess_resp, dict) else []
        matched_count = sum(1 for s in items if _ip_in_any(s.get("nasipaddress", ""), site_nad_matchers))
        summary.active_sessions = matched_count
        if len(items) >= 500:
            summary.note = (
                summary.note + " " if summary.note else ""
            ) + "Session pull capped at 500 — actual count may be higher."
    except Exception as e:
        logger.warning("site_health_check: ClearPass sessions fetch failed — {}", e)
        summary.error = (summary.error or "") + f"sessions fetch failed: {e}; "

    # System events: count recent ERROR-level events that reference any
    # site NAD by name. Best effort — ClearPass doesn't expose a per-NAD
    # auth-failure counter over REST.
    try:
        event_filter = json.dumps({"timestamp_utc": {"$gt": cutoff}, "level": "ERROR"})
        events_resp = await asyncio.to_thread(
            session_client._send_request,
            f"/system-event?filter={event_filter}&limit=500",
            "get",
        )
        event_items = events_resp.get("_embedded", {}).get("items", []) if isinstance(events_resp, dict) else []
        name_set = {n.lower() for n in site_nad_names}
        if name_set:
            summary.recent_auth_failures = sum(
                1 for e in event_items if any(nm in str(e.get("description", "")).lower() for nm in name_set)
            )
        else:
            summary.recent_auth_failures = 0
    except Exception as e:
        logger.warning("site_health_check: ClearPass system events fetch failed — {}", e)

    return summary


# --- Synthesis -----------------------------------------------------------


def _synthesize(
    site_name: str,
    mist: MistSummary | None,
    central: CentralSummary | None,
    clearpass: ClearPassSummary | None,
) -> tuple[Literal["healthy", "degraded", "critical", "unknown"], str, list[str]]:
    """Compute overall status, headline, and recommendations."""
    recommendations: list[str] = []
    worst: Literal["healthy", "degraded", "critical", "unknown"] = "unknown"
    headline_parts: list[str] = []

    def _worsen(new: Literal["healthy", "degraded", "critical", "unknown"]) -> None:
        nonlocal worst
        rank = {"unknown": 0, "healthy": 1, "degraded": 2, "critical": 3}
        if rank[new] > rank[worst]:
            worst = new

    if mist and mist.found:
        _worsen("healthy")
        if mist.alarms_critical:
            _worsen("critical")
            headline_parts.append(f"{mist.alarms_critical} critical Mist alarms")
            recommendations.append(
                f"Mist: investigate {mist.alarms_critical} critical alarms — call "
                f"mist_search_alarms(scope='site', site_id='{mist.site_id}', severity='critical')."
            )
        elif mist.alarms_total > 10:
            _worsen("degraded")
            headline_parts.append(f"{mist.alarms_total} Mist alarms")

        if (
            mist.num_devices is not None
            and mist.num_devices_connected is not None
            and mist.num_devices_connected < mist.num_devices
        ):
            down = mist.num_devices - mist.num_devices_connected
            _worsen("degraded" if down < 3 else "critical")
            headline_parts.append(f"{down}/{mist.num_devices} Mist devices offline")
            recommendations.append(
                f"Mist: {down} device(s) offline — call mist_search_device(site_id='{mist.site_id}', "
                "status='disconnected') to identify them."
            )

    if central and central.found:
        _worsen("healthy")
        if central.alerts_critical:
            _worsen("critical")
            headline_parts.append(f"{central.alerts_critical} critical Central alerts")
            recommendations.append(
                f"Central: investigate {central.alerts_critical} critical alerts — call "
                f"central_get_alerts(site_id='{central.site_id}', status='Active')."
            )
        elif central.alerts_active > 10:
            _worsen("degraded")
            headline_parts.append(f"{central.alerts_active} Central alerts")

        if central.health_score is not None:
            if central.health_score < 50:
                _worsen("critical")
                headline_parts.append(f"Central health {central.health_score}/100")
            elif central.health_score < 80:
                _worsen("degraded")
                headline_parts.append(f"Central health {central.health_score}/100")

    if (
        clearpass
        and clearpass.queried
        and clearpass.matched_nads
        and clearpass.recent_auth_failures
        and clearpass.recent_auth_failures > 50
    ):
        _worsen("degraded")
        headline_parts.append(f"{clearpass.recent_auth_failures} ClearPass auth failures")
        recommendations.append(
            "ClearPass: elevated auth failures — call clearpass_get_system_events() "
            "with a time-bounded filter for detail."
        )

    if worst == "unknown":
        headline = f"Site '{site_name}' not found on any queried platform."
        recommendations.append(
            "Verify the site name. On Mist, sites come from mist_get_configuration_objects"
            "(object_type='org_sites'). On Central, sites come from central_get_site_name_id_mapping."
        )
    elif worst == "healthy":
        headline = f"Site '{site_name}' healthy — no critical issues detected."
    else:
        headline = f"Site '{site_name}' {worst}: " + ", ".join(headline_parts) + "."

    return worst, headline, recommendations


# --- Helpers -------------------------------------------------------------


def _severity_rank(sev: Any) -> int:
    order = {"critical": 0, "major": 1, "minor": 2, "warn": 3, "info": 4}
    return order.get(str(sev or "").lower(), 5)


def _epoch_to_iso(value: Any) -> str | None:
    if not value:
        return None
    try:
        from datetime import UTC, datetime

        return datetime.fromtimestamp(float(value), tz=UTC).isoformat()
    except (TypeError, ValueError):
        return None


# --- Registration --------------------------------------------------------


def register(mcp: Any, config: Any) -> None:
    """Register the cross-platform site_health_check tool.

    Requires at least one of Mist or Central to be enabled — those are the
    platforms that own site definitions. ClearPass is additive.
    """
    if not (config.mist or config.central):
        logger.info("site_health_check: skipped (neither Mist nor Central enabled)")
        return

    @mcp.tool(
        annotations={
            "title": "Cross-platform site health check",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
            "idempotentHint": True,
        },
    )
    async def site_health_check(
        ctx: Context,
        site_name: Annotated[
            str,
            Field(description="Exact site name as shown in Mist and/or Central."),
        ],
        time_window_hours: Annotated[
            int,
            Field(
                description=("Lookback window for alarms, sessions, and events. Default 24 hours."),
                default=24,
                ge=1,
                le=168,
            ),
        ] = 24,
        platform: Annotated[
            str | list[str] | None,
            Field(
                description=(
                    "Optional platform filter. Omit (null) to query every enabled site "
                    "platform — the normal cross-platform aggregation. Pass one name "
                    "('central', 'mist', or 'clearpass') or a list (['mist','central']) "
                    "to restrict the report to those platforms only. Use this when the "
                    "user's question explicitly names a platform (e.g. 'how is site X "
                    "doing in Central'). Apstra and GreenLake are not valid here — they "
                    "don't have site-scoped telemetry."
                ),
                default=None,
            ),
        ] = None,
    ) -> SiteHealthReport:
        """Aggregate a site's health across enabled HPE networking platforms.

        Pulls Mist site stats and alarms, Central site health and active alerts,
        and (when ClearPass is configured) matches site device IPs to ClearPass
        NADs to count active sessions and recent auth failures. Returns a single
        compact report with an overall status and concrete next-step
        recommendations — replaces ~8–12 individual tool calls.

        Use when the user asks how a site is doing, whether a site is healthy,
        or wants an at-a-glance status for a specific location. When the user
        explicitly names a platform ('how is site X doing in Central'), pass
        platform='central' (or the relevant name) so the report is scoped to
        that platform only. For deep-dive investigation of specific issues
        surfaced in the report, follow the recommendations, which reference
        the appropriate drill-down tools.
        """
        config = ctx.lifespan_context["config"]

        enabled_site_platforms: list[str] = []
        if config.mist:
            enabled_site_platforms.append("mist")
        if config.central:
            enabled_site_platforms.append("central")
        if config.clearpass:
            enabled_site_platforms.append("clearpass")

        wanted = _normalize_site_platform_filter(platform, enabled_site_platforms)

        query_mist = config.mist is not None and "mist" in wanted
        query_central = config.central is not None and "central" in wanted
        query_clearpass = config.clearpass is not None and "clearpass" in wanted

        platforms_queried: list[str] = []
        tasks: list[Any] = []
        if query_mist:
            platforms_queried.append("mist")
            tasks.append(_collect_mist(ctx, site_name, time_window_hours))
        if query_central:
            platforms_queried.append("central")
            tasks.append(_collect_central(ctx, site_name, time_window_hours))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        mist_summary: MistSummary | None = None
        central_summary: CentralSummary | None = None
        idx = 0
        if query_mist:
            r = results[idx]
            mist_summary = r if isinstance(r, MistSummary) else MistSummary(error=str(r))
            idx += 1
        if query_central:
            r = results[idx]
            central_summary = r if isinstance(r, CentralSummary) else CentralSummary(error=str(r))
            idx += 1

        device_ips: list[str] = []
        if central_summary and central_summary.found and central_summary.site_id:
            device_ips.extend(await asyncio.to_thread(_extract_central_device_ips, ctx, central_summary.site_id))
        if mist_summary and mist_summary.found and mist_summary.site_id:
            device_ips.extend(await asyncio.to_thread(_extract_mist_device_ips, ctx, mist_summary.site_id))
        device_ips = list(dict.fromkeys(device_ips))  # de-dupe preserving order

        clearpass_summary: ClearPassSummary | None = None
        if query_clearpass:
            platforms_queried.append("clearpass")
            clearpass_summary = await _collect_clearpass(ctx, device_ips, time_window_hours)

        matched: list[str] = []
        if mist_summary and mist_summary.found:
            matched.append("mist")
        if central_summary and central_summary.found:
            matched.append("central")
        if clearpass_summary and clearpass_summary.matched_nads:
            matched.append("clearpass")

        status, headline, recommendations = _synthesize(
            site_name,
            mist_summary,
            central_summary,
            clearpass_summary,
        )

        logger.info(
            "site_health_check: site='{}' status={} matched={}",
            site_name,
            status,
            matched,
        )

        return SiteHealthReport(
            site_name=site_name,
            time_window_hours=time_window_hours,
            platforms_queried=platforms_queried,
            platforms_matched=matched,
            overall_status=status,
            headline=headline,
            mist=mist_summary,
            central=central_summary,
            clearpass=clearpass_summary,
            recommendations=recommendations,
        )

    logger.info("Cross-platform: registered site_health_check tool")
