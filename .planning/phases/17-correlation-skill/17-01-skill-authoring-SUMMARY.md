---
phase: 17-correlation-skill
plan: 01
subsystem: skills
tags: [skill, uxi, correlation, markdown, diagnostics]
dependency_graph:
  requires:
    - "Phase 15 UXI platform module (src/hpe_networking_mcp/platforms/uxi/)"
    - "Phase 16 UXI write tools (sub-tree on this base; not directly used by skill)"
    - "Existing skill engine (src/hpe_networking_mcp/skills/_engine.py)"
    - "health() aggregator (src/hpe_networking_mcp/platforms/health.py) with _probe_uxi wired"
  provides:
    - "uxi-cross-platform-diagnostics skill — auto-discovered by SkillRegistry.from_directory()"
    - "GO/DEGRADED/CRITICAL verdict template for UXI synthetic-test correlation"
  affects:
    - "skills_list / skills_load tool surface (new bundled skill appears)"
tech_stack:
  added: []
  patterns:
    - "Skill-as-runbook: prose markdown executed by AI at inference time"
    - "Frontmatter-driven discovery: yaml frontmatter + body separated by --- delimiters"
    - "Reachability gate pattern from aos-migration.md Stage -1"
    - "Platform-aware narrowing (Skip if clauses) from infrastructure-health-check.md"
    - "Paste-bundle fallback from change-pre-check.md"
key_files:
  created:
    - "src/hpe_networking_mcp/skills/uxi-cross-platform-diagnostics.md (663 lines)"
  modified: []
decisions:
  - "Skill references `health` (singular aggregator), not a separate uxi_health tool — there is no `uxi_health` tool; `_probe_uxi` is invoked via `health()`."
  - "UXI issue field discipline: skill body documents the ACTUAL `uxi_get_sensor_status` return shape ({isOnline, isTesting, issues:[{code, severity, status, timestamp, id, context, incidentId}]}) and instructs the AI to resolve networkName/groupPath/serviceTestName via the related list tools (uxi_list_wireless_networks, uxi_list_groups, uxi_list_service_tests) when those keys are not directly on the issue."
  - "Severity classification keyed off issue `code` prefix (sensor.offline / service_test.radius_auth / service_test.dns / etc.) — not UXI's free-form severity label — per D-10."
  - "Skill uses `wirelessMacAddress` as the sensor's MAC for Anchor 3 client lookup (sensors associate to APs over Wi-Fi; the wireless MAC is the one infrastructure platforms surface in client tables)."
  - "uv.lock drift NOT included in this plan's commit — uv regenerated the lock when invoking `uv run python` for SkillRegistry verification; the diff is upstream-sync drift unrelated to skill authoring."
metrics:
  duration_minutes: "~25"
  completed_date: "2026-05-17"
  tasks_completed: 2
  files_created: 1
  files_modified: 0
  total_lines_added: 663
---

# Phase 17 Plan 01: Skill Authoring Summary

Authored `uxi-cross-platform-diagnostics` skill markdown runbook
(663 lines) implementing SKILL-01..SKILL-04 with full
GO/DEGRADED/CRITICAL verdict, paste fallback, and platform-aware
correlation against Central / Mist / AOS 8.

## Tasks

### Task 1 — Pre-condition check (UXI platform module presence)

Status: PASSED — UXI module verified present on this worktree base.

Verification output:

```
src/hpe_networking_mcp/platforms/uxi/
├── __init__.py
├── _registry.py
├── client.py            (uxi_get helper present)
├── tools/
│   ├── __init__.py
│   ├── agents.py        (uxi_list_agents)
│   ├── assignments.py   (4 list_*_assignments tools)
│   ├── groups.py        (uxi_list_groups)
│   ├── networks.py      (uxi_list_wired_networks, uxi_list_wireless_networks)
│   ├── sensors.py       (uxi_list_sensors, uxi_get_sensor_status)
│   ├── service_tests.py (uxi_list_service_tests)
│   └── writes/
src/hpe_networking_mcp/platforms/health.py
├── _probe_uxi          (line 214 — wired into _PROBES at line 238)
```

UXI read-tool count (worktree base): **11**
(`uxi_list_agents`, `uxi_list_agent_group_assignments`,
`uxi_list_sensor_group_assignments`,
`uxi_list_network_group_assignments`,
`uxi_list_service_test_group_assignments`, `uxi_list_groups`,
`uxi_list_wired_networks`, `uxi_list_wireless_networks`,
`uxi_list_sensors`, `uxi_get_sensor_status`,
`uxi_list_service_tests`).

**Note on UXI health surface:** there is NO standalone `uxi_health`
tool. UXI reachability is surfaced through the unified
`health()` aggregator via `_probe_uxi` in `platforms/health.py`.
The skill's `tools:` frontmatter list therefore references `health`
(singular), NOT `uxi_health`. This is the canonical pattern
(matches `aos-migration.md` and `infrastructure-health-check.md`).

**Field-name mapping verified against sensors.py:**

`uxi_get_sensor_status` returns:

| Field | Type | Notes |
|---|---|---|
| `isOnline` | bool | Drives D-09 (offline → CRITICAL/REGRESSION) |
| `isTesting` | bool | Drives "online but idle" DRIFT |
| `issues` | list[obj] | Each item has: |
| `issues[].code` | string | Drives Stage 3 severity (D-10) — e.g. `sensor.offline`, `service_test.radius_auth.failed` |
| `issues[].severity` | string | UXI label (informational; skill ignores) |
| `issues[].status` | string | open / resolved |
| `issues[].timestamp` | ISO string | — |
| `issues[].id` | string | UXI issue id |
| `issues[].context` | obj | Free-form; may contain serviceTestName / networkName / groupPath |
| `issues[].incidentId` | string | nullable |

**Deviation from CONTEXT.md A1 assumption:** CONTEXT.md / RESEARCH.md
asserted the issue object has direct fields `networkName`,
`macAddress`, `serviceTestName`, `groupPath`. Inspection of
`sensors.py` shows these are NOT direct fields — they live inside
`issues[].context` when present. The skill body documents the
actual schema and instructs the AI to resolve those anchors from
the related UXI list endpoints when `context` does not surface
them.

### Task 2 — Author skill markdown

Status: COMPLETED.

File: `src/hpe_networking_mcp/skills/uxi-cross-platform-diagnostics.md`
Length: 663 lines.
Commit: `8d4a411` (feat(17-01): author uxi-cross-platform-diagnostics skill).

Structural checks passed:

| Check | Result |
|---|---|
| `name: uxi-cross-platform-diagnostics` (frontmatter, exact) | PASS |
| `platforms: [uxi, central, mist, aos8]` (exact order) | PASS |
| `### Stage` headings count | 7 (`Stage -1`, `Stage 0`, `Stage 1`, `Stage 1'`, `Stage 2`, `Stage 3`, `Stage 4`) |
| `GO` / `DEGRADED` / `CRITICAL` tokens present | PASS (35 occurrences combined) |
| `REGRESSION` / `DRIFT` / `INFO` tokens present | PASS |
| `**Skip if:**` clauses | 14 (≥ 3 required) |
| `sensor's OWN MAC` phrase count | 11 (≥ 2 required) |
| `case-insensitive exact match` phrase | 2 occurrences (Anchor 1, Anchor 2) |
| Six-rule output-hygiene block present | PASS |
| `**Skip if:**` on every Stage 2 sub-step | PASS |
| No fenced code blocks containing `import` / `def ` | PASS (0) |
| Loads cleanly via `SkillRegistry.from_directory()` | PASS — `s.platforms == ('uxi','central','mist','aos8')`, 24 tools resolved |

## Tools referenced (frontmatter `tools:` list — 24 entries)

UXI (8): `uxi_list_sensors`, `uxi_get_sensor_status`,
`uxi_list_agents`, `uxi_list_service_tests`, `uxi_list_groups`,
`uxi_list_wireless_networks`, `uxi_list_wired_networks`,
plus the aggregator `health`.

Central (6): `central_get_sites`, `central_get_wlans`,
`central_get_clients`, `central_get_aps`, `central_get_site_health`,
`central_get_alerts`.

Mist (5): `mist_get_site_info`, `mist_list_org_wlans`,
`mist_search_org_wireless_clients`, `mist_list_site_devices`,
`mist_search_site_alarms`.

AOS 8 (5): `aos8_find_client`, `aos8_get_client_detail`,
`aos8_get_active_aps`, `aos8_show_command`, `aos8_get_alarms`.

## Decisions D-01 through D-14 → skill-section map

| Decision | Encoded at |
|---|---|
| D-01 platform-aware narrowing | Stage 0 (reachable-platform discovery) + 14 `**Skip if:**` clauses across Stage 2 anchors |
| D-02 sensor's OWN MAC | Scope boundaries (2nd bullet), Anchor 3 (reminder paragraph), Caveats (2nd bullet); phrase appears 11 times |
| D-03 networkName → SSID | Anchor 1 (Stage 2) |
| D-04 groupPath top segment → site | Anchor 2 (Stage 2) |
| D-05 service-test → site infra | Anchor 4 (Stage 2) |
| D-06 CRITICAL conditions | Stage 3 classification table rows 1-5 |
| D-07 DEGRADED conditions | Stage 3 rows 6-7 |
| D-08 GO verdict | Stage 3 verdict-computation paragraph + table (last 3 rows) |
| D-09 sensor offline → CRITICAL/REGRESSION | Stage 3 row 1; agent-offline analog as row 8 |
| D-10 service-test type drives severity | Stage 3 explanatory paragraph + table column "Severity" |
| D-11 paste fallback | Stage 1' (Paste fallback) with exact paste-bundle template |
| D-12 paste mode still probes infra | Stage 1' final paragraph; Stage 2 runs unchanged in either mode |
| D-13 case-insensitive exact match | Anchor 1 + Anchor 2 prose; explicit "No substring, no fuzzy" |
| D-14 unmatched networkName → DRIFT | Anchor 1 no-match branch; Stage 3 table row 7 |

## Deviations from plan

1. **[Rule 2 — Missing critical functionality] Skill `tools:` list
   uses `health` instead of `uxi_health`.**
   - The plan's Task 2 action paragraph lists `uxi_health` as a
     required `tools:` entry. But `uxi_health` does NOT exist as a
     registered tool on the worktree base — UXI reachability is
     surfaced through the unified `health()` aggregator via
     `_probe_uxi`. Including a non-existent tool name would have
     failed the SKILL-05 CI regression test (Plan 02 deliverable)
     because no tool resolves to that name.
   - Files modified: `src/hpe_networking_mcp/skills/uxi-cross-platform-diagnostics.md`
   - Commit: `8d4a411`

2. **[Rule 1 — Schema bug] UXI issue object schema documented
   accurately, not per CONTEXT.md A1 assumption.**
   - CONTEXT.md / RESEARCH.md A1 assumed `issues[]` items have
     direct fields `networkName`, `macAddress`, `serviceTestName`,
     `groupPath`. Inspection of `sensors.py` (Task 1 acceptance
     criterion) shows these are NOT direct fields — they reside
     inside `issues[].context` when present. The skill body
     documents the actual schema and instructs the AI to resolve
     missing anchors via related UXI list endpoints
     (`uxi_list_wireless_networks` for `networkName`,
     `uxi_list_groups` for `groupPath`, `uxi_list_service_tests`
     for `serviceTestName`).
   - Files modified: `src/hpe_networking_mcp/skills/uxi-cross-platform-diagnostics.md`
   - Commit: `8d4a411`

3. **[Rule 3 — Blocking] `uv run python ...` regenerated `uv.lock`
   from upstream-sync state during the SkillRegistry verification
   step.**
   - The lockfile drift is unrelated to this plan's deliverable
     (skill markdown). The `uv.lock` change was NOT staged or
     committed by this plan. Should be addressed by a separate
     dependency-sync commit, or left for the next plan that
     touches dependencies.
   - Files modified: none (uv.lock left as unstaged working-tree
     change).

## Deviations from PATTERNS.md analog assignments

None. The skill body composes the three named analogs exactly as
PATTERNS.md prescribes:

- Frontmatter shape → `aos-migration.md` lines 1-50 pattern.
- Stage -1 reachability gate → `aos-migration.md` lines 118-134
  pattern with UXI substitutions.
- Stage 0 platform-aware narrowing → `infrastructure-health-check.md`
  lines 27-90 pattern; `**Skip if:**` clauses applied to every
  Stage 2 sub-step (14 occurrences).
- Stage 1' paste bundle → `change-pre-check.md` lines 146-180
  pattern with UXI sensor-bundle field set.
- Hygiene rules + "format is mandatory" guard → `aos-migration.md`
  lines 1316-1338 pattern with one-word substitutions
  (`AOS 8` → `UXI sensor data`; rule 6 platform-prefix list
  updated to `uxi_* / central_* / mist_* / aos8_*`).
- Verdict block → `aos-migration.md` lines 1339-1478 template
  adapted from 4-state (GO/BLOCKED/PARTIAL/EMPTY-SOURCE) to
  3-state (GO/DEGRADED/CRITICAL).

## Known stubs

None. The skill is complete prose — there are no placeholder
sections, no "TODO" markers, no empty headings.

## Threat flags

None new. All `tools:` references resolve to registered tools (the
threat register's T-17-07 mitigation is in place). No new trust
boundaries were introduced; the skill operates entirely within the
existing operator → skill → tool-registry surface already
threat-modelled for the broader skill engine.

## Verification commands run

- `ls src/hpe_networking_mcp/platforms/uxi/` — directory exists
- `ls src/hpe_networking_mcp/platforms/uxi/tools/sensors.py` — file exists
- `grep "_probe_uxi" src/hpe_networking_mcp/platforms/health.py` — wired (line 214, 238)
- `grep -rE '^async def uxi_' src/hpe_networking_mcp/platforms/uxi/tools/*.py | wc -l` → 11
- Structural greps (frontmatter `name`, `platforms`, stage count, verdict tokens, hygiene rules) — all pass (see table above)
- `uv run python -c "from hpe_networking_mcp.skills._engine import SkillRegistry; ..."` → PASS — skill loads, `platforms == ('uxi','central','mist','aos8')`, 24 tools resolved

## Commits

| Task | Hash | Message |
|---|---|---|
| Task 1 | (none — verification only) | UXI module presence confirmed; no files modified |
| Task 2 | `8d4a411` | feat(17-01): author uxi-cross-platform-diagnostics skill |

## Self-Check: PASSED

- File exists: `src/hpe_networking_mcp/skills/uxi-cross-platform-diagnostics.md` — FOUND
- Commit `8d4a411` exists on worktree branch — FOUND
- SkillRegistry loads new skill cleanly — VERIFIED
