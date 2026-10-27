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
* ``apiRegistries`` — every uploaded file, each with a per-file ``uuid``. Around
  2026-09-29 the hub moved this list (see ``_REGISTRY_PATHS``); the old
  location broke every sync with "no OpenAPI definitions found".

This script parses ssr-props, resolves each current filename to its registry
``uuid``, and fetches the compiled OAS by uuid from the ReadMe dash API::

    https://dash.readme.com/api/v1/api-registry/<uuid>

Some current-branch definitions have **no** registry entry (New Central serves
several that way). Those are located through their reference pages and rebuilt
from the per-operation documents each page's Markdown view embeds (indexed by
the project's ``llms.txt``), rather than silently dropped.

It validates each parses as OpenAPI 3.x with >= 1 path, and writes one
``<title-slug>.json`` per definition (keys sorted for stable diffs) plus a
deterministic ``_manifest.json``. No browser required.

**Adding a platform = one entry in ``PROJECTS``** (the same ReadMe pattern
backs aruba-uxi, aruba-cppm, aruba-aoscx, etc. — verify the hub path first).

Tool regeneration is intentionally NOT run here: the maintainer re-runs the
Central importer at release time so tool-surface changes are reviewed before
tagging. Exit code is non-zero on any project failure so the workflow's
issue-on-failure step fires and no bad snapshot is committed.
"""

from __future__ import annotations

import argparse
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
# branch's specs live under ``apiDefinitions``; uploaded files live in a
# registry list keyed by a per-file ``uuid`` (see ``_REGISTRY_PATHS``).
# The raw compiled OAS is fetched by uuid from the ReadMe dash API.
_SSR_PROPS_RE = re.compile(r'<script id="ssr-props"[^>]*>(.*?)</script>', re.DOTALL)
_README_REGISTRY = "https://dash.readme.com/api/v1/api-registry"

#: Names the definition file a reference page renders.
_RAYCAST_OAS_BYTES_RE = re.compile(rb'data-raycast-oas="[^"]*/apis/([^"/]+\.json)"')
_STREAM_CHUNK = 64 * 1024

#: How far back to scan for the object start when extracting an embedded OAS.
_EMBED_SCAN_LIMIT = 4000
#: A reference page's Markdown view (``<page>.md``) embeds the OpenAPI document of
#: that page's operation in a fenced ``json`` block. Since October 2026 the hub
#: embeds only the page's own operation -- the HTML page once carried the whole
#: definition -- so a registry-less definition is rebuilt from every page that
#: renders it.
_MD_OAS_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
#: The project's ``llms.txt`` lists every reference page's ``.md`` URL.
_LLMS_REFERENCE_RE = re.compile(r"\((https://[^)\s]+/reference/[^)\s]+\.md)\)")
#: Pause between reference-page fetches: about 360 pages for New Central, once a run.
_MD_PAGE_DELAY = 0.5
#: Ceiling on reference pages read for one project; past it, the index is wrong.
_MD_PAGE_LIMIT = 2000
#: A definition whose path count falls below this share of the vendored one is
#: refused: a partial document, never a real upstream removal of that size.
_MIN_PATH_SHARE = 0.5

#: Ceiling on the reference-page discovery walk. It resolves a handful of
#: registry-less definitions; on 2026-10-01 New Central's six ``*-final-openapi``
#: files took 7 pages and 2 MB (interleaved walk, streamed reads). About seven
#: times that is the ceiling: a walk this long means discovery is broken.
_PAGE_LIMIT = 50
_PAGE_BYTES_LIMIT = 64 * 2**20

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


def _http_read_until(url: str, pattern: re.Pattern[bytes]) -> bytes:
    """GET *url* but stop reading once *pattern* matches; same retries as ``_http_get``.

    A reference page names its definition about a third of the way in, ahead of
    the definition itself (about 1 MB on New Central), so discovery reads that far
    and closes the connection.
    """
    last_exc: Exception | None = None
    for attempt in range(1, _RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310 (trusted host)
                buf = b""
                while chunk := resp.read(_STREAM_CHUNK):
                    # Search only the new chunk plus enough overlap for a match split across reads.
                    tail = len(buf)
                    buf += chunk
                    if pattern.search(buf, max(0, tail - 512)):
                        break
                return buf
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


#: ``apiDefinitions`` ``type`` labels that name an OpenAPI document. The hub labels
#: an upload by how it arrived, not by its version: since 2026-10-09 every ClearPass
#: definition reads ``swagger`` although the documents are ``openapi: 3.0.0``.
#: Anything else (e.g. ``graphql``) is skipped; each fetched document is still
#: checked by ``_looks_like_oas`` before it is written.
_OAS_DEFINITION_TYPES: frozenset[str | None] = frozenset({None, "openapi", "swagger"})


#: Where ssr-props keeps the current version's ``{filename, uuid}`` registry list,
#: newest layout first. Around 2026-09-29 the hub moved it from
#: ``context.project.stable`` (which now holds only ``version``) to
#: ``context.version`` and ``context.project.child.stable``.
_REGISTRY_PATHS: tuple[tuple[str, ...], ...] = (
    ("context", "version", "apiRegistries"),
    ("context", "project", "child", "stable", "apiRegistries"),
    ("context", "project", "stable", "apiRegistries"),
)


def _current_registries(props: dict[str, Any]) -> list[dict[str, Any]]:
    """The first non-empty registry list among ``_REGISTRY_PATHS``."""
    for path in _REGISTRY_PATHS:
        node: Any = props
        for key in path:
            node = node.get(key) if isinstance(node, dict) else None
        if isinstance(node, list) and node:
            return node
    return []


def _discover_specs(slug: str) -> list[dict[str, str]]:
    """Discover the CURRENT branch's OpenAPI specs as ``[{filename, uuid|page, via}]``.

    ``apiDefinitions`` is the active branch's live set (e.g. New Central =
    monitoring-80/reporting-84/... on branch 26.04); the registry list holds
    every uploaded file keyed by a per-file ``uuid`` — which is what the raw
    OAS endpoint fetches by. We take the current filenames and resolve each to
    its registry uuid (last/most-recent entry wins on a duplicate filename).
    Definitions with no registry entry are located via their reference pages.
    """
    props = _parse_ssr_props(slug)
    api_defs = props.get("apiDefinitions") or []
    registries = _current_registries(props)
    if api_defs and not registries:
        # Without the registry list every definition would go to the page
        # walk: a hub layout change once turned the config sync into a 1.4 GB+
        # page walk. A moved list is a failure to fix here, not to work around.
        where = ", ".join(".".join(path) for path in _REGISTRY_PATHS)
        raise RuntimeError(
            f"{slug}: ssr-props lists {len(api_defs)} definitions but no apiRegistries at any known path "
            f"({where}); the hub layout moved. Refusing to scrape every reference page instead."
        )

    uuid_by_file: dict[str, str] = {}
    for reg in registries:
        filename, uuid = reg.get("filename"), reg.get("uuid")
        if filename and uuid:
            uuid_by_file[filename] = uuid  # later entries (more recent) override

    specs: list[dict[str, str]] = []
    unresolved: list[str] = []
    skipped_types: set[str] = set()
    for definition in api_defs:
        if definition.get("type") not in _OAS_DEFINITION_TYPES:
            skipped_types.add(str(definition.get("type")))
            continue  # not an OpenAPI document (e.g. graphql)
        filename = definition.get("filename")
        if not filename:
            continue
        uuid = uuid_by_file.get(filename)
        if uuid:
            specs.append({"filename": filename, "uuid": uuid, "via": "registry"})
        else:
            # NOT skipped. A current-branch definition with no registry entry is
            # still published — New Central serves several that way — and silently
            # dropping it hides live endpoints from the spec index and get_schema.
            unresolved.append(filename)

    if unresolved:
        specs.extend(_discover_via_pages(slug, unresolved))

    if not specs:
        # Say what was there: a bare "none found" once hid that every definition
        # had simply been relabelled to a type this filter did not accept.
        why = f"; skipped {len(api_defs)} of type {sorted(skipped_types)}" if skipped_types else ""
        raise RuntimeError(f"{slug}: no OpenAPI definitions found in ssr-props apiDefinitions{why}")
    return specs


def _interleave(sequences: list[list[str]]) -> list[str]:
    """One item from each sequence in turn: ``[[a1, a2], [b1]] -> [a1, b1, a2]``."""
    out: list[str] = []
    for i in range(max((len(seq) for seq in sequences), default=0)):
        out.extend(seq[i] for seq in sequences if i < len(seq))
    return out


def _sidebar_leaf_pages(props: dict[str, Any]) -> list[str]:
    """Every reference-page slug in the sidebar, interleaved across its sections.

    In depth-first order the page walk spent its whole budget inside the first
    big section: on New Central, 150 pages in Monitoring, never reaching
    Services, MSP, Notifications, Troubleshooting or Reporting, where the other
    registry-less definitions live. Taking one page from each branch in turn,
    at every level, reaches every section within the first few pages.
    """

    def walk(node: Any) -> list[str]:
        if isinstance(node, list):
            return _interleave([walk(child) for child in node])
        if not isinstance(node, dict):
            return []
        uri = node.get("uri") or ""
        own = [uri.rsplit("/", 1)[-1]] if "/reference/" in uri and "/categories/" not in uri else []
        return own + walk(node.get("pages") or [])

    return walk(props.get("sidebar") or [])


def _discover_via_pages(slug: str, wanted: list[str]) -> list[dict[str, str]]:
    """Locate definitions that have no registry uuid, via their reference pages.

    Those definitions are unreachable through ``api-registry/<uuid>`` because
    they have no uuid. They ARE reachable through the docs: every operation page
    names its source definition file in a ``data-raycast-oas`` attribute, so one
    page identifies one definition exactly rather than by guessing from
    ``info.title`` (both the numbered and the ``*-final-openapi`` definitions
    report the same title).

    Walks the sidebar's leaf pages in order until every wanted definition has
    been named by one. The walk stops at ``_PAGE_LIMIT`` pages or
    ``_PAGE_BYTES_LIMIT`` bytes: past that, discovery is broken, not slow.
    """
    props = _parse_ssr_props(slug)
    remaining = set(wanted)
    found: list[dict[str, str]] = []
    seen_pages: set[str] = set()
    pages = downloaded = 0

    for page_slug in _sidebar_leaf_pages(props):
        if not remaining:
            break
        if page_slug in seen_pages:
            continue
        if pages >= _PAGE_LIMIT or downloaded >= _PAGE_BYTES_LIMIT:
            raise RuntimeError(
                f"{slug}: page discovery stopped after {pages} pages ({downloaded / 2**20:.0f} MB) with "
                f"{sorted(remaining)} still unresolved. It exists for a few registry-less definitions; "
                "this many means discovery is broken."
            )
        seen_pages.add(page_slug)
        pages += 1
        try:
            raw = _http_read_until(f"{HUB}/{slug}/reference/{page_slug}", _RAYCAST_OAS_BYTES_RE)
        except Exception:  # noqa: BLE001 — one unreachable page must not abort discovery
            continue
        downloaded += len(raw)
        m = _RAYCAST_OAS_BYTES_RE.search(raw)
        if not m:
            continue
        filename = m.group(1).decode("utf-8", "replace")
        if filename not in remaining:
            continue
        remaining.discard(filename)
        found.append({"filename": filename, "page": page_slug, "via": "page"})

    print(f"  {slug}: {len(found)} definition(s) via reference pages ({pages} pages, {downloaded / 2**20:.0f} MB)")
    if remaining:
        raise RuntimeError(
            f"{slug}: {len(remaining)} current-branch definition(s) could not be resolved "
            f"by registry uuid OR by reference page: {sorted(remaining)}. "
            "They are published but would be vendored as nothing — refusing to sync a "
            "silently incomplete set."
        )
    return found


def _extract_embedded_oas(page: str) -> dict[str, Any] | None:
    """Pull the compiled OAS that the reference page embeds inline.

    Since October 2026 that is only the page's own operations, not the whole
    definition; ``_fetch_spec_via_page`` reads it for the definition's title.
    Brace-match outward from the ``"paths":`` key to recover the enclosing object.
    """
    key = page.find('"paths":')
    if key < 0:
        return None
    for start in reversed([i for i, ch in enumerate(page[:key]) if ch == "{"][-_EMBED_SCAN_LIMIT:]):
        candidate = _brace_match(page, start)
        if not candidate or '"paths":' not in candidate:
            continue
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if _looks_like_oas(obj):
            return obj
    return None


def _brace_match(text: str, start: int) -> str | None:
    """Return the balanced ``{...}`` span beginning at *start*, or None."""
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


#: Every reference page's embedded OAS, per project, read once per run.
_PAGE_SPECS: dict[str, list[dict[str, Any]]] = {}


def _page_oas(text: str) -> dict[str, Any] | None:
    """The OpenAPI document a reference page's ``.md`` embeds, or None."""
    m = _MD_OAS_RE.search(text)
    if not m:
        return None
    try:
        obj = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    return obj if _looks_like_oas(obj) else None


def _reference_page_specs(project_slug: str) -> list[dict[str, Any]]:
    """Every reference page's embedded OAS for ``project_slug``, fetched once and cached.

    A page that can't be fetched fails the run: a definition rebuilt without it
    would be silently incomplete.
    """
    cached = _PAGE_SPECS.get(project_slug)
    if cached is not None:
        return cached
    index = _http_get(f"{HUB}/{project_slug}/llms.txt").decode("utf-8", "replace")
    urls = list(dict.fromkeys(_LLMS_REFERENCE_RE.findall(index)))
    if not urls or len(urls) > _MD_PAGE_LIMIT:
        raise RuntimeError(f"{project_slug}: llms.txt lists {len(urls)} reference pages; expected 1-{_MD_PAGE_LIMIT}")
    specs: list[dict[str, Any]] = []
    for i, url in enumerate(urls):
        if i:
            time.sleep(_MD_PAGE_DELAY)
        spec = _page_oas(_http_get(url).decode("utf-8", "replace"))
        if spec is not None:
            specs.append(spec)
    print(f"  {project_slug}: {len(specs)} operation(s) from {len(urls)} reference pages")
    _PAGE_SPECS[project_slug] = specs
    return specs


def _merge_specs(parts: list[dict[str, Any]]) -> dict[str, Any]:
    """One document from per-operation documents: paths and components unioned, tags kept once."""
    merged: dict[str, Any] = {k: v for k, v in parts[0].items() if k not in ("paths", "components", "tags")}
    paths: dict[str, dict[str, Any]] = {}
    components: dict[str, dict[str, Any]] = {}
    tags: dict[str, Any] = {}
    for part in parts:
        for path, operations in (part.get("paths") or {}).items():
            paths.setdefault(path, {}).update(operations)
        for kind, items in (part.get("components") or {}).items():
            components.setdefault(kind, {}).update(items)
        for tag in part.get("tags") or []:
            if isinstance(tag, dict) and tag.get("name"):
                tags.setdefault(tag["name"], tag)
    merged["paths"] = paths
    if components:
        merged["components"] = components
    if tags:
        merged["tags"] = list(tags.values())
    return merged


def _fetch_spec_via_page(project_slug: str, page_slug: str) -> dict[str, Any] | None:
    """A registry-less definition, rebuilt from every reference page that renders it.

    ``page_slug`` is the page discovery found naming the definition. The document
    its HTML embeds gives the definition's ``info.title``; every reference page
    with that title belongs to it (the docs render the registry-less definition,
    not the numbered one sharing its title), and their operations are merged.
    """
    page = _http_get(f"{HUB}/{project_slug}/reference/{page_slug}").decode("utf-8", "replace")
    own = _extract_embedded_oas(page)
    if own is None:
        return None
    title = own.get("info", {}).get("title")
    parts = [s for s in _reference_page_specs(project_slug) if s.get("info", {}).get("title") == title]
    return _merge_specs(parts or [own])


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


def collect_definitions(slug: str, specs: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Fetch every discovered definition: ``({file slug: record}, superseded slugs)``."""
    # vendored file slug -> record. Page-backed definitions SUPERSEDE
    # registry-backed ones sharing a slug: both report the same ``info.title``
    # (e.g. "Monitoring"), but the page-backed file is the one the reference docs
    # actually render and it is the newer surface. Vendoring both would
    # double-index every shared endpoint.
    collected: dict[str, dict[str, Any]] = {}
    superseded: list[str] = []
    unfetchable: list[str] = []

    for entry in sorted(specs, key=lambda e: e["via"] == "page"):  # registry first, page last
        filename, via = entry["filename"], entry["via"]
        spec = _fetch_spec(entry["uuid"]) if via == "registry" else _fetch_spec_via_page(slug, entry["page"])
        if spec is None:
            # Not skipped: an unfetchable definition would vendor a silently
            # incomplete set.
            unfetchable.append(filename)
            continue

        file_slug = _slugify(str(spec.get("info", {}).get("title", "untitled")))
        previous = collected.get(file_slug)
        if previous is not None:
            if previous["via"] == "page":
                # Two page-backed definitions claiming one slug is unexpected --
                # disambiguate rather than silently discard one.
                file_slug = f"{file_slug}-{_slugify(filename.removesuffix('.json'))}"
            else:
                print(f"  {slug}: {file_slug}: {previous['filename']} superseded by {filename}")
                superseded.append(file_slug)
        collected[file_slug] = {
            "filename": filename,
            "via": via,
            "spec": spec,
            "source": entry.get("uuid") or entry.get("page"),
        }

    if unfetchable:
        raise RuntimeError(
            f"{slug}: {len(unfetchable)} definition(s) were discovered but could not be fetched: "
            f"{sorted(unfetchable)}. Refusing to vendor a silently incomplete set."
        )

    if not collected:
        raise RuntimeError(f"{slug}: no valid OpenAPI definitions discovered")
    return collected, superseded


def vendor_definitions(
    slug: str,
    outdir: Path,
    specs: list[dict[str, Any]],
    collected: dict[str, dict[str, Any]],
    superseded: list[str],
) -> dict[str, Any]:
    """Guard against a shrunken set, then write ``collected`` and its manifest into ``outdir``."""
    outdir.mkdir(parents=True, exist_ok=True)
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

        # Per definition, too: one that lost most of its paths is a partial
        # document (a hub change, a truncated fetch), not an upstream removal.
        prev_paths = {d.get("slug"): d.get("path_count", 0) for d in prev.get("definitions", [])}
        shrunk = [
            f"{s}: {prev_paths[s]} -> {len(r['spec'].get('paths', {}))} paths"
            for s, r in sorted(collected.items())
            if prev_paths.get(s) and len(r["spec"].get("paths", {})) < _MIN_PATH_SHARE * prev_paths[s]
        ]
        if shrunk:
            raise RuntimeError(
                f"{slug}: definition(s) lost more than half their paths: {'; '.join(shrunk)}. "
                "Refusing to update; a partial document would hide live endpoints."
            )

    # Write specs; prune .json files for definitions that no longer exist.
    keep = {f"{s}.json" for s in collected} | {"_manifest.json"}
    for existing in outdir.glob("*.json"):
        if existing.name not in keep:
            existing.unlink()

    definitions = []
    total_paths = 0
    for file_slug, record in sorted(collected.items()):
        spec = record["spec"]
        _write_json(outdir / f"{file_slug}.json", spec)
        info = spec.get("info", {})
        path_count = len(spec.get("paths", {}))
        total_paths += path_count
        # Provenance (upstream filename, registry id, resolution path) goes to the
        # log, not the manifest: it can change while the spec stays byte-identical,
        # and a manifest-only change would open a sync PR for nothing.
        print(f"  {slug}: {file_slug} <- {record['filename']} via {record['via']} ({record['source']})")
        definitions.append(
            {
                "slug": file_slug,
                "title": str(info.get("title", "?")),
                "version": str(info.get("version", "?")),
                "path_count": path_count,
            }
        )

    manifest = {
        "project": slug,
        "source": f"{_README_REGISTRY}/<uuid> (discovered via {HUB}/{slug}/reference)",
        # Every current-branch definition, including those with no registry entry,
        # so the count can be checked against upstream rather than trusted.
        "branch_definition_count": len(specs),
        "definition_count": len(definitions),
        "total_paths": total_paths,
        "superseded": sorted(superseded),
        "definitions": sorted(definitions, key=lambda d: str(d["slug"])),
    }
    _write_json(outdir / "_manifest.json", manifest)

    return {"slug": slug, "definitions": len(definitions), "paths": total_paths}


def sync_project(project: dict[str, str]) -> dict[str, Any]:
    """Discover, fetch, validate and vendor one project's OAS definitions.

    Returns a summary dict. Raises on any failure that should block the run
    (no ids, zero valid definitions, or a regression in definition/path count).
    """
    slug, outdir_name = project["slug"], project["outdir"]
    specs = _discover_specs(slug)
    collected, superseded = collect_definitions(slug, specs)
    return vendor_definitions(slug, VENDOR / outdir_name, specs, collected, superseded)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Vendor the Aruba developer-hub OpenAPI documents.")
    parser.add_argument("--only", action="append", default=[], metavar="SLUG", help="sync only these project slugs")
    args = parser.parse_args(argv)
    selected = [p for p in PROJECTS if not args.only or p["slug"] in args.only]
    if args.only and len(selected) != len(set(args.only)):
        known = sorted(p["slug"] for p in PROJECTS)
        print(f"::error::unknown project slug in --only; known: {known}", file=sys.stderr)
        return 2

    failures: list[str] = []
    summaries: list[dict[str, Any]] = []
    for project in selected:
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
