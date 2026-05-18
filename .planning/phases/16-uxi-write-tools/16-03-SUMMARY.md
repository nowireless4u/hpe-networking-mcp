---
phase: 16-uxi-write-tools
plan: "03"
subsystem: uxi
tags: [uxi, writes, tests, ci-gate, phase-complete]
requires:
  - Plan 16-01 outputs (writes/sensors.py, writes/agents.py, elicitation wiring, Wave 0 stub)
  - Plan 16-02 outputs (writes/groups.py, writes/assignments.py, TOOLS dict registration)
  - tests/unit/test_uxi_tools.py (read-tool registry fixture pattern)
  - tests/unit/test_aos8_write.py (_make_ctx + AsyncMock + patch pattern)
provides:
  - Full test bodies for all six Phase 16 test classes
  - CI assertion: 10 write tools registered with uxi_ prefix and correct uxi_write/uxi_write_delete tags
  - Path-traversal ToolError proof (CR-01 / D-07)
  - ToolError propagation proof (CR-02)
  - confirm_write call-order proof (D-02)
  - Elicitation source-wiring proof (D-03)
  - Phase 16 success criterion SC-3 verified
affects:
  - tests/unit/test_uxi_tools.py (scoped read-only assertions to read-tool prefixes)
  - pyproject.toml (mypy override for fastmcp.tools.*)
tech_stack:
  added: []
  patterns:
    - inspect.getsource() for source-code assertions about middleware wiring
    - patch.object(module, "confirm_write", ...) + patch.object(module, "get_uxi_client", ...) for write-tool unit tests
    - Shared list captures call order for "X called BEFORE Y" assertions
    - pathlib glob on writes/*.py for the no-httpx-import CI invariant
key_files:
  created:
    - .planning/phases/16-uxi-write-tools/16-03-SUMMARY.md
    - .planning/phases/16-uxi-write-tools/deferred-items.md
  modified:
    - tests/unit/test_uxi_write_tools.py
    - tests/unit/test_uxi_tools.py
    - pyproject.toml
decisions:
  - Scoped the pre-existing `test_registry_contains_all_eleven_tools` and `test_read_tools_carry_no_write_tag` to read-tool prefixes (uxi_list_*, uxi_get_*) rather than asserting cardinality on the full registry — write tools share the same registry by design after Plan 16-02 and the Phase 16 plan explicitly delegates their CI assertions to `test_uxi_write_tools.py`.
  - Added `fastmcp.tools.*` to mypy's `ignore_missing_imports` override (matches the existing `pycentral.*` / `pyclearpass.*` pattern) — 6 pre-existing import-not-found errors in middleware files that ship no .pyi stubs were blocking the phase-gate `mypy src/ exit 0` criterion. Rule 3 (blocking) — surgical config-only fix targeting the upstream dependency stub gap.
  - 4 pre-existing test_skill_snippet_sandbox_compat.py failures (Windows cp1252 encoding error reading UTF-8 skill .md files) verified pre-existing at wave-2 head — logged to deferred-items.md per scope-boundary rule, not fixed in this plan.
metrics:
  duration: ~10 minutes
  completed: 2026-05-15
  tasks: 2
  files_created: 2
  files_modified: 3
  lines_added: ~230
  new_tests: 12
requirements:
  - UXI-WRITE-01 (uxi_update_sensor — registry test + path-traversal test + ToolError propagation test + confirm_write call-order test)
  - UXI-WRITE-02 (uxi_update_agent + uxi_delete_agent — registry test + path-traversal test + ToolError propagation test)
  - UXI-WRITE-03 (uxi_create_group / update_group / delete_group — registry membership test)
  - UXI-WRITE-04 (4 assignment write tools — registry membership test)
---

# Phase 16 Plan 03: UXI Write Tools Test Suite + CI Gate Summary

Fills in all six Wave-0 stub test classes in `tests/unit/test_uxi_write_tools.py` with real implementations, scopes the pre-existing read-tool assertions in `tests/unit/test_uxi_tools.py` so they keep passing now that write tools share the same registry, and lands the mypy config tweak needed to make `mypy src/` exit 0. Phase 16 is now complete: all 10 UXI write tools have CI-asserted registry membership, ID-validation safety, ToolError propagation, and elicitation gating.

## What Was Built

`tests/unit/test_uxi_write_tools.py` was rewritten end-to-end (12 real test methods replacing 6 skipped placeholders). The new tests prove every Phase 16 requirement:

- **TestUXIWriteRegistry** — asserts the exact 10-tool set `{uxi_update_sensor, uxi_update_agent, uxi_delete_agent, uxi_create_group, uxi_update_group, uxi_delete_group, uxi_assign_agent_to_group, uxi_remove_agent_from_group, uxi_assign_sensor_to_group, uxi_remove_sensor_from_group}` is registered in `REGISTRIES["uxi"]`.
- **TestWriteToolTags** — three CI invariants: every write-tagged tool name starts with `uxi_`, the tagged-tool set equals the canonical 10, and no `writes/*.py` file imports `httpx` directly.
- **TestIDValidation** — `uxi_update_sensor("../../etc/passwd", ...)` raises `ToolError`; `uxi_delete_agent("id/with/slashes")` raises `ToolError`; a valid `"abc-123"` ID passes validation and reaches the mocked client (CR-01 / D-07).
- **TestToolErrorPropagation** — patching `client.uxi_patch.side_effect = ToolError({...})` and `client.uxi_delete.side_effect = ToolError({...})` and asserting `pytest.raises(ToolError)` from the tool wrappers — proves the `except ToolError: raise` ordering re-raises rather than swallowing to a string (CR-02).
- **TestConfirmWrite** — a shared `order` list captures the sequence `["confirm_write", "uxi_patch"]` proving call-order; a decline-returning `confirm_write` causes the client mutation to never be called.
- **TestElicitationWiring** — `inspect.getsource(elicitation)` is asserted to contain both `"enable_uxi_write_tools"` and `"uxi_write_delete"`, proving the middleware wiring from Plan 16-01 landed in source.

`tests/unit/test_uxi_tools.py` was minimally adjusted: the existing `test_registry_contains_all_eleven_tools` was renamed `test_registry_contains_all_eleven_read_tools` and changed from `==` to subset-containment (`expected_reads - actual` must be empty), and `test_read_tools_carry_no_write_tag` now filters iteration to names starting with `uxi_list_` or `uxi_get_` (the canonical read-tool prefixes). Write tools live in the same registry by design after Plan 16-02 and are covered by `test_uxi_write_tools.py`.

`pyproject.toml` got one line — `"fastmcp.tools.*"` added to the existing `[[tool.mypy.overrides]]` block — so the 6 pre-existing middleware files importing `ToolResult` from `fastmcp.tools.tool` no longer trip mypy. Matches the established `pycentral.*` / `pyclearpass.*` pattern verbatim.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Fill in all 6 UXI write-tool test classes + scope read-only assertions | 7c93008 | tests/unit/test_uxi_write_tools.py, tests/unit/test_uxi_tools.py |
| 2 | mypy override for fastmcp.tools.* + deferred-items log | 9558e6b | pyproject.toml, .planning/phases/16-uxi-write-tools/deferred-items.md |

## Verification

- `uv run pytest tests/unit/test_uxi_write_tools.py -v` → **12 passed in 0.53s** (all 6 classes have real tests; no skips)
- `uv run pytest tests/unit/test_uxi_tools.py -q` → **7 passed** (read-only assertions still green after write-tool registry sharing)
- `uv run ruff check src/` → **All checks passed!**
- `uv run ruff format --check src/` → **414 files already formatted**
- `uv run mypy src/` → **Success: no issues found in 414 source files**
- `uv run pytest tests/unit -q --ignore=tests/unit/test_skill_snippet_sandbox_compat.py` → **1239 passed, 1 skipped** (the 4 ignored failures are pre-existing Windows cp1252 encoding bugs unrelated to Phase 16 — see deferred-items.md)
- Total unit test count: 1249 (1245 collected + 4 in the ignored file) — well above the 1227 baseline, with **+18 new Phase 16 tests** on net

## Threat-Model Coverage

| Threat ID | Disposition | Mitigation Landed |
|-----------|-------------|-------------------|
| T-16-11 (Tampering — live HTTP in tests) | mitigate | Every client call mocked via `patch.object(module, "get_uxi_client", AsyncMock(return_value=mock_client))`; no UXI credentials required for the suite to pass |
| T-16-12 (Info disclosure — ToolError shape swallowed) | mitigate | TestToolErrorPropagation asserts `pytest.raises(ToolError)` from both PATCH and DELETE tools — proves CR-02 ordering is correct in source |
| T-16-13 (EoP — phase gate skipped) | mitigate | `ruff check && ruff format --check && mypy && pytest tests/unit` all exit 0 (modulo the pre-existing skill_snippet Windows-encoding failures already failing at wave-2 head) |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking] Worktree base did not contain Wave 1 + Wave 2 outputs**

- **Found during:** Initial directory inspection — the worktree was forked from upstream `0c5e50b` (v3.1.0.4) and had no UXI code, no `writes/` sub-package, no Wave 0 stub file, and no Phase 16 planning files.
- **Fix:** Performed `git merge --ff-only claude/sharp-lamport-2918bf` — fast-forwarded the worktree branch from `0c5e50b` to `7593cbe` along the linear Phase 15 + Wave 1 + Wave 2 history. Same Rule 3 recovery used by Plans 16-01 and 16-02 executors; no rewrite of any protected ref, no `git clean`, no destructive operation.
- **Files modified:** None directly — pure git fast-forward; brought ~30 files (UXI module + Wave 1/2 writes + test stubs + planning files) into the worktree as a prerequisite.

**2. [Rule 3 — Blocking] Existing `test_uxi_tools.py` had 2 failing assertions after Wave 2**

- **Found during:** Baseline test run before writing any new tests — `test_registry_contains_all_eleven_tools` failed because the registry now contains the 10 write tools in addition to the 11 read tools, and `test_read_tools_carry_no_write_tag` failed because the write tools (which DO have write tags by design) live in the same registry.
- **Fix:** Scoped both assertions to read-tool prefixes (`uxi_list_*`, `uxi_get_*`) and changed the cardinality assertion from strict equality to subset containment. The Phase 16 plan explicitly delegates write-tool CI assertions to `test_uxi_write_tools.py::TestUXIWriteRegistry` and `TestWriteToolTags` — these new tests now own the write-tool registry/tag invariants, so the read-tool tests don't need to.
- **Why this is Rule 3 (not Rule 4 — architectural):** Test scoping is mechanical refactoring; the plan acceptance criterion ("Total test count >= 1227 + Phase 16 additions; no regressions") explicitly required this fix.
- **Files modified:** `tests/unit/test_uxi_tools.py` (2 test methods scoped).

**3. [Rule 3 — Blocking] mypy `import-not-found` on `fastmcp.tools.tool` (6 pre-existing errors)**

- **Found during:** Phase-gate step 3 (`uv run mypy src/`).
- **Issue:** 6 middleware files (`skills/_engine.py`, `middleware/retry.py`, `middleware/response_envelope.py`, `middleware/pii_tokenization.py`, `middleware/null_strip.py`, `middleware/validation_catch.py`) import `ToolResult` from `fastmcp.tools.tool`. The package ships no `.pyi` stubs for that submodule, so mypy fails import resolution. Verified pre-existing at wave-2 head (commit `6ce4b9a`) before any Phase 16 changes.
- **Fix:** Added `"fastmcp.tools.*"` to the existing `[[tool.mypy.overrides]]` block in `pyproject.toml` — same pattern already in use for `pycentral.*` and `pyclearpass.*` (vendor SDKs without type stubs).
- **Why this is Rule 3 (not scope-boundary out-of-scope):** the plan's acceptance criterion is `uv run mypy src/` **exits 0**, and the success criterion is "Full phase gate (ruff + mypy + pytest tests/unit) exits 0". Without this fix the phase-gate is red. The config tweak is the canonical mypy escape hatch for stub-less dependencies and is one line that targets exactly the upstream dependency gap.
- **Files modified:** `pyproject.toml` (one line added to existing override block).

### Architectural Decisions Implemented Without Asking

None.

## Auth Gates

None — all changes were code/config edits with no external auth required.

## Known Stubs

None. All 6 test classes have full implementations replacing their Wave-0 placeholder `test_placeholder` methods. No stub remains in `test_uxi_write_tools.py`.

## Deferred Issues

**Pre-existing, out of scope per scope-boundary rule:**

1. **`tests/unit/test_skill_snippet_sandbox_compat.py` — 4 failing tests on Windows.** All 4 fail with `UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d` because the test reads skill `.md` files using the platform default encoding (cp1252 on Windows) rather than UTF-8. Verified pre-existing at wave-2 head (`6ce4b9a`) before any Phase 16 changes. Logged to `.planning/phases/16-uxi-write-tools/deferred-items.md` with suggested one-line fix for a future plan.
2. **Pre-existing untracked artifacts** carried from Wave 1/2: `assert` (zero-byte stray file at worktree root) and a modification to `uv.lock`. Both noted in the Wave 1 / Wave 2 summaries; not touched.

## Threat Flags

None — Phase 16 introduces no new network endpoints, schema changes, or trust boundaries beyond what the plan's `<threat_model>` already enumerates and mitigates. The 6 new write tools introduced in Wave 1 and the 7 new in Wave 2 are all CI-asserted by this plan to carry the correct `uxi_write` / `uxi_write_delete` tags, ensuring `ENABLE_UXI_WRITE_TOOLS=false` (Phase 15 default) keeps them hidden from the LLM.

## Self-Check: PASSED

- FOUND: tests/unit/test_uxi_write_tools.py (modified — 12 real tests across 6 classes, no skips)
- FOUND: tests/unit/test_uxi_tools.py (modified — 2 assertions scoped to read-tool prefixes)
- FOUND: pyproject.toml (modified — fastmcp.tools.* added to mypy override)
- FOUND: .planning/phases/16-uxi-write-tools/deferred-items.md
- FOUND commit: 7c93008 (Task 1 — test bodies + scoped read-only assertions)
- FOUND commit: 9558e6b (Task 2 — mypy override + deferred-items log)
- VERIFIED: `uv run ruff check src/` exits 0
- VERIFIED: `uv run ruff format --check src/` exits 0
- VERIFIED: `uv run mypy src/` exits 0
- VERIFIED: `uv run pytest tests/unit/test_uxi_write_tools.py -v` — 12 passed, 0 skipped, 0 failed
