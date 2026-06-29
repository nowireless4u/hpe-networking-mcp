"""Guard that every Generative-UI skill teaches the safe render contract (#531).

Skills that render via ``generate_prefab_ui`` must, for small/local models:
1. call it as a TOP-LEVEL tool (not from inside an ``execute()`` block),
2. describe a no-Generative-UI fallback (it no-ops in non-apps clients), and
3. mandate a text summary regardless of whether the widget renders.

Discovered dynamically (any skill referencing ``generate_prefab_ui``) so a new
Generative-UI skill is covered automatically.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_SKILLS = Path("src/hpe_networking_mcp/skills")

pytestmark = pytest.mark.unit


def _genui_skills() -> list[str]:
    out: list[str] = []
    for p in sorted(_SKILLS.glob("*.md")):
        if p.name == "TEMPLATE.md":
            continue
        if "generate_prefab_ui" in p.read_text(encoding="utf-8"):
            out.append(p.name)
    return out


_GENUI = _genui_skills()

_FALLBACK_KEYWORDS = ("fallback", "no-op", "isn't available", "not available", "unavailable")
_TEXT_SUMMARY_KEYWORDS = ("text summary", "walkthrough", "markdown summary", "regardless of render", "always emit")


def test_discovery_finds_known_genui_skills() -> None:
    """Guard the guard: the parametrized checks can't degrade to a vacuous pass."""
    assert {"central-site-dashboard.md", "central-ucc-quality.md"}.issubset(_GENUI), _GENUI


@pytest.mark.parametrize("name", _GENUI)
def test_top_level_call_reminder(name: str) -> None:
    text = (_SKILLS / name).read_text(encoding="utf-8").lower()
    assert "top-level" in text, (
        f"{name}: must state generate_prefab_ui is a TOP-LEVEL tool (not called from inside execute())."
    )


@pytest.mark.parametrize("name", _GENUI)
def test_no_tool_fallback_described(name: str) -> None:
    text = (_SKILLS / name).read_text(encoding="utf-8").lower()
    assert any(k in text for k in _FALLBACK_KEYWORDS), (
        f"{name}: must describe a no-Generative-UI fallback (the tool no-ops in non-apps clients)."
    )


@pytest.mark.parametrize("name", _GENUI)
def test_mandatory_text_summary(name: str) -> None:
    text = (_SKILLS / name).read_text(encoding="utf-8").lower()
    assert any(k in text for k in _TEXT_SUMMARY_KEYWORDS), (
        f"{name}: must mandate a text summary regardless of whether the widget renders."
    )
