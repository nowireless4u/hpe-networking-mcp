"""Canonical → Mist writer tests.

Cover the auth mapping (open/owe/psk/sae/enterprise/mpsk/transition), inline
RADIUS, NAC→mist_nac, cloud-MPSK→dynamic_psk, VLAN, the per-WLAN template +
applies (with unresolved-scope flagging), and the capture/inject markers that
thread the template id into the WLAN create.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.canonical.wlan import (
    Assignment,
    AuthSource,
    AuthSourceKind,
    CanonicalWlan,
    CoaServer,
    KeyMgmt,
    MpskSource,
    RadiusConfig,
    RadiusServer,
    Security,
    Vlan,
    VlanMode,
    WpaVersion,
)
from hpe_networking_mcp.translations.writers.mist import mist_write_wlan

pytestmark = pytest.mark.unit


def _wlan(sec: Security, **kw) -> CanonicalWlan:
    return CanonicalWlan(ssid="CORP", security=sec, **kw)


def _calls(sec: Security, **kw):
    return mist_write_wlan(_wlan(sec, **kw), org_id="ORG")


def test_template_then_wlan_with_capture_inject() -> None:
    calls = _calls(Security(key_mgmt=KeyMgmt.OPEN))
    assert calls[0]["path"] == "/api/v1/orgs/ORG/templates"
    assert calls[0]["capture"] == "template_id"
    assert calls[0]["idempotent"] is False
    assert calls[1]["path"] == "/api/v1/orgs/ORG/wlans"
    assert calls[1]["inject"] == {"template_id": "template_id"}
    assert calls[1]["depends_on"] == [0]


@pytest.mark.parametrize(
    "km,wpa,expected_type,expected_pairwise",
    [
        (KeyMgmt.OPEN, WpaVersion.NONE, "open", None),
        (KeyMgmt.PSK, WpaVersion.WPA2, "psk", ["wpa2-ccmp"]),
        (KeyMgmt.PSK, WpaVersion.WPA_WPA2, "psk", ["wpa1-ccmp", "wpa2-ccmp"]),
        (KeyMgmt.SAE, WpaVersion.WPA3, "psk", ["wpa3"]),
        (KeyMgmt.ENTERPRISE, WpaVersion.WPA2, "eap", ["wpa2-ccmp"]),
    ],
)
def test_auth_mapping(km, wpa, expected_type, expected_pairwise) -> None:
    sec = Security(key_mgmt=km, wpa_version=wpa)
    if km in (KeyMgmt.PSK, KeyMgmt.SAE):
        sec.psk = "x"
    auth = _calls(sec)[1]["body"]["auth"]
    assert auth["type"] == expected_type
    if expected_pairwise is not None:
        assert auth["pairwise"] == expected_pairwise


def test_owe_maps_to_open_with_flag() -> None:
    auth = _calls(Security(key_mgmt=KeyMgmt.OWE))[1]["body"]["auth"]
    assert auth["type"] == "open"
    assert auth["owe"] == "enabled"


def test_transition_adds_wpa3_and_wpa2() -> None:
    sec = Security(key_mgmt=KeyMgmt.SAE, wpa_version=WpaVersion.WPA3, wpa2_wpa3_transition=True, psk="x")
    auth = _calls(sec)[1]["body"]["auth"]
    assert "wpa3" in auth["pairwise"] and "wpa2-ccmp" in auth["pairwise"]


def test_inline_radius() -> None:
    sec = Security(
        key_mgmt=KeyMgmt.ENTERPRISE,
        wpa_version=WpaVersion.WPA2,
        auth_source=AuthSource(kind=AuthSourceKind.RADIUS_GROUP),
        radius=RadiusConfig(
            auth_servers=[RadiusServer(host="10.1.1.5", port=1812, secret="s")],
            acct_servers=[RadiusServer(host="10.1.1.5", port=1813, secret="s")],
            coa=[CoaServer(ip="10.1.1.5", port=3799, secret="s")],
        ),
    )
    body = _calls(sec)[1]["body"]
    assert body["auth_servers"] == [{"host": "10.1.1.5", "port": 1812, "secret": "s"}]
    assert body["acct_servers"][0]["port"] == 1813
    assert body["coa_servers"][0]["ip"] == "10.1.1.5"
    assert body["coa_enabled"] is True


def test_variable_host_passes_through() -> None:
    sec = Security(
        key_mgmt=KeyMgmt.ENTERPRISE,
        wpa_version=WpaVersion.WPA2,
        auth_source=AuthSource(kind=AuthSourceKind.RADIUS_GROUP),
        radius=RadiusConfig(auth_servers=[RadiusServer(host="{{RADIUS_PRIMARY}}", port=1812)]),
    )
    assert _calls(sec)[1]["body"]["auth_servers"][0]["host"] == "{{RADIUS_PRIMARY}}"


def test_nac_maps_to_mist_nac_no_radius() -> None:
    sec = Security(
        key_mgmt=KeyMgmt.ENTERPRISE, wpa_version=WpaVersion.WPA2, auth_source=AuthSource(kind=AuthSourceKind.NAC)
    )
    body = _calls(sec)[1]["body"]
    assert body["mist_nac"] == {"enabled": True}
    assert "auth_servers" not in body


def test_cloud_mpsk_maps_to_dynamic_psk() -> None:
    sec = Security(key_mgmt=KeyMgmt.MPSK, wpa_version=WpaVersion.WPA2, mpsk_source=MpskSource.CLOUD)
    body = _calls(sec)[1]["body"]
    assert body["dynamic_psk"] == {"enabled": True, "source": "cloud"}


def test_vlan_id_and_named() -> None:
    bid = _calls(Security(key_mgmt=KeyMgmt.OPEN), vlan=Vlan(mode=VlanMode.ID, id=80))[1]["body"]
    assert bid["vlan_enabled"] is True and bid["vlan_id"] == 80
    bn = _calls(Security(key_mgmt=KeyMgmt.OPEN), vlan=Vlan(mode=VlanMode.NAMED, name="CORP"))[1]["body"]
    assert bn["dynamic_vlan"]["vlans"] == {"CORP": ""}


@pytest.mark.parametrize("km", [KeyMgmt.WEP_STATIC, KeyMgmt.WEP_DYNAMIC])
def test_wep_is_flagged_unsupported(km) -> None:
    # WEP has no Mist mapping → the WLAN call is flagged unresolved so the plan
    # blocks instead of emitting an empty auth block.
    calls = _calls(Security(key_mgmt=km, wpa_version=WpaVersion.NONE))
    assert calls[1]["unresolved"] == [
        {"kind": "unsupported_auth", "name": "CORP (WEP is not supported by the Mist writer)"}
    ]


def test_template_applies_and_unresolved() -> None:
    canon = _wlan(Security(key_mgmt=KeyMgmt.OPEN), assignment=Assignment(org_wide=True, sites=["HOME", "GHOST"]))
    calls = mist_write_wlan(canon, org_id="ORG", site_name_to_id={"HOME": "site-1"})
    applies = calls[0]["body"]["applies"]
    assert applies["org_id"] == "ORG"
    assert applies["site_ids"] == ["site-1"]
    assert calls[0]["unresolved"] == [{"kind": "site", "name": "GHOST"}]
