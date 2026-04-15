"""Unit tests for cross-platform WLAN field mapper."""

import pytest

from hpe_networking_mcp.platforms.wlan_mapper import (
    central_to_mist,
    is_tunneled_central,
    is_tunneled_mist,
    mist_to_central,
    resolve_mist_template_var,
)

# ---------------------------------------------------------------------------
# Tunnel detection
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTunnelDetection:
    def test_central_bridge_not_tunneled(self):
        assert not is_tunneled_central({"forward-mode": "FORWARD_MODE_BRIDGE"})

    def test_central_default_not_tunneled(self):
        assert not is_tunneled_central({})

    def test_central_tunnel_is_tunneled(self):
        assert is_tunneled_central({"forward-mode": "FORWARD_MODE_TUNNEL"})

    def test_mist_all_not_tunneled(self):
        assert not is_tunneled_mist({"interface": "all"})

    def test_mist_default_not_tunneled(self):
        assert not is_tunneled_mist({})

    def test_mist_tunnel_is_tunneled(self):
        assert is_tunneled_mist({"interface": "mxtunnel"})


# ---------------------------------------------------------------------------
# Central → Mist: core fields
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCentralToMistCore:
    def test_basic_open_ssid(self):
        profile = {
            "ssid": "OPEN-WIFI",
            "essid": {"name": "OPEN-WIFI"},
            "opmode": "OPEN",
            "enable": True,
            "hide-ssid": False,
        }
        result = central_to_mist(profile)
        assert result["ssid"] == "OPEN-WIFI"
        assert result["enabled"] is True
        assert result["hide_ssid"] is False
        assert result["auth"]["type"] == "open"

    def test_resolved_ssid_overrides_essid(self):
        profile = {"essid": {"name": "PROFILE-NAME"}, "opmode": "OPEN"}
        result = central_to_mist(profile, resolved_ssid="ACTUAL-SSID")
        assert result["ssid"] == "ACTUAL-SSID"

    def test_disabled_ssid(self):
        profile = {"opmode": "OPEN", "enable": False}
        result = central_to_mist(profile)
        assert result["enabled"] is False


# ---------------------------------------------------------------------------
# Central → Mist: auth / opmode
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCentralToMistAuth:
    def test_wpa2_personal(self):
        profile = {
            "opmode": "WPA2_PERSONAL",
            "personal-security": {"wpa-passphrase": "test1234"},
        }
        result = central_to_mist(profile)
        assert result["auth"]["type"] == "psk"
        assert result["auth"]["pairwise"] == ["wpa2-ccmp"]
        assert result["auth"]["psk"] == "test1234"

    def test_wpa3_personal(self):
        profile = {"opmode": "WPA3_PERSONAL"}
        result = central_to_mist(profile, resolved_psk="wpa3pass!")
        assert result["auth"]["type"] == "psk"
        assert result["auth"]["pairwise"] == ["wpa3"]
        assert result["auth"]["psk"] == "wpa3pass!"

    def test_wpa2_enterprise(self):
        profile = {"opmode": "WPA2_ENTERPRISE"}
        result = central_to_mist(profile)
        assert result["auth"]["type"] == "eap"
        assert result["auth"]["pairwise"] == ["wpa2-ccmp"]

    def test_wpa3_enterprise_transition(self):
        profile = {"opmode": "WPA3_ENTERPRISE_CCM_128"}
        result = central_to_mist(profile)
        assert result["auth"]["type"] == "eap"
        assert "wpa3" in result["auth"]["pairwise"]
        assert "wpa2-ccmp" in result["auth"]["pairwise"]

    def test_wpa3_transition_mode(self):
        profile = {
            "opmode": "WPA2_PERSONAL",
            "wpa3-transition-mode-enable": True,
            "personal-security": {"wpa-passphrase": "pass1234"},
        }
        result = central_to_mist(profile)
        pairwise = result["auth"]["pairwise"]
        assert "wpa3" in pairwise
        assert "wpa2-ccmp" in pairwise

    def test_mpsk_cloud(self):
        profile = {
            "opmode": "WPA2_MPSK_AES",
            "personal-security": {"mpsk-cloud-auth": True},
        }
        result = central_to_mist(profile)
        assert result["auth"]["type"] == "psk"
        assert result["dynamic_psk"]["enabled"] is True
        assert result["dynamic_psk"]["source"] == "cloud"

    def test_mac_auth(self):
        profile = {"opmode": "WPA2_ENTERPRISE", "mac-authentication": True}
        result = central_to_mist(profile)
        assert result["auth"]["enable_mac_auth"] is True

    def test_resolved_psk_overrides_inline(self):
        profile = {
            "opmode": "WPA2_PERSONAL",
            "personal-security": {"wpa-passphrase": "inline-pass"},
        }
        result = central_to_mist(profile, resolved_psk="alias-resolved-pass")
        assert result["auth"]["psk"] == "alias-resolved-pass"


# ---------------------------------------------------------------------------
# Central → Mist: RADIUS
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCentralToMistRadius:
    def test_resolved_server_group(self):
        profile = {"opmode": "WPA2_ENTERPRISE"}
        servers = [
            {"host": "10.1.1.100", "port": 1812, "secret": "s3cret"},
            {"host": "10.1.1.101", "port": 1812, "secret": "s3cret"},
        ]
        result = central_to_mist(profile, resolved_servers=servers)
        assert len(result["auth_servers"]) == 2
        assert result["auth_servers"][0]["host"] == "10.1.1.100"
        assert result["auth_server_selection"] == "ordered"

    def test_inline_primary_backup_fallback(self):
        profile = {
            "opmode": "WPA2_ENTERPRISE",
            "primary-auth-server": "radius1.corp.local",
            "backup-auth-server": "radius2.corp.local",
        }
        result = central_to_mist(profile)
        assert len(result["auth_servers"]) == 2
        assert result["auth_servers"][0]["host"] == "radius1.corp.local"
        assert result["auth_servers"][1]["host"] == "radius2.corp.local"

    def test_accounting_servers(self):
        profile = {
            "opmode": "WPA2_ENTERPRISE",
            "primary-auth-server": "10.1.1.100",
            "radius-accounting": True,
            "primary-acct-server": "10.1.1.100",
            "radius-interim-accounting-interval": 600,
        }
        result = central_to_mist(profile)
        assert "acct_servers" in result
        assert result["acct_servers"][0]["host"] == "10.1.1.100"
        assert result["acct_interim_interval"] == 600

    def test_nas_id_and_ip(self):
        profile = {"opmode": "WPA2_ENTERPRISE", "primary-auth-server": "10.1.1.1"}
        result = central_to_mist(
            profile, resolved_nas_id="my-nas", resolved_nas_ip="10.0.0.1"
        )
        assert result["auth_servers_nas_id"] == "my-nas"
        assert result["auth_servers_nas_ip"] == "10.0.0.1"

    def test_coa_servers(self):
        profile = {"opmode": "WPA2_ENTERPRISE"}
        servers = [
            {
                "host": "10.1.1.100",
                "port": 1812,
                "secret": "s3cret",
                "dynamic-authorization-enable": True,
                "coa-port": 3799,
            },
        ]
        result = central_to_mist(profile, resolved_servers=servers)
        assert len(result["coa_servers"]) == 1
        assert result["coa_servers"][0]["ip"] == "10.1.1.100"
        assert result["coa_servers"][0]["port"] == 3799

    def test_radsec(self):
        profile = {"opmode": "WPA2_ENTERPRISE"}
        servers = [{"host": "10.1.1.100", "port": 1812, "enable-radsec": True}]
        result = central_to_mist(profile, resolved_servers=servers)
        assert result["radsec"]["enabled"] is True

    def test_no_radius_for_psk(self):
        profile = {
            "opmode": "WPA2_PERSONAL",
            "personal-security": {"wpa-passphrase": "test"},
            "primary-auth-server": "10.1.1.100",
        }
        result = central_to_mist(profile)
        assert "auth_servers" not in result


# ---------------------------------------------------------------------------
# Central → Mist: VLAN
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCentralToMistVlan:
    def test_resolved_vlan_id(self):
        profile = {"opmode": "OPEN", "vlan-name": "USER-VLAN"}
        result = central_to_mist(profile, resolved_vlan_id=100)
        assert result["vlan_enabled"] is True
        assert result["dynamic_vlan"]["enabled"] is True
        assert result["dynamic_vlan"]["default_vlan_ids"] == [100]
        assert result["dynamic_vlan"]["vlans"]["100"] == "USER-VLAN"
        assert result["dynamic_vlan"]["type"] == "airespace-interface-name"

    def test_unresolved_vlan_name_fallback(self):
        profile = {"opmode": "OPEN", "vlan-name": "USER-VLAN"}
        result = central_to_mist(profile)
        assert result["vlan_enabled"] is True
        assert result["vlan_id"] == "USER-VLAN"
        assert "dynamic_vlan" not in result

    def test_no_vlan(self):
        profile = {"opmode": "OPEN"}
        result = central_to_mist(profile)
        assert "vlan_enabled" not in result


# ---------------------------------------------------------------------------
# Central → Mist: RF band
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCentralToMistBands:
    def test_band_all(self):
        profile = {"opmode": "OPEN", "rf-band": "BAND_ALL"}
        result = central_to_mist(profile)
        assert result["bands"] == ["24", "5", "6"]

    def test_24ghz_5ghz(self):
        profile = {"opmode": "OPEN", "rf-band": "24GHZ_5GHZ"}
        result = central_to_mist(profile)
        assert result["bands"] == ["24", "5"]

    def test_5ghz_only(self):
        profile = {"opmode": "OPEN", "rf-band": "5GHZ"}
        result = central_to_mist(profile)
        assert result["bands"] == ["5"]

    def test_6ghz_only(self):
        profile = {"opmode": "OPEN", "rf-band": "6GHZ"}
        result = central_to_mist(profile)
        assert result["bands"] == ["6"]

    def test_default_bands(self):
        profile = {"opmode": "OPEN"}
        result = central_to_mist(profile)
        assert result["bands"] == ["24", "5"]


# ---------------------------------------------------------------------------
# Central → Mist: data rates
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCentralToMistDataRates:
    def test_compatible_rates(self):
        profile = {
            "opmode": "OPEN",
            "g-legacy-rates": {"basic-rates": ["1", "2"]},
        }
        result = central_to_mist(profile)
        assert result["rateset"]["24"]["template"] == "compatible"
        assert result["rateset"]["5"]["template"] == "compatible"

    def test_no_legacy_rates(self):
        profile = {
            "opmode": "OPEN",
            "g-legacy-rates": {"basic-rates": ["12"]},
        }
        result = central_to_mist(profile)
        assert result["rateset"]["24"]["template"] == "no-legacy"

    def test_high_density_rates(self):
        profile = {
            "opmode": "OPEN",
            "a-legacy-rates": {"basic-rates": ["24"]},
        }
        result = central_to_mist(profile)
        assert result["rateset"]["24"]["template"] == "high-density"

    def test_no_rates_info(self):
        profile = {"opmode": "OPEN"}
        result = central_to_mist(profile)
        assert "rateset" not in result


# ---------------------------------------------------------------------------
# Central → Mist: performance, roaming, isolation, WMM
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCentralToMistPerformance:
    def test_performance_defaults(self):
        profile = {"opmode": "OPEN"}
        result = central_to_mist(profile)
        assert result["dtim"] == 2
        assert result["max_num_clients"] == 0
        assert result["max_idletime"] == 1800

    def test_performance_custom(self):
        profile = {
            "opmode": "OPEN",
            "dtim-period": 3,
            "max-clients-threshold": 50,
            "inactivity-timeout": 900,
        }
        result = central_to_mist(profile)
        assert result["dtim"] == 3
        assert result["max_num_clients"] == 50
        assert result["max_idletime"] == 900

    def test_dot11r_maps_to_11r(self):
        profile = {"opmode": "OPEN", "dot11r": True}
        result = central_to_mist(profile)
        assert result["roam_mode"] == "11r"

    def test_no_dot11r(self):
        profile = {"opmode": "OPEN"}
        result = central_to_mist(profile)
        assert "roam_mode" not in result

    def test_eht_disabled(self):
        profile = {
            "opmode": "OPEN",
            "extremely-high-throughput": {"enable": False},
        }
        result = central_to_mist(profile)
        assert result["disable_11be"] is True

    def test_client_isolation(self):
        profile = {"opmode": "OPEN", "client-isolation": True}
        result = central_to_mist(profile)
        assert result["isolation"] is True

    def test_arp_filter(self):
        profile = {
            "opmode": "OPEN",
            "broadcast-filter-ipv4": "BCAST_FILTER_ARP",
        }
        result = central_to_mist(profile)
        assert result["arp_filter"] is True

    def test_wmm_disabled(self):
        profile = {"opmode": "OPEN", "wmm-cfg": {"enable": False, "uapsd": False}}
        result = central_to_mist(profile)
        assert result["disable_wmm"] is True
        assert result["disable_uapsd"] is True

    def test_broadcast_limiting(self):
        profile = {"opmode": "OPEN", "deny-inter-user-bridging": True}
        result = central_to_mist(profile)
        assert result["limit_bcast"] is True


# ---------------------------------------------------------------------------
# Mist → Central: core fields
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMistToCentralCore:
    def test_basic_open_ssid(self):
        wlan = {"ssid": "OPEN-WIFI", "enabled": True, "hide_ssid": False}
        result = mist_to_central(wlan)
        assert result["ssid"] == "OPEN-WIFI"
        assert result["essid"]["name"] == "OPEN-WIFI"
        assert result["enable"] is True
        assert result["hide-ssid"] is False
        assert result["opmode"] == "OPEN"
        assert result["forward-mode"] == "FORWARD_MODE_BRIDGE"


# ---------------------------------------------------------------------------
# Mist → Central: auth
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMistToCentralAuth:
    def test_psk_wpa2(self):
        wlan = {
            "ssid": "PSK-NET",
            "auth": {"type": "psk", "pairwise": ["wpa2-ccmp"], "psk": "pass1234"},
        }
        result = mist_to_central(wlan)
        assert result["opmode"] == "WPA2_PERSONAL"
        assert result["personal-security"]["wpa-passphrase"] == "pass1234"

    def test_psk_wpa3(self):
        wlan = {
            "ssid": "WPA3-NET",
            "auth": {"type": "psk", "pairwise": ["wpa3"], "psk": "wpa3pass"},
        }
        result = mist_to_central(wlan)
        assert result["opmode"] == "WPA3_PERSONAL"

    def test_eap_wpa2(self):
        wlan = {"ssid": "DOT1X", "auth": {"type": "eap", "pairwise": ["wpa2-ccmp"]}}
        result = mist_to_central(wlan)
        assert result["opmode"] == "WPA2_ENTERPRISE"

    def test_eap_wpa3_transition(self):
        wlan = {
            "ssid": "DOT1X-WPA3",
            "auth": {"type": "eap", "pairwise": ["wpa3", "wpa2-ccmp"]},
        }
        result = mist_to_central(wlan)
        assert result["opmode"] == "WPA3_ENTERPRISE_CCM_128"
        assert result["wpa3-transition-mode-enable"] is True

    def test_mpsk_cloud(self):
        wlan = {
            "ssid": "MPSK-NET",
            "auth": {"type": "psk"},
            "dynamic_psk": {"enabled": True, "source": "cloud"},
        }
        result = mist_to_central(wlan)
        assert result["opmode"] == "WPA2_MPSK_AES"

    def test_mac_auth(self):
        wlan = {
            "ssid": "MAC-NET",
            "auth": {"type": "eap", "enable_mac_auth": True},
        }
        result = mist_to_central(wlan)
        assert result["mac-authentication"] is True


# ---------------------------------------------------------------------------
# Mist → Central: RADIUS
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMistToCentralRadius:
    def test_auth_servers(self):
        wlan = {
            "ssid": "DOT1X",
            "auth": {"type": "eap"},
            "auth_servers": [
                {"host": "10.1.1.100", "port": 1812, "secret": "s"},
                {"host": "10.1.1.101", "port": 1812, "secret": "s"},
            ],
        }
        result = mist_to_central(wlan)
        assert result["primary-auth-server"] == "10.1.1.100"
        assert result["backup-auth-server"] == "10.1.1.101"

    def test_resolved_template_vars(self):
        wlan = {
            "ssid": "DOT1X",
            "auth": {"type": "eap"},
            "auth_servers": [
                {"host": "{{auth_srv1}}", "port": 1812},
                {"host": "{{auth_srv2}}", "port": 1812},
            ],
        }
        result = mist_to_central(
            wlan, resolved_auth_hosts=["10.1.1.100", "10.1.1.101"]
        )
        assert result["primary-auth-server"] == "10.1.1.100"
        assert result["backup-auth-server"] == "10.1.1.101"

    def test_acct_servers(self):
        wlan = {
            "ssid": "DOT1X",
            "auth": {"type": "eap"},
            "acct_servers": [{"host": "10.1.1.100", "port": 1813}],
            "acct_interim_interval": 600,
        }
        result = mist_to_central(wlan)
        assert result["radius-accounting"] is True
        assert result["primary-acct-server"] == "10.1.1.100"
        assert result["radius-interim-accounting-interval"] == 600

    def test_nas_id_and_ip(self):
        wlan = {
            "ssid": "DOT1X",
            "auth_servers_nas_id": "my-nas",
            "auth_servers_nas_ip": "10.0.0.1",
        }
        result = mist_to_central(wlan)
        assert result["nas-identifier"] == "my-nas"
        assert result["nas-ip-address"] == "10.0.0.1"

    def test_coa(self):
        wlan = {
            "ssid": "DOT1X",
            "coa_servers": [{"ip": "10.1.1.100", "port": 3799}],
        }
        result = mist_to_central(wlan)
        assert result["dynamic-authorization-enable"] is True

    def test_radsec(self):
        wlan = {"ssid": "DOT1X", "radsec": {"enabled": True}}
        result = mist_to_central(wlan)
        assert result["enable-radsec"] is True


# ---------------------------------------------------------------------------
# Mist → Central: VLAN
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMistToCentralVlan:
    def test_dynamic_vlan_airespace(self):
        wlan = {
            "ssid": "VLAN-NET",
            "dynamic_vlan": {
                "enabled": True,
                "type": "airespace-interface-name",
                "default_vlan_ids": [100],
                "vlans": {"100": "USER-VLAN"},
            },
        }
        result = mist_to_central(wlan)
        assert result["vlan-selector"] == "NAMED_VLAN"
        assert result["vlan-name"] == "USER-VLAN"

    def test_dynamic_vlan_no_name(self):
        wlan = {
            "ssid": "VLAN-NET",
            "dynamic_vlan": {
                "enabled": True,
                "vlans": {"200": ""},
            },
        }
        result = mist_to_central(wlan)
        assert result["vlan-name"] == "200"

    def test_simple_vlan_id(self):
        wlan = {"ssid": "SIMPLE", "vlan_enabled": True, "vlan_id": 100}
        result = mist_to_central(wlan)
        assert result["vlan-selector"] == "NAMED_VLAN"
        assert result["vlan-name"] == "100"

    def test_no_vlan(self):
        wlan = {"ssid": "NO-VLAN"}
        result = mist_to_central(wlan)
        assert "vlan-selector" not in result


# ---------------------------------------------------------------------------
# Mist → Central: RF band
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMistToCentralBands:
    def test_all_bands(self):
        wlan = {"ssid": "ALL", "bands": ["24", "5", "6"]}
        result = mist_to_central(wlan)
        assert result["rf-band"] == "BAND_ALL"

    def test_dual_band(self):
        wlan = {"ssid": "DUAL", "bands": ["24", "5"]}
        result = mist_to_central(wlan)
        assert result["rf-band"] == "24GHZ_5GHZ"

    def test_5ghz_only(self):
        wlan = {"ssid": "5G", "bands": ["5"]}
        result = mist_to_central(wlan)
        assert result["rf-band"] == "5GHZ"

    def test_default_bands(self):
        wlan = {"ssid": "DEFAULT"}
        result = mist_to_central(wlan)
        assert result["rf-band"] == "24GHZ_5GHZ"


# ---------------------------------------------------------------------------
# Mist → Central: data rates
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMistToCentralDataRates:
    def test_compatible_template(self):
        wlan = {"ssid": "COMPAT", "rateset": {"24": {"template": "compatible"}}}
        result = mist_to_central(wlan)
        assert result["g-legacy-rates"]["basic-rates"] == ["1", "2"]
        assert result["a-legacy-rates"]["basic-rates"] == ["6"]

    def test_no_legacy_template(self):
        wlan = {"ssid": "NOLEG", "rateset": {"5": {"template": "no-legacy"}}}
        result = mist_to_central(wlan)
        assert result["g-legacy-rates"]["basic-rates"] == ["12"]

    def test_high_density_template(self):
        wlan = {"ssid": "HD", "rateset": {"24": {"template": "high-density"}}}
        result = mist_to_central(wlan)
        assert result["g-legacy-rates"]["basic-rates"] == ["24"]

    def test_no_rateset(self):
        wlan = {"ssid": "NONE"}
        result = mist_to_central(wlan)
        assert "g-legacy-rates" not in result


# ---------------------------------------------------------------------------
# Mist → Central: performance, roaming, isolation, WMM
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMistToCentralPerformance:
    def test_performance_defaults(self):
        wlan = {"ssid": "DEFAULT"}
        result = mist_to_central(wlan)
        assert result["dtim-period"] == 2
        assert result["max-clients-threshold"] == 64
        assert result["inactivity-timeout"] == 1800

    def test_dot11r(self):
        wlan = {"ssid": "ROAM", "roam_mode": "11r"}
        result = mist_to_central(wlan)
        assert result["dot11r"] is True

    def test_no_roaming(self):
        wlan = {"ssid": "NO-ROAM", "roam_mode": "NONE"}
        result = mist_to_central(wlan)
        assert "dot11r" not in result

    def test_eht_disabled(self):
        wlan = {"ssid": "NO-EHT", "disable_11be": True}
        result = mist_to_central(wlan)
        assert result["extremely-high-throughput"]["enable"] is False

    def test_isolation_and_broadcast(self):
        wlan = {
            "ssid": "ISO",
            "isolation": True,
            "limit_bcast": True,
            "arp_filter": True,
        }
        result = mist_to_central(wlan)
        assert result["client-isolation"] is True
        assert result["deny-inter-user-bridging"] is True
        assert result["broadcast-filter-ipv4"] == "BCAST_FILTER_ARP"

    def test_wmm(self):
        wlan = {"ssid": "WMM", "disable_wmm": True, "disable_uapsd": True}
        result = mist_to_central(wlan)
        assert result["wmm-cfg"]["enable"] is False
        assert result["wmm-cfg"]["uapsd"] is False


# ---------------------------------------------------------------------------
# Template variable resolution
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTemplateVarResolution:
    def test_resolves_variable(self):
        result = resolve_mist_template_var(
            "{{auth_srv1}}", {"auth_srv1": "10.1.1.100"}
        )
        assert result == "10.1.1.100"

    def test_resolves_fqdn(self):
        result = resolve_mist_template_var(
            "{{radius_primary}}", {"radius_primary": "radius.corp.local"}
        )
        assert result == "radius.corp.local"

    def test_passthrough_literal_ip(self):
        result = resolve_mist_template_var("10.1.1.100", {"auth_srv1": "other"})
        assert result == "10.1.1.100"

    def test_missing_variable_returns_original(self):
        result = resolve_mist_template_var("{{missing_var}}", {})
        assert result == "{{missing_var}}"

    def test_passthrough_fqdn(self):
        result = resolve_mist_template_var("radius.corp.local", {})
        assert result == "radius.corp.local"
