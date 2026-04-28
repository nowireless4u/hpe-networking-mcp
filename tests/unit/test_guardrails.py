"""Unit tests for Mist best-practice guardrails."""

import pytest

from hpe_networking_mcp.platforms.mist.tools.guardrails import (
    validate_org_write,
    validate_site_write,
)


@pytest.mark.unit
class TestSiteWlanCreation:
    def test_site_wlan_create_warns(self):
        result = validate_site_write("wlans", "create", {})
        assert len(result.warnings) == 1
        assert "org-level WLAN templates" in result.warnings[0]
        assert len(result.suggestions) == 1

    def test_site_wlan_create_warning_lists_all_valid_scopes(self):
        """The warning text should list every valid template-assignment scope
        (org, site group, specific sites) — NOT just site groups. The original
        wording said 'assign the template to the site's site group' which an
        AI would interpret as 'site groups are the only valid target'. Closes
        the WLAN-scope correction in v2.3.0.4."""
        result = validate_site_write("wlans", "create", {})
        warning = result.warnings[0]
        assert "org" in warning.lower(), "must mention org-wide assignment"
        assert "site group" in warning.lower(), "must mention site-group assignment"
        assert "specific sites" in warning.lower() or "site_ids" in warning, (
            "must mention site-level assignment as a valid target — not just site groups"
        )
        # The "never at device level" rule belongs here too: it's the only
        # scope the user said was off-limits.
        assert "device level" in warning.lower() or "device_ids" in warning, (
            "must call out 'never at device level' explicitly"
        )

    def test_site_wlan_update_no_warn(self):
        result = validate_site_write("wlans", "update", {})
        assert len(result.warnings) == 0

    def test_site_wlan_delete_no_warn(self):
        result = validate_site_write("wlans", "delete", {})
        assert len(result.warnings) == 0

    def test_org_wlan_create_no_warn(self):
        result = validate_org_write("wlans", "create", {})
        assert len(result.warnings) == 0


@pytest.mark.unit
class TestHardcodedRadius:
    def test_hardcoded_ip_warns(self):
        payload = {"auth_servers": [{"host": "10.0.0.1", "port": 1812}]}
        result = validate_site_write("wlans", "update", payload)
        assert any("RADIUS" in w for w in result.warnings)

    def test_template_variable_no_warn(self):
        payload = {"auth_servers": [{"host": "{{auth_srv1}}", "port": 1812}]}
        result = validate_site_write("wlans", "update", payload)
        assert not any("RADIUS" in w for w in result.warnings)

    def test_acct_servers_also_checked(self):
        payload = {"acct_servers": [{"host": "192.168.1.100"}]}
        result = validate_org_write("wlans", "create", payload)
        assert any("RADIUS" in w for w in result.warnings)

    def test_non_wlan_type_not_checked(self):
        payload = {"auth_servers": [{"host": "10.0.0.1"}]}
        result = validate_site_write("webhooks", "create", payload)
        assert len(result.warnings) == 0

    def test_empty_auth_servers_no_warn(self):
        payload = {"auth_servers": []}
        result = validate_org_write("wlans", "create", payload)
        assert not any("RADIUS" in w for w in result.warnings)


@pytest.mark.unit
class TestFixedRf:
    def test_fixed_channels_warns(self):
        payload = {"band_24": {"channels": [1, 6, 11]}}
        result = validate_org_write("rftemplates", "create", payload)
        assert any("fixed channels" in w for w in result.warnings)

    def test_fixed_power_warns(self):
        payload = {"band_5": {"power": 17}}
        result = validate_org_write("rftemplates", "create", payload)
        assert any("fixed TX power" in w for w in result.warnings)

    def test_no_overrides_no_warn(self):
        payload = {"band_24": {"bandwidth": 20}}
        result = validate_org_write("rftemplates", "create", payload)
        assert len(result.warnings) == 0

    def test_empty_channels_no_warn(self):
        payload = {"band_24": {"channels": []}}
        result = validate_org_write("rftemplates", "create", payload)
        assert len(result.warnings) == 0

    def test_non_rftemplate_not_checked(self):
        payload = {"band_24": {"channels": [1, 6, 11]}}
        result = validate_org_write("wlans", "create", payload)
        assert len(result.warnings) == 0


@pytest.mark.unit
class TestStaticPsk:
    def test_static_psk_suggests(self):
        payload = {"passphrase": "my-shared-key", "ssid": "IoT"}
        result = validate_site_write("psks", "create", payload)
        assert any("Cloud PSK" in s for s in result.suggestions)

    def test_cloud_psk_no_suggest(self):
        payload = {"passphrase": "unique-key", "usage": "multi", "ssid": "IoT"}
        result = validate_site_write("psks", "create", payload)
        assert not any("Cloud PSK" in s for s in result.suggestions)

    def test_non_psk_not_checked(self):
        payload = {"passphrase": "something"}
        result = validate_site_write("wlans", "update", payload)
        assert not any("Cloud PSK" in s for s in result.suggestions)


@pytest.mark.unit
class TestSiteLevelOverride:
    def test_wxrules_create_suggests(self):
        result = validate_site_write("wxrules", "create", {})
        assert any("org level" in s for s in result.suggestions)

    def test_wxtags_create_suggests(self):
        result = validate_site_write("wxtags", "create", {})
        assert any("org level" in s for s in result.suggestions)

    def test_wxrules_update_no_suggest(self):
        result = validate_site_write("wxrules", "update", {})
        assert not any("org level" in s for s in result.suggestions)


@pytest.mark.unit
class TestEdgeCases:
    def test_empty_payload_no_crash(self):
        result = validate_site_write("wlans", "create", {})
        assert isinstance(result.warnings, list)

    def test_unrelated_object_no_warn(self):
        result = validate_site_write("webhooks", "create", {})
        assert len(result.warnings) == 0
        assert len(result.suggestions) == 0

    def test_org_empty_payload_no_crash(self):
        result = validate_org_write("wlans", "create", {})
        assert isinstance(result.warnings, list)
