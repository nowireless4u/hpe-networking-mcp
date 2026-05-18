---
phase: 17-correlation-skill
plan: 02
subsystem: ci-tests-and-docs
tags: [ci, tests, regression, frontmatter, instructions, phase-gate]
dependency_graph:
  requires:
    - "Plan 17-01 — uxi-cross-platform-diagnostics.md authored"
    - "Phase 15 — UXI platform module + REGISTRIES entries"
  provides:
    - "CI regression coverage for uxi_* tool references in any skill"
    - "Frontmatter `platforms` assertion for the new skill"
    - "INSTRUCTIONS.md routing for UXI correlation queries"
  affects:
    - "tests/unit/test_skill_tool_references.py (regex + 3 platform tuples)"
    - "tests/unit/test_skills.py (TestBundledSkills expected set + 1 new test method)"
    - "src/hpe_networking_mcp/INSTRUCTIONS.md (skill-mapping table)"
tech_stack:
  added: []
  patterns:
    - "Tuple-append platform extension (matches PATTERNS.md guidance — minimize diff churn)"
    - "Order-sensitive tuple equality for frontmatter platforms (defense in depth beyond subset check)"
    - "Allowlist for regex-artifact prose (forbidden-tool prefixes, paste-template field labels, Docker secret names)"
key_files:
  created: []
  modified:
    - "tests/unit/test_skill_tool_references.py (regex + 3 platform-tuple extensions + 7 allowlist entries)"
    - "tests/unit/test_skills.py (expected-set extension + new test_uxi_correlation_skill_frontmatter_platforms)"
    - "src/hpe_networking_mcp/INSTRUCTIONS.md (1 new skill-mapping table row)"
decisions:
  - "Test assertion uses `health` (singular aggregator) in the tools tuple — matches Plan 01's deviation (no standalone uxi_health tool exists; reachability flows through health() / _probe_uxi). Plan text said `uxi_health` but that name does not resolve in the catalog; aligning to the actual skill prevents SKILL-05 from being self-contradictory."
  - "Pre-existing failures in tests/unit/test_uxi_write_tools.py (5 SIM117 + format drift) and tests/unit/test_skill_snippet_sandbox_compat.py (4 Windows charmap UnicodeDecodeErrors) are deferred — out of scope per executor SCOPE BOUNDARY rule (introduced by Phase 16 commits 0e94e82/7c93008 and v3.0.1.10 respectively, untouched by this plan)."
  - "`aos8_send_reset_` added to _GLOBAL_ALLOWLIST as a regex artifact — the new skill's Scope boundaries section documents it as a FORBIDDEN tool prefix (`no aos8_send_reset_*`), not a referenced tool."
metrics:
  duration_minutes: "~15"
  completed_date: "2026-05-17"
  tasks_completed: 3
  files_created: 0
  files_modified: 3
  total_lines_added: 65
  total_lines_removed: 5
---

# Phase 17 Plan 02: CI Tests + Docs Summary

Extended the skill-tool-reference regex and platform catalog to validate
`uxi_*` tool names; added a frontmatter `platforms` tuple-equality
assertion for the new skill; routed UXI correlation queries through
the INSTRUCTIONS.md skill-mapping table. SKILL-05 ("tools validated by
CI regression test" + "platforms: [uxi, central, mist, aos8] validated
by CI regression test") fully satisfied with two CI tests both green.

## Tasks

### Task 1 — Extend test_skill_tool_references.py

**File:** `tests/unit/test_skill_tool_references.py`
**Commit:** `a6e5ce5` — `test(17-02): extend tool-reference regex + catalog to cover uxi_*`

Four structural edits + 5 allowlist additions:

| Edit | Location | Before | After |
|---|---|---|---|
| A | Line 39 — `_TOOL_REF_PATTERN` | `(...|aos8)_` | `(...|aos8|uxi)_` |
| B | Line 152 — `_build_full_catalog()` platform import loop | `(..., "aos8")` | `(..., "aos8", "uxi")` |
| C | Line 191 — `tool_module_prefixes` tuple | `(..., "aos8")` | `(..., "aos8", "uxi")` |
| D | Line 207 — dynamic-mode meta-tool loop | `(..., "aos8")` | `(..., "aos8", "uxi")` |

Allowlist additions (`_GLOBAL_ALLOWLIST`):

- `uxi_client_id`, `uxi_client_secret` — Docker secret names referenced in INSTRUCTIONS.md UXI section
- `uxi_write`, `uxi_write_delete` — write-tool tag names referenced in INSTRUCTIONS.md UXI Write Tools section
- `uxi_severity` — paste-bundle field label in the new skill's Stage 1' (data field, not a tool)
- `aos8_send_reset_` — regex artifact from the new skill's Scope boundaries prose (`no aos8_send_reset_*` — a FORBIDDEN write-tool prefix, not a tool)

**Verification:** `uv run pytest tests/unit/test_skill_tool_references.py -v` → 11 passed in 4.34s; parametrized case for `uxi-cross-platform-diagnostics.md` PASSED; no regression on the 8 other skills.

**RED state captured:** Before Edits A-D the test failed on `aos8_send_reset_` (the only `uxi_*` reference the unmodified regex couldn't match — UXI references were silently passing because the regex didn't include `uxi`). After Edits A-D the `uxi_*` references became visible to the regex and resolved against the now-populated UXI catalog (11 UXI read tools + 3 UXI meta-tools).

### Task 2 — Extend test_skills.py

**File:** `tests/unit/test_skills.py`
**Commit:** `72e43f3` — `test(17-02): extend bundled-skills set + add UXI frontmatter assertion`

Two edits:

**Edit A — bundled-skills expected set extension:**

```diff
 expected = {
     "infrastructure-health-check",
     "change-pre-check",
     "wlan-sync-validation",
+    "uxi-cross-platform-diagnostics",  # Phase 17
 }
```

**Edit B — new test method** `test_uxi_correlation_skill_frontmatter_platforms` inside `TestBundledSkills`:

- Loads `SkillRegistry.from_directory()`, locates `uxi-cross-platform-diagnostics` (asserts presence with diagnostic message)
- Asserts `skill.platforms == ("uxi", "central", "mist", "aos8")` exactly (tuple equality, order-sensitive)
- Asserts `"health" in skill.tools` — UXI reachability surfaced through the unified `health()` aggregator
- Asserts `"uxi_list_sensors" in skill.tools` — SKILL-01 entry point
- Asserts `"uxi_get_sensor_status" in skill.tools` — SKILL-02 core data tool

**Verification:** `uv run pytest tests/unit/test_skills.py -v` → 33 passed in 2.48s; `pytest -k uxi tests/unit/test_skills.py` shows the new test collected and PASSED.

### Task 3 — INSTRUCTIONS.md + phase gate

**File:** `src/hpe_networking_mcp/INSTRUCTIONS.md` + `tests/unit/test_skill_tool_references.py` (line wrap follow-up)
**Commit:** `990c959` — `docs(17-02): add uxi-cross-platform-diagnostics skill-mapping row`

New row appended to the "Common skill mappings" table:

```markdown
| *"uxi sensors failing"*, *"why are my synthetic tests failing"*, *"correlate uxi failures"*, *"are my sensors healthy"*, *"uxi sensor offline"*, *"uxi service test failing"*, *"diagnose uxi"*, *"correlate uxi to central / mist / aos8"* | `uxi-cross-platform-diagnostics` |
```

8 trigger phrases — subset of the skill's `description:` trigger list — operators searching with these phrases route to the correlation skill.

Also wrapped a long comment line in `test_skill_tool_references.py` to satisfy E501 (line length 120) — the `aos8_send_reset_` allowlist comment landed as a single 142-char line in commit `a6e5ce5`.

### Phase gate outputs

| Step | Command | Outcome |
|---|---|---|
| 1 | `uv run ruff check src/hpe_networking_mcp` | All checks passed |
| 2 | `uv run ruff check tests/unit/test_skill_tool_references.py tests/unit/test_skills.py` (plan-scoped) | All checks passed |
| 3 | `uv run ruff format --check tests/unit/test_skill_tool_references.py tests/unit/test_skills.py` (plan-scoped) | 2 files already formatted |
| 4 | `uv run mypy src/hpe_networking_mcp` | exit 0 (no errors) |
| 5 | `uv run pytest tests/unit/test_skill_tool_references.py tests/unit/test_skills.py -v` | 44 passed in 6.75s |
| 6 | `uv run pytest tests/unit -q` | 1248 passed, 1 skipped, 4 failed (pre-existing — see Deferred Issues) |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 — Missing critical functionality] Plan called for `uxi_health` in the frontmatter-platforms test; aligned to `health` instead.**

- **Found during:** Task 2 authoring
- **Issue:** Plan 17-02 frontmatter spec (`<acceptance_criteria>` for Task 2 step 5) listed `"uxi_health" in skill.tools` as a required assertion. But Plan 01's SUMMARY documents that `uxi_health` does NOT exist as a tool — UXI reachability flows through the unified `health()` aggregator via `_probe_uxi` in `platforms/health.py`. The skill's `tools:` list correctly references `health` (singular), not `uxi_health`. Asserting `uxi_health` would fail because the actual skill doesn't declare it.
- **Fix:** Test asserts `"health" in skill.tools` (matches the skill); skill-mapping table left as-is in the plan's success criteria interpretation. Test docstring documents the rationale so future maintainers understand the inconsistency between Plan 17-02 text and the actual UXI surface.
- **Files modified:** `tests/unit/test_skills.py`
- **Commit:** `72e43f3`

**2. [Rule 3 — Blocking] Allowlist additions for INSTRUCTIONS.md `uxi_client_id` / `uxi_client_secret` / `uxi_write` / `uxi_write_delete`.**

- **Found during:** Task 1 verification (RED → GREEN gate)
- **Issue:** Once the regex was extended to match `uxi_*`, the `TestInstructionsToolReferences` test started failing because INSTRUCTIONS.md's UXI section legitimately mentions Docker secret names (`uxi_client_id`, `uxi_client_secret`) and write-tool tag names (`uxi_write`, `uxi_write_delete`) — none of which are tool names.
- **Fix:** Added 4 entries to `_GLOBAL_ALLOWLIST` with explanatory comments grouped under the existing "Secret names" section, matching the established pattern for `aos8_host` / `aos8_password` / `axis_api_token`.
- **Files modified:** `tests/unit/test_skill_tool_references.py`
- **Commit:** `a6e5ce5`

**3. [Rule 3 — Blocking] Allowlist additions for `uxi_severity` and `aos8_send_reset_`.**

- **Found during:** Task 1 verification (RED → GREEN gate, second iteration)
- **Issue:** The new skill's body legitimately mentions `uxi_severity` (a field label in the Stage 1' paste-bundle template — not a tool) and `aos8_send_reset_*` (the Scope boundaries section documents this as a FORBIDDEN write-tool prefix — meta-reference to forbidden tools, not a reference to an actual tool). Both are picked up by the regex but neither resolves in the tool catalog.
- **Fix:** Added both entries to `_GLOBAL_ALLOWLIST` with explanatory inline comments.
- **Files modified:** `tests/unit/test_skill_tool_references.py`
- **Commits:** `a6e5ce5` (added) + `990c959` (line-wrap fix for the comment)

### Out-of-scope items not fixed (logged as Deferred)

**1. [SCOPE BOUNDARY] Pre-existing ruff failures in `tests/unit/test_uxi_write_tools.py`.**

- 5 × SIM117 (nested `with` statements) + ruff format drift (1 file would be reformatted)
- Introduced by Phase 16 commits `0e94e82` (`feat(16-01)`) and `7c93008` (`test(16-03)`); landed before Plan 17-02 started.
- Not modified by this plan; out of scope per executor SCOPE BOUNDARY rule.

**2. [SCOPE BOUNDARY] Pre-existing Windows-runner failures in `tests/unit/test_skill_snippet_sandbox_compat.py`.**

- 4 × `UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d` — the test reads `.md` files without specifying `encoding="utf-8"`, defaulting to cp1252 on Windows.
- Pre-existing since commit `b7e1a6a` (v3.0.1.10); affects `aos-migration.md`, `central-scope-audit.md`, `wlan-sync-validation.md` and the extractor test — none of these files were modified by Plan 17-02.
- Not modified by this plan; out of scope per executor SCOPE BOUNDARY rule.

## SKILL-01 through SKILL-05 Traceability

| Requirement | Coverage |
|---|---|
| SKILL-01 — UXI sensor enumeration entry point | `test_uxi_correlation_skill_frontmatter_platforms` asserts `"uxi_list_sensors" in skill.tools`; skill body Stage 1 invokes it (Plan 01 SUMMARY) |
| SKILL-02 — Per-sensor status / issues / isOnline / isTesting | `test_uxi_correlation_skill_frontmatter_platforms` asserts `"uxi_get_sensor_status" in skill.tools`; skill body Stage 1 collects via this tool (Plan 01 SUMMARY) |
| SKILL-03 — Cross-platform correlation (networkName / groupPath / macAddress anchors) | Plan 01 skill body Stage 2 Anchors 1-4 (Plan 01 SUMMARY); `test_skill_references_resolve[uxi-cross-platform-diagnostics.md]` validates all referenced `central_*` / `mist_*` / `aos8_*` correlation tools resolve |
| SKILL-04 — GO/DEGRADED/CRITICAL verdict + REGRESSION/DRIFT/INFO findings | Plan 01 skill body Stage 3 verdict table (Plan 01 SUMMARY); structural validation via `test_bundled_skills_load_without_warnings` + non-empty body check |
| SKILL-05 — `tools:` validated by CI regression test + `platforms: [uxi, central, mist, aos8]` validated by CI regression test | Tools: `test_skill_references_resolve[uxi-cross-platform-diagnostics.md]` — every `uxi_*` / `central_*` / `mist_*` / `aos8_*` / `health` name in the skill's `tools:` list and body prose resolves to a registered tool. Platforms: `test_uxi_correlation_skill_frontmatter_platforms` — order-sensitive tuple equality with `("uxi", "central", "mist", "aos8")` |

## Known Stubs

None.

## Threat Flags

None new. T-17-08 (regex tampering) mitigation landed exactly as the threat register prescribed: `aos8\|uxi)_` is in `_TOOL_REF_PATTERN` and the grep enforcement passes. T-17-10 (subset-check spoofing) mitigation landed: the new frontmatter test uses exact tuple equality.

## Commits

| Task | Hash | Message |
|---|---|---|
| Task 1 | `a6e5ce5` | test(17-02): extend tool-reference regex + catalog to cover uxi_* |
| Task 2 | `72e43f3` | test(17-02): extend bundled-skills set + add UXI frontmatter assertion |
| Task 3 | `990c959` | docs(17-02): add uxi-cross-platform-diagnostics skill-mapping row |

## Self-Check: PASSED

- `tests/unit/test_skill_tool_references.py` — modified, contains `aos8|uxi)_` (regex) and `"uxi"` in 3 platform tuples: FOUND
- `tests/unit/test_skills.py` — modified, contains `"uxi-cross-platform-diagnostics"` 4 times (expected set + 3 assertion error messages) and `test_uxi_correlation_skill_frontmatter_platforms`: FOUND
- `src/hpe_networking_mcp/INSTRUCTIONS.md` — modified, contains new skill-mapping table row referencing `uxi-cross-platform-diagnostics`: FOUND
- Commit `a6e5ce5` exists on worktree branch: FOUND
- Commit `72e43f3` exists on worktree branch: FOUND
- Commit `990c959` exists on worktree branch: FOUND
- Targeted phase-17 tests (`test_skill_tool_references.py` + `test_skills.py`): 44 passed in 6.75s
