---
name: morning-coffee-report
title: Morning coffee report — daily ops digest of who-did-what + what's broken + top talkers
description: |
  Open-the-laptop-with-coffee read: a single combined digest of activity
  (who logged into Central / Mist over the last 24h and what they did),
  active alerts/alarms (what needs attention), top talkers (clients and
  APs by load), and AI insights (Marvis SLEs, Central anomalies). Use
  when the user asks for a "morning coffee report", "morning digest",
  "give me the rundown", or "what happened overnight" — anything that
  asks for an overnight ops summary across platforms.
platforms: [mist, central]
tags: [morning, daily-digest, audit, alerts, top-talkers, sle, baseline]
tools: [health, mist_get_self, mist_search_audit_logs, mist_search_events, mist_search_alarms, mist_search_client, mist_search_device, mist_get_org_sle, mist_get_org_sites_sle, mist_get_site_sle, mist_get_insight_metrics, central_get_audit_logs, central_get_audit_log_detail, central_get_alerts, central_get_alert_classification, central_get_clients, central_get_aps, central_get_sites, central_get_site_health]
---

# Morning coffee report — daily ops digest

## Objective

Single combined digest readable in under 90 seconds with morning coffee.
Covers the **last 24 hours** across enabled platforms (Mist + Central
this release; ClearPass / Apstra / Axis follow in a later phase).

The very first line of the report is a **gas-gauge status indicator**
(🟢 GREEN / 🟡 YELLOW / 🔴 RED) so the operator can decide in two
seconds whether they need to read the rest. Green means skip and go
about your day; yellow means read the headline; red means read all the
way through.

Five sections, in this order:

1. **Headline + status indicator** — gas-gauge color + the
   if-you-only-read-one-paragraph view (3–5 lines).
2. **Activity** — who logged in, who changed config, top actions per user.
3. **What's broken right now** — active alerts/alarms, severity-ordered.
4. **Top talkers** — clients, APs, SSIDs by load.
5. **Insights** — AI-surfaced anomalies (Mist Marvis SLE; Central anomalies).

**Day-over-day delta** ("what changed since yesterday") is **deferred to
phase 2** (separate skill iteration). Phase 1 produces the last-24h view.

## Prerequisites

- At least one of Mist or Central enabled. The runbook adapts — if a
  platform is `unavailable`, that platform's sections are skipped with a
  one-line note.
- Run `health()` first — confirms reachability and gives you the
  `org_count` per platform to sanity-check.
- For Mist: the org_id from `mist_get_self(action_type="account_info")`
  is needed for org-scoped queries; cache it once for the whole run.
- For Central: most of its read tools are tenant-scoped via the configured
  workspace; no extra context needed. For per-site rollups you may need
  site IDs from `central_get_sites()`.

## Time window

The "last 24 hours" window is computed from **the operator's submission
time** (the moment the user asks for the report). Pass that as ISO 8601
`<now>` and `<now-24h>` to every tool that takes a time range. Do NOT
compute "now" inside the code-mode sandbox — it blocks `datetime.now()`.
Either ask the operator for the current time once at the start, or accept
the timestamp as a skill input parameter.

## Procedure

### Step 1 — Reachability + org context

**Tools:**
- `health(platform="mist")` and `health(platform="central")` (call both
  in parallel where possible; in code-mode sandbox they're sequential)
- `mist_get_self(action_type="account_info")` — extract `org_id` from
  the returned `privileges` array (look for `scope: "org"`)

**Why:** Confirms each platform is reachable before spending time on
drill-downs. Gives you the Mist org_id every later Mist call needs.

**Expected result:** Each enabled platform reports `status: ok`. The
self-info call returns at least one org-scoped privilege.

**If anomaly:** A `degraded` or `unavailable` platform means skip its
sections with a one-line note in the headline (*"Mist: unavailable —
skipping activity, alarms, top talkers, SLE"*). The report should still
produce useful output for whichever platform IS reachable.

### Step 2 — Activity: who's been in Central + Mist (last 24h)

**Tools:**
- `central_get_audit_logs(start_time=<now-24h>, end_time=<now>, limit=100)`
- `mist_search_audit_logs(org_id=<from step 1>, start=<now-24h>, end=<now>, limit=200)`

**Why:** Audit logs capture who logged in, who took write actions, and
what they targeted. This is the "who's been in" answer.

**Expected result:** A list of audit entries per platform. Each entry
typically has a user/email, timestamp, action, and target resource.

**If anomaly:** If audit logs are empty, surface that as an INFO line
("no audit activity in the last 24h on Central") — it's noteworthy by
itself.

**Aggregation:**
- Group by user (email or username).
- Per user, count: total events, login events, write actions (anything
  that's not a read/list/get).
- Highlight users who took **config write actions**: in Central, audit
  log entries with action verbs like `Update`, `Create`, `Delete`; in
  Mist, audit entries that aren't `LOGIN` or read-shaped events.
- Surface the **top 3 actions per user** with target resource (the
  thing that was changed) — not the full event stream.

**For drill-down (don't run for every event — only when the user asks
follow-up):** `central_get_audit_log_detail(audit_log_id=<id>)` to get
the full payload of a specific Central event.

### Step 3 — What's broken right now: active alerts + alarms

**Tools (Central):**
- `central_get_alert_classification(classify_by="severity", filter="status eq 'Active'")` — get the severity buckets in one call (cheap; no per-alert paging needed for the headline count)
- For severity-ordered detail: `central_get_alerts(site_id=<each site>, status="Active", sort="severity desc", limit=20)` — note this requires a `site_id`, so loop over sites if needed (only if the user wants per-site detail)

**Tools (Mist):**
- `mist_search_alarms(org_id=<from step 1>, duration="1d", limit=100)` — last-24h alarm search

**Why:** Lead with what needs attention TODAY. Severity-ordered, deduplicated.

**Expected result:** Counts per severity from Central (Critical / Major /
Minor / Info totals); a list of alarms from Mist with `type` + `severity` +
`count`.

**If anomaly:** Empty active-alert lists are good news — surface as
"no critical or major alerts today."

**Aggregation:**
- Headline: "X critical, Y major active across all sites" (Central);
  "Z alarm types with N total events" (Mist).
- Below the headline, the top 5 alerts by severity (Central) and the
  top 5 alarm types by count (Mist), each with the affected
  device/site name.
- Collapse repeats: "Switch port flap on AP-Floor-3 (12 events in 6h)"
  is one line, not 12.
- Flag anything `Critical` with a 🔴 prefix in the rendered output (or
  `[CRITICAL]` if rendering plain text).

### Step 4 — Top talkers

**Tools (Central):**
- `central_get_clients(...)` — sort by traffic descending; pull the top
  10. Inspect the schema via `central_get_tool_schema(name="central_get_clients")`
  for the exact sort parameter name and time-range filter.
- `central_get_aps(...)` — sort by client count or load; pull the top 10.

**Tools (Mist):**
- `mist_search_client(org_id=<from step 1>, duration="1d", limit=20)` —
  search clients in the last 24h; pull tx/rx if available.
- `mist_search_device(org_id=<from step 1>, device_type="ap", duration="1d", limit=20)` —
  for AP-side load.

**Why:** Top talkers tell you which clients/devices are doing real work
right now. Useful to spot the one device gobbling all the bandwidth or
the AP that's saturated.

**Expected result:** Two ranked lists per platform — top clients (by
total traffic) and top APs (by client count or aggregate load).

**Aggregation:**
- 5–10 entries per category, no more.
- Per client: name (from `device_name` or `hostname` if available;
  otherwise MAC), connected SSID, traffic volume.
- Per AP: name, site, current client count, load.

**If anomaly:** A specific client consuming >40% of total traffic
warrants a callout. An AP with 50+ concurrent clients warrants a
callout (likely capacity issue).

### Step 5 — Insights: SLEs and AI-surfaced anomalies

**Tools (Mist):**
- `mist_get_org_sle(org_id=<from step 1>)` — overall SLE rollup for the org
- `mist_get_org_sites_sle(org_id=<from step 1>)` — per-site SLE summary
  (lets you see which site is dragging the org-wide number)
- `mist_get_site_sle(site_id=<each>)` — only for the worst-performing
  site (don't fan out to all sites)
- `mist_get_insight_metrics(...)` — when the user asks for a specific
  metric drill-down

**Tools (Central):**
- Central doesn't expose a single "AI insights" tool; surface
  Central-side insights from `central_get_alert_classification` (above)
  combined with notable trends from `central_get_alerts` over the last
  24h. Phase 2 may add a dedicated tool when one becomes available.

**Why:** SLE and Marvis insights surface anomalies the operator
shouldn't have to look for. Worst-performing SLE category in the last
24h is usually the most actionable signal Mist produces.

**Expected result:** Mist SLE values per category (Time-to-Connect,
Throughput, Capacity, Coverage, Roaming, Successful Connects). Central:
a brief "alert categories trending up" note from the classification
data.

**Aggregation:**
- Lead with worst-performing SLE category and its score.
- Identify the worst-performing site (lowest aggregate score across
  categories).
- Don't dump every SLE value — surface the bottom 1–2 categories and
  the bottom 1–2 sites only.

## Status indicator rubric

The gas-gauge color at the top of the report is computed from the data
the procedure already collected — no extra tool calls. Apply these
rules in order; the first match wins.

🔴 **RED** — read the whole report; needs immediate attention. Any of:

- One or more `Critical` active alerts on Central
- One or more Mist alarms with `severity: critical`
- Any Mist SLE category at <75% (org-wide rollup from `mist_get_org_sle`)
- A config-write action by an unexpected user (i.e. a user the
  operator wouldn't recognize as a member of the team — surface this
  as a flag, don't decide for them, but if the AI sees writes from
  `system` or known team members only, that's not a flag)
- Either platform reporting `unavailable` from `health()`

🟡 **YELLOW** — read the headline + scan the sections. Any of:

- One or more `Major` active alerts on Central (no critical)
- Mist alarm count >10 in the last 24h
- Any Mist SLE category between 75–85%
- An AP with 50+ concurrent clients (capacity warning)
- A single client consuming >40% of total traffic
- Any platform reporting `degraded` from `health()`

🟢 **GREEN** — all of the following are true:

- 0 critical alerts on Central
- 0 critical alarms on Mist (and total alarm count under 10 in 24h)
- All Mist SLE categories ≥85%
- No platform `unavailable` or `degraded`
- No anomalous traffic patterns (no client >40%, no AP >50 clients)
- Audit log activity, if any, is from expected users only

Show the rubric color at the very top of the report on its own line,
followed by a single sentence summarizing why that color was chosen
(*"all SLEs above 90%, no critical alerts overnight, only routine
audit activity"* for green; *"5 critical alerts at HOME-KNAPP, MTU
mismatch on aggregation link"* for red).

## Decision matrix

| Condition | Action |
|---|---|
| Both Mist and Central are `unavailable` | Stop. Report the unavailability and ask the user to check connectivity. |
| Mist is `unavailable` | Skip steps 2 (Mist half), 3 (Mist half), 4 (Mist half), 5 (Mist half). Run Central-only sections. |
| Central is `unavailable` | Skip Central halves of steps 2–5. Run Mist-only sections. |
| User asks for a single site only | Pass `site_id` filters to every tool that supports one (`central_get_alerts(site_id=)`, `central_get_site_health`, `mist_get_site_sle`). Skip the org-wide SLE rollup. |
| Audit log returns 0 events in 24h | Surface as INFO ("no audit activity") — don't omit the section. |
| All alert lists are empty | Headline says "no critical or major alerts overnight." Don't omit the section. |
| Top-talker call returns no clients | Likely an off-hours window — note it in the section but don't expand to "top X over the last 7 days" (out of scope). |
| Worst-performing SLE category is >85% | Skip the SLE callout in the headline (everything's healthy). |

## Output formatting

The report must follow this exact structure so different runs produce
comparable output. Use Markdown headings; render in the AI client.

```
# Morning coffee report — <ISO date>
**Window:** last 24 hours (since <now-24h ISO>)
**Platforms:** mist (ok | unavailable), central (ok | unavailable)

## Status: 🟢 GREEN | 🟡 YELLOW | 🔴 RED

One sentence describing why this color was chosen. Examples:

- 🟢 GREEN — all SLEs above 90%, 0 critical alerts, only routine audit activity
- 🟡 YELLOW — 2 major alerts at HOME-KNAPP (PoE budget warning), all SLEs healthy
- 🔴 RED — 5 critical alerts at HOME-KNAPP (MTU mismatch + VSX keepalive), Time-to-Connect SLE at 72%

## Headline

3–5 sentences. The most-important takeaway. Examples:

- "All quiet overnight — no critical alerts, 2 admin logins, top talker
  is a single client at 8.2 GB."
- "5 critical alerts at HOME-KNAPP — MTU mismatch on aggregation
  link is the priority. 1 admin made 14 config changes overnight."

## Activity

**Central** (N total events, M write actions):
- alice@corp.com — 12 events: 3 logins, 9 reads, 0 writes
- bob@corp.com — 4 events: 1 login, 1 write (`Update Site` at HOME)
- system — 23 events: routine (skip detail)

**Mist** (N total events, M write actions):
- (same shape as Central)

## What's broken right now

**Central** (severity counts: X critical / Y major / Z minor):
- 🔴 [CRITICAL] MTU mismatch — HOME-AGG-SW1-1 1/1/4 ↔ 6100 1/1/15 (9198 vs 1500)
- [MAJOR] VSX keepalive failed — HOME-AGG-SW1-1 loopback0
- ... (top 5)

**Mist** (N alarm types, M total events):
- AP unreachable — AP-Floor-3 (4 events in 18h)
- ... (top 5)

## Top talkers

**Central — top clients:**
| Client | SSID | Site | Traffic (24h) |
|---|---|---|---|
| johns-laptop | Corp-Wifi | HOME | 8.2 GB |
| ... |

**Central — top APs:**
| AP | Site | Clients | Load |
|---|---|---|---|
| AP-Floor-3 | HOME | 47 | 78% |
| ... |

**Mist — top clients / top APs:**
(same shape as Central)

## Insights

**Mist SLE:**
- Worst category: Time-to-Connect at 87% (org-wide)
- Worst site: HOME-KNAPP at 78% aggregate

**Central:**
- Alert category trending up: "Client" alerts +40% vs the 7-day average

## Suggested next steps

1–3 bullets, each pointing at a tool/skill to drill in:
- Run `central-scope-audit` on HOME-KNAPP to investigate the MTU and VSX issues
- Run `mist_get_site_sle(site_id=<HOME-KNAPP id>)` for the SLE breakdown
```

## Caveats

- **No day-over-day delta in phase 1.** "What changed since yesterday"
  is deferred. Don't fabricate it; if the user explicitly asks, say it's
  not in the phase 1 runbook and offer to run a manual comparison via a
  one-shot tool query against a 24-48h-ago window.
- **ClearPass / Apstra / Axis are out of scope for phase 1.** When those
  platforms are configured, skip them silently — don't say "ClearPass
  has nothing to report" because we haven't surveyed it.
- **No anomaly inference beyond what tools already surface.** SLE
  numbers and alert classifications are tool-provided signals; don't
  invent "this looks suspicious" analysis on top of raw data the user
  can verify independently.

## Example queries

> "morning coffee report"
> "give me the morning rundown"
> "what happened overnight"
> "morning digest"
> "who's been in Central / Mist over the last day"
