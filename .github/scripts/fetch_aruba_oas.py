#!/usr/bin/env python3
"""Sync Aruba ReadMe-hosted OpenAPI definitions into ``vendor/<project>/``.

Each Aruba developer-hub project (``developer.arubanetworks.com/<project>``) is
a ReadMe project whose API reference is split across **multiple** uploaded
OpenAPI definitions (e.g. New Central MRT is Monitoring + Troubleshooting +
Services + Reporting + Notifications + MSP + Authorization).

Aruba migrated the hub to ReadMe's **"SuperHub"** platform on 2026-07-02, which
retired the old ``/<project>/openapi/<hex-apiSetting-id>`` endpoint (now 404s)
and the ``"apiSetting"`` HTML markers. The reference page now server-renders its
props into a ``<script id="ssr-props">`` JSON block:

* ``apiDefinitions`` — the **active branch's** current specs (filename + uri).
* ``context.project.stable.apiRegistries`` — every uploaded version, each with a
  per-file ``uuid``.

This script parses ssr-props, resolves each current filename to its registry
``uuid``, and fetches the compiled OAS by uuid from the ReadMe dash API::

    https://dash.readme.com/api/v1/api-registry/<uuid>

It validates each parses as OpenAPI 3.x with >= 1 path, and writes one
``<title-slug>.json`` per definition (keys sorted for stable diffs) plus a
deterministic ``_manifest.json`` recording provenance. No browser required.

**Adding a platform = one entry in ``PROJECTS``** (the same ReadMe pattern
backs aruba-uxi, aruba-cppm, aruba-aoscx, etc. — verify the hub path first).

Tool regeneration is intentionally NOT run here: the maintainer re-runs the
Central importer at release time so tool-surface changes are reviewed before
tagging. Exit code is non-zero on any project failure so the workflow's
issue-on-failure step fires and no bad snapshot is committed.
"""

from __future__ import annotations

import html as _html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

HUB = "https://developer.arubanetworks.com"

# Each entry: the developer-hub project slug -> output subdir under vendor/.
# Extend this list to vendor additional Aruba ReadMe projects.
PROJECTS: list[dict[str, str]] = [
    {"slug": "new-central", "outdir": "central/mrt"},
    {"slug": "new-central-config", "outdir": "central/config"},
    # ArubaOS 8 JSON API — the full source-side object model (168 paths /
    # ~1240 schemas), authoritative field universe for AOS 8 → Central
    # translation mapping (pairs with the Central config OAS above).
    {"slug": "aos8", "outdir": "aos8"},
    # Other Aruba developer-hub projects we have a tool surface for —
    # vendored so their authoritative field schemas are on hand (the slugs
    # are the canonical short forms per developer.arubanetworks.com/llms.txt).
    {"slug": "uxi", "outdir": "uxi"},
    {"slug": "cppm", "outdir": "clearpass"},
    {"slug": "aoscx", "outdir": "aoscx"},
]

# ReadMe "SuperHub" (Aruba migrated the hub 2026-07-02) server-renders the
# reference page's props into a JSON <script id="ssr-props"> block. The active
# branch's specs live under ``apiDefinitions``; every historical version lives
# under ``context.project.stable.apiRegistries`` keyed by a per-file ``uuid``.
# The raw compiled OAS is fetched by uuid from the ReadMe dash API.
_SSR_PROPS_RE = re.compile(r'<script id="ssr-props"[^>]*>(.*?)</script>', re.DOTALL)
_README_REGISTRY = "https://dash.readme.com/api/v1/api-registry"
_SLUG_RE = re.compile(r"[^a-z0-9]+")

_UA = "Mozilla/5.0 (compatible; hpe-networking-mcp-oas-sync/1.0)"
_TIMEOUT = 30
_RETRIES = 3
_RETRY_BACKOFF = 3  # seconds, multiplied by attempt number

VENDOR = Path(__file__).resolve().parents[2] / "vendor"


def _http_get(url: str) -> bytes:
    """GET *url* with a browser UA and bounded retries; raise on final failure."""
    last_exc: Exception | None = None
    for attempt in range(1, _RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310 (trusted host)
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last_exc = exc
            if attempt < _RETRIES:
                time.sleep(_RETRY_BACKOFF * attempt)
    raise RuntimeError(f"GET failed after {_RETRIES} attempts: {url} ({last_exc})")


def _slugify(title: str) -> str:
    """Convert an OpenAPI ``info.title`` to a filesystem-stable slug."""
    return _SLUG_RE.sub("-", title.strip().lower()).strip("-") or "untitled"


def _looks_like_oas(obj: Any) -> bool:
    """True when *obj* is an OpenAPI/Swagger doc carrying at least one path."""
    return (
        isinstance(obj, dict)
        and bool(obj.get("openapi") or obj.get("swagger"))
        and isinstance(obj.get("paths"), dict)
        and len(obj["paths"]) > 0
    )


def _parse_ssr_props(slug: str) -> dict[str, Any]:
    """Parse the ``<script id="ssr-props">`` JSON from a project's /reference page."""
    page = _http_get(f"{HUB}/{slug}/reference").decode("utf-8", "replace")
    match = _SSR_PROPS_RE.search(page)
    if not match:
        raise RuntimeError(f"no ssr-props on {HUB}/{slug}/reference (portal structure changed?)")
    try:
        return json.loads(_html.unescape(match.group(1).strip()))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{slug}: ssr-props JSON did not parse ({exc})") from exc


def _discover_specs(slug: str) -> list[dict[str, str]]:
    """Discover the CURRENT branch's OpenAPI specs as ``[{filename, uuid}]``.

    ``apiDefinitions`` is the active branch's live set (e.g. New Central =
    monitoring-80/reporting-84/... on branch 26.04); ``apiRegistries`` holds
    every uploaded version keyed by a per-file ``uuid`` — which is what the raw
    OAS endpoint fetches by. We take the current filenames and resolve each to
    its registry uuid (last/most-recent entry wins on a duplicate filename).
    """
    props = _parse_ssr_props(slug)
    api_defs = props.get("apiDefinitions") or []
    registries = (((props.get("context") or {}).get("project") or {}).get("stable") or {}).get("apiRegistries") or []

    uuid_by_file: dict[str, str] = {}
    for reg in registries:
        filename, uuid = reg.get("filename"), reg.get("uuid")
        if filename and uuid:
            uuid_by_file[filename] = uuid  # later entries (more recent) override

    specs: list[dict[str, str]] = []
    for definition in api_defs:
        if definition.get("type") not in (None, "openapi"):
            continue  # skip non-OpenAPI definitions (e.g. graphql), if any
        filename = definition.get("filename")
        uuid = uuid_by_file.get(filename or "")
        if not uuid:
            continue  # current definition with no matching registry uuid — skip
        specs.append({"filename": filename, "uuid": uuid})

    if not specs:
        raise RuntimeError(f"{slug}: no OpenAPI definitions found in ssr-props apiDefinitions")
    return specs


def _fetch_spec(uuid: str) -> dict[str, Any] | None:
    """Fetch one compiled OAS by its ReadMe api-registry uuid.

    Returns the OAS dict, or None if the response isn't a valid OpenAPI doc.
    """
    raw = _http_get(f"{_README_REGISTRY}/{uuid}")
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return obj if _looks_like_oas(obj) else None


def _load_prev_manifest(outdir: Path) -> dict[str, Any] | None:
    """Load a project's previous _manifest.json, or None on first run."""
    mf = outdir / "_manifest.json"
    if not mf.is_file():
        return None
    try:
        return json.loads(mf.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _write_json(path: Path, obj: Any) -> None:
    """Write *obj* as deterministic, sorted, newline-terminated JSON."""
    path.write_text(
        json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def sync_project(project: dict[str, str]) -> dict[str, Any]:
    """Discover, fetch, validate and vendor one project's OAS definitions.

    Returns a summary dict. Raises on any failure that should block the run
    (no ids, zero valid definitions, or a regression in definition count).
    """
    slug, outdir_name = project["slug"], project["outdir"]
    outdir = VENDOR / outdir_name
    outdir.mkdir(parents=True, exist_ok=True)

    specs = _discover_specs(slug)
    # vendored file slug -> (registry uuid, spec)
    collected: dict[str, tuple[str, dict[str, Any]]] = {}
    for entry in specs:
        uuid = entry["uuid"]
        spec = _fetch_spec(uuid)
        if spec is None:
            continue  # unfetchable / not a valid OAS doc
        title = str(spec.get("info", {}).get("title", "untitled"))
        file_slug = _slugify(title)
        if file_slug in collected:  # title collision — disambiguate by uuid
            file_slug = f"{file_slug}-{uuid[:6]}"
        collected[file_slug] = (uuid, spec)

    if not collected:
        raise RuntimeError(f"{slug}: no valid OpenAPI definitions discovered")

    # Regression guard: refuse to shrink the vendored set on a transient miss.
    # A genuine upstream removal will fail here too — that's intentional, it
    # forces a human to review the drop rather than auto-merging a deletion.
    prev = _load_prev_manifest(outdir)
    if prev is not None:
        prev_count = len(prev.get("definitions", []))
        if len(collected) < prev_count:
            raise RuntimeError(
                f"{slug}: definition count dropped {prev_count} -> {len(collected)}; "
                "refusing to update (re-run once upstream is stable, or investigate)"
            )

    # Write specs; prune .json files for definitions that no longer exist.
    keep = {f"{s}.json" for s in collected} | {"_manifest.json"}
    for existing in outdir.glob("*.json"):
        if existing.name not in keep:
            existing.unlink()

    definitions = []
    total_paths = 0
    for file_slug, (uuid, spec) in sorted(collected.items()):
        _write_json(outdir / f"{file_slug}.json", spec)
        info = spec.get("info", {})
        path_count = len(spec.get("paths", {}))
        total_paths += path_count
        definitions.append(
            {
                "slug": file_slug,
                "id": uuid,
                "title": str(info.get("title", "?")),
                "version": str(info.get("version", "?")),
                "path_count": path_count,
            }
        )

    manifest = {
        "project": slug,
        "source": f"{_README_REGISTRY}/<uuid> (discovered via {HUB}/{slug}/reference)",
        "definition_count": len(definitions),
        "total_paths": total_paths,
        "definitions": sorted(definitions, key=lambda d: d["slug"]),
    }
    _write_json(outdir / "_manifest.json", manifest)

    return {"slug": slug, "definitions": len(definitions), "paths": total_paths}


def main() -> int:
    failures: list[str] = []
    summaries: list[dict[str, Any]] = []
    for project in PROJECTS:
        try:
            summaries.append(sync_project(project))
        except Exception as exc:  # noqa: BLE001 — report per-project, continue
            failures.append(str(exc))
            print(f"::error::{exc}", file=sys.stderr)

    for s in summaries:
        print(f"  {s['slug']}: {s['definitions']} definitions, {s['paths']} paths")

    if failures:
        print(f"FAILED: {len(failures)} project(s) errored", file=sys.stderr)
        return 1
    print("OK: all projects synced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
