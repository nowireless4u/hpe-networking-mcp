---
phase: 16-uxi-write-tools
plan: "02"
subsystem: uxi
tags: [uxi, writes, groups, assignments, registration]
requires:
  - Plan 16-01 outputs (writes/__init__.py, writes/sensors.py, writes/agents.py)
  - platforms.uxi.client.uxi_post / uxi_patch / uxi_delete
  - platforms.uxi.tools.{WRITE, WRITE_DELETE}
  - middleware.elicitation.confirm_write
  - platforms.uxi._registry.tool
provides:
  - uxi_create_group (POST /groups)
  - uxi_update_group (PATCH /groups/{id})
  - uxi_delete_group (DELETE /groups/{id})
  - uxi_assign_agent_to_group (POST /agent-group-assignments)
  - uxi_remove_agent_from_group (DELETE /agent-group-assignments/{id})
  - uxi_assign_sensor_to_group (POST /sensor-group-assignments)
  - uxi_remove_sensor_from_group (DELETE /sensor-group-assignments/{id})
  - TOOLS dict entries: writes.sensors, writes.agents, writes.groups, writes.assignments
affects:
  - src/hpe_networking_mcp/platforms/uxi/__init__.py
tech_stack:
  added: []
  patterns:
    - Reuse of Plan 16-01 write-tool pattern verbatim (regex ID guard, confirm_write, ToolError-first except)
    - camelCase API field mapping (parentId, agentId, sensorId, groupId)
    - Assignment DELETE uses assignment record ID (NOT resource ID) — documented in docstring per T-16-08 acceptance
    - importlib dotted-key resolution: "writes.groups" -> tools/writes/groups.py
key_files:
  created:
    - src/hpe_networking_mcp/platforms/uxi/tools/writes/groups.py
    - src/hpe_networking_mcp/platforms/uxi/tools/writes/assignments.py
    - .planning/phases/16-uxi-write-tools/16-02-SUMMARY.md
  modified:
    - src/hpe_networking_mcp/platforms/uxi/__init__.py
decisions:
  - groups.py uses POST/PATCH/DELETE pattern combined; ~120 lines (well under 500)
  - assignments.py keeps all 4 tools in one file (~165 lines); the planner explicitly waived the split criterion since the file is well under the 500-line limit
  - parent_id is validated only when provided (it is optional in POST /groups); name is NOT validated as an ID since it is a free-form label, not a URL path component
  - Worktree base did not include Wave 1 outputs; fast-forwarded to orchestrator HEAD 466c2bb to seed the writes/ pattern files (same Rule 3 recovery used in 16-01)
metrics:
  duration: ~5 minutes
  completed: 2026-05-15
  tasks: 3
  files_created: 2
  files_modified: 1
  lines_added: ~292
requirements:
  - UXI-WRITE-03 (uxi_create_group, uxi_update_group, uxi_delete_group — implementation complete; full registry test in 16-03)
  - UXI-WRITE-04 (4 assignment write tools — implementation complete; full registry test in 16-03)
---

# Phase 16 Plan 02: UXI Group + Assignment Write Tools Summary

Adds the remaining 7 UXI write tools (3 group lifecycle + 4 assignment management) and registers all 10 Phase 16 write tools in the TOOLS dict so importlib-based registration discovers them at server startup.

## What Was Built

`writes/groups.py` (3 tools — create/update/delete a group), `writes/assignments.py` (4 tools — assign/remove agent and sensor to/from groups), and a 4-entry addition to the TOOLS dict in `platforms/uxi/__init__.py`. All 7 new tools follow the Plan 16-01 pattern verbatim — `_validate_id` regex guard for every URL-interpolated ID, `confirm_write` elicitation before every mutation, and the `except ToolError: raise` ordering ahead of the broad `Exception` catch for CR-02 propagation. POST bodies use the camelCase field names verified in 16-RESEARCH.md (`parentId`, `agentId`, `sensorId`, `groupId`). The 4 remove tools take an `assignment_id` (assignment record ID) rather than the agent/sensor/group ID, with the distinction called out in the docstring per the T-16-08 mitigation plan.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | writes/groups.py — uxi_create_group, uxi_update_group, uxi_delete_group | 9f59297 | src/hpe_networking_mcp/platforms/uxi/tools/writes/groups.py |
| 2 | writes/assignments.py — 4 agent/sensor assignment write tools | 5a452b6 | src/hpe_networking_mcp/platforms/uxi/tools/writes/assignments.py |
| 3 | Register all 10 Phase 16 write tools in TOOLS dict | 6ce4b9a | src/hpe_networking_mcp/platforms/uxi/__init__.py |

## Verification

- `uv run python -c "from ...writes.groups import uxi_create_group, uxi_update_group, uxi_delete_group; print('groups OK')"` -> `groups OK`
- `uv run python -c "from ...writes.assignments import uxi_assign_agent_to_group, uxi_remove_agent_from_group, uxi_assign_sensor_to_group, uxi_remove_sensor_from_group; print('assignments OK')"` -> `assignments OK`
- `uv run python -c "from hpe_networking_mcp.platforms.uxi import TOOLS; ... assert n == 10"` -> `TOOLS dict OK -- 10 write tools registered`
- `uv run python -c "from hpe_networking_mcp.platforms.uxi import TOOLS; print(list(TOOLS.keys()))"` -> `['sensors', 'agents', 'groups', 'networks', 'service_tests', 'assignments', 'writes.sensors', 'writes.agents', 'writes.groups', 'writes.assignments']`
- `uv run ruff check src/hpe_networking_mcp/platforms/uxi/tools/writes/ src/hpe_networking_mcp/platforms/uxi/__init__.py` -> All checks passed
- `grep -r "import httpx" src/hpe_networking_mcp/platforms/uxi/tools/writes/` -> 0 matches (writes go through client helpers only)

## Threat-Model Coverage

| Threat ID | Disposition | Mitigation Landed |
|-----------|-------------|-------------------|
| T-16-06 (Tampering — group_id/parent_id URL interpolation) | mitigate | `_validate_id(group_id, "group_id")` in update/delete; `_validate_id(parent_id, "parent_id")` in create (when provided); raises `ToolError(400)` |
| T-16-07 (Tampering — assignment URL/body interpolation) | mitigate | `_validate_id()` called for every ID param (agent_id, sensor_id, group_id, assignment_id) in all 4 assignment tools before POST body / DELETE URL construction |
| T-16-08 (EoP — DELETE uses assignment_id, not resource ID) | accept | Assignment-record-ID semantics documented in remove-tool docstrings ("Pass the assignment record 'id' from uxi_list_*_group_assignments items[].id — NOT the agent or group ID"); `_validate_id` still gates path traversal |
| T-16-09 (Repudiation — silent mutations) | mitigate | `confirm_write(ctx, ...)` called BEFORE every mutation in all 7 new tools |
| T-16-10 (Tampering — ToolError swallowed) | mitigate | `except ToolError: raise` placed BEFORE `except Exception as e:` in every try block of all 7 new tools |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking] Worktree base did not contain Wave 1 outputs**

- **Found during:** Task 1 read-first phase (the plan instructs reading `writes/sensors.py` and `writes/agents.py` from Plan 16-01 as the canonical pattern; both files were absent).
- **Issue:** The worktree was forked from upstream `0c5e50b` (v3.1.0.4) and did not include any of the Wave 1 (Plan 16-01) commits — the `writes/` sub-package, the elicitation wiring, or even the Phase 15 UXI module that Plan 16-01 itself depends on.
- **Fix:** Performed `git merge --ff-only 466c2bb67406a87a29fd5bf591e175b081b10e1b` (the orchestrator HEAD after Wave 1 merge, identified by the orchestrator's `<worktree_branch_check>` block). The merge was a clean fast-forward along linear history — no rewrite of any protected ref, no `git clean`, no destructive operation. After the merge, all Wave 1 outputs (writes/sensors.py, writes/agents.py, elicitation.py wiring) were present at the canonical paths the plan references.
- **Why this is Rule 3 (not Rule 4 — architectural):** The branch base selection is mechanical — the orchestrator instructions explicitly named 466c2bb as the expected fork point. Fast-forwarding to that point is the canonical recovery; this is the same recovery Plan 16-01's executor performed against its own pre-condition.
- **Files modified:** None directly — pure git fast-forward.

**2. [Process — absolute-path safety] First Write of SUMMARY.md targeted main repo .planning/, not worktree .planning/**

- **Found during:** SUMMARY commit (Task 4 / final-commit phase).
- **Issue:** The first Write call passed an absolute path `C:/Dev/adams_mcp/.planning/...` which resolved to the **main repo's** `.planning/` directory rather than the worktree's. This is the exact #3099 absolute-path-safety failure mode flagged in the worktree-path-safety reference.
- **Fix:** Deleted the misplaced file from the main repo's .planning/ and re-wrote the SUMMARY using the canonical worktree-rooted path (`C:/Dev/adams_mcp/.claude/worktrees/agent-a03c46454e34b188d/.planning/phases/16-uxi-write-tools/16-02-SUMMARY.md`). No commits were affected — the misplaced file had not been added or committed.
- **Why noted:** Process error worth documenting so the next executor (or a future revision of the executor instructions) catches the same trap.

### Architectural Decisions Implemented Without Asking

None.

## Auth Gates

None — all changes were pure code edits; no external auth required.

## Known Stubs

None. All 7 new tools have full implementations (validation, elicitation, client call, error handling). The Wave 0 test stubs in `tests/unit/test_uxi_write_tools.py` are owned by Plan 16-01 / 16-03 and were not touched here.

## Deferred Issues

A pre-existing zero-byte stray file `dict[str` exists at the worktree root from prior unrelated work. It is untracked and has nothing to do with this plan's scope; left in place per the executor scope-boundary rule (do not fix unrelated pre-existing artifacts). A pre-existing modification to `uv.lock` is also present from Wave 1's merge fast-forward and is similarly out of scope for this plan.

## Threat Flags

None — no new security-relevant surface introduced beyond what the plan's `<threat_model>` already enumerates and mitigates. The 4 new POST endpoints and 3 new DELETE endpoints are all gated by the existing `ENABLE_UXI_WRITE_TOOLS` write-gate (Phase 15) plus the elicitation middleware extension landed in Plan 16-01.

## Self-Check: PASSED

- FOUND: src/hpe_networking_mcp/platforms/uxi/tools/writes/groups.py
- FOUND: src/hpe_networking_mcp/platforms/uxi/tools/writes/assignments.py
- FOUND: src/hpe_networking_mcp/platforms/uxi/__init__.py (modified — verified via `'writes.assignments' in TOOLS`)
- FOUND commit: 9f59297 (Task 1 — groups.py)
- FOUND commit: 5a452b6 (Task 2 — assignments.py)
- FOUND commit: 6ce4b9a (Task 3 — TOOLS dict registration)
