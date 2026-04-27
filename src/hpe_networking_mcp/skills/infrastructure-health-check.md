---
name: infrastructure-health-check
title: Cross-platform infrastructure health snapshot
description: |
  One-shot operational overview of every enabled platform — reachability,
  active alarms/alerts, and any platform-specific red flags. Use this when
  the user asks "is everything healthy?", "give me a daily standup", or
  starts a session and wants a baseline before drilling in.
platforms: [mist, central, clearpass, apstra, greenlake, axis]
tags: [health, monitoring, daily-standup, baseline]
tools: [health, mist_search_alarms, central_get_alerts, clearpass_get_recent_audit_log]
---

# Cross-platform infrastructure health snapshot

## Objective

Surface anything degraded or actively alarming across every enabled platform
in a single concise report. Aim for under 60 seconds wall-clock and a result
the user can read in under 30 seconds.

## Prerequisites

- At least one platform must be configured (the skill adapts to whatever is
  enabled — it does NOT require all six).
- Run `health()` first; if every enabled platform returns `status: ok` and
  the user only asked for reachability, you can stop after step 1.

## Procedure

### Step 1 — Reachability across all enabled platforms

**Tool:** `health()` (no `platform` filter — pull every enabled platform at once)
**Why:** Confirms the server can reach each platform's API. A platform that's
`unavailable` can't be queried in later steps; mark it and skip its drill-down.
**Expected result:** Each enabled platform reports `status: ok` (and Axis
reports a `token_expires_in_days` countdown).
**If anomaly:** A `degraded` or `unavailable` platform means credentials are
wrong, the upstream API is down, or networking is broken — surface the
`message` field verbatim and skip steps 2-7 for that platform.

### Step 2 — Mist alarms (last 24h)

**Tool:** `mist_search_alarms(org_id=<from health>, duration="1d", limit=50)`
**Why:** Active alarms are Mist's primary signal for "something is wrong."
**Expected result:** Empty list, or a list of alarms with `type` + `severity` + `count`.
**If anomaly:** Group by `type`, surface the top 5 by count. Don't list every
alarm individually — the user wants a triage summary, not a dump.
**Skip if:** Mist is not enabled or returned `unavailable` in step 1.

### Step 3 — Central alerts

**Tool:** `central_get_alerts(severity="Major,Critical")`
**Why:** Critical/Major alerts are Central's actionable layer.
**Expected result:** Empty list, or alerts grouped by `description`.
**If anomaly:** Surface the top 5 alerts by recency.
**Skip if:** Central is not enabled or returned `unavailable` in step 1.

### Step 4 — ClearPass recent admin activity

**Tool:** `clearpass_get_recent_audit_log(limit=20)`
**Why:** Catches "someone just changed something" before the user starts
their work. Especially valuable in environments where multiple operators
share an account.
**Expected result:** A list of recent admin actions with timestamps + actor.
**If anomaly:** Note any actions in the last 4 hours by actors other than
the current user. Don't surface routine read-only logins.
**Skip if:** ClearPass is not enabled or returned `unavailable` in step 1.

### Step 5 — Apstra anomalies (if Apstra is enabled)

**Tool:** `apstra_invoke_tool(name="apstra_get_anomalies", params={...})`
(or the equivalent in code mode: `await call_tool("apstra_get_anomalies", ...)`)
**Why:** Apstra surfaces fabric-level health (e.g. BGP session down, MLAG split-brain).
**Expected result:** Empty list, or anomalies grouped by `type`.
**Skip if:** Apstra is not enabled.

### Step 6 — Axis connector status (if Axis is enabled)

**Tool:** `axis_get_connectors()` then look at `cpuStatus`, `memoryStatus`,
`networkStatus`, `enabled` fields.
**Why:** Axis tunnels can degrade silently; CPU/memory/network status fields
flag pre-failure conditions.
**Expected result:** All connectors `enabled: true` with `*Status: ok`.
**Skip if:** Axis is not enabled.

### Step 7 — Format the snapshot

Combine all findings into one terse summary (see *Output formatting* below).

## Decision matrix

| Condition | Action |
|---|---|
| Every platform `ok` and no alarms/alerts | Output one line: "All clear" + reachability table |
| One platform `unavailable` | Surface its error message, then continue with the rest |
| Critical/Major alerts present | Lead with those — they're what the user should act on first |
| Recent admin activity in ClearPass last 4h | Call it out explicitly so the user knows context |

## Output formatting

```
## Infrastructure health — <timestamp>

**Reachability**
- Mist: ok
- Central: ok
- ClearPass: ok
- Apstra: degraded (token expires in 28 days)

**Active alarms / alerts**
- Mist: 3 alarms — `ap_disconnected` (2), `radius_server_unreachable` (1)
- Central: 1 critical — "Switch CX-1 unreachable" (HOME)
- ClearPass: 5 admin actions in last 4h by `tech-on-duty`

**Action items**
- Investigate Mist `ap_disconnected` cluster at HOME
- Confirm Apstra token renewal scheduled
```

Keep it under 25 lines total. The user reads this *before* drilling in.

## Example queries that should trigger this skill

> "is everything healthy?"
> "give me an infra snapshot"
> "daily standup"
> "what's broken right now?"
