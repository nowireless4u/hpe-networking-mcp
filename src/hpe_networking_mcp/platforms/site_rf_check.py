"""Cross-platform site RF / channel-planning aggregation tool.

One tool call that pulls per-AP, per-band radio state from every enabled
platform (Mist + Central) for a given site, aggregates channel
distribution + utilization per band, and returns a compact report.
Replaces 10+ separate tool calls with a single pre-aggregated response.

The AI-discovery gap this exists to close: questions like "show me how my
5/6 GHz channels are operating" used to produce Mist-only answers even
when the user had Aruba APs in Central at the same site. By exposing a
single purpose-built tool the AI reaches for it directly instead of
picking one platform's meta-tool and stopping.
"""

import asyncio
import re
from collections import Counter
from typing import Annotated, Any, Literal

from fastmcp import Context
from loguru import logger
from pydantic import BaseModel, Field

# Response models — compact shapes to keep Claude's context cheap.


class Radio(BaseModel):
    """One radio on one AP: live per-band state snapshot."""

    band: Literal["2.4", "5", "6"]
    channel: str | None = None
    primary_channel: int | None = None
    bandwidth_mhz: int | None = None
    power_dbm: float | None = None
    channel_utilization_pct: float | None = None
    noise_floor_dbm: float | None = None
    num_clients: int | None = None
    status: str | None = None


class APSummary(BaseModel):
    """Per-AP RF state: name, identity, and the three radios (if present)."""

    name: str | None = None
    model: str | None = None
    serial: str | None = None
    mac: str | None = None
    platform: Literal["mist", "central"]
    connected: bool = True
    radios: list[Radio] = Field(default_factory=list)
    error: str | None = None


class BandSummary(BaseModel):
    """Site-level summary for one band across all reporting APs."""

    band: Literal["2.4", "5", "6"]
    ap_count: int = 0
    radios_active: int = 0
    channel_distribution: dict[str, int] = Field(default_factory=dict)
    avg_utilization_pct: float | None = None
    max_utilization_pct: float | None = None
    avg_noise_floor_dbm: float | None = None
    allowed_channels: list[int] | None = None
    note: str | None = None


class MistRF(BaseModel):
    found: bool = False
    site_id: str | None = None
    ap_count: int = 0
    aps_connected: int = 0
    rf_template_name: str | None = None
    rf_template_allowed: dict[str, list[int] | None] = Field(default_factory=dict)
    error: str | None = None


class CentralRF(BaseModel):
    found: bool = False
    site_id: str | None = None
    ap_count: int = 0
    aps_online: int = 0
    error: str | None = None


class SiteOption(BaseModel):
    """A selectable site returned when the caller omits ``site_name``."""

    name: str
    platform: Literal["mist", "central"]
    site_id: str | None = None
    ap_count: int = 0
    online_ap_count: int | None = None


class SiteRFReport(BaseModel):
    site_name: str
    platforms_queried: list[str]
    platforms_matched: list[str]
    headline: str
    bands: dict[Literal["2.4", "5", "6"], BandSummary] = Field(default_factory=dict)
    aps: list[APSummary] = Field(default_factory=list)
    mist: MistRF | None = None
    central: CentralRF | None = None
    recommendations: list[str] = Field(default_factory=list)
    site_options: list[SiteOption] | None = None
    rendered_report: str | None = None


_RF_PLATFORMS: tuple[str, ...] = ("mist", "central")


def _normalize_rf_platform_filter(
    value: str | list[str] | None,
    enabled: list[str],
) -> list[str]:
    """Resolve the ``platform`` argument to the subset of RF platforms to query."""
    if value is None:
        return [p for p in _RF_PLATFORMS if p in enabled]
    candidates = [value] if isinstance(value, str) else [str(v) for v in value]

    wanted: list[str] = []
    for name in candidates:
        name = name.strip().lower()
        if name in _RF_PLATFORMS and name not in wanted:
            wanted.append(name)
        elif name not in _RF_PLATFORMS:
            logger.warning(
                "site_rf_check(platform={!r}) — not an RF platform, skipping (valid: mist, central)",
                name,
            )
    return wanted


# --- Parsing helpers -----------------------------------------------------

# Central channel strings are free-form: "1", "36", "165S", "49T+" — a
# primary-channel integer optionally followed by bonding suffixes like
# "S" (secondary), "T+"/"T-" (triplet), "+"/"-" (HT40 pairing). The
# leading integer is always the primary channel.
_CHANNEL_PRIMARY_RE = re.compile(r"^(\d+)")
_NUMERIC_RE = re.compile(r"^-?\d+(\.\d+)?")


def _parse_primary_channel(raw: Any) -> int | None:
    """Extract the primary channel number from a raw channel value."""
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw
    s = str(raw).strip()
    if not s:
        return None
    m = _CHANNEL_PRIMARY_RE.match(s)
    return int(m.group(1)) if m else None


def _parse_numeric(raw: Any) -> float | None:
    """Extract the leading number from a value that may carry a unit suffix."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip()
    if not s:
        return None
    m = _NUMERIC_RE.match(s)
    return float(m.group(0)) if m else None


def _parse_bandwidth_mhz(raw: Any) -> int | None:
    """'160 MHz' -> 160; '20' -> 20; None -> None."""
    n = _parse_numeric(raw)
    return int(n) if n is not None else None


def _band_key(raw: Any) -> Literal["2.4", "5", "6"] | None:
    """Normalize Mist/Central band values to our canonical 3 keys."""
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if s in ("24", "2.4", "2.4 ghz", "2.4ghz"):
        return "2.4"
    if s in ("5", "5 ghz", "5ghz"):
        return "5"
    if s in ("6", "6 ghz", "6ghz"):
        return "6"
    return None


# --- Mist collection -----------------------------------------------------


def _mist_band_from_stat_key(key: str) -> Literal["2.4", "5", "6"] | None:
    """Mist radio_stat keys are band_24 / band_5 / band_6."""
    return _band_key(key.removeprefix("band_"))


async def _collect_mist(
    ctx: Context,
    site_name: str,
) -> tuple[MistRF, list[APSummary]]:
    try:
        import mistapi
    except ImportError as e:
        return MistRF(error=f"mistapi not available: {e}"), []

    session = ctx.lifespan_context.get("mist_session")
    org_id = ctx.lifespan_context.get("mist_org_id")
    if not session or not org_id:
        return MistRF(error="Mist not initialized"), []

    summary = MistRF()

    try:
        sites_resp = mistapi.api.v1.orgs.sites.listOrgSites(session, org_id=org_id)
        if sites_resp.status_code != 200 or not isinstance(sites_resp.data, list):
            summary.error = f"Mist listOrgSites HTTP {sites_resp.status_code}"
            return summary, []
        site_id = next(
            (s["id"] for s in sites_resp.data if s.get("name") == site_name),
            None,
        )
        if not site_id:
            return summary, []
        summary.found = True
        summary.site_id = site_id
    except Exception as e:
        logger.warning("site_rf_check: Mist site resolve failed — {}", e)
        summary.error = f"site resolve failed: {e}"
        return summary, []

    # Per-device stats (live radio_stat on each AP) and current channel
    # planning template in parallel. The template gives us allowed_channels
    # per band even when no APs are connected.
    stats_resp: Any = None
    template_resp: Any = None
    try:
        stats_resp, template_resp = await asyncio.gather(
            asyncio.to_thread(
                session.mist_get,
                uri=f"/api/v1/sites/{site_id}/stats/devices",
                query={"type": "ap", "limit": 100},
            ),
            asyncio.to_thread(
                mistapi.api.v1.sites.rrm.getSiteCurrentChannelPlanning,
                session,
                site_id=site_id,
            ),
            return_exceptions=True,
        )
    except Exception as e:
        summary.error = f"Mist stats/template call failed: {e}"
        return summary, []

    aps: list[APSummary] = []
    if not isinstance(stats_resp, Exception):
        data = getattr(stats_resp, "data", None) or {}
        results = data.get("results", []) if isinstance(data, dict) else []
        summary.ap_count = data.get("total", len(results)) if isinstance(data, dict) else len(results)
        for dev in results:
            connected = dev.get("status") == "connected"
            if connected:
                summary.aps_connected += 1
            radios: list[Radio] = []
            radio_stat = dev.get("radio_stat") or {}
            if connected and isinstance(radio_stat, dict):
                for stat_key, stat in radio_stat.items():
                    band = _mist_band_from_stat_key(stat_key)
                    if band is None or not isinstance(stat, dict):
                        continue
                    radios.append(
                        Radio(
                            band=band,
                            channel=str(stat.get("channel")) if stat.get("channel") is not None else None,
                            primary_channel=_parse_primary_channel(stat.get("channel")),
                            bandwidth_mhz=_parse_bandwidth_mhz(stat.get("bandwidth")),
                            power_dbm=_parse_numeric(stat.get("power")),
                            channel_utilization_pct=_parse_numeric(stat.get("usage")),
                            noise_floor_dbm=_parse_numeric(stat.get("noise_floor")),
                            num_clients=stat.get("num_clients"),
                            status="UP",
                        )
                    )
            aps.append(
                APSummary(
                    name=dev.get("name"),
                    model=dev.get("model"),
                    serial=dev.get("serial"),
                    mac=dev.get("mac"),
                    platform="mist",
                    connected=connected,
                    radios=radios,
                )
            )

    if not isinstance(template_resp, Exception) and getattr(template_resp, "status_code", 0) == 200:
        tpl = (getattr(template_resp, "data", None) or {}).get("rftemplate") or {}
        summary.rf_template_name = (getattr(template_resp, "data", None) or {}).get("rftemplate_name")
        for raw_band, tpl_band in ("24", "band_24"), ("5", "band_5"), ("6", "band_6"):
            cfg = tpl.get(tpl_band) or {}
            channels = cfg.get("channels")
            if isinstance(channels, list) and channels:
                summary.rf_template_allowed[raw_band] = list(channels)
            else:
                summary.rf_template_allowed[raw_band] = None

    return summary, aps


# --- Central collection --------------------------------------------------


async def _collect_central(
    ctx: Context,
    site_name: str,
    max_aps: int,
) -> tuple[CentralRF, list[APSummary]]:
    conn = ctx.lifespan_context.get("central_conn")
    if not conn:
        return CentralRF(error="Central not initialized"), []

    summary = CentralRF()

    try:
        from pycentral.new_monitoring.aps import MonitoringAPs
        from pycentral.new_monitoring.sites import MonitoringSites
    except ImportError as e:
        return CentralRF(error=f"pycentral not available: {e}"), []

    try:
        sites = await asyncio.to_thread(MonitoringSites.get_all_sites, central_conn=conn)
        match = next((s for s in sites if s.get("siteName") == site_name), None)
        if not match:
            return summary, []
        summary.found = True
        summary.site_id = str(match.get("id"))
    except Exception as e:
        logger.warning("site_rf_check: Central site resolve failed — {}", e)
        summary.error = f"site resolve failed: {e}"
        return summary, []

    # List all APs at the site (site-level filter), then fan out per-AP
    # details in parallel to get the radios array. Cap to max_aps to bound
    # cost on large sites — users can raise the cap via the tool param.
    try:
        ap_list = await asyncio.to_thread(
            MonitoringAPs.get_all_aps,
            central_conn=conn,
            filter_str=f"siteId eq '{summary.site_id}'",
        )
    except Exception as e:
        summary.error = f"AP list fetch failed: {e}"
        return summary, []

    if not ap_list:
        return summary, []

    summary.ap_count = len(ap_list)
    summary.aps_online = sum(1 for ap in ap_list if ap.get("status") == "ONLINE")

    online_aps = [ap for ap in ap_list if ap.get("status") == "ONLINE"]
    targets = online_aps[:max_aps]
    truncated = len(online_aps) > max_aps

    details_list = await asyncio.gather(
        *[
            asyncio.to_thread(
                MonitoringAPs.get_ap_details,
                central_conn=conn,
                serial_number=ap.get("serialNumber"),
            )
            for ap in targets
        ],
        return_exceptions=True,
    )

    aps: list[APSummary] = []
    for ap, details in zip(targets, details_list, strict=False):
        if isinstance(details, Exception):
            aps.append(
                APSummary(
                    name=ap.get("deviceName"),
                    model=ap.get("model"),
                    serial=ap.get("serialNumber"),
                    mac=ap.get("macAddress"),
                    platform="central",
                    connected=ap.get("status") == "ONLINE",
                    error=f"details fetch failed: {details}",
                )
            )
            continue
        d = details if isinstance(details, dict) else {}
        radios: list[Radio] = []
        for radio in d.get("radios") or []:
            band = _band_key(radio.get("band"))
            if band is None:
                continue
            stats = radio.get("radioStats") or [{}]
            stat = stats[0] if isinstance(stats, list) and stats else {}
            raw_ch = radio.get("channel")
            radios.append(
                Radio(
                    band=band,
                    channel=str(raw_ch) if raw_ch is not None else None,
                    primary_channel=_parse_primary_channel(raw_ch),
                    bandwidth_mhz=_parse_bandwidth_mhz(radio.get("bandwidth")),
                    power_dbm=_parse_numeric(radio.get("power")),
                    channel_utilization_pct=_parse_numeric(stat.get("channelUtilization")),
                    noise_floor_dbm=_parse_numeric(stat.get("noiseFloor")),
                    num_clients=None,
                    status=radio.get("status"),
                )
            )
        aps.append(
            APSummary(
                name=d.get("deviceName") or ap.get("deviceName"),
                model=d.get("model") or ap.get("model"),
                serial=d.get("serialNumber") or ap.get("serialNumber"),
                mac=d.get("macAddress") or ap.get("macAddress"),
                platform="central",
                connected=(d.get("status") or ap.get("status")) == "ONLINE",
                radios=radios,
            )
        )

    if truncated:
        summary.error = (
            f"Per-AP details fetched for {max_aps} of {len(online_aps)} online APs — raise "
            "`max_aps_per_platform` to cover more."
        )

    return summary, aps


# --- Aggregation ---------------------------------------------------------


def _aggregate_bands(
    aps: list[APSummary],
    mist_template: dict[str, list[int] | None],
) -> dict[Literal["2.4", "5", "6"], BandSummary]:
    """Build per-band summary from the flat AP list."""
    bands: dict[Literal["2.4", "5", "6"], BandSummary] = {}
    for band in ("2.4", "5", "6"):
        radios = [r for ap in aps for r in ap.radios if r.band == band and ap.connected]
        channels = Counter(str(r.primary_channel) for r in radios if r.primary_channel is not None)
        utils = [r.channel_utilization_pct for r in radios if r.channel_utilization_pct is not None]
        noises = [r.noise_floor_dbm for r in radios if r.noise_floor_dbm is not None]
        ap_count_for_band = len({(ap.platform, ap.serial) for ap in aps if any(r.band == band for r in ap.radios)})

        summary = BandSummary(
            band=band,
            ap_count=ap_count_for_band,
            radios_active=len(radios),
            channel_distribution=dict(channels),
            avg_utilization_pct=round(sum(utils) / len(utils), 1) if utils else None,
            max_utilization_pct=max(utils) if utils else None,
            avg_noise_floor_dbm=round(sum(noises) / len(noises), 1) if noises else None,
            allowed_channels=mist_template.get("24" if band == "2.4" else band),
        )
        if summary.allowed_channels is None and mist_template.get("24" if band == "2.4" else band) is None:
            summary.note = "RF template allowed_channels not set — auto (regulatory default)."
        bands[band] = summary  # type: ignore[index]
    return bands


def _synthesize(
    site_name: str,
    bands: dict[Literal["2.4", "5", "6"], BandSummary],
    aps: list[APSummary],
    mist: MistRF | None,
    central: CentralRF | None,
) -> tuple[str, list[str]]:
    """Compute headline and recommendations from the aggregated bands."""
    recommendations: list[str] = []
    headline_parts: list[str] = []

    connected_aps = sum(1 for ap in aps if ap.connected)
    total_aps = (mist.ap_count if mist and mist.found else 0) + (central.ap_count if central and central.found else 0)
    if total_aps:
        headline_parts.append(f"{connected_aps}/{total_aps} APs online")

    for band_name in ("2.4", "5", "6"):
        bs = bands.get(band_name)  # type: ignore[arg-type]
        if not bs or bs.radios_active == 0:
            continue
        chans = [f"ch{c}×{n}" for c, n in sorted(bs.channel_distribution.items(), key=lambda kv: -kv[1])[:3]]
        headline_parts.append(f"{band_name}GHz: " + ", ".join(chans))

        # Co-channel cluster: 3+ APs on the same primary channel in 5 or 6 GHz
        if band_name in ("5", "6"):
            for ch, count in bs.channel_distribution.items():
                if count >= 3:
                    recommendations.append(
                        f"{band_name} GHz — {count} APs on channel {ch}; consider staggering via RRM "
                        "or manually via the RF template."
                    )

        if bs.max_utilization_pct is not None and bs.max_utilization_pct >= 70:
            recommendations.append(
                f"{band_name} GHz — peak channel utilization {bs.max_utilization_pct:.0f}% "
                "(>=70% indicates airtime pressure; check busiest AP)."
            )

        if bs.avg_noise_floor_dbm is not None and bs.avg_noise_floor_dbm > -70:
            recommendations.append(
                f"{band_name} GHz — noise floor {bs.avg_noise_floor_dbm:.0f} dBm is elevated (>-70 dBm); "
                "investigate external interference."
            )

    if not headline_parts:
        if (mist and mist.found) or (central and central.found):
            headline = f"Site '{site_name}' resolved but no APs are currently online to report RF state."
        else:
            headline = f"Site '{site_name}' not found on any queried platform."
        return headline, recommendations
    headline = f"Site '{site_name}': " + " | ".join(headline_parts)
    return headline, recommendations


# --- Site enumeration (no site_name given) ------------------------------


async def _list_mist_site_options(ctx: Context) -> list[SiteOption]:
    """Every Mist site in the org, plus an AP-count per site.

    One call to listOrgSites for the site list, one call to
    searchOrgDevices(type=ap) for the AP counts — then group AP count by
    site_id client-side. Total: 2 Mist calls regardless of site count.
    """
    try:
        import mistapi
    except ImportError:
        return []

    session = ctx.lifespan_context.get("mist_session")
    org_id = ctx.lifespan_context.get("mist_org_id")
    if not session or not org_id:
        return []

    sites_resp: Any = None
    devices_resp: Any = None
    try:
        sites_resp, devices_resp = await asyncio.gather(
            asyncio.to_thread(mistapi.api.v1.orgs.sites.listOrgSites, session, org_id=org_id),
            asyncio.to_thread(
                session.mist_get,
                uri=f"/api/v1/orgs/{org_id}/inventory",
                query={"type": "ap", "limit": 1000},
            ),
            return_exceptions=True,
        )
    except Exception as e:
        logger.warning("site_rf_check: Mist site enumeration failed — {}", e)
        return []

    if isinstance(sites_resp, Exception) or getattr(sites_resp, "status_code", 0) != 200:
        return []

    sites = sites_resp.data if isinstance(sites_resp.data, list) else []
    ap_counts: dict[str, int] = {}
    online_counts: dict[str, int] = {}
    if not isinstance(devices_resp, Exception):
        data = getattr(devices_resp, "data", None)
        items = data if isinstance(data, list) else []
        for dev in items:
            sid = dev.get("site_id")
            if not sid:
                continue
            ap_counts[sid] = ap_counts.get(sid, 0) + 1
            # /orgs/{id}/inventory uses `connected: bool`, not `status`.
            online_counts[sid] = online_counts.get(sid, 0) + (1 if dev.get("connected") else 0)

    options: list[SiteOption] = []
    for s in sites:
        sid = s.get("id")
        if not sid:
            continue
        ap_count = ap_counts.get(sid, 0)
        options.append(
            SiteOption(
                name=s.get("name") or f"site {sid}",
                platform="mist",
                site_id=sid,
                ap_count=ap_count,
                # Distinguish "no APs at all" (None) from "has APs, none online" (0).
                online_ap_count=online_counts.get(sid, 0) if ap_count > 0 else None,
            )
        )
    return options


async def _list_central_site_options(ctx: Context) -> list[SiteOption]:
    """Every Central site, plus an AP-count per site.

    `get_all_sites` returns site metadata; `get_all_aps` (no filter) is
    org-wide. Group AP count by siteId client-side.
    """
    conn = ctx.lifespan_context.get("central_conn")
    if not conn:
        return []

    try:
        from pycentral.new_monitoring.aps import MonitoringAPs
        from pycentral.new_monitoring.sites import MonitoringSites
    except ImportError:
        return []

    sites: Any = None
    aps: Any = None
    try:
        sites, aps = await asyncio.gather(
            asyncio.to_thread(MonitoringSites.get_all_sites, central_conn=conn),
            asyncio.to_thread(MonitoringAPs.get_all_aps, central_conn=conn),
            return_exceptions=True,
        )
    except Exception as e:
        logger.warning("site_rf_check: Central site enumeration failed — {}", e)
        return []

    if isinstance(sites, Exception):
        return []
    aps_list = aps if isinstance(aps, list) else []

    ap_counts: dict[str, int] = {}
    online_counts: dict[str, int] = {}
    for ap in aps_list:
        sid = str(ap.get("siteId") or "")
        if not sid:
            continue
        ap_counts[sid] = ap_counts.get(sid, 0) + 1
        if ap.get("status") == "ONLINE":
            online_counts[sid] = online_counts.get(sid, 0) + 1

    options: list[SiteOption] = []
    for s in sites:
        sid = str(s.get("id") or "")
        if not sid:
            continue
        ap_count = ap_counts.get(sid, 0)
        options.append(
            SiteOption(
                name=s.get("siteName") or f"site {sid}",
                platform="central",
                site_id=sid,
                ap_count=ap_count,
                # Distinguish "no APs at all" (None) from "has APs, none online" (0).
                online_ap_count=online_counts.get(sid, 0) if ap_count > 0 else None,
            )
        )
    return options


def _merge_site_options(options: list[SiteOption]) -> list[SiteOption]:
    """Sort options: most online APs first, then most APs, then alphabetical."""
    return sorted(
        options,
        key=lambda o: (
            -(o.online_ap_count or 0),
            -o.ap_count,
            o.name.lower(),
        ),
    )


def _render_site_options(options: list[SiteOption]) -> str:
    """Compact picker UI for when the caller didn't name a site."""
    if not options:
        return "# RF Check — pick a site\n\nNo sites available on the queried platforms.\n"

    lines = [
        "# RF Check — pick a site",
        "",
        'No `site_name` was given. Re-run `site_rf_check(site_name="...")` with one of the below:',
        "",
    ]
    rows: list[tuple[str, str, str, str]] = [("Site", "Platform", "APs total", "APs online")]
    for opt in options[:50]:
        rows.append(
            (
                opt.name,
                opt.platform,
                str(opt.ap_count),
                "?" if opt.online_ap_count is None else str(opt.online_ap_count),
            )
        )
    widths = [max(len(r[i]) for r in rows) for i in range(4)]
    for i, row in enumerate(rows):
        lines.append("  " + "  ".join(cell.ljust(widths[j]) for j, cell in enumerate(row)))
        if i == 0:
            lines.append("  " + "  ".join("─" * widths[j] for j in range(4)))
    if len(options) > 50:
        lines.append("")
        lines.append(f"...and {len(options) - 50} more sites (truncated to top 50 by AP count).")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# --- Rendering -----------------------------------------------------------


def _bar(value: float | None, full: float = 100.0, width: int = 20) -> str:
    """Render a single horizontal bar. `value` and `full` are same-unit."""
    if value is None:
        return "░" * width
    filled = max(0, min(width, round((value / full) * width)))
    return "█" * filled + "░" * (width - filled)


def _render_channel_distribution(band_name: str, bs: BandSummary) -> list[str]:
    """Per-band channel distribution chart (channel -> AP count bar)."""
    lines: list[str] = []
    if bs.radios_active == 0:
        lines.append(f"### {band_name} GHz — no active radios")
        if bs.allowed_channels:
            lines.append(f"Template allows: {', '.join(str(c) for c in bs.allowed_channels)}")
        return lines

    lines.append(f"### {band_name} GHz — {bs.radios_active} radio(s) across {bs.ap_count} AP(s)")

    util_line = ""
    if bs.avg_utilization_pct is not None:
        util_line = f"util avg {bs.avg_utilization_pct:.0f}%"
        if bs.max_utilization_pct is not None:
            util_line += f" / peak {bs.max_utilization_pct:.0f}%"
    if bs.avg_noise_floor_dbm is not None:
        noise_clause = f"noise {bs.avg_noise_floor_dbm:.0f} dBm"
        util_line = f"{util_line} · {noise_clause}" if util_line else noise_clause
    if util_line:
        lines.append(util_line)

    if bs.avg_utilization_pct is not None:
        lines.append(f"  avg util  │ {_bar(bs.avg_utilization_pct)} {bs.avg_utilization_pct:.0f}%")
    if bs.max_utilization_pct is not None:
        lines.append(f"  peak util │ {_bar(bs.max_utilization_pct)} {bs.max_utilization_pct:.0f}%")

    lines.append("")
    lines.append("  Channel occupancy:")
    max_count = max(bs.channel_distribution.values(), default=0) or 1
    for ch, count in sorted(bs.channel_distribution.items(), key=lambda kv: int(kv[0])):
        width = 20
        filled = max(1, round((count / max_count) * width))
        bar = "■" * filled + " " * (width - filled)
        flag = " ⚠ co-channel" if count >= 3 and band_name in ("5", "6") else ""
        lines.append(f"    ch{ch:>4}  │ {bar} ({count}){flag}")

    if bs.allowed_channels:
        active = {int(c) for c in bs.channel_distribution}
        unused = [c for c in bs.allowed_channels if c not in active]
        if unused:
            lines.append(f"  Allowed but unused: {', '.join(str(c) for c in unused)}")
    return lines


def _render_ap_table(aps: list[APSummary]) -> list[str]:
    """Compact per-AP radio table."""
    if not aps:
        return []
    rows: list[tuple[str, str, str, str, str, str]] = [
        ("AP", "Platform", "Model", "2.4 GHz", "5 GHz", "6 GHz"),
    ]

    def _fmt(r: Radio | None) -> str:
        if r is None:
            return "—"
        parts = []
        if r.channel:
            parts.append(f"ch{r.channel}")
        if r.bandwidth_mhz:
            parts.append(f"{r.bandwidth_mhz}MHz")
        if r.power_dbm is not None:
            parts.append(f"{r.power_dbm:.0f}dBm")
        if r.channel_utilization_pct is not None:
            parts.append(f"{r.channel_utilization_pct:.0f}%util")
        return " ".join(parts) if parts else "—"

    for ap in aps:
        by_band = {r.band: r for r in ap.radios}
        name = ap.name or "(unnamed)"
        if not ap.connected:
            name = f"{name} (offline)"
        rows.append(
            (
                name,
                ap.platform,
                ap.model or "—",
                _fmt(by_band.get("2.4")),
                _fmt(by_band.get("5")),
                _fmt(by_band.get("6")),
            )
        )

    widths = [max(len(r[i]) for r in rows) for i in range(6)]
    lines: list[str] = []
    for i, row in enumerate(rows):
        lines.append("  " + "  ".join(cell.ljust(widths[j]) for j, cell in enumerate(row)))
        if i == 0:
            lines.append("  " + "  ".join("─" * widths[j] for j in range(6)))
    return lines


def _render_report(report: SiteRFReport) -> str:
    """Produce a human-readable markdown/ASCII report from the structured data."""
    lines: list[str] = []
    lines.append(f"# RF Check — {report.site_name}")
    lines.append("")
    lines.append(report.headline)
    lines.append("")
    if report.platforms_matched:
        lines.append(f"Platforms: queried={report.platforms_queried}, matched={report.platforms_matched}")
    if report.mist and report.mist.rf_template_name:
        lines.append(f"Mist RF template: {report.mist.rf_template_name}")
    lines.append("")

    for band_name in ("2.4", "5", "6"):
        bs = report.bands.get(band_name)  # type: ignore[arg-type]
        if not bs:
            continue
        lines.extend(_render_channel_distribution(band_name, bs))
        lines.append("")

    if report.aps:
        lines.append("## Per-AP radio snapshot")
        lines.append("")
        lines.extend(_render_ap_table(report.aps))
        lines.append("")

    if report.recommendations:
        lines.append("## Recommendations")
        lines.append("")
        for rec in report.recommendations:
            lines.append(f"- {rec}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# --- Registration --------------------------------------------------------


def register(mcp: Any, config: Any) -> None:
    """Register the cross-platform site_rf_check tool.

    Requires at least one of Mist or Central to be enabled — those are the
    platforms that own AP/radio telemetry.
    """
    if not (config.mist or config.central):
        logger.info("site_rf_check: skipped (neither Mist nor Central enabled)")
        return

    @mcp.tool(
        annotations={
            "title": "Cross-platform site RF check",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
            "idempotentHint": True,
        },
    )
    async def site_rf_check(
        ctx: Context,
        site_name: Annotated[
            str | None,
            Field(
                description=(
                    "Exact site name as shown in Mist and/or Central. "
                    "When omitted, the tool returns a list of selectable sites "
                    "(with AP counts per platform) in the `site_options` field "
                    "instead of a full RF report — call back with one of those "
                    "names. The `platform` filter still applies when listing."
                ),
                default=None,
            ),
        ] = None,
        platform: Annotated[
            str | list[str] | None,
            Field(
                description=(
                    "Optional platform filter. Omit (null) to query every enabled RF "
                    "platform (Mist + Central) — the normal cross-platform aggregation. "
                    "Pass one name ('mist' or 'central') or a list (['mist','central']) to "
                    "restrict the report. ClearPass, Apstra, and GreenLake are not valid — "
                    "they don't expose per-AP RF telemetry."
                ),
                default=None,
            ),
        ] = None,
        max_aps_per_platform: Annotated[
            int,
            Field(
                description=(
                    "Cap on per-AP detail fetches per platform (Central fans out serial-by-serial). "
                    "Default 50. Lower for faster responses on large sites; raise to cover more APs."
                ),
                default=50,
                ge=1,
                le=500,
            ),
        ] = 50,
        include_rendered_report: Annotated[
            bool,
            Field(
                description=(
                    "When true (default), include a pre-rendered markdown/ASCII RF dashboard in "
                    "the `rendered_report` field — per-band channel occupancy bars, utilization "
                    "meters, per-AP radio table. Displays directly in chat even if the client "
                    "doesn't draw charts. Set false for scripted/bulk callers that only want the "
                    "structured data."
                ),
                default=True,
            ),
        ] = True,
    ) -> SiteRFReport:
        """Aggregate per-AP RF state across enabled HPE networking platforms.

        Pulls live per-band channel, power, utilization, and noise floor for
        every AP at a site from Mist AND Central in parallel, aggregates the
        channel distribution and utilization per band (2.4 / 5 / 6 GHz), and
        returns a single compact report with recommendations.

        Use when the user asks about channel planning, RF health, 5/6 GHz
        spectrum, co-channel interference, or "how is my Wi-Fi doing" in
        terms of radio-layer behavior. Do not limit the query to a single
        vendor unless the user explicitly asks — this tool exists precisely
        because mixed Mist + Central deployments need both sides queried.

        The report includes:
        - Per-band summary (ch distribution, avg/max util, noise floor, allowed channels from the Mist RF template)
        - Per-AP radios (name, model, band, channel, power, util, noise)
        - Recommendations (co-channel clusters, high util, elevated noise)
        - A pre-rendered ASCII dashboard in `rendered_report`

        When `site_name` is omitted, the tool returns a list of selectable
        sites (with per-platform AP counts) in `site_options` instead of a
        full RF report — the `platform` filter still applies to the listing.
        Re-call with `site_name=<name>` to get the full report.
        """
        config = ctx.lifespan_context["config"]

        enabled: list[str] = []
        if config.mist:
            enabled.append("mist")
        if config.central:
            enabled.append("central")

        wanted = _normalize_rf_platform_filter(platform, enabled)
        query_mist = config.mist is not None and "mist" in wanted
        query_central = config.central is not None and "central" in wanted

        platforms_queried: list[str] = []
        if query_mist:
            platforms_queried.append("mist")
        if query_central:
            platforms_queried.append("central")

        # Site picker: site_name omitted -> return selectable sites, not a full RF report.
        if not site_name:
            enum_tasks: list[Any] = []
            if query_mist:
                enum_tasks.append(_list_mist_site_options(ctx))
            if query_central:
                enum_tasks.append(_list_central_site_options(ctx))
            enum_results = await asyncio.gather(*enum_tasks, return_exceptions=True)
            merged: list[SiteOption] = []
            for r in enum_results:
                if isinstance(r, list):
                    merged.extend(r)
            ordered = _merge_site_options(merged)

            headline = (
                f"No site_name given — {len(ordered)} site(s) available on {platforms_queried}. "
                "Call back with `site_name=<one of the listed names>`."
            )
            report = SiteRFReport(
                site_name="(not specified)",
                platforms_queried=platforms_queried,
                platforms_matched=[],
                headline=headline,
                site_options=ordered,
            )
            if include_rendered_report:
                report.rendered_report = _render_site_options(ordered)
            return report

        tasks: list[Any] = []
        if query_mist:
            tasks.append(_collect_mist(ctx, site_name))
        if query_central:
            tasks.append(_collect_central(ctx, site_name, max_aps_per_platform))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        mist_summary: MistRF | None = None
        central_summary: CentralRF | None = None
        all_aps: list[APSummary] = []
        idx = 0
        if query_mist:
            r = results[idx]
            if isinstance(r, tuple):
                mist_summary, mist_aps = r
                all_aps.extend(mist_aps)
            else:
                mist_summary = MistRF(error=str(r))
            idx += 1
        if query_central:
            r = results[idx]
            if isinstance(r, tuple):
                central_summary, central_aps = r
                all_aps.extend(central_aps)
            else:
                central_summary = CentralRF(error=str(r))
            idx += 1

        mist_template = mist_summary.rf_template_allowed if mist_summary else {}
        bands = _aggregate_bands(all_aps, mist_template)

        matched: list[str] = []
        if mist_summary and mist_summary.found:
            matched.append("mist")
        if central_summary and central_summary.found:
            matched.append("central")

        headline, recommendations = _synthesize(
            site_name,
            bands,
            all_aps,
            mist_summary,
            central_summary,
        )

        logger.info(
            "site_rf_check: site='{}' matched={} aps={}",
            site_name,
            matched,
            len(all_aps),
        )

        report = SiteRFReport(
            site_name=site_name,
            platforms_queried=platforms_queried,
            platforms_matched=matched,
            headline=headline,
            bands=bands,
            aps=all_aps,
            mist=mist_summary,
            central=central_summary,
            recommendations=recommendations,
        )
        if include_rendered_report:
            report.rendered_report = _render_report(report)
        return report

    logger.info("Cross-platform: registered site_rf_check tool")
