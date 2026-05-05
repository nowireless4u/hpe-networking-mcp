"""Unit tests for the cross-platform ``site_rf_check`` tool."""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.site_rf_check import (
    APSummary,
    BandSummary,
    CentralRF,
    MistRF,
    Radio,
    SiteOption,
    SiteRFReport,
    _aggregate_bands,
    _band_key,
    _merge_site_options,
    _mist_band_from_stat_key,
    _normalize_rf_platform_filter,
    _parse_bandwidth_mhz,
    _parse_numeric,
    _parse_primary_channel,
    _render_report,
    _render_site_options,
    _synthesize,
)

# --- Parsers -------------------------------------------------------------


@pytest.mark.unit
class TestParsePrimaryChannel:
    def test_plain_int(self):
        assert _parse_primary_channel(6) == 6

    def test_plain_string(self):
        assert _parse_primary_channel("36") == 36

    def test_aruba_secondary_suffix(self):
        # "165S" = primary 165 with a secondary 20MHz channel
        assert _parse_primary_channel("165S") == 165

    def test_aruba_triplet_suffix(self):
        # "49T+" = Wi-Fi 6E 320MHz bonded channel notation
        assert _parse_primary_channel("49T+") == 49

    def test_none(self):
        assert _parse_primary_channel(None) is None

    def test_empty_string(self):
        assert _parse_primary_channel("") is None

    def test_non_numeric_garbage(self):
        assert _parse_primary_channel("auto") is None


@pytest.mark.unit
class TestParseNumeric:
    def test_plain_int(self):
        assert _parse_numeric(42) == 42.0

    def test_plain_float(self):
        assert _parse_numeric(42.5) == 42.5

    def test_unit_suffix(self):
        assert _parse_numeric("28 dBm") == 28.0

    def test_negative(self):
        assert _parse_numeric("-93") == -93.0

    def test_percent_suffix(self):
        assert _parse_numeric("32") == 32.0

    def test_none(self):
        assert _parse_numeric(None) is None


@pytest.mark.unit
class TestParseBandwidth:
    def test_with_unit(self):
        assert _parse_bandwidth_mhz("160 MHz") == 160

    def test_plain_int(self):
        assert _parse_bandwidth_mhz(20) == 20

    def test_none(self):
        assert _parse_bandwidth_mhz(None) is None


@pytest.mark.unit
class TestBandKey:
    def test_central_strings(self):
        assert _band_key("2.4 GHz") == "2.4"
        assert _band_key("5 GHz") == "5"
        assert _band_key("6 GHz") == "6"

    def test_mist_numeric_strings(self):
        assert _band_key("24") == "2.4"
        assert _band_key("5") == "5"
        assert _band_key("6") == "6"

    def test_mist_radio_stat_prefix(self):
        assert _mist_band_from_stat_key("band_24") == "2.4"
        assert _mist_band_from_stat_key("band_5") == "5"
        assert _mist_band_from_stat_key("band_6") == "6"

    def test_unknown(self):
        assert _band_key("60 GHz") is None
        assert _band_key(None) is None


# --- Platform filter -----------------------------------------------------


@pytest.mark.unit
class TestNormalizeRFPlatformFilter:
    def test_none_returns_all_enabled(self):
        assert _normalize_rf_platform_filter(None, ["mist", "central"]) == ["mist", "central"]

    def test_missing_enabled_excluded(self):
        # mist disabled → only central returned
        assert _normalize_rf_platform_filter(None, ["central"]) == ["central"]

    def test_single_string(self):
        assert _normalize_rf_platform_filter("mist", ["mist", "central"]) == ["mist"]

    def test_list(self):
        assert _normalize_rf_platform_filter(["central", "mist"], ["mist", "central"]) == ["central", "mist"]

    def test_case_insensitive(self):
        assert _normalize_rf_platform_filter("MIST", ["mist"]) == ["mist"]

    def test_non_rf_platform_dropped(self):
        # clearpass, apstra, greenlake aren't RF platforms
        assert _normalize_rf_platform_filter("clearpass", ["mist", "central"]) == []
        assert _normalize_rf_platform_filter(["apstra", "mist"], ["mist", "central"]) == ["mist"]


# --- Aggregation ---------------------------------------------------------


def _ap(name: str, platform: str, *radios: Radio, connected: bool = True) -> APSummary:
    return APSummary(
        name=name,
        platform=platform,  # type: ignore[arg-type]
        connected=connected,
        radios=list(radios),
    )


def _r(band: str, channel: int, power: float = 20.0, util: float = 15.0, noise: float = -90.0) -> Radio:
    return Radio(
        band=band,  # type: ignore[arg-type]
        channel=str(channel),
        primary_channel=channel,
        bandwidth_mhz=20 if band == "2.4" else 80,
        power_dbm=power,
        channel_utilization_pct=util,
        noise_floor_dbm=noise,
        status="UP",
    )


@pytest.mark.unit
class TestAggregateBands:
    def test_empty(self):
        bands = _aggregate_bands([], {})
        assert bands["2.4"].radios_active == 0
        assert bands["5"].radios_active == 0
        assert bands["6"].radios_active == 0

    def test_channel_distribution(self):
        aps = [
            _ap("A", "central", _r("2.4", 1), _r("5", 36)),
            _ap("B", "central", _r("2.4", 1), _r("5", 149)),
            _ap("C", "mist", _r("2.4", 6), _r("5", 36)),
        ]
        bands = _aggregate_bands(aps, {})
        assert bands["2.4"].channel_distribution == {"1": 2, "6": 1}
        assert bands["5"].channel_distribution == {"36": 2, "149": 1}
        assert bands["6"].radios_active == 0

    def test_util_avg_and_max(self):
        aps = [
            _ap("A", "central", _r("5", 36, util=30)),
            _ap("B", "central", _r("5", 149, util=70)),
        ]
        bands = _aggregate_bands(aps, {})
        assert bands["5"].avg_utilization_pct == 50.0
        assert bands["5"].max_utilization_pct == 70.0

    def test_noise_floor_average(self):
        aps = [
            _ap("A", "central", _r("5", 36, noise=-85)),
            _ap("B", "central", _r("5", 149, noise=-95)),
        ]
        bands = _aggregate_bands(aps, {})
        assert bands["5"].avg_noise_floor_dbm == -90.0

    def test_mist_template_allowed_channels_piped_through(self):
        bands = _aggregate_bands([], {"24": [1, 6, 11], "5": None, "6": None})
        assert bands["2.4"].allowed_channels == [1, 6, 11]
        assert bands["5"].allowed_channels is None

    def test_disconnected_aps_excluded_from_radio_stats(self):
        # disconnected AP contributes to ap_count (has `radios` list from history)
        # but its radios are NOT included in the per-band aggregation.
        aps = [
            _ap("online", "central", _r("5", 36, util=50)),
            _ap("offline", "mist", _r("5", 149, util=80), connected=False),
        ]
        bands = _aggregate_bands(aps, {})
        # only the online AP's radio counts
        assert bands["5"].radios_active == 1
        assert bands["5"].channel_distribution == {"36": 1}
        assert bands["5"].avg_utilization_pct == 50.0


# --- Synthesis -----------------------------------------------------------


@pytest.mark.unit
class TestSynthesize:
    def _bands(
        self,
        util_max: dict[str, float] | None = None,
        noise_avg: dict[str, float] | None = None,
        channel_dist: dict[str, dict[str, int]] | None = None,
    ) -> dict[str, BandSummary]:
        util_max = util_max or {}
        noise_avg = noise_avg or {}
        channel_dist = channel_dist or {}
        bands: dict[str, BandSummary] = {}
        for band in ("2.4", "5", "6"):
            dist = channel_dist.get(band, {})
            bands[band] = BandSummary(
                band=band,  # type: ignore[arg-type]
                ap_count=max(3, sum(dist.values())),
                radios_active=sum(dist.values()),
                channel_distribution=dist,
                max_utilization_pct=util_max.get(band),
                avg_noise_floor_dbm=noise_avg.get(band),
            )
        return bands

    def test_co_channel_cluster_flagged_5ghz(self):
        bands = self._bands(channel_dist={"5": {"36": 3}})
        _, recs = _synthesize("X", bands, [_ap("A", "central", _r("5", 36))] * 3, None, None)
        assert any("5 GHz" in r and "channel 36" in r for r in recs)

    def test_co_channel_below_threshold_not_flagged(self):
        bands = self._bands(channel_dist={"5": {"36": 2}})
        _, recs = _synthesize("X", bands, [_ap("A", "central", _r("5", 36))] * 2, None, None)
        assert not any("co-channel" in r.lower() or "channel 36" in r for r in recs)

    def test_co_channel_not_flagged_24ghz(self):
        # 2.4 GHz only has 3 non-overlapping channels, so 3 APs on the same one is normal.
        bands = self._bands(channel_dist={"2.4": {"1": 3}})
        _, recs = _synthesize("X", bands, [_ap("A", "central", _r("2.4", 1))] * 3, None, None)
        assert not any("channel 1" in r for r in recs)

    def test_high_utilization_flagged(self):
        bands = self._bands(
            util_max={"5": 85.0},
            channel_dist={"5": {"36": 1}},
        )
        _, recs = _synthesize("X", bands, [_ap("A", "central", _r("5", 36, util=85))], None, None)
        assert any("utilization" in r.lower() for r in recs)

    def test_elevated_noise_floor_flagged(self):
        bands = self._bands(
            noise_avg={"5": -65.0},
            channel_dist={"5": {"36": 1}},
        )
        _, recs = _synthesize("X", bands, [_ap("A", "central", _r("5", 36, noise=-65))], None, None)
        assert any("noise" in r.lower() for r in recs)

    def test_healthy_site_no_recommendations(self):
        bands = self._bands(
            util_max={"5": 20.0},
            noise_avg={"5": -90.0},
            channel_dist={"5": {"36": 1, "149": 1}},
        )
        headline, recs = _synthesize(
            "X",
            bands,
            [_ap("A", "central", _r("5", 36)), _ap("B", "central", _r("5", 149))],
            MistRF(found=True, ap_count=2, aps_connected=2),
            None,
        )
        assert recs == []
        assert "5GHz" in headline

    def test_site_not_found_headline(self):
        bands = self._bands()
        headline, _ = _synthesize("X", bands, [], None, None)
        assert "not found" in headline.lower()


# --- Renderer ------------------------------------------------------------


@pytest.mark.unit
class TestRenderReport:
    def test_smoke(self):
        report = SiteRFReport(
            site_name="HQ",
            platforms_queried=["mist", "central"],
            platforms_matched=["mist", "central"],
            headline="Site 'HQ': all good",
            bands={
                "2.4": BandSummary(band="2.4", ap_count=2, radios_active=2, channel_distribution={"1": 2}),
                "5": BandSummary(band="5", ap_count=0, radios_active=0, channel_distribution={}),
                "6": BandSummary(band="6", ap_count=0, radios_active=0, channel_distribution={}),
            },
            aps=[
                _ap("AP1", "central", _r("2.4", 1), _r("5", 36)),
                _ap("AP2", "mist", _r("2.4", 1), connected=True),
            ],
            recommendations=["Look into channel 1 density"],
        )
        out = _render_report(report)
        # Headline + bands header + AP table + recommendations all present
        assert "# RF Check — HQ" in out
        assert "Site 'HQ'" in out
        assert "### 2.4 GHz — 2 radio(s)" in out
        assert "ch   1" in out  # channel occupancy line
        assert "## Per-AP radio snapshot" in out
        assert "AP1" in out and "AP2" in out
        assert "## Recommendations" in out
        assert "Look into channel 1 density" in out

    def test_co_channel_warning_suffix_rendered(self):
        report = SiteRFReport(
            site_name="X",
            platforms_queried=["central"],
            platforms_matched=["central"],
            headline="",
            bands={
                "2.4": BandSummary(band="2.4", ap_count=0, radios_active=0),
                "5": BandSummary(
                    band="5",
                    ap_count=3,
                    radios_active=3,
                    channel_distribution={"36": 3},
                ),
                "6": BandSummary(band="6", ap_count=0, radios_active=0),
            },
            aps=[],
        )
        out = _render_report(report)
        assert "co-channel" in out

    def test_no_active_radios_per_band(self):
        report = SiteRFReport(
            site_name="X",
            platforms_queried=["mist"],
            platforms_matched=["mist"],
            headline="no APs",
            bands={
                "2.4": BandSummary(band="2.4", ap_count=0, radios_active=0, allowed_channels=[1, 6, 11]),
                "5": BandSummary(band="5", ap_count=0, radios_active=0),
                "6": BandSummary(band="6", ap_count=0, radios_active=0),
            },
            aps=[],
        )
        out = _render_report(report)
        # Should surface allowed-but-unused context even when no radios are active
        assert "no active radios" in out
        assert "Template allows" in out


# --- Site picker ---------------------------------------------------------


@pytest.mark.unit
class TestMergeSiteOptions:
    def test_sort_by_online_then_total_then_name(self):
        opts = [
            SiteOption(name="zeta", platform="mist", ap_count=2, online_ap_count=2),
            SiteOption(name="alpha", platform="central", ap_count=10, online_ap_count=0),
            SiteOption(name="beta", platform="mist", ap_count=5, online_ap_count=5),
            SiteOption(name="gamma", platform="central", ap_count=0, online_ap_count=None),
        ]
        ordered = _merge_site_options(opts)
        names = [o.name for o in ordered]
        # most-online first (beta=5, zeta=2), then by total (alpha=10 > gamma=0)
        assert names == ["beta", "zeta", "alpha", "gamma"]

    def test_empty(self):
        assert _merge_site_options([]) == []


@pytest.mark.unit
class TestRenderSiteOptions:
    def test_empty(self):
        out = _render_site_options([])
        assert "No sites available" in out

    def test_with_options(self):
        opts = [
            SiteOption(name="HQ", platform="central", ap_count=3, online_ap_count=3),
            SiteOption(name="HQ", platform="mist", ap_count=5, online_ap_count=0),
        ]
        out = _render_site_options(opts)
        assert "HQ" in out
        assert "central" in out and "mist" in out
        assert "site_rf_check" in out
        # Header columns rendered
        assert "APs total" in out and "APs online" in out

    def test_truncation_at_50(self):
        opts = [SiteOption(name=f"site-{i:02d}", platform="central", ap_count=i) for i in range(60)]
        out = _render_site_options(opts)
        assert "and 10 more sites" in out


# --- Models --------------------------------------------------------------


@pytest.mark.unit
class TestModels:
    def test_site_rf_report_serializes_with_rendered_field(self):
        report = SiteRFReport(
            site_name="HQ",
            platforms_queried=["mist"],
            platforms_matched=["mist"],
            headline="ok",
            rendered_report="# test",
        )
        dumped = report.model_dump()
        assert dumped["rendered_report"] == "# test"
        assert dumped["site_name"] == "HQ"

    def test_mist_central_summaries_default_missing(self):
        # A report with no platforms found should still serialize cleanly.
        report = SiteRFReport(
            site_name="Nonexistent",
            platforms_queried=["mist", "central"],
            platforms_matched=[],
            headline="Site not found",
            mist=MistRF(),
            central=CentralRF(),
        )
        dumped = report.model_dump()
        assert dumped["mist"]["found"] is False
        assert dumped["central"]["found"] is False
