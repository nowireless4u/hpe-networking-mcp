"""FastMCP server setup, lifespan management, and tool loading."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

_INSTRUCTIONS = (Path(__file__).parent / "INSTRUCTIONS.md").read_text()


class _LifespanProbeCtx:
    """Minimal Context stand-in for the startup probe loop.

    ``platforms/health.py`` probe helpers read from ``ctx.lifespan_context``,
    which doesn't exist yet at lifespan construction time (the dict is
    being *built* into what becomes ``ctx.lifespan_context`` downstream).
    This shim exposes the in-progress dict as ``lifespan_context`` so the
    probes can run against it without duplicating their logic in lifespan.
    """

    def __init__(self, context: dict) -> None:
        self.lifespan_context = context


@asynccontextmanager
async def lifespan(server: FastMCP):
    """Initialize platform clients at startup, clean up on shutdown."""
    # Config is attached to the server instance before run() is called
    config: ServerConfig = server._hpe_config  # type: ignore[attr-defined]
    context: dict = {"config": config}

    # --- Mist ---
    # Construct the session and resolve org_id; the shared probe in
    # platforms/health.py re-verifies via the same getSelf() call at tool time.
    if config.mist:
        try:
            import mistapi

            mist_session = mistapi.APISession(
                host=config.mist.host,
                apitoken=config.mist.api_token,
            )
            if hasattr(mist_session, "set_verbose"):
                mist_session.set_verbose(False)
            context["mist_session"] = mist_session
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
        except Exception as e:
            logger.warning("Mist: failed to initialize — {}", e)
            context["mist_session"] = None
    else:
        context["mist_session"] = None

    # --- Central ---
    if config.central:
        try:
            from pycentral import NewCentralBase

            context["central_conn"] = NewCentralBase(
                token_info={
                    "new_central": {
                        "base_url": config.central.base_url,
                        "client_id": config.central.client_id,
                        "client_secret": config.central.client_secret,
                    }
                }
            )
        except Exception as e:
            logger.warning("Central: failed to initialize — {}", e)
            context["central_conn"] = None
    else:
        context["central_conn"] = None

    # --- GreenLake ---
    if config.greenlake:
        try:
            from hpe_networking_mcp.platforms.greenlake.auth import TokenManager

            context["greenlake_token_manager"] = TokenManager(
                api_base_url=config.greenlake.api_base_url,
                client_id=config.greenlake.client_id,
                client_secret=config.greenlake.client_secret,
                workspace_id=config.greenlake.workspace_id,
            )
        except Exception as e:
            logger.warning("GreenLake: failed to initialize — {}", e)
            context["greenlake_token_manager"] = None
    else:
        context["greenlake_token_manager"] = None

    # --- ClearPass ---
    if config.clearpass:
        try:
            from hpe_networking_mcp.platforms.clearpass.client import ClearPassTokenManager

            context["clearpass_token_manager"] = ClearPassTokenManager(config.clearpass)
            context["clearpass_config"] = config.clearpass
        except Exception as e:
            logger.warning("ClearPass: failed to initialize — {}", e)
            context["clearpass_config"] = None
            context["clearpass_token_manager"] = None
    else:
        context["clearpass_config"] = None
        context["clearpass_token_manager"] = None

    # --- Apstra ---
    if config.apstra:
        try:
            from hpe_networking_mcp.platforms.apstra.client import ApstraClient

            context["apstra_client"] = ApstraClient(config.apstra)
            context["apstra_config"] = config.apstra
        except Exception as e:
            logger.warning("Apstra: failed to initialize — {}", e)
            context["apstra_client"] = None
            context["apstra_config"] = None
    else:
        context["apstra_client"] = None
        context["apstra_config"] = None

    # --- Axis ---
    if config.axis:
        try:
            from hpe_networking_mcp.platforms.axis.client import AxisClient

            context["axis_client"] = AxisClient(config.axis)
            context["axis_config"] = config.axis
        except Exception as e:
            logger.warning("Axis: failed to initialize — {}", e)
            context["axis_client"] = None
            context["axis_config"] = None
    else:
        context["axis_client"] = None
        context["axis_config"] = None

    # --- Verify every enabled platform via the shared probe helpers from
    # platforms/health.py. One source of truth: startup log output and the
    # runtime ``health`` tool report the same status. Probes that fail do
    # not abort startup — the platform stays in the context with degraded
    # status and the health tool surfaces the error. ---
    if config.enabled_platforms:
        try:
            from hpe_networking_mcp.platforms.health import run_probes

            probe_ctx = _LifespanProbeCtx(context)
            results = await run_probes(probe_ctx, list(config.enabled_platforms))
            for platform, result in results.items():
                status = result.get("status")
                detail = result.get("message", "")
                if status == "ok":
                    logger.info("{}: startup probe ok — {}", platform, detail)
                else:
                    logger.warning(
                        "{}: startup probe reported {} — {}",
                        platform,
                        status,
                        detail,
                    )
        except Exception as e:
            logger.warning("Startup probe loop raised unexpectedly — {}", e)

    try:
        yield context
    finally:
        # Cleanup
        gl_tm = context.get("greenlake_token_manager")
        if gl_tm and hasattr(gl_tm, "close"):
            await gl_tm.close()
        apstra = context.get("apstra_client")
        if apstra is not None:
            await apstra.aclose()
        axis = context.get("axis_client")
        if axis is not None:
            await axis.aclose()
        logger.info("Server shutdown complete")


def create_server(config: ServerConfig) -> FastMCP:
    """Create and configure the FastMCP server with all enabled platform tools."""
    from hpe_networking_mcp.middleware.elicitation import (
        ElicitationMiddleware,
    )
    from hpe_networking_mcp.middleware.null_strip import NullStripMiddleware
    from hpe_networking_mcp.middleware.validation_catch import ValidationCatchMiddleware

    mcp = FastMCP(
        name="HPE Networking MCP",
        instructions=_INSTRUCTIONS,
        lifespan=lifespan,
        on_duplicate="replace",
        mask_error_details=True,
        middleware=[NullStripMiddleware(), ValidationCatchMiddleware(), ElicitationMiddleware()],
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
    if config.apstra:
        _register_apstra_tools(mcp, config)
    if config.axis:
        _register_axis_tools(mcp, config)

    # --- Cross-platform aggregators ---
    # These are workarounds for dynamic mode's "AI picks one platform and stops"
    # problem. Code mode's premise is that the LLM can compose per-platform tools
    # into cross-platform answers itself via `call_tool` in the sandbox — so we
    # explicitly do NOT register the aggregators in code mode. If code mode
    # can't reliably synthesize cross-platform answers, that's the "keep dynamic
    # as default" signal, not a reason to re-register them here.
    if config.tool_mode != "code":
        if config.mist and config.central:
            _register_sync_tools(mcp)
            _register_sync_prompts(mcp)
        if config.mist or config.central:
            _register_site_health_check(mcp, config)
            _register_site_rf_check(mcp, config)

    # --- Cross-platform `health` tool (always registered in every mode —
    # reachability info is not aggregation; useful to have callable in the
    # code-mode sandbox too) ---
    from hpe_networking_mcp.platforms.health import register as _register_health

    _register_health(mcp)

    # --- Write tool visibility (per-platform) ---
    from fastmcp.server.transforms import Visibility

    if not config.enable_mist_write_tools:
        mcp.add_transform(Visibility(False, tags={"mist_write", "mist_write_delete"}, components={"tool"}))
    if not config.enable_central_write_tools:
        mcp.add_transform(Visibility(False, tags={"central_write_delete"}, components={"tool"}))
    if not config.enable_clearpass_write_tools:
        mcp.add_transform(Visibility(False, tags={"clearpass_write_delete"}, components={"tool"}))
    if not config.enable_apstra_write_tools:
        mcp.add_transform(Visibility(False, tags={"apstra_write", "apstra_write_delete"}, components={"tool"}))
    if not config.enable_axis_write_tools:
        mcp.add_transform(Visibility(False, tags={"axis_write", "axis_write_delete"}, components={"tool"}))

    # --- Tool-mode-specific catalog transforms ---
    if config.tool_mode == "dynamic":
        # Dynamic mode: hide the individual registry-managed tools so the
        # exposed surface is just the per-platform meta-tools plus the 3
        # cross-platform statics (health, site_health_check, manage_wlan_profile).
        # Tools opt in by being tagged "dynamic_managed" via their platform's
        # tool() shim; any platform that hasn't migrated yet keeps all its
        # tools visible regardless of tool_mode.
        mcp.add_transform(Visibility(False, tags={"dynamic_managed"}, components={"tool"}))
    elif config.tool_mode == "code":
        # Code mode: replace the catalog with `CodeMode` — a four-tier
        # progressive-disclosure surface (get_tags → search → get_schema →
        # execute). The LLM writes Python inside `execute`; `call_tool(name,
        # params)` dispatches through the real FastMCP call_tool, so our
        # NullStripMiddleware + ElicitationMiddleware + Pydantic coercion
        # all keep working. Write gating (the per-platform Visibility
        # transforms above) still fires.
        #
        # Cross-platform aggregators (site_health_check, site_rf_check,
        # manage_wlan_profile) were not registered above in code mode, so
        # they don't leak into Search's catalog.
        _register_code_mode(mcp)

    return mcp


def _register_code_mode(mcp: FastMCP) -> None:
    """Install the FastMCP CodeMode transform for ``MCP_TOOL_MODE=code``.

    Falls back with a warning if ``pydantic-monty`` isn't installed — the
    dependency ships in the ``fastmcp[code-mode]`` extra and is already
    pinned in ``pyproject.toml``, but older wheels may have it missing.
    """
    try:
        from fastmcp.experimental.transforms.code_mode import (
            CodeMode,
            GetSchemas,
            GetTags,
            MontySandboxProvider,
            Search,
        )
        from pydantic_monty import ResourceLimits
    except ImportError as e:
        logger.error(
            "MCP_TOOL_MODE=code requires fastmcp[code-mode] + pydantic-monty ({}); "
            "falling back to untransformed catalog (every registered tool visible)",
            e,
        )
        return

    limits = ResourceLimits(
        max_duration_secs=30.0,
        max_memory=128 * 1024 * 1024,
        max_recursion_depth=50,
    )
    mcp.add_transform(
        CodeMode(
            sandbox_provider=MontySandboxProvider(limits=limits),
            discovery_tools=[
                GetTags(default_detail="brief"),
                Search(default_detail="brief"),
                GetSchemas(default_detail="detailed"),
            ],
        )
    )
    logger.info("Code mode enabled — exposed surface: get_tags + search + get_schema + execute")


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


def _register_apstra_tools(mcp: FastMCP, config: ServerConfig) -> None:
    """Register all Apstra platform tools."""
    from hpe_networking_mcp.platforms.apstra import register_tools

    count = register_tools(mcp, config)
    logger.info("Apstra: registered {} tools", count)


def _register_axis_tools(mcp: FastMCP, config: ServerConfig) -> None:
    """Register all Axis platform tools."""
    from hpe_networking_mcp.platforms.axis import register_tools

    count = register_tools(mcp, config)
    logger.info("Axis: registered {} tools", count)


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


def _register_site_health_check(mcp: FastMCP, config: ServerConfig) -> None:
    """Register the cross-platform site_health_check aggregation tool."""
    try:
        from hpe_networking_mcp.platforms.site_health_check import register

        register(mcp, config)
    except Exception as e:
        logger.warning("Cross-platform: failed to load site_health_check — {}", e)


def _register_site_rf_check(mcp: FastMCP, config: ServerConfig) -> None:
    """Register the cross-platform site_rf_check aggregation tool."""
    try:
        from hpe_networking_mcp.platforms.site_rf_check import register

        register(mcp, config)
    except Exception as e:
        logger.warning("Cross-platform: failed to load site_rf_check — {}", e)
