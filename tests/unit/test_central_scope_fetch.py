"""Unit tests for central scope_fetch (the scope-tree data source).

Regression coverage for the retired route: ``cnxdevice/v1/debug/get_scope_data``
now gateway-404s ("404 Route Not Found"), which broke ``central_get_scope_tree``
and every tool built on the scope tree. The tree is now read from the
network-config scope routes.

Probed read-only on two tenants (US-1) 2026-10-30:
``cnxdevice/v1/debug/get_scope_data``   -> 404,
``network-config/v1/{global,sites,site-collections,device-groups}`` -> 200,
``network-config/v1alpha1/devices``     -> 200 (scopeId, siteId, deviceGroupId per device),
``network-config/v1/hierarchy?type=device&id=<serial>`` -> 200 (device paths, leaf to root).

Mocks ``retry_central_command`` / ``paginated_fetch`` at the import site.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hpe_networking_mcp.platforms.central.scope_builder import _build_tree

pytestmark = pytest.mark.unit

MOD = "hpe_networking_mcp.platforms.central.scope_fetch"

GLOBAL = {"scopeId": "g1", "id": "g1", "type": "network-config/global"}
COLLECTIONS = {"items": [{"scopeId": "sc1", "scopeName": "District"}], "total": 1}
SITES = {
    "items": [
        {"scopeId": "s1", "scopeName": "HQ", "collectionId": "sc1"},
        {"scopeId": "s2", "scopeName": "Annex", "collectionId": None},
    ],
    "total": 2,
}
GROUPS = {"items": [{"scopeId": "dg1", "scopeName": "AP-Group"}], "total": 1}
PERSONAS = {
    "device_type_list": [
        {"device-type": "AP", "supported-persona": [{"value": "CAMPUS_AP", "label": "Campus Access Point"}]}
    ]
}
DEVICES = {
    "items": [
        {"scopeName": "SER1", "scopeId": "d1", "siteId": "s1", "deviceGroupId": "dg1"},
        {"scopeName": "SER2", "scopeId": "d2", "siteId": None, "deviceGroupId": "dg1"},
    ],
    "total": 2,
}
INVENTORY = [
    {
        "serialNumber": "SER1",
        "deviceName": "ap-hq-1",
        "deviceType": "ACCESS_POINT",
        "model": "AP-635",
        "deviceFunction": "Campus Access Point",
        "macAddress": "aa:bb",
    },
    {
        "serialNumber": "SER2",
        "deviceName": "ap-2",
        "deviceType": "ACCESS_POINT",
        "model": "AP-515",
        "deviceFunction": "Campus Access Point",
    },
]


def _routes(devices_ok: bool = True):
    def fake(central_conn, api_method, api_path, api_params=None, **_):
        if api_path == "network-config/v1alpha1/devices" and not devices_ok:
            raise RuntimeError("404 Route Not Found")
        if api_path == "network-config/v1/hierarchy":
            serial = api_params["id"]
            dev = {"scopeId": "d1" if serial == "SER1" else "d2", "scopeType": "device"}
            if serial == "SER1":
                paths = [
                    [dev, {"scopeId": "dg1", "scopeType": "device_collection"}, {"scopeId": "g1", "scopeType": "org"}],
                    [
                        dev,
                        {"scopeId": "s1", "scopeType": "site"},
                        {"scopeId": "sc1", "scopeType": "site_collection"},
                        {"scopeId": "g1", "scopeType": "org"},
                    ],
                ]
            else:
                paths = [
                    [dev, {"scopeId": "dg1", "scopeType": "device_collection"}, {"scopeId": "g1", "scopeType": "org"}]
                ]
            return {"code": 200, "msg": {"items": [{"hierarchy": p} for p in paths]}}
        msg = {
            "network-config/v1/global": GLOBAL,
            "network-config/v1/site-collections": COLLECTIONS,
            "network-config/v1/sites": SITES,
            "network-config/v1/device-groups": GROUPS,
            "network-config/v1alpha1/device-persona-mapping": PERSONAS,
            "network-config/v1alpha1/devices": DEVICES,
        }[api_path]
        return {"code": 200, "msg": msg}

    return fake


async def _fetch(devices_ok: bool = True) -> dict:
    from hpe_networking_mcp.platforms.central.scope_fetch import fetch_scope_data

    with (
        patch(f"{MOD}.retry_central_command", side_effect=_routes(devices_ok)) as cmd,
        patch(f"{MOD}.paginated_fetch", return_value=INVENTORY),
    ):
        data = await fetch_scope_data(MagicMock())
    paths = [c.kwargs["api_path"] for c in cmd.call_args_list]
    assert "cnxdevice/v1/debug/get_scope_data" not in paths
    return data


def _by_id(data: dict) -> dict:
    return {n["scope_id"]: n for n in data["devices"]}


class TestFetchScopeData:
    async def test_container_scopes_and_paths(self):
        nodes = _by_id(await _fetch())
        assert nodes["g1"]["type"] == "GLOBAL"
        assert nodes["sc1"]["hier_path"] == ["sc1", "g1"]
        assert nodes["s1"]["hier_path"] == ["s1", "sc1", "g1"]
        assert nodes["s2"]["hier_path"] == ["s2", "g1"]
        assert nodes["dg1"]["type"] == "DEVICE_COLLECTION"

    async def test_devices_from_bulk_list(self):
        nodes = _by_id(await _fetch())
        d1, d2 = nodes["d1"], nodes["d2"]
        assert d1["type"] == "DEVICE"
        assert d1["hier_path"] == ["d1", "s1", "sc1", "g1"]
        assert d1["persona"] == "CAMPUS_AP"
        assert d1["meta"]["scope_name"] == "ap-hq-1"
        assert d1["meta"]["device_model"] == "AP-635"
        # No site: the device hangs off its device-group.
        assert d2["hier_path"] == ["d2", "dg1", "g1"]

    async def test_per_device_fallback_matches_bulk(self):
        bulk, fallback = _by_id(await _fetch()), _by_id(await _fetch(devices_ok=False))
        assert fallback["d1"]["hier_path"] == bulk["d1"]["hier_path"]
        assert fallback["d2"]["hier_path"] == bulk["d2"]["hier_path"]
        assert fallback.keys() == bulk.keys()

    async def test_tree_builds_from_fetched_nodes(self):
        tree = _build_tree(
            await _fetch(), {"scope-map": [{"scope-name": "s1", "persona": "CAMPUS_AP", "resource": "wlan/x"}]}
        )
        assert tree.root == "g1"
        assert tree.parent("d1").identifier == "s1"
        assert tree.parent("s1").identifier == "sc1"
        assert tree.get_node("s1").data["resources"].get_node("CAMPUS_AP") is not None
