"""Unit tests for hpe_networking_mcp.platforms.central.utils — OData filter, time windows, helpers."""

from datetime import UTC, datetime, timedelta

import pytest

from hpe_networking_mcp.platforms.central.utils import (
    FilterField,
    _safe_float,
    build_odata_filter,
    compute_time_window,
    process_site_health_data,
    transform_to_site_data,
)

# ---------------------------------------------------------------------------
# build_odata_filter
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBuildOdataFilter:
    def test_single_field_single_value(self):
        ff = FilterField(api_field="status")
        result = build_odata_filter([(ff, "Up")])
        assert result == "status eq 'Up'"

    def test_comma_separated_values_uses_in(self):
        ff = FilterField(api_field="deviceType")
        result = build_odata_filter([(ff, "AP,Switch")])
        assert result == "deviceType in ('AP', 'Switch')"

    def test_returns_none_for_empty_pairs(self):
        result = build_odata_filter([])
        assert result is None

    def test_multiple_fields_joined_with_and(self):
        ff1 = FilterField(api_field="status")
        ff2 = FilterField(api_field="type")
        result = build_odata_filter([(ff1, "Up"), (ff2, "AP")])
        assert result == "status eq 'Up' and type eq 'AP'"

    def test_validates_against_allowed_values(self):
        ff = FilterField(api_field="status", allowed_values=["Up", "Down"])
        with pytest.raises(ValueError, match="Invalid value"):
            build_odata_filter([(ff, "Unknown")])

    def test_allowed_values_pass_when_valid(self):
        ff = FilterField(api_field="status", allowed_values=["Up", "Down"])
        result = build_odata_filter([(ff, "Up")])
        assert result == "status eq 'Up'"

    def test_allowed_values_with_comma_separated(self):
        ff = FilterField(api_field="status", allowed_values=["Up", "Down"])
        result = build_odata_filter([(ff, "Up,Down")])
        assert result == "status in ('Up', 'Down')"

    def test_allowed_values_rejects_invalid_in_comma_list(self):
        ff = FilterField(api_field="status", allowed_values=["Up", "Down"])
        with pytest.raises(ValueError, match="Invalid value"):
            build_odata_filter([(ff, "Up,Unknown")])

    def test_no_allowed_values_means_free_text(self):
        ff = FilterField(api_field="name")
        result = build_odata_filter([(ff, "anything-goes")])
        assert result == "name eq 'anything-goes'"


# ---------------------------------------------------------------------------
# compute_time_window
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestComputeTimeWindow:
    def test_last_1h(self):
        start, end = compute_time_window("last_1h")
        assert end - start <= timedelta(hours=1, seconds=1)
        assert end - start >= timedelta(minutes=59)

    def test_last_6h(self):
        start, end = compute_time_window("last_6h")
        assert end - start <= timedelta(hours=6, seconds=1)
        assert end - start >= timedelta(hours=5, minutes=59)

    def test_last_24h(self):
        start, end = compute_time_window("last_24h")
        assert end - start <= timedelta(hours=24, seconds=1)
        assert end - start >= timedelta(hours=23, minutes=59)

    def test_last_7d(self):
        start, end = compute_time_window("last_7d")
        assert end - start <= timedelta(days=7, seconds=1)
        assert end - start >= timedelta(days=6, hours=23)

    def test_last_30d(self):
        start, end = compute_time_window("last_30d")
        assert end - start <= timedelta(days=30, seconds=1)
        assert end - start >= timedelta(days=29, hours=23)

    def test_today(self):
        start, end = compute_time_window("today")
        now = datetime.now(UTC)
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0
        assert start.date() == now.date()

    def test_yesterday(self):
        start, end = compute_time_window("yesterday")
        now = datetime.now(UTC)
        yesterday = now - timedelta(days=1)
        assert start.date() == yesterday.date()
        assert start.hour == 0
        assert end.date() == yesterday.date()
        assert end.hour == 23
        assert end.minute == 59

    def test_invalid_range_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid time_range"):
            compute_time_window("last_99d")


# ---------------------------------------------------------------------------
# _safe_float
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSafeFloat:
    def test_converts_valid_int(self):
        assert _safe_float(42) == 42.0

    def test_converts_valid_float(self):
        assert _safe_float(3.14) == 3.14

    def test_converts_valid_string(self):
        assert _safe_float("1.5") == 1.5

    def test_returns_none_for_invalid_string(self):
        assert _safe_float("not-a-number") is None

    def test_returns_none_for_none(self):
        assert _safe_float(None) is None

    def test_returns_none_for_empty_string(self):
        assert _safe_float("") is None


# ---------------------------------------------------------------------------
# process_site_health_data + transform_to_site_data — pinned to the actual
# Aruba Central /sites-health response shape (siteName, clients.count,
# devices.count, alerts.totalCount, *.health.groups[]). Captured live from
# a real tenant 2026-04-26. If the API ever renames these fields again,
# these tests fail loudly instead of silently returning empty/zero data
# (root cause of Zach's "0 clients" bug — fix landed in this PR).
# ---------------------------------------------------------------------------


def _sample_sites_health_response() -> list[dict]:
    """Single-site fragment matching the live ``/sites-health`` response shape."""
    return [
        {
            "siteName": "HOME",
            "id": "18413656377",
            "address": {"city": "Anytown", "country": "US"},
            "location": {"latitude": "39.0", "longitude": "-77.0"},
            "health": {
                "groups": [
                    {"name": "Poor", "value": 0},
                    {"name": "Fair", "value": 0},
                    {"name": "Good", "value": 1},
                ]
            },
            "devices": {
                "count": 17,
                "health": {
                    "groups": [
                        {"name": "Poor", "value": 6},
                        {"name": "Fair", "value": 1},
                        {"name": "Good", "value": 10},
                    ]
                },
            },
            "clients": {
                "count": 38,
                "health": {
                    "groups": [
                        {"name": "Poor", "value": 0},
                        {"name": "Fair", "value": 0},
                        {"name": "Good", "value": 38},
                    ]
                },
            },
            "alerts": {
                "totalCount": 3,
                "groups": [{"name": "Critical", "count": 2}],
            },
        }
    ]


def _sample_sites_device_health_response() -> list[dict]:
    """Single-site fragment matching the live ``/sites-device-health`` response shape."""
    return [
        {
            "siteName": "HOME",
            "id": "18413656377",
            "type": "v1",
            "deviceTypes": [
                {
                    "name": "Access Points",
                    "health": {
                        "groups": [
                            {"name": "Poor", "value": 1},
                            {"name": "Fair", "value": 0},
                            {"name": "Good", "value": 3},
                        ]
                    },
                },
            ],
        }
    ]


def _sample_sites_client_health_response() -> list[dict]:
    """Single-site fragment matching the live ``/sites-client-health`` response shape."""
    return [
        {
            "siteName": "HOME",
            "id": "18413656377",
            "type": "v1",
            "clientTypes": [
                {
                    "name": "Wired",
                    "health": {
                        "groups": [
                            {"name": "Poor", "value": 0},
                            {"name": "Fair", "value": 0},
                            {"name": "Good", "value": 4},
                        ]
                    },
                },
                {
                    "name": "Wireless",
                    "health": {
                        "groups": [
                            {"name": "Poor", "value": 0},
                            {"name": "Fair", "value": 0},
                            {"name": "Good", "value": 34},
                        ]
                    },
                },
            ],
        }
    ]


@pytest.mark.unit
class TestProcessSiteHealthData:
    """Regression coverage for the ``name`` -> ``siteName`` field-rename bug."""

    def test_processes_sites_keyed_by_site_name(self):
        """Filtering on ``"name"`` (the old code) drops every site silently.
        With ``"siteName"`` we keep them all.
        """
        result = process_site_health_data(
            _sample_sites_health_response(),
            _sample_sites_device_health_response(),
            _sample_sites_client_health_response(),
        )
        assert "HOME" in result, (
            "process_site_health_data must key on the 'siteName' field — "
            "if this fails, the API response shape changed or the field-rename regressed"
        )
        assert len(result) == 1

    def test_device_details_merge_on_site_name(self):
        """Device-health enrichment must merge on ``siteName``, not ``name``."""
        result = process_site_health_data(
            _sample_sites_health_response(),
            _sample_sites_device_health_response(),
            _sample_sites_client_health_response(),
        )
        details = result["HOME"].metrics.devices.get("Details")
        assert details is not None, "deviceTypes details missing — siteName merge regression"
        assert "Access Points" in details

    def test_client_details_merge_on_site_name(self):
        """Client-health enrichment must merge on ``siteName``, not ``name``."""
        result = process_site_health_data(
            _sample_sites_health_response(),
            _sample_sites_device_health_response(),
            _sample_sites_client_health_response(),
        )
        details = result["HOME"].metrics.clients.get("Details")
        assert details is not None, "clientTypes details missing — siteName merge regression"
        assert "Wired" in details and "Wireless" in details


@pytest.mark.unit
class TestTransformToSiteData:
    """Regression coverage for the SiteData.name field — must read from siteName."""

    def test_name_is_read_from_site_name_field(self):
        """The previous implementation read ``site_raw["name"]`` which doesn't
        exist in the real response — yielding empty-string names everywhere.
        """
        site = transform_to_site_data(_sample_sites_health_response()[0])
        assert site.name == "HOME", f"Expected 'HOME', got '{site.name}' — siteName mapping regressed"

    def test_summary_total_derived_from_groups_when_count_present(self):
        """Per-site totals come from summing the health.groups[] values via
        the existing ``groups_to_map`` helper. Asserts the derivation works
        end-to-end against the real shape.
        """
        site = transform_to_site_data(_sample_sites_health_response()[0])
        assert site.metrics.devices["Summary"].get("Total") == 17
        assert site.metrics.clients["Summary"].get("Total") == 38
