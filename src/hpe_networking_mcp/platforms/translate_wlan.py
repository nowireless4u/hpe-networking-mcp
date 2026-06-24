"""Cross-platform WLAN translation bridge tools.

Exposes the canonical translation engine (``hpe_networking_mcp.translations``) to
AI clients. The engine can't be imported inside the code-mode ``execute()``
sandbox, so these tools are the bridge — same rationale as
``central_translation_preview`` for the legacy JSON engine.

* ``translate_wlan_preview`` — read-only: fetch a source WLAN + context, run the
  engine planner, return the ordered target calls (PII-scrubbed) for review.
* ``translate_wlan_apply`` — execute the plan against the target platform. Gated:
  it checks the TARGET platform's ``ENABLE_*_WRITE_TOOLS`` flag at runtime and
  fires the universal elicitation confirmation before writing.

Self-contained: given ``(source_platform, target_platform, ssid)`` the tools
fetch everything the engine needs server-side (reusing the engine's own context
resolvers), so the caller never has to assemble the heavy context. ``source_override``
/ ``context_override`` allow bypassing the fetch (tests, or an AOS 8 source whose
joined ``virtual_ap`` + profile lists the caller supplies).
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.middleware.elicitation import confirm_gated_invoke
from hpe_networking_mcp.platforms._common.tool_registry import _GATE_CONFIG_ATTR
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.translations import orchestrator
from hpe_networking_mcp.utils.logging import logger

_REDACT = "***REDACTED***"
_SOURCES = ("mist", "central", "aos8")
_TARGETS = ("central", "mist")


# --------------------------------------------------------------------------- #
# context fetching
# --------------------------------------------------------------------------- #
async def _fetch_mist_source(ctx: Context, ssid: str) -> tuple[dict, dict]:
    client = ctx.lifespan_context.get("mist_client")
    org_id = ctx.lifespan_context.get("mist_org_id")
    if not client or not org_id:
        raise ToolError({"status_code": 500, "message": "Mist client/org not available"})
    wlans = (await client.get(f"/api/v1/orgs/{path_seg(org_id)}/wlans")).json()
    wlan = next((w for w in wlans if w.get("ssid") == ssid), None) if isinstance(wlans, list) else None
    if not wlan:
        raise ToolError({"status_code": 404, "message": f"Mist WLAN with SSID {ssid!r} not found"})
    template = None
    tid = wlan.get("template_id")
    if tid:
        r = await client.get(f"/api/v1/orgs/{path_seg(org_id)}/templates/{path_seg(tid)}")
        if r.status_code < 300:
            template = r.json()
    reader_ctx = {
        "template": template,
        "site_id_to_name": await _mist_id_to_name(client, org_id, "sites"),
        "sitegroup_id_to_name": await _mist_id_to_name(client, org_id, "sitegroups"),
        "deviceprofile_id_to_name": await _mist_id_to_name(client, org_id, "deviceprofiles"),
    }
    return wlan, reader_ctx


async def _mist_id_to_name(client: Any, org_id: str, kind: str) -> dict[str, str]:
    rows = (await client.get(f"/api/v1/orgs/{path_seg(org_id)}/{path_seg(kind)}")).json()
    return {r["id"]: r.get("name", "") for r in rows if isinstance(r, dict) and r.get("id")}


async def _fetch_central_source(ctx: Context, ssid: str) -> tuple[dict, dict]:
    conn = ctx.lifespan_context.get("central_conn")
    if not conn:
        raise ToolError({"status_code": 500, "message": "Central connection not available"})

    async def _list(path: str, key: str) -> list[dict]:
        m = (await conn.command("GET", f"network-config/v1alpha1/{path_seg(path)}"))["msg"]
        return m.get(key, []) if isinstance(m, dict) else []

    w = (await conn.command("GET", f"network-config/v1alpha1/wlan-ssids/{path_seg(ssid)}"))["msg"]
    if not isinstance(w, dict) or not w:
        raise ToolError({"status_code": 404, "message": f"Central WLAN {ssid!r} not found"})
    reader_ctx = {
        "server_groups": await _list("server-groups", "server-group"),
        "auth_servers": await _list("auth-servers", "auth-server"),
        "aliases": await _list("aliases", "alias"),
        "assignments": await _list("config-assignments", "config-assignment"),
    }
    return w, reader_ctx


async def _central_writer_ctx(ctx: Context) -> dict:
    conn = ctx.lifespan_context.get("central_conn")
    if not conn:
        raise ToolError({"status_code": 500, "message": "Central connection not available"})
    return await orchestrator.resolve_central_wlan_scopes(conn)


async def _mist_writer_ctx(ctx: Context) -> dict:
    client = ctx.lifespan_context.get("mist_client")
    org_id = ctx.lifespan_context.get("mist_org_id")
    if not client or not org_id:
        raise ToolError({"status_code": 500, "message": "Mist client/org not available"})

    def _invert(m: dict[str, str]) -> dict[str, str]:
        return {v: k for k, v in m.items() if v}

    return {
        "org_id": org_id,
        "site_name_to_id": _invert(await _mist_id_to_name(client, org_id, "sites")),
        "sitegroup_name_to_id": _invert(await _mist_id_to_name(client, org_id, "sitegroups")),
        "deviceprofile_name_to_id": _invert(await _mist_id_to_name(client, org_id, "deviceprofiles")),
    }


async def _build_plan(
    ctx: Context,
    source_platform: str,
    target_platform: str,
    ssid: str,
    *,
    target_mode: str,
    gateway_clusters: list[str] | None,
    gateway_cluster_list: list[dict] | None = None,
    source_override: dict | None,
    context_override: dict | None,
) -> orchestrator.TranslationPlan:
    if source_platform not in _SOURCES:
        raise ToolError({"status_code": 400, "message": f"Unknown source_platform {source_platform!r}"})
    if target_platform not in _TARGETS:
        raise ToolError({"status_code": 400, "message": f"Unknown target_platform {target_platform!r}"})

    co = context_override or {}

    # --- source object + reader context ---
    if source_override is not None:
        source_obj: dict = source_override
        reader_ctx: dict = dict(co.get("reader_ctx") or {})
    elif source_platform == "mist":
        source_obj, reader_ctx = await _fetch_mist_source(ctx, ssid)
    elif source_platform == "central":
        source_obj, reader_ctx = await _fetch_central_source(ctx, ssid)
    else:  # aos8 — by-SSID auto-fetch isn't a clean primitive (SSID lives in ssid_prof)
        raise ToolError(
            {
                "status_code": 400,
                "message": "aos8 source requires source_override (the virtual_ap) + "
                "context_override.reader_ctx (ssid_profiles/aaa_profiles/server_groups/auth_servers)",
            }
        )
    if source_platform == "aos8":
        reader_ctx.setdefault("target_mode", target_mode)
        if gateway_clusters:
            reader_ctx.setdefault("gateway_clusters", gateway_clusters)

    # --- writer context ---
    writer_ctx = co.get("writer_ctx")
    if writer_ctx is None:
        writer_ctx = await (_central_writer_ctx(ctx) if target_platform == "central" else _mist_writer_ctx(ctx))

    # Central overlay (tunneled/hybrid/dual) binds to gateway cluster(s) via the
    # resolved gw-cluster-list. Those entries (cluster-type/scope/tunnel-type) are
    # operator/topology decisions, so the caller supplies them as a public param
    # rather than the tool guessing — explicit param wins over any context_override.
    if target_platform == "central" and gateway_cluster_list is not None:
        writer_ctx = {**(writer_ctx or {}), "gateway_cluster_list": gateway_cluster_list}

    return orchestrator.plan(
        source_platform, target_platform, orchestrator.WLAN, source_obj, reader_ctx=reader_ctx, writer_ctx=writer_ctx
    )


# --------------------------------------------------------------------------- #
# PII scrubbing (preview output only — never the plan used by apply)
# --------------------------------------------------------------------------- #
def _scrub_canonical(canon: Any) -> dict:
    """PII-safe dict of the canonical WLAN (PSK + RADIUS/CoA secrets redacted)."""
    d = canon.model_dump()
    sec = d.get("security") or {}
    if sec.get("psk"):
        sec["psk"] = _REDACT
    rad = sec.get("radius") or {}
    for key in ("auth_servers", "acct_servers"):
        for s in rad.get(key) or []:
            if s.get("secret"):
                s["secret"] = _REDACT
    for c in rad.get("coa") or []:
        if c.get("secret"):
            c["secret"] = _REDACT
    return d


def _preview_calls(calls: list[dict]) -> list[dict]:
    """Call descriptors without bodies (bodies carry plaintext secrets)."""
    return [
        {
            "method": c["method"],
            "path": c["path"],
            "purpose": c.get("purpose"),
            "depends_on": c.get("depends_on"),
            "unresolved": c.get("unresolved") or c.get("unresolved_clusters"),
        }
        for c in calls
    ]


# --------------------------------------------------------------------------- #
# command adapters for orchestrator.execute()
# --------------------------------------------------------------------------- #
def _mist_command(client: Any):
    async def cmd(method: str, path: str, api_params: dict | None = None, api_data: Any = None) -> dict:
        kwargs: dict[str, Any] = {}
        if api_params:
            kwargs["params"] = {k: v for k, v in api_params.items() if v is not None}
        if api_data is not None and method.upper() not in ("GET", "DELETE"):
            kwargs["json"] = api_data
        resp = await client.request(method, path, **kwargs)
        body = resp.json() if resp.content else {}
        return {"code": resp.status_code, "msg": body, "id": body.get("id") if isinstance(body, dict) else None}

    return cmd


_PREVIEW_ANN = {"title": "Translate WLAN (preview)", "readOnlyHint": True, "openWorldHint": True}
_APPLY_ANN = {
    "title": "Translate WLAN (apply)",
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": False,
    "openWorldHint": True,
}


async def _preview_impl(
    ctx: Context,
    source_platform: str,
    target_platform: str,
    ssid: str,
    *,
    target_mode: str,
    gateway_clusters: list[str] | None,
    gateway_cluster_list: list[dict] | None = None,
    source_override: dict | None,
    context_override: dict | None,
) -> dict[str, Any]:
    plan = await _build_plan(
        ctx,
        source_platform,
        target_platform,
        ssid,
        target_mode=target_mode,
        gateway_clusters=gateway_clusters,
        gateway_cluster_list=gateway_cluster_list,
        source_override=source_override,
        context_override=context_override,
    )
    return {
        "supported": orchestrator.supported(),
        "canonical": _scrub_canonical(plan.canonical),
        "calls": _preview_calls(plan.calls),
        "unresolved": plan.unresolved,
        "preview": plan.preview(),
    }


async def _apply_impl(
    ctx: Context,
    source_platform: str,
    target_platform: str,
    ssid: str,
    *,
    target_mode: str,
    gateway_clusters: list[str] | None,
    gateway_cluster_list: list[dict] | None = None,
    source_override: dict | None,
    context_override: dict | None,
    confirmed: bool,
) -> dict[str, Any]:
    # 1) runtime write-gate on the TARGET platform (not a static tag — the target
    #    varies per call, so a tag would hide the tool for the wrong flag).
    attr = _GATE_CONFIG_ATTR.get(target_platform)
    config = ctx.lifespan_context.get("config")
    if attr and not getattr(config, attr, False):
        raise ToolError(
            {
                "status_code": 403,
                "message": f"Writes to {target_platform} are disabled. Set {attr.upper()}=true to apply.",
            }
        )

    plan = await _build_plan(
        ctx,
        source_platform,
        target_platform,
        ssid,
        target_mode=target_mode,
        gateway_clusters=gateway_clusters,
        gateway_cluster_list=gateway_cluster_list,
        source_override=source_override,
        context_override=context_override,
    )

    # 2) elicitation confirmation (same chokepoint the platform invokers use)
    gate = await confirm_gated_invoke(
        ctx,
        f"Apply WLAN '{ssid}' translation {source_platform}→{target_platform} "
        f"({len(plan.calls)} write call(s) to {target_platform})",
        {"ssid": ssid, "source_platform": source_platform, "target_platform": target_platform, "confirmed": confirmed},
    )
    if gate is not None:
        return gate

    # 3) execute against the target
    if target_platform == "central":
        conn = ctx.lifespan_context.get("central_conn")
        if not conn:
            raise ToolError({"status_code": 500, "message": "Central connection not available"})
        command = conn.command
    else:
        client = ctx.lifespan_context.get("mist_client")
        if not client:
            raise ToolError({"status_code": 500, "message": "Mist client not available"})
        command = _mist_command(client)

    results = await orchestrator.execute(command, plan)
    return {"results": results, "unresolved": plan.unresolved, "preview": plan.preview()}


def register(mcp: FastMCP) -> None:
    """Register the cross-platform WLAN translation bridge tools."""

    @mcp.tool(name="translate_wlan_preview", annotations=_PREVIEW_ANN)
    async def translate_wlan_preview(
        ctx: Context,
        source_platform: str,
        target_platform: str,
        ssid: str,
        target_mode: str = "bridged",
        gateway_clusters: list[str] | None = None,
        gateway_cluster_list: list[dict] | None = None,
        source_override: dict | None = None,
        context_override: dict | None = None,
    ) -> dict[str, Any]:
        """Preview the ordered target calls to mirror a WLAN from one platform to
        another, via the canonical translation engine. Read-only — makes no writes.

        Args:
            source_platform: where the WLAN lives now — 'mist' | 'central' | 'aos8'
                (aos8 requires source_override + context_override).
            target_platform: where to mirror it — 'central' | 'mist'.
            ssid: the source SSID to translate.
            target_mode: AOS8 forward mode — bridged | tunneled | hybrid | bridged_and_tunneled.
            gateway_clusters: neutral cluster NAMES (AOS8 source hint only).
            gateway_cluster_list: resolved Central overlay entries for tunneled/hybrid/
                dual WLANs — ``[{cluster, cluster-type, cluster-scope-id,
                cluster-redundancy-type, tunnel-type}]``. These are topology decisions,
                so the caller/skill supplies them; without them an overlay WLAN's
                cluster binding is reported in ``unresolved`` and apply will block.
            source_override / context_override: bypass the live fetch (tests / AOS8).

        Returns:
            {supported, canonical (secrets redacted), calls (bodies omitted),
            unresolved, preview}.
        """
        return await _preview_impl(
            ctx,
            source_platform,
            target_platform,
            ssid,
            target_mode=target_mode,
            gateway_clusters=gateway_clusters,
            gateway_cluster_list=gateway_cluster_list,
            source_override=source_override,
            context_override=context_override,
        )

    @mcp.tool(name="translate_wlan_apply", annotations=_APPLY_ANN)
    async def translate_wlan_apply(
        ctx: Context,
        source_platform: str,
        target_platform: str,
        ssid: str,
        target_mode: str = "bridged",
        gateway_clusters: list[str] | None = None,
        gateway_cluster_list: list[dict] | None = None,
        source_override: dict | None = None,
        context_override: dict | None = None,
        confirmed: bool = False,
    ) -> dict[str, Any]:
        """Translate a WLAN and EXECUTE the result against the target platform.

        Gated: requires the target platform's ENABLE_*_WRITE_TOOLS flag, and fires
        the universal confirmation prompt before writing. Idempotent for Central
        (ensure-or-create); Mist creates are not idempotent (re-run makes duplicates).

        Same args as ``translate_wlan_preview`` plus ``confirmed`` (the popup-less
        fallback honored only when the client can't present an elicitation prompt).
        For tunneled/hybrid/dual WLANs pass ``gateway_cluster_list`` or the apply
        will block on the unresolved cluster binding.
        """
        return await _apply_impl(
            ctx,
            source_platform,
            target_platform,
            ssid,
            target_mode=target_mode,
            gateway_clusters=gateway_clusters,
            gateway_cluster_list=gateway_cluster_list,
            source_override=source_override,
            context_override=context_override,
            confirmed=confirmed,
        )

    logger.info("Cross-platform: registered translate_wlan_preview + translate_wlan_apply tools")
