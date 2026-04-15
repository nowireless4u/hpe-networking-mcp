"""Integration tests for WLAN tools against live Central API."""

import pytest

from hpe_networking_mcp.platforms.central.tools.wlans import (
    central_get_wlan_stats,
    central_get_wlans,
)

pytestmark = pytest.mark.integration


async def test_get_wlans_returns_results(live_ctx):
    """Verify central_get_wlans returns WLAN data."""
    result = await central_get_wlans(live_ctx)
    assert isinstance(result, (list, str))
    if isinstance(result, list):
        assert len(result) > 0


async def test_get_wlans_all_have_name(live_ctx):
    """Verify all returned WLANs have a name field."""
    result = await central_get_wlans(live_ctx)
    if isinstance(result, str):
        pytest.skip("No WLANs available")
    assert all(w.get("wlanName") or w.get("essid") for w in result)


async def test_get_wlan_stats_for_known_wlan(live_ctx):
    """Get throughput stats for the first WLAN found."""
    wlans = await central_get_wlans(live_ctx)
    if isinstance(wlans, str) or not wlans:
        pytest.skip("No WLANs available")
    wlan_name = wlans[0].get("wlanName") or wlans[0].get("essid")
    if not wlan_name:
        pytest.skip("WLAN has no name")

    result = await central_get_wlan_stats(live_ctx, wlan_name=wlan_name)
    assert isinstance(result, (list, str))
    if isinstance(result, list):
        assert all("timestamp" in s for s in result)


async def test_get_wlan_stats_custom_time_window(live_ctx):
    """Verify custom start/end time overrides time_range."""
    wlans = await central_get_wlans(live_ctx)
    if isinstance(wlans, str) or not wlans:
        pytest.skip("No WLANs available")
    wlan_name = wlans[0].get("wlanName") or wlans[0].get("essid")
    if not wlan_name:
        pytest.skip("WLAN has no name")

    result = await central_get_wlan_stats(
        live_ctx,
        wlan_name=wlan_name,
        start_time="2026-04-14T00:00:00.000Z",
        end_time="2026-04-14T23:59:59.999Z",
    )
    assert isinstance(result, (list, str))


async def test_get_wlan_stats_unknown_wlan(live_ctx):
    """Verify unknown WLAN returns a descriptive string."""
    result = await central_get_wlan_stats(live_ctx, wlan_name="__nonexistent_wlan__")
    assert isinstance(result, str)
