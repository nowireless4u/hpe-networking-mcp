"""Unit tests for hpe_networking_mcp.platforms.central.utils — OData filter, time windows, helpers."""

from datetime import datetime, timedelta, timezone

import pytest

from hpe_networking_mcp.platforms.central.utils import (
    FilterField,
    _safe_float,
    build_odata_filter,
    compute_time_window,
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
        now = datetime.now(timezone.utc)
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0
        assert start.date() == now.date()

    def test_yesterday(self):
        start, end = compute_time_window("yesterday")
        now = datetime.now(timezone.utc)
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
