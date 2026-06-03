#!/usr/bin/env python3
"""Sync Aruba ReadMe-hosted OpenAPI definitions into ``vendor/<project>/``.

Each Aruba developer-hub project (``developer.arubanetworks.com/<project>``) is
a ReadMe project whose API reference is split across **multiple** uploaded
OpenAPI definitions (e.g. New Central MRT is Monitoring + Troubleshooting +
Services + Reporting + Notifications + MSP + Authorization). ReadMe serves each
compiled definition as raw JSON at::

    https://developer.arubanetworks.com/<project>/openapi/<apiSetting-id>

The ``<apiSetting-id>`` values are embedded in every reference page's HTML.
This script discovers them by scraping the project's ``/reference`` page,
fetches each definition, validates it parses as OpenAPI 3.x with >= 1 path,
and writes one ``<title-slug>.json`` per definition (keys sorted for stable
diffs) plus a deterministic ``_manifest.json`` recording provenance.

No browser is required. The earlier Playwright approach failed because this
portal embeds specs in server-rendered HTML rather than fetching them at
runtime, so there was no standalone JSON response to intercept (and a single
reference page only inlines its own operation). The ``/openapi/<id>`` endpoint
is the real upstream source.

**Adding a platform = one entry in ``PROJECTS``** (the same ReadMe pattern
backs aruba-uxi, aruba-cppm, aruba-aoscx, etc. — verify the hub path first).

Tool regeneration is intentionally NOT run here: the maintainer re-runs the
Central importer at release time so tool-surface changes are reviewed before
tagging. Exit code is non-zero on any project failure so the workflow's
issue-on-failure step fires and no bad snapshot is committed.
"""

from __future__ import annotations

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
]

# ReadMe apiSetting ids are 24-char hex Mongo ObjectIds embedded in page HTML.
_API_SETTING_RE = re.compile(r'"apiSetting":"([0-9a-f]{24})"')
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


def _discover_ids(slug: str) -> list[str]:
    """Scrape a project's /reference page for its apiSetting definition ids."""
    html = _http_get(f"{HUB}/{slug}/reference").decode("utf-8", "replace")
    ids = sorted(set(_API_SETTING_RE.findall(html)))
    if not ids:
        raise RuntimeError(f"no apiSetting ids found on {HUB}/{slug}/reference")
    return ids


def _fetch_spec(slug: str, setting_id: str) -> dict[str, Any] | None:
    """Fetch one definition; return the OAS dict or None if stale/invalid.

    Stale apiSetting ids (definitions deleted upstream) return a tiny error
    body that fails JSON/OAS validation — those are silently skipped.
    """
    raw = _http_get(f"{HUB}/{slug}/openapi/{setting_id}")
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

    ids = _discover_ids(slug)
    # file slug -> (apiSetting id, spec)
    collected: dict[str, tuple[str, dict[str, Any]]] = {}
    for setting_id in ids:
        spec = _fetch_spec(slug, setting_id)
        if spec is None:
            continue  # stale/retired definition id
        title = str(spec.get("info", {}).get("title", "untitled"))
        file_slug = _slugify(title)
        if file_slug in collected:  # title collision — disambiguate by id
            file_slug = f"{file_slug}-{setting_id[:6]}"
        collected[file_slug] = (setting_id, spec)

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
    for file_slug, (setting_id, spec) in sorted(collected.items()):
        _write_json(outdir / f"{file_slug}.json", spec)
        info = spec.get("info", {})
        path_count = len(spec.get("paths", {}))
        total_paths += path_count
        definitions.append(
            {
                "slug": file_slug,
                "id": setting_id,
                "title": str(info.get("title", "?")),
                "version": str(info.get("version", "?")),
                "path_count": path_count,
            }
        )

    manifest = {
        "project": slug,
        "source": f"{HUB}/{slug}/openapi/<apiSetting-id>",
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
