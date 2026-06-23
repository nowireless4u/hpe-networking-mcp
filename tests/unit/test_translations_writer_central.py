"""Canonical → Central WLAN writer tests.

Cover opmode mapping, essid shape, enterprise/MAC server-group references,
MPSK-cloud, and the four assignment facets (org_wide → GLOBAL, sites,
site_collections, device_groups) including unresolved-scope flagging.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.canonical.wlan import (
    Assignment,
    CanonicalWlan,
    Cipher,
    KeyMgmt,
    MpskSource,
    RadiusConfig,
    RadiusServer,
    Security,
    Vlan,
    VlanMode,
    WpaVersion,
)
from hpe_networking_mcp.translations.writers.central import central_write_wlan, server_group_name

pytestmark = pytest.mark.unit


def _wlan(**kw) -> CanonicalWlan:
    base = {"ssid": "CORP", "security": Security(key_mgmt=KeyMgmt.OPEN)}
    base.update(kw)
    return CanonicalWlan(**base)


def test_open_wlan_create_only_when_unassigned() -> None:
    calls = central_write_wlan(_wlan())
    assert len(calls) == 1
    create = calls[0]
    assert create["method"] == "POST"
    assert create["path"].endswith("/wlan-ssids/CORP")
    assert create["query"] == {}  # no-query library create
    assert create["body"]["opmode"] == "OPEN"
    assert create["body"]["essid"] == {"name": "CORP", "use-alias": False}


@pytest.mark.parametrize(
    "key_mgmt,wpa,cipher,expected",
    [
        (KeyMgmt.OPEN, WpaVersion.NONE, Cipher.NONE, "OPEN"),
        (KeyMgmt.OWE, WpaVersion.NONE, Cipher.NONE, "ENHANCED_OPEN"),
        (KeyMgmt.WEP_STATIC, WpaVersion.NONE, Cipher.WEP, "STATIC_WEP"),
        (KeyMgmt.WEP_DYNAMIC, WpaVersion.NONE, Cipher.WEP, "DYNAMIC_WEP"),
        (KeyMgmt.PSK, WpaVersion.WPA, Cipher.AES_CCM, "WPA_PERSONAL"),
        (KeyMgmt.PSK, WpaVersion.WPA2, Cipher.AES_CCM, "WPA2_PERSONAL"),
        (KeyMgmt.PSK, WpaVersion.WPA_WPA2, Cipher.AES_CCM, "BOTH_WPA_WPA2_PSK"),
        (KeyMgmt.SAE, WpaVersion.WPA3, Cipher.AES_CCM, "WPA3_SAE"),
        (KeyMgmt.ENTERPRISE, WpaVersion.WPA, Cipher.AES_CCM, "WPA_ENTERPRISE"),
        (KeyMgmt.ENTERPRISE, WpaVersion.WPA2, Cipher.AES_CCM, "WPA2_ENTERPRISE"),
        (KeyMgmt.ENTERPRISE, WpaVersion.WPA_WPA2, Cipher.AES_CCM, "BOTH_WPA_WPA2_DOT1X"),
        (KeyMgmt.ENTERPRISE, WpaVersion.WPA3, Cipher.AES_CCM, "WPA3_ENTERPRISE_CCM_128"),
        (KeyMgmt.ENTERPRISE, WpaVersion.WPA3, Cipher.GCM_256, "WPA3_ENTERPRISE_GCM_256"),
        (KeyMgmt.ENTERPRISE, WpaVersion.WPA3, Cipher.CNSA, "WPA3_ENTERPRISE_CNSA"),
        (KeyMgmt.MPSK, WpaVersion.WPA2, Cipher.AES_CCM, "WPA2_MPSK_AES"),
    ],
)
def test_opmode_mapping(key_mgmt, wpa, cipher, expected) -> None:
    sec = Security(key_mgmt=key_mgmt, wpa_version=wpa, cipher=cipher)
    if key_mgmt in (KeyMgmt.PSK, KeyMgmt.SAE):
        sec.psk = "x"
    calls = central_write_wlan(_wlan(security=sec))
    assert calls[0]["body"]["opmode"] == expected


def test_mpsk_local_opmode() -> None:
    sec = Security(key_mgmt=KeyMgmt.MPSK, wpa_version=WpaVersion.WPA2, mpsk_source=MpskSource.LOCAL)
    assert central_write_wlan(_wlan(security=sec))[0]["body"]["opmode"] == "WPA2_MPSK_LOCAL"


def _ent(wpa=WpaVersion.WPA2, **rad) -> Security:
    return Security(key_mgmt=KeyMgmt.ENTERPRISE, wpa_version=wpa, radius=RadiusConfig(**rad))


def test_enterprise_references_server_group() -> None:
    sec = _ent(auth_servers=[RadiusServer(host="10.1.1.1")])
    body = central_write_wlan(_wlan(ssid="EAP", security=sec))[0]["body"]
    assert body["auth-server-group"] == server_group_name("EAP") == "EAP_nac"


def test_acct_server_group_only_when_acct_present() -> None:
    sec = _ent(auth_servers=[RadiusServer(host="10.1.1.1")])
    body = central_write_wlan(_wlan(security=sec))[0]["body"]
    assert "acct-server-group" not in body
    sec.radius.acct_servers = [RadiusServer(host="10.1.1.1")]
    body2 = central_write_wlan(_wlan(security=sec))[0]["body"]
    assert body2["acct-server-group"] == "CORP_nac"


def test_mpsk_cloud_sets_cloud_auth_no_values() -> None:
    sec = Security(key_mgmt=KeyMgmt.MPSK, wpa_version=WpaVersion.WPA2, mpsk_source=MpskSource.CLOUD)
    body = central_write_wlan(_wlan(security=sec))[0]["body"]
    assert body["personal-security"] == {"mpsk-cloud-auth": True}


def test_numeric_vlan_uses_vlan_ranges() -> None:
    body = central_write_wlan(_wlan(vlan=Vlan(mode=VlanMode.ID, id=100)))[0]["body"]
    assert body["vlan-selector"] == "VLAN_RANGES"
    assert body["vlan-id-range"] == ["100"]


@pytest.mark.parametrize(
    "forward,expected",
    [(None, "FORWARD_MODE_BRIDGE")],
)
def test_forward_mode_default_bridge(forward, expected) -> None:
    body = central_write_wlan(_wlan())[0]["body"]
    assert body["forward-mode"] == "FORWARD_MODE_BRIDGE"


def test_named_vlan() -> None:
    body = central_write_wlan(_wlan(vlan=Vlan(mode=VlanMode.NAMED, name="CORP")))[0]["body"]
    assert body["vlan-selector"] == "NAMED_VLAN"
    assert body["vlan-name"] == "CORP"


def test_org_wide_emits_global_assignment() -> None:
    calls = central_write_wlan(_wlan(assignment=Assignment(org_wide=True)), global_scope_id="197674198")
    assert len(calls) == 2
    asg = calls[1]
    assert asg["path"].endswith("/config-assignments")
    entry = asg["body"]["config-assignment"][0]
    assert entry["scope-id"] == "197674198"
    assert entry["profile-type"] == "wlan-ssids"
    assert entry["profile-instance"] == "CORP"
    assert asg["depends_on"] == [0]


def test_site_assignment_resolved_and_unresolved() -> None:
    canon = _wlan(assignment=Assignment(sites=["HOME", "BRANCH-1"]))
    calls = central_write_wlan(canon, site_name_to_scope_id={"HOME": "18413656377"})
    home = calls[1]["body"]["config-assignment"][0]
    branch = calls[2]
    assert home["scope-id"] == "18413656377"
    assert calls[1]["unresolved"] is None
    assert branch["body"]["config-assignment"][0]["scope-id"] is None
    assert branch["unresolved"] == {"kind": "site", "name": "BRANCH-1"}


def test_site_collection_and_device_group_facets() -> None:
    canon = _wlan(assignment=Assignment(site_collections=["EST"], device_groups=["APs"]))
    calls = central_write_wlan(
        canon,
        site_collection_name_to_scope_id={"EST": "8179082016"},
        device_group_name_to_scope_id={"APs": "18377048403"},
    )
    ids = {c["body"]["config-assignment"][0]["scope-id"] for c in calls[1:]}
    assert ids == {"8179082016", "18377048403"}
