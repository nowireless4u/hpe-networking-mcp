"""Regression tests for the `cross-platform-rf-check` skill body.

The skill is a code-mode runbook that the in-sandbox AI follows verbatim.
Two operator-transcript failure modes have to stay fixed:

1. **Mist bare-name dispatch (issue #328 class).** The AI on Sonnet 4.6
   ran `call_tool("mist_get_self", {})` and the sandbox raised
   `Unknown tool: mist_get_self` — the spec-driven Mist tools are
   registered but NOT in the resolvable catalog by bare name; they must
   be reached via `mist_invoke_tool`. The skill must teach this pattern
   prominently AND its Step-2/4/5 examples must use it.
2. **`radioStats` shape (operator transcript, 2026-05-15).** The AI
   called `radio["radioStats"].get("channelUtilization")` and crashed
   with `'list' object has no attribute 'get'`. Central's
   `central_get_ap_details` returns `radioStats` as a single-element
   **list**, not a dict — the skill must say so plainly with the
   `[0]` indexing pattern.

These tests guard the skill body against silent drift back to the
broken phrasing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

SKILL_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "hpe_networking_mcp" / "skills" / "cross-platform-rf-check.md"
)


@pytest.fixture(scope="module")
def skill_body() -> str:
    assert SKILL_PATH.exists(), f"skill file missing at {SKILL_PATH}"
    return SKILL_PATH.read_text(encoding="utf-8")


@pytest.mark.unit
def test_skill_has_mist_dispatch_warning(skill_body: str) -> None:
    """The skill must carry a prominent Mist-dispatch warning — covering
    BOTH the correct pattern (`mist_invoke_tool`) and the wrong one
    (bare `call_tool("mist_...")` → `Unknown tool`) so the in-sandbox AI
    can't repeat the operator's mistake.
    """
    assert "mist_invoke_tool" in skill_body, (
        "skill must teach `mist_invoke_tool` as the Mist dispatch path (operator transcript 2026-05-15 / #328)"
    )
    assert "Unknown tool" in skill_body, (
        "skill must explicitly warn about the `Unknown tool` error from "
        "bare `call_tool('mist_...')` (operator transcript 2026-05-15)"
    )


@pytest.mark.unit
def test_step2_uses_mist_invoke_tool_for_get_self(skill_body: str) -> None:
    """Step 2 (Mist site resolution) must concretely show
    `mist_get_self` being dispatched via `mist_invoke_tool` to discover
    `org_id` — vague "comes from health or session context" wording is
    what led the operator's AI to invent `call_tool("mist_get_self", {})`.
    """
    # Pull the Step 2 section by slicing between its heading and the next ###.
    start = skill_body.find("### Step 2 ")
    assert start != -1, "Step 2 heading missing"
    end = skill_body.find("### Step 3 ", start)
    assert end != -1, "Step 3 heading missing (used to bound Step 2)"
    step2 = skill_body[start:end]

    assert "mist_invoke_tool" in step2, "Step 2 must dispatch via `mist_invoke_tool`"
    assert "mist_get_self" in step2, "Step 2 must name `mist_get_self` as the org_id source"
    # And the wiring must be the dispatch shape, not the bare-name shape.
    assert 'name": "mist_get_self"' in step2 or "name='mist_get_self'" in step2 or 'name="mist_get_self"' in step2, (
        "Step 2 must show the `mist_invoke_tool(name='mist_get_self', ...)` shape concretely"
    )


@pytest.mark.unit
def test_steps_4_and_5_use_mist_invoke_tool(skill_body: str) -> None:
    """Steps 4 and 5 (Mist per-AP stats / channel-planning template) must
    also dispatch via `mist_invoke_tool` — every Mist tool in this skill
    is spec-driven and bare-name dispatch fails.
    """
    for step_name in ("### Step 4 ", "### Step 5 "):
        start = skill_body.find(step_name)
        assert start != -1, f"{step_name} heading missing"
        # Next ### heading bounds the section.
        end = skill_body.find("\n### ", start + 1)
        assert end != -1, f"closing boundary for {step_name} missing"
        section = skill_body[start:end]
        assert "mist_invoke_tool" in section, (
            f"{step_name.strip()} must dispatch its Mist tool via `mist_invoke_tool` (#328)"
        )


@pytest.mark.unit
def test_radiostats_documented_as_list(skill_body: str) -> None:
    """`radioStats` on Central's `central_get_ap_details` is a
    single-element **list**, not a dict. The skill must say so plainly
    AND show the `radioStats[0]` indexing pattern, so the in-sandbox AI
    can't repeat `radio['radioStats'].get(...)` and crash with
    `'list' object has no attribute 'get'`.
    """
    body_lower = skill_body.lower()
    assert "radiostats" in body_lower, "radioStats must be documented (Central response shape)"
    # The word "list" must appear in the same neighborhood as radioStats.
    # Look for "radioStats" within 400 chars of "list" (or vice versa), one direction.
    idx = body_lower.find("radiostats")
    nearby_window = skill_body[max(0, idx - 50) : idx + 600]
    assert "list" in nearby_window.lower(), (
        "skill must call out `radioStats` as a LIST near where it's first introduced"
    )
    # The corrective indexing pattern must appear verbatim.
    assert 'radioStats"][0]' in skill_body or "radioStats'][0]" in skill_body or "radioStats[0]" in skill_body, (
        "skill must show the `radioStats[0]` indexing pattern (operator transcript 2026-05-15)"
    )
    # And the specific error string must be quoted so the AI recognizes it.
    assert "'list' object has no attribute 'get'" in skill_body, (
        "skill must quote the exact error string "
        "(`'list' object has no attribute 'get'`) so the AI recognizes the symptom"
    )


@pytest.mark.unit
def test_frontmatter_tools_list_includes_dispatch_and_get_self(skill_body: str) -> None:
    """The skill's frontmatter `tools:` allowlist must include
    `mist_invoke_tool` (the dispatch wrapper) and `mist_get_self`
    (newly referenced in Step 2 for org_id discovery).
    """
    # Frontmatter is the leading --- ... --- block.
    assert skill_body.startswith("---\n"), "frontmatter must lead the file"
    end = skill_body.find("\n---\n", 4)
    assert end != -1, "closing frontmatter --- missing"
    frontmatter = skill_body[: end + 5]
    for required in ("mist_invoke_tool", "mist_get_self"):
        assert required in frontmatter, f"frontmatter `tools:` allowlist must include `{required}`"
