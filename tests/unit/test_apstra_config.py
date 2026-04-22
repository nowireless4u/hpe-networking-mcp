"""Unit tests for Apstra config loading."""

from __future__ import annotations

import pytest

from hpe_networking_mcp.config import ApstraSecrets, _load_apstra


@pytest.mark.unit
class TestLoadApstra:
    def test_returns_secrets_when_all_required_present(self, patch_secrets_dir):
        result = _load_apstra()
        assert isinstance(result, ApstraSecrets)
        assert result.server == "apstra.test.example.com"
        assert result.port == 443
        assert result.username == "admin"
        assert result.password == "apstra-test-password"
        assert result.verify_ssl is True

    def test_returns_none_when_server_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "apstra_server").unlink()
        assert _load_apstra() is None

    def test_returns_none_when_username_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "apstra_username").unlink()
        assert _load_apstra() is None

    def test_returns_none_when_password_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "apstra_password").unlink()
        assert _load_apstra() is None

    def test_port_defaults_to_443_when_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "apstra_port").unlink()
        result = _load_apstra()
        assert result is not None
        assert result.port == 443

    def test_port_parses_integer(self, patch_secrets_dir):
        (patch_secrets_dir / "apstra_port").write_text("8443")
        result = _load_apstra()
        assert result is not None
        assert result.port == 8443

    def test_invalid_port_falls_back_to_443(self, patch_secrets_dir):
        (patch_secrets_dir / "apstra_port").write_text("not-a-port")
        result = _load_apstra()
        assert result is not None
        assert result.port == 443

    def test_verify_ssl_defaults_true_when_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "apstra_verify_ssl").unlink()
        result = _load_apstra()
        assert result is not None
        assert result.verify_ssl is True

    @pytest.mark.parametrize("value", ["false", "FALSE", "0", "no", "No"])
    def test_verify_ssl_false_variants(self, patch_secrets_dir, value):
        (patch_secrets_dir / "apstra_verify_ssl").write_text(value)
        result = _load_apstra()
        assert result is not None
        assert result.verify_ssl is False

    @pytest.mark.parametrize("value", ["true", "1", "yes", ""])
    def test_verify_ssl_truthy_defaults(self, patch_secrets_dir, value):
        (patch_secrets_dir / "apstra_verify_ssl").write_text(value)
        result = _load_apstra()
        assert result is not None
        # Empty string triggers the `not verify_ssl_str` branch → default True.
        assert result.verify_ssl is True
