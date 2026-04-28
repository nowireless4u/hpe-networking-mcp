---
name: change-pre-check
title: Pre-change baseline snapshot
description: |
  Capture a known-good baseline of the affected target before a planned
  configuration change so the operator (a) has something to diff against
  post-change, (b) can spot pre-existing issues that aren't theirs to own,
  and (c) catches recent admin activity that might collide with the change.
  Use this when the user mentions an upcoming change, maintenance window,
  config push, firmware upgrade, WLAN modification, or NAC policy edit.
platforms: [mist, central, clearpass, apstra]
tags: [change-management, maintenance, baseline, pre-flight]
tools: [health, mist_search_alarms, mist_search_audit_logs, central_get_alerts, central_get_audit_logs, clearpass_get_system_events, clearpass_get_sessions, clearpass_get_enforcement_policies, mist_get_wlans, central_get_wlans, mist_get_switch_details, central_get_switch_details, mist_search_device, central_get_devices, mist_get_configuration_objects, apstra_get_blueprints]
---

# Pre-change baseline snapshot

## Objective

Capture a snapshot of the affected target *before* the change so the
operator has (1) a baseline to diff against, (2) evidence of pre-existing
issues, and (3) awareness of any recent activity that could collide with
their planned change.

This skill is the partner to a future `change-post-check` skill. Steps 2,
3, and 6 are designed to be re-run after the change and diffed against
this snapshot.

## Prerequisites

- The user has identified the change scope. **Do NOT proceed without
  confirming the target.** Ask the user one clarifying question if scope
  is ambiguous: "Which site / device / WLAN / policy is being changed?"
- The affected platforms must be reachable. Run `health(platform=[...])`
  first and abort with a clear error if any required platform is
  `unavailable` — running pre-check against a flapping platform produces a
  misleading baseline.

## Procedure

### Step 1 — Confirm change scope

Ask the user (if not already provided):
- **What** is being changed? (WLAN config, switch port, AP firmware, NAC
  policy, gateway settings, etc.)
- **Where** does it apply? (specific `site_name`, `device_id`, `wlan_id`,
  `enforcement_policy_id`, etc.)
- **When** is the change scheduled? (informational — included in the
  snapshot timestamp note)

Record the answers; every later step is scoped to them.

### Step 2 — Baseline reachability

**Tool:** `health(platform=<inferred from change scope>)`
**Why:** Confirms every platform involved is reachable BEFORE the change so
post-change reachability degradation is attributable to the change, not to
a pre-existing API outage.
**Expected result:** Each platform `status: ok`.
**If anomaly:** Stop. Surface the failure to the user and ask whether to
proceed anyway (rare cases — operator is changing the broken thing). Do
not silently continue with a bad baseline.

### Step 3 — Pre-existing alarms / alerts on the affected target

**Mist (if affected):**
`mist_search_alarms(org_id=..., site_id=<target>, duration="1d", limit=20)`
Filter the response down to alarms whose `device_id` or `site_id` overlap
with the change target.

**Central (if affected):**
`central_get_alerts(severity="Major,Critical")` — then filter the response
to alerts naming the affected device(s) / site.

**Why:** Catches "this was already broken before I touched it." The
operator pastes this into the change ticket so post-change failures aren't
incorrectly attributed.
**Expected result:** Empty list (clean) or a small list of pre-existing
alarms.

### Step 4 — Recent admin activity (last 24h)

**Mist:** `mist_search_audit_logs(org_id=..., duration="1d", limit=50)`
**Central:** `central_get_audit_logs` (filter to last 24h client-side)
**ClearPass (if affected):** `clearpass_get_system_events(limit=50)`

**Why:** Detects "someone else just changed something here." Two engineers
unknowingly working on adjacent configs is a classic root-cause for
incidents during change windows.
**Expected result:** Routine activity OR the operator's own recent changes.
**If anomaly:** Any change in the last 4 hours by another actor scoped to
the target → call it out explicitly. Suggest the operator confirm with that
actor before proceeding.

### Step 5 — Current configuration of the change target

Read the affected resource's *current* config so step 7's snapshot can
include it for post-change diffing.

| Change type | Tool to call |
|---|---|
| WLAN | `mist_get_configuration_objects(object_type="wlans", object_id=...)` (Mist) or `central_get_wlans(site_id=...)` (Central) |
| Switch port | `mist_get_switch_details(device_id=...)` (Mist — port config is part of switch detail) or `central_get_switch_details(serial=...)` (Central) |
| AP firmware target | `mist_search_device(text=<name>, device_type="ap")` to find the device, then `mist_get_ap_details(device_id=...)` to read `version` + `target_version` (Mist); `central_get_devices(serial_number=...)` for Central APs |
| NAC enforcement policy | `clearpass_get_enforcement_policies(policy_id=...)` |
| Apstra blueprint baseline | `apstra_get_blueprints(blueprint_id=...)` to record the current `version` field; pair with `apstra_get_diff_status(blueprint_id=...)` to confirm there are no pending uncommitted changes before yours |

**Why:** A clean copy of the BEFORE config makes "did the change cause X?"
straightforward to answer. Without this you're guessing.

### Step 6 — Active impact metrics

**Wi-Fi changes:** `mist_get_site_health(site_id=<target>)` — record
`num_clients`, `num_aps_up`, `num_devices_disconnected`.
**Switch changes:** `central_get_site_health(site_name=<target>)` — record
device counts and active client count.
**NAC changes:** `clearpass_get_sessions(limit=...)` — record total
active session count and breakdown by service.

**Why:** Active counts are the leading indicator of customer impact during
the change. A delta of ±10% within 5 minutes of the change is the operator's
"abort or commit" signal.

### Step 7 — Format the baseline snapshot

Bundle everything into one structured snapshot the operator pastes into
their change ticket (see *Output formatting* below).

## Decision matrix

| Condition | Action |
|---|---|
| User hasn't specified the change target | STOP. Ask for it. Don't run with default scope. |
| Health check finds the affected platform `unavailable` | Surface the error and ask whether to proceed (likely the operator is changing the broken thing) |
| Pre-existing alarms on the target | Lead the snapshot with these so they're documented BEFORE the change |
| Recent admin activity by another actor | Recommend confirming with that actor before proceeding |
| User says they're upgrading firmware | Add a step to confirm the rollback path (target version is recoverable) |

## Output formatting

Use the EXACT structure below. Every section heading must be present even
if its content is "0 active" / "no recent activity" — consistency lets the
post-check skill diff against this snapshot reliably. Don't add freeform
sections; if you have observations, put them under "Notes."

```
## Pre-change baseline — <change description>
**Captured:** <ISO timestamp>
**Target:** <site / device / WLAN / policy>
**Affected platforms:** Mist, Central

### Reachability (T-0)
- Mist: ok
- Central: ok

### Pre-existing alarms / alerts
- Mist: 0 active on target
- Central: 1 minor — "AP-12 fan speed warning" (PRE-EXISTING, not caused by change)

### Recent admin activity (last 24h)
- Mist: 3 actions by current user
- Central: 1 action by tech-on-duty at 14:22 UTC — investigate before proceeding

### Current configuration
<paste of relevant config block(s) — typically 5-30 lines>

### Active impact metrics (snapshot for post-change diff)
- Mist site `HOME`: 38 clients, 17 APs up, 0 disconnected
- Central site `HOME`: 24 switches, 0 alerts

### Notes
- Pre-existing minor alarm on AP-12 — NOT my change.
```

Save this snapshot before proceeding with the change.

## After the change — run the post-check

End the response by reminding the operator:

> "Save this snapshot. After the change lands, run the `change-post-check`
> skill to diff against this baseline and get a CLEAN / IMPACT-OBSERVED /
> REGRESSION verdict. If you stay in this same chat, the AI will read
> this snapshot directly from context — you won't need to paste it back."

## Example queries that should trigger this skill

> "I'm about to push a config change to the HOME WLAN — give me a baseline"
> "running pre-change checks for the AP firmware push tonight"
> "before I touch the NAC policy can you snapshot the current state"
