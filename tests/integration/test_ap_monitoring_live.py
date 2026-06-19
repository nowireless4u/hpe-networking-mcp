"""Integration tests for AP monitoring tools against live Central API."""

import pytest

from hpe_networking_mcp.platforms.central.tools.monitoring import (
    central_get_ap_details,
    central_get_ap_wlans,
    central_get_aps,
)

pytestmark = pytest.mark.integration


async def test_get_aps_no_filter(live_ctx):
    """Verify central_get_aps returns the uniform {"items": [...]} collection (#491)."""
    result = await central_get_aps(live_ctx)
    assert isinstance(result, dict)
    items = result["items"]
    assert isinstance(items, list)
    assert all(isinstance(ap, dict) for ap in items)


async def test_get_aps_online_filter(live_ctx):
    """Verify filtering by ONLINE status."""
    result = await central_get_aps(live_ctx, status="ONLINE")
    assert isinstance(result, dict)
    assert isinstance(result["items"], list)


async def test_get_aps_offline_filter(live_ctx):
    """Verify filtering by OFFLINE status."""
    result = await central_get_aps(live_ctx, status="OFFLINE")
    assert isinstance(result, dict)
    assert isinstance(result["items"], list)


async def test_get_ap_details_for_known_ap(live_ctx):
    """Get details for the first AP found."""
    aps = (await central_get_aps(live_ctx))["items"]
    if not aps:
        pytest.skip("No APs available")
    serial = aps[0].get("serialNumber", aps[0].get("serial_number"))
    if not serial:
        pytest.skip("AP has no serial number")
    result = await central_get_ap_details(live_ctx, serial_number=serial)
    assert isinstance(result, (dict, str))


async def test_get_ap_wlans_for_known_ap(live_ctx):
    """Get WLANs for the first online AP."""
    aps = (await central_get_aps(live_ctx, status="ONLINE"))["items"]
    if not aps:
        pytest.skip("No online APs available")
    serial = aps[0].get("serialNumber", aps[0].get("serial_number"))
    if not serial:
        pytest.skip("AP has no serial number")
    result = await central_get_ap_wlans(live_ctx, serial_number=serial)
    assert isinstance(result, dict)
    assert isinstance(result["items"], list)


async def test_get_ap_wlans_name_filter(live_ctx):
    """Verify wlan_name filter works client-side."""
    aps = (await central_get_aps(live_ctx, status="ONLINE"))["items"]
    if not aps:
        pytest.skip("No online APs available")
    serial = aps[0].get("serialNumber", aps[0].get("serial_number"))
    if not serial:
        pytest.skip("AP has no serial number")

    all_wlans = (await central_get_ap_wlans(live_ctx, serial_number=serial))["items"]
    if not all_wlans:
        pytest.skip("No WLANs on this AP")

    target = all_wlans[0].get("wlanName")
    filtered = (await central_get_ap_wlans(live_ctx, serial_number=serial, wlan_name=target))["items"]
    assert all(w.get("wlanName") == target for w in filtered)
