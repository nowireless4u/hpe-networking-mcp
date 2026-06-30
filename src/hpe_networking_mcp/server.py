"""FastMCP server setup, lifespan management, and tool loading."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools.function_tool import FunctionTool
from fastmcp.tools.tool import ToolResult
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

_INSTRUCTIONS = (Path(__file__).parent / "INSTRUCTIONS.md").read_text(encoding="utf-8")


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
    # FileUpload provider handle (present only when MCP_APP_ENABLE=true) so tools
    # can read an uploaded file server-side without it entering model context.
    context["file_upload_provider"] = getattr(server, "_hpe_file_upload", None)
    # PII token store (always constructed in create_server). Tools that tokenize
    # their own outputs server-side — e.g. greenlake_bulk_add_devices redacting
    # device serials in its result — build a per-session Tokenizer from this.
    # Without it on lifespan_context, that tokenization silently no-ops to a bare
    # ``[serial]`` placeholder (latent gap fixed alongside #546).
    context["token_store"] = getattr(server, "_hpe_token_store", None)

    # --- Mist ---
    # v3.1.0.0 (issue #304): the ``mistapi`` SDK is gone; we go direct via
    # httpx. Build the client from host + token and resolve org_id at
    # startup via a single ``GET /api/v1/self``. The shared probe in
    # platforms/health.py re-verifies at tool time.
    if config.mist:
        try:
            from hpe_networking_mcp.platforms.mist._client import (
                build_mist_client,
                resolve_org_id_from_self,
            )

            mist_client = build_mist_client(
                host=config.mist.host,
                api_token=config.mist.api_token,
            )
            context["mist_client"] = mist_client
            try:
                org_id = await resolve_org_id_from_self(mist_client)
                if org_id:
                    context["mist_org_id"] = org_id
                    logger.info("Mist: resolved org_id={}", org_id)
            except Exception as e:
                logger.warning("Mist: failed to resolve org_id at startup — {}", e)
        except Exception as e:
            logger.warning("Mist: failed to initialize — {}", e)
            context["mist_client"] = None
    else:
        context["mist_client"] = None

    # --- Central ---
    if config.central:
        try:
            from hpe_networking_mcp.platforms.central.client import create_connection

            # Construction is non-blocking: the first API call triggers the
            # initial OAuth2 token fetch via the shared AsyncTokenManager.
            context["central_conn"] = create_connection(config.central)
        except Exception as e:
            logger.warning("Central: failed to initialize — {}", e)
            context["central_conn"] = None
    else:
        context["central_conn"] = None

    # --- GreenLake ---
    if config.greenlake:
        try:
            from hpe_networking_mcp.platforms.greenlake.client import make_token_manager

            # Construction is non-blocking: the first API call triggers the
            # initial token fetch via the shared AsyncTokenManager (the #440
            # to_thread workaround is no longer needed).
            context["greenlake_token_manager"] = make_token_manager(config.greenlake)
        except Exception as e:
            logger.warning("GreenLake: failed to initialize — {}", e)
            context["greenlake_token_manager"] = None
    else:
        context["greenlake_token_manager"] = None

    # --- ClearPass ---
    if config.clearpass:
        try:
            from hpe_networking_mcp.platforms.clearpass.client import create_client

            # Construction is non-blocking: the first API call triggers the
            # initial OAuth2 token fetch via the shared AsyncTokenManager.
            context["clearpass_client"] = create_client(config.clearpass)
        except Exception as e:
            logger.warning("ClearPass: failed to initialize — {}", e)
            context["clearpass_client"] = None
    else:
        context["clearpass_client"] = None

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

    # --- AOS8 ---
    if config.aos8:
        try:
            from hpe_networking_mcp.platforms.aos8.client import AOS8Client

            context["aos8_client"] = AOS8Client(config.aos8)
            context["aos8_config"] = config.aos8
        except Exception as e:
            logger.warning("AOS8: failed to initialize — {}", e)
            context["aos8_client"] = None
            context["aos8_config"] = None
    else:
        context["aos8_client"] = None
        context["aos8_config"] = None

    # --- UXI ---
    if config.uxi:
        try:
            from hpe_networking_mcp.platforms.uxi.client import UXIClient

            context["uxi_client"] = UXIClient(config.uxi)
            context["uxi_config"] = config.uxi
        except Exception as e:
            logger.warning("UXI: failed to initialize — {}", e)
            context["uxi_client"] = None
            context["uxi_config"] = None
    else:
        context["uxi_client"] = None
        context["uxi_config"] = None

    # --- EdgeConnect ---
    if config.edgeconnect:
        try:
            from hpe_networking_mcp.platforms.edgeconnect.client import EdgeConnectClient

            context["edgeconnect_client"] = EdgeConnectClient(config.edgeconnect)
            context["edgeconnect_config"] = config.edgeconnect
        except Exception as e:
            logger.warning("EdgeConnect: failed to initialize — {}", e)
            context["edgeconnect_client"] = None
            context["edgeconnect_config"] = None
    else:
        context["edgeconnect_client"] = None
        context["edgeconnect_config"] = None

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
        central = context.get("central_conn")
        if central is not None:
            try:
                await central.aclose()
            except Exception as e:  # noqa: BLE001 — shutdown must not raise
                logger.warning("Central: aclose failed during shutdown — {}", e)
        clearpass = context.get("clearpass_client")
        if clearpass is not None:
            try:
                await clearpass.aclose()
            except Exception as e:  # noqa: BLE001 — shutdown must not raise
                logger.warning("ClearPass: aclose failed during shutdown — {}", e)
        mist_client_cleanup: Any = context.get("mist_client")
        if mist_client_cleanup is not None:
            try:
                await mist_client_cleanup.aclose()
            except Exception as e:  # noqa: BLE001 — shutdown must not raise
                logger.warning("Mist: aclose failed during shutdown — {}", e)
        apstra = context.get("apstra_client")
        if apstra is not None:
            await apstra.aclose()
        axis = context.get("axis_client")
        if axis is not None:
            await axis.aclose()
        aos8 = context.get("aos8_client")
        if aos8 is not None:
            try:
                await aos8.aclose()
            except Exception as e:  # noqa: BLE001 — shutdown must not raise
                logger.warning("AOS8: aclose failed during shutdown — {}", e)
        uxi = context.get("uxi_client")
        if uxi is not None:
            try:
                await uxi.aclose()
            except Exception as e:  # noqa: BLE001
                logger.warning("UXI: aclose failed during shutdown — {}", e)
        edgeconnect = context.get("edgeconnect_client")
        if edgeconnect is not None:
            try:
                await edgeconnect.aclose()
            except Exception as e:  # noqa: BLE001
                logger.warning("EdgeConnect: aclose failed during shutdown — {}", e)
        logger.info("Server shutdown complete")


def _mcp_apps_enabled() -> bool:
    """Whether the MCP-Apps providers are enabled (env-gated by ``MCP_APP_ENABLE``).

    A single switch for every MCP-Apps capability — the ``FileUpload`` provider and
    the ``GenerativeUI`` provider — since both emit ``ui://`` MCP-Apps resources that
    only render in MCP-Apps hosts. Off by default.
    """
    import os

    return os.environ.get("MCP_APP_ENABLE", "").strip().lower() in ("1", "true", "yes")


# Prepended to the GenerativeUI tool's own description. Tool descriptions are part
# of the function-calling contract a client uses to PICK a tool — unlike
# INSTRUCTIONS.md, which MCP clients treat as untrusted server content and largely
# ignore (see the project_mcp_memory_arch_finding note). Putting the steer HERE is
# what actually makes the model reach for generate_prefab_ui instead of hand-writing
# HTML for a dashboard request.
_GENERATIVE_UI_GUIDANCE = (
    "USE THIS TOOL FIRST for any request to build, render, draw, show, or visualize "
    "a dashboard, report, chart, graph, table, scorecard, status board, or any "
    "graphical / interactive view of network data (Juniper Mist, Aruba Central + MRT, "
    "HPE GreenLake, ClearPass, Apstra, Axis, AOS 8, UXI). Workflow: gather the data "
    "first (platform read tools / an `execute` block), then pass it here and compose "
    "the view from Prefab components (metric cards, bar/line/area/pie charts, data "
    "tables, badges) with reactive state for in-window filtering. Do NOT hand-write "
    "raw HTML as a text response for visualization requests — render it through this "
    "tool so the client shows a live, interactive widget instead of a static blob.\n\n"
    "DATA CONTRACT (avoids the #1 error): pass the values you gathered as the `data` "
    "argument, which MUST be a dict. Each TOP-LEVEL KEY of that dict becomes a global "
    "variable of that same name inside your `code` — reference those names directly. "
    "Example: data={'devices': [...], 'top_aps': [...]} -> in code use `devices` and "
    "`top_aps`. There is NO variable named `data` in the sandbox; writing `data[...]` "
    "or `data.get(...)` raises `NameError: name 'data' is not defined`. Embed the real "
    "values you collected (do not invent placeholders).\n\n"
    "DATA SHAPE (unwrap before passing): platform reads return an envelope — "
    "`{ok, status, data, message, tool, platform}` — and `<platform>_invoke_tool` "
    "wraps results the same way. Read the inner `data` first (some tools nest a "
    "further `result` / `items`); passing the raw envelope renders bookkeeping keys "
    "instead of your values.\n\n"
    "COMPONENTS (discover in ONE call): `search_prefab_components` with a broad or "
    "empty query returns the whole catalog at once — do NOT fan out many narrow "
    "searches. For network dashboards the common set is: `metric` (KPI cards), "
    "`charts` (bar / line / area / pie), `histogram`, `data_table` / `table`, "
    "`badge` + `dot` (status), `card`, `column` / `row` / `grid` (layout), "
    "`heading` / `text`, `progress` / `ring`, `tabs`, `alert`.\n\n"
    "---\n\n"
)


def create_server(config: ServerConfig) -> FastMCP:
    """Create and configure the FastMCP server with all enabled platform tools."""
    from hpe_networking_mcp.middleware.elicitation import (
        ElicitationMiddleware,
    )
    from hpe_networking_mcp.middleware.null_strip import NullStripMiddleware
    from hpe_networking_mcp.middleware.pii_tokenization import (
        PIITokenizationMiddleware,
    )
    from hpe_networking_mcp.middleware.response_envelope import ResponseEnvelopeMiddleware
    from hpe_networking_mcp.middleware.retry import RetryMiddleware
    from hpe_networking_mcp.middleware.sandbox_error_catch import (
        SandboxErrorCatchMiddleware,
    )
    from hpe_networking_mcp.middleware.unknown_tool_suggest import (
        UnknownToolSuggestMiddleware,
    )
    from hpe_networking_mcp.middleware.validation_catch import ValidationCatchMiddleware
    from hpe_networking_mcp.redaction.token_store import TokenStore

    # The token store is process-scoped (one TokenStore per FastMCP
    # instance, with per-session keymaps inside). It is passed to the
    # middleware so it survives across tool calls within a session.
    token_store = TokenStore(max_entries_per_session=config.pii_max_tokens_per_session)

    # Middleware order (outermost → innermost):
    #   NullStrip           — drop nulls before validation
    #   ValidationCatch     — Pydantic ValidationError → readable string return
    #   SandboxErrorCatch   — code-mode MontyRuntimeError on execute → string return
    #   UnknownToolSuggest  — top-level "Unknown tool" → structured "did you
    #                         mean" candidate list (#489)
    #   PIITokenization     — detokenize inbound args / tokenize outbound results
    #                         (always normalizes MACs even when toggle is off)
    #   Elicitation         — write-tool confirmation gate; user sees real values
    #                         post-detokenization, which is correct (the user is
    #                         the trust boundary holder, not the AI)
    #   Retry               — transient failures retry transparently after elicit
    #   ResponseEnvelope    — v2.5.1.0 prototype (#246): wraps the 4 cross-platform
    #                         tools' raw output in {ok, data, status, message, tool,
    #                         platform}. Innermost so retry's status-code extraction
    #                         + PII tokenization see the envelope shape on the way out.
    mcp = FastMCP(
        name="HPE Networking MCP",
        instructions=_INSTRUCTIONS,
        lifespan=lifespan,
        on_duplicate="replace",
        mask_error_details=True,
        middleware=[
            NullStripMiddleware(),
            ValidationCatchMiddleware(),
            SandboxErrorCatchMiddleware(),
            UnknownToolSuggestMiddleware(),
            PIITokenizationMiddleware(token_store, enabled=config.enable_pii_tokenization),
            ElicitationMiddleware(),
            RetryMiddleware(),
            ResponseEnvelopeMiddleware(),
        ],
    )

    # Stash the token store on the FastMCP instance so future tooling
    # (e.g. an audit/reveal endpoint) can access it without going
    # through the middleware.
    mcp._hpe_token_store = token_store  # type: ignore[attr-defined]

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
    if config.aos8:
        _register_aos8_tools(mcp, config)
    if config.uxi:
        _register_uxi_tools(mcp, config)
    if config.edgeconnect:
        _register_edgeconnect_tools(mcp, config)

    # --- MCP-Apps providers (experimental, env-gated by MCP_APP_ENABLE) ---
    # One switch enables every MCP-Apps capability. Both providers emit `ui://`
    # MCP-Apps resources that render only in MCP-Apps hosts (Claude Desktop /
    # ChatGPT / claude.ai); they're no-op visuals in Claude Code.
    #
    # FileUpload: exposes a `file_manager` drag/pick upload tool (carrying MCP-Apps
    # `ui` render metadata) plus `list_files`. In code mode the CodeMode transform
    # would hide them, so _register_code_mode() re-exposes them top-level via
    # discovery_tools (their `ui` metadata rides through intact). The provider's
    # `read_file` tool is DELIBERATELY removed below (Visibility transform): it
    # returns raw uploaded content to the model, which would defeat the whole point
    # of uploads (device serials/MACs, AOS 8 configs with PSKs and RADIUS/TACACS
    # secrets must never enter the model context). Consuming tools instead read
    # server-side via `provider.on_read` (see utils/uploads.read_uploaded_text).
    #
    # GenerativeUI: exposes `generate_prefab_ui` — the model writes Prefab Python
    # that renders as a live dashboard from data it collected (e.g. AP health across
    # sites) — a `search_prefab_components` discovery tool, and a `ui://` streaming
    # renderer resource. Server-side validation uses Deno (baked into the image).
    if _mcp_apps_enabled():
        import asyncio

        from fastmcp.apps.file_upload import FileUpload
        from fastmcp.apps.generative import GenerativeUI

        _file_upload = FileUpload()
        mcp.add_provider(_file_upload)
        # Keep a handle so tools can read an uploaded file SERVER-SIDE via
        # ``provider.on_read(name, ctx)`` — i.e. without pulling the file
        # through the model context. ``greenlake_bulk_add_devices`` uses this
        # for large CSVs (up to 10k rows). Surfaced on lifespan_context below.
        mcp._hpe_file_upload = _file_upload  # type: ignore[attr-defined]
        # SECURITY: remove the model-visible `read_file` tool. It returns raw
        # uploaded file CONTENT to the LLM — uploads exist precisely so that
        # content (device serials/MACs, AOS 8 configs carrying PSKs and
        # RADIUS/TACACS secrets) never reaches the model. Tools that need the
        # data read it server-side via `provider.on_read`. A Visibility(False)
        # transform both hides it from listing AND makes a direct call fail with
        # "Unknown tool" (verified) — `remove_tool` does not work on
        # provider-registered tools. `list_files` (metadata only) + `file_manager`
        # (upload UI) stay.
        from fastmcp.server.transforms import Visibility

        mcp.add_transform(Visibility(False, names={"read_file"}, components={"tool"}))
        logger.info("MCP Apps: FileUpload registered (MCP_APP_ENABLE=true); read_file removed (server-side reads only)")

        mcp.add_provider(GenerativeUI())
        logger.info("MCP Apps: GenerativeUI provider registered (MCP_APP_ENABLE=true)")

        # Steer dashboard/visualization requests to this tool by prepending
        # networking-specific guidance to its description (preserving the upstream
        # Prefab authoring instructions). get_tool returns the live instance and the
        # change persists to list_tools, so this covers BOTH code and dynamic mode.
        # create_server runs before the event loop, so a one-shot asyncio.run is safe
        # (same justification as the code-mode re-expose below).
        try:
            _gen_tool = asyncio.run(mcp.get_tool("generate_prefab_ui"))
            if _gen_tool is not None:
                _gen_tool.description = _GENERATIVE_UI_GUIDANCE + (_gen_tool.description or "")
                logger.info("Generative UI: generate_prefab_ui description augmented with dashboard guidance")
        except Exception as e:  # pragma: no cover - defensive
            logger.warning("Generative UI: could not augment generate_prefab_ui description: {}", e)

    # --- Cross-platform aggregators ---
    # These are workarounds for dynamic mode's "AI picks one platform and stops"
    # problem. Code mode's premise is that the LLM can compose per-platform tools
    # into cross-platform answers itself via `call_tool` in the sandbox — so we
    # explicitly do NOT register the aggregators in code mode. If code mode
    # can't reliably synthesize cross-platform answers, that's the "keep dynamic
    # as default" signal, not a reason to re-register them here.
    if config.tool_mode != "code" and (config.mist or config.central):
        _register_site_health_check(mcp, config)
        _register_site_rf_check(mcp, config)

    # --- Cross-platform `health` tool (always registered in every mode —
    # reachability info is not aggregation; useful to have callable in the
    # code-mode sandbox too) ---
    from hpe_networking_mcp.platforms.health import register as _register_health

    _register_health(mcp)

    # --- Cross-platform WLAN translation bridge (always registered, every mode).
    # Unlike the legacy aggregators these wrap the canonical translation engine
    # (which can't be imported inside the code-mode sandbox), so they must be
    # reachable from execute() via call_tool — hence unconditional registration. ---
    if config.mist or config.central:
        from hpe_networking_mcp.platforms.translate_wlan import register as _register_translate_wlan

        _register_translate_wlan(mcp)

    # --- Cross-platform CONFIG translation bridge (AOS 8 → Central, every mode).
    # Same rationale as translate_wlan: wraps the canonical engine for the 12
    # non-WLAN config kinds (vlan / role / policy / net_group / AAA chain /
    # gateway_cluster), reachable from the code-mode sandbox via call_tool. ---
    if config.central:
        from hpe_networking_mcp.platforms.translate_config import register as _register_translate_config

        _register_translate_config(mcp)

    # --- Skills (markdown-defined multi-step procedures, always visible) ---
    # In dynamic mode, register via @mcp.tool — they appear at the top level
    # via the standard catalog. In CODE mode (default since v3.0.0.0), we
    # deliberately skip this path and instead pass discovery-tool factories
    # to CodeMode below (see _register_code_mode); CodeMode's transform_tools
    # replaces the visible catalog with [discovery_tools, execute] only,
    # which would otherwise hide @mcp.tool registrations.
    if config.tool_mode != "code":
        from hpe_networking_mcp.skills import register as _register_skills

        _register_skills(mcp)

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
    if not config.enable_aos8_write_tools:
        mcp.add_transform(Visibility(False, tags={"aos8_write", "aos8_write_delete"}, components={"tool"}))
    if not config.enable_uxi_write_tools:
        mcp.add_transform(Visibility(False, tags={"uxi_write", "uxi_write_delete"}, components={"tool"}))
    if not config.enable_greenlake_write_tools:
        mcp.add_transform(Visibility(False, tags={"greenlake_write"}, components={"tool"}))
    if not config.enable_edgeconnect_write_tools:
        mcp.add_transform(
            Visibility(False, tags={"edgeconnect_write", "edgeconnect_write_delete"}, components={"tool"})
        )

    # --- Tool-mode-specific catalog transforms ---
    if config.tool_mode == "dynamic":
        # Dynamic mode: hide the individual registry-managed tools so the
        # exposed surface is just the per-platform meta-tools plus the
        # cross-platform statics (health, site_health_check, site_rf_check,
        # translate_wlan_preview/apply).
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
        # Cross-platform aggregators (site_health_check, site_rf_check) were not
        # registered above in code mode, so they don't leak into Search's catalog.
        # (health + translate_wlan_* ARE registered in every mode — they wrap
        # engines/probes the sandbox can't import, so they must be call_tool-able.)
        _register_code_mode(mcp, config.code_sandbox_max_duration_secs)

    return mcp


# Discovery tool descriptions — keyword-rich so client-side semantic
# tool_search (Claude Desktop / web / IDE / CoWork etc.) surfaces them on
# queries like "list mist sites" / "search central tools". The default
# fastmcp descriptions ("Search for available tools by query") are too
# generic and lose the relevance ranking against other MCP servers'
# more descriptive tools. See issue #302 — Mike Gallagher's
# "Mist intermittent" report 2026-05-12.
# Prepended to every catalog-discovery tool description so "skills first"
# is a tool-layer gate, not an implication an AI can rationalize past.
# See issue #338 — an "RF check" request jumped straight to `search`
# because nothing in `search`'s own description said to check skills first.
_SKILLS_FIRST_GATE = (
    "Call `skills_list` FIRST. If a bundled skill covers the request — "
    "audits, migrations, health / RF / channel-planning checks, change "
    "validation, or any multi-step or cross-platform procedure — then "
    "`skills_load` it and follow that runbook instead of improvising. "
    "Only fall through to this tool when `skills_list` returns no "
    "applicable skill.\n\n"
)

_SEARCH_DESCRIPTION = _SKILLS_FIRST_GATE + (
    "Find or list available HPE networking tools by name, function, or "
    "description across mist, central, aos8, clearpass, apstra, axis, "
    "greenlake, uxi, and edgeconnect platforms. Use this to discover the exact tool name "
    "for any networking task — listing sites, getting devices, searching "
    "events, managing config, checking health, etc. Returns matching tools "
    "ranked by relevance. Prefer this over guessing tool names: each "
    "platform has its own naming convention and discovery is faster than "
    "trial and error."
)

_TAGS_DESCRIPTION = _SKILLS_FIRST_GATE + (
    "Browse the HPE networking tool catalog grouped by category tag — "
    "platform name (mist / central / aos8 / clearpass / apstra / axis / "
    "greenlake / uxi / edgeconnect), read/write classification, or feature area. Use to scope "
    "the tool catalog by category before drilling in with `search` or "
    "`get_schema`. By default returns each tag name with a tool COUNT; pass "
    '`detail="full"` to list the actual tools under each tag.'
)

_GET_SCHEMA_DESCRIPTION = _SKILLS_FIRST_GATE + (
    "Get full parameter schemas, enum values, types, and descriptions for "
    "one or more HPE networking tools (mist, central, aos8, clearpass, "
    "apstra, axis, greenlake, uxi, edgeconnect). Use after `search` or `tags` to confirm a "
    "tool's exact input shape before invoking it. Each schema returned "
    "includes the parameter list, defaults, optional/required markers, "
    "and any nested object or enum types."
)


class _ArgTolerantFunctionTool(FunctionTool):
    """Discovery tool that tolerates extra / misnamed args (issue #488).

    Small local models routinely call e.g.
    ``search(query="sites", platform="central")``. fastmcp's generated
    discovery tools validate incoming arguments against the function
    signature (``type_adapter.validate_python``), so any unknown kwarg raises
    ``Unexpected keyword argument`` and the **entire** call is rejected —
    which dead-ends the discovery entry point and blocks everything
    downstream. The published JSON schema is not the validator, so relaxing
    ``additionalProperties`` would not help.

    This subclass normalizes arguments before validation:
      - a ``platform`` arg is folded into the existing ``tags`` filter
        (platforms are catalog tags), preserving the model's intent; and
      - any remaining key not in the published schema is dropped,
    so the call succeeds instead of being rejected wholesale.
    """

    async def run(self, arguments: dict[str, Any]) -> ToolResult:
        props = (self.parameters or {}).get("properties", {})
        args = dict(arguments or {})
        platform = args.pop("platform", None)
        if platform is not None and "tags" in props:
            # Only list/tuple/set means "multiple platforms". Any other value
            # (str, or a malformed scalar like int/bool) is treated as one —
            # never list() a non-iterable scalar, which would raise TypeError
            # and re-create the very dead-end this fix removes (#488).
            plats = list(platform) if isinstance(platform, (list, tuple, set)) else [platform]
            existing = args.get("tags") or []
            if isinstance(existing, str):
                existing = [existing]
            args["tags"] = list(existing) + [str(p).lower() for p in plats]
        # Drop any unknown keys so validate_python doesn't reject the call.
        args = {k: v for k, v in args.items() if k in props}
        return await super().run(args)


# Published-schema description for the optional `platform` argument (#496).
_PLATFORM_ARG_SCHEMA: dict[str, Any] = {
    "anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}],
    "default": None,
    "description": (
        "Optional platform to scope results to — one name (e.g. 'central') or a "
        "list. One of: mist, central, greenlake, clearpass, apstra, axis, aos8, "
        "uxi, edgeconnect. Folded into the tag filter."
    ),
}


def _advertise_platform_arg(tool: _ArgTolerantFunctionTool) -> None:
    """Surface the tolerated ``platform`` arg in the published input schema (#496).

    ``_ArgTolerantFunctionTool`` already *accepts* a ``platform`` argument and
    folds it into ``tags`` (#488), but a model that introspects the schema has
    no signal that ``platform`` is a first-class way to scope a call — it only
    works for models that pass it blind. Advertising it lets schema-aware
    clients use it deliberately. Only tools that actually have a ``tags`` filter
    can act on ``platform``, so we add it solely where ``tags`` exists (in
    practice: ``search``). Runtime behavior is unchanged — ``run`` validates
    against the function signature, not this schema. Idea from @gaoflow (#494).
    """
    params = tool.parameters
    props = params.get("properties") if isinstance(params, dict) else None
    if props is not None and "tags" in props and "platform" not in props:
        props["platform"] = dict(_PLATFORM_ARG_SCHEMA)


def _make_arg_tolerant(tool: FunctionTool) -> _ArgTolerantFunctionTool:
    """Reconstruct a produced discovery Tool as the arg-tolerant subclass.

    fastmcp's discovery-tool factories always build a plain ``FunctionTool``;
    we copy its validated field values into ``_ArgTolerantFunctionTool`` so the
    argument-normalizing ``run`` override takes effect (issue #488), then
    advertise the optional ``platform`` arg in the published schema (#496).
    """
    tolerant = _ArgTolerantFunctionTool(**{f: getattr(tool, f) for f in type(tool).model_fields})
    _advertise_platform_arg(tolerant)
    return tolerant


# Set during _register_code_mode so the skill-aware `search` tool — which is
# reconstructed via model_fields and therefore can't carry instance state —
# can reach the skill registry at request time (issue #493).
_SEARCH_SKILL_REGISTRY: Any = None


def _render_skill_matches(matches: list) -> str:
    """Render matched skills as an observation block prepended to search results (#493)."""
    lines = ["MATCHING SKILLS (vetted runbooks — load with skills_load before improvising):"]
    for s in matches:
        lines.append(f"- {s.name} — {s.title}  ->  skills_load(name={s.name!r})")
    return "\n".join(lines)


class _SkillAwareSearchTool(_ArgTolerantFunctionTool):
    """`search` that surfaces matching bundled skills as result data (issue #493).

    Skills-first was previously enforced only through untrusted channels — the
    server ``instructions`` blob and prepended description prose, which frontier
    models do not reliably honor. This makes it structural: when the query
    matches a bundled skill, the match list is prepended to the search result
    as an observation the model acts on, not an instruction it must trust.
    Builds on the arg-tolerant ``run`` (#488); inert if no registry is set or
    no skill matches.
    """

    async def run(self, arguments: dict[str, Any]) -> ToolResult:
        from mcp.types import TextContent

        result = await super().run(arguments)
        args = arguments or {}
        query = args.get("query", "")
        tags = args.get("tags")
        detail = args.get("detail", "brief")

        # #527: annotate brief result rows with compact safety markers so a
        # model sees write/delete/confirmation BEFORE selecting a tool. Only
        # the brief format is line-oriented (`- name: desc`); detailed/full are
        # left as-is.
        if detail == "brief":
            result.content = [
                TextContent(type="text", text=_annotate_search_safety(b.text))
                if isinstance(b, TextContent) and b.text
                else b
                for b in result.content
            ]

        # #526: a tags-only call (tags set, query blank) returns "No tools
        # matched" because ranking needs query terms. Guide the model to a
        # usable path instead of a dead end.
        if tags and isinstance(query, str) and not query.strip():
            note = (
                "Tags-only search isn't supported — relevance ranking needs query terms. "
                "Either pass a non-empty `query` (the `tags` filter then narrows it, e.g. "
                'search(query="site", tags=["central"])), or call `tags(detail="full")` to '
                "list every tool under a tag."
            )
            result.content = [TextContent(type="text", text=note), *result.content]
            return result

        registry = _SEARCH_SKILL_REGISTRY
        if registry is None or not isinstance(query, str):
            return result
        matches = registry.match(query)
        if not matches:
            return result
        result.content = [TextContent(type="text", text=_render_skill_matches(matches)), *result.content]
        return result


def _safety_marker(tool_name: str) -> str:
    """Compact safety marker for a tool name, or '' for a safe read / unknown (#527)."""
    from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, tool_safety

    for registry in REGISTRIES.values():
        spec = registry.get(tool_name)
        if spec is None:
            continue
        safety = tool_safety(spec)
        if safety["capability"] == "read" and not safety["requires_confirmation"]:
            return ""  # safe read — keep the row clean (absence == safe)
        bits = [safety["capability"]]
        if safety["requires_confirmation"]:
            bits.append("confirm")
        return f"  [{', '.join(bits)}]"
    return ""  # cross-platform tool / not in any registry — leave untouched


def _annotate_search_safety(text: str) -> str:
    """Append safety markers to brief search rows (#527).

    Brief rows are ``- <name>: <desc>`` or ``- <name>``. Resolve each name in
    the registries and append a marker for write/delete/operational or
    confirmation-gated tools. Rows that don't resolve (headers, cross-platform
    tools) are left untouched; already-marked rows are skipped (idempotent).
    """
    out: list[str] = []
    for line in text.split("\n"):
        if line.startswith("- ") and not line.rstrip().endswith("]"):
            name = line[2:].split(":", 1)[0].strip()
            if name and " " not in name:
                line += _safety_marker(name)
        out.append(line)
    return "\n".join(out)


def _make_skill_aware_search(tool: FunctionTool) -> _SkillAwareSearchTool:
    """Reconstruct the produced `search` tool as the skill-aware subclass (#493),
    preserving the #488 arg-tolerance and #496 platform advertisement."""
    aware = _SkillAwareSearchTool(**{f: getattr(tool, f) for f in type(tool).model_fields})
    _advertise_platform_arg(aware)
    return aware


def _register_code_mode(mcp: FastMCP, max_duration_secs: float = 30.0) -> None:
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
            Search,
        )
        from pydantic_monty import ResourceLimits

        from hpe_networking_mcp.code_sandbox import ClockEnabledMontySandboxProvider
    except ImportError as e:
        logger.error(
            "MCP_TOOL_MODE=code requires fastmcp[code-mode] + pydantic-monty ({}); "
            "falling back to untransformed catalog (every registered tool visible)",
            e,
        )
        return

    # Subclasses that override the description on the produced Tool so
    # client semantic tool_search surfaces our discovery tools on queries
    # like "list mist sites" / "search central tools" (issue #302). The
    # parent classes' __init__ doesn't accept a description argument, so we
    # mutate the returned Tool object before it goes upstream, then
    # reconstruct it as the arg-tolerant subclass (issue #488).

    class _HpeSearch(Search):
        def __call__(self, get_catalog):
            tool = super().__call__(get_catalog)
            tool.description = _SEARCH_DESCRIPTION
            return _make_skill_aware_search(tool)

    class _HpeGetTags(GetTags):
        def __call__(self, get_catalog):
            tool = super().__call__(get_catalog)
            tool.description = _TAGS_DESCRIPTION
            return _make_arg_tolerant(tool)

    class _HpeGetSchemas(GetSchemas):
        def __call__(self, get_catalog):
            tool = super().__call__(get_catalog)
            tool.description = _GET_SCHEMA_DESCRIPTION
            return _make_arg_tolerant(tool)

    limits = ResourceLimits(
        max_duration_secs=max_duration_secs,
        max_memory=128 * 1024 * 1024,
        max_recursion_depth=50,
    )
    # Override the default `execute` description. It must steer the LLM to
    # the ONE dispatch pattern that works for every platform tool:
    # `<platform>_invoke_tool`. The spec-driven Mist tools (~1000 of them)
    # are registered with FastMCP but deliberately not *listed* in the
    # catalog — so CodeMode's sandbox `call_tool`, which resolves names
    # against the listed catalog, raises `Unknown tool` for a direct
    # `call_tool('mist_get_self', ...)`. Hand-curated platform tools
    # (central_/aos8_/etc.) happen to be directly callable, but telling the
    # LLM "names start with mist_/central_/..." over-promises and produces
    # `Unknown tool` failures on Mist (issue #328). The default fastmcp
    # string is even thinner — it doesn't say what `call_tool` reaches at
    # all, which caused the `Unknown tool: search` failures in #208/#302.
    execute_description = (
        "Run Python in a sandbox to compose multiple platform tool calls. "
        "Use `return` to produce output.\n\n"
        "STATELESS: each `execute()` call runs in a FRESH sandbox — variables, "
        "imports, and results from a previous `execute()` block do NOT persist. "
        "Do all the work for one task in a SINGLE block; never reference a "
        "variable (e.g. `org_id`) defined in an earlier call.\n\n"
        "PREREQUISITE — call `skills_list` at the outer surface BEFORE "
        "using `execute`. If a bundled skill covers the request, "
        "`skills_load` it and follow that runbook; only write your own "
        "code block when `skills_list` returns no applicable skill "
        "(issue #338).\n\n"
        "In scope: `await call_tool(name: str, params: dict) -> Any`.\n\n"
        "`call_tool` reaches:\n"
        "  - Any per-platform tool (mist / central / greenlake / clearpass / "
        "apstra / axis / aos8 / uxi / edgeconnect) — discover names with "
        "`search` / `<platform>_list_tools`, then call EITHER directly by name "
        "(e.g. `await call_tool('mist_search_org_devices', {...})`) OR via "
        "`<platform>_invoke_tool(name=<tool>, params=<dict>)`. Both work and "
        "are equivalent; `invoke_tool` is handy when you're dispatching a name "
        "you looked up dynamically.\n"
        "  - `<platform>_list_tools` / `<platform>_get_tool_schema` — "
        "per-platform discovery meta-tools.\n"
        "  - `health` — cross-platform reachability.\n"
        "  - `translate_wlan_preview` / `translate_wlan_apply` — translate a WLAN "
        "between platforms (mist/central/aos8 → central/mist) via the canonical "
        "engine; preview is read-only, apply is target-write-gated + confirmed.\n\n"
        "Discovery from inside execute(): if you don't know a platform's "
        'tool names, call `<platform>_list_tools(filter="...")` (e.g. '
        "`await call_tool('mist_list_tools', {'filter': 'site'})`) to get "
        "a name+params catalog, then "
        "`await call_tool('<platform>_get_tool_schema', {'name': ...})` for "
        "full schemas, then dispatch via "
        "`await call_tool('<platform>_invoke_tool', {'name': ..., 'params': ...})`.\n\n"
        "The TOP-LEVEL discovery tools `tags`, `search`, `get_schema`, "
        "`skills_list`, and `skills_load` are NOT callable from inside "
        "execute() — they live at the outer MCP surface for planning. "
        "Use them BEFORE writing your code block when the client surfaces "
        "them; otherwise use the `<platform>_list_tools` path above.\n\n"
        "Known sandbox limits: `asyncio.gather()` is unavailable — use "
        "sequential `await` calls. The clock IS available: "
        "`datetime.now()`, `datetime.now(datetime.timezone.utc)`, and "
        "`datetime.date.today()` work. But `datetime.utcnow()` does NOT exist "
        "in the sandbox (use `datetime.now(datetime.timezone.utc)`), there is "
        "no `time` module (use `datetime.now().timestamp()`), and file I/O, "
        "`os.environ`, and `subprocess` are blocked. Many search/report tools "
        'also accept a `duration` argument (e.g. "1d") so you often don\'t '
        "need to compute a window at all. Not every stdlib module exists in the sandbox — "
        "e.g. `import collections` (Counter/defaultdict) raises "
        "ModuleNotFoundError. Use builtins instead: a plain `dict` for "
        "counting/grouping, plus `set`, `sorted`, `sum`, and `min`/`max`."
    )

    # Build the skills registry once and hand factories to CodeMode so the
    # skills surface sits at the discovery layer alongside tags/search/etc.
    # (See skills/_engine.py — discovery factories are needed because
    # CodeMode.transform_tools replaces the visible catalog with
    # [discovery_tools, execute] only.)
    from hpe_networking_mcp.skills import (
        SkillRegistry,
        SkillsListDiscoveryTool,
        SkillsLoadDiscoveryTool,
    )

    skill_registry = SkillRegistry.from_directory()
    # Expose the registry to the skill-aware `search` tool so it can surface
    # matching skills as result data at request time (issue #493).
    global _SEARCH_SKILL_REGISTRY
    _SEARCH_SKILL_REGISTRY = skill_registry
    logger.info("Skills: registered {} skill(s) (code mode discovery layer)", len(skill_registry.all()))

    # Heterogeneous discovery-tool factories (the _Hpe* subclasses, the Skills
    # factories, and the file_manager passthrough lambda) — annotate as Any so
    # appending the lambda below doesn't collapse the inferred type to object.
    discovery_tools: list[Any] = [
        _HpeGetTags(default_detail="brief"),
        _HpeSearch(default_detail="brief"),
        _HpeGetSchemas(default_detail="detailed"),
        SkillsListDiscoveryTool(skill_registry),
        SkillsLoadDiscoveryTool(skill_registry),
    ]

    # If the MCP-Apps providers are registered (MCP_APP_ENABLE), re-expose their
    # model-visible tools top-level so CodeMode doesn't bury them behind `execute`:
    #   FileUpload  — file_manager (renders the upload UI; carries MCP-Apps `ui`
    #                 meta) + list_files (metadata only — name/size/type, no
    #                 content). read_file is NOT re-exposed and is removed entirely
    #                 (Visibility transform above): it would return raw uploaded
    #                 content to the model. store_files is app-only (UI-internal)
    #                 and intentionally NOT re-exposed. Consuming tools read uploads
    #                 server-side via provider.on_read (utils/uploads).
    #   GenerativeUI — generate_prefab_ui (carries the streaming-renderer `ui`
    #                 meta) + search_prefab_components.
    # A discovery factory is `(get_catalog) -> Tool`; ours ignores the catalog and
    # returns the already-registered Tool unchanged, so the `ui` render metadata
    # survives the transform. The `ui://` renderer resources are not tools, so the
    # CodeMode tool transform leaves them untouched. create_server() runs before the
    # event loop starts, so a one-shot asyncio.run to fetch each tool is safe.
    if _mcp_apps_enabled():
        import asyncio

        for app_tool_name in (
            "file_manager",
            "list_files",
            "generate_prefab_ui",
            "search_prefab_components",
        ):
            try:
                app_tool = asyncio.run(mcp.get_tool(app_tool_name))
                discovery_tools.append(lambda get_catalog, _t=app_tool: _t)
                logger.info("MCP Apps: {} re-exposed top-level in code mode", app_tool_name)
            except Exception as e:  # pragma: no cover - defensive
                logger.warning("MCP Apps: could not expose {} top-level: {}", app_tool_name, e)

    mcp.add_transform(
        CodeMode(
            # ClockEnabledMontySandboxProvider passes os=OSAccess() so sandbox
            # code can call datetime.now()/date.today() (the stock provider
            # blocks the clock); the FS/env stay fully sandboxed. See
            # code_sandbox.py.
            sandbox_provider=ClockEnabledMontySandboxProvider(limits=limits),
            discovery_tools=discovery_tools,
            execute_description=execute_description,
        )
    )
    logger.info("Code mode enabled — exposed surface: tags + search + get_schema + skills_list + skills_load + execute")


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


def _register_aos8_tools(mcp: FastMCP, config: ServerConfig) -> None:
    """Register all AOS8 platform tools (Phase 2: wires _registry; Phase 3 adds tools/)."""
    from hpe_networking_mcp.platforms.aos8 import register_tools

    count = register_tools(mcp, config)
    logger.info("AOS8: registered {} tools", count)


def _register_uxi_tools(mcp: FastMCP, config: ServerConfig) -> None:
    """Register all UXI platform tools."""
    from hpe_networking_mcp.platforms.uxi import register_tools

    count = register_tools(mcp, config)
    logger.info("UXI: registered {} tools", count)


def _register_edgeconnect_tools(mcp: FastMCP, config: ServerConfig) -> None:
    """Register all EdgeConnect (Orchestrator) platform tools."""
    from hpe_networking_mcp.platforms.edgeconnect import register_tools

    count = register_tools(mcp, config)
    logger.info("EdgeConnect: registered {} tools", count)


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
