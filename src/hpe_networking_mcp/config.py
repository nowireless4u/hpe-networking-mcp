"""Secrets and configuration management for HPE Networking MCP Server.

Loads credentials from Docker Compose secrets files at /run/secrets/.
Each secret is a separate file. Missing secret files auto-disable that platform.

Docker Compose secrets are:
- Mounted read-only at /run/secrets/<name>
- Not exposed in `docker inspect` or environment variables
- Not baked into the Docker image

Secret file mapping:
    /run/secrets/mist_api_token
    /run/secrets/mist_host
    /run/secrets/central_base_url
    /run/secrets/central_client_id
    /run/secrets/central_client_secret
    /run/secrets/greenlake_api_base_url
    /run/secrets/greenlake_client_id
    /run/secrets/greenlake_client_secret
    /run/secrets/greenlake_workspace_id
    /run/secrets/clearpass_server
    /run/secrets/clearpass_client_id
    /run/secrets/clearpass_client_secret
    /run/secrets/clearpass_verify_ssl (optional, default true)
    /run/secrets/apstra_server
    /run/secrets/apstra_port (optional, default 443)
    /run/secrets/apstra_username
    /run/secrets/apstra_password
    /run/secrets/apstra_verify_ssl (optional, default true)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from hpe_networking_mcp.utils.logging import mask_secret

# Default Docker secrets mount path
SECRETS_DIR = os.getenv("SECRETS_DIR", "/run/secrets")


@dataclass
class MistSecrets:
    api_token: str
    host: str


@dataclass
class CentralSecrets:
    base_url: str
    client_id: str
    client_secret: str


@dataclass
class GreenLakeSecrets:
    api_base_url: str
    client_id: str
    client_secret: str
    workspace_id: str


@dataclass
class ClearPassSecrets:
    server: str  # e.g. https://clearpass.example.com/api
    client_id: str
    client_secret: str
    verify_ssl: bool = True


@dataclass
class ApstraSecrets:
    server: str  # hostname only, e.g. apstra.example.com
    username: str
    password: str
    port: int = 443
    verify_ssl: bool = True


@dataclass
class AxisSecrets:
    """Axis Atmos Cloud credentials.

    Single static API token, generated in the Axis admin portal at
    Settings → Admin API → New API Token. There is no refresh mechanism
    — when the token expires, regenerate in the portal and update
    ``axis_api_token``.
    """

    api_token: str


@dataclass
class AOS8Secrets:
    """Aruba OS 8 / Mobility Conductor credentials."""

    host: str
    username: str
    password: str
    port: int = 4343
    verify_ssl: bool = True


@dataclass
class ServerConfig:
    """Global server configuration."""

    port: int = 8000
    host: str = "0.0.0.0"
    log_level: str = "INFO"
    enable_mist_write_tools: bool = False
    enable_central_write_tools: bool = False
    enable_clearpass_write_tools: bool = False
    enable_apstra_write_tools: bool = False
    enable_axis_write_tools: bool = False
    enable_aos8_write_tools: bool = False
    disable_elicitation: bool = False
    debug: bool = False
    log_file: str | None = None

    # Origin allowlist for the streamable-HTTP transport. Defends against
    # browser-driven DNS rebinding (MCP spec requirement). Matches the
    # ``Origin`` request header literally; ``*`` disables the check entirely.
    # Non-browser clients (supergateway, curl, native MCP clients) don't
    # send Origin and are always allowed.
    allowed_origins: list[str] = field(default_factory=lambda: ["http://localhost:8000", "http://127.0.0.1:8000"])

    # Tool exposure mode (generalized from GreenLake's original setting, #151).
    # "static"  — every tool registers with FastMCP individually; all visible.
    # "dynamic" — the per-platform 3 meta-tools (list / schema / invoke) are
    #             exposed; the underlying tools are hidden via a Visibility
    #             transform. Default since v2.0.0.0; set MCP_TOOL_MODE=static
    #             to opt out.
    tool_mode: str = "dynamic"

    # PII tokenization (v2.3.1.0). When enabled, sensitive fields (PSKs,
    # RADIUS secrets, certificates) and identifiers (UUIDs, hostnames,
    # emails, etc.) in tool responses are replaced with session-stable
    # ``[[KIND:uuid]]`` tokens before reaching the AI. The AI can pass
    # the tokens back into write tools; the inbound side substitutes
    # plaintext before the API call. MAC address normalization is
    # always-on regardless of this toggle (no security impact, just
    # consistency). Off by default this release; flip default in PR 2.
    enable_pii_tokenization: bool = False
    pii_max_tokens_per_session: int = 10_000

    # Platform secrets — None means platform is disabled
    mist: MistSecrets | None = None
    central: CentralSecrets | None = None
    greenlake: GreenLakeSecrets | None = None
    clearpass: ClearPassSecrets | None = None
    apstra: ApstraSecrets | None = None
    axis: AxisSecrets | None = None
    aos8: AOS8Secrets | None = None

    @property
    def enabled_platforms(self) -> list[str]:
        platforms = []
        if self.mist:
            platforms.append("mist")
        if self.central:
            platforms.append("central")
        if self.greenlake:
            platforms.append("greenlake")
        if self.clearpass:
            platforms.append("clearpass")
        if self.apstra:
            platforms.append("apstra")
        if self.axis:
            platforms.append("axis")
        if self.aos8:
            platforms.append("aos8")
        return platforms


def _read_secret(name: str) -> str | None:
    """Read a single secret from /run/secrets/<name>.

    Returns the stripped file contents, or None if the file doesn't exist.
    """
    secret_path = Path(SECRETS_DIR) / name
    if secret_path.is_file():
        try:
            value = secret_path.read_text().strip()
            if value:
                return value
        except OSError as e:
            logger.warning("Failed to read secret {}: {}", name, e)
    return None


def _load_mist() -> MistSecrets | None:
    """Load Mist credentials from Docker secrets."""
    api_token = _read_secret("mist_api_token")
    host = _read_secret("mist_host")

    if not api_token:
        logger.info("Mist: disabled (mist_api_token secret not found)")
        return None
    if not host:
        logger.info("Mist: disabled (mist_host secret not found)")
        return None

    logger.info(
        "Mist: credentials loaded (token: {}, host: {})",
        mask_secret(api_token),
        host,
    )
    return MistSecrets(api_token=api_token, host=host)


def _load_central() -> CentralSecrets | None:
    """Load Central credentials from Docker secrets."""
    base_url = _read_secret("central_base_url")
    client_id = _read_secret("central_client_id")
    client_secret = _read_secret("central_client_secret")

    missing = []
    if not base_url:
        missing.append("central_base_url")
    if not client_id:
        missing.append("central_client_id")
    if not client_secret:
        missing.append("central_client_secret")

    if missing:
        logger.info("Central: disabled (missing secrets: {})", ", ".join(missing))
        return None

    assert base_url is not None
    assert client_id is not None
    assert client_secret is not None
    logger.info("Central: credentials loaded (base_url: {})", base_url)
    return CentralSecrets(
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
    )


def _load_greenlake() -> GreenLakeSecrets | None:
    """Load GreenLake credentials from Docker secrets."""
    api_base_url = _read_secret("greenlake_api_base_url")
    client_id = _read_secret("greenlake_client_id")
    client_secret = _read_secret("greenlake_client_secret")
    workspace_id = _read_secret("greenlake_workspace_id")

    missing = []
    if not api_base_url:
        missing.append("greenlake_api_base_url")
    if not client_id:
        missing.append("greenlake_client_id")
    if not client_secret:
        missing.append("greenlake_client_secret")
    if not workspace_id:
        missing.append("greenlake_workspace_id")

    if missing:
        logger.info("GreenLake: disabled (missing secrets: {})", ", ".join(missing))
        return None

    assert api_base_url is not None
    assert client_id is not None
    assert client_secret is not None
    assert workspace_id is not None
    logger.info("GreenLake: credentials loaded (base_url: {})", api_base_url)
    return GreenLakeSecrets(
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        workspace_id=workspace_id,
    )


def _load_clearpass() -> ClearPassSecrets | None:
    """Load ClearPass credentials from Docker secrets."""
    server = _read_secret("clearpass_server")
    client_id = _read_secret("clearpass_client_id")
    client_secret = _read_secret("clearpass_client_secret")
    verify_ssl_str = _read_secret("clearpass_verify_ssl")

    missing = []
    if not server:
        missing.append("clearpass_server")
    if not client_id:
        missing.append("clearpass_client_id")
    if not client_secret:
        missing.append("clearpass_client_secret")

    if missing:
        logger.info("ClearPass: disabled (missing secrets: {})", ", ".join(missing))
        return None

    assert server is not None
    assert client_id is not None
    assert client_secret is not None

    verify_ssl = verify_ssl_str.lower() not in ("false", "0", "no") if verify_ssl_str else True

    logger.info("ClearPass: credentials loaded (server: {})", server)
    return ClearPassSecrets(
        server=server,
        client_id=client_id,
        client_secret=client_secret,
        verify_ssl=verify_ssl,
    )


def _load_apstra() -> ApstraSecrets | None:
    """Load Apstra credentials from Docker secrets."""
    server = _read_secret("apstra_server")
    port_str = _read_secret("apstra_port")
    username = _read_secret("apstra_username")
    password = _read_secret("apstra_password")
    verify_ssl_str = _read_secret("apstra_verify_ssl")

    missing = []
    if not server:
        missing.append("apstra_server")
    if not username:
        missing.append("apstra_username")
    if not password:
        missing.append("apstra_password")

    if missing:
        logger.info("Apstra: disabled (missing secrets: {})", ", ".join(missing))
        return None

    assert server is not None
    assert username is not None
    assert password is not None

    try:
        port = int(port_str) if port_str else 443
    except ValueError:
        logger.warning("Apstra: invalid apstra_port value '{}', defaulting to 443", port_str)
        port = 443

    verify_ssl = verify_ssl_str.lower() not in ("false", "0", "no") if verify_ssl_str else True

    logger.info(
        "Apstra: credentials loaded (server: {}, port: {}, user: {}, verify_ssl: {})",
        server,
        port,
        username,
        verify_ssl,
    )
    return ApstraSecrets(
        server=server,
        username=username,
        password=password,
        port=port,
        verify_ssl=verify_ssl,
    )


def _load_axis() -> AxisSecrets | None:
    """Load Axis Atmos Cloud credentials from Docker secrets."""
    api_token = _read_secret("axis_api_token")
    if not api_token:
        logger.info("Axis: disabled (axis_api_token secret not found)")
        return None
    logger.info("Axis: credentials loaded (token: {})", mask_secret(api_token))
    return AxisSecrets(api_token=api_token)


def _load_aos8() -> AOS8Secrets | None:
    """Load AOS8 / Mobility Conductor credentials from Docker secrets.

    Returns:
        AOS8Secrets if all required secrets (host, username, password) are present
        and non-empty. None otherwise — logged at INFO level with the list of
        missing secret names. Optional secrets (port, verify_ssl) fall back to
        defaults (4343, True) when absent or empty.
    """
    host = _read_secret("aos8_host")
    username = _read_secret("aos8_username")
    password = _read_secret("aos8_password")
    port_str = _read_secret("aos8_port")
    verify_ssl_str = _read_secret("aos8_verify_ssl")

    missing: list[str] = []
    if not host:
        missing.append("aos8_host")
    if not username:
        missing.append("aos8_username")
    if not password:
        missing.append("aos8_password")

    if missing:
        logger.info("AOS8: disabled (missing secrets: {})", ", ".join(missing))
        return None

    assert host is not None
    assert username is not None
    assert password is not None

    try:
        port = int(port_str) if port_str else 4343
    except ValueError:
        logger.warning("AOS8: invalid aos8_port value '{}', defaulting to 4343", port_str)
        port = 4343

    verify_ssl = verify_ssl_str.lower() not in ("false", "0", "no") if verify_ssl_str else True

    logger.info(
        "AOS8: credentials loaded (host: {}, port: {}, user: {}, verify_ssl: {})",
        host,
        port,
        username,
        verify_ssl,
    )
    return AOS8Secrets(
        host=host,
        username=username,
        password=password,
        port=port,
        verify_ssl=verify_ssl,
    )


def load_config() -> ServerConfig:
    """Load server configuration from Docker secrets and environment variables.

    Secrets are read from files at /run/secrets/<name> (Docker Compose secrets).
    Server settings come from environment variables:
        MCP_PORT, MCP_HOST, LOG_LEVEL, ENABLE_WRITE_TOOLS,
        DISABLE_ELICITATION, MCP_TOOL_MODE

    Returns:
        ServerConfig with validated platform credentials.

    Raises:
        SystemExit: If no platforms have valid credentials.
    """
    logger.info("Loading secrets from {}", SECRETS_DIR)

    # Parse environment overrides for server settings
    port = int(os.getenv("MCP_PORT", "8000"))
    host = os.getenv("MCP_HOST", "0.0.0.0")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    _truthy = ("true", "1", "yes")
    enable_mist_write = os.getenv("ENABLE_MIST_WRITE_TOOLS", "false").lower() in _truthy
    enable_central_write = os.getenv("ENABLE_CENTRAL_WRITE_TOOLS", "false").lower() in _truthy
    enable_clearpass_write = os.getenv("ENABLE_CLEARPASS_WRITE_TOOLS", "false").lower() in _truthy
    enable_apstra_write = os.getenv("ENABLE_APSTRA_WRITE_TOOLS", "false").lower() in _truthy
    enable_axis_write = os.getenv("ENABLE_AXIS_WRITE_TOOLS", "false").lower() in _truthy
    enable_aos8_write = os.getenv("ENABLE_AOS8_WRITE_TOOLS", "false").lower() in _truthy
    disable_elicit = os.getenv("DISABLE_ELICITATION", "false").lower() in _truthy
    debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    log_file = os.getenv("LOG_FILE") or None

    # Tool exposure mode — MCP_TOOL_MODE env var. Same env-var name as the
    # old GreenLake-specific setting; the internal config field is now just
    # ``tool_mode`` because every platform honors it in v2.0. Default flipped
    # from "static" → "dynamic" in v2.0.0.0.
    tool_mode = os.getenv("MCP_TOOL_MODE", "dynamic").lower().strip()
    if tool_mode not in ("static", "dynamic", "code"):
        logger.warning("Ignoring unknown MCP_TOOL_MODE={!r}, defaulting to 'dynamic'", tool_mode)
        tool_mode = "dynamic"

    # ALLOWED_ORIGINS — comma-separated. Empty value falls back to the
    # localhost defaults (most users). ``*`` disables the check.
    allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
    if allowed_origins_env is None:
        allowed_origins = [f"http://localhost:{port}", f"http://127.0.0.1:{port}"]
    else:
        allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

    # PII tokenization (v2.3.1.0). MAC normalization runs regardless;
    # full tokenization is opt-in via ENABLE_PII_TOKENIZATION while the
    # ruleset matures.
    enable_pii_tokenization = os.getenv("ENABLE_PII_TOKENIZATION", "false").lower() in _truthy
    try:
        pii_max_tokens = int(os.getenv("PII_MAX_TOKENS_PER_SESSION", "10000"))
    except ValueError:
        logger.warning(
            "Invalid PII_MAX_TOKENS_PER_SESSION; defaulting to 10000",
        )
        pii_max_tokens = 10_000

    # Load platform credentials from Docker secrets
    mist = _load_mist()
    central = _load_central()
    greenlake = _load_greenlake()
    clearpass = _load_clearpass()
    apstra = _load_apstra()
    axis = _load_axis()
    aos8 = _load_aos8()

    config = ServerConfig(
        port=port,
        host=host,
        log_level=log_level,
        enable_mist_write_tools=enable_mist_write,
        enable_central_write_tools=enable_central_write,
        enable_clearpass_write_tools=enable_clearpass_write,
        enable_apstra_write_tools=enable_apstra_write,
        enable_axis_write_tools=enable_axis_write,
        enable_aos8_write_tools=enable_aos8_write,
        disable_elicitation=disable_elicit,
        debug=debug,
        log_file=log_file,
        tool_mode=tool_mode,
        allowed_origins=allowed_origins,
        enable_pii_tokenization=enable_pii_tokenization,
        pii_max_tokens_per_session=pii_max_tokens,
        mist=mist,
        central=central,
        greenlake=greenlake,
        clearpass=clearpass,
        apstra=apstra,
        axis=axis,
        aos8=aos8,
    )

    if not config.enabled_platforms:
        logger.error(
            "No platforms have valid credentials. Create secret files in {} (see secrets/ directory for examples).",
            SECRETS_DIR,
        )
        raise SystemExit(1)

    logger.info("Enabled platforms: {}", ", ".join(config.enabled_platforms))
    logger.info("Tool mode: {}", tool_mode)
    if "*" in allowed_origins:
        logger.warning("Origin validation: DISABLED (ALLOWED_ORIGINS contains '*')")
    else:
        logger.info("Origin validation: allowlist = {}", allowed_origins)
    if enable_pii_tokenization:
        logger.info(
            "PII tokenization: ENABLED (max {} tokens/session, MAC normalization always-on)",
            pii_max_tokens,
        )
    else:
        logger.info("PII tokenization: disabled (MAC normalization still applied)")
    return config
