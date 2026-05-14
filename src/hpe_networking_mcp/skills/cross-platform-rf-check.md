---
name: cross-platform-rf-check
title: Cross-platform site RF / channel-planning check
description: |
  TRIGGERS — call this when the user asks about RF health, channel
  planning, spectrum, or radio state across a site: "how are my 5/6 GHz
  channels operating", "check RF at site HQ", "channel-planning audit",
  "any co-channel interference", "is my airtime saturated", "RF health
  for Mist and Central". Replicates the `site_rf_check` cross-platform
  tool as a runbook so it works in CODE mode, where `site_rf_check` is
  NOT registered. Use this instead of reaching for a single platform's
  RF tools and stopping — the whole point is one site, both platforms.
platforms: [mist, central]
tags: [rf, channel-planning, spectrum, wireless, audit]
tools: [health, mist_list_org_sites, mist_list_site_devices_stats, mist_get_site_current_channel_planning, central_get_site_name_id_mapping, central_get_aps, central_get_ap_details]
---

# Cross-platform site RF / channel-planning check

## Objective

Pull per-AP, per-band radio state (channel, bandwidth, power, channel
utilization, noise floor) for one site from **both** Mist and Central,
aggregate per-band channel distribution and airtime pressure, flag
co-channel clusters and elevated noise, and present a unified RF report.

This is the code-mode runbook equivalent of the `site_rf_check`
cross-platform tool. That tool is only registered in `dynamic` mode; in
`code` mode (the default since v3.0.0.0) it does not exist, so the AI
must compose the same answer from per-platform tools. This skill is that
composition — follow it instead of guessing.

This skill is *read-only*. It reports RF state and recommendations; it
does NOT change channels, power, or RF templates.

## Prerequisites

- At least one of Mist or Central must be enabled and reachable. The
  skill adapts to whichever is present — it does not require both.
- The user has supplied a `site_name`. If they have not, list candidate
  sites (Step 2 / Step 3 enumerate them) and ask which one.

## Procedure

### Step 1 — Confirm platform reachability

**Tool:** `health(platform=["mist", "central"])`
**Why:** RF data comes live from each platform's API; a `degraded` or
`unavailable` platform can't contribute and its steps must be skipped.
**Expected result:** `status: ok` for each enabled platform.
**If anomaly:** Mark the unreachable platform and skip its collection
steps. If BOTH are unavailable, stop and surface the errors.

### Step 2 — Resolve the site on Mist

**Tool:** `mist_list_org_sites(org_id=...)`
**Why:** Mist tools are site-scoped by `site_id`; the user gives a name,
so resolve name → id first. The org_id comes from `health` or the Mist
session context.
**Expected result:** A list of sites; find the one whose `name` matches
the user's `site_name` (case-insensitive) and capture its `id`.
**If anomaly:** No match → Mist has no such site; note it and continue
with Central only. If the user gave no site_name, surface the site list
and ask.
**Skip if:** Mist is not enabled or returned `unavailable` in Step 1.

### Step 3 — Resolve the site on Central

**Tool:** `central_get_site_name_id_mapping()`
**Why:** Same reason — Central AP queries are scoped by site id. This
tool returns a name → id mapping for every site.
**Expected result:** The mapping contains the user's `site_name`; capture
its site id.
**If anomaly:** No match → Central has no such site; note it and continue
with Mist only.
**Skip if:** Central is not enabled or returned `unavailable` in Step 1.

### Step 4 — Pull Mist per-AP radio stats

**Tool:** `mist_list_site_devices_stats(site_id=..., type="ap")`
**Why:** This is the live per-AP radio snapshot. Each connected AP carries
a `radio_stat` object keyed `band_24` / `band_5` / `band_6`; each band
entry has `channel`, `bandwidth`, `power`, `usage` (channel utilization
%), `noise_floor`, `num_clients`.
**Expected result:** A list of AP device-stat records. `status ==
"connected"` APs have populated `radio_stat`; offline APs do not.
**If anomaly:** 100+ APs — the site is large; proceed but note the count
in the report. Empty list — no APs at the site or none online.
**Skip if:** Mist site was not resolved in Step 2.

### Step 5 — Pull the Mist channel-planning template

**Tool:** `mist_get_site_current_channel_planning(site_id=...)`
**Why:** Gives the RF template's *allowed* channels per band, so the
report can flag "allowed but unused" channels even when few APs are
online. Look for `rftemplate.band_24/band_5/band_6.channels` and
`rftemplate_name`.
**Expected result:** A current-RRM object with the template name and the
per-band allowed-channel lists.
**If anomaly:** No template / empty — note "no RF template" and skip the
allowed-channel comparison; channel distribution still works.
**Skip if:** Mist site was not resolved in Step 2.

### Step 6 — Pull Central APs, then per-AP RF detail

**Tool:** `central_get_aps(site_id=...)` to list the site's APs, then
`central_get_ap_details(serial_number=...)` for each ONLINE AP.
**Why:** Central has no bulk per-AP radio-stats endpoint — you must list
the APs, then fan out one detail call per AP. `central_get_ap_details`
returns a `radios` array; each radio has `band`, `channel`, `bandwidth`,
`power`, and `radioStats` with `channelUtilization` and `noiseFloor`.
**Expected result:** An AP list filtered to the site; per-AP detail
records with a populated `radios` array on ONLINE APs.
**If anomaly:** Many APs — cap the per-AP fan-out at ~30 ONLINE APs to
bound cost, and state the cap in the report. Offline APs — list them but
skip the detail call (no live radio data).
**Skip if:** Central site was not resolved in Step 3.

### Step 7 — Normalize, aggregate, analyze

Normalize band labels to three canonical keys: `2.4` (from `band_24`,
`24`, `2.4ghz`), `5` (`band_5`, `5ghz`), `6` (`band_6`, `6ghz`).

For each band, across every reporting radio on both platforms:
- **Channel distribution** — count of radios per primary channel.
- **Utilization** — average and peak channel-utilization %.
- **Noise floor** — average noise floor in dBm.

Then flag:

| Signal | Threshold | Recommendation |
|---|---|---|
| Co-channel cluster | 3+ APs on the same primary channel, 5 or 6 GHz | "N APs on channel C — stagger via RRM or the RF template" |
| Airtime pressure | peak channel utilization ≥ 70% | "peak util N% — check the busiest AP" |
| Elevated noise | average noise floor > −70 dBm | "noise floor N dBm is elevated — investigate non-Wi-Fi interference" |
| Allowed-but-unused | Mist template allows channels with zero active radios | "channels X, Y allowed but unused" |

### Step 8 — Format the report

See *Output formatting* below.

## Decision matrix

| Condition | Action |
|---|---|
| Only Mist enabled | Run Steps 2, 4, 5; skip 3, 6. Report Mist-only. |
| Only Central enabled | Run Steps 3, 6; skip 2, 4, 5. Report Central-only; note RF-template comparison is unavailable (Central has no RF-template concept). |
| Site found on one platform only | Report that platform; state explicitly the site was not found on the other. |
| No APs online on either platform | Report the empty state — site resolved, zero online radios. Don't fabricate channel data. |
| Site has only switches (`aos-s` / `cx`), no APs | Stop — there is no RF state to report; tell the user the site is wired-only. |
| 100+ Mist APs or 30+ Central APs | Proceed but cap the Central per-AP fan-out and state the cap + total count in the report. |

## Output formatting

Lead with a one-line headline (`<site>: <connected>/<total> APs online |
2.4GHz: <channels> | 5GHz: ... | 6GHz: ...`), then a per-band section,
then a per-AP table, then recommendations. Match this structure:

```
# RF Check — <site name>

<headline line>

Platforms: queried=<n>, matched=<n>
Mist RF template: <name>   (omit if Central-only)

### 2.4 GHz — <radios_active> radio(s) across <ap_count> AP(s)
util avg <n>% / peak <n>% · noise <n> dBm
  Channel occupancy:
    ch   1  │ ■■■■■ (3)
    ch   6  │ ■■ (1)
    ch  11  │ ■■■ (2)
  Allowed but unused: <channels>

### 5 GHz — ...
    ch  36  │ ■■■■■ (4) ⚠ co-channel
    ...

### 6 GHz — ...

## Per-AP radio snapshot

  AP            Platform  Model      2.4 GHz              5 GHz                6 GHz
  ────────────  ────────  ─────────  ───────────────────  ───────────────────  ──────
  HQ-LOBBY-AP   mist      AP45       ch6 20MHz 8dBm 22%u  ch36 80MHz 17dBm 31%u  —
  HQ-FLOOR2-AP  central   635        ch1 20MHz ...        ch149 80MHz ...        ch37 ...

## Recommendations

- 5 GHz — 3 APs on channel 36; consider staggering via RRM or the RF template.
- 5 GHz — peak channel utilization 74% (>=70% indicates airtime pressure; check the busiest AP).
```

Keep it scannable — the operator should read the headline + recommendations
in a few seconds and drill into the band sections only if needed.

## Example

> "how are my 5 and 6 GHz channels operating at HQ?"
> "run an RF check on site BRANCH-1"
> "any co-channel interference across Mist and Central at the main office?"
