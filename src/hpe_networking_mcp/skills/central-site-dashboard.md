---
name: central-site-dashboard
title: Aruba Central single-site operational dashboard — gather health/devices/clients/alerts, render a live board
description: |
  PRIMARY TRIGGER — invoke whenever the operator asks to build, render, draw,
  show, or visualize a DASHBOARD, status board, scorecard, or overview for ONE
  Aruba Central site. This is the fast path: a fixed data-gather runbook (3-4
  tool calls with the exact response-envelope unwraps baked in) plus a Prefab
  Generative-UI render — it replaces ad-hoc dashboard building, which burns
  ~20+ exploratory round-trips rediscovering schemas and fighting the
  {ok,status,data} envelope.

  Match phrases include: "dashboard for site HQ", "show me a dashboard for
  <site>", "render a status board for <site>", "site overview for <site>",
  "visualize site health for <site>", "give me a scorecard for <site>",
  "draw a dashboard of <site>'s devices and alerts".

  Scope: ONE Central site (health score, device status by type, client counts,
  active alerts). Central only — no Mist / ClearPass / UXI overlay in this
  version. For voice/call-quality use central-ucc-quality; for config drift use
  central-scope-audit.
platforms: [central]
tags: [central, dashboard, visualization, site, health, devices, alerts, monitoring, generative-ui]
tools: [health, central_invoke_tool, central_get_site_name_id_mapping, central_get_site_health, central_get_devices, central_get_alerts, generate_prefab_ui, search_prefab_components]
---

# Aruba Central single-site operational dashboard

## Objective

Produce one live, interactive dashboard for a single Aruba Central site —
overall health score, device status broken out by type, client counts, and the
active alerts — by running a fixed 3-4 call gather and rendering the result
through the `generate_prefab_ui` Generative-UI tool. The whole point is to skip
the exploratory flailing: this runbook already knows the exact tools, the
response-envelope shape, and the dashboard layout, so the model fetches once and
renders once.

## Prerequisites

- Central is configured and reachable (`health(platform="central")` if unsure).
- The operator has named a site (e.g. "HQ", "BRANCH-1"). If they only said
  "a dashboard" with no site, ask which site first.
- Generative UI renders only in an MCP-Apps host (Claude Desktop / claude.ai /
  ChatGPT). In a non-apps client (e.g. Claude Code) `generate_prefab_ui` is a
  no-op visual — Step 3's text summary is then the deliverable, so ALWAYS emit
  it regardless.

## Response-shape contract (READ FIRST — this is what trips ad-hoc attempts)

Every `central_*` read returns the standard envelope; `<platform>_invoke_tool`
wraps results the same way. Read the inner `data`, and note the shapes are
**not uniform** across these three reads:

```text
central_get_site_name_id_mapping  -> data is a DICT: {site_name: {site_id, health, total_devices, total_clients, total_alerts}}
central_get_site_health           -> data is a LIST of site dicts          -> take data[0]
central_get_devices               -> data is a LIST of device dicts        -> OR the string "No devices found..." when empty
central_get_alerts                -> data is a DICT {items, total, next_cursor} -> rows are under data["items"] (NOT "result")
```

`central_get_alerts` **requires** `site_id` — resolve it first (Step 0).

Sandbox rules (code mode): sequential `await` only (no `asyncio.gather`); no
`datetime.now()` / `time.time()` / file I/O. Parse with plain builtins.

## Procedure

### Step 0 — Resolve the site name to a site_id

`central_get_site_health(site_name="<NAME>")` returns the `site_id` AND every
metric in one call, so it doubles as the resolver. Only fall back to
`central_get_site_name_id_mapping` when the operator's name is partial or
ambiguous and you need to pick the exact key.

**If the health `data` comes back `None` or an empty list:** the name didn't
match (a bogus site name returns `data: None`, not an error). Call
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
if not isinstance(health, list) or not health:
    return {"error": f"site {SITE_NAME!r} not found"}   # -> Step 0 fallback
site = health[0]
site_id = site["site_id"]
# `or {}` (not `.get(k, {})`): Central may return a section as null, not absent
# — `.get("metrics", {})` would hand back None and the next `.get` would crash.
metrics = site.get("metrics") or {}

devices_raw = _unwrap(await call_tool("central_invoke_tool",
    {"name": "central_get_devices", "params": {"site_id": str(site_id)}}))
devices = devices_raw if isinstance(devices_raw, list) else []   # "" / "No devices..." -> []

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

return {
    "site": {"name": site.get("name"), "site_id": site_id,
             "address": site.get("address"),
             "health": metrics.get("health") or {}},         # {Poor,Fair,Good,Summary}
    "device_summary": metrics.get("devices") or {},          # {Summary:{...}, Details:{by type}}
    "client_summary": (metrics.get("clients") or {}).get("Summary") or {},  # {Poor,Fair,Good,Total}
    "alert_summary": metrics.get("alerts") or {},            # {Critical, Total}
    "devices": device_rows,
    "alerts": alert_list,
}
```

### Step 2 — Render the dashboard (Generative UI)

Call `generate_prefab_ui` directly (top-level tool). Pass the Step 1 return as
the `data` argument — **each top-level key becomes a global** inside `code`
(`site`, `device_summary`, `client_summary`, `alert_summary`, `devices`,
`alerts`). There is NO `data` variable in the sandbox.

If you need to confirm component names, call `search_prefab_components` ONCE
with a broad query — don't fan out. The common set for this board:

- `metric` — KPI cards: Health score, Devices total, Clients total, Alerts (show Critical as the delta/secondary).
- `data_table` — the device list (name / type / model / status / ip) and the alert list (severity / name / device_type / created_at).
- `charts` — a small bar chart of `device_summary["Details"]` (Good/Fair/Poor per device type), or use `badge` rows if a chart is overkill.
- `badge` / `dot` — status pills (Good=green, Fair=amber, Poor/Down=red; Critical alerts=red).
- `column` / `row` / `grid` + `heading` — layout.

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
app = PrefabApp(view=view)
```

(Use the exact component signatures from `search_prefab_components`; the above
is the shape, not a guaranteed API.)

### Step 3 — Walkthrough beneath the board (ALWAYS emit)

Whether or not the widget renders, write a short text summary so the answer is
useful in every client: health score and trend, device count with any Poor/Down
devices named, client count, and the alert count leading with criticals (name
the critical alerts). In a non-apps client this text IS the dashboard.

## Unhappy paths (trace these)

- **Site not found** — health list empty → Step 0 fallback (list names, ask).
- **No devices** — `central_get_devices` returns "No devices found..." (a string,
  not a list) → `devices = []`; the table renders empty, the summary says so.
- **No alerts** — `data["items"]` is `[]` → "No active alerts" (a clean, good
  state, not an error).
- **Generative UI unavailable** — `generate_prefab_ui` no-ops in non-apps
  clients; Step 3's text summary covers it. Never let a non-rendering widget
  leave the operator with nothing.
- **Stacked switches** — `aos-s`/`cx` stacks share a `stack_id`; the device
  list may show stack members. That's fine for an overview; don't dedupe.

## When NOT to use this skill

- Multi-site / org-wide or cross-platform (Mist/ClearPass/UXI) boards — out of
  scope for v1; gather per-platform and compose manually, or use
  `infrastructure-health-check` for a cross-platform health snapshot.
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
