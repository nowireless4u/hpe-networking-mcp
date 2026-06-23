"""Mist → canonical reader tests.

Cover the security-mode classification (open / psk / sae / mpsk-cloud /
enterprise-radius / enterprise-nac / mac-auth), RADIUS extraction (auth / acct /
coa, literal + ``{{var}}`` hosts), VLAN, rates, forward-mode, and the assignment
facet derived from a WLAN template's ``applies`` block.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.canonical.wlan import (
    AuthSourceKind,
    ForwardMode,
    KeyMgmt,
    MpskSource,
    VlanMode,
    WpaVersion,
)
from hpe_networking_mcp.translations.readers.mist import mist_read_wlan

pytestmark = pytest.mark.unit


def test_open_wlan() -> None:
    c = mist_read_wlan({"ssid": "GUEST", "auth": {"type": "open"}})
    assert c.ssid == "GUEST"
    assert c.profile_name == "GUEST"
    assert c.security.key_mgmt == KeyMgmt.OPEN
    assert c.security.auth_source is None


def test_psk_wlan_keeps_passphrase() -> None:
    c = mist_read_wlan({"ssid": "CORP", "auth": {"type": "psk", "psk": "s3cret-pass"}})
    assert c.security.key_mgmt == KeyMgmt.PSK
    assert c.security.wpa_version == WpaVersion.WPA2
    assert c.security.psk == "s3cret-pass"


def test_enterprise_wpa3_from_pairwise() -> None:
    c = mist_read_wlan({"ssid": "EAP3", "auth": {"type": "eap", "pairwise": ["wpa3"]}})
    assert c.security.key_mgmt == KeyMgmt.ENTERPRISE
    assert c.security.wpa_version == WpaVersion.WPA3


def test_sae_wpa3_only() -> None:
    c = mist_read_wlan({"ssid": "SAE", "auth": {"type": "psk", "pairwise": ["wpa3"], "psk": "x"}})
    assert c.security.key_mgmt == KeyMgmt.SAE


def test_mpsk_cloud_is_default_source() -> None:
    c = mist_read_wlan({"ssid": "MPSK", "auth": {"type": "psk"}, "dynamic_psk": {"enabled": True}})
    assert c.security.key_mgmt == KeyMgmt.MPSK
    assert c.security.mpsk_source == MpskSource.CLOUD


def test_mpsk_local_source() -> None:
    c = mist_read_wlan({"ssid": "MPSK-L", "auth": {"type": "psk"}, "dynamic_psk": {"enabled": True, "source": "local"}})
    assert c.security.key_mgmt == KeyMgmt.MPSK
    assert c.security.mpsk_source == MpskSource.LOCAL


def test_enterprise_with_mist_nac_is_nac_source() -> None:
    c = mist_read_wlan({"ssid": "NAC", "auth": {"type": "eap"}, "mist_nac": {"enabled": True}})
    assert c.security.key_mgmt == KeyMgmt.ENTERPRISE
    assert c.security.auth_source is not None
    assert c.security.auth_source.kind == AuthSourceKind.NAC
    assert c.security.radius is None


def test_enterprise_external_radius_is_radius_group() -> None:
    c = mist_read_wlan(
        {
            "ssid": "EAP",
            "auth": {"type": "eap"},
            "auth_servers": [{"host": "10.1.1.1", "port": 1812, "secret": "x"}],
            "acct_servers": [{"host": "10.1.1.1", "port": 1813, "secret": "x"}],
            "coa_servers": [{"ip": "10.1.1.1", "port": 3799, "secret": "x"}],
        }
    )
    assert c.security.auth_source.kind == AuthSourceKind.RADIUS_GROUP
    rad = c.security.radius
    assert rad is not None
    assert [s.host for s in rad.auth_servers] == ["10.1.1.1"]
    assert [s.host for s in rad.acct_servers] == ["10.1.1.1"]
    assert [s.ip for s in rad.coa] == ["10.1.1.1"]


def test_radius_variable_host_preserved() -> None:
    c = mist_read_wlan(
        {"ssid": "EAP", "auth": {"type": "eap"}, "auth_servers": [{"host": "{{RADIUS_PRIMARY}}", "port": 1812}]}
    )
    assert c.security.radius.auth_servers[0].host == "{{RADIUS_PRIMARY}}"


def test_mac_auth_flag() -> None:
    c = mist_read_wlan({"ssid": "MAC", "auth": {"type": "open", "enable_mac_auth": True}})
    assert c.security.mac_auth is True
    assert c.security.auth_source is not None  # mac-auth needs an auth source


def test_wpa2_wpa3_transition() -> None:
    c = mist_read_wlan({"ssid": "T", "auth": {"type": "psk", "pairwise": ["wpa3", "wpa2-ccmp"], "psk": "x"}})
    assert c.security.wpa2_wpa3_transition is True


def test_vlan_static_id() -> None:
    c = mist_read_wlan({"ssid": "V", "auth": {"type": "open"}, "vlan_enabled": True, "vlan_id": "100"})
    assert c.vlan.mode == VlanMode.ID
    assert c.vlan.id == 100


def test_vlan_named_dynamic() -> None:
    c = mist_read_wlan(
        {
            "ssid": "V",
            "auth": {"type": "open"},
            "dynamic_vlan": {"enabled": True, "default_vlan_ids": ["10"], "vlans": {"10": "CORP"}},
        }
    )
    assert c.vlan.mode == VlanMode.NAMED
    assert c.vlan.name == "CORP"
    assert c.vlan.id == 10


def test_forward_mode_tunneled_vs_bridged() -> None:
    bridged = mist_read_wlan({"ssid": "B", "auth": {"type": "open"}, "interface": "all"})
    tunneled = mist_read_wlan({"ssid": "T", "auth": {"type": "open"}, "interface": "tunnel"})
    assert bridged.forward == ForwardMode.BRIDGED
    assert tunneled.forward == ForwardMode.TUNNELED


def test_assignment_org_wide_from_template() -> None:
    tmpl = {"applies": {"org_id": "org-1"}}
    c = mist_read_wlan({"ssid": "X", "auth": {"type": "open"}}, template=tmpl)
    assert c.assignment.org_wide is True
    assert c.assignment.sites == []


def test_assignment_sites_mapped_by_name() -> None:
    tmpl = {"applies": {"site_ids": ["s1", "s2"]}}
    c = mist_read_wlan(
        {"ssid": "X", "auth": {"type": "open"}},
        template=tmpl,
        site_id_to_name={"s1": "HOME", "s2": "BRANCH-1"},
    )
    assert c.assignment.org_wide is False
    assert c.assignment.sites == ["HOME", "BRANCH-1"]


def test_assignment_sitegroups_and_deviceprofiles() -> None:
    tmpl = {
        "applies": {"sitegroup_ids": ["g1"]},
        "filter_by_deviceprofile": True,
        "deviceprofile_ids": ["d1"],
    }
    c = mist_read_wlan(
        {"ssid": "X", "auth": {"type": "open"}},
        template=tmpl,
        sitegroup_id_to_name={"g1": "EST Sites"},
        deviceprofile_id_to_name={"d1": "APs"},
    )
    assert c.assignment.site_collections == ["EST Sites"]
    assert c.assignment.device_groups == ["APs"]


def test_no_template_means_no_assignment() -> None:
    c = mist_read_wlan({"ssid": "X", "auth": {"type": "open"}})
    assert c.assignment.org_wide is False
    assert c.assignment.sites == []
