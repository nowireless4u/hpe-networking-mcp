---
name: wlan-sync-validation
title: Mist ↔ Central WLAN consistency check
description: |
  Compare WLAN definitions between Mist and Central to surface configuration
  drift — same SSID, different security mode; same network, different VLAN
  assignment; one platform missing a WLAN entirely. Use when the user asks
  "are our WLANs in sync?", "did the WLAN sync run cleanly?", or after
  running `manage_wlan_profile` to verify the result.
platforms: [mist, central]
tags: [wlan, sync, drift-detection, audit]
tools: [health, mist_invoke_tool, central_invoke_tool, manage_wlan_profile]
---

# Mist ↔ Central WLAN consistency check

## Objective

Identify WLAN configuration drift between Mist and Central — SSIDs that
exist on one platform but not the other, or that exist on both but with
divergent settings. Output a per-WLAN comparison table the operator can
act on.

This skill is *read-only*. It identifies drift; it does NOT correct it.
Use `manage_wlan_profile` to apply corrections after reviewing this report.

## Prerequisites

- Both Mist AND Central must be enabled and reachable. If either returns
  `unavailable`, this skill cannot complete — surface the error and stop.
- The user has identified the comparison scope: organization-wide, a
  specific site, or a specific WLAN name. Default to organization-wide if
  the user doesn't specify.

## Procedure

### Step 1 — Confirm both platforms reachable

**Tool:** `health(platform=["mist", "central"])`
**Why:** The skill's whole premise is comparing live configs from both
platforms. A `degraded` Mist or Central means we can't trust the comparison.
**Expected result:** Both `status: ok`.
**If anomaly:** Stop. Tell the user which platform is unreachable and that
the comparison can't run.

### Step 2 — Pull Mist WLANs

**Tool:** `mist_get_org_wlans(org_id=<from health>)` — or scoped to a site
via `mist_get_site_wlans(site_id=...)` if the user gave a site.
**Why:** Mist's WLAN catalog is the source-of-truth for the comparison.
**Expected result:** A list of WLANs with `ssid`, `enabled`, `auth.type`,
`auth.psk` (presence only — never log the actual key), `vlan_ids`,
`interface`, `band`, `hide_ssid`.
**Note:** If Mist returns 100+ WLANs the operator probably wants a more
specific scope. Surface the count and ask before continuing.

### Step 3 — Pull Central WLANs

**Tool:** `central_get_wlans()` (or scope to a site via `central_get_site_wlans(site_name=...)`)
**Why:** Central's view of the same WLAN universe.
**Expected result:** A list with `ssid`, `enabled`, `security_type`,
`vlan`, `band`, `broadcast_ssid`.

### Step 4 — Build the comparison index

Key both lists by SSID (case-insensitive). For each SSID, classify into one
of four buckets:

| Bucket | Meaning |
|---|---|
| **In sync** | Present on both, all compared fields match |
| **Mist only** | SSID exists in Mist, absent from Central |
| **Central only** | SSID exists in Central, absent from Mist |
| **Drift** | Present on both but at least one field differs |

### Step 5 — Compute the diff for "Drift" SSIDs

For each drift SSID, list the fields that differ. Map the platform-native
field names to a common comparison vocabulary:

| Common name | Mist field | Central field |
|---|---|---|
| Auth type | `auth.type` (e.g. `psk`, `eap`, `open`) | `security_type` (e.g. `wpa2_psk`, `wpa2_enterprise`, `open`) |
| VLAN | `vlan_ids` (list) | `vlan` (single int) |
| Hidden SSID | `hide_ssid` (bool) | `broadcast_ssid` (bool — INVERTED) |
| Enabled | `enabled` (bool) | `enabled` (bool) |
| Band | `band` (`24`, `5`, `6`, `both`) | `band` (`2.4ghz`, `5ghz`, `6ghz`, `dual`) |

**Note the inverted `hide_ssid` / `broadcast_ssid` semantics.** A Mist WLAN
with `hide_ssid: true` and a Central WLAN with `broadcast_ssid: false`
ARE in sync — flag this as a known-quirk in the output.

### Step 6 — Format the comparison report

See *Output formatting* below.

## Decision matrix

| Condition | Action |
|---|---|
| Either platform unavailable | Stop. Cannot compare without both. |
| 0 WLANs on either side | Surface the empty result; the user may have hit the wrong scope |
| All SSIDs in sync | One-line summary: "N WLANs in sync — no drift" |
| Drift only on `hide_ssid` semantics | Note explicitly that this is a known terminology quirk, not real drift |
| 100+ WLANs returned | Ask the user to narrow scope before generating the full report |

## Output formatting

```
## WLAN sync report — <scope: org or site name>
**Captured:** <ISO timestamp>
**Mist WLANs:** N | **Central WLANs:** M

### In sync (X)
- corp
- guest
- iot

### Mist only (1)
- legacy-mist-test (consider deleting from Mist or pushing to Central)

### Central only (1)
- emergency-byod (consider pushing to Mist or deleting from Central)

### Drift (1)
- corp:
    - vlan: Mist=[10] vs Central=20  ← align these
    - auth: Mist=psk vs Central=wpa2_enterprise  ← MAJOR — different security
```

Lead with the count summary; the user reads it first to decide whether to
keep going. Always group by bucket so "everything is fine" is one glance.

## Example queries that should trigger this skill

> "are our WLANs in sync between Mist and Central?"
> "did the WLAN sync run cleanly?"
> "audit WLAN drift for site HOME"
> "compare WLANs across platforms"
