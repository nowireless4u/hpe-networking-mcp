"""FastMCP server setup, lifespan management, and tool loading."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

_INSTRUCTIONS = (Path(__file__).parent / "INSTRUCTIONS.md").read_text()


@asynccontextmanager
async def lifespan(server: FastMCP):
    """Initialize platform clients at startup, clean up on shutdown."""
    # Config is attached to the server instance before run() is called
    config: ServerConfig = server._hpe_config  # type: ignore[attr-defined]
    context: dict = {"config": config}

    # --- Mist ---
    if config.mist:
        try:
            import mistapi

            mist_session = mistapi.APISession(
                host=config.mist.host,
                apitoken=config.mist.api_token,
            )
            # Disable mistapi's own console output (method varies by version)
            if hasattr(mist_session, "set_verbose"):
                mist_session.set_verbose(False)
            context["mist_session"] = mist_session
            # Resolve org_id from API token at startup
            try:
                self_resp = mistapi.api.v1.self.self.getSelf(mist_session)
                if self_resp.status_code == 200 and self_resp.data:
                    privileges = self_resp.data.get("privileges", [])
                    org_privs = [p for p in privileges if p.get("scope") == "org"]
                    if org_privs:
                        context["mist_org_id"] = org_privs[0]["org_id"]
                        logger.info("Mist: resolved org_id={}", context["mist_org_id"])
            except Exception as e:
                logger.warning("Mist: failed to resolve org_id at startup — {}", e)
            logger.info("Mist: API session initialized")
        except Exception as e:
            logger.warning("Mist: failed to initialize — {}", e)
            context["mist_session"] = None
    else:
        context["mist_session"] = None

    # --- Central ---
    if config.central:
        try:
            from pycentral import NewCentralBase

            central_conn = NewCentralBase(
                token_info={
                    "new_central": {
                        "base_url": config.central.base_url,
                        "client_id": config.central.client_id,
                        "client_secret": config.central.client_secret,
                    }
                }
            )
            # Verify with lightweight call
            resp = central_conn.command(
                "GET",
                "network-monitoring/v1/sites-health",
                api_params={"limit": 1},
            )
            if resp.get("code") and 200 <= resp["code"] < 300:
                logger.info("Central: connection verified")
            else:
                logger.warning(
                    "Central: verification returned code {}",
                    resp.get("code"),
                )
            context["central_conn"] = central_conn
        except Exception as e:
            logger.warning("Central: failed to initialize — {}", e)
            context["central_conn"] = None
    else:
        context["central_conn"] = None

    # --- GreenLake ---
    if config.greenlake:
        try:
            from hpe_networking_mcp.platforms.greenlake.auth import (
                TokenManager,
            )

            gl_token_mgr = TokenManager(
                api_base_url=config.greenlake.api_base_url,
                client_id=config.greenlake.client_id,
                client_secret=config.greenlake.client_secret,
                workspace_id=config.greenlake.workspace_id,
            )
            context["greenlake_token_manager"] = gl_token_mgr
            logger.info("GreenLake: token manager initialized")
        except Exception as e:
            logger.warning("GreenLake: failed to initialize — {}", e)
            context["greenlake_token_manager"] = None
    else:
        context["greenlake_token_manager"] = None

    # --- ClearPass ---
    if config.clearpass:
        try:
            from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

            test_client = ApiLocalServerConfiguration(
                server=config.clearpass.server,
                granttype="client_credentials",
                clientid=config.clearpass.client_id,
                clientsecret=config.clearpass.client_secret,
            )
            test_client.verify_ssl = config.clearpass.verify_ssl
            version_info = test_client.get_server_version()
            # Check if auth failed — pyclearpass returns error dicts instead of raising
            if not test_client.api_token:
                error_detail = (
                    version_info.get("detail", "unknown error") if isinstance(version_info, dict) else str(version_info)
                )
                raise RuntimeError(f"OAuth2 authentication failed: {error_detail}")
            # Cache token for reuse across all tool calls
            context["clearpass_token"] = test_client.api_token
            context["clearpass_config"] = config.clearpass
            version_str = version_info.get("app_major_version", "unknown") if isinstance(version_info, dict) else "?"
            logger.info("ClearPass: connection verified (version: {})", version_str)
        except Exception as e:
            logger.warning("ClearPass: failed to initialize — {}", e)
            context["clearpass_config"] = None
            context["clearpass_token"] = None
    else:
        context["clearpass_config"] = None
        context["clearpass_token"] = None

    try:
        yield context
    finally:
        # Cleanup
        gl_tm = context.get("greenlake_token_manager")
        if gl_tm and hasattr(gl_tm, "close"):
            await gl_tm.close()
        logger.info("Server shutdown complete")


def create_server(config: ServerConfig) -> FastMCP:
    """Create and configure the FastMCP server with all enabled platform tools."""
    from hpe_networking_mcp.middleware.elicitation import (
        ElicitationMiddleware,
    )
    from hpe_networking_mcp.middleware.null_strip import NullStripMiddleware

    mcp = FastMCP(
        name="HPE Networking MCP",
        instructions=_INSTRUCTIONS,
        lifespan=lifespan,
        on_duplicate="replace",
        mask_error_details=True,
        middleware=[NullStripMiddleware(), ElicitationMiddleware()],
    )

    # Attach config for lifespan to access
    mcp._hpe_config = config  # type: ignore[attr-defined]

    # --- Register platform tools ---
    if config.mist:
        _register_mist_tools(mcp, config)
    if config.central:
        _register_central_tools(mcp, config)
    if config.greenlake:
        _register_greenlake_tools(mcp, config)
    if config.clearpass:
        _register_clearpass_tools(mcp, config)

    # --- Cross-platform tools and prompts (require both Mist and Central) ---
    if config.mist and config.central:
        _register_sync_tools(mcp)
        _register_sync_prompts(mcp)

    # --- Write tool visibility (per-platform) ---
    from fastmcp.server.transforms import Visibility

    if not config.enable_mist_write_tools:
        mcp.add_transform(Visibility(False, tags={"mist_write", "mist_write_delete"}, components={"tool"}))
    if not config.enable_central_write_tools:
        mcp.add_transform(Visibility(False, tags={"central_write_delete"}, components={"tool"}))
    if not config.enable_clearpass_write_tools:
        mcp.add_transform(Visibility(False, tags={"clearpass_write_delete"}, components={"tool"}))

    return mcp


def _register_mist_tools(mcp: FastMCP, config: ServerConfig) -> None:
    """Register all Mist platform tools."""
    from hpe_networking_mcp.platforms.mist import register_tools

    count = register_tools(mcp, config)
    logger.info("Mist: registered {} tools", count)


def _register_central_tools(mcp: FastMCP, config: ServerConfig) -> None:
    """Register all Central platform tools."""
    from hpe_networking_mcp.platforms.central import register_tools

    count = register_tools(mcp, config)
    logger.info("Central: registered {} tools", count)


def _register_greenlake_tools(mcp: FastMCP, config: ServerConfig) -> None:
    """Register all GreenLake platform tools."""
    from hpe_networking_mcp.platforms.greenlake import register_tools

    count = register_tools(mcp, config)
    logger.info("GreenLake: registered {} tools", count)


def _register_clearpass_tools(mcp: FastMCP, config: ServerConfig) -> None:
    """Register all ClearPass platform tools."""
    from hpe_networking_mcp.platforms.clearpass import register_tools

    count = register_tools(mcp, config)
    logger.info("ClearPass: registered {} tools", count)


def _register_sync_tools(mcp: FastMCP) -> None:
    """Register cross-platform WLAN management tool (requires both Mist and Central)."""
    try:
        from hpe_networking_mcp.platforms.manage_wlan import register

        register(mcp)
        logger.info("Cross-platform: registered manage_wlan_profile tool")
    except Exception as e:
        logger.warning("Cross-platform: failed to load manage_wlan_profile — {}", e)


def _register_sync_prompts(mcp: FastMCP) -> None:
    """Register cross-platform WLAN sync prompts (requires both Mist and Central)."""
    try:
        from hpe_networking_mcp.platforms.sync_prompts import register

        register(mcp)
        logger.info("Cross-platform: registered sync prompts")
    except Exception as e:
        logger.warning("Cross-platform: failed to load sync prompts — {}", e)
