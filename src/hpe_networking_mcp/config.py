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
"""

import os
from dataclasses import dataclass
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
class ServerConfig:
    """Global server configuration."""

    port: int = 8000
    host: str = "0.0.0.0"
    log_level: str = "INFO"
    enable_write_tools: bool = False
    disable_elicitation: bool = False
    debug: bool = False
    log_file: str | None = None

    # GreenLake tool mode: "static" (10 dedicated tools) or "dynamic" (3 meta-tools)
    greenlake_tool_mode: str = "static"

    # Platform secrets — None means platform is disabled
    mist: MistSecrets | None = None
    central: CentralSecrets | None = None
    greenlake: GreenLakeSecrets | None = None

    @property
    def enabled_platforms(self) -> list[str]:
        platforms = []
        if self.mist:
            platforms.append("mist")
        if self.central:
            platforms.append("central")
        if self.greenlake:
            platforms.append("greenlake")
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

    logger.info("Mist: credentials loaded (token: {}, host: {})", mask_secret(api_token), host)
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

    logger.info("Central: credentials loaded (base_url: {})", base_url)
    return CentralSecrets(base_url=base_url, client_id=client_id, client_secret=client_secret)


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

    logger.info("GreenLake: credentials loaded (base_url: {})", api_base_url)
    return GreenLakeSecrets(
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        workspace_id=workspace_id,
    )


def load_config() -> ServerConfig:
    """Load server configuration from Docker secrets and environment variables.

    Secrets are read from files at /run/secrets/<name> (Docker Compose secrets).
    Server settings come from environment variables:
        MCP_PORT, MCP_HOST, LOG_LEVEL, ENABLE_WRITE_TOOLS, DISABLE_ELICITATION,
        MCP_TOOL_MODE

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
    enable_write = os.getenv("ENABLE_WRITE_TOOLS", "false").lower() in ("true", "1", "yes")
    disable_elicit = os.getenv("DISABLE_ELICITATION", "false").lower() in ("true", "1", "yes")
    debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    log_file = os.getenv("LOG_FILE") or None

    # GreenLake tool mode: "static" (10 dedicated tools) or "dynamic" (3 meta-tools)
    greenlake_tool_mode = os.getenv("MCP_TOOL_MODE", "static").lower().strip()

    # Load platform credentials from Docker secrets
    mist = _load_mist()
    central = _load_central()
    greenlake = _load_greenlake()

    config = ServerConfig(
        port=port,
        host=host,
        log_level=log_level,
        enable_write_tools=enable_write,
        disable_elicitation=disable_elicit,
        debug=debug,
        log_file=log_file,
        greenlake_tool_mode=greenlake_tool_mode,
        mist=mist,
        central=central,
        greenlake=greenlake,
    )

    if not config.enabled_platforms:
        logger.error(
            "No platforms have valid credentials. "
            "Create secret files in {} (see secrets/ directory for examples).",
            SECRETS_DIR,
        )
        raise SystemExit(1)

    logger.info("Enabled platforms: {}", ", ".join(config.enabled_platforms))
    if greenlake_tool_mode != "static":
        logger.info("GreenLake tool mode: {}", greenlake_tool_mode)
    return config
