"""Cross-platform CONFIG translation bridge tools (AOS 8 → Central).

Exposes the canonical translation engine for the 12 non-WLAN config kinds —
``vlan_id`` / ``named_vlan`` / ``net_group`` / ``role`` / ``policy`` / the AAA
chain (``auth_server`` / ``server_group`` / ``dot1x_auth`` / ``mac_auth`` /
``captive_portal`` / ``aaa_profile``) / ``gateway_cluster``. Same rationale as
``translate_wlan``: the engine can't be imported inside the code-mode sandbox, so
these tools bridge it.

* ``translate_config_preview`` — read-only: run the planner over one AOS 8 source
  record and return the ordered Central calls (PII-scrubbed bodies kept, so the
  operator reviews the real wire payload — only ``auth_server`` carries a secret).
* ``translate_config_apply`` — execute the plan against Central. Gated on
  ``ENABLE_CENTRAL_WRITE_TOOLS`` + the universal elicitation confirmation. Secret-
  bearing kinds (``auth_server``) are blocked until AOS 8 secret tokenization
  ships — their bodies carry cleartext shared secrets.

Unlike ``translate_wlan`` there is no by-name live fetch: config kinds take the
source record (and any kind-specific ``extra_ctx``) directly from the caller — the
migration skill already collected them in Stage 1.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.middleware.elicitation import confirm_gated_invoke
from hpe_networking_mcp.platforms._common.tool_registry import _GATE_CONFIG_ATTR
from hpe_networking_mcp.translations import orchestrator
from hpe_networking_mcp.utils.logging import logger

_REDACT = "***REDACTED***"
_SOURCES = ("aos8",)
_TARGETS = ("central",)
# Keys whose values are secrets — redacted in any previewed canonical dump.
_SECRET_KEYS = frozenset({"plaintext-value", "psk", "secret", "shared-secret"})
# Kinds whose Central body carries a cleartext secret — apply is blocked until the
# PII tokenization layer extends to AOS 8 auth-server secrets.
_PII_BLOCKED_KINDS = frozenset({"auth_server"})


def _valid_kinds() -> set[str]:
    """Config kinds with both an aos8 reader and a central writer registered."""
    sup = orchestrator.supported()
    readers = {r.split(":", 1)[1] for r in sup["readers"] if r.startswith("aos8:")}
    writers = {w.split(":", 1)[1] for w in sup["writers"] if w.startswith("central:")}
    return (readers & writers) - {orchestrator.WLAN}


def _scrub(value: Any) -> Any:
    """Recursively redact secret-valued keys in a canonical/body dump."""
    if isinstance(value, dict):
        return {k: (_REDACT if (k in _SECRET_KEYS and v) else _scrub(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_scrub(v) for v in value]
    return value


def _preview_calls(calls: list[dict]) -> list[dict]:
    """Call descriptors with PII-scrubbed bodies.

    Unlike ``translate_wlan`` (whose every body can carry a PSK, so it omits
    bodies wholesale), config bodies are secret-free except ``auth_server`` — and
    ``_scrub`` redacts that — so the migration preview keeps the actual Central
    POST bodies (operators review the real wire payload), with secrets masked.
    """
    return [
        {
            "method": c["method"],
            "path": c["path"],
            "query": c.get("query") or None,
            "body": _scrub(c.get("body")),
            "purpose": c.get("purpose"),
            "depends_on": c.get("depends_on"),
            "unresolved": c.get("unresolved"),
        }
        for c in calls
    ]


def _body_has_secret(value: Any) -> bool:
    """True if any nested key in ``value`` is a secret key with a truthy value."""
    if isinstance(value, dict):
        return any((k in _SECRET_KEYS and v) or _body_has_secret(v) for k, v in value.items())
    if isinstance(value, list):
        return any(_body_has_secret(v) for v in value)
    return False


def _build_plan(
    ctx: Context,
    source_platform: str,
    target_platform: str,
    kind: str,
    source_record: dict,
    *,
    scope_id: str | None,
    device_functions: list[str] | None,
    extra_ctx: dict | None,
) -> orchestrator.TranslationPlan:
    if source_platform not in _SOURCES:
        raise ToolError({"status_code": 400, "message": f"Unknown source_platform {source_platform!r} (expected aos8)"})
    if target_platform not in _TARGETS:
        raise ToolError(
            {"status_code": 400, "message": f"Unknown target_platform {target_platform!r} (expected central)"}
        )
    valid = _valid_kinds()
    if kind not in valid:
        raise ToolError({"status_code": 400, "message": f"Unknown config kind {kind!r}; available: {sorted(valid)}"})
    if not isinstance(source_record, dict) or not source_record:
        raise ToolError({"status_code": 400, "message": "source_record must be a non-empty object"})

    reader_ctx = dict(extra_ctx or {})
    writer_ctx: dict[str, Any] = {"scope_id": scope_id}
    if device_functions:
        writer_ctx["device_functions"] = device_functions

    try:
        return orchestrator.plan(
            source_platform, target_platform, kind, source_record, reader_ctx=reader_ctx, writer_ctx=writer_ctx
        )
    except TypeError as e:
        # An unexpected extra_ctx key the kind's reader doesn't accept.
        raise ToolError({"status_code": 400, "message": f"Invalid extra_ctx for kind {kind!r}: {e}"}) from e
    except ValueError as e:
        # Reader validation (e.g. policy needs role_records, gateway_cluster needs cluster_strategy).
        raise ToolError({"status_code": 400, "message": str(e)}) from e


_PREVIEW_ANN = {"title": "Translate config (preview)", "readOnlyHint": True, "openWorldHint": True}
_APPLY_ANN = {
    "title": "Translate config (apply)",
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
}


async def _preview_impl(
    ctx: Context,
    source_platform: str,
    target_platform: str,
    kind: str,
    source_record: dict,
    *,
    scope_id: str | None,
    device_functions: list[str] | None,
    extra_ctx: dict | None,
) -> dict[str, Any]:
    plan = _build_plan(
        ctx,
        source_platform,
        target_platform,
        kind,
        source_record,
        scope_id=scope_id,
        device_functions=device_functions,
        extra_ctx=extra_ctx,
    )
    canonical = plan.canonical.model_dump() if hasattr(plan.canonical, "model_dump") else plan.canonical
    return {
        "supported": orchestrator.supported(),
        "canonical": _scrub(canonical),
        "calls": _preview_calls(plan.calls),
        "unresolved": plan.unresolved,
        "preview": plan.preview(),
    }


async def _apply_impl(
    ctx: Context,
    source_platform: str,
    target_platform: str,
    kind: str,
    source_record: dict,
    *,
    scope_id: str | None,
    device_functions: list[str] | None,
    extra_ctx: dict | None,
    confirmed: bool,
) -> dict[str, Any]:
    # 1) runtime write-gate on the TARGET platform.
    attr = _GATE_CONFIG_ATTR.get(target_platform)
    config = ctx.lifespan_context.get("config")
    if attr and not getattr(config, attr, False):
        raise ToolError(
            {
                "status_code": 403,
                "message": f"Writes to {target_platform} are disabled. Set {attr.upper()}=true to apply.",
            }
        )

    plan = _build_plan(
        ctx,
        source_platform,
        target_platform,
        kind,
        source_record,
        scope_id=scope_id,
        device_functions=device_functions,
        extra_ctx=extra_ctx,
    )

    # 2) PII guard — block any plan whose bodies carry a cleartext secret until the
    #    redaction layer extends to AOS 8 secrets (auth_server today).
    if kind in _PII_BLOCKED_KINDS or any(_body_has_secret(c.get("body")) for c in plan.calls):
        raise ToolError(
            {
                "status_code": 403,
                "message": (
                    f"Apply blocked for kind {kind!r}: the Central body carries a cleartext shared secret. "
                    "PII tokenization for AOS 8 auth-server secrets is required before this can be written. "
                    "Use translate_config_preview to review, and create the auth-server manually for now."
                ),
            }
        )

    # 3) elicitation confirmation.
    obj_name = (
        source_record.get("name")
        or source_record.get("accname")
        or source_record.get("profile-name")
        or source_record.get("dstname")
        or source_record.get("rname")
        or "?"
    )
    gate = await confirm_gated_invoke(
        ctx,
        f"Apply {kind} '{obj_name}' translation {source_platform}→{target_platform} ({len(plan.calls)} write call(s))",
        {"kind": kind, "source_platform": source_platform, "target_platform": target_platform, "confirmed": confirmed},
    )
    if gate is not None:
        return gate

    # 4) execute against Central.
    conn = ctx.lifespan_context.get("central_conn")
    if not conn:
        raise ToolError({"status_code": 500, "message": "Central connection not available"})
    results = await orchestrator.execute(conn.command, plan)
    return {"results": results, "unresolved": plan.unresolved, "preview": plan.preview()}


def register(mcp: FastMCP) -> None:
    """Register the cross-platform config translation bridge tools."""

    @mcp.tool(name="translate_config_preview", annotations=_PREVIEW_ANN)
    async def translate_config_preview(
        ctx: Context,
        source_platform: str,
        target_platform: str,
        kind: str,
        source_record: dict,
        scope_id: str | None = None,
        device_functions: list[str] | None = None,
        extra_ctx: dict | None = None,
    ) -> dict[str, Any]:
        """Preview the ordered Central calls to migrate one AOS 8 config object.

        Read-only — makes no writes. Runs the canonical translation engine over a
        single AOS 8 source record and returns the Central calls it would emit.

        Args:
            source_platform: source — only ``'aos8'`` today.
            target_platform: target — only ``'central'`` today.
            kind: the config kind — one of vlan_id / named_vlan / net_group / role /
                policy / auth_server / server_group / dot1x_auth / mac_auth /
                captive_portal / aaa_profile / gateway_cluster.
            source_record: the AOS 8 source record (e.g. one ``role`` / ``acl_sess`` /
                ``netdst`` / ``aaa_prof`` record). For named_vlan, pre-merge
                ``vlan_name`` ⨝ ``vlan_name_id`` into ``{name, vlan-ids}``.
            scope_id: the resolved Central scope-id to assign the object to
                (Stage 7). ``None`` is reported in ``unresolved`` and apply blocks.
            device_functions: override the per-kind default device-functions
                (vlan = MOBILITY_GW + CAMPUS_AP; everything else = MOBILITY_GW).
            extra_ctx: kind-specific reader inputs —
                ``role_records`` (policy: every AOS 8 role record, for role
                attribution), ``coa_servers`` (auth_server: aaa_prof.rfc3576_client[]
                for AUTH_AND_COA correlation), ``cluster_strategy`` (gateway_cluster:
                ha_only | intent_site | intent_manual), ``alias_name`` (named_vlan:
                override the default lower-cased alias name).

        Returns:
            {supported, canonical (secrets redacted), calls (bodies omitted),
            unresolved, preview}.
        """
        return await _preview_impl(
            ctx,
            source_platform,
            target_platform,
            kind,
            source_record,
            scope_id=scope_id,
            device_functions=device_functions,
            extra_ctx=extra_ctx,
        )

    @mcp.tool(name="translate_config_apply", annotations=_APPLY_ANN)
    async def translate_config_apply(
        ctx: Context,
        source_platform: str,
        target_platform: str,
        kind: str,
        source_record: dict,
        scope_id: str | None = None,
        device_functions: list[str] | None = None,
        extra_ctx: dict | None = None,
        confirmed: bool = False,
    ) -> dict[str, Any]:
        """Translate one AOS 8 config object and EXECUTE it against Central.

        Gated: requires ENABLE_CENTRAL_WRITE_TOOLS and fires the universal
        confirmation prompt before writing. Idempotent (ensure-or-create by name).
        Blocks ``kind='auth_server'`` (and any secret-bearing body) with a 403
        until AOS 8 secret tokenization ships — preview it and create manually.

        Same args as ``translate_config_preview`` plus ``confirmed`` (honored only
        when the client can't present an elicitation prompt).
        """
        return await _apply_impl(
            ctx,
            source_platform,
            target_platform,
            kind,
            source_record,
            scope_id=scope_id,
            device_functions=device_functions,
            extra_ctx=extra_ctx,
            confirmed=confirmed,
        )

    logger.info("Cross-platform: registered translate_config_preview + translate_config_apply tools")
