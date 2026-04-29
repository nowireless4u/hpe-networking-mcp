"""Unit tests for AOS8 config loading."""

from __future__ import annotations

import pytest

from hpe_networking_mcp.config import AOS8Secrets, _load_aos8


@pytest.mark.unit
class TestLoadAOS8:
    """Test AOS8 secrets loading from Docker secrets directory."""

    def test_returns_secrets_when_all_required_present(self, patch_secrets_dir):
        result = _load_aos8()
        assert isinstance(result, AOS8Secrets)
        assert result.host == "conductor.test.example.com"
        assert result.port == 4343
        assert result.username == "admin"
        assert result.password == "aos8-test-password"
        assert result.verify_ssl is True

    def test_returns_none_when_host_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "aos8_host").unlink()
        assert _load_aos8() is None

    def test_returns_none_when_username_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "aos8_username").unlink()
        assert _load_aos8() is None

    def test_returns_none_when_password_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "aos8_password").unlink()
        assert _load_aos8() is None

    def test_port_defaults_to_4343_when_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "aos8_port").unlink()
        result = _load_aos8()
        assert result is not None
        assert result.port == 4343

    def test_port_parses_integer(self, patch_secrets_dir):
        (patch_secrets_dir / "aos8_port").write_text("8443")
        result = _load_aos8()
        assert result is not None
        assert result.port == 8443

    def test_invalid_port_falls_back_to_4343(self, patch_secrets_dir):
        (patch_secrets_dir / "aos8_port").write_text("not-a-port")
        result = _load_aos8()
        assert result is not None
        assert result.port == 4343

    def test_verify_ssl_defaults_true_when_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "aos8_verify_ssl").unlink()
        result = _load_aos8()
        assert result is not None
        assert result.verify_ssl is True

    @pytest.mark.parametrize("value", ["false", "FALSE", "0", "no", "No"])
    def test_verify_ssl_false_variants(self, patch_secrets_dir, value):
        (patch_secrets_dir / "aos8_verify_ssl").write_text(value)
        result = _load_aos8()
        assert result is not None
        assert result.verify_ssl is False

    @pytest.mark.parametrize("value", ["true", "1", "yes", ""])
    def test_verify_ssl_truthy_defaults(self, patch_secrets_dir, value):
        (patch_secrets_dir / "aos8_verify_ssl").write_text(value)
        result = _load_aos8()
        assert result is not None
        assert result.verify_ssl is True


def test_aos8_auto_disabled_when_secrets_missing(tmp_path, monkeypatch):
    """TEST-05: AOS8 platform auto-disables when no secrets present.

    Closes the name-presence gap for the Phase 7 hard-fail verification scan
    (`auto_disabled` / `disabled_when_secrets_missing` token).
    """
    from hpe_networking_mcp import config as cfg_mod

    monkeypatch.setattr(cfg_mod, "SECRETS_DIR", tmp_path)
    assert cfg_mod._load_aos8() is None
