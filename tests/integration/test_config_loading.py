"""Integration tests for configuration loading from Docker secrets.

These tests exercise the full load_config() flow by writing temporary
secret files and pointing SECRETS_DIR at them. No real Docker secrets
or network calls are involved.
"""

import pytest

from hpe_networking_mcp.config import (
    ServerConfig,
    MistSecrets,
    CentralSecrets,
    GreenLakeSecrets,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_secret(secrets_dir, name: str, value: str) -> None:
    """Write a secret file into the temporary secrets directory."""
    (secrets_dir / name).write_text(value)


def _write_mist_secrets(secrets_dir) -> None:
    _write_secret(secrets_dir, "mist_api_token", "test-mist-token")
    _write_secret(secrets_dir, "mist_host", "api.mist.com")


def _write_central_secrets(secrets_dir) -> None:
    _write_secret(secrets_dir, "central_base_url", "https://us5.api.central.arubanetworks.com")
    _write_secret(secrets_dir, "central_client_id", "test-central-id")
    _write_secret(secrets_dir, "central_client_secret", "test-central-secret")


def _write_greenlake_secrets(secrets_dir) -> None:
    _write_secret(secrets_dir, "greenlake_api_base_url", "https://global.api.greenlake.hpe.com")
    _write_secret(secrets_dir, "greenlake_client_id", "test-gl-id")
    _write_secret(secrets_dir, "greenlake_client_secret", "test-gl-secret")
    _write_secret(secrets_dir, "greenlake_workspace_id", "test-workspace-id")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestLoadConfig:
    """Tests for hpe_networking_mcp.config.load_config()."""

    def test_all_platforms_when_all_secrets_exist(self, tmp_path, monkeypatch):
        """load_config() returns config with all 3 platforms when all secret files are present."""
        import hpe_networking_mcp.config as config_module

        _write_mist_secrets(tmp_path)
        _write_central_secrets(tmp_path)
        _write_greenlake_secrets(tmp_path)

        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))

        config = config_module.load_config()

        assert isinstance(config, ServerConfig)
        assert config.mist is not None
        assert isinstance(config.mist, MistSecrets)
        assert config.mist.api_token == "test-mist-token"
        assert config.mist.host == "api.mist.com"

        assert config.central is not None
        assert isinstance(config.central, CentralSecrets)
        assert config.central.base_url == "https://us5.api.central.arubanetworks.com"
        assert config.central.client_id == "test-central-id"
        assert config.central.client_secret == "test-central-secret"

        assert config.greenlake is not None
        assert isinstance(config.greenlake, GreenLakeSecrets)
        assert config.greenlake.api_base_url == "https://global.api.greenlake.hpe.com"
        assert config.greenlake.client_id == "test-gl-id"
        assert config.greenlake.client_secret == "test-gl-secret"
        assert config.greenlake.workspace_id == "test-workspace-id"

        assert sorted(config.enabled_platforms) == ["central", "greenlake", "mist"]

    def test_only_mist_when_only_mist_secrets_exist(self, tmp_path, monkeypatch):
        """load_config() enables only Mist when only Mist secret files are present."""
        import hpe_networking_mcp.config as config_module

        _write_mist_secrets(tmp_path)

        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))

        config = config_module.load_config()

        assert config.mist is not None
        assert config.central is None
        assert config.greenlake is None
        assert config.enabled_platforms == ["mist"]

    def test_only_central_when_only_central_secrets_exist(self, tmp_path, monkeypatch):
        """load_config() enables only Central when only Central secret files are present."""
        import hpe_networking_mcp.config as config_module

        _write_central_secrets(tmp_path)

        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))

        config = config_module.load_config()

        assert config.mist is None
        assert config.central is not None
        assert config.greenlake is None
        assert config.enabled_platforms == ["central"]

    def test_only_greenlake_when_only_greenlake_secrets_exist(self, tmp_path, monkeypatch):
        """load_config() enables only GreenLake when only GreenLake secret files are present."""
        import hpe_networking_mcp.config as config_module

        _write_greenlake_secrets(tmp_path)

        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))

        config = config_module.load_config()

        assert config.mist is None
        assert config.central is None
        assert config.greenlake is not None
        assert config.enabled_platforms == ["greenlake"]

    def test_raises_system_exit_when_no_secrets_exist(self, tmp_path, monkeypatch):
        """load_config() raises SystemExit(1) when no secret files are found."""
        import hpe_networking_mcp.config as config_module

        # tmp_path exists but is empty -- no secret files
        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))

        with pytest.raises(SystemExit) as exc_info:
            config_module.load_config()

        assert exc_info.value.code == 1

    def test_env_var_override_mcp_port(self, tmp_path, monkeypatch):
        """MCP_PORT environment variable overrides the default port."""
        import hpe_networking_mcp.config as config_module

        _write_mist_secrets(tmp_path)
        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))
        monkeypatch.setenv("MCP_PORT", "9090")

        config = config_module.load_config()

        assert config.port == 9090

    def test_env_var_override_log_level(self, tmp_path, monkeypatch):
        """LOG_LEVEL environment variable overrides the default log level."""
        import hpe_networking_mcp.config as config_module

        _write_mist_secrets(tmp_path)
        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))
        monkeypatch.setenv("LOG_LEVEL", "debug")

        config = config_module.load_config()

        assert config.log_level == "DEBUG"

    def test_env_var_override_enable_write_tools(self, tmp_path, monkeypatch):
        """ENABLE_WRITE_TOOLS=true environment variable enables write tools."""
        import hpe_networking_mcp.config as config_module

        _write_mist_secrets(tmp_path)
        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))
        monkeypatch.setenv("ENABLE_WRITE_TOOLS", "true")

        config = config_module.load_config()

        assert config.enable_write_tools is True

    def test_enable_write_tools_defaults_to_false(self, tmp_path, monkeypatch):
        """ENABLE_WRITE_TOOLS defaults to False when not set."""
        import hpe_networking_mcp.config as config_module

        _write_mist_secrets(tmp_path)
        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))
        monkeypatch.delenv("ENABLE_WRITE_TOOLS", raising=False)

        config = config_module.load_config()

        assert config.enable_write_tools is False

    def test_partial_platform_secrets_disables_that_platform(self, tmp_path, monkeypatch):
        """A platform with only some of its required secrets is disabled (returns None)."""
        import hpe_networking_mcp.config as config_module

        # Write only Mist secrets (complete) plus partial Central (missing client_secret)
        _write_mist_secrets(tmp_path)
        _write_secret(tmp_path, "central_base_url", "https://us5.api.central.arubanetworks.com")
        _write_secret(tmp_path, "central_client_id", "test-central-id")
        # central_client_secret is intentionally missing

        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))

        config = config_module.load_config()

        assert config.mist is not None
        assert config.central is None
        assert config.enabled_platforms == ["mist"]

    def test_whitespace_in_secret_files_is_stripped(self, tmp_path, monkeypatch):
        """Secret values with leading/trailing whitespace or newlines are stripped."""
        import hpe_networking_mcp.config as config_module

        _write_secret(tmp_path, "mist_api_token", "  test-mist-token\n")
        _write_secret(tmp_path, "mist_host", "\tapi.mist.com  \n")

        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))

        config = config_module.load_config()

        assert config.mist is not None
        assert config.mist.api_token == "test-mist-token"
        assert config.mist.host == "api.mist.com"

    def test_empty_secret_file_disables_platform(self, tmp_path, monkeypatch):
        """A secret file that exists but is empty (or whitespace-only) disables the platform."""
        import hpe_networking_mcp.config as config_module

        _write_secret(tmp_path, "mist_api_token", "   ")  # whitespace only
        _write_secret(tmp_path, "mist_host", "api.mist.com")

        monkeypatch.setattr(config_module, "SECRETS_DIR", str(tmp_path))

        # Mist disabled because api_token is empty after strip, no other platforms
        with pytest.raises(SystemExit):
            config_module.load_config()
