"""Regenerate the Mist tool surface from the vendored OpenAPI spec.

Run from the repo root as:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

This is intended to run **at release time** by the maintainer. The
vendored spec (``vendor/mist_openapi.json``) is auto-synced daily by
``.github/workflows/sync-mist-openapi.yml``, but regeneration happens
deliberately so the maintainer can review the tool diff before tagging.

The CLI:

1. Deletes every ``.py`` file under ``platforms/mist/tools/`` (clean slate).
2. Re-generates one ``.py`` file per OpenAPI tag from the vendored spec.
3. Emits the barrel ``__init__.py`` that imports every generated module.
4. Reports a per-tag summary so the maintainer can spot drift.

After regeneration the maintainer should run the normal pre-push
checklist — ``uv run ruff check . --fix && uv run ruff format .`` —
which handles any cosmetic-style adjustments to the emitted source.
The generator emits ruff-canonical code, but final ``ruff format``
passes shake out any drift from the canonical form.

Exit code is 0 on success, non-zero on failure. Generated files should
be committed with the release.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from hpe_networking_mcp.platforms.mist._generator import generate_tool_files


def _repo_root() -> Path:
    """Find the repo root by walking up from this file until pyproject.toml is seen."""
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Could not locate repo root (no pyproject.toml found)")


def main() -> int:
    """Entry point for ``python -m hpe_networking_mcp.platforms.mist.regenerate``."""
    root = _repo_root()
    spec_path = root / "vendor" / "mist_openapi.json"
    tools_dir = root / "src" / "hpe_networking_mcp" / "platforms" / "mist" / "tools"

    if not spec_path.exists():
        print(f"ERROR: vendored spec not found at {spec_path}", file=sys.stderr)
        return 1

    print(f"Reading spec: {spec_path}")
    print(f"Output dir:   {tools_dir}")

    # Clean slate: delete the existing tools/ directory then recreate.
    if tools_dir.exists():
        shutil.rmtree(tools_dir)
    tools_dir.mkdir(parents=True, exist_ok=True)

    summary = generate_tool_files(spec_path=spec_path, output_dir=tools_dir)

    total = sum(summary.values())
    print(f"\nGenerated {total} tools across {len(summary)} modules.")

    # The generator emits ruff-canonical source directly (import ordering,
    # line wrapping, conditional ``Literal`` imports). After regeneration
    # the maintainer's normal ``uv run ruff format .`` step in the
    # pre-push checklist is sufficient — no need to spawn a subprocess
    # from this CLI just to format.
    print("\nPer-tag breakdown:")
    for slug, count in sorted(summary.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {count:4}  {slug}")

    print("\nDone. Review the diff and commit before tagging.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
