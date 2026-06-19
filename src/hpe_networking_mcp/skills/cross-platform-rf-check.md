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
tools: [health, mist_invoke_tool, mist_get_self, mist_list_org_sites, mist_list_site_devices_stats, mist_get_site_current_channel_planning, central_get_site_name_id_mapping, central_get_aps, central_get_ap_details]
---

# Cross-platform site RF / channel-planning check

## Objective

Pull per-AP, per-band radio state (channel, bandwidth, power, channel
utilization, noise floor) for one site from **both** Mist and Central,
aggregate per-band channel distribution and airtime pressure, flag
co-channel clusters and elevated noise, present a unified RF report, and
finish with an interactive RF-planner-style coverage map the operator
can explore.

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

## Mist dispatch — CRITICAL

**Mist tools are spec-driven (~1000 tools) and are NOT listed in the
sandbox's resolvable catalog by bare name.** Calling a Mist tool by name
through `call_tool("mist_get_self", ...)` raises `Unknown tool: mist_get_self`
and aborts the whole `execute()` block. Every Mist tool MUST be dispatched
through `mist_invoke_tool`:

```python
# WRONG — raises "Unknown tool: mist_get_self"
resp = await call_tool("mist_get_self", {})

# RIGHT
resp = await call_tool("mist_invoke_tool", {"name": "mist_get_self", "params": {}})
```

This applies to every Mist tool used in this runbook: `mist_get_self`,
`mist_list_org_sites`, `mist_list_site_devices_stats`,
`mist_get_site_current_channel_planning`. Central tools (`central_get_*`)
are top-level registered and CAN be called by bare name via `call_tool`.

## Response shapes

Every tool response is the universal envelope `{ok, status, data, ...}` —
but the **shape of `data` differs by tool**. Guessing wrong (calling
`.get()` on a value that is actually a list, or indexing `["result"]` on a
value that has no such key) crashes the run. Check this table before
iterating any response:

| Tool | `data` shape | Iterate via |
|---|---|---|
| `mist_get_self` (via `mist_invoke_tool`) | dict with `privileges` list | `for p in resp["data"]["privileges"]` — pick `p["scope"] == "org"` for `p["org_id"]` |
| `mist_list_org_sites` (via `mist_invoke_tool`) | bare JSON array of site dicts | `for site in resp["data"]` |
| `mist_list_site_devices_stats` (via `mist_invoke_tool`) | bare JSON array of device-stat dicts | `for ap in resp["data"]` |
| `mist_get_site_current_channel_planning` (via `mist_invoke_tool`) | dict | `resp["data"]["rftemplate"]`, `["band_5"]`, … |
| `central_get_site_name_id_mapping` | `{"items": [ {site_name, site_id, …} ]}` | find the item where `item["site_name"]` matches, take `item["site_id"]` |
| `central_get_aps` | `{"items": [ <ap dict> ]}` (#491) | `for ap in resp["data"]["items"]` |
| `central_get_ap_details` | dict with an inner `result` **dict** | `resp["data"]["result"]["radios"]` (see nested-shape note below) |

**Central `radios[].radioStats` is a LIST, not a dict.** Each radio in
`radios` carries `radioStats` as a single-element list of stat dicts —
calling `.get()` on it raises `'list' object has no attribute 'get'`. Take
`radio["radioStats"][0]` first to reach `channelUtilization` / `noiseFloor`:

```python
# WRONG — 'list' object has no attribute 'get'
util = radio["radioStats"].get("channelUtilization")

# RIGHT — radioStats is a [{...}] list; index [0] first
stats = radio["radioStats"][0] if radio.get("radioStats") else {}
util = stats.get("channelUtilization")
```

Rule of thumb: Mist `*_list_*` tools return `data` as a **bare array**; the
Central monitoring tools wrap their payload under `data["result"]`; the
`*_get_*` / mapping tools return `data` as a **dict**. When unsure,
`isinstance(...)` before you index — never call `.get()` on a value that
might be a list. Central records are camelCase (`deviceName`,
`serialNumber`, `radioStats`); Mist records are snake_case (`name`,
`serial`, `radio_stat`).

## Procedure

Before iterating any tool response, consult the *Response shapes* table
above.

### Step 0 — Determine platform scope from the user's request

**The user's request is the authoritative scope** and overrides this
runbook's default of fan-out across both platforms. Before running any
platform step, parse the user's request for explicit platform language and
capture `user_scope` as a list of platform names:

| User language in the request | `user_scope` |
|---|---|
| "in Mist" / "on Mist" / "from Mist" / "Mist site X" | `["mist"]` |
| "in Central" / "on Central" / "in Aruba Central" / "Aruba" (Central context) | `["central"]` |
| No platform named, OR "across both" / "everywhere" / "Mist and Central" / "all platforms" | `["mist", "central"]` |

`user_scope` gates every subsequent step. If `"mist" not in user_scope`,
the Mist collection steps (2, 4, 5) are skipped entirely. If
`"central" not in user_scope`, the Central collection steps (3, 6) are
skipped entirely.

**Do NOT "still check both per the runbook" when the user named one
platform.** The runbook fans out across platforms only when the user has
not constrained the scope. When they have, this becomes a single-platform
run (the Decision matrix has rows for it). Honor the user's scope; do not
override it with the runbook's default.

### Step 1 — Confirm platform reachability

**Tool:** `health(platform=["mist", "central"])`
**Why:** RF data comes live from each platform's API; a `degraded` or
`unavailable` platform can't contribute and its steps must be skipped.
**Expected result:** `status: ok` for each enabled platform.
**If anomaly:** Mark the unreachable platform and skip its collection
steps. If BOTH are unavailable, stop and surface the errors.

### Step 2 — Resolve the site on Mist

**Tools (BOTH dispatched via `mist_invoke_tool` — see Mist dispatch above):**

1. `mist_invoke_tool(name="mist_get_self", params={})` →
   `resp["data"]["privileges"]` is a list; pick the entry where
   `scope == "org"` to read `org_id`.
2. `mist_invoke_tool(name="mist_list_org_sites", params={"org_id": <org_id>})`
   → `resp["data"]` is a bare list of site dicts.

```python
# Step 2 — Mist site resolution (note the dispatch pattern on every call)
self_resp = await call_tool("mist_invoke_tool", {"name": "mist_get_self", "params": {}})
privileges = self_resp.get("data", {}).get("privileges", [])
org_id = next((p["org_id"] for p in privileges if p.get("scope") == "org"), None)

sites_resp = await call_tool(
    "mist_invoke_tool",
    {"name": "mist_list_org_sites", "params": {"org_id": org_id}},
)
site_match = next(
    (s for s in sites_resp.get("data", []) if s.get("name", "").lower() == site_name.lower()),
    None,
)
```

**Why:** Mist tools are site-scoped by `site_id`; the user gives a name,
so resolve name → id first. The Mist session has an API token but the AI
must read `org_id` out of `mist_get_self`'s `privileges` — it is not in
the `health` response.
**Expected result:** A list of sites; find the one whose `name` matches
the user's `site_name` (case-insensitive) and capture its `id`.
**If anomaly:** No match → Mist has no such site; note it and continue
with Central only. If the user gave no site_name, surface the site list
and ask. If `privileges` carries multiple `scope == "org"` entries, take
the first (single-tenant case is dominant).
**Skip if:** Mist is not enabled or returned `unavailable` in Step 1, OR
`"mist" not in user_scope` (the user scoped to Central only — see Step 0).

### Step 3 — Resolve the site on Central

**Tool:** `central_get_site_name_id_mapping()`
**Why:** Same reason — Central AP queries are scoped by site id. This
tool returns a name → id mapping for every site.
**Expected result:** The mapping contains the user's `site_name`; capture
its site id.
**If anomaly:** No match → Central has no such site; note it and continue
with Mist only.
**Skip if:** Central is not enabled or returned `unavailable` in Step 1,
OR `"central" not in user_scope` (the user scoped to Mist only — see
Step 0).

### Step 4 — Pull Mist per-AP radio stats

**Tool (dispatched via `mist_invoke_tool`):**
`mist_invoke_tool(name="mist_list_site_devices_stats", params={"site_id": ..., "type": "ap"})`
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

**Tool (dispatched via `mist_invoke_tool`):**
`mist_invoke_tool(name="mist_get_site_current_channel_planning", params={"site_id": ...})`
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
`central_get_ap_details(serial_number=...)` for each ONLINE AP. Both are
top-level Central tools — call by bare name through `call_tool`, no
`central_invoke_tool` wrapper needed.
**Why:** Central has no bulk per-AP radio-stats endpoint — you must list
the APs, then fan out one detail call per AP. `central_get_ap_details`
returns a `radios` array; each radio has `band`, `channel`, `bandwidth`,
`power`, and a `radioStats` **list** (single-element). Pull stats via
`radio["radioStats"][0]["channelUtilization"]` and
`["noiseFloor"]` — see *Response shapes* above for the list-vs-dict
footgun.
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

### Step 9 — Render the interactive RF visualization

After the text report, produce a visualization so the operator can
*explore* the RF picture, not just read it. This always comes AFTER the
Step 8 text report — never instead of it.

**Preferred — self-contained HTML artifact** (when the client renders HTML
artifacts, e.g. Claude.ai / Claude Desktop): emit a single self-contained
HTML document — inline CSS + vanilla JS, no external assets, no network
calls, **no gradients or glows** (solid fills with opacity only — it reads
cleaner and renders consistently). Build a proper **RF-planner widget**
that renders **one band at a time**, laid out exactly like this, top to
bottom:

1. **Header.** An eyebrow line `SITE <site_id> · <N> APs · <model(s)>`, the
   title `<site_name> · RF planner`, and — top-right — a band-toggle button
   group (`2.4 GHz` / `5 GHz` / `6 GHz`). Render a button only for a band
   that has reporting radios. Clicking a band sets it active and re-renders
   the whole widget. Colour the active band's accents on an EM-spectrum
   ramp — amber 2.4 GHz, teal 5 GHz, purple 6 GHz.

2. **Stats strip.** Four cards, all for the **active band only**: Active
   band · Avg utilization (colour amber→red as it climbs) · Avg noise
   floor (dBm) · Connected clients (sum).

3. **Floor-plan canvas (SVG, the main panel).** Place each AP in a room on
   a floor plan:
   - If Mist map coordinates are present (`x`, `y`, `map_id` on the
     device-stat record), use them.
   - Otherwise **synthesize a floor plan from the AP names** — do not just
     scatter dots on a blank canvas. Parse a room/area hint from each AP
     name (the segment between the site/platform prefix and the `-AP`
     suffix — e.g. `…-LOBBY-AP` → "Lobby", `…-FLOOR2-AP` → "Floor 2",
     `…-WAREHOUSE-AP` → "Warehouse") and draw labelled room rectangles:
     group plausibly-indoor rooms inside one "Main level" building box and
     place outbuilding-style names (garage, warehouse, annex, shed) as
     their own separate rectangles. Label the canvas "logical layout —
     synthesized from AP names" when there are no real coordinates.
   - A faint coordinate grid sits behind everything.
   - Each AP renders as a marker dot in its room with the room label, the
     transmit power (`12 dBm`), and a channel pill (`Ch 6`).
   - Around each AP draw concentric coverage contours — 3–4 nested
     translucent rings, solid fill with decreasing opacity (NOT gradients),
     radius scaled by band + the radio's `power` dBm (2.4 GHz widest,
     6 GHz tightest). Include a small "Signal contour … far" legend.

4. **AP cards (right sidebar).** One card per AP, **active band only**:
   coloured dot + AP name; a `Ch <n> · <bw> MHz · <power> dBm` row; a
   "Channel busy <util>%" horizontal bar (amber, turning red as it climbs
   past ~60 %); a `Noise <n> dBm · <n> clients` footer.

5. **Channel-plan strip (bottom).** Heading `<active band> channel plan`,
   then one compact pill per AP: `<ap> · ch <n> · <bw> MHz · <power> dBm`.
   Flag any co-channel collision (2+ APs sharing a primary channel, or
   overlapping 80/160 MHz blocks) right here — it is the single most
   actionable thing an RF planner surfaces.

**Interaction rules:**

- **One band at a time** — never expose all three bands' channels at once.
  The header toggle is the only way to switch; the stats strip, canvas, AP
  cards, and channel-plan strip all reflect just the active band.
- Clicking an AP marker (or its card) highlights that AP; if the client's
  artifact runtime supports emitting a follow-up prompt (e.g. Claude
  artifacts), also emit one with the AP name so the operator can drill in
  conversationally.

Keep it dependency-free and compact. If PII tokenization is on, tokenized
values display verbatim — the artifact is a view, it does not detokenize.
Every `<…>` and room name above is a **format placeholder** — render the
operator's real site, AP, and room names from the live data.

**Fallback — rich ASCII spectrum diagram** (when the client does NOT render
HTML artifacts): emit the spatial channel-allocation diagram described
under *Interactive RF visualization* in *Output formatting* below. Same
RF picture, laid out spatially in monospace text.

When unsure whether the client renders artifacts, pick the ASCII fallback —
a raw HTML code block is worse than a clean ASCII diagram.

## Decision matrix

| Condition | Action |
|---|---|
| User scoped to Mist only (`user_scope == ["mist"]`) | Run Steps 0–2, 4, 5; skip 3, 6. Report Mist-only; the headline states scope was user-requested. |
| User scoped to Central only (`user_scope == ["central"]`) | Run Steps 0–1, 3, 6; skip 2, 4, 5. Report Central-only; the headline states scope was user-requested; note RF-template comparison is unavailable (Central has no RF-template concept). |
| Only Mist enabled | Run Steps 2, 4, 5; skip 3, 6. Report Mist-only. |
| Only Central enabled | Run Steps 3, 6; skip 2, 4, 5. Report Central-only; note RF-template comparison is unavailable (Central has no RF-template concept). |
| Site found on one platform only | Report that platform; state explicitly the site was not found on the other. |
| No APs online on either platform | Report the empty state — site resolved, zero online radios. Don't fabricate channel data. |
| Site has only switches (`aos-s` / `cx`), no APs | Stop — there is no RF state to report; tell the user the site is wired-only. |
| 100+ Mist APs or 30+ Central APs | Proceed but cap the Central per-AP fan-out and state the cap + total count in the report. |

## Output formatting

Lead with a one-line headline (`<site>: <connected>/<total> APs online |
2.4GHz: <channels> | 5GHz: ... | 6GHz: ...`), then a per-band section,
then a per-AP table, then recommendations. When `user_scope` covered only
one platform, the `Platforms:` line MUST include `(scope: user-requested
<platform>)` so the operator can see the run honored their constraint.
Match this structure:

```
# RF Check — <site name>

<headline line>

Platforms: queried=<n>, matched=<n>   (scope: user-requested central)
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

## Interactive RF visualization

This is Step 9's output — it comes AFTER the text report above, never
instead of it. Prefer the self-contained HTML artifact (see Step 9); use
this ASCII spectrum diagram as the fallback when the client can't render
artifacts.

The ASCII fallback lays radios out spatially on a channel axis per band —
block width proportional to bandwidth so channel overlaps are visible:

```
RF spectrum — <site name>

5 GHz
  ch:   36         40    44    48    …   149        153   157
        [HQ-LOBBY-AP  80MHz ]                [HQ-FL2-AP  80MHz ]
              [HQ-FL1-AP  80MHz ]
        └─ 3 radios on ch36  ⚠ co-channel
  util: ▇ 74%   ▃ 52%        …   ▁ 18%
  allowed-but-unused: 60, 64, 100, 104

6 GHz
  ch:   37    53    69    …
        [HQ-LOBBY-AP 80MHz]
  util: ▃ 41%

2.4 GHz
  ch:   1              6              11
        [AP1 20][AP4 20]       [AP2 20]
  util: ▃ 48%          ▁ 22%          ▃ 55%

util key:  ▁ <40%    ▃ 40–70%    ▇ ≥70%
```

The block label carries AP name + bandwidth; stacked rows show co-channel
overlap; the util sparkline under each band conveys the airtime picture.
Order the bands 5 → 6 → 2.4 — operators triage 5 / 6 GHz first.

## Example

> "how are my 5 and 6 GHz channels operating at HQ?" → `user_scope=["mist","central"]` (no platform named)
> "run an RF check on site BRANCH-1" → `user_scope=["mist","central"]`
> "any co-channel interference across Mist and Central at the main office?" → `user_scope=["mist","central"]` (both named)
> "Do an RF check at HQ in Central" → `user_scope=["central"]` (Mist steps skip)
> "RF check on Mist site BRANCH-1" → `user_scope=["mist"]` (Central steps skip)
