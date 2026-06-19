---
name: central-site-dashboard
title: Aruba Central single-site operational dashboard — health/devices/clients/alerts + ClearPass NAC overlay, rendered live
description: |
  PRIMARY TRIGGER — invoke whenever the operator asks to build, render, draw,
  show, or visualize a DASHBOARD, status board, scorecard, or overview for ONE
  Aruba Central site. This is the fast path: a fixed data-gather runbook (the
  exact response-envelope unwraps baked in) plus a Prefab Generative-UI render —
  it replaces ad-hoc dashboard building, which burns ~20+ exploratory
  round-trips rediscovering schemas and fighting the {ok,status,data} envelope.

  Match phrases include: "dashboard for site HQ", "show me a dashboard for
  <site>", "render a status board for <site>", "site overview for <site>",
  "visualize site health for <site>", "give me a scorecard for <site>",
  "draw a dashboard of <site>'s devices and alerts", "show NAC / who's
  connected at <site>".

  Scope: ONE Central site — health score, device status by type, client counts,
  active alerts (Central) PLUS a ClearPass NAC overlay of the active sessions on
  that site's APs (active-client count, breakdown by enforcement role + SSID,
  session table). The ClearPass panel is best-effort: it's skipped cleanly when
  ClearPass is disabled/unreachable. Single-site only — for cross-platform
  health use infrastructure-health-check; voice/call-quality use
  central-ucc-quality; config drift use central-scope-audit.
platforms: [central, clearpass]
tags: [central, clearpass, dashboard, visualization, site, health, devices, alerts, nac, sessions, monitoring, generative-ui]
tools: [health, central_invoke_tool, central_get_site_name_id_mapping, central_get_site_health, central_get_devices, central_get_alerts, clearpass_invoke_tool, clearpass_get_sessions, generate_prefab_ui, search_prefab_components]
---

# Aruba Central single-site operational dashboard

## Objective

Produce one live, interactive dashboard for a single Aruba Central site —
overall health score, device status broken out by type, client counts, and the
active alerts, PLUS a ClearPass NAC overlay (the active sessions on that site's
APs) — by running a fixed gather and rendering the result through the
`generate_prefab_ui` Generative-UI tool. The whole point is to skip the
exploratory flailing: this runbook already knows the exact tools, the
response-envelope shapes, the cross-platform correlation key, and the dashboard
layout, so the model fetches once and renders once.

## Prerequisites

- Central is configured and reachable (`health(platform="central")` if unsure).
- The operator has named a site (e.g. "HQ", "BRANCH-1"). If they only said
  "a dashboard" with no site, ask which site first.
- ClearPass is OPTIONAL — the NAC overlay is best-effort. If ClearPass is
  disabled or unreachable, the dashboard still renders with the Central panels
  and notes that NAC data was unavailable. Never let a missing ClearPass fail
  the whole dashboard.
- Generative UI renders only in an MCP-Apps host (Claude Desktop / claude.ai /
  ChatGPT). In a non-apps client (e.g. Claude Code) `generate_prefab_ui` is a
  no-op visual — Step 3's text summary is then the deliverable, so ALWAYS emit
  it regardless.

## Response-shape contract (READ FIRST — this is what trips ad-hoc attempts)

Every `central_*` read returns the standard envelope; `<platform>_invoke_tool`
wraps results the same way. Read the inner `data`. As of v3.4.x the Central
collection reads share **one uniform shape** — rows are always under
`data["items"]` (#491) — so you no longer special-case bare lists, name-keyed
dicts, or empty-result strings:

```text
central_get_site_name_id_mapping  -> data is {"items": [ {site_name, site_id, health, total_devices, total_clients, total_alerts} ]}
central_get_site_health           -> data is {"items": [ <site dict> ]}      -> take data["items"][0]
central_get_devices               -> data is {"items": [ <device dict> ]}    -> empty is {"items": []} (no "No devices" string)
central_get_alerts                -> data is {"items": [...], total, next_cursor} -> rows under data["items"]
clearpass_get_sessions            -> data is {_embedded:{items:[...]}, count, _links} -> rows under data["_embedded"]["items"]
```

`central_get_alerts` **requires** `site_id` — resolve it first (Step 0).

**ClearPass correlation (the cross-platform key):** ClearPass has no "site"
concept, so scope its sessions to the site by the NAS. The proven correlation:
filter active sessions where the session's `ap_name` is one of the site's AP
names (the AP names from the Central device gather). Verified mechanics:

- **Active only:** `{"acctstoptime": {"$exists": false}}` — this is the ONLY
  filter that works for "still connected" (states `active`/`stale`). `{"state":
  ...}`, `$ne`, and empty-string filters silently return nothing. Without this
  you get the full ~80k-row historical accounting table.
- **Site scope:** AND a second clause `{"ap_name": {"$in": [<site AP names>]}}`.
  ClearPass does **not** support `$or`, so this is wireless-AP correlation only
  — wired 802.1X sessions (switch NAS) are out of v1 scope (see limitation in
  Notes).
- **Count from the data, not `calculate_count`:** paginate (`limit`/`offset`)
  the full active set and derive `active_count = len(all)` so it matches the
  `by_role` / `by_ssid` breakdowns. Using `calculate_count` with a capped
  `limit` would report a total larger than the rows the breakdowns actually saw
  — a silent under-count of the breakdowns. Only the rendered session *table* is
  display-capped (first 100, flagged by `sessions_truncated`); the count and
  breakdowns stay complete unless pagination hits the 10k runaway guard, in which
  case set `aggregate_truncated` and surface that the count/breakdowns are partial
  (never present a capped aggregate as complete).
- **Role field:** use `arubauserrole` (or `tipsrole`) for the role breakdown —
  `role_name` is empty on these records.

Sandbox rules (code mode): sequential `await` only (no `asyncio.gather`); no
`datetime.now()` / `time.time()` / file I/O. `import json` is available. Parse
with plain builtins (no `collections.Counter` — group with a plain dict).

## Procedure

### Step 0 — Resolve the site name to a site_id

`central_get_site_health(site_name="<NAME>")` returns the `site_id` AND every
metric in one call, so it doubles as the resolver. Only fall back to
`central_get_site_name_id_mapping` when the operator's name is partial or
ambiguous and you need to pick the exact key.

**If the health `data["items"]` comes back empty:** the name didn't match (a
bogus site name returns `{"items": []}`, not an error). Call
`central_get_site_name_id_mapping`, show the operator the available site names
(case-insensitive contains-match on their input), and ask them to confirm.

### Step 1 — Gather everything in one execute block

One block, sequential awaits, returns exactly what the dashboard needs (trim
rows so the payload stays small):

```python
def _unwrap(r):
    # Standard envelope -> inner data. Tolerates an already-unwrapped value.
    return r["data"] if isinstance(r, dict) and "data" in r and "ok" in r else r

SITE_NAME = "HQ"  # <- replace with the operator's site name

health = _unwrap(await call_tool("central_invoke_tool",
    {"name": "central_get_site_health", "params": {"site_name": SITE_NAME}}))
health_items = health.get("items", []) if isinstance(health, dict) else []
if not health_items:
    return {"error": f"site {SITE_NAME!r} not found"}   # -> Step 0 fallback
site = health_items[0]
site_id = site["site_id"]
# `or {}` (not `.get(k, {})`): Central may return a section as null, not absent
# — `.get("metrics", {})` would hand back None and the next `.get` would crash.
metrics = site.get("metrics") or {}

devices_raw = _unwrap(await call_tool("central_invoke_tool",
    {"name": "central_get_devices", "params": {"site_id": str(site_id)}}))
devices = devices_raw.get("items", []) if isinstance(devices_raw, dict) else []   # empty -> {"items": []}

alerts_raw = _unwrap(await call_tool("central_invoke_tool",
    {"name": "central_get_alerts", "params": {"site_id": str(site_id), "limit": 25}}))
alert_rows = alerts_raw.get("items", []) if isinstance(alerts_raw, dict) else []

# Trim to the fields the dashboard shows (keeps the render payload compact).
device_rows = [
    {"name": d.get("name"), "type": d.get("device_type"), "model": d.get("model"),
     "status": d.get("status"), "ip": d.get("ipv4")}
    for d in devices
]
alert_list = [
    {"severity": a.get("severity"), "name": a.get("name"),
     "device_type": a.get("device_type"), "summary": a.get("summary"),
     "created_at": a.get("created_at"), "status": a.get("status")}
    for a in alert_rows
]

# --- ClearPass NAC overlay (best-effort) ---
# nac["status"] distinguishes the three cases so the render + walkthrough don't
# conflate them: "ok" (queried — panel renders, even with 0 sessions),
# "no_aps" (wired-only/empty site — nothing to correlate), "unavailable"
# (ClearPass disabled/unreachable — call raised).
import json
ap_names = sorted({r["name"] for r in device_rows if r.get("type") == "ACCESS_POINT" and r.get("name")})
nac = {"status": "no_aps", "active_count": 0, "by_role": {}, "by_ssid": {},
       "sessions": [], "sessions_truncated": False, "aggregate_truncated": False}
if ap_names:
    try:
        cp_filter = {"acctstoptime": {"$exists": False}, "ap_name": {"$in": ap_names}}
        # Paginate the FULL active set so active_count + by_role + by_ssid all come
        # from the SAME complete data — calculate_count would let the count exceed
        # what the breakdowns saw. Only the rendered table is display-capped (below).
        # CAP is a runaway guard; if we hit it the aggregates are themselves partial,
        # so flag aggregate_truncated and surface it (don't present capped counts as complete).
        all_sess, offset, PAGE, CAP = [], 0, 500, 10000
        while offset < CAP:
            cp = _unwrap(await call_tool("clearpass_invoke_tool", {"name": "clearpass_get_sessions",
                "params": {"filter": json.dumps(cp_filter), "limit": PAGE, "offset": offset}}))
            page = (cp.get("_embedded") or {}).get("items", []) if isinstance(cp, dict) else []
            all_sess.extend(page)
            if len(page) < PAGE:
                break
            offset += PAGE
        else:
            nac["aggregate_truncated"] = True                # hit CAP without exhausting — counts/breakdowns are partial
        nac["status"] = "ok"
        nac["active_count"] = len(all_sess)                  # consistent with the breakdowns below
        for s in all_sess:
            role = s.get("arubauserrole") or s.get("tipsrole") or "(none)"
            ssid = s.get("ssid") or "(none)"
            nac["by_role"][role] = nac["by_role"].get(role, 0) + 1
            nac["by_ssid"][ssid] = nac["by_ssid"].get(ssid, 0) + 1
        nac["sessions"] = [
            {"user": s.get("username"), "mac": s.get("mac_address"), "ap": s.get("ap_name"),
             "ssid": s.get("ssid"), "role": s.get("arubauserrole") or s.get("tipsrole"),
             "ip": s.get("framedipaddress"), "uptime_s": s.get("acctsessiontime")}
            for s in all_sess[:100]                          # table display cap only
        ]
        nac["sessions_truncated"] = len(all_sess) > 100      # count + breakdowns stay complete
    except Exception:
        nac["status"] = "unavailable"

return {
    "site": {"name": site.get("name"), "site_id": site_id,
             "address": site.get("address"),
             "health": metrics.get("health") or {}},         # {Poor,Fair,Good,Summary}
    "device_summary": metrics.get("devices") or {},          # {Summary:{...}, Details:{by type}}
    "client_summary": (metrics.get("clients") or {}).get("Summary") or {},  # {Poor,Fair,Good,Total}
    "alert_summary": metrics.get("alerts") or {},            # {Critical, Total}
    "devices": device_rows,
    "alerts": alert_list,
    "nac": nac,                                              # ClearPass overlay (status: ok | no_aps | unavailable)
}
```

### Step 2 — Render the dashboard (Generative UI)

Call `generate_prefab_ui` directly (top-level tool). Pass the Step 1 return as
the `data` argument — **each top-level key becomes a global** inside `code`
(`site`, `device_summary`, `client_summary`, `alert_summary`, `devices`,
`alerts`, `nac`). There is NO `data` variable in the sandbox.

If you need to confirm component names, call `search_prefab_components` ONCE
with a broad query — don't fan out. The common set for this board:

- `metric` — KPI cards: Health score, Devices total, Clients total, Alerts (show Critical as the delta/secondary).
- `data_table` — the device list (name / type / model / status / ip) and the alert list (severity / name / device_type / created_at).
- `charts` — a small bar chart of `device_summary["Details"]` (Good/Fair/Poor per device type), or use `badge` rows if a chart is overkill.
- `badge` / `dot` — status pills (Good=green, Fair=amber, Poor/Down=red; Critical alerts=red).
- `column` / `row` / `grid` + `heading` — layout.
- ClearPass NAC panel (render only when `nac["status"] == "ok"`): a `metric` for
  the active-client count, two small `data_table`s for the role + SSID
  breakdowns, and a `data_table` of `nac["sessions"]`. Gate the whole panel on
  `status == "ok"` so it disappears (not errors) for `no_aps` / `unavailable`;
  at `ok` with 0 active it still renders (an informative "0 active clients").
  When `nac["sessions_truncated"]`, add a line noting the table shows the first
  100 while the count + breakdowns are complete. When `nac["aggregate_truncated"]`
  (a very large site that hit the 10k pagination guard), add a clear warning that
  the count AND breakdowns are themselves partial — don't present them as complete.

Build with the context-manager form (children register onto the open
container), assign a `PrefabApp`, e.g.:

```python
with Column(gap=4) as view:
    Heading(f"{site['name']} — site dashboard")
    with Row(gap=4):
        Metric(label="Health", value=site["health"].get("Summary"))
        Metric(label="Devices", value=(device_summary.get("Summary") or {}).get("Total"))
        Metric(label="Clients", value=client_summary.get("Total"))
        Metric(label="Alerts", value=alert_summary.get("Total"),
               description=f'{alert_summary.get("Critical", 0)} critical')
    Heading("Devices")
    DataTable(rows=devices)
    Heading("Active alerts")
    DataTable(rows=alerts)
    if nac["status"] == "ok":   # APs queried — render even at 0 active (informative)
        Heading("ClearPass — active NAC sessions on this site's APs")
        with Row(gap=4):
            Metric(label="Active clients", value=nac["active_count"])
        if nac["aggregate_truncated"]:
            Text(f"⚠ Capped at {nac['active_count']} sessions — count and breakdowns below are PARTIAL.")
        DataTable(rows=[{"role": k, "clients": v} for k, v in nac["by_role"].items()])
        DataTable(rows=[{"ssid": k, "clients": v} for k, v in nac["by_ssid"].items()])
        if nac["sessions_truncated"]:
            note = "counts above are partial" if nac["aggregate_truncated"] else "counts above are complete"
            Text(f"Showing first {len(nac['sessions'])} of {nac['active_count']} active sessions ({note}).")
        DataTable(rows=nac["sessions"])
app = PrefabApp(view=view)
```

(Use the exact component signatures from `search_prefab_components`; the above
is the shape, not a guaranteed API.)

### Step 3 — Walkthrough beneath the board (ALWAYS emit)

Whether or not the widget renders, write a short text summary so the answer is
useful in every client: health score and trend, device count with any Poor/Down
devices named, client count, and the alert count leading with criticals (name
the critical alerts). Then add a NAC line keyed on `nac["status"]`:
- `ok` → "N active clients on the site's APs" + the dominant role/SSID (or
  "0 active clients on the site's APs" when N is 0).
- `no_aps` → "this site has no APs — NAC overlay not applicable" (do NOT say
  ClearPass was unreachable).
- `unavailable` → "ClearPass not reachable — NAC overlay omitted".

In a non-apps client this text IS the dashboard.

## Unhappy paths (trace these)

- **Site not found** — `health["items"]` empty → Step 0 fallback (list names, ask).
- **No devices** — `central_get_devices` returns `{"items": []}` →
  `devices = []`; the table renders empty, the summary says so.
- **No alerts** — `data["items"]` is `[]` → "No active alerts" (a clean, good
  state, not an error).
- **Generative UI unavailable** — `generate_prefab_ui` no-ops in non-apps
  clients; Step 3's text summary covers it. Never let a non-rendering widget
  leave the operator with nothing.
- **Stacked switches** — `aos-s`/`cx` stacks share a `stack_id`; the device
  list may show stack members. That's fine for an overview; don't dedupe.
- **ClearPass disabled / unreachable** — the `try` sets `nac["status"] =
  "unavailable"`; the panel is omitted and the walkthrough says NAC was
  unreachable. The Central dashboard still renders fully.
- **Site has no APs** (wired-only / empty site) — `ap_names` is empty, the
  ClearPass call is skipped, `nac["status"] = "no_aps"`. Distinct from
  unreachable: the walkthrough says NAC is "not applicable", NOT "unreachable".
- **APs exist but zero active sessions** — `nac["status"] = "ok"` with
  `active_count == 0`; the panel renders "0 active clients" (a clean state),
  not an error.
- **Wired sessions not shown** — correlation is by `ap_name` (wireless). Switch
  802.1X sessions (matched only by `nasipaddress`) are NOT in this panel because
  ClearPass rejects `$or`; call that out if the operator expects wired clients.

## When NOT to use this skill

- Multi-site / org-wide boards, or overlays from Mist / UXI — out of scope;
  gather per-platform and compose manually, or use `infrastructure-health-check`
  for a cross-platform health snapshot. (Central + ClearPass single-site IS in
  scope — that's this skill.)
- Voice / call-quality dashboards → `central-ucc-quality`.
- Config drift / scope assignment review → `central-scope-audit` or
  `central-scope-visualizer`.
- RF / channel planning → `cross-platform-rf-check`.

## Notes

- Device types in Central: `ap` (access points), `aos-s` / `cx` (switches —
  NOT APs), `gateways`. The health `Details` tree already buckets them
  (Access Points / Switches / Gateways / Bridges / Edge VMs).
- This runbook is the code-mode equivalent of pointing `generate_prefab_ui` at
  a known data shape — it exists so small/local models don't have to author the
  gather + unwrap + render from scratch.
- ClearPass session rows carry client PII (username, MAC, framed IP). That's
  expected in the operator's own dashboard — the operator is the trust-boundary
  holder, and the PII-tokenization middleware redacts these in transit when
  enabled. Do NOT paste real session values into chat outside the rendered
  board; keep the Step 3 walkthrough aggregate (counts, roles, SSIDs).
- ClearPass→site correlation is by `ap_name` matching the site's Central AP
  device names. It depends on ClearPass and Central naming the same APs
  consistently; an AP whose ClearPass `ap_name` differs from its Central
  `name` won't be counted. Wired correlation (`nasipaddress`) is a future
  extension blocked on ClearPass not supporting `$or` in one filter.
