"""Canonical translation orchestrator.

Ties the reader/writer layers together for the rebuilt translation engine:

    source object --reader--> CanonicalWlan --writer(s)--> ordered call list

``plan()`` is pure (no I/O): it runs the registered reader then the registered
writer(s), merging multiple writer outputs into one ordered call list with
re-based ``depends_on`` indices. ``execute()`` runs that plan against a live
client with ensure-or-create semantics (skip a create whose target already
exists; skip an assignment that is already in place).

This is the canonical path; the legacy JSON ``engine.emit_calls`` stays only for
the AOS8→Central translations until cutover.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from hpe_networking_mcp.translations.readers.aos8 import aos8_read_wlan
from hpe_networking_mcp.translations.readers.mist import mist_read_wlan
from hpe_networking_mcp.translations.writers.central import central_write_wlan
from hpe_networking_mcp.translations.writers.central_radius import central_write_server_group

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

WLAN = "wlan"

# (source_platform, kind) -> reader(source_obj, **ctx) -> canonical
_READERS: dict[tuple[str, str], Callable[..., Any]] = {
    ("mist", WLAN): mist_read_wlan,
    ("aos8", WLAN): aos8_read_wlan,
}

# (target_platform, kind) -> ordered list of writer(canon, **ctx) -> [call descriptors].
# Writers run in list order; the orchestrator merges + re-bases depends_on and
# chains each writer's first call onto the previous writer's last call.
_WRITERS: dict[tuple[str, str], list[Callable[..., list[dict[str, Any]]]]] = {
    ("central", WLAN): [central_write_server_group, central_write_wlan],
}


def supported() -> dict[str, list[str]]:
    """Return the registered readers/writers, for discovery/preview."""
    return {
        "readers": [f"{p}:{k}" for (p, k) in _READERS],
        "writers": [f"{p}:{k}" for (p, k) in _WRITERS],
    }


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------


@dataclass
class TranslationPlan:
    """A translated, ordered set of target calls plus the canonical intermediate."""

    source_platform: str
    target_platform: str
    kind: str
    canonical: Any
    calls: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def unresolved(self) -> list[dict[str, Any]]:
        """Anything the caller could not resolve — assignment scopes AND gateway
        clusters. A tunneled/hybrid/dual overlay with no cluster binding is as
        incomplete as a WLAN assigned to a non-existent scope; both must block
        before any write (the writer flags clusters via ``unresolved_clusters``)."""
        out = [c["unresolved"] for c in self.calls if c.get("unresolved")]
        out += [
            {"kind": "gateway_cluster", "name": c["path"].split("/")[-1]}
            for c in self.calls
            if c.get("unresolved_clusters")
        ]
        return out

    def preview(self) -> str:
        """Human-readable dry-run rendering of the ordered calls."""
        lines = [f"{self.source_platform} → {self.target_platform} [{self.kind}]"]
        for i, c in enumerate(self.calls):
            lines.append(f"  {i}. {c['method']} {c['path']} — {c.get('purpose', '')}")
        for u in self.unresolved:
            lines.append(f"  ! unresolved {u['kind']}: {u['name']}")
        return "\n".join(lines)


def _merge(call_lists: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Concatenate writer outputs, re-basing depends_on and chaining writers.

    Each writer returns a self-consistent list whose depends_on are indices into
    its own list. On merge we offset those indices, and make each writer's first
    call depend on the previous writer's last call (so e.g. the WLAN create runs
    after its server-group exists).
    """
    merged: list[dict[str, Any]] = []
    prev_last: int | None = None
    for calls in call_lists:
        if not calls:
            continue
        offset = len(merged)
        first_idx = offset
        for c in calls:
            nc = dict(c)
            nc["depends_on"] = [d + offset for d in c.get("depends_on", [])]
            merged.append(nc)
        if prev_last is not None and first_idx not in merged[first_idx]["depends_on"]:
            merged[first_idx]["depends_on"].append(prev_last)
        prev_last = len(merged) - 1
    return merged


def to_canonical(source_platform: str, kind: str, source_obj: Any, **reader_ctx: Any) -> Any:
    """Run the registered reader for (source_platform, kind)."""
    try:
        reader = _READERS[(source_platform, kind)]
    except KeyError as e:
        raise ValueError(f"No reader registered for {source_platform}:{kind}") from e
    return reader(source_obj, **reader_ctx)


def from_canonical(target_platform: str, kind: str, canon: Any, **writer_ctx: Any) -> list[dict[str, Any]]:
    """Run all registered writers for (target_platform, kind), merged + ordered."""
    try:
        writers = _WRITERS[(target_platform, kind)]
    except KeyError as e:
        raise ValueError(f"No writer registered for {target_platform}:{kind}") from e
    # server-group writer takes no scope ctx; WLAN writer does. Pass ctx only to
    # writers that accept it (simple: try with ctx, fall back to none).
    outputs: list[list[dict[str, Any]]] = []
    for w in writers:
        try:
            outputs.append(w(canon, **writer_ctx))
        except TypeError:
            outputs.append(w(canon))
    return _merge(outputs)


def plan(
    source_platform: str,
    target_platform: str,
    kind: str,
    source_obj: Any,
    *,
    reader_ctx: dict[str, Any] | None = None,
    writer_ctx: dict[str, Any] | None = None,
) -> TranslationPlan:
    """Translate a source object into an ordered target-call plan (pure, no I/O)."""
    canon = to_canonical(source_platform, kind, source_obj, **(reader_ctx or {}))
    calls = from_canonical(target_platform, kind, canon, **(writer_ctx or {}))
    p = TranslationPlan(
        source_platform=source_platform,
        target_platform=target_platform,
        kind=kind,
        canonical=canon,
        calls=calls,
    )
    if p.unresolved:
        p.notes.append(f"{len(p.unresolved)} assignment scope(s) unresolved — create them first.")
    return p


# ---------------------------------------------------------------------------
# Central scope resolution (builds writer_ctx for central:wlan assignment)
# ---------------------------------------------------------------------------


async def resolve_central_wlan_scopes(conn: Any) -> dict[str, Any]:
    """Build the central WLAN writer_ctx (scope-id maps) from the live scope tree.

    Returns ``global_scope_id`` + name→scope-id maps for SITE / SITE_COLLECTION /
    DEVICE_COLLECTION, matching the four canonical assignment facets. Names that
    don't resolve are surfaced by the writer as ``unresolved`` for the skill to
    create first.
    """
    # Lazy import: keeps the pure planning layer free of Central internals.
    from hpe_networking_mcp.platforms.central.scope_builder import _node_to_dict, build_scope_tree

    tree = await build_scope_tree(conn)
    root = _node_to_dict(tree, tree.root) if tree.root else None

    flat: list[dict[str, Any]] = []

    def _walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        flat.append({"id": node.get("scope_id"), "name": node.get("scope_name"), "type": node.get("type")})
        for ch in node.get("children", []):
            _walk(ch)

    _walk(root)

    def _map(scope_type: str) -> dict[str, str]:
        return {r["name"]: r["id"] for r in flat if r["type"] == scope_type and r["name"] and r["id"]}

    global_ids = [r["id"] for r in flat if r["type"] == "GLOBAL" and r["id"]]
    return {
        "global_scope_id": global_ids[0] if global_ids else None,
        "site_name_to_scope_id": _map("SITE"),
        "site_collection_name_to_scope_id": _map("SITE_COLLECTION"),
        "device_group_name_to_scope_id": _map("DEVICE_COLLECTION"),
    }


# ---------------------------------------------------------------------------
# Execute
# ---------------------------------------------------------------------------

# A client call: (method, path, params, data) -> {"code", "msg"}
ClientCall = Callable[..., Awaitable[dict[str, Any]]]

_CONFIG_ASSIGNMENTS = "network-config/v1alpha1/config-assignments"


async def _exists(command: ClientCall, path: str) -> bool:
    """True if a GET on a library object path returns a non-empty config.

    Central returns ``200 + {}`` for a GET on a non-existent named object (not a
    404), so a 2xx alone is not proof of existence — the body must be a
    populated dict (a real object always carries at least ``name``/``type``).
    """
    r = await command("GET", path)
    if not 200 <= r.get("code", 0) < 300:
        return False
    msg = r.get("msg")
    return isinstance(msg, dict) and bool(msg)


async def _assignment_exists(command: ClientCall, body: dict[str, Any]) -> bool:
    """True if the config-assignment in ``body`` is already present."""
    entry = body["config-assignment"][0]
    r = await command("GET", _CONFIG_ASSIGNMENTS)
    rows = r["msg"].get("config-assignment", []) if isinstance(r.get("msg"), dict) else []
    return any(
        row.get("scope-id") == entry.get("scope-id")
        and row.get("profile-type") == entry.get("profile-type")
        and row.get("profile-instance") == entry.get("profile-instance")
        for row in rows
    )


async def execute(
    command: ClientCall,
    plan: TranslationPlan,
    *,
    ensure_or_create: bool = True,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Run a plan's calls in order with ensure-or-create semantics.

    Args:
        command: async ``(method, path, api_params=, api_data=) -> {code, msg}``.
        plan: the TranslationPlan to run.
        ensure_or_create: when True, skip a create whose target already exists,
            and skip an assignment already in place (your "if it exists, use it").
        dry_run: when True, perform no writes — only existence checks + the plan.

    Returns:
        One result row per call: ``{path, action, code}`` where action is one of
        ``created`` / ``assigned`` / ``skipped_exists`` / ``planned`` / ``failed``.
    """
    if plan.unresolved:
        # Don't push a half-wired WLAN: unresolved scopes must be created first.
        return [{"path": "-", "action": "blocked_unresolved", "detail": plan.unresolved}]

    results: list[dict[str, Any]] = []
    # Indices whose call completed successfully (created / assigned / already
    # exists / would-run in a dry run). A call is only attempted once every index
    # in its depends_on has completed — otherwise a prerequisite failure (e.g. the
    # auth-server create) would leave the dependent WLAN/assignment to run against
    # a half-built config.
    done: set[int] = set()
    for i, call in enumerate(plan.calls):
        path, method, body = call["path"], call["method"], call.get("body", {})
        is_assignment = path == _CONFIG_ASSIGNMENTS

        unmet = [d for d in call.get("depends_on", []) if d not in done]
        if unmet:
            results.append({"path": path, "action": "blocked_dependency_failed", "depends_on": unmet})
            continue

        if ensure_or_create and method == "POST":
            already = await _assignment_exists(command, body) if is_assignment else await _exists(command, path)
            if already:
                results.append({"path": path, "action": "skipped_exists", "code": 200})
                done.add(i)
                continue

        if dry_run:
            results.append({"path": path, "action": "planned", "code": None})
            done.add(i)
            continue

        r = await command(method, path, api_params=call.get("query") or None, api_data=body)
        code = r.get("code", 0)
        ok = 200 <= code < 300
        if ok:
            done.add(i)
        action = ("assigned" if is_assignment else "created") if ok else "failed"
        row: dict[str, Any] = {"path": path, "action": action, "code": code}
        if not ok:
            row["msg"] = r.get("msg")
        results.append(row)
    return results
