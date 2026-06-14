"""Unit tests for the build-time Prefab/Pyodide prewarm module.

The prewarm runs in the Dockerfile to bake the Deno + Pyodide cache into the
image layer. These tests pin its structural contract WITHOUT invoking the
sandbox (which needs the Deno binary + a multi-second cold start) — the live
render is exercised in the dev container during the build, not in unit CI.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp import prefab_prewarm

pytestmark = pytest.mark.unit


def test_warmup_program_is_a_valid_prefab_render() -> None:
    """The warmup program must build a PrefabApp (the path a real render hits)."""
    prog = prefab_prewarm._WARMUP_PROGRAM
    assert "PrefabApp" in prog
    assert "import" in prog
    # Must compile as Python — a syntax slip would silently no-op the prewarm.
    compile(prog, "<warmup>", "exec")


def test_main_is_best_effort(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() must NEVER fail the build: any sandbox error returns exit code 0."""

    def fake_run(coro: object) -> None:
        coro.close()  # type: ignore[attr-defined]  # avoid 'never awaited' warning
        raise RuntimeError("deno missing / no network")

    monkeypatch.setattr(prefab_prewarm.asyncio, "run", fake_run)
    assert prefab_prewarm.main() == 0


def test_main_returns_zero_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """The success path also returns 0 (and does not raise)."""

    def fake_run(coro: object) -> None:
        coro.close()  # type: ignore[attr-defined]

    monkeypatch.setattr(prefab_prewarm.asyncio, "run", fake_run)
    assert prefab_prewarm.main() == 0
