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
        assert config.apstra is not None
        assert set(config.enabled_platforms) == {"mist", "central", "greenlake", "apstra", "aos8"}

    def test_raises_system_exit_when_no_platforms_have_credentials(self, tmp_path, monkeypatch):
        """An empty secrets directory means zero platforms -- must exit."""
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        with pytest.raises(SystemExit):
            load_config()

    def test_returns_config_with_only_mist_enabled(self, patch_secrets_dir):
        # Remove Central, GreenLake, and Apstra secrets
        for name in [
            "central_base_url",
            "central_client_id",
            "central_client_secret",
            "greenlake_api_base_url",
            "greenlake_client_id",
            "greenlake_client_secret",
            "greenlake_workspace_id",
            "aos8_host",
            "aos8_username",
            "aos8_password",
            "aos8_port",
            "aos8_verify_ssl",
            "apstra_server",
            "apstra_port",
            "apstra_username",
            "apstra_password",
            "apstra_verify_ssl",
        ]:
            (patch_secrets_dir / name).unlink()
        config = load_config()
        assert config.enabled_platforms == ["mist"]
        assert config.central is None
        assert config.greenlake is None
        assert config.apstra is None

    def test_reads_env_overrides(self, patch_secrets_dir, monkeypatch):
        monkeypatch.setenv("MCP_PORT", "9090")
        monkeypatch.setenv("LOG_LEVEL", "debug")
        monkeypatch.setenv("ENABLE_MIST_WRITE_TOOLS", "true")
        monkeypatch.setenv("ENABLE_CENTRAL_WRITE_TOOLS", "yes")
        monkeypatch.setenv("ENABLE_AOS8_WRITE_TOOLS", "true")
        monkeypatch.setenv("DISABLE_ELICITATION", "yes")
        monkeypatch.setenv("DEBUG", "1")
        config = load_config()
        assert config.port == 9090
        assert config.log_level == "DEBUG"
        assert config.enable_mist_write_tools is True
        assert config.enable_central_write_tools is True
        assert config.enable_aos8_write_tools is True
        assert config.disable_elicitation is True
        assert config.debug is True

    def test_code_sandbox_max_duration_defaults_to_30(self, patch_secrets_dir, monkeypatch):
        monkeypatch.delenv("CODE_SANDBOX_MAX_DURATION_SECS", raising=False)
        config = load_config()
        assert config.code_sandbox_max_duration_secs == 30.0

    def test_code_sandbox_max_duration_env_override(self, patch_secrets_dir, monkeypatch):
        monkeypatch.setenv("CODE_SANDBOX_MAX_DURATION_SECS", "90")
        config = load_config()
        assert config.code_sandbox_max_duration_secs == 90.0

    @pytest.mark.parametrize("bad_value", ["abc", "0", "-5", ""])
    def test_code_sandbox_max_duration_invalid_falls_back_to_30(self, patch_secrets_dir, monkeypatch, bad_value):
        monkeypatch.setenv("CODE_SANDBOX_MAX_DURATION_SECS", bad_value)
        config = load_config()
        assert config.code_sandbox_max_duration_secs == 30.0

    def test_customer_name_from_env(self, patch_secrets_dir, monkeypatch):
        monkeypatch.setenv("CUSTOMER_NAME", "Acme-Corp")
        config = load_config()
        assert config.customer_name == "Acme-Corp"

    def test_customer_name_defaults_to_none(self, patch_secrets_dir, monkeypatch):
        monkeypatch.delenv("CUSTOMER_NAME", raising=False)
        config = load_config()
        assert config.customer_name is None

    def test_customer_name_empty_treated_as_none(self, patch_secrets_dir, monkeypatch):
        monkeypatch.setenv("CUSTOMER_NAME", "   ")
        config = load_config()
        assert config.customer_name is None


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


# ---------------------------------------------------------------------------
# _read_secret — environment variable fallback
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestReadSecretEnvFallback:
    """Tests for the two-tier lookup: Docker secret file > env var > None."""

    def test_env_var_used_when_file_missing(self, patch_secrets_dir, monkeypatch):
        """Env var provides the value when no secret file exists."""
        monkeypatch.setenv("NONEXISTENT_SECRET", "from-env")
        result = _read_secret("nonexistent_secret")
        assert result == "from-env"

    def test_file_takes_priority_over_env_var(self, patch_secrets_dir, monkeypatch):
        """Docker secret file wins when both file and env var exist."""
        monkeypatch.setenv("MIST_API_TOKEN", "from-env")
        result = _read_secret("mist_api_token")
        assert result == "test-mist-token-value-1234"

    def test_returns_none_when_neither_source(self, patch_secrets_dir, monkeypatch):
        """Returns None when no file and no env var."""
        monkeypatch.delenv("TOTALLY_MISSING", raising=False)
        result = _read_secret("totally_missing")
        assert result is None

    def test_env_var_whitespace_stripped(self, patch_secrets_dir, monkeypatch):
        """Env var value is stripped of surrounding whitespace."""
        monkeypatch.setenv("PADDED_VALUE", "  my-token  ")
        result = _read_secret("padded_value")
        assert result == "my-token"

    def test_empty_env_var_treated_as_missing(self, patch_secrets_dir, monkeypatch):
        """Empty or whitespace-only env var is treated as not set."""
        monkeypatch.setenv("EMPTY_VAR", "   ")
        result = _read_secret("empty_var")
        assert result is None

    def test_empty_file_falls_through_to_env_var(self, patch_secrets_dir, monkeypatch):
        """Empty secret file falls through to env var."""
        (patch_secrets_dir / "empty_file").write_text("")
        monkeypatch.setenv("EMPTY_FILE", "from-env")
        result = _read_secret("empty_file")
        assert result == "from-env"


@pytest.mark.unit
class TestLoadConfigFromEnvVars:
    """Test that platforms can be enabled purely via environment variables."""

    def test_mist_enabled_via_env_only(self, tmp_path, monkeypatch):
        """Mist enabled with env vars and empty secrets dir."""
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        monkeypatch.setenv("MIST_API_TOKEN", "env-token-value")
        monkeypatch.setenv("MIST_HOST", "api.eu.mist.com")
        config = load_config()
        assert "mist" in config.enabled_platforms
        assert config.mist is not None
        assert config.mist.api_token == "env-token-value"
        assert config.mist.host == "api.eu.mist.com"

    def test_central_enabled_via_env_only(self, tmp_path, monkeypatch):
        """Central enabled with env vars and empty secrets dir."""
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        monkeypatch.setenv("CENTRAL_BASE_URL", "https://apigw-us1.central.arubanetworks.com")
        monkeypatch.setenv("CENTRAL_CLIENT_ID", "env-client-id")
        monkeypatch.setenv("CENTRAL_CLIENT_SECRET", "env-client-secret")
        config = load_config()
        assert "central" in config.enabled_platforms
        assert config.central is not None
        assert config.central.base_url == "https://apigw-us1.central.arubanetworks.com"

    def test_multiple_platforms_via_env(self, tmp_path, monkeypatch):
        """Multiple platforms enabled simultaneously from env vars."""
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        monkeypatch.setenv("MIST_API_TOKEN", "t")
        monkeypatch.setenv("MIST_HOST", "api.mist.com")
        monkeypatch.setenv("AXIS_API_TOKEN", "axis-token")
        config = load_config()
        assert set(config.enabled_platforms) == {"mist", "axis"}
