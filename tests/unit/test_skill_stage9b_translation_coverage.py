"""Guard test for issue #437: every shipped ``central:*`` translation must be
represented in the aos-migration skill's Stage 9b preview section.

Stage 9b is the deterministic, engine-driven preview the operator reads to see
what the migration will emit per object. If a translation spec ships but Stage 9b
never references it, the operator can believe the preview is complete when it
silently omits that object family — exactly the bug #437 reported (the AAA chain
was omitted). This test fails when a newly-shipped ``central:*`` translation is
not wired into Stage 9b, unless it is explicitly listed in ``OUT_OF_SCOPE`` with
a documented reason.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from hpe_networking_mcp.translations import load_translations

SKILL_PATH = Path("src/hpe_networking_mcp/skills/aos-migration.md")

# Translations deliberately NOT wired into Stage 9b. Each entry MUST carry a
# reason. Empty today — every shipped central:* translation is represented.
# Add here (with justification) only if a translation is intentionally excluded
# from the deterministic preview path.
OUT_OF_SCOPE: dict[str, str] = {}


def _stage9b_section(markdown: str) -> str:
    """Return the Stage 9b section text, bounded from the ``### Stage 9b`` heading
    to the next top-level (``## ``) heading that is OUTSIDE a fenced code block.

    The Stage 9b report template embeds ``## ``-prefixed lines inside a ```` ``` ````
    fence (the sample operator report), so a naive line scan would cut the section
    short. Track fences and only treat a heading as a boundary when not fenced.
    """
    lines = markdown.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith("### Stage 9b")), None)
    assert start is not None, "skill is missing the '### Stage 9b' heading"

    in_fence = False
    end = len(lines)
    for i in range(start + 1, len(lines)):
        ln = lines[i]
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and ln.startswith("## "):
            end = i
            break
    return "\n".join(lines[start:end])


@pytest.fixture(scope="module")
def shipped_central_translations() -> set[str]:
    return {k for k in load_translations() if str(k).startswith("central:")}


@pytest.fixture(scope="module")
def stage9b_text() -> str:
    return _stage9b_section(SKILL_PATH.read_text(encoding="utf-8"))


@pytest.mark.unit
class TestStage9bTranslationCoverage:
    def test_every_shipped_translation_is_represented(
        self, shipped_central_translations: set[str], stage9b_text: str
    ) -> None:
        missing = sorted(
            tid for tid in shipped_central_translations if tid not in OUT_OF_SCOPE and tid not in stage9b_text
        )
        assert not missing, (
            f"Shipped central:* translations not represented in Stage 9b: {missing}. "
            "Wire each into the Stage 9b preview (a §2x subsection + the translation table row), "
            "or add it to OUT_OF_SCOPE with a documented reason. See issue #437."
        )

    def test_out_of_scope_entries_still_ship(self, shipped_central_translations: set[str]) -> None:
        """An OUT_OF_SCOPE entry for a translation that no longer ships is stale — remove it."""
        stale = sorted(tid for tid in OUT_OF_SCOPE if tid not in shipped_central_translations)
        assert not stale, f"OUT_OF_SCOPE lists translations that no longer ship: {stale}"

    def test_aaa_chain_present_in_dependency_order(self, stage9b_text: str) -> None:
        """Issue #437: the AAA chain must appear in execution/dependency order so the
        operator reads prerequisites before the objects that reference them."""
        chain = [
            "central:auth_server",
            "central:server_group",
            "central:aaa_profile",
        ]
        positions = [stage9b_text.find(tid) for tid in chain]
        assert all(p >= 0 for p in positions), f"AAA chain link missing from Stage 9b: {chain}"
        assert positions == sorted(positions), (
            "AAA chain must appear in dependency order in Stage 9b "
            "(auth_server -> server_group -> ... -> aaa_profile); "
            f"found positions {dict(zip(chain, positions, strict=True))}"
        )
