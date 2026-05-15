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


# --- Issue #342: user-stated platform scope must override the runbook default ---


@pytest.mark.unit
def test_step0_user_scope_exists(skill_body: str) -> None:
    """Step 0 (platform scope detection from the user's request) must
    exist at the top of the Procedure section. INSTRUCTIONS.md guidance
    cannot enforce this (untrusted in AI-client view); only the loaded
    skill body can. The transcript showed the AI saying "I'll still check
    both platforms per the runbook" after the user named one — the runbook
    must remove that out by establishing scope as Step 0 (#342).
    """
    # Step 0 must precede Step 1 in the Procedure.
    step0_idx = skill_body.find("### Step 0 ")
    step1_idx = skill_body.find("### Step 1 ")
    assert step0_idx != -1, "Step 0 (platform scope) missing — required for #342"
    assert step1_idx != -1, "Step 1 missing"
    assert step0_idx < step1_idx, "Step 0 must come before Step 1 in the Procedure"


@pytest.mark.unit
def test_step0_captures_user_scope_with_keywords(skill_body: str) -> None:
    """Step 0 must explicitly name the scope keywords ("in Mist", "in
    Central") so the AI knows what user language to recognize, and it
    must capture a `user_scope` list for downstream gating.
    """
    start = skill_body.find("### Step 0 ")
    end = skill_body.find("### Step 1 ", start)
    assert start != -1 and end != -1, "Step 0 / Step 1 headings missing"
    step0 = skill_body[start:end]

    assert "user_scope" in step0, "Step 0 must capture a `user_scope` variable"
    # The scope keywords the AI has to recognize.
    for keyword in ('"in Mist"', '"in Central"'):
        assert keyword in step0, f"Step 0 must name the {keyword} scope keyword"
    # The override directive — explicit, since the transcript showed the AI
    # deferring to the runbook over the user's constraint.
    assert "authoritative" in step0.lower() or "override" in step0.lower(), (
        "Step 0 must state that user scope is authoritative / overrides the runbook default (#342)"
    )
    # And the specific anti-pattern the operator's AI hit, quoted so it's recognizable.
    assert "still check both per the runbook" in step0, (
        "Step 0 must explicitly call out the 'still check both per the runbook' anti-pattern from the transcript (#342)"
    )


@pytest.mark.unit
def test_mist_steps_gate_on_user_scope(skill_body: str) -> None:
    """Step 2 (the Mist entry point) must gate its `Skip if` on
    `"mist" not in user_scope` so the Mist branch skips when the user
    scoped to Central. Steps 4 and 5 cascade off Step 2 and inherit the
    skip naturally — they don't need to repeat the gate.
    """
    start = skill_body.find("### Step 2 ")
    end = skill_body.find("### Step 3 ", start)
    assert start != -1 and end != -1, "Step 2 / Step 3 headings missing"
    step2 = skill_body[start:end]
    assert '"mist" not in user_scope' in step2, (
        'Step 2 must skip when `"mist" not in user_scope` — gate the Mist branch on user_scope (#342)'
    )


@pytest.mark.unit
def test_central_steps_gate_on_user_scope(skill_body: str) -> None:
    """Step 3 (the Central entry point) must gate its `Skip if` on
    `"central" not in user_scope` so the Central branch skips when the
    user scoped to Mist. Step 6 cascades off Step 3 and inherits the skip.
    """
    start = skill_body.find("### Step 3 ")
    end = skill_body.find("### Step 4 ", start)
    assert start != -1 and end != -1, "Step 3 / Step 4 headings missing"
    step3 = skill_body[start:end]
    assert '"central" not in user_scope' in step3, (
        'Step 3 must skip when `"central" not in user_scope` — gate the Central branch on user_scope (#342)'
    )


@pytest.mark.unit
def test_decision_matrix_has_user_scoped_rows(skill_body: str) -> None:
    """The Decision matrix must include explicit rows for user-scoped
    runs so the AI sees that single-platform-by-user-request is a
    supported, first-class shape — not a deviation from the runbook.
    """
    start = skill_body.find("## Decision matrix")
    assert start != -1, "Decision matrix section missing"
    end = skill_body.find("\n## ", start + 1)
    matrix = skill_body[start : end if end != -1 else len(skill_body)]
    # Each scope-to-one-platform row must appear.
    assert "User scoped to Mist only" in matrix, "Decision matrix must carry a 'User scoped to Mist only' row (#342)"
    assert "User scoped to Central only" in matrix, (
        "Decision matrix must carry a 'User scoped to Central only' row (#342)"
    )


@pytest.mark.unit
def test_output_format_surfaces_user_scope_in_headline(skill_body: str) -> None:
    """Step 8 / Output formatting must instruct the AI to surface the
    user-requested scope in the report headline so the operator can see
    the run honored their constraint.
    """
    fmt_start = skill_body.find("## Output formatting")
    assert fmt_start != -1, "Output formatting section missing"
    fmt_end = skill_body.find("\n## ", fmt_start + 1)
    fmt = skill_body[fmt_start : fmt_end if fmt_end != -1 else len(skill_body)]
    assert "scope: user-requested" in fmt, (
        "Output formatting must instruct the AI to print `(scope: user-requested <platform>)` "
        "in the report headline when user_scope covered one platform (#342)"
    )
