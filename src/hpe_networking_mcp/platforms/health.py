"""Cross-platform ``health`` tool and per-platform probe helpers.

The ``health`` tool is the single entry point for platform reachability
reporting across every configured platform. It replaces the per-platform
``apstra_health`` and ``clearpass_test_connection`` tools that existed
in v1.x — both removed in v2.0. Accepts a ``platform`` filter
(``str | list[str] | None``) matching the rule established in v1.0.0.1
(#146): omit for all, pass one name for one, pass a list for several.

The same ``_probe_<platform>()`` helpers are called by
``server.py:lifespan()`` at startup so there's a single source of truth
for "is this platform reachable" — no divergence between what startup
logs say and what the tool reports.
"""

from __future__ import annotations

import time
from typing import Any

from fastmcp import Context, FastMCP
from loguru import logger
from mcp.types import ToolAnnotations

_PROBE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)

_ALL_PLATFORMS: tuple[str, ...] = ("mist", "central", "greenlake", "clearpass", "apstra", "axis", "aos8")


def _normalize_platform_filter(
    value: str | list[str] | None,
    enabled: list[str],
) -> list[str]:
    """Resolve the ``platform`` argument to a list of platform names to probe.

    - ``None`` -> every enabled platform
    - ``"apstra"`` -> ``["apstra"]``
    - ``["apstra", "clearpass"]`` -> the list as-is

    Unknown names are dropped with a warning; the probe dict will simply
    omit them. Platforms that are not configured are skipped silently
    (they appear in the result dict as ``unavailable``).
    """
    if value is None:
        return list(enabled)
    candidates = [value] if isinstance(value, str) else [str(v) for v in value]

    wanted: list[str] = []
    for name in candidates:
        name = name.strip().lower()
        if name in _ALL_PLATFORMS:
            wanted.append(name)
        else:
            logger.warning("health(platform={!r}) — unknown platform name, skipping", name)
    return wanted


# ---------------------------------------------------------------------------
# Per-platform probes
#
# Each probe returns a dict with at minimum: status ("ok"/"degraded"/"unavailable")
# plus a message string. Additional keys may carry platform-specific detail.
# ---------------------------------------------------------------------------


async def _probe_mist(ctx: Context) -> dict[str, Any]:
    import mistapi

    session = ctx.lifespan_context.get("mist_session")
    if session is None:
        return {"status": "unavailable", "message": "Mist is not configured or failed to initialize"}
    try:
        resp = mistapi.api.v1.self.self.getSelf(session)
        if resp.status_code == 200 and resp.data:
            privileges = resp.data.get("privileges", [])
            org_count = sum(1 for p in privileges if p.get("scope") == "org")
            return {"status": "ok", "message": "Mist API session active", "org_count": org_count}
        return {
            "status": "degraded",
            "message": f"Unexpected response from Mist self endpoint (HTTP {resp.status_code})",
        }
    except Exception as e:
        return {"status": "degraded", "message": f"Mist probe failed: {e}"}


async def _probe_central(ctx: Context) -> dict[str, Any]:
    conn = ctx.lifespan_context.get("central_conn")
    if conn is None:
        return {"status": "unavailable", "message": "Central is not configured or failed to initialize"}
    try:
        resp = conn.command(
            "GET",
            "network-monitoring/v1/sites-health",
            api_params={"limit": 1},
        )
        code = resp.get("code", 0)
        if 200 <= code < 300:
            return {"status": "ok", "message": "Central REST API reachable", "http_status": code}
        return {
            "status": "degraded",
            "message": f"Central verification returned HTTP {code}",
            "body": resp.get("msg", {}),
        }
    except Exception as e:
        return {"status": "degraded", "message": f"Central probe failed: {e}"}


async def _probe_greenlake(ctx: Context) -> dict[str, Any]:
    tm = ctx.lifespan_context.get("greenlake_token_manager")
    if tm is None:
        return {"status": "unavailable", "message": "GreenLake is not configured or failed to initialize"}
    try:
        token = tm.get_raw_token() if hasattr(tm, "get_raw_token") else None
        if not token and hasattr(tm, "get_auth_headers"):
            # Force a refresh by asking for headers, then re-read the token
            tm.get_auth_headers()
            token = tm.get_raw_token() if hasattr(tm, "get_raw_token") else None
        if token:
            return {"status": "ok", "message": "GreenLake access token available"}
        return {"status": "degraded", "message": "GreenLake token manager returned empty token"}
    except Exception as e:
        return {"status": "degraded", "message": f"GreenLake probe failed: {e}"}


async def _probe_clearpass(ctx: Context) -> dict[str, Any]:
    tm = ctx.lifespan_context.get("clearpass_token_manager")
    if tm is None:
        return {"status": "unavailable", "message": "ClearPass is not configured or failed to initialize"}
    try:
        token = tm.get_token()
        if token:
            return {"status": "ok", "message": "ClearPass OAuth2 token active"}
        return {"status": "degraded", "message": "ClearPass token manager returned empty token"}
    except Exception as e:
        return {"status": "degraded", "message": f"ClearPass probe failed: {e}"}


async def _probe_apstra(ctx: Context) -> dict[str, Any]:
    client = ctx.lifespan_context.get("apstra_client")
    if client is None:
        return {"status": "unavailable", "message": "Apstra is not configured or failed to initialize"}
    try:
        await client.health_check()
        return {"status": "ok", "message": "Apstra API reachable", "server": client.server}
    except Exception as e:
        return {"status": "degraded", "message": f"Apstra probe failed: {e}"}


async def _probe_axis(ctx: Context) -> dict[str, Any]:
    client = ctx.lifespan_context.get("axis_client")
    if client is None:
        return {"status": "unavailable", "message": "Axis is not configured or failed to initialize"}
    try:
        await client.health_check()
    except Exception as e:
        return {"status": "degraded", "message": f"Axis probe failed: {e}"}

    days = client.token_expires_in_days
    result: dict[str, Any] = {"status": "ok", "message": "Axis API reachable", "base_url": client.base_url}
    if days is None:
        return result
    if days <= 0:
        return {
            "status": "degraded",
            "message": "Axis API token has expired — regenerate at Settings → Admin API",
            "base_url": client.base_url,
            "token_expires_in_days": days,
        }
    if days <= 30:
        return {
            "status": "degraded",
            "message": f"Axis token expires in {days} day(s) — regenerate at Settings → Admin API before it lapses",
            "base_url": client.base_url,
            "token_expires_in_days": days,
        }
    result["token_expires_in_days"] = days
    return result


async def _probe_aos8(ctx: Context) -> dict[str, Any]:
    """Probe the AOS8 / Mobility Conductor platform.

    Returns a status dict with hostname + version on success, degraded on
    failure, unavailable when the platform is not configured.
    """
    client = ctx.lifespan_context.get("aos8_client")
    if client is None:
        return {
            "status": "unavailable",
            "message": "AOS8 is not configured or failed to initialize",
        }
    try:
        info = await client.health_check()
        # Keep the session token alive after the probe. The startup probe
        # session is reused by the first real tool call, avoiding an immediate
        # re-login that can fail on some AOS8 controllers. The 401-retry in
        # AOS8Client.request() handles natural session expiry (900s idle
        # timeout) transparently.
        return {
            "status": "ok",
            "message": "AOS8 API reachable",
            "host": client.server,
            "hostname": info.get("hostname"),
            "version": info.get("version"),
        }
    except Exception as e:  # noqa: BLE001 — health probe must not raise
        return {"status": "degraded", "message": f"AOS8 probe failed: {e}"}


_PROBES = {
    "mist": _probe_mist,
    "central": _probe_central,
    "greenlake": _probe_greenlake,
    "clearpass": _probe_clearpass,
    "apstra": _probe_apstra,
    "axis": _probe_axis,
    "aos8": _probe_aos8,
}


async def run_probes(ctx: Any, platforms: list[str]) -> dict[str, dict[str, Any]]:
    """Run each requested platform's probe and collect results.

    Exposed separately from the ``health`` tool so ``server.py:lifespan``
    can reuse the same probe logic at startup (via a shim wrapper that
    exposes the in-progress lifespan dict as ``lifespan_context``). The
    wider ``Any`` type accommodates both a live ``fastmcp.Context`` and
    the startup shim without pulling runtime dependencies into the
    lifespan's type surface.
    """
    results: dict[str, dict[str, Any]] = {}
    for name in platforms:
        probe = _PROBES.get(name)
        if probe is None:
            continue
        try:
            results[name] = await probe(ctx)
        except Exception as e:  # pragma: no cover — defensive; individual probes already catch
            logger.warning("health probe for {} raised unexpectedly — {}", name, e)
            results[name] = {"status": "degraded", "message": f"probe raised: {e}"}
    return results


def _overall_status(results: dict[str, dict[str, Any]]) -> str:
    """Summarize per-platform statuses into a single top-level value.

    - ``ok`` if every probe returned ``ok``.
    - ``degraded`` if at least one probe reports ``degraded`` or ``unavailable``.
    - ``ok`` (trivially) for an empty result set.
    """
    if not results:
        return "ok"
    values = {r.get("status", "unknown") for r in results.values()}
    if values <= {"ok"}:
        return "ok"
    return "degraded"


def register(mcp: FastMCP) -> None:
    """Register the cross-platform ``health`` tool on the FastMCP server."""

    @mcp.tool(
        name="health",
        description=(
            "Report health of enabled HPE networking platforms in a single call. "
            "Accepts an optional platform filter: omit for every enabled platform, "
            "pass one name as a string (e.g. 'apstra'), or pass a list "
            "(['apstra', 'clearpass']). This is the recommended entry point for "
            "platform-reachability checks; the v1.x-era apstra_health and "
            "clearpass_test_connection tools were removed in v2.0 in favor of "
            "this cross-platform tool."
        ),
        annotations=_PROBE_ANNOTATIONS,
    )
    async def health(
        ctx: Context,
        platform: str | list[str] | None = None,
    ) -> dict[str, Any]:
        config = ctx.lifespan_context.get("config")
        enabled = config.enabled_platforms if config is not None else list(_ALL_PLATFORMS)
        wanted = _normalize_platform_filter(platform, enabled)
        results = await run_probes(ctx, wanted)
        return {
            "status": _overall_status(results),
            "service": "hpe-networking-mcp",
            "timestamp": time.time(),
            "platforms": results,
        }

    logger.info("Cross-platform: registered health tool")
