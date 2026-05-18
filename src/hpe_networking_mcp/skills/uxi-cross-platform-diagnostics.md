---
name: uxi-cross-platform-diagnostics
title: UXI cross-platform diagnostic correlation — GO / DEGRADED / CRITICAL
description: |
  PRIMARY TRIGGER — invoke this skill whenever the operator mentions UXI
  sensor failures, failing UXI synthetic tests, sensor offline conditions,
  or asks to correlate UXI test failures to a network root cause in
  Aruba Central, Juniper Mist, or AOS 8 / Mobility Conductor. Do NOT
  improvise: this skill encodes the reachability gate, per-anchor
  correlation rules (networkName / groupPath / macAddress), and the
  GO / DEGRADED / CRITICAL verdict that free-form analysis cannot
  reproduce.

  This skill is platform-aware: it probes which infrastructure platforms
  are reachable before running correlation queries and emits an INFO
  finding (not a failure) for each unreachable platform. A platform that
  the operator does not have deployed never causes a false-positive
  CRITICAL.

  Paste mode is supported: if the UXI platform itself is unreachable
  from this MCP server, the skill prompts the operator for a structured
  paste bundle (one block per failing sensor) and still correlates
  against any reachable infrastructure platform. UXI being offline does
  NOT imply the infrastructure platforms are offline.

  IMPORTANT — UXI sensors are SYNTHETIC clients. The `macAddress`
  associated with a sensor or an issue is the SENSOR'S OWN MAC
  ADDRESS, not the MAC of an end-user device. Use it to identify
  which AP the sensor is currently attached to — never to attribute
  impact to a real user.

  Trigger phrases include but are not limited to: "uxi sensors failing",
  "why are my synthetic tests failing", "correlate uxi failures to
  central", "uxi cross-platform diagnostic", "what's wrong with my uxi
  sensors", "are my sensors healthy", "uxi sensor offline", "uxi service
  test failing", "uxi sensor radius failure", "uxi sensor dhcp failure",
  "uxi sensor dns failure", "uxi sensor association failure",
  "correlate uxi to mist", "correlate uxi to aos8", "diagnose uxi".
platforms: [uxi, central, mist, aos8]
tags: [uxi, diagnostics, correlation, health, sensors]
tools:
  - health
  - uxi_list_sensors
  - uxi_get_sensor_status
  - uxi_list_agents
  - uxi_list_service_tests
  - uxi_list_groups
  - uxi_list_wireless_networks
  - uxi_list_wired_networks
  - central_get_sites
  - central_get_wlans
  - central_get_clients
  - central_get_aps
  - central_get_site_health
  - central_get_alerts
  - mist_get_site_info
  - mist_list_org_wlans
  - mist_search_org_wireless_clients
  - mist_list_site_devices
  - mist_search_site_alarms
  - aos8_find_client
  - aos8_get_client_detail
  - aos8_get_active_aps
  - aos8_show_command
  - aos8_get_alarms
---

# UXI cross-platform diagnostic correlation

## Objective

Correlate Aruba UXI synthetic test failures and sensor state to the
network infrastructure root cause in Aruba Central, Juniper Mist, and
AOS 8 / Mobility Conductor — and emit a single **GO / DEGRADED /
CRITICAL** verdict with structured **REGRESSION / DRIFT / INFO**
findings linking each UXI symptom to its correlated platform finding.
Operators get one paste-ready report instead of having to cross-
reference four tool surfaces by hand.

## Scope boundaries (what this skill IS and is NOT)

The skill IS:

- A **correlation engine** between UXI sensor / service-test state and
  the infrastructure platforms (Central, Mist, AOS 8). It joins UXI
  data to platform data via three anchors:
  - `networkName` → SSID lookup
  - `groupPath` top-level segment → site
  - sensor `macAddress` → AP attachment (sensor's OWN MAC; see below)
- A **platform-aware** runbook that only queries platforms whose
  `health()` status is `ok`. Unreachable platforms emit a single
  **INFO** finding — never a REGRESSION or DRIFT.
- A **GO / DEGRADED / CRITICAL** verdict generator with explicit
  severity rules (sensor offline → CRITICAL; auth / association / DNS /
  DHCP failure → CRITICAL; HTTP / application failure → DEGRADED; no
  networkName match → DRIFT / DEGRADED).
- A **paste-fallback** path when UXI is unreachable from this MCP
  server. The operator pastes one structured block per failing sensor
  and the skill still runs Central / Mist / AOS 8 correlation.

The skill is NOT:

- An **end-user impact estimator.** UXI sensors are synthetic clients.
  A UXI failure tells you a synthetic probe failed at a specific
  location at a specific time — it does NOT measure how many real
  end-user devices are affected.
- A **user-MAC lookup tool.** The `macAddress` in UXI sensor records
  and UXI issue context is the SENSOR'S OWN MAC ADDRESS — it is the
  hardware MAC of the UXI sensor itself, not the MAC of any end-user
  device. Use it to look up which AP the SENSOR is currently
  associated to. Never write findings that imply a real end user is
  experiencing the problem because their MAC was seen.
- A **write tool.** No `*_manage_*`, no `*_disconnect_*`, no
  `aos8_send_reset_*`. Read-only correlation.
- A **platform health probe.** Use `infrastructure-health-check` for
  a daily reachability snapshot. This skill assumes the operator has
  a specific UXI symptom and wants the root cause.
- A **substitute** for paging on critical infrastructure outages.
  Treat CRITICAL findings as a starting point for triage; do not
  defer real incident response to a chat skill.

## Prerequisites

- UXI must be configured on this MCP server (UXI client credentials
  resolvable). If not, see Stage -1: the skill stops with an
  actionable message.
- At least one of `central`, `mist`, or `aos8` must be reachable for
  correlation to be useful. With zero reachable infrastructure
  platforms the skill still runs Stage 1 (UXI inventory) and emits
  the verdict from UXI-only signals (sensor online/offline and issue
  severity), with INFO findings for each unreachable platform.
- The operator has invoked the skill because of a UXI-flavored
  symptom (failing sensors, failing synthetic tests). The skill does
  not run as a daily standup snapshot.

## Procedure — five stages

The skill runs sequentially through stages -1, 0, 1 (or 1' in paste
mode), 2, 3, and 4. Each stage gates the next; do not skip ahead.

---

### Stage -1 — UXI reachability gate (SKILL-01)

Call `health()` once and inspect the `uxi` entry of the result.

**If `uxi.status == "ok"`** — proceed to Stage 0 in **live mode**. No
announcement, no operator interview. Cache the `health()` result and
reuse it in Stage 0 (do NOT call `health()` again).

**If `uxi.status == "degraded"` or `uxi.status == "unavailable"`** —
switch to **paste mode**. Announce to the operator verbatim:

> UXI is not reachable from this MCP server — switching to paste
> mode. The skill will prompt you for a structured sensor bundle,
> then still correlate against any reachable infrastructure platforms
> (Central / Mist / AOS 8).

Proceed to Stage 0 with `mode = "paste-fallback"`. Stage 1 will be
replaced by Stage 1' (paste fallback).

**If `uxi` is not in the `health()` result (platform not configured)**
— stop. Emit:

> UXI not configured on this MCP server. This skill correlates UXI
> synthetic-test failures to network infrastructure root causes — it
> requires UXI client credentials. Configure the UXI Docker secrets
> and restart the server, or run the `infrastructure-health-check`
> skill for a Central / Mist / AOS 8 health snapshot.

No further stages run.

---

### Stage 0 — Reachable-platform discovery (D-01)

Re-inspect the cached `health()` result from Stage -1. Build the
`correlation_platforms` set: each member of `{central, mist, aos8}`
whose `status == "ok"`. Record the result for the report metadata
block.

For each member of `{central, mist, aos8}` that is `degraded`,
`unavailable`, or not configured, emit exactly **one** INFO finding:

> `<platform> unreachable — no correlation attempted; verify
> connectivity.` (source: `health()`)

Do NOT call any tool against a platform that is not in
`correlation_platforms`. Every Stage 2 sub-step is gated by a
`**Skip if:** <platform> is not in correlation_platforms` clause —
this is non-negotiable (D-01). Calling `central_*` / `mist_*` /
`aos8_*` tools against an unreachable platform causes 429s and
clutter, and was the most common Phase 16 pitfall.

If `correlation_platforms` is empty, continue: the skill still runs
Stage 1 to inventory UXI state and emits a UXI-only verdict.

---

### Stage 1 — UXI data collection (SKILL-02, live mode only)

Skip this stage entirely and go to **Stage 1'** if `mode ==
"paste-fallback"`.

Collect UXI tenant state with the following sequence. Pass every
response through extraction guidance below — do NOT dump raw JSON
into the report.

1. **List sensors.** Tool: `uxi_list_sensors`.
   Extract per item: `id`, `name`, `serial`, `model`, `macAddress`,
   `wirelessMacAddress` (the sensor's wireless interface MAC — this
   is the value most likely to appear in client-search results on
   Central / Mist / AOS 8 because the sensor associates to APs over
   Wi-Fi). Page via `next_cursor` until `next is null`.

2. **Get sensor status, per sensor.** Tool: `uxi_get_sensor_status`
   (called once per `sensor.id` from step 1). Returns:

   ```
   {
     isOnline: <bool>,
     isTesting: <bool>,
     issues: [
       {
         code: <string>,         # e.g. "sensor.offline",
                                 # "service_test.radius_auth.failed",
                                 # "service_test.dns.failed",
                                 # "service_test.dhcp.failed",
                                 # "service_test.association.failed",
                                 # "service_test.http.failed"
         severity: <"critical" | "major" | "minor">,
         status: <"open" | "resolved">,
         timestamp: <ISO timestamp>,
         id: <issue id>,
         context: { ... },       # may contain serviceTestName,
                                 # networkName, groupPath references
         incidentId: <string | null>,
       },
       ...
     ]
   }
   ```

   Extract per sensor:
   - `isOnline` — if `false`, the sensor is dead-monitoring (D-09,
     CRITICAL severity).
   - `isTesting` — if `false` while `isOnline=true`, sensor is
     online but not running its scheduled tests; emit DRIFT.
   - For each open issue:
     - `code` drives the service-test failure classification (Stage 3
       severity table). Map prefixes: `sensor.offline` →
       sensor-offline; `service_test.radius_auth.*` →
       RADIUS / 802.1x; `service_test.association.*` → association;
       `service_test.dns.*` → DNS; `service_test.dhcp.*` → DHCP;
       `service_test.http.*` → HTTP / application.
     - `severity` is UXI's own severity label (informational; the
       skill's severity classification comes from `code`, not from
       this field, per D-10).
     - `context` is a free-form dict — look for `serviceTestName`,
       `networkName`, `groupPath` keys when present. **If these keys
       are NOT directly on the issue, resolve them via the related
       UXI list tools** (steps 3-7 below) by joining on the sensor's
       group / network bindings.

3. **List service tests.** Tool: `uxi_list_service_tests`.
   Extract per item: `id`, `name`, `category` (e.g. dns / dhcp /
   radius / association / http), `targetNetworkId`. Provides the
   human-readable `serviceTestName` for any issue whose `context`
   references a service-test ID instead of a name.

4. **List agents.** Tool: `uxi_list_agents`. Extract per item:
   `id`, `name`, `isOnline`. Agents are the UXI orchestration plane;
   include an agent's offline state in the verdict (CRITICAL — an
   offline agent makes its sensors silently stop reporting).

5. **List groups.** Tool: `uxi_list_groups`. Extract per item: `id`,
   `name`, `path` (the `groupPath` string used for Stage 2 anchor 2).

6. **List wireless networks.** Tool: `uxi_list_wireless_networks`.
   Extract per item: `id`, `name` (this IS the `networkName` value
   used for Stage 2 anchor 1), `ssid`, `security`. The `name` here
   is the UXI-side label that joins to a platform SSID.

7. **List wired networks.** Tool: `uxi_list_wired_networks`. Extract
   per item: `id`, `name`. Wired-network sensors emit `networkName`
   from this list (or `"-"` if not bound to a named network).

Build a normalized **UXI issue record** for every open issue across
all sensors:

```
issue_record = {
    sensor_id:        <from uxi_list_sensors>,
    sensor_name:      <from uxi_list_sensors>,
    sensor_mac:       <sensor's wirelessMacAddress, sensor's OWN MAC>,
    is_online:        <isOnline>,
    is_testing:       <isTesting>,
    code:             <issue.code>,
    uxi_severity:     <issue.severity>,
    service_test:     <resolved serviceTestName, or "-" if N/A>,
    network_name:     <resolved networkName, or "-" if N/A>,
    group_path:       <resolved groupPath, or "-" if N/A>,
    timestamp:        <issue.timestamp>,
}
```

Proceed to Stage 2.

---

### Stage 1' — Paste fallback (when UXI unreachable, D-11)

Only runs when `mode == "paste-fallback"`. Prompt the operator with
the EXACT block below and wait for the paste. Do NOT improvise field
order or field names — downstream parsing depends on the order.

> Paste each failing sensor's state in this format (one block per
> sensor, separated by a blank line):
>
> ```
> Sensor:        <sensor name or serial>
> isOnline:      <true | false>
> isTesting:     <true | false>
> groupPath:     <e.g. "HQ > Floor 2 > North Wing">
> networkName:   <SSID or wired network name, or "-" if none>
> Failing tests: <comma-separated: dns, dhcp, radius_auth, association, http_app>
> wirelessMacAddress: <sensor's OWN wireless MAC, format aa:bb:cc:dd:ee:ff>
> Severity:      <critical | major | minor>
> ```

Parse each block into one UXI issue record (same shape as Stage 1).
A pasted `isOnline: false` synthesizes a `sensor.offline` code; each
entry in `Failing tests` synthesizes one `service_test.<name>.failed`
code. Severity from the paste populates `uxi_severity`. Continue to
Stage 2 **exactly** as in live mode (D-12) — paste mode only affects
how UXI data is collected, not how the correlation runs. Live
correlation against any reachable Central / Mist / AOS 8 is still
performed.

---

### Stage 2 — Correlation against reachable platforms only (SKILL-03)

For each UXI issue record from Stage 1 or Stage 1', run **four
anchors**. Every anchor sub-step carries an explicit `**Skip if:**`
clause for per-platform narrowing (D-01). Unreachable platforms
contribute zero correlation rows and emit no DRIFT / REGRESSION.

#### Anchor 1 — networkName → SSID (D-03 + D-13)

If `network_name` is `-` or empty, skip this anchor for the record.

Normalize both sides with `lowercase()` before comparing.
**Case-insensitive EXACT match.** No substring matching, no fuzzy
matching, no `startswith`. `Corp-WiFi` does NOT match
`Corp-WiFi-Legacy`. (Pitfall 5 — false-positive correlation.)

- **Central.** Tool: `central_get_wlans` → enumerate the returned
  WLANs and select rows where the SSID field (commonly `essid` or
  `ssid` depending on response shape) `.lower()` equals
  `network_name.lower()`.
  **Skip if:** `central` is not in `correlation_platforms`.

- **Mist.** Tool: `mist_list_org_wlans(org_id=<from health()
  result>)` → select WLANs whose `ssid.lower()` equals
  `network_name.lower()`.
  **Skip if:** `mist` is not in `correlation_platforms`.

- **AOS 8.** Tool: `aos8_show_command(command="show wlan
  ssid-profile")` → parse the returned profile list, select rows
  whose SSID profile name `.lower()` equals `network_name.lower()`.
  **Skip if:** `aos8` is not in `correlation_platforms`.

**No match in any reachable platform** → emit DRIFT finding per
D-14:

> `networkName '<network_name>' not matched to any SSID in
> [<list of platforms checked>]. The wireless network may have been
> removed or renamed.` (source: `central_get_wlans()`,
> `mist_list_org_wlans()`, `aos8_show_command()`)

**Match found** → record auth-type / VLAN / security per matched
platform for use in the report.

#### Anchor 2 — groupPath top segment → site (D-04)

If `group_path` is `-` or empty, skip this anchor.

Take the top-level segment: split `group_path` on `>`, strip the
first element, lowercase it. e.g. `"HQ > Floor 2 > North Wing"` →
`"hq"`. **Case-insensitive exact match.** No substring, no fuzzy.

- **Central.** Tool: `central_get_sites` → select sites whose
  `site_name.lower()` equals the top segment.
  **Skip if:** `central` is not in `correlation_platforms`.

- **Mist.** Tool: `mist_get_site_info(site_id=<id>)` for each known
  Mist site; or, if no per-site iteration is practical, use the org
  site list returned by `health()` enrichment. Match `name.lower()`
  to the top segment.
  **Skip if:** `mist` is not in `correlation_platforms`.

- **AOS 8.** Use the top segment as a `config_path` candidate. Tool:
  `aos8_get_active_aps(config_path="/md/<top-segment>")` — if it
  returns a non-empty AP list, treat the top segment as a valid AOS 8
  scope. (AOS 8 has no flat "site" concept; the `config_path`
  hierarchy is the equivalent.)
  **Skip if:** `aos8` is not in `correlation_platforms`.

**No match** → INFO finding (not DRIFT — groupPath schemas often
don't align cleanly with platform site names):

> `groupPath top segment '<segment>' not matched to a site in
> [<platforms checked>]. Site-level infra checks will be skipped
> for this issue.` (source: `central_get_sites()`,
> `mist_get_site_info()`, `aos8_get_active_aps()`)

#### Anchor 3 — sensor macAddress → AP attachment (D-02)

**Reminder:** `sensor_mac` is the sensor's OWN MAC address — the
hardware MAC of the UXI sensor itself. Use it to find which AP
the SENSOR is currently associated to, NOT to identify an affected
end user (Pitfall 3). Findings derived from this anchor MUST say
"sensor's OWN MAC" or "the UXI sensor's MAC" — never "the affected
client's MAC" or "the user's device".

- **Central.** Tool: `central_get_clients` (filter the result
  client-side by `mac == sensor_mac`). Record the matched client's
  `ap_name` / `ap_serial` as the sensor's current AP attachment.
  **Skip if:** `central` is not in `correlation_platforms`.

- **Mist.** Tool: `mist_search_org_wireless_clients(org_id=<from
  health>, mac=<sensor_mac>)`. Record the returned client's
  `ap_mac` / `ap_id`.
  **Skip if:** `mist` is not in `correlation_platforms`.

- **AOS 8.** Tool: `aos8_find_client(macaddr=<sensor_mac>)` — if a
  match is returned, follow up with `aos8_get_client_detail` for AP
  attachment.
  **Skip if:** `aos8` is not in `correlation_platforms`.

No match in any reachable platform is acceptable (the sensor may
not be associated at the moment, especially when `isOnline=false`).
Emit INFO only:

> `Sensor '<sensor_name>' (sensor's OWN MAC <sensor_mac>) not found
> in client lookup on [<platforms checked>] — sensor may be
> disassociated.` (source: `central_get_clients()`,
> `mist_search_org_wireless_clients()`, `aos8_find_client()`)

#### Anchor 4 — service-test failure → site infra check (D-05)

Run this anchor only when (a) the issue record has a service-test
failure code (i.e. `code` is NOT `sensor.offline`) AND (b) Anchor 2
matched a site on at least one platform.

For each matched site, query the platform's infra surface
**best-effort** — degrade gracefully if any sub-call returns no data
or fails. This is informational enrichment, NOT a verdict-blocking
gate.

- **Central matched site.** Tools (in order):
  - `central_get_aps(site_id=<matched site id>)` — AP count + status
    at the site.
  - `central_get_site_health(site_name=<matched site name>)` —
    aggregated site health snapshot.
  - `central_get_alerts(severity="Major,Critical")` — filter the
    response to alerts whose site / device falls within the matched
    site.
  **Skip if:** `central` is not in `correlation_platforms` OR Anchor
  2 did not match a Central site.

- **Mist matched site.** Tools:
  - `mist_list_site_devices(site_id=<matched site id>)` — AP / device
    list at the matched Mist site.
  - `mist_search_site_alarms(site_id=<matched site id>)` — recent
    alarms at the site.
  **Skip if:** `mist` is not in `correlation_platforms` OR Anchor 2
  did not match a Mist site.

- **AOS 8 matched scope.** Tools:
  - `aos8_get_active_aps(config_path=<matched scope>)` — AP list at
    the matched AOS 8 scope.
  - `aos8_get_alarms(config_path=<matched scope>)` — alarms at the
    scope.
  **Skip if:** `aos8` is not in `correlation_platforms` OR Anchor 2
  did not match an AOS 8 scope.

Record any infra anomaly (high alert count, low AP count vs.
expectation, site-health degraded) for inclusion in the matching
finding's prose.

---

### Stage 3 — Classification (D-06 / D-07 / D-08 / D-09 / D-10)

Classify each UXI issue record using the **verdict classification
table** below. The skill's severity decision derives from the issue
`code` (which describes WHAT failed), not from UXI's own severity
label (which is informational). This is D-10: infrastructure-layer
failures are CRITICAL; application-layer failures are DEGRADED.

| UXI symptom (issue.code prefix or sensor state) | Severity | Finding class |
|---|---|---|
| `sensor.offline` (or `isOnline=false`) | CRITICAL | REGRESSION (D-09) |
| `service_test.radius_auth.*` (RADIUS / 802.1x failure) | CRITICAL | REGRESSION (D-06 / D-10 network-layer) |
| `service_test.association.*` (wireless association failure) | CRITICAL | REGRESSION (D-06 / D-10) |
| `service_test.dns.*` (DNS lookup failure) | CRITICAL | REGRESSION (D-06 / D-10) |
| `service_test.dhcp.*` (DHCP failure) | CRITICAL | REGRESSION (D-06 / D-10) |
| `service_test.http.*` (HTTP / application failure, latency, throughput) | DEGRADED | DRIFT (D-07 / D-10 app-layer) |
| `networkName` has NO matching SSID in any reachable platform | DEGRADED | DRIFT (D-14) |
| Agent offline (`uxi_list_agents.items[i].isOnline=false`) | CRITICAL | REGRESSION (D-09 analog — sensors silently stop reporting) |
| `isOnline=true` AND `isTesting=false` AND no failing tests | DEGRADED | DRIFT (sensor online but idle) |
| `isOnline=true` AND `isTesting=true` AND zero open issues | (none — sensor healthy) | not emitted |
| `<platform> unreachable` (from Stage 0) | INFO | INFO |
| Site lookup miss (Anchor 2 no-match) | INFO | INFO |
| Client lookup miss (Anchor 3 no-match) | INFO | INFO |
| Open issue with severity `minor` and no service-test failure code | (suppressed; ignore in verdict) | not emitted |

**Verdict computation:**

- If any **CRITICAL** finding exists → verdict is **CRITICAL**.
- Else if any **DEGRADED** finding exists → verdict is **DEGRADED**.
- Else (every sensor online + testing, no DRIFT, no REGRESSION) →
  verdict is **GO** (D-08).

INFO findings never elevate the verdict (D-01).

---

### Stage 4 — Verdict + report rendering (SKILL-04)

Render the report using the EXACT template below. Every heading must
appear even if empty (write "None." in empty sections). Operators
paste this report verbatim into change-management tickets and
incident channels — consistency matters more than legibility, and
deviation from the template breaks downstream tooling.

**Paste-fallback substitutions (when Mode = paste-fallback):** UXI is
unreachable, so only pasted sensor data is available. Fill the UXI
inventory block as follows — do NOT leave these fields blank or omit them:
- Sensors: count the pasted sensor blocks
- Agents: `unknown (UXI unreachable)`
- Service tests configured: `unknown (UXI unreachable)`
- Groups: `unknown (UXI unreachable)`

```
**<VERDICT>** — <X> REGRESSION / <Y> DRIFT / <Z> INFO findings. This UXI tenant (<N> sensors, <M> agents, <K> reachable infrastructure platforms: <central / mist / aos8>) <one plain-English action sentence>.

## UXI cross-platform diagnostic — <ISO timestamp>
**Mode:** <live | paste-fallback>
**UXI reachability:** <ok | degraded | unavailable>
**Correlation platforms reachable:** <comma-separated list, or "none">
**Verdict:** <GO | DEGRADED | CRITICAL>

### UXI inventory
- Sensors: <N> total (<O> online, <I> testing, <F> with open issues)
- Agents: <N> total (<O> online)
- Service tests configured: <N>
- Groups: <N>

### REGRESSION findings (must fix — drives CRITICAL verdict)
- **Sensor `<sensor_name>` offline** at groupPath `<group_path>`. Site matched to <platform> site `<site_name>`. Site AP health: <summary or "site lookup missed">. Recommended action: verify sensor power / uplink / agent connectivity. (D-09; source: `uxi_get_sensor_status()`, `central_get_site_health()`)
- **Sensor `<sensor_name>` RADIUS auth failure** on networkName `<network_name>`. SSID matched to <platform> WLAN `<wlan_name>` (auth-type=`<auth_type>`). Sensor's OWN MAC `<sensor_mac>` last seen on AP `<ap_name>`. Recommended action: confirm RADIUS server reachability and NAS entry for the sensor's MAC. (D-06 / D-10; source: `uxi_get_sensor_status()`, `central_get_wlans()`, `central_get_clients()`)
- **Sensor `<sensor_name>` DNS failure** on networkName `<network_name>`. Site matched: <site_name>. Site alarms in window: <count>. Recommended action: verify DHCP-assigned DNS servers and upstream resolution from the matched site. (D-06 / D-10; source: `uxi_get_sensor_status()`, `central_get_site_health()`)
- **Sensor `<sensor_name>` DHCP failure** on networkName `<network_name>`. Recommended action: confirm DHCP pool capacity and reachability from the matched AP / scope. (D-06 / D-10; source: `uxi_get_sensor_status()`)
- **Sensor `<sensor_name>` association failure** on networkName `<network_name>`. Sensor's OWN MAC `<sensor_mac>`; SSID matched: <wlan_name>. Recommended action: verify WLAN is enabled at the matched site and the sensor radio is in range. (D-06 / D-10; source: `uxi_get_sensor_status()`, `mist_list_org_wlans()`)
- **Agent `<agent_name>` offline.** All sensors orchestrated by this agent stop reporting silently. Recommended action: restart agent or verify agent host. (D-09 analog; source: `uxi_list_agents()`)
- (or "None.")

### DRIFT findings (should address — drives DEGRADED verdict)
- **Sensor `<sensor_name>` HTTP / application test failing** on networkName `<network_name>`. Site `<site_name>` reports <count> active APs, <count> recent alarms — no infrastructure CRITICAL detected. (D-07 / D-10; source: `uxi_get_sensor_status()`, `central_get_aps()`, `central_get_alerts()`)
- **networkName `<network_name>` not matched to any SSID** in [<platforms checked>]. The wireless network may have been removed or renamed. (D-14; source: `central_get_wlans()`, `mist_list_org_wlans()`, `aos8_show_command()`)
- **Sensor `<sensor_name>` online but not testing** (`isTesting=false`). Recommended action: confirm at least one service test is assigned to the sensor's group. (source: `uxi_get_sensor_status()`, `uxi_list_service_tests()`)
- (or "None.")

### INFO findings (operational reference)
- **<platform> unreachable** — no correlation attempted; verify connectivity. (D-01; source: `health()`)
- **groupPath top segment `<segment>` not matched to a site** in [<platforms checked>]. Site-level infra checks were skipped for affected issues. (source: `central_get_sites()`, `mist_get_site_info()`)
- **Sensor `<sensor_name>` (sensor's OWN MAC `<sensor_mac>`) not found in client lookup** on [<platforms checked>] — sensor may be disassociated. (source: `central_get_clients()`, `mist_search_org_wireless_clients()`, `aos8_find_client()`)
- (or "None.")

### Caveats
- This report correlates **synthetic** UXI sensor tests to infrastructure state — it does NOT measure end-user impact directly. A CRITICAL verdict means a synthetic probe failed, not necessarily that real users are affected.
- UXI `macAddress` values in this report are the **sensors' OWN MAC addresses** — never end-user device MACs. Anchor 3 attribution is "which AP is the sensor attached to," not "which user is affected."
- Paste-mode reports include only the sensors the operator pasted; sensors not pasted are invisible to the correlation. Live mode walks the full tenant.
- Findings are best-effort against the reachable platforms only. Platforms marked unreachable in INFO contribute zero correlation rows — the absence of a finding for an unreachable platform does NOT imply that platform is healthy.
```

---

## Decision matrix (edge cases)

| Condition | Action |
|---|---|
| Sensor `isTesting=true` AND no open issues returned | Healthy — do NOT emit a finding for this sensor. |
| `networkName == "-"` (wired sensor with no named network) | Skip Anchor 1 (SSID lookup) for this record; Anchors 2-4 still run. |
| `groupPath` has only one segment (no `>`) | The whole string IS the top segment — use it directly for Anchor 2. |
| `groupPath` is empty / null | Skip Anchor 2 AND Anchor 4 (no site → no site-infra check). Emit INFO. |
| Sensor's MAC not found in any platform's client list | Acceptable when `isOnline=false`. Emit INFO; do NOT promote to CRITICAL on this basis alone. |
| `correlation_platforms` is empty (zero reachable) | Run Stage 1 / Stage 1' anyway. Emit verdict from UXI-only signals (sensor offline → CRITICAL; otherwise GO). Add INFO for every unreachable platform. |
| Multiple platforms match the SAME networkName | Record the match in each platform; do NOT collapse rows. Each match becomes a separate `(source: ...)` attribution in the finding. |
| Pasted block in Stage 1' is missing a field | Treat the missing field as `"-"`. Do not infer values. Emit one INFO note in the report: `Paste block for sensor '<name>' was missing field '<field>'.` |
| UXI returns hundreds of sensors, most healthy | Inventory the totals in the metadata block; emit findings only for sensors with open issues. Do NOT list every healthy sensor. |
| `health()` itself fails | Treat as `uxi` unavailable → Stage -1 paste-mode path. Inform the operator that infrastructure-platform reachability is also unknown, and recommend running `infrastructure-health-check` separately. |

---

## Output formatting (mandatory)

These rules apply to every finding in every section of the Stage 4
template. They are copied (with one-word substitutions) from the
canonical hygiene rules in `aos-migration.md` lines 1316-1326 — DO
NOT relax them.

1. **No raw JSON blobs.** When citing UXI sensor data or a platform
   API response, extract and quote only the specific field value
   relevant to the finding. Never dump the full response dict.
2. **No tool-call syntax in finding text.** Tool names belong in the
   `(source: tool_name())` attribution at the end of the finding —
   never inside the finding sentence itself. Findings read as
   prose; attributions read as code references.
3. **No stack traces.** If a tool call raises an exception while
   running the skill, emit a brief one-line error note and continue
   with the next anchor. Never include a Python traceback in the
   report.
4. **No ellipsis or truncation markers.** Do not write `...`,
   `[truncated]`, `etc`, or similar. If a response is large,
   summarise the salient values in prose; do not abbreviate with
   placeholder markers.
5. **No fabricated documentation anchors.** If a finding has no
   real anchor (no decision ID, no VSG section, no doc reference),
   the cell reads literally `none`. Do not invent IDs.
6. **No invented tool names.** If a `uxi_*` / `central_*` / `mist_*`
   / `aos8_*` tool does not exist for a row, write `[no tool —
   manual verification required]`. Tool names must resolve to a
   registered tool; the CI regression test validates this.

### Output format is mandatory — do NOT substitute alternatives

Every output element specified in the Stage 4 template — verdict
paragraph, metadata block, UXI inventory block, REGRESSION / DRIFT
/ INFO finding lists, Caveats section — must be produced in
**exactly the format shown**. Do NOT substitute:

- **Diagrams, charts, ASCII art, or rendered visualizations** in
  place of the markdown bullet lists. The output is paste-able into
  customer change tickets and incident Slack threads; formats that
  don't render as plain text are out of scope.
- **Prose paragraphs** in place of finding lists. Findings are
  bullets so an operator can scan + cite each one independently.
- **Collapsed multi-finding rows** (e.g. "These 3 sensors all have
  DNS issues") in place of one bullet per sensor. Each finding is
  its own row so each can be acted on independently.
- **Reframed verdicts** (e.g. "tentatively CRITICAL" or "DEGRADED
  with caveats"). Verdicts are the literal three values: **GO**,
  **DEGRADED**, or **CRITICAL**.

If you believe a different format would be more legible, the answer
is no — operators want paste-ability and consistency across runs
more than they want artistic legibility.

---

## Example queries that should trigger this skill

> "uxi sensors failing"
> "why are my synthetic tests failing"
> "correlate uxi failures to central"
> "what's wrong with my uxi sensors"
> "are my uxi sensors healthy"
