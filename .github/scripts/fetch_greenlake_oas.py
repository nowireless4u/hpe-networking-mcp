#!/usr/bin/env python3
"""Sync HPE GreenLake public northbound OpenAPI specs into ``vendor/greenlake/``.

Driven by ``vendor/greenlake/sources.json`` — a curated manifest of verified
``_bundle/...json?download`` URLs. The portal (developer.greenlake.hpe.com) is a
Redocly SPA whose spec index is ``/llms.txt``; the raw bundle files **preserve
source casing** (``openApi.json`` / ``openapiBeta.json`` / ``@v1``) while the
``llms.txt`` doc paths are lowercased, so URLs cannot be derived by string
transform — they are pinned (and human-verified) in ``sources.json``.

Each spec is fetched, validated as OpenAPI with >= 1 path, and written with
sorted keys for stable diffs. The script also diffs the live ``llms.txt``
against ``sources.json`` and prints a GitHub ``::warning::`` for any
newly-published service missing from the manifest.

Exit code is non-zero on any download/parse failure so the workflow's
issue-on-failure step fires and no bad snapshot is committed. Tool regeneration
is intentionally NOT run here — the maintainer regenerates the GreenLake tool
surface at release time so changes are reviewed before tagging.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

PORTAL = "https://developer.greenlake.hpe.com"
LLMS_URL = f"{PORTAL}/llms.txt"
VENDOR_DIR = Path(__file__).resolve().parents[2] / "vendor" / "greenlake"
SOURCES = VENDOR_DIR / "sources.json"
_UA = "hpe-networking-mcp greenlake-oas-sync"
_TIMEOUT = 60

# A public northbound spec lives on the GreenLake gateway. The portal occasionally
# serves INTERNAL/UI specs under a /public/ URL (servers on *.ccs.arubathena.com,
# paths like /auditlogs/ui/v1/*) — see issue #636. Two guards:
#   * internal PATH prefixes (/ui/) mean the spec is the wrong, non-public one and
#     its generated tools will 404 on the gateway → HARD FAIL the sync.
#   * non-public SERVER hosts are cosmetic (our runtime ignores the spec's servers
#     and uses the configured base_url), so we warn + normalize them to the gateway.
_PUBLIC_HOST = "global.api.greenlake.hpe.com"
_INTERNAL_PATH_RE = re.compile(r"/ui/")


def _is_public_server(url: str) -> bool:
    # Any HPE production host is public (greenlake.hpe.com, data.cloud.hpe.com,
    # common.cloud.hpe.com, …). Internal hosts (arubathena.com, localhost, bare
    # IPs) are not — those are the ones worth normalizing away.
    host = urlparse(url).hostname or ""
    return host.endswith(".hpe.com")


def _validate_and_canonicalize(file: str, doc: dict) -> None:
    """Reject internal/UI specs; normalize non-public server hosts to the gateway."""
    ui_paths = [p for p in doc.get("paths", {}) if _INTERNAL_PATH_RE.search(p)]
    if ui_paths:
        raise ValueError(
            f"internal/UI paths (not a public API): {ui_paths[:3]} — the pinned URL is the "
            "wrong spec; find the public bundle for this service (see issue #636)"
        )
    servers = doc.get("servers") or []
    if servers and not all(_is_public_server(s.get("url", "")) for s in servers):
        hosts = [s.get("url") for s in servers]
        print(f"::warning::{file}: non-public server host(s) {hosts}; normalizing to {_PUBLIC_HOST}")
        doc["servers"] = [{"url": f"https://{_PUBLIC_HOST}"}]


def _http_get(url: str) -> bytes:
    last: Exception | None = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310 (trusted host)
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last = exc
            time.sleep(2 * (attempt + 1))
    assert last is not None
    raise last


def _fetch_specs(specs: list[dict]) -> list[tuple[str, str]]:
    """Download + validate + canonicalize each spec. Returns list of failures."""
    failures: list[tuple[str, str]] = []
    for s in specs:
        try:
            doc = json.loads(_http_get(s["url"]))
            if not (doc.get("openapi") and doc.get("paths")):
                raise ValueError("response is not an OpenAPI document with paths")
            _validate_and_canonicalize(s["file"], doc)
            out = VENDOR_DIR / s["file"]
            out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"ok   {s['file']} ({len(doc['paths'])} paths)")
        except Exception as exc:  # noqa: BLE001
            failures.append((s["file"], str(exc)))
            print(f"FAIL {s['file']}: {exc}")
    return failures


def _new_service_warnings(known_services: set[str], llms: str) -> None:
    """Warn about services with a real (non-changelog) spec page not yet vendored."""
    real: set[str] = set()
    for m in re.finditer(r"/services/([a-z0-9-]+)/public/openapi/([^)\s]+)", llms):
        page = m.group(2)
        if "changelog" not in page and "getting-help" not in page:
            real.add(m.group(1))
    for svc in sorted(real - known_services):
        print(f"::warning::New GreenLake service on portal not in sources.json: {svc}")


def _ver_rank(name: str) -> tuple[int, int, int]:
    """Rank a version token so newer sorts higher. GA > beta > alpha within a major."""
    m = re.search(r"v(\d+)(alpha|beta)?(\d+)?", name)
    if not m:
        return (0, 0, 0)
    stab = {"alpha": 0, "beta": 1, None: 2}[m.group(2)]
    return (int(m.group(1)), stab, int(m.group(3) or 0))


def _version_drift_warnings(specs: list[dict], llms: str) -> None:
    """Warn when a pinned spec has a newer version published on the portal (issue #636).

    The portal has no auto-latest bundle — every URL pins an explicit version — so a
    service that ships a newer spec silently goes stale. This parses llms.txt for each
    service's published spec pages and flags any pin whose version is behind the newest
    sibling (same filename family, ignoring version tokens). Informational only.
    """
    pages: dict[str, list[str]] = {}
    for m in re.finditer(r"/services/([a-z0-9-]+)/public/openapi/(\S+?)\.md", llms):
        svc, page = m.group(1), m.group(2)
        if page.count("/") == 0 or any(x in page for x in ("changelog", "guide", "getting-help")):
            continue
        pages.setdefault(svc, []).append(page.split("/")[-1])

    def family(name: str) -> str:
        return re.sub(r"[-_@]?v\d[a-z0-9]*", "", name).lower()

    for s in specs:
        m = re.search(r"/([^/]+)\.json", s["url"])
        cur = m.group(1) if m else ""
        siblings = [p for p in pages.get(s["service"], []) if family(p) == family(cur)]
        if not siblings:
            continue
        newest = max(siblings, key=_ver_rank)
        if _ver_rank(newest) > _ver_rank(cur):
            print(
                f"::warning::{s['service']}/{s['file']}: pinned '{cur}' is behind "
                f"newer published spec '{newest}' — consider re-pinning (issue #636)"
            )


def main() -> int:
    manifest = json.loads(SOURCES.read_text(encoding="utf-8"))
    specs = manifest["specs"]
    failures = _fetch_specs(specs)
    try:
        llms = _http_get(LLMS_URL).decode("utf-8", "replace")
        _new_service_warnings({s["service"] for s in specs}, llms)
        _version_drift_warnings(specs, llms)
    except Exception as exc:  # noqa: BLE001
        print(f"::warning::llms.txt drift checks skipped: {exc}")
    if failures:
        print(f"::error::{len(failures)} GreenLake spec(s) failed to sync", file=sys.stderr)
        return 1
    print(f"synced {len(specs)} specs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
