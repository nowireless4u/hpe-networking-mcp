---
name: central-ucc-quality
title: Aruba Central UCC call-quality check — correlate the live UCM tables, render a voice dashboard
description: |
  TRIGGERS — call this when the operator asks about UCC (Unified
  Communications & Collaboration) / real-time voice & video call
  quality on Aruba Central AOS-10 APs (or gateways): WiFi Calling
  (VoWiFi), Zoom, Microsoft Teams, RTP, WebRTC streams.

  Match phrases include:

  - "UCC call quality", "check call quality", "voice quality on
    <AP/site>", "how are my calls", "is my WiFi Calling OK",
    "Zoom / Teams call quality", "VoWiFi quality"
  - "UCC dashboard", "build me a call-quality dashboard", "show me
    active calls on <AP>", "what calls are live right now"
  - "why is my call choppy / laggy", "delay / jitter / packet loss
    on voice", "UCC score", "is voice degraded at <site>"
  - "show ucm cdrs", "show ucm hashtable", "datapath session ucc"
    (operators who already know the raw commands)

  AOS-10 APs run the UCM ALG and expose live UCC telemetry via
  `central_show_commands` (gateways too). This skill does the thing
  a single command can't: it **correlates three UCM tables** to tell
  a genuinely-live call from a stale Call Detail Record, joins each
  stream back to a client MAC, and gates quality on the UCC Score —
  then (optionally) renders it as an interactive Generative-UI
  dashboard.

  **Read-only.** Runs `show` commands only; mutates nothing.
platforms: [central]
tags: [central, ucc, voice, call-quality, wifi-calling, zoom, teams, dashboard, visualization, troubleshooting]
tools: [central_get_site_name_id_mapping, central_get_aps, central_get_devices, central_list_supported_show_commands, central_show_commands, generate_prefab_ui, search_prefab_components]
---

# Aruba Central UCC call-quality check

## Objective

Produce a trustworthy view of **real-time voice/video call quality** on
one AOS-10 AP, a list of APs, or a whole site — and (when the client can
render it) an interactive dashboard.

The hard part is **not** reading metrics. `show ucm cdrs` hands you
delay/jitter/loss/UCC-Score per stream directly. The hard part is that
the CDR is a *Call Detail Record log that persists after calls end*, with
**no timestamp and no active/ended flag** — so a torn-down call is
byte-for-byte indistinguishable from a live degraded one. A naive tool
that wraps `show ucm cdrs` alone reports **phantom "active calls" with
stale metrics**. This skill exists to get that right.

## What "getting it right" means (read first)

These rules are load-bearing — they come from live AOS-10 capture
(issue #400). Violate them and the output lies.

1. **Liveness is decided by `show datapath session ucc`, never by the
   CDR.** A CDR stream is **LIVE** only if its IP/port flow appears in
   `show datapath session ucc` with a populated **`Codec:`** field
   (e.g. `Codec:G711`). `Codec:--` or absent = not currently flowing.
   Everything in the CDR that is *not* backed by a live datapath session
   is a **STALE** record — show it separately or drop it, never as a
   live call.
2. **`Callinfo list:N > 0` in the hashtable does NOT prove a call is
   live.** Captured fact: a client sat at `Callinfo list:2` with frozen
   metrics across every poll while its datapath sessions were long gone.
   Use the hashtable for the **IP → MAC join only**, not for liveness.
3. **The join key is the IP/port 4-tuple** — `src_ip + src_port +
   dst_ip + dst_port`. It's the field set shared by all three tables.
   **Why 4-tuple and not a strict 5-tuple:** `show ucm cdrs` does **not**
   emit a protocol column, so protocol can't be part of the CDR↔datapath
   match — the join is on IPs + ports only. For UCC media this is
   effectively unique: the streams are UDP (RTP/SRTP, IKE/4500), and two
   *simultaneous* flows sharing the exact same `src_ip:src_port →
   dst_ip:dst_port` on different protocols (one stale in the CDR, one live
   in datapath) is not a real-world condition. `show datapath session
   ucc` *does* carry protocol (column 3, `17` = UDP) — if you want to
   harden the match, restrict the live set to `proto == "17"` before
   correlating; the residual collision risk without it is negligible but
   non-zero, so don't claim a strict 5-tuple match. The CDR's `src_ip`
   is the **client IP**; the hashtable maps client IP → client MAC.
   That's how a CDR row becomes "Hayley's Pixel".
4. **Gate quality on the UCC Score (0–100 composite), not on the Delay
   field.** The `Delay` value routinely reads thousands of ms (≈9000 ms
   observed) — it is **not** one-way latency, so applying the ITU-T
   G.114 150 ms threshold to it flags essentially every record. Bands:
   **GOOD ≥ 80 · FAIR 70–79 · POOR < 70.** Surface delay/jitter/loss as
   *context* (and optionally a secondary flag for loss > 1% / high
   jitter), but the verdict rides on the score.
5. **One atomic snapshot per device.** Run all three commands in a
   single comma-separated `central_show_commands` call so the three
   tables describe the same instant. Polling them separately invites
   skew.
6. **Read-only.** This skill never writes. (If a call is bad, the
   *operator* decides remediation; you report.)

## Scope / applicability

- **AOS-10 APs** are the primary target (`device_type="aps"`). Gateways
  also run UCM (`device_type="gateways"`) — the same three commands work;
  swap the device type if the operator asks about a gateway.
- UCM telemetry only exists where the **UCC ALG / DPI** has classified
  voice/video flows. An AP with no voice clients returns empty tables —
  that's "no active calls", not an error.
- AOS-8 / Mobility-Conductor controllers are **out of scope** here (use
  the `aos8_*` tools / their own UCM CLI). This skill is Central-managed
  AOS-10 only.

## The three commands

| Command | What it gives you | Role in the correlation |
|---|---|---|
| `show ucm hashtable` | per-client `vc:` entries — `mac:`, `IP:`, the ALGs tracked, and `Callinfo list:N` | **IP → MAC join.** Identity only — NOT liveness (rule 2). |
| `show datapath session ucc` | active UCC datapath sessions — full 5-tuple (incl. protocol col), `Prio:`, `ToS:`, `Flags:`, **`Codec:`** | **Liveness source of truth.** A populated `Codec:` = the flow is live right now. |
| `show ucm cdrs` | per-stream call records — `[A]`/`[V]` marker, IP/port 4-tuple (no protocol col), app, `(delay)/(jitter)/(loss)/(UCC-Score)` | **The metrics.** Filter to only the streams that datapath says are live. |

## Procedure

### Step 0 — Resolve the target device(s)

The operator names an AP (by name/serial), a site, or a gateway.

```python
# Resolve a site name to its APs (most common entry point).
# For a single named AP or a known serial, skip straight to the serial.
sites = await call_tool("central_invoke_tool",
    {"name": "central_get_site_name_id_mapping", "params": {}})
sites = sites.get("data", sites)            # unwrap the response envelope
# pick the operator's site key (exact, case-insensitive), then:
aps = await call_tool("central_invoke_tool",
    {"name": "central_get_aps", "params": {"site_name": "HQ", "status": "Up"}})
aps = aps.get("data", aps)
ap_rows = aps.get("result", aps) if isinstance(aps, dict) else aps
# each row carries the AP name + serial; collect (name, serial) pairs.
targets = [{"name": a.get("deviceName") or a.get("name"),
            "serial": a.get("serial") or a.get("serialNumber")} for a in ap_rows]
```

Keep `targets` small for a site sweep (UCC matters per-AP; a 50-AP site
is 50 sequential `show` calls — confirm scope with the operator before a
large sweep, and `log`-equivalent note it).

### Step 1 — One atomic snapshot per device

Run the three commands comma-separated so they describe the same instant.
`device_type` is `"aps"` (or `"gateways"`).

```python
RAW = {}
for t in targets:
    resp = await call_tool("central_invoke_tool", {"name": "central_show_commands", "params": {
        "serial_number": t["serial"],
        "device_type": "aps",
        "commands": "show ucm hashtable,show datapath session ucc,show ucm cdrs",
    }})
    RAW[t["serial"]] = resp.get("data", resp)
```

The result carries the three command outputs (commonly a list of
`{command, output}` blocks, or a dict keyed by command — **inspect the
shape once** and pull each block's raw text). If unsure which `show`
commands a device supports, `central_list_supported_show_commands` lists
them first.

### Step 2 — Parse each block (string ops only — sandbox-safe)

The sandbox has no `re`/`collections`; parse with `.split()` and plain
dicts. Field order is positional, so parse the metric-bearing rows
**from the right** to stay robust against the leading `[A]`/`[V]` marker.

```python
def parse_hashtable(text):
    # Build {client_ip: {"mac": ..., "callinfo": N}}.  Identity join only.
    ip_to = {}
    cur_ip = None
    for line in text.splitlines():
        if "mac:" in line and "IP:" in line:
            mac = line.split("mac:", 1)[1].split(",")[0].split(")")[0].strip()
            ip = line.split("IP:", 1)[1].split(")")[0].split(",")[0].strip()
            cur_ip = ip
            ip_to[ip] = {"mac": mac, "callinfo": 0}
        elif "Callinfo list:" in line and cur_ip:
            try:
                n = int(line.split("Callinfo list:", 1)[1].split()[0])
            except (ValueError, IndexError):
                n = 0
            if n > ip_to[cur_ip]["callinfo"]:
                ip_to[cur_ip]["callinfo"] = n
    return ip_to

def parse_datapath(text):
    # Build a set of LIVE IP/port 4-tuples (both orientations) + codec per
    # tuple. datapath carries protocol (col 3); the CDR does not, so the
    # correlation key is the 4-tuple (see rule 3). UCC media is UDP — to
    # harden, add `and proto == "17"` to the guard below.
    live = set()
    codec_of = {}
    for line in text.splitlines():
        if "Codec:" not in line:
            continue
        toks = line.split()
        codec = ""
        for tk in toks:
            if tk.startswith("Codec:"):
                codec = tk.split(":", 1)[1]
        if not codec or codec == "--":
            continue
        # leading columns: src_ip dst_ip proto src_port dst_port ...
        if len(toks) < 5:
            continue
        s_ip, d_ip, proto, s_port, d_port = toks[0], toks[1], toks[2], toks[3], toks[4]
        fwd = (s_ip, s_port, d_ip, d_port)
        rev = (d_ip, d_port, s_ip, s_port)
        live.add(fwd); live.add(rev)
        codec_of[fwd] = codec; codec_of[rev] = codec
    return live, codec_of

def parse_cdrs(text):
    # Each metric row ends in (delay)/(jitter)/(loss)/(score). Parse from the right.
    rows = []
    for line in text.splitlines():
        toks = line.split()
        if len(toks) < 7:
            continue
        blob = toks[-1]
        if not (blob.startswith("(") and blob.endswith(")") and "/" in blob):
            continue
        nums = blob.replace("(", "").replace(")", "").split("/")
        if len(nums) != 4:
            continue
        try:
            delay, jitter, loss, score = [float(x) for x in nums]
        except ValueError:
            continue
        app = toks[-2]
        d_port, d_ip, s_port, s_ip = toks[-3], toks[-4], toks[-5], toks[-6]
        rows.append({
            "src_ip": s_ip, "src_port": s_port, "dst_ip": d_ip, "dst_port": d_port,
            "app": app, "delay_ms": round(delay, 1), "jitter_ms": round(jitter, 1),
            "loss_pct": round(loss, 2), "ucc_score": round(score, 1),
        })
    return rows
```

> If the live output's columns don't match this recipe exactly, **print a
> few raw lines first and adjust** — show-command formats can drift across
> AP firmware. The recipe above matches AOS-10 capture as of issue #400;
> treat it as a guide, not a contract.

### Step 3 — Correlate: live vs stale, and join to the MAC

First, a sandbox-safe extractor that pulls the three raw command outputs
out of the `central_show_commands` response across the shapes it comes
back in (list of `{command, output}` blocks, dict keyed by command, or a
single concatenated string). It's keyed on a keyword in each command
label; if the response can't be split per-command it returns the whole
blob — harmless, because every parser above is **line-filtered** (mac/IP
lines, `Codec:` lines, metric rows), so a concatenated output still
parses correctly.

```python
def pick_blocks(resp):
    # Normalize the response to a list of (command_label, output_text) pairs.
    body = resp
    if isinstance(body, dict):
        inner = body.get("result") or body.get("output") or body.get("commands")
        if isinstance(inner, (list, dict)):
            body = inner
    pairs = []
    if isinstance(body, dict):
        for k, v in body.items():
            pairs.append((str(k), v if isinstance(v, str) else str(v)))
    elif isinstance(body, list):
        for item in body:
            if isinstance(item, dict):
                cmd = item.get("command") or item.get("cmd") or item.get("name") or ""
                out = item.get("output") or item.get("result") or item.get("data") or ""
                pairs.append((str(cmd), out if isinstance(out, str) else str(out)))
            elif isinstance(item, str):
                pairs.append(("", item))
    elif isinstance(body, str):
        pairs.append(("", body))

    def find(keyword):
        for cmd, out in pairs:
            if keyword in cmd.lower():
                return out
        return "\n".join([o for _, o in pairs])   # un-split: parsers self-filter
    return find("hashtable"), find("datapath"), find("cdr")

def band(score):
    if score >= 80: return "GOOD"
    if score >= 70: return "FAIR"
    return "POOR"

calls, stale = [], []
for serial, resp in RAW.items():
    ht_text, dp_text, cdr_text = pick_blocks(resp)
    ip_to = parse_hashtable(ht_text)
    live, codec_of = parse_datapath(dp_text)
    for r in parse_cdrs(cdr_text):
        # 4-tuple key — the CDR exposes no protocol column (see rule 3).
        tup = (r["src_ip"], r["src_port"], r["dst_ip"], r["dst_port"])
        ident = ip_to.get(r["src_ip"], {})
        row = dict(r)
        row["mac"] = ident.get("mac", "unknown")
        row["ap_serial"] = serial
        if tup in live:                       # rule 1 — datapath = liveness
            row["band"] = band(r["ucc_score"])
            row["codec"] = codec_of.get(tup, "")
            # secondary context flags (do NOT change the band)
            row["loss_flag"] = r["loss_pct"] > 1.0
            row["jitter_flag"] = r["jitter_ms"] > 30.0
            calls.append(row)
        else:
            row["band"] = "STALE"
            stale.append(row)                 # persisted record, not flowing now
```

Sort live calls **worst-first** (`calls.sort(key=lambda c: c["ucc_score"])`)
so the degraded ones lead. Build the dashboard payload:

```python
def count_by(seq, key):
    out = {}
    for x in seq:
        k = x[key]
        out[k] = out.get(k, 0) + 1
    return out

poor = [c for c in calls if c["band"] == "POOR"]
fair = [c for c in calls if c["band"] == "FAIR"]
payload = {
    "scope_label": scope_label,                       # e.g. "AP HOME-GARAGE-AP" or "Site HOME — 4 APs"
    "summary": {
        "live_calls": len(calls),
        "degraded_calls": len(poor) + len(fair),
        "poor_calls": len(poor),
        "apps_count": len(count_by(calls, "app")),
        "worst_score": min([c["ucc_score"] for c in calls], default=None),
        "stale_records": len(stale),
    },
    "calls": calls,
    "stale": stale,
    "by_app": [{"app": k, "count": v} for k, v in count_by(calls, "app").items()],
    "by_band": {b: len([c for c in calls if c["band"] == b]) for b in ("GOOD", "FAIR", "POOR")},
}
return payload
```

`return payload` from the `execute()` block so it lands in your context;
you then hand it to the dashboard step.

### Step 4 — Render the dashboard (Generative UI)

The UCC check is **already complete** after Step 3 — Step 4 is only
*presentation*. Whether `generate_prefab_ui` exists changes how you show
the result, never whether the check succeeded. A "tool not found" /
disabled-app condition is **not** a UCC failure: fall through to the
Markdown rendering and report the same data.

If `generate_prefab_ui` is available (it's exposed when the server runs
with `MCP_APP_ENABLE=true`), build an interactive Prefab dashboard.

**DATA CONTRACT — read this or you'll hit `NameError`.** The values you
pass in `data={...}` are injected into the Prefab sandbox as **globals
keyed by name** — there is **no `data` variable**. Pass
`data={"summary": summary, "calls": calls, "by_app": by_app, ...}` and
then reference `summary`, `calls`, `by_app` as **bare globals** in the
Prefab code. Referencing `data` raises `NameError: name 'data'`.

1. First call **`search_prefab_components`** (top-level tool) to confirm
   exact component names/args — e.g. `search_prefab_components(query="Card Metric Badge DataTable Tabs BarChart")`.
2. Then call **`generate_prefab_ui`** (top-level tool — not via
   `call_tool`) with the Prefab code + `data`. Suggested layout:
   - **Header** — title from `scope_label`, plus a status `Badge` whose
     color is the worst band present (red if any POOR, amber if any FAIR,
     green otherwise).
   - **KPI row** — `Metric` cards: Live Calls (`summary["live_calls"]`),
     Degraded (`summary["degraded_calls"]`), Apps in use
     (`summary["apps_count"]`), Worst UCC Score (`summary["worst_score"]`).
   - **Live calls `DataTable`** sorted worst-first — columns: Client (MAC),
     IP, App, **UCC Score** (color the cell/badge by band: red < 70, amber
     70–79, green ≥ 80), Delay ms, Jitter ms, Loss %, Codec, AP. Built-in
     search/sort makes it interactive without custom reactivity.
   - **Charts** — calls `by_app` (bar) and `by_band` (donut/bar).
   - **Stale records** — a separate, visually de-emphasized table or a
     one-line note (`summary["stale_records"]` CDR rows excluded as
     not-currently-flowing). Never mix these into the live table.
   - **Footnote** — "Liveness from `show datapath session ucc`; metrics
     from `show ucm cdrs`; quality gated on UCC Score (≥80 good / 70–79
     fair / <70 poor). Delay is not one-way latency."

**Fallback (no Generative UI).** If `generate_prefab_ui` isn't available
(tool not found / `MCP_APP_ENABLE` unset / a non-app client like the code
sandbox CLI), render a **Markdown** summary instead: a KPI line, a live-calls
table sorted worst-first with the UCC Score column emoji-coded
(🔴 < 70 · 🟡 70–79 · 🟢 ≥ 80), and a short stale-records note. Same data,
text-mode presentation. Do not error out just because the dashboard tool
is absent.

### Step 5 — Walkthrough beneath the output

Add a short (3–6 sentence) plain-English read regardless of render mode:

- Lead with the worst live call (client, app, score) and what's dragging
  it (jitter? loss? — cite the context fields, not the Delay number).
- State how many live calls vs how many stale CDR records were filtered
  out, so the operator trusts the count.
- If everything is GOOD, say so plainly ("3 live calls, all ≥ 85 — voice
  is healthy on this AP").
- Offer the next step: drill into another AP, or watch a specific client.

## Worked example

Operator: *"Check call quality on the garage AP."*

1. Step 0 → resolve `HOME-GARAGE-AP` → serial.
2. Step 1 → one `central_show_commands` with the three commands.
3. Steps 2–3 → parse + correlate. Say the CDR has 5 streams but datapath
   shows only 2 live (codec populated); the other 3 are stale records →
   `calls` has 2, `stale` has 3.
4. Step 4 → dashboard (or Markdown): 2 live WiFi-Calling streams, one at
   UCC 67 (POOR, 1.1% loss), one at 86 (GOOD). Worst-first.
5. Step 5 → *"2 live calls on HOME-GARAGE-AP. One WiFi-Calling stream to
   141.207.x is degraded — UCC 67 with 1.1% packet loss (the IPsec tunnel
   is struggling); the other is healthy at 86. 3 older CDR records were
   stale (no live datapath session) and excluded. Want me to watch this
   client or check another AP?"*

## When NOT to use this skill

- **"Is the AP up / how many clients"** — that's `central_get_aps` /
  `central_get_site_health`, not UCC.
- **Historical call trends / SLA reporting** — UCM tables are a *live*
  snapshot; they don't carry history. Use Central's monitoring/analytics
  for trends.
- **AOS-8 controller voice** — out of scope; use the `aos8_*` tools.
- **Building a non-voice dashboard** (devices/clients/bandwidth/alerts) —
  gather the relevant Central/ClearPass data and call `generate_prefab_ui`
  directly; this skill is specifically the UCC correlation.

## Notes

- **No new tools.** This is a correlation + presentation runbook over
  existing read tools — deliberately, because the value is the *join*
  (three tables, stale-vs-live discrimination, score gating), which a
  single hardcoded tool can't capture cleanly (issue #400).
- **Sandbox limits** apply to every snippet here: no `re`, no
  `collections`, no `datetime.now()` / `time.time()`, no `asyncio.gather`.
  Parse with `.split()` + plain dicts; loop sequentially.
