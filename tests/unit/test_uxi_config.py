"""Unit tests for UXI config — UXISecrets dataclass and _load_uxi() auto-disable.

Validates UXI-AUTH-01: the platform auto-disables when either uxi_client_id or
uxi_client_secret Docker secret is missing, and correctly loads credentials when
both secrets are present.
"""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestUXIConfig:
    """Tests for UXISecrets dataclass and ServerConfig UXI fields."""

    def test_uxi_secrets_dataclass(self):
        """UXISecrets constructs correctly and exposes client_id and client_secret."""
        from hpe_networking_mcp.config import UXISecrets

        s = UXISecrets(client_id="cid", client_secret="csecret")
        assert s.client_id == "cid"
        assert s.client_secret == "csecret"

    def test_server_config_uxi_field_default_none(self):
        """ServerConfig().uxi defaults to None (auto-disable when no secrets)."""
        from hpe_networking_mcp.config import ServerConfig

        cfg = ServerConfig()
        assert cfg.uxi is None

    def test_server_config_enable_uxi_write_tools_default_false(self):
        """ServerConfig().enable_uxi_write_tools defaults to False."""
        from hpe_networking_mcp.config import ServerConfig

        cfg = ServerConfig()
        assert cfg.enable_uxi_write_tools is False

    def test_uxi_in_enabled_platforms_when_secrets_set(self):
        """'uxi' appears in enabled_platforms when UXISecrets is provided."""
        from hpe_networking_mcp.config import ServerConfig, UXISecrets

        cfg = ServerConfig(uxi=UXISecrets(client_id="a", client_secret="b"))
        assert "uxi" in cfg.enabled_platforms

    def test_uxi_absent_from_enabled_platforms_when_none(self):
        """'uxi' is absent from enabled_platforms when uxi=None."""
        from hpe_networking_mcp.config import ServerConfig

        cfg = ServerConfig()
        assert "uxi" not in cfg.enabled_platforms

    def test_load_uxi_returns_none_when_client_id_missing(self, tmp_path, monkeypatch):
        """_load_uxi() returns None when uxi_client_id secret file is absent."""
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        (tmp_path / "uxi_client_secret").write_text("mysecret")
        from hpe_networking_mcp.config import _load_uxi

        result = _load_uxi()
        assert result is None

    def test_load_uxi_returns_none_when_client_secret_missing(self, tmp_path, monkeypatch):
        """_load_uxi() returns None when uxi_client_secret secret file is absent."""
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        (tmp_path / "uxi_client_id").write_text("myid")
        from hpe_networking_mcp.config import _load_uxi

        result = _load_uxi()
        assert result is None

    def test_load_uxi_returns_none_when_both_missing(self, tmp_path, monkeypatch):
        """_load_uxi() returns None when both secret files are absent."""
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        from hpe_networking_mcp.config import _load_uxi

        result = _load_uxi()
        assert result is None

    def test_load_uxi_returns_secrets_when_both_present(self, tmp_path, monkeypatch):
        """_load_uxi() returns UXISecrets with correct values when both secrets present."""
        (tmp_path / "uxi_client_id").write_text("myid")
        (tmp_path / "uxi_client_secret").write_text("mysecret")
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        from hpe_networking_mcp.config import _load_uxi

        secrets = _load_uxi()
        assert secrets is not None
        assert secrets.client_id == "myid"
        assert secrets.client_secret == "mysecret"
