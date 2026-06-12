"""Unit tests for ``translations/preprocessing/aos8_wlan_ssid.py``.

Covers the virtual_ap + ssid_prof join, the opmode mapping table, the
target_mode → forward-mode fork, named/numeric VLAN handling, the overlay flag,
and the deferred bridged_and_tunneled guard. Generic placeholder data only.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.preprocessing.aos8_wlan_ssid import (
    preprocess_wlan_ssid,
)

pytestmark = pytest.mark.unit


def _vap(vlan: str = "corp-vlan", ssid_name: str = "corp-ssid") -> dict:
    return {
        "profile-name": "corp-vap",
        "ssid_prof": {"profile-name": ssid_name},
        "aaa_prof": {"profile-name": "corp-aaa"},
        "vlan": {"vlan": vlan},
    }


def _ssids() -> list[dict]:
    return [
        {"profile-name": "corp-ssid", "essid": {"essid": "CORP-WIFI"}, "opmode": {"wpa2-aes": True}},
    ]


def _rt(mode: str, **extra) -> dict:
    rt = {"central_scope_id": "S", "target_mode": mode, "ssid_profiles": _ssids()}
    # Overlay modes require gw_cluster_list (issue #438); default one so unrelated
    # tests don't trip the guard. Tests targeting the guard override it explicitly.
    if mode in {"tunneled", "hybrid", "bridged_and_tunneled"} and "gw_cluster_list" not in extra:
        rt["gw_cluster_list"] = [{"cluster": "East", "cluster-scope-id": "S"}]
    rt.update(extra)
    return rt


def test_join_and_core_fields() -> None:
    out = preprocess_wlan_ssid(_vap(), _rt("tunneled"))
    assert out["_name"] == "corp-vap"
    assert out["_essid"] == "CORP-WIFI"
    assert out["_essid_obj"] == {"name": "CORP-WIFI"}
    assert out["_opmode"] == "WPA2_ENTERPRISE"


def test_forward_mode_fork() -> None:
    assert preprocess_wlan_ssid(_vap(), _rt("bridged"))["_forward_mode"] == "FORWARD_MODE_BRIDGE"
    assert preprocess_wlan_ssid(_vap(), _rt("tunneled"))["_forward_mode"] == "FORWARD_MODE_L2"
    assert preprocess_wlan_ssid(_vap(), _rt("hybrid"))["_forward_mode"] == "FORWARD_MODE_MIXED"


def test_overlay_flag_only_for_tunnel_hybrid() -> None:
    assert "_needs_overlay" not in preprocess_wlan_ssid(_vap(), _rt("bridged"))
    assert preprocess_wlan_ssid(_vap(), _rt("tunneled"))["_needs_overlay"] is True
    assert preprocess_wlan_ssid(_vap(), _rt("hybrid"))["_needs_overlay"] is True


def test_overlay_modes_require_gw_cluster_list() -> None:
    """Issue #438: tunneled / hybrid / dual must have a non-empty gw_cluster_list."""
    for mode in ("tunneled", "hybrid", "bridged_and_tunneled"):
        rt_missing = {"central_scope_id": "S", "target_mode": mode, "ssid_profiles": _ssids()}
        if mode == "bridged_and_tunneled":
            rt_missing |= {"bridge_scope_id": "B", "tunnel_scope_id": "T"}
        with pytest.raises(ValueError, match="gw_cluster_list"):
            preprocess_wlan_ssid(_vap(), rt_missing)
        # empty list is also rejected
        with pytest.raises(ValueError, match="gw_cluster_list"):
            preprocess_wlan_ssid(_vap(), {**rt_missing, "gw_cluster_list": []})


def test_bridged_needs_no_gw_cluster_list() -> None:
    """bridged is the only mode that may omit gw_cluster_list."""
    out = preprocess_wlan_ssid(_vap(), {"central_scope_id": "S", "target_mode": "bridged", "ssid_profiles": _ssids()})
    assert out["_forward_mode"] == "FORWARD_MODE_BRIDGE"


def test_named_vlan() -> None:
    out = preprocess_wlan_ssid(_vap(vlan="corp-vlan"), _rt("tunneled"))
    assert out["_vlan_selector"] == "NAMED_VLAN"
    assert out["_vlan_name"] == "corp-vlan"
    assert "_vlan_id_range" not in out


def test_numeric_vlan() -> None:
    out = preprocess_wlan_ssid(_vap(vlan="306"), _rt("tunneled"))
    assert out["_vlan_selector"] == "VLAN_RANGES"
    assert out["_vlan_id_range"] == ["306"]
    assert "_vlan_name" not in out


def test_opmode_mapping_table() -> None:
    cases = {
        "opensystem": "OPEN",
        "wpa2-psk-aes": "WPA2_PERSONAL",
        "wpa3-sae-aes": "WPA3_SAE",
        "wpa3-aes-gcm-256": "WPA3_ENTERPRISE_GCM_256",
        "enhanced-open": "ENHANCED_OPEN",
    }
    for aos, central in cases.items():
        ssids = [{"profile-name": "corp-ssid", "essid": {"essid": "E"}, "opmode": {aos: True}}]
        out = preprocess_wlan_ssid(
            _vap(),
            {
                "central_scope_id": "S",
                "target_mode": "tunneled",
                "ssid_profiles": ssids,
                "gw_cluster_list": [{"cluster": "East"}],
            },
        )
        assert out["_opmode"] == central, f"{aos} -> {central}"


def test_legacy_opmode_unmapped() -> None:
    """bSec / xSec have no Central equivalent → _opmode omitted."""
    ssids = [{"profile-name": "corp-ssid", "essid": {"essid": "E"}, "opmode": {"xSec": True}}]
    out = preprocess_wlan_ssid(
        _vap(),
        {
            "central_scope_id": "S",
            "target_mode": "tunneled",
            "ssid_profiles": ssids,
            "gw_cluster_list": [{"cluster": "East"}],
        },
    )
    assert "_opmode" not in out


def test_gw_cluster_list_passthrough() -> None:
    gw = [{"cluster": "East", "cluster-type": "GATEWAY"}]
    out = preprocess_wlan_ssid(_vap(), _rt("tunneled", gw_cluster_list=gw))
    assert out["_gw_cluster_list"] == gw


def _dual_rt(**extra) -> dict:
    return {
        "central_scope_id": "S",
        "target_mode": "bridged_and_tunneled",
        "ssid_profiles": _ssids(),
        "bridge_scope_id": "BRANCH",
        "tunnel_scope_id": "CAMPUS",
        "gw_cluster_list": [{"cluster": "East"}],  # overlay mode requires it (#438)
        **extra,
    }


def test_dual_mode_alias_and_profiles() -> None:
    out = preprocess_wlan_ssid(_vap(), _dual_rt())
    assert out["_emit_dual"] is True
    assert "_emit_single" not in out
    # ESSID alias shared by both profiles
    assert out["_essid_alias"] == "CORP-WIFI"
    assert out["_essid_obj_alias"] == {"use-alias": True, "alias": "CORP-WIFI"}
    # distinct per-mode profile names
    assert out["_name_bridge"] == "corp-vap-bridge"
    assert out["_name_tunnel"] == "corp-vap-tunnel"
    # no single-profile artifacts
    assert "_forward_mode" not in out and "_essid_obj" not in out and "_needs_overlay" not in out


def test_dual_mode_requires_both_scopes() -> None:
    with pytest.raises(ValueError, match="bridge_scope_id"):
        preprocess_wlan_ssid(_vap(), {**_dual_rt(), "bridge_scope_id": ""})
    with pytest.raises(ValueError, match="tunnel_scope_id|bridge_scope_id"):
        preprocess_wlan_ssid(
            _vap(),
            {
                "central_scope_id": "S",
                "target_mode": "bridged_and_tunneled",
                "ssid_profiles": _ssids(),
                "gw_cluster_list": [{"cluster": "East"}],  # present so we reach the scope check
            },
        )


def test_invalid_target_mode_raises() -> None:
    with pytest.raises(ValueError, match="target_mode"):
        preprocess_wlan_ssid(_vap(), {"central_scope_id": "S", "ssid_profiles": _ssids()})


def test_missing_ssid_prof_join_is_soft() -> None:
    """No matching ssid_prof → essid/opmode omitted (surfaces as a finding), no crash."""
    out = preprocess_wlan_ssid(_vap(ssid_name="absent"), _rt("tunneled"))
    assert "_essid" not in out and "_opmode" not in out
    assert out["_name"] == "corp-vap"
