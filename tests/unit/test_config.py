"""Unit tests for hpe_networking_mcp.config — secrets loading and ServerConfig."""

import pytest

from hpe_networking_mcp.config import (
    CentralSecrets,
    GreenLakeSecrets,
    MistSecrets,
    ServerConfig,
    _load_central,
    _load_greenlake,
    _load_mist,
    _read_secret,
    load_config,
)

# ---------------------------------------------------------------------------
# _read_secret
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestReadSecret:
    def test_returns_contents_when_file_exists(self, patch_secrets_dir):
        result = _read_secret("mist_api_token")
        assert result == "test-mist-token-value-1234"

    def test_returns_none_when_file_missing(self, patch_secrets_dir):
        result = _read_secret("nonexistent_secret")
        assert result is None

    def test_returns_none_for_empty_file(self, patch_secrets_dir):
        (patch_secrets_dir / "empty_secret").write_text("")
        result = _read_secret("empty_secret")
        assert result is None

    def test_returns_none_for_whitespace_only_file(self, patch_secrets_dir):
        (patch_secrets_dir / "whitespace_secret").write_text("   \n  \t  \n")
        result = _read_secret("whitespace_secret")
        assert result is None

    def test_strips_whitespace_from_value(self, patch_secrets_dir):
        (patch_secrets_dir / "padded_secret").write_text("  my-token  \n")
        result = _read_secret("padded_secret")
        assert result == "my-token"


# ---------------------------------------------------------------------------
# _load_mist
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLoadMist:
    def test_returns_mist_secrets_when_both_files_present(self, patch_secrets_dir):
        result = _load_mist()
        assert isinstance(result, MistSecrets)
        assert result.api_token == "test-mist-token-value-1234"
        assert result.host == "api.mist.com"

    def test_returns_none_when_api_token_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "mist_api_token").unlink()
        result = _load_mist()
        assert result is None

    def test_returns_none_when_host_missing(self, patch_secrets_dir):
        (patch_secrets_dir / "mist_host").unlink()
        result = _load_mist()
        assert result is None


# ---------------------------------------------------------------------------
# _load_central
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLoadCentral:
    def test_returns_central_secrets_when_all_files_present(self, patch_secrets_dir):
        result = _load_central()
        assert isinstance(result, CentralSecrets)
        assert result.base_url == "https://us5.api.central.arubanetworks.com"
        assert result.client_id == "central-client-id-value"
        assert result.client_secret == "central-client-secret-value"

    @pytest.mark.parametrize(
        "missing_file",
        ["central_base_url", "central_client_id", "central_client_secret"],
    )
    def test_returns_none_when_any_file_missing(self, patch_secrets_dir, missing_file):
        (patch_secrets_dir / missing_file).unlink()
        result = _load_central()
        assert result is None


# ---------------------------------------------------------------------------
# _load_greenlake
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLoadGreenLake:
    def test_returns_greenlake_secrets_when_all_files_present(self, patch_secrets_dir):
        result = _load_greenlake()
        assert isinstance(result, GreenLakeSecrets)
        assert result.api_base_url == "https://global.api.greenlake.hpe.com"
        assert result.client_id == "greenlake-client-id-value"
        assert result.client_secret == "greenlake-client-secret-value"
        assert result.workspace_id == "greenlake-workspace-id-value"

    @pytest.mark.parametrize(
        "missing_file",
        [
            "greenlake_api_base_url",
            "greenlake_client_id",
            "greenlake_client_secret",
            "greenlake_workspace_id",
        ],
    )
    def test_returns_none_when_any_file_missing(self, patch_secrets_dir, missing_file):
        (patch_secrets_dir / missing_file).unlink()
        result = _load_greenlake()
        assert result is None


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLoadConfig:
    def test_returns_config_with_all_platforms_enabled(self, patch_secrets_dir):
        config = load_config()
        assert isinstance(config, ServerConfig)
        assert config.mist is not None
        assert config.central is not None
        assert config.greenlake is not None
        assert set(config.enabled_platforms) == {"mist", "central", "greenlake"}

    def test_raises_system_exit_when_no_platforms_have_credentials(self, tmp_path, monkeypatch):
        """An empty secrets directory means zero platforms -- must exit."""
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        with pytest.raises(SystemExit):
            load_config()

    def test_returns_config_with_only_mist_enabled(self, patch_secrets_dir):
        # Remove Central and GreenLake secrets
        for name in [
            "central_base_url",
            "central_client_id",
            "central_client_secret",
            "greenlake_api_base_url",
            "greenlake_client_id",
            "greenlake_client_secret",
            "greenlake_workspace_id",
        ]:
            (patch_secrets_dir / name).unlink()
        config = load_config()
        assert config.enabled_platforms == ["mist"]
        assert config.central is None
        assert config.greenlake is None

    def test_reads_env_overrides(self, patch_secrets_dir, monkeypatch):
        monkeypatch.setenv("MCP_PORT", "9090")
        monkeypatch.setenv("LOG_LEVEL", "debug")
        monkeypatch.setenv("ENABLE_MIST_WRITE_TOOLS", "true")
        monkeypatch.setenv("ENABLE_CENTRAL_WRITE_TOOLS", "yes")
        monkeypatch.setenv("DISABLE_ELICITATION", "yes")
        monkeypatch.setenv("DEBUG", "1")
        config = load_config()
        assert config.port == 9090
        assert config.log_level == "DEBUG"
        assert config.enable_mist_write_tools is True
        assert config.enable_central_write_tools is True
        assert config.disable_elicitation is True
        assert config.debug is True


# ---------------------------------------------------------------------------
# enabled_platforms property
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEnabledPlatforms:
    def test_empty_when_no_platforms(self):
        config = ServerConfig()
        assert config.enabled_platforms == []

    def test_returns_mist_only(self):
        config = ServerConfig(mist=MistSecrets(api_token="t", host="h"))
        assert config.enabled_platforms == ["mist"]

    def test_returns_all_three(self):
        config = ServerConfig(
            mist=MistSecrets(api_token="t", host="h"),
            central=CentralSecrets(base_url="u", client_id="c", client_secret="s"),
            greenlake=GreenLakeSecrets(api_base_url="u", client_id="c", client_secret="s", workspace_id="w"),
        )
        assert config.enabled_platforms == ["mist", "central", "greenlake"]
