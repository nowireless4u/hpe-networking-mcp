"""AOS8 → canonical reader tests.

Cover the opmode→triplet map (the granular point), VLAN named/numeric, the
operator target_mode → forward/dual mapping, the virtual_ap↔ssid_prof join, and
the aaa_prof → server_group_prof (sg_name) → rad_server RADIUS chain incl. CoA.
Shapes mirror live AOS8 data (fields one-level-wrapped, _flags.default markers).
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.canonical.wlan import (
    AuthSourceKind,
    Cipher,
    ForwardMode,
    KeyMgmt,
    VlanMode,
    WpaVersion,
)
from hpe_networking_mcp.translations.readers.aos8 import aos8_read_wlan

pytestmark = pytest.mark.unit


def _vap(name="VAP", ssid="SP", aaa=None, vlan=None, **kw):
    v = {"profile-name": name, "ssid_prof": {"profile-name": ssid}}
    if aaa:
        v["aaa_prof"] = {"profile-name": aaa}
    if vlan is not None:
        v["vlan"] = {"vlan": vlan}
    v.update(kw)
    return v


def _sp(name="SP", essid="CORP", opmode="wpa2-aes"):
    return {"profile-name": name, "essid": {"essid": essid}, "opmode": {opmode: True}}


@pytest.mark.parametrize(
    "opmode,km,wpa,cipher",
    [
        ("opensystem", KeyMgmt.OPEN, WpaVersion.NONE, Cipher.NONE),
        ("enhanced-open", KeyMgmt.OWE, WpaVersion.NONE, Cipher.NONE),
        ("static-wep", KeyMgmt.WEP_STATIC, WpaVersion.NONE, Cipher.WEP),
        ("wpa-psk-aes", KeyMgmt.PSK, WpaVersion.WPA, Cipher.AES_CCM),
        ("wpa2-psk-tkip", KeyMgmt.PSK, WpaVersion.WPA2, Cipher.TKIP),
        ("wpa2-aes", KeyMgmt.ENTERPRISE, WpaVersion.WPA2, Cipher.AES_CCM),
        ("wpa3-sae-aes", KeyMgmt.SAE, WpaVersion.WPA3, Cipher.AES_CCM),
        ("wpa3-aes-gcm-256", KeyMgmt.ENTERPRISE, WpaVersion.WPA3, Cipher.GCM_256),
        ("wpa3-cnsa", KeyMgmt.ENTERPRISE, WpaVersion.WPA3, Cipher.CNSA),
        ("mpsk-aes", KeyMgmt.MPSK, WpaVersion.WPA2, Cipher.AES_CCM),
    ],
)
def test_opmode_to_triplet(opmode, km, wpa, cipher) -> None:
    c = aos8_read_wlan(_vap(), ssid_profiles=[_sp(opmode=opmode)])
    assert c.security.key_mgmt == km
    assert c.security.wpa_version == wpa
    assert c.security.cipher == cipher


def test_essid_and_profile_name() -> None:
    c = aos8_read_wlan(_vap(name="MYVAP", ssid="SP1"), ssid_profiles=[_sp(name="SP1", essid="CORP-WIFI")])
    assert c.ssid == "CORP-WIFI"
    assert c.profile_name == "MYVAP"


def test_vlan_numeric_vs_named() -> None:
    num = aos8_read_wlan(_vap(vlan="150"), ssid_profiles=[_sp()])
    assert num.vlan.mode == VlanMode.ID
    assert num.vlan.id == 150
    named = aos8_read_wlan(_vap(vlan="guest"), ssid_profiles=[_sp()])
    assert named.vlan.mode == VlanMode.NAMED
    assert named.vlan.name == "guest"


@pytest.mark.parametrize(
    "mode,forward,dual",
    [
        ("bridged", ForwardMode.BRIDGED, False),
        ("tunneled", ForwardMode.TUNNELED, False),
        ("hybrid", ForwardMode.HYBRID, False),
        ("bridged_and_tunneled", ForwardMode.TUNNELED, True),
    ],
)
def test_target_mode(mode, forward, dual) -> None:
    c = aos8_read_wlan(_vap(), ssid_profiles=[_sp()], target_mode=mode)
    assert c.forward == forward
    assert c.dual_mode == dual


def test_flags_default_opmode_ignored_falls_back_open() -> None:
    sp = {"profile-name": "SP", "essid": {"essid": "X"}, "opmode": {"_flags": {"default": True}}}
    c = aos8_read_wlan(_vap(), ssid_profiles=[sp])
    assert c.security.key_mgmt == KeyMgmt.OPEN


def test_radius_chain_auth_acct_coa() -> None:
    vap = _vap(ssid="SP", aaa="AAA1", vlan="150")
    sp = _sp(opmode="wpa2-aes")
    aaa = {
        "profile-name": "AAA1",
        "dot1x_server_group": {"srv-group": "ClearPass"},
        "rad_acct_sg": {"server_group_name": "ClearPass"},
        "rfc3576_client": [{"rfc3576_server": "10.1.1.9"}],
    }
    sg = {"sg_name": "ClearPass", "auth_server": [{"name": "rad1"}]}
    rad = {
        "rad_server_name": "rad1",
        "rad_host": {"host": "10.1.1.5"},
        "rad_key": {"key": "s"},
        "rad_authport": {"authport": 1812},
    }
    c = aos8_read_wlan(vap, ssid_profiles=[sp], aaa_profiles=[aaa], server_groups=[sg], auth_servers=[rad])
    assert c.security.key_mgmt == KeyMgmt.ENTERPRISE
    assert c.security.auth_source.kind == AuthSourceKind.RADIUS_GROUP
    r = c.security.radius
    assert [s.host for s in r.auth_servers] == ["10.1.1.5"]
    assert [s.host for s in r.acct_servers] == ["10.1.1.5"]
    assert [x.ip for x in r.coa] == ["10.1.1.9"]


def test_mac_auth_from_mba_server_group() -> None:
    aaa = {"profile-name": "AAA1", "mba_server_group": {"srv-group": "ClearPass"}}
    sg = {"sg_name": "ClearPass", "auth_server": [{"name": "rad1"}]}
    rad = {"rad_server_name": "rad1", "rad_host": {"host": "10.1.1.5"}, "rad_key": {"key": "s"}}
    c = aos8_read_wlan(
        _vap(ssid="SP", aaa="AAA1"),
        ssid_profiles=[_sp(opmode="opensystem")],
        aaa_profiles=[aaa],
        server_groups=[sg],
        auth_servers=[rad],
    )
    assert c.security.mac_auth is True
    assert c.security.radius is not None


def test_vlan_inherited_default_filtered() -> None:
    # an inherited-default vlan wrapper should be ignored (no VLAN set)
    vap = {
        "profile-name": "V",
        "ssid_prof": {"profile-name": "SP"},
        "vlan": {"vlan": "150", "_flags": {"default": True}},
    }
    c = aos8_read_wlan(vap, ssid_profiles=[_sp()])
    assert c.vlan.mode == VlanMode.NONE
