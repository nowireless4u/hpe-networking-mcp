"""Read-only bridge that exposes the translations engine to AI clients.

The translations engine (``hpe_networking_mcp.translations``) lives in the
package and produces deterministic ``TargetCall`` descriptors from a
source-platform record (e.g. an AOS 8 ``acl_sess`` row) plus runtime
context (Central scope_id, role records, etc.). The engine never makes
API calls — it's pure data — so a tool wrapping it is read-only by
construction.

Why this tool exists: code-mode ``execute()`` blocks imports of internal
modules (verified via Zach's OpenClaw + Qwen3 4B test report 2026-05-07
where ``import hashlib`` failed). AI clients running in code mode can't
``import hpe_networking_mcp.translations`` directly. This tool is the
bridge — it accepts the same inputs the engine takes, runs the engine
server-side, and returns JSON-serializable output.

Use cases:

* aos-migration Stage 9b — engine-driven preview of what the migration
  will emit per AOS 8 object (per role, per ACL, per VLAN). Today's
  Phase-3-lite read-only step before #240's actual writes land.
* Future ad-hoc translation previews ("show me what this AOS 8 role
  would look like in Central").

The tool is intentionally ungated by ``ENABLE_CENTRAL_WRITE_TOOLS``
because it cannot write — every code path returns dict / list of
descriptors. No ``central_*`` API call is made. Real execution (write
path) lands later as a separate ``central_manage_*`` tool with
elicitation gating, per #240.
"""

from __future__ import annotations

import dataclasses
from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.translations import (
    EngineError,
    LoaderError,
    TargetCall,
    Translation,
    emit_calls,
    load_translations,
)

# Module-level cache. Translations are validated JSON files — load once,
# reuse across calls. Cleared automatically when the process restarts.
_TRANSLATIONS_CACHE: dict[str, Translation] | None = None


def _get_translations() -> dict[str, Translation]:
    """Lazily load + cache the shipped translations.

    Caches at module level on first call. ``LoaderError`` propagates to
    the tool wrapper which converts it to a readable error response.
    """
    global _TRANSLATIONS_CACHE
    if _TRANSLATIONS_CACHE is None:
        _TRANSLATIONS_CACHE = load_translations()
    return _TRANSLATIONS_CACHE


def _record_id(record: dict[str, Any], translation_id: str) -> str:
    """Extract a meaningful primary-key string from one source record.

    Falls back to ``"<unknown>"`` if the expected field isn't present so
    the preview output stays useful even when source data is malformed.
    """
    if not isinstance(record, dict):
        return "<not-a-dict>"

    primary_key_by_translation: dict[str, str] = {
        "central:policy": "accname",
        "central:role": "rname",
        "central:vlan_id": "id",
        "central:named_vlan": "name",
    }
    field = primary_key_by_translation.get(translation_id)
    if field is None:
        # Best-effort: try a few common identifier fields.
        for guess in ("id", "name", "rname", "accname"):
            if guess in record:
                return str(record[guess])
        return "<unknown>"

    value = record.get(field)
    return str(value) if value is not None else "<missing>"


def _serialize_call(call: TargetCall) -> dict[str, Any]:
    """Convert a ``TargetCall`` dataclass to a JSON-friendly dict."""
    return dataclasses.asdict(call)


@tool(annotations=READ_ONLY)
async def central_translation_preview(
    ctx: Context,
    translation_id: str,
    source_records: list[dict],
    runtime_values: dict[str, Any] | None = None,
    source_platform: str = "aos8",
    overrides: dict[str, Any] | None = None,
) -> dict:
    """
    Read-only preview of what the translations engine would emit per source record.

    Runs the translations engine server-side over a list of source-platform
    records and returns the deterministic ``TargetCall`` descriptors per
    record. **Does not write to Central.** Real execution lands in a future
    ``central_manage_*`` tool gated by ``ENABLE_CENTRAL_WRITE_TOOLS`` and
    elicitation; this tool is the read-only preview path used by
    aos-migration Stage 9b.

    Available shipped translations (as of v3.0.1.6):

    * ``central:vlan_id`` — AOS 8 ``vlan_id`` → Central layer2-vlan
    * ``central:named_vlan`` — AOS 8 composite (vlan_name + vlan_name_id) → Central named-VLAN with alias chain
    * ``central:role`` — AOS 8 ``role`` → Central role profile (Gateway-targeted)
    * ``central:policy`` — AOS 8 ``acl_sess`` → Central /policies POST

    Required ``runtime_values`` per translation:

    * ``central:vlan_id`` / ``central:named_vlan`` / ``central:role`` —
      ``central_scope_id`` (string).
    * ``central:policy`` — ``central_scope_id`` (string) PLUS
      ``role_records`` (list of full AOS 8 role records, used by the
      engine's preprocessing step to compute role_attribution per ACL
      via reverse-index lookup).

    For ``central:named_vlan``: pre-merge the composite source (vlan_name
    join vlan_name_id by ``name``) before passing each merged record.
    The engine's per-record contract assumes a single dict per call.

    Parameters:
        translation_id: Composite key like ``"central:policy"`` matching
            ``"<target_platform>:<target_id>"`` from a shipped translation
            JSON. Unknown ids return an error in the response.
        source_records: List of source-platform records to preview, one
            per emit_calls invocation. Empty list returns an empty result.
        runtime_values: Target-platform-specific runtime context (e.g.
            ``{"central_scope_id": "...", "role_records": [...]}``). The
            translation declares which keys are required; missing keys
            surface per-record as a ``skip_reason``.
        source_platform: Which ``sources.<platform>`` block of the
            translation to consume. Defaults to ``"aos8"`` (the only
            shipped source today).
        overrides: Optional per-session operator overrides for derived
            values (e.g. ``{"alias_name": "custom-name"}`` for named_vlan).

    Returns:
        Dict with:

        * ``translation_id`` — echo of the input
        * ``source_platform`` — echo of the input
        * ``record_count`` — total source records processed
        * ``translatable_count`` — records that produced TargetCalls
        * ``skipped_count`` — records that hit an EngineError
        * ``results`` — list of per-record dicts with
          ``record_id`` / ``target_calls`` / ``call_count`` /
          ``skip_reason`` (None on success).

        On a fatal error (unknown translation_id, loader failure, etc.)
        returns ``{"ok": false, "error": "..."}`` instead of the normal
        shape — code-mode error contract per
        ``project_code_mode_error_contract``.
    """
    _ = ctx  # ctx is unused — pure-data tool, no platform conn needed
    runtime_values = runtime_values or {}
    overrides = overrides or {}

    try:
        translations = _get_translations()
    except LoaderError as exc:
        return {"ok": False, "error": f"Translation loader failed: {exc}"}

    if translation_id not in translations:
        return {
            "ok": False,
            "error": f"Unknown translation_id {translation_id!r}; available: {sorted(translations.keys())}",
        }
    translation = translations[translation_id]

    if source_platform not in translation.sources:
        return {
            "ok": False,
            "error": (
                f"Translation {translation_id!r} does not declare source {source_platform!r}; "
                f"available: {sorted(translation.sources.keys())}"
            ),
        }

    results: list[dict[str, Any]] = []
    translatable = 0
    skipped = 0
    for record in source_records:
        rid = _record_id(record, translation_id)
        try:
            calls = emit_calls(
                translation=translation,
                source_data=record,
                source_platform_id=source_platform,
                runtime_values=runtime_values,
                overrides=overrides,
            )
        except EngineError as exc:
            results.append(
                {
                    "record_id": rid,
                    "target_calls": [],
                    "call_count": 0,
                    "skip_reason": str(exc),
                }
            )
            skipped += 1
            continue

        results.append(
            {
                "record_id": rid,
                "target_calls": [_serialize_call(c) for c in calls],
                "call_count": len(calls),
                "skip_reason": None,
            }
        )
        translatable += 1

    return {
        "translation_id": translation_id,
        "source_platform": source_platform,
        "record_count": len(source_records),
        "translatable_count": translatable,
        "skipped_count": skipped,
        "results": results,
    }
