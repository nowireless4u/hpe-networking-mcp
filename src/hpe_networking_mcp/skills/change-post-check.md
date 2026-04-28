---
name: change-post-check
title: Post-change verification + diff
description: |
  Re-run the same checks captured in `change-pre-check` after a planned
  configuration change has completed, then diff against the baseline to
  produce a verdict (CLEAN / IMPACT-OBSERVED / REGRESSION). Use this when
  the user says "the change is done — verify it", "post-change check", or
  finishes a maintenance window. Pairs with `change-pre-check`.
platforms: [mist, central, clearpass, apstra]
tags: [change-management, maintenance, verification, post-flight]
tools: [health, mist_search_alarms, mist_search_audit_logs, central_get_alerts, central_get_audit_logs, clearpass_get_system_events]
---

# Post-change verification + diff

## Objective

Confirm the planned change landed cleanly by re-pulling the same data
captured in `change-pre-check` and diffing the two snapshots. Output a
verdict — `CLEAN`, `IMPACT-OBSERVED`, or `REGRESSION` — that the operator
pastes into the change ticket as the post-change verification entry.

This skill is the partner to `change-pre-check`. The pre-check captures
the BEFORE; this captures the AFTER and shows the delta.

## Prerequisites

- A `change-pre-check` snapshot for the SAME target / scope must be
  available — either in the current conversation or pasted back by the
  user. **Without a baseline this skill can't run.** A post-check that
  isn't comparing against a baseline is just another pre-check.
- The change should actually be complete. If the user is still mid-change,
  ask them to confirm the change landed before continuing — running
  post-check during the change produces a misleading delta.

## Procedure

### Step 1 — Locate the baseline snapshot

**Look in conversation context first.** If you can see a `change-pre-check`
snapshot earlier in this chat covering the same target/scope, use it
directly — you don't need to ask the user to re-paste it. The pre-check
output has a recognizable shape:

```
## Pre-change baseline — <description>
**Captured:** <timestamp>
**Target:** <scope>
**Affected platforms:** ...
```

**Otherwise ask the user to paste it back.** Say:
> "I don't see a pre-check snapshot in this conversation. Paste the
> baseline output here (the block starting with `## Pre-change baseline`)
> and I'll diff against it."

Record the baseline's `Captured:` timestamp, target, and platform list —
those scope every later step.

### Step 2 — Re-run reachability

**Tool:** `health(platform=<same as baseline>)`
**Why:** Confirms the change didn't break reachability to any of the
involved platforms. A platform that was `ok` in pre-check and is now
`degraded` is a major red flag.
**Compare to:** Baseline reachability section.
**Verdict contribution:**
- All platforms still `ok` → CLEAN signal
- Any platform now `degraded` / `unavailable` that was `ok` → REGRESSION
  signal (lead with this)

### Step 3 — New alarms / alerts since baseline

**Mist:** `mist_search_alarms(org_id=..., site_id=<target>, duration="<delta>")`
where `<delta>` is approximately the time elapsed since the pre-check
`Captured:` timestamp (round up to nearest hour and add 30 minutes of
buffer). Filter to alarms matching the change target.

**Central:** `central_get_alerts(severity="Major,Critical")` then filter
to alerts on the affected device(s)/site that are NOT in the baseline.

**Why:** New alarms in the change window are correlated with the change
unless proven otherwise. Pre-existing alarms documented in the baseline
should NOT be re-flagged here — they were already broken.
**Compare to:** Baseline pre-existing alarms section.
**Verdict contribution:**
- 0 new alarms / alerts → CLEAN signal
- New alarms within 10 minutes of the change → IMPACT-OBSERVED, list them
- New critical alarms after the change → REGRESSION

### Step 4 — Audit log confirmation

**Mist:** `mist_search_audit_logs(org_id=..., duration="<delta>", limit=50)`
**Central:** `central_get_audit_logs` (filter to the change window)
**ClearPass (if affected):** `clearpass_get_system_events(limit=50)`

**Why:** Two things to verify:
1. The planned change is recorded — confirms it actually landed (not just
   "the API returned 200" but "the system recorded the action").
2. **No unplanned admin actions in the change window.** If someone else
   pushed an unrelated change concurrently, that's a finding — flag it
   even if it didn't cause a problem, because it complicates root-cause
   analysis if something does break later.

**Verdict contribution:**
- Planned change recorded + no unplanned activity → CLEAN signal
- Planned change recorded + unrelated admin actions in the window → note
  in the report (not necessarily a regression; informational)
- Planned change NOT recorded → REGRESSION (the change didn't actually
  apply or wasn't audited correctly)

### Step 5 — Current configuration vs baseline

Re-read the affected resource's *current* config using the same tool the
pre-check used (see the "Current configuration" section of the baseline).

**Compare line-by-line to the baseline's captured config.** Show the diff
inline. Highlight:
- Lines that match the operator's change description → expected
- Lines that don't match the change description → unplanned drift
- Lines that the change description said WOULD change but didn't →
  potential failure-to-apply

**Verdict contribution:**
- Diff matches change description exactly → CLEAN signal
- Diff includes unplanned changes → REGRESSION (something else got
  changed beyond what was planned)
- Diff is missing planned changes → REGRESSION (the change didn't fully
  apply)

### Step 6 — Active impact metrics

Re-pull the same metrics the pre-check captured (Wi-Fi: client count,
APs up, disconnected; Switch: device count, active client count; NAC:
active session count by service).

**Compute the delta vs baseline:**

| Metric | Baseline | Now | Delta % |
|---|---|---|---|
| Clients (HOME) | 38 | 35 | -7.9% |
| APs up (HOME) | 17 | 17 | 0% |
| Active NAC sessions | 1240 | 1198 | -3.4% |

**Verdict contribution by delta magnitude:**
- |delta| < 5% on all metrics → CLEAN signal (likely just normal churn)
- 5-15% drop on one metric → IMPACT-OBSERVED, attribute to the change
- 15%+ drop on any metric → REGRESSION; lead the report with this

Wi-Fi changes have a 5-15 minute settling window — if the post-check
happens within 5 minutes of the change landing, mention that the
delta may not be fully meaningful yet.

### Step 7 — Compute verdict + format the report

Aggregate the verdict signals from steps 2-6 into one of three values:

| Verdict | Trigger |
|---|---|
| **CLEAN** | Every step contributed CLEAN signals (no new alarms, reachability unchanged, config diff matches plan, deltas <5%) |
| **IMPACT-OBSERVED** | At least one IMPACT signal but no REGRESSION signals (new minor alarm, 5-15% client delta, etc.) — change landed but had user-visible effect |
| **REGRESSION** | Any REGRESSION signal (platform unreachable, planned change didn't land, unplanned config drift, >15% delta) |

Format the report as shown below.

## Decision matrix

| Condition | Action |
|---|---|
| No baseline available in chat or paste | STOP. Ask user for the pre-check snapshot. Don't run blind. |
| Baseline target ≠ current scope | STOP. Pre-check covered site `HOME`, post-check shouldn't run against site `OFFICE`. Confirm with user. |
| Change landed less than 5 minutes ago + Wi-Fi affected | Note that client/RF metrics may still be settling; consider a follow-up post-check in 10 minutes |
| Verdict is REGRESSION | Lead the report with the regression specifics. Suggest the operator consider rollback. |
| Audit log shows unplanned admin actions | Surface the actor + timestamp explicitly so the operator can investigate |

## Output formatting

Use the EXACT structure below. Every section heading must be present —
the operator pastes this into the change ticket and the consistency
matters when comparing against the pre-check snapshot. For REGRESSION
verdicts, lead with the specifics under "Verdict reasoning."

```
## Post-change verification — <change description>
**Captured:** <ISO timestamp>
**Baseline:** <baseline timestamp from pre-check>
**Target:** <site / device / WLAN / policy>
**Verdict:** CLEAN / IMPACT-OBSERVED / REGRESSION

### Reachability diff
- Mist: ok → ok ✓
- Central: ok → ok ✓

### New alarms / alerts since baseline
- Mist: 0 new on target ✓
- Central: 1 new minor — "AP-12 fan speed warning" — but PRE-EXISTING in baseline (NOT caused by change)

### Audit log
- Planned change recorded at 14:31 UTC by current user ✓
- No unplanned admin actions in window ✓

### Configuration diff
<inline diff vs baseline — highlight what changed>

### Impact metrics
| Metric | Baseline | Now | Delta |
|---|---|---|---|
| Clients (HOME) | 38 | 35 | -7.9% (within normal churn) |
| APs up (HOME) | 17 | 17 | 0% |

### Verdict reasoning
- Reachability unchanged
- 0 new alarms in change window
- Config diff matches change description
- Metric deltas within normal churn range
- → CLEAN
```

For REGRESSION verdicts, lead with the specifics; the operator needs to
decide whether to roll back.

## Example queries that should trigger this skill

> "the WLAN change is done — verify it"
> "run the change-post-check now"
> "post-change checks for the AP firmware push that just finished"
> "is the change clean?"
