---
phase: 16-uxi-write-tools
plan: "01"
subsystem: uxi
tags: [uxi, writes, elicitation, foundational]
requires:
  - claude/modest-booth-acfc9f branch tip (d74c838 — CR-01 sensor_id guard + CR-02 ToolError propagation)
  - config.enable_uxi_write_tools (Phase 15)
  - middleware.elicitation.confirm_write
  - platforms.uxi.client.uxi_patch / uxi_delete / get_uxi_client / format_http_error
  - platforms.uxi.tools.{WRITE, WRITE_DELETE}
  - platforms.uxi._registry.tool
provides:
  - platforms.uxi.tools.writes sub-package
  - uxi_update_sensor (PATCH /sensors/{id})
  - uxi_update_agent (PATCH /agents/{id})
  - uxi_delete_agent (DELETE /agents/{id})
  - elicitation.any_write includes uxi_write + enable block fires {uxi_write, uxi_write_delete}
  - tests/unit/test_uxi_write_tools.py (six Wave 0 stub classes)
affects:
  - middleware/elicitation.py
tech_stack:
  added: []
  patterns:
    - sparse PATCH body (skip None fields)
    - regex ID validation re.compile(r'^[A-Za-z0-9_-]{1,128}$') before URL interpolation
    - confirm_write elicitation BEFORE mutation
    - "except ToolError: raise" precedes "except Exception" (CR-02)
    - empty-body no_op short-circuit BEFORE confirm_write (avoids confirming a non-update)
    - pcap_mode enum guard (light/full/off) BEFORE body construction
key_files:
  created:
    - src/hpe_networking_mcp/platforms/uxi/tools/writes/__init__.py
    - src/hpe_networking_mcp/platforms/uxi/tools/writes/sensors.py
    - src/hpe_networking_mcp/platforms/uxi/tools/writes/agents.py
    - tests/unit/test_uxi_write_tools.py
    - .planning/phases/16-uxi-write-tools/16-01-SUMMARY.md
  modified:
    - src/hpe_networking_mcp/middleware/elicitation.py
decisions:
  - Used regex `^[A-Za-z0-9_-]{1,128}$` (D-07 stricter form) over inline slash-check; defined per-module (writes self-contained, do not import from read tools)
  - pcap_mode enum validated client-side BEFORE body build to give a clear ToolError(400) instead of forwarding an opaque 422 from the API (resolves Open Question 2)
  - Empty-body guard returns `{"status": "no_op", ...}` BEFORE calling confirm_write (avoids prompting for a non-update)
  - Worktree base was upstream v3.1.0.4 (0c5e50b) with no UXI code; fast-forward merged claude/modest-booth-acfc9f to satisfy plan pre-condition (Rule 3 — blocking issue auto-fix; non-destructive linear merge)
metrics:
  duration: ~5 minutes
  completed: 2026-05-15
  tasks: 3
  files_created: 5
  files_modified: 1
  lines_added: ~290
requirements:
  - UXI-WRITE-01 (uxi_update_sensor — partial; full registry test in 16-03)
  - UXI-WRITE-02 (uxi_update_agent + uxi_delete_agent — partial; full registry test in 16-03)
---

# Phase 16 Plan 01: UXI Write Tools Foundation Summary

PATCH/DELETE skeleton for UXI sensors and agents with elicitation-gated mutations, regex ID validation, and ToolError propagation; elicitation middleware now recognizes UXI as a write platform.

## What Was Built

Three foundational write tools (`uxi_update_sensor`, `uxi_update_agent`, `uxi_delete_agent`), the `writes/` sub-package skeleton, the elicitation middleware extension to honor `enable_uxi_write_tools`, and a Wave 0 test stub file with six pytest-collectable class skeletons. The plan establishes every pattern that subsequent UXI write-tool plans (16-02 groups+assignments, 16-03 tests+CI) will copy verbatim — sparse PATCH body construction, ID regex guard, pre-elicitation empty-body short-circuit, pcap_mode enum validation, `except ToolError: raise` ordering, and the camelCase API field mapping (`pcap_mode` → `pcapMode`).

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | writes/ sub-package skeleton + branch pre-condition verification | bf2bd3c | src/hpe_networking_mcp/platforms/uxi/tools/writes/__init__.py |
| 2 | writes/sensors.py + writes/agents.py (3 tools) | 04f9ec8 | src/hpe_networking_mcp/platforms/uxi/tools/writes/sensors.py, src/hpe_networking_mcp/platforms/uxi/tools/writes/agents.py |
| 3 | elicitation.py UXI wiring + Wave 0 test stub | 0e94e82 | src/hpe_networking_mcp/middleware/elicitation.py, tests/unit/test_uxi_write_tools.py |

## Verification

- `uv run python -c "from hpe_networking_mcp.platforms.uxi.tools.writes.sensors import uxi_update_sensor; from hpe_networking_mcp.platforms.uxi.tools.writes.agents import uxi_update_agent, uxi_delete_agent; print('OK')"` → exit 0, prints `OK`
- `uv run pytest tests/unit/test_uxi_write_tools.py --collect-only -q` → 6 tests collected (all six stub classes import-clean and pytest-collectable)
- `uv run ruff check src/hpe_networking_mcp/platforms/uxi/tools/writes/ src/hpe_networking_mcp/middleware/elicitation.py` → All checks passed
- `grep -c 'uxi_write = config.enable_uxi_write_tools' src/hpe_networking_mcp/middleware/elicitation.py` → 1
- `grep -c 'or uxi_write' src/hpe_networking_mcp/middleware/elicitation.py` → 1

## Threat-Model Coverage

| Threat ID | Disposition | Mitigation Landed |
|-----------|-------------|-------------------|
| T-16-01 (Tampering — sensor_id/agent_id URL interpolation) | mitigate | `_validate_id()` with regex `^[A-Za-z0-9_-]{1,128}$` before every URL build; raises `ToolError(400)` |
| T-16-02 (EoP — write-tool surface gating) | mitigate (inherited from Phase 15 + this plan's elicitation wiring) | `enable_uxi_write_tools` defaults False; `any_write` now includes uxi; `enable_components` fires for `{uxi_write, uxi_write_delete}` |
| T-16-03 (Repudiation — silent mutations) | mitigate | `confirm_write(ctx, ...)` called BEFORE every mutation in all three tools |
| T-16-04 (Info disclosure — ToolError swallowed) | mitigate | `except ToolError: raise` placed BEFORE `except Exception` in every try block |
| T-16-05 (Tampering — empty PATCH no-op) | mitigate | Pre-elicitation empty-body guard returns `{"status": "no_op", ...}` |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking] Worktree base did not contain Phase 15 UXI code or d74c838**

- **Found during:** Task 1 pre-condition check
- **Issue:** The worktree was reset to upstream v3.1.0.4 (0c5e50b) by the orchestrator's worktree branch check. Plan 16-01's Task 1 explicitly requires d74c838 to be on the branch and `platforms/uxi/tools/sensors.py` to contain the CR-01 guard. Neither was present (no UXI directory existed at all).
- **Fix:** Performed `git merge --ff-only claude/modest-booth-acfc9f`, which fast-forwarded the worktree branch from `0c5e50b` to `d74c838` along the linear Phase 15 history (no rewrite of any protected ref; no clean; pure forward merge). After the merge, d74c838 was on HEAD, the UXI directory existed, and `sensors.py` contained the CR-01 guard.
- **Why this is Rule 3 (not Rule 4 — architectural):** The branch base selection is mechanical, not architectural. The plan explicitly names `claude/modest-booth-acfc9f` as the required base; the orchestrator simply did not seed the worktree from there. Fast-forwarding to the named base is the canonical recovery, not a design change.
- **Files modified:** None directly — operation was a pure git fast-forward; brought 19 Phase 15 files into the worktree as a prerequisite.

### Architectural Decisions Implemented Without Asking

None.

## Auth Gates

None — all changes were pure code edits; no external auth required.

## Known Stubs

The new test file `tests/unit/test_uxi_write_tools.py` contains six pytest-skipped placeholder methods (`test_placeholder` in each class). These are **intentional** Wave 0 stubs called out in the plan's must_haves block: "Wave 0 test stubs — all test classes importable, Phase 16 tests can be run." Real test bodies land in Plan 16-03 per the Phase 16 wave plan.

## Deferred Issues

None — all three tasks completed cleanly with all acceptance criteria met.

## Threat Flags

None — no new security-relevant surface introduced beyond what the plan's `<threat_model>` already enumerates and mitigates.

## Self-Check: PASSED

- FOUND: src/hpe_networking_mcp/platforms/uxi/tools/writes/__init__.py
- FOUND: src/hpe_networking_mcp/platforms/uxi/tools/writes/sensors.py
- FOUND: src/hpe_networking_mcp/platforms/uxi/tools/writes/agents.py
- FOUND: tests/unit/test_uxi_write_tools.py
- FOUND: src/hpe_networking_mcp/middleware/elicitation.py (modified — verified by grep)
- FOUND commit: bf2bd3c (Task 1 — writes/ skeleton)
- FOUND commit: 04f9ec8 (Task 2 — sensors.py + agents.py)
- FOUND commit: 0e94e82 (Task 3 — elicitation wiring + test stub)
