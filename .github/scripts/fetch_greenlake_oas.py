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

PORTAL = "https://developer.greenlake.hpe.com"
LLMS_URL = f"{PORTAL}/llms.txt"
VENDOR_DIR = Path(__file__).resolve().parents[2] / "vendor" / "greenlake"
SOURCES = VENDOR_DIR / "sources.json"
_UA = "hpe-networking-mcp greenlake-oas-sync"
_TIMEOUT = 60


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
            out = VENDOR_DIR / s["file"]
            out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"ok   {s['file']} ({len(doc['paths'])} paths)")
        except Exception as exc:  # noqa: BLE001
            failures.append((s["file"], str(exc)))
            print(f"FAIL {s['file']}: {exc}")
    return failures


def _drift_warnings(known_services: set[str]) -> None:
    """Warn about services with a real (non-changelog) spec page not yet vendored."""
    try:
        llms = _http_get(LLMS_URL).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        print(f"::warning::llms.txt drift check skipped: {exc}")
        return
    real: set[str] = set()
    for m in re.finditer(r"/services/([a-z0-9-]+)/public/openapi/([^)\s]+)", llms):
        page = m.group(2)
        if "changelog" not in page and "getting-help" not in page:
            real.add(m.group(1))
    for svc in sorted(real - known_services):
        print(f"::warning::New GreenLake service on portal not in sources.json: {svc}")


def main() -> int:
    manifest = json.loads(SOURCES.read_text(encoding="utf-8"))
    specs = manifest["specs"]
    failures = _fetch_specs(specs)
    _drift_warnings({s["service"] for s in specs})
    if failures:
        print(f"::error::{len(failures)} GreenLake spec(s) failed to sync", file=sys.stderr)
        return 1
    print(f"synced {len(specs)} specs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
