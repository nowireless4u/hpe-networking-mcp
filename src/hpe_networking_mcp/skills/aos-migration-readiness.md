---
name: aos-migration-readiness
title: AOS 6 / AOS 8 / Instant AP → AOS 10 migration readiness audit (PoC)
description: |
  TRIGGERS — call this when the user asks: "AOS 8 to 10 migration",
  "AOS 6 to AOS 10", "Instant AP migration to AOS 10", "IAP to AOS 10",
  "migration readiness", "am I ready to upgrade to AOS 10", "audit my
  AOS 8 environment for migration", "validate my migration plan",
  "check Central readiness for AOS 10 cutover", "Tunnel vs Bridge vs
  Mixed mode planning", "switchport configuration for AOS 10",
  "RADIUS NAD changes for AOS 10". Anchored on Aruba Validated
  Solution Guide — Campus Migrate. Operator runs a fixed set of CLI
  commands on their source platform (AOS 6 Conductor / AOS 8 Mobility
  Conductor + Controller / IAP Virtual Controller) and pastes all
  outputs into the chat as one bundle; the audit parses the bundle,
  runs Central-side API checks, applies VSG-anchored rules per
  source/target combination across ~50 granular checks, and emits
  a go/no-go readiness report with cutover sequencing and rollback
  validation. PoC — for production migrations, use VALID8 (HPE
  channel-partner-only discovery + analysis tool).
platforms: [central]
tags: [central, migration, aos8, aos6, iap, aos10, readiness, audit, vsg]
tools: [health, central_get_scope_tree, central_get_devices, central_get_aps, central_get_sites, central_get_site_name_id_mapping, central_recommend_firmware, central_get_config_assignments, central_get_server_groups, central_get_wlan_profiles, central_get_roles, central_get_named_vlans, clearpass_get_network_devices, clearpass_get_device_groups, clearpass_get_server_certificates, clearpass_get_local_users, greenlake_get_subscriptions, greenlake_get_workspace, greenlake_get_devices, aos8_get_md_hierarchy, aos8_get_effective_config, aos8_get_ap_database, aos8_get_cluster_state, aos8_show_command, aos8_get_clients, aos8_get_bss_table, aos8_get_active_aps, aos8_get_ap_wired_ports]
---

# AOS 6 / AOS 8 / Instant AP → AOS 10 migration readiness audit (PoC)

## Objective

Decide **GO / BLOCKED / PARTIAL** for a migration from a legacy Aruba WLAN
platform (AOS 6, AOS 8, or Instant AP) to AOS 10 / Aruba Central.

Anchored on **Aruba Campus Migrate VSG** — covering the three migration paths:

- AOS 6 Campus → AOS 10 Tunnel or Bridge Mode (VSG §225-§588)
- Instant AP cluster → AOS 10 Bridge Mode (VSG §589-§932)
- AOS 8 Campus → AOS 10 Tunnel or Bridge or Mixed Mode (VSG §934-§1336)

The audit combines two data sources:

1. **Operator-pasted CLI output** from the source platform (the same data items VALID8 collects). The skill tells the operator exactly which commands to run; operator runs them in one CLI session and pastes the bundle back into chat.
2. **Central-side API checks** — site/scope tree, AP onboarding state, licenses, ClearPass NAD list, GreenLake subscriptions, ClearPass certificate state.

**Read-only.** Identifies blockers; does not fix them. For production migrations, use VALID8 (HPE channel-partner-only) for automated discovery — this skill is a PoC for the in-chat workflow.

## PoC scope + roadmap caveat

This skill expects the operator to **paste CLI output directly into chat**. That output may contain customer-identifiable data (server IPs, MAC addresses, cleartext RADIUS shared secrets if `encrypt disable` is in use, local user databases, etc.). For this PoC the audit does **not** auto-redact or tokenize — that's deferred until a future architecture where the config can be uploaded to a place the AI client never sees, with the MCP server alone owning the parse + redact.

The skill's job here is to prove the in-chat workflow produces credible readiness findings on a representative dataset; sanitization is a separate problem.

## Procedure — 6 stages, ~50 granular checks

### Stage -1 — Session-start AOS8 detection (DETECT-01)

Before beginning the Stage 0 operator interview, call `health()` once and inspect the per-platform status.

**If `aos8.status == "ok"`** (AOS8 platform is configured and reachable):
> Announce to the operator, verbatim:
> **"AOS8 API mode — live data. Stage 1 collection will run via API; no CLI paste required for the AOS8 source path."**
>
> Then proceed to Stage 0. The Stage 1 AOS8 section will use the live-mode sub-path (API calls in four grouped batches — COLLECT-01..04). The paste table is not used unless an individual API batch fails.

**Otherwise** (AOS8 not configured, status `unavailable` / `degraded`, or no AOS8 secrets mounted):
> Proceed silently to Stage 0. Make no announcement. The paste-driven flow is unchanged for AOS6, IAP, and unreachable-AOS8 sessions. Stage 1 will use the paste-fallback sub-path.

This detection step never blocks the audit — failures silently fall through to the existing paste flow.
### Stage 0 — Operator interview (mandatory before data collection)

Lock these answers into the audit context:

1. **Source platform** — which legacy environment are we migrating from?
   - `aos6` — Aruba OS 6 Mobility Conductor + Mobility Controllers (Conductor-Member or standalone)
   - `aos8` — Aruba OS 8 Mobility Conductor + Mobility Controllers
   - `iap` — Instant AP cluster (Virtual Controller managed; VC may be local-only, AirWave-managed, or Central-managed)
2. **Current AirWave state** (AOS 6 / AOS 8 only) — is AirWave currently in the path? AirWave + AMON + SNMP are deprecated in AOS 10 (VSG §312-§313, §514-§515).
3. **Target SSID forwarding mode** — which AOS 10 model is the target?
   - `tunnel` — keep tunneled traffic via Gateway cluster (AOS 10 Tunnel Mode)
   - `bridge` — local-bridged at AP (AOS 10 Bridge Mode — required for IAP migrations per VSG §672-§676)
   - `mixed` — per-SSID mode mix
4. **Migration scope** — single-site PoC, multi-site, or fleet-wide?
5. **Cluster type** (AOS 8 only) — L2 cluster, L3 cluster, or LMS/Backup LMS pattern? (Affects HA mapping per VSG §1161-§1162)
6. **L3 Mobility in use** (AOS 6 / AOS 8 / IAP) — yes/no? AOS 10 **eliminates** L3 Mobility (VSG §897-§900); requires L2-adjacent VLANs in the roaming domain instead.
7. **HA expectation in AOS 10** — Auto Group, Auto Site, or Manual? (per VSG §410-§411, §1161-§1162)

The audit must NOT proceed without all seven answers.

### Stage 1 — Operator data collection (paste-driven, all-at-once)

Tell the operator: *"Run all of the commands below in one CLI session, save the entire output, and paste the bundle back here in one message. Pre-flight tips:* `no paging` *to avoid space-bar prompts; enable session logging in PuTTY / SecureCRT first;* `encrypt disable` *if you want passphrases visible in cleartext (note: this exposes RADIUS shared secrets — confirm before pasting)."*

Per VSG §1832-§1872 — *"Checklist for Information Collection"* — the data set differs per source platform.
#### If source = `aos8` (anchor: VSG §1671-§1873)

##### AOS8 live-mode sub-path — used when Stage -1 announced "AOS8 API mode"
No CLI paste required. Calls AOS8 tools directly in **four grouped batches** (COLLECT-01..04). On any tool error, fall back per-batch to an exact-CLI paste request for that batch only.

**Batch 1 — MD hierarchy + per-node effective config (COLLECT-01)**
1. Call `aos8_get_md_hierarchy()`. Expected: node tree `/md`, `/md/<region>`, `/md/<region>/<site>`, `/md/<region>/<site>/<ap-group>`.
2. For each config object type (`ap_sys_prof`, `virtual_ap`, `ssid_prof`, `aaa_prof`, `aaa_server_group`, `wlan_ssid_profile`, `reg_domain_profile`, `arm_profile`, `dot11a_radio_prof`, `dot11g_radio_prof`), call `aos8_get_effective_config(object_name="<type>", config_path="/md")`. Tool is **object-scoped** — iterate; results feed Stage 3 rule checks.
3. Call `aos8_show_command(command="show configuration effective detail")` for a text capture.
*On batch 1 error:* ask operator to run `show configuration node-hierarchy` and `show configuration effective detail <node>` and paste. Continue to Batch 2.
**Batch 2 — Full AP inventory (COLLECT-02)**
Call `aos8_get_ap_database()`. Expected: per-AP `model`, `mac`, `serial`, `ip_mode` (DHCP / static), `group`, `ap_name`, `ip` — replaces `show ap database long` (VSG §1740, §1851-§1852). Stage 3 RULES-04 reuses `ip_mode` directly.
*On batch 2 error:* ask operator to run `show ap database long` and paste. Continue to Batch 3.
**Batch 3 — Cluster state + running-config + local-user db + inventory + ports (COLLECT-03)**
1. Call `aos8_get_cluster_state()`. Expected: cluster L2 / L3 status — replaces `show lc-cluster group-membership` (VSG §2399).
2. Call `aos8_show_command(command="show running-config")`.
3. Call `aos8_show_command(command="show local-user db")`.
4. Call `aos8_show_command(command="show inventory")`.
5. Call `aos8_show_command(command="show port status")` and `aos8_show_command(command="show trunk")`.
*On batch 3 error:* identify which step(s) failed; ask operator for **only the failed CLI commands** by name. Continue to Batch 4.
**Batch 4 — Client baseline + BSS/SSID table + active APs + AP wired ports (COLLECT-04)**
1. Call `aos8_get_clients()`. Expected: aggregate counts (clients-by-SSID, total, users-with-roles) — replaces `show ap association` + `show user-table`.
2. Call `aos8_get_bss_table()`. Expected: SSID name + AP-broadcasting count + radio band — replaces `show ap essid`.
3. Call `aos8_get_active_aps()`. Expected: active AP list with channel / TX power / client count — replaces `show ap active`.
4. For each AP from Batch 2 (or a representative sample), call `aos8_get_ap_wired_ports(ap_name="<ap_name>")`. Tool is **per-AP** — iterate. Replaces `show ap lldp neighbors`.
*On batch 4 error:* identify which call(s) failed; ask operator to run the failed command(s) and paste. Continue to Stage 2.

After all four batches, present a compiled Stage 1 inventory table (AP count, controller list, cluster state, local-user count, SSID count) before Stage 2.

##### AOS8 paste-fallback sub-path — used when Stage -1 was silent (AOS8 unreachable or not configured)
Use the same 16-command bundle (API path unavailable):

| # | Where | Command | Purpose (VSG anchor) |
|---|---|---|---|
| 1 | Mobility Conductor | `show configuration node-hierarchy` | Plan AOS 10 Site / Site Collection / Device Group structure (§1834-§1835) |
| 2 | Mobility Conductor | `show configuration committed <node>` (per node from #1) | What's committed at each node (§1847-§1850) |
| 3 | Mobility Conductor | `show configuration effective detail <node>` (per node from #1) | Resolved/inherited config at each node (§1847-§1850) |
| 4 | Mobility Conductor | `show ap database long` | AP inventory: model, MAC, serial (§1740, §1851-§1852) |
| 5 | Mobility Controller (each) | `show ap-group` then `show ap-group <group_name>` per group | AP-group → VAP / RF-profile mapping (§1756-§1761) |
| 6 | Mobility Controller (each) | `show ap association` and `show user-table` | Active client baseline for post-cutover diff (§1769-§1770) |
| 7 | Mobility Controller (each) | `show ap lldp neighbors` | Switch / port per AP (cutover troubleshooting reference) (§1787) |
| 8 | Mobility Controller (each) | `show ap essid` | Active SSID + AP-per-SSID counts (§1796) |
| 9 | Mobility Controller (each) | `show ap active` | Active AP list + radio statistics (§1806) |
| 10 | Mobility Controller (each) | `show running-config` | Full config: firmware version, RADIUS server groups, NAS-IP value, VRRP VIP, auth servers (§1815) |
| 11 | Mobility Controller (each) | `show port status` | Identify active ports (§1881-§1882) |
| 12 | Mobility Controller (each) | `show trunk` | VLAN/port assignments (§1883-§1884) |
| 13 | Mobility Controller (each) | `show controller-ip` | Controller management IP + VLAN (§1885-§1886) |
| 14 | Mobility Controller (each) | `show local-user db` | Local users (need to be re-homed in AOS 10 — VSG §1898-§1899) |
| 15 | Mobility Controller (each) | `show inventory` | Serial + MAC of controller (§1900-§1901) |
| 16 | Mobility Controller (each) | `show lc-cluster group-membership` | Cluster L2/L3 status — required pre-flight before single-controller upgrade (§2399) |

Operator also captures, if available:
- AirWave Group + Site structure (VSG §1820-§1827, cross-validation against CLI)
- Configuration backup (TAR/snapshot) of each Mobility Controller per VSG §2435 — *"Always perform a backup and save a copy of the appliance configuration prior to any upgrade."*

#### If source = `aos6` (anchor: VSG §225-§588)

Use the AOS 8 command set as a baseline; substitute as needed:

- AOS 6 standalone Conductor (no Mobility Conductor): drop the `node-hierarchy` / `committed` / `effective` triplet — use `show running-config` only on the Conductor.
- AOS 6 Conductor-Member: use the same commands as AOS 8.
- AOS 6 has additional considerations vs AOS 8: AP Override is **supported** in AOS 6 but not AOS 8 (VSG §422-§426). Look for AP-override stanzas in the running-config.
- HA pattern naming: AOS 6 has *LMS / Backup LMS, Active-Active, AP Fast Failover* (VSG §410-§411) — different from AOS 8's L2/L3 cluster terminology.

Plus AirWave (per VSG §1818-§1827):
- Group / Site structure export
- AP inventory + associated SSIDs
- Per-AP configuration overrides

#### If source = `iap` (anchor: VSG §603-§932)

| # | Where | Command | Purpose |
|---|---|---|---|
| 1 | IAP cluster Virtual Controller | `show running-config` | Full IAP config: cluster + WLANs + RF + VC config |
| 2 | IAP cluster Virtual Controller | `show aps` | Cluster member list (note which is acting as VC / Conductor AP per VSG §606-§607) |
| 3 | IAP cluster Virtual Controller | `show clients` | Active client baseline for post-cutover diff |
| 4 | IAP cluster Virtual Controller | `show network` | SSID list + auth modes + VC-managed (NAT'd) flag per SSID |
| 5 | IAP cluster Virtual Controller | `show ap-env` | Per-AP environment / overrides (these become device-level overrides in AOS 10) |
| 6 | IAP cluster Virtual Controller | `show summary` | Cluster state + VC IP |
| 7 | IAP cluster Virtual Controller | `show ssid-profile <name>` (per SSID from #4) | Per-SSID profile detail (auth, VLAN, security) |
| 8 | IAP cluster Virtual Controller | `show ap-group` | Cluster-level AP group config |
| 9 | IAP cluster Virtual Controller | `show audit-trail-log` | Recent config changes (cross-check with operator's expected state) |
| 10 | Switch attached to APs | LLDP neighbor query (varies per switch vendor — operator's call) | Switch / port per AP for cutover reference |

Plus, if AirWave is in use — same AirWave exports as AOS 6 / 8.

### Stage 2 — Parse the pasted bundle

For each pasted artifact, extract the data points listed below. The audit produces an **inventory table** as part of the report; the parsed values feed the rule checks in Stage 3.

##### AOS8 live-mode sub-path — used when Stage -1 announced "AOS8 API mode"

If AOS8 live mode is active (Stage -1 announced API mode), Stage 1 already collected every AOS8 data point in the table below via the four-batch live-mode sub-path. **Skip paste parsing for AOS8 data points and proceed directly to Stage 3.** The AOS8 extraction table below remains authoritative for the paste-fallback path (used when AOS8 is unreachable, or for AOS6 / IAP source platforms which always use paste).

#### AOS 8 — what to extract from each artifact

| Artifact | Extract | VSG anchor |
|---|---|---|
| `show configuration node-hierarchy` | Hierarchy tree (`/md`, `/md/<region>`, `/md/<region>/<site>`, `/md/<region>/<site>/<ap-group>`) → suggested AOS 10 Sites / Site Collections / Device Groups | §1834 |
| `show configuration committed <node>` + `show configuration effective detail <node>` | Per-node config keys; flag features in the "doesn't transfer" list (Stage 3) | §1847-§1850 |
| `show ap database long` | Per-AP: model, MAC, serial, IP, IP-mode (static vs DHCP), AP-group, SSIDs, ap-name → table for the AOS 10 onboarding plan | §1740, §1851-§1852 |
| `show ap-group <name>` | Per-group: VAP profile name, 802.11 radio profile, ARM profile (replaced in AOS 10), regulatory domain profile (replaced) | §1855-§1857 |
| `show ap association` + `show user-table` | Aggregate counts: clients-by-SSID, total-clients, users-with-roles → baseline for post-cutover diff | §1858-§1861 |
| `show ap lldp neighbors` | Per-AP: switch hostname / port → cutover wiring reference | §1862-§1864 |
| `show ap essid` | SSID name + AP-broadcasting count per SSID + radio band | §1864-§1865 |
| `show ap active` | Active AP list with radio stats (channel, TX power, client count) → RF baseline | §1866-§1867 |
| `show running-config` (controller) | Controller firmware version (must be 8.10.0.12 / 8.12.0.1+ per §1643-§1645); cluster definitions; RADIUS server groups; NAS-IP value; VRRP virtual IP; AP system profiles with LMS IP (must be VRRP VIP, not individual controller IP per §1654-§1656); 802.1X auth servers; captive portal config; user roles + ACLs | §1815 |
| `show port status` + `show trunk` | Switch-side port status per controller; VLAN trunking → AP-uplink VLAN baseline for switchport-config validation | §1881-§1884 |
| `show controller-ip` | Controller management IP + VLAN | §1885-§1886 |
| `show local-user db` | Local user list — these can't move directly to AOS 10 (no Internal Auth Server in AOS 10 per §1134-§1136); operator must plan ClearPass migration | §1898-§1899 |
| `show inventory` | Controller serial + MAC + model | §1900-§1901 |
| `show lc-cluster group-membership` | Cluster L2/L3 status; pre-flight blocker if cluster isn't healthy at audit time | §2399 |

#### AOS 6 — extra extraction items (vs AOS 8)

- **AP Override stanzas in running-config** — per VSG §422-§426, AP Override is supported in AOS 6 but not AOS 8 / not in AOS 10. Each AP-override must map to an AOS 10 device-level override (DRIFT, not REGRESSION; VSG explicitly provides a device-level-override mapping in AOS 10).
- **HA mode**: scan running-config for *LMS-IP*, *Backup-LMS-IP*, *AP Fast Failover* — map to AOS 10 Auto Group / Auto Site / Manual per VSG §410-§411.
- **AirWave references**: AOS 6 deployments commonly require SNMP / AMON to AirWave (VSG §312-§313, §285-§287). These are deprecated in AOS 10 — flag the firewall rules / monitoring agent dependencies.

#### IAP — what to extract

| Artifact | Extract | VSG anchor |
|---|---|---|
| `show running-config` | VC IP / cluster ID; SSIDs and their security; static-vs-DHCP AP IP; PoE settings; AP group config; RADIUS server config; NAS-IP source (VC IP if Dynamic Radius Proxy enabled per §721-§723) | §603-§669 |
| `show aps` | Cluster member list; identify which AP is currently acting as VC / Conductor AP | §603-§607 |
| `show clients` | Active client baseline | §1763-§1770 (analogous to AOS 8) |
| `show network` | SSIDs + auth modes; flag VC-managed (NAT'd) WLANs — these change behavior in AOS 10 Bridge Mode (no central NAT point per §854-§857, §907-§909) | §641-§645 |
| `show ap-env` | Per-AP environment overrides → these become device-level overrides in AOS 10 | §735-§739 |
| `show summary` | Cluster state, VC IP — note that IAP VC is deprecated in AOS 10 (per §752-§756, §1262-§1264); Bridge Mode AOS 10 scales ~4× IAP cluster limits |
| `show ssid-profile <name>` | Per-SSID profile detail | §641-§645 |
| `show ap-group` | Cluster-level AP group config | n/a |
| `show audit-trail-log` | Recent config changes (sanity for the operator's expected baseline) | n/a |

### Stage 3 — Apply VSG-anchored readiness rules

Different rule sets apply based on **source platform** AND **target SSID mode**. The audit walks the rules below and classifies each finding as **REGRESSION** (must fix before migration), **DRIFT** (should address; not blocking), or **INFO** (operator reference).

#### AOS8 live-mode sub-path — rules evaluated from Stage 1 data (used when Stage -1 announced "AOS8 API mode")

When AOS8 live mode is active, RULES-01, RULES-02, and RULES-04 are evaluated directly from the Stage 1 batch data already in context — no re-fetching, no operator paste. RULES-03 result is **pending Stage 4 A11** (ClearPass cross-check). After this sub-path, continue with the universal + AOS6/8 + per-target-mode rule tables below — those apply regardless of source path.

Each finding below uses the format **Severity — Description (VSG §anchor) (source: `tool_call(args)`, Batch N)**.

##### RULES-01 — VRRP VIP for AP system profiles (REGRESSION, VSG §1654-§1657)

From the Batch 1 `aos8_get_effective_config(object_name='ap_sys_prof', config_path='/md')` response, inspect the LMS IP field (and Backup-LMS IP, if present) of each `ap_sys_prof` returned. If the LMS IP matches a controller management IP (any individual managed-device address from `aos8_get_md_hierarchy()` Batch 1) rather than the VRRP virtual IP, emit:

- **REGRESSION** — AP system profile `<profile_name>` LMS IP is `<lms_ip_value>`, which matches an individual controller management IP rather than the VRRP virtual IP. APs will strand on first controller upgrade. (VSG §1654-§1657) (source: `aos8_get_effective_config(object_name='ap_sys_prof', config_path='/md')`, Batch 1)

Reference the field by intent ("the LMS IP field in the `ap_sys_prof` response") — do **not** pin a specific JSON key path; introspect the response structure at runtime. If multiple `ap_sys_prof` objects return, emit one finding per profile with the wrong IP.

*If Batch 1 failed:* RULES-01 cannot be evaluated from live data. Mark as **inconclusive — paste required** and consult any per-batch fallback paste of `show running-config` already supplied. Equivalent paste-mode rule is C2 below.

##### RULES-02 — ARM / radio / regulatory-domain profile detection (DRIFT, VSG §1163-§1166)

From the Batch 1 effective-config results for `arm_profile`, `dot11a_radio_prof`, `dot11g_radio_prof`, and `reg_domain_profile` (each fetched via `aos8_get_effective_config(object_name=<profile_type>, config_path='/md')`), detect presence of any configured object across all four profile types. Empty/absent at every queried path means no DRIFT for that profile type — distinguish "envelope present" from "objects present".

If any of the four profile types has at least one configured object at the queried `/md` root scope, emit:

- **DRIFT** — Active legacy RF profiles detected at `/md` root: `<list of profile_type=profile_name pairs>`. These are replaced by Central AirMatch + ClientMatch in AOS 10 (channel, TX power, channel-width, DFS, band-steering all move to Central). (VSG §1163-§1166) (source: `aos8_get_effective_config(object_name='arm_profile|dot11a_radio_prof|dot11g_radio_prof|reg_domain_profile', config_path='/md')`, Batch 1)

Per-AP-group enumeration is out of scope for this phase — Batch 1 collects at the `/md` root and AOS8 effective config inherits down. Report at the granularity Stage 1 collected.

*If Batch 1 failed:* RULES-02 cannot be evaluated from live data. Mark as **inconclusive — paste required** and consult any pasted `show configuration effective detail` output. Equivalent paste-mode rule is C4 below.

##### RULES-03 — Local user count cross-check (DRIFT) — pending Stage 4 A11

Stage 1 Batch 3 already collected the AOS8 local-user count via `aos8_show_command(command='show local-user db')`. The cross-check against ClearPass executes in **Stage 4 A11** (`clearpass_get_local_users()`) — do **not** call ClearPass twice. Stage 3 emits no RULES-03 finding here; the determination is deferred. See Stage 4 A11 for the dual-source-of-truth comparison.

*If Batch 3 failed:* The AOS8 local-user count is unavailable; A11 will note "AOS8 count unknown — paste of `show local-user db` required for full cross-check".

##### RULES-04 — Static AP IP detection (REGRESSION, VSG §1232-§1234)

From the Batch 2 `aos8_get_ap_database()` response, inspect the `ip_mode` field of each AP entry. For every AP whose `ip_mode` is anything other than DHCP (e.g., `static`), emit one finding:

- **REGRESSION** — AP `<ap_name>` (MAC `<wired_mac>`) has `ip_mode='<value>'` (statically addressed). AOS 10 does not support static AP IPs — APs must be DHCP-addressed before AP convert. (VSG §1232-§1234) (source: `aos8_get_ap_database()`, Batch 2)

If no APs have a non-DHCP `ip_mode`, emit a single INFO confirmation: "AP database shows all APs DHCP-addressed (RULES-04 PASS)."

*If Batch 2 failed:* RULES-04 cannot be evaluated from live data. Mark as **inconclusive — paste required** and consult any pasted `show ap database long` output. Equivalent paste-mode rule is U2 (Universal rules table) below.

#### Universal rules (apply to all source → target combinations)

| # | Check | Severity | Anchor |
|---|---|---|---|
| U1 | TCP 443 outbound from AP/controller management to Aruba Central reachable; firewall rules permit Central FQDNs | **REGRESSION** if blocked | VSG §312-§319, §1190-§1193 |
| U2 | DHCP available for AP IP assignment (static APs are NOT supported on AOS 10) | **REGRESSION** if any AP is statically addressed | VSG §1232-§1234, §475-§477 |
| U3 | GreenLake account / `workspace_id` configured + Central / AOS 10 subscriptions present | **REGRESSION** if missing | VSG §1619-§1620 |
| U4 | Central scope tree set up (Sites + Site Collections + Device Groups) for the migration's target sites | **DRIFT** if not pre-created (operator can do at cutover; per VSG §30-§34 this is part of "New Central Readiness") | VSG §30-§34 |
| U5 | NAD/RADIUS client list on RADIUS server (typically ClearPass) updated for the new source IPs (see per-target-mode rules below for which IPs) | **REGRESSION** if not updated before cutover | VSG §1121-§1141 |
| U6 | AAA FastConnect (EAP-Offload) **NOT in use** — feature is **not supported in AOS 10** | **REGRESSION** if in use | VSG §1137-§1141, §393-§396, §728-§731 |
| U7 | Internal Authentication Server **NOT in use** (no Local Auth Server in AOS 10) | **REGRESSION** if in use; operator must plan ClearPass / Cloud Auth | VSG §1134-§1136, §390-§392, §725-§727 |
| U8 | Cryptographic key distribution flow: in AOS 10, key distribution is managed by Central (VSG §915-§917). Verify that any custom OKC / 802.11r config doesn't depend on AOS 8 controller-managed key distribution | **DRIFT** | VSG §915-§917 |
| U9 | Round-trip time latency to Central services < 500 ms for global / WAN-served sites | **DRIFT** if WAN-served sites haven't been measured | VSG §919-§920 |
| U10 | Backup taken of source-platform configuration before cutover | **REGRESSION** if no backup procedure established | VSG §2435 — *"Always perform a backup..."* |
| U11 | Rollback procedure documented for each cutover stage (controller upgrade, AP convert) | **DRIFT** if not documented | VSG §1624, §2590-§2591 |

#### AOS 6 / AOS 8 source — additional rules

| # | Check | Severity | Anchor |
|---|---|---|---|
| C1 | **AOS 8 controller firmware prerequisite**: AOS 8 controllers must be on `8.10.0.12`, `8.12.0.1`, or later before AOS 10 swap | **REGRESSION** if below | VSG §1643-§1649 |
| C2 | **AP discovery configured properly**: AP system profiles use VRRP virtual IP (NOT individual controller IP); OR DHCP option 43/60 / DNS aruba-master / ADP working | **REGRESSION** if APs would strand on first controller upgrade | VSG §1651-§1657 |
| C3 | **AP Override in use** (AOS 6 only — supported in 6, not in 8) | **DRIFT** — replaced by device-level override pattern in AOS 10 | VSG §422-§426 |
| C4 | **ARM Profiles / Dot11a/g Radio Profiles / Regulatory Domain Profiles in active use** | **DRIFT** — replaced by **AirMatch** in Central. Channel, TX power, channel-width, DFS decisions all move to AirMatch (per §412-§415, §1163-§1166). ClientMatch tunables (Band Steering / Sticky / Load Balancing) are no longer adjustable per §416-§418, §1167-§1169 — fixed at Central WLAN Control & Services. | VSG §412-§418, §1163-§1169 |
| C5 | **Cluster topology mapping**: AOS 8 L2/L3 cluster + LMS/Backup LMS → AOS 10 Auto Group / Auto Site / Manual modes. Operator selected target mode in Stage 0; verify it matches the source pattern's cleanest map. | **INFO** | VSG §1161-§1162, §410-§411 |
| C6 | **Mobility Conductor configuration scope**: AOS 8 Conductor-Member hierarchy → AOS 10 Site / Collection / Group mapping (planned via `show configuration node-hierarchy` extract) | **INFO** — produce the suggested mapping table | VSG §1529-§1559 |
| C7 | **AirWave deprecation**: any monitoring tooling that depends on AirWave (SNMP, AMON, syslog targets, scripts) needs replacement before cutover | **DRIFT** | VSG §312-§313, §514-§515 |
| C8 | **Internal management LAN Internet block**: AOS 6 / AOS 8 deployments commonly block Internet from management LAN; AOS 10 needs outbound TCP 443 to Central from APs (and any tunneled-mode gateway) | **REGRESSION** if currently blocked and not yet permitted | VSG §315-§317, §1067-§1070 |
| C9 | **Internal AirGroup / Bonjour proxies**: the way mDNS / Bonjour is handled may differ in AOS 10. Operator must validate per-SSID. | **DRIFT** | VSG §641-§645 (datapath patterns) |
| C10 | **Captive Portal certificate**: replace any default cert before AOS 10 cutover (per VSG §364, §370 — same rule as scope audit) | **REGRESSION** if default cert | VSG §364, §370 |

#### IAP source — additional rules

| # | Check | Severity | Anchor |
|---|---|---|---|
| I1 | **Target mode = Bridge** required for IAP migration (Tunnel target requires standing up new gateway clusters) | **REGRESSION** if operator picked Tunnel | VSG §672-§676 |
| I2 | **AP cluster size**: AOS 10 Bridge Mode max AP-management subnet `/20`; user VLANs no greater than `/20`; max **500 APs / 5,000 clients** per Bridge Mode roaming domain (current at VSG publication; not hard limits) | **DRIFT** if currently exceeded | VSG §544-§548, §893-§895, §865-§867 |
| I3 | **L2 adjacency for AP management subnet** (across the roaming domain) | **REGRESSION** if currently routed | VSG §1247-§1248, §494-§495 |
| I4 | **L2 adjacency for wireless user VLANs** (across roaming domain — AOS 10 eliminates L3 Mobility per VSG §897-§900) | **REGRESSION** if currently routed and L3 Mobility was load-bearing | VSG §897-§900 |
| I5 | **VC-managed (NAT'd) WLANs**: any SSID with the *Virtual Controller Managed* flag must have NAT + DHCP services moved upstream (L3 switch / firewall / router / Aruba Gateway) before cutover — AOS 10 Bridge Mode APs do **not** provide NAT or DHCP | **REGRESSION** if VC-managed WLANs depend on VC NAT/DHCP and upstream services aren't in place | VSG §641-§645, §854-§857, §907-§909 |
| I6 | **Dynamic Radius Proxy (DRP)**: deprecated in AOS 10 Bridge Mode (no VC). If currently relied on for RADIUS source-IP consistency, replace with per-AP NAD entries on the RADIUS server | **REGRESSION** if currently relied on | VSG §1262-§1264, §721-§723 |
| I7 | **Secure PAPI between APs** (UDP 8211): AOS 10 requires Secure PAPI permitted between all APs in the roaming domain (firewall / ACL on the management VLAN must allow) | **REGRESSION** if currently blocked | VSG §902-§905 |
| I8 | **L3 Mobility deprecation**: if the IAP design currently uses cross-cluster L3 Mobility, AOS 10 doesn't have it. The expanded Bridge Mode roaming domain (~4× IAP) often eliminates the need but must be validated. | **DRIFT** if L3 Mobility was load-bearing | VSG §897-§900, §865-§882 |
| I9 | **Per-AP environment overrides** (`show ap-env` outputs): each becomes a device-level override in AOS 10. Operator should plan which to keep and which to consolidate into device profiles. | **INFO** | VSG §735-§739 |
| I10 | **AP discovery method**: IAPs use Unified AP discovery (DHCP option 43/60, ADP multicast, ADP broadcast, DNS aruba-master, IAP VC discovery, AirWave discovery, Activate, SetMeUp). AOS 10 prefers TCP 443 to Central first; falls back to Unified discovery if not in Central / not licensed (per VSG §796-§807). Confirm Central reachability + license assignment before AP convert. | **REGRESSION** if license + reachability gap | VSG §796-§807 |

#### Per-target-mode rules (apply on top of source rules)

##### Target = Tunnel Mode (anchors: VSG §340-§357, §1102-§1110, §1213-§1227, §1930-§1953)

| # | Check | Severity | Anchor |
|---|---|---|---|
| T1 | **NAD source IP changes to Gateway management address**. ClearPass NAD list must include the AOS 10 Gateway management IP(s). If multiple gateways in cluster, all gateway management IPs. | **REGRESSION** if missing | VSG §1130-§1133, §376-§378 |
| T2 | **AP switch ports in access mode**, native VLAN = AP management VLAN. Trunk mode is also acceptable but native VLAN must equal access VLAN to handle AP management traffic correctly (per VSG §1936-§1938). | **REGRESSION** if currently trunked with broader allowed-VLAN list when only Tunnel mode is the target | VSG §342-§346, §1930-§1953 |
| T3 | **Tunneled-SSID data VLANs pruned from AP switch ports** — APs must NOT learn client MAC addresses via the wired interface. Example from VSG §1213-§1223: if SSID `CorpWiFi` places users on VLAN 10, VLAN 10 must NOT be allowed (native or tagged) on the AP-uplink switchport. | **REGRESSION** if not pruned | VSG §1213-§1223 |
| T4 | **VLAN 1 NOT used for tunneled-SSID clients** — AP uplink VLAN is VLAN 1 by default (cannot be changed currently per VSG §1224-§1227); using VLAN 1 for tunneled clients creates a learning loop. | **REGRESSION** if currently configured | VSG §1224-§1227 |
| T5 | **Gateway cluster sizing** for Tunnel Mode: confirm the AOS 10 gateway model + cluster mode (Auto Group / Auto Site / Manual) supports the planned client load | **INFO** | VSG §410-§411 |
| T6 | **Jumbo frame support** between APs and Gateway cluster — recommended for tunneled traffic encapsulation (best practice carryover from AOS 6 / AOS 8 per VSG §294-§295, §1244-§1245) | **DRIFT** if not enabled on the path | VSG §294-§295 |
| T7 | **Encrypt/Decrypt 802.11 frames** moves to AP (vs at controller in AOS 6/8 Tunnel) per VSG §471-§473, §1228-§1231. AP CPU load consideration. | **INFO** | VSG §471-§473 |

##### Target = Bridge Mode (anchors: VSG §486-§556, §891-§932, §1239-§1336, §1956-§2003)

| # | Check | Severity | Anchor |
|---|---|---|---|
| B1 | **NAD source IP changes to individual AP management address**. ClearPass NAD list must include the AP management subnet (e.g. 10.x.x.0/24) **or** each AP's individual IP. | **REGRESSION** if missing | VSG §1259-§1264, §501-§508, §912-§925 |
| B2 | **AP management subnet L2-adjacent across the roaming domain** (no L3 separation between APs participating in the same Bridge Mode roaming domain) | **REGRESSION** if currently routed | VSG §1247-§1248, §494-§495 |
| B3 | **Wireless user VLANs L2-adjacent across roaming domain** (AOS 10 eliminates L3 Mobility per VSG §897-§900; if you had L3 Mobility you must collapse user VLANs to L2 OR move to Tunnel Mode with a Gateway cluster) | **REGRESSION** if currently routed and L3 Mobility was load-bearing | VSG §897-§900 |
| B4 | **AP switch ports in trunk mode** with appropriate data VLANs (per VSG §1956-§1972 — trunk port with native VLAN for management + tagged VLANs for bridged traffic) | **REGRESSION** if access-mode-only | VSG §1956-§1972 |
| B5 | **East/west AP-to-AP traffic permitted** (Secure PAPI UDP 8211 between APs in roaming domain) | **REGRESSION** if blocked | VSG §902-§905, §1281-§1287 |
| B6 | **Roaming domain scaling within limits**: max 500 APs, 5,000 clients per Bridge Mode roaming domain (current at VSG publication) | **DRIFT** if exceeded | VSG §544-§548, §865-§867 |
| B7 | **AP management subnet sizing**: max `/20` (currently tested + supported per VSG §544) | **DRIFT** if exceeded | VSG §544 |
| B8 | **User VLAN sizing**: subnet should be no greater than `/20`; greater scale → switch to Tunnel Mode with Gateway cluster | **DRIFT** if exceeded | VSG §545-§546 |
| B9 | **NAT / DHCP services** for any historically VC-managed WLANs must be relocated upstream (L3 switch / firewall / router / Aruba Gateway) — APs do not provide NAT/DHCP in AOS 10 Bridge Mode | **REGRESSION** if VC-managed WLANs exist and upstream services aren't ready | VSG §854-§857, §907-§909 |
| B10 | **QoS prioritization** for AP management traffic recommended in dense Bridge Mode deployments | **DRIFT** if not configured | VSG §537-§538, §1287 |
| B11 | **Authentication latency** target < 500 ms RTT to Central from APs | **DRIFT** if WAN sites haven't been measured | VSG §919-§920 |

##### Target = Mixed Mode (anchors: VSG §347-§357, §556-§584, §1102-§1110, §1975-§2003)

| # | Check | Severity | Anchor |
|---|---|---|---|
| M1 | All Tunnel rules (T1-T7) AND all Bridge rules (B1-B11) apply per-SSID depending on which forwarding mode each SSID uses | various | VSG §1102-§1107 |
| M2 | **VLAN segmentation strict**: bridged + tunneled clients **cannot** share the same VLAN (VSG §1107). Each SSID gets a dedicated VLAN. | **REGRESSION** if VLAN reuse detected | VSG §1107 |
| M3 | **AP switch port = trunk** with native VLAN for AP management + tagged VLANs for bridged traffic + tunneled-SSID VLANs **pruned** (per VSG §1975-§1993) | **REGRESSION** if VLAN handling not exact | VSG §1975-§1993 |
| M4 | **NAD registration per mode**: Tunnel Mode SSIDs require gateway(s) as RADIUS NAD; Bridge Mode SSIDs require all APs as RADIUS NAD (per VSG §576-§580) | **REGRESSION** if either set is missing | VSG §576-§580 |
| M5 | **AP management VLAN as native (untagged)** on AP switch ports — best practice per VSG §575 | **DRIFT** if not set | VSG §575 |

### Stage 4 — Central-side API checks (no operator paste needed)

Run these in parallel with the parse stage. They use only Central / ClearPass / GreenLake tools — no operator data needed. Each maps to specific MCP tools in the catalog.

#### AOS8 live-mode sub-path — Central enrichment (ENRICH-01..04, used when Stage -1 announced "AOS8 API mode")

When AOS8 live mode is active, the four Central enrichment checks (AP count gap, per-model AOS10 firmware recommendations, SSID conflicts, role/VLAN conflicts) are evaluated using AOS8 Stage 1 batch data already in context plus a small set of Central tool calls — no operator paste, no re-fetching of AOS8 batches. After this sub-path, continue with the A1–A13 Central API checks below; A4 / A7 / A8 / A9 are superseded by this sub-path's findings when live mode is active.

Each finding below uses the format **Severity — Description. (source: `tool_call(args)`, Batch N where applicable)**.

##### ENRICH-01 — AP count gap (INFO)

From the Batch 2 `aos8_get_ap_database()` response already in context, count total APs (call this `X`). Then call `central_get_aps()` with no filter and count the response (call this `Y`). Compute `Z = X - Y` (Z may be negative if Central reports more — surface that as-is). Emit one finding:

- **INFO** — Source AP count: `X`. Central onboarded: `Y`. Gap: `Z` not yet onboarded. (source: `aos8_get_ap_database()` Batch 2 + `central_get_aps()`)

*If `central_get_aps()` fails:* AP count gap (ENRICH-01) cannot complete from live data. Fall back to A4 in the table below.
*If Batch 2 was unavailable:* AOS8 AP count is unknown — operator paste of `show ap database long` required for ENRICH-01.

##### ENRICH-02 — Per-model AOS10 firmware recommendation (INFO)

Make **one call**, fleet-wide, no filter: `central_recommend_firmware()`. Central returns a fleet-wide recommendation list already grouped by device model — do NOT iterate per model. Extract the distinct AP `model` values from the Batch 2 `aos8_get_ap_database()` response, then for each distinct model walk the `central_recommend_firmware()` response and pull the recommended AOS10 firmware version for that model. Emit a compact two-column markdown table inline:

| AP Model | Recommended AOS10 Firmware |
|----------|----------------------------|
| `<model>` | `<version-from-central>` |
| `<model>` | `<version-from-central>` |

(source: distinct models from `aos8_get_ap_database()` Batch 2; recommendations from `central_recommend_firmware()`)

If Central's recommendation list omits a model present in the AOS8 fleet, emit one row per missing model with the value `no recommendation returned — verify with Aruba support`. Restrict the table to AP models only — controller firmware is owned by CUTOVER-02 in Stage 5, not by this rule.

*If `central_recommend_firmware()` fails:* per-model firmware recommendation (ENRICH-02) cannot complete. Fall back to A13 in the table below.
*If Batch 2 was unavailable:* distinct AP models are unknown — operator paste of `show ap database long` required for ENRICH-02.

##### ENRICH-03 — SSID conflict detection (REGRESSION, one finding per conflict)

From the Batch 4 `aos8_get_bss_table()` response already in context, extract the distinct AOS8 SSID names. Call `central_get_wlan_profiles()` with no `ssid` argument to retrieve the full Central WLAN profile list. For every AOS8 SSID name that already appears as a profile in the Central response, emit ONE finding (do not collapse multiple conflicts into a single bullet):

- **REGRESSION** — SSID `"<ssid_name>"` already exists in Central (profile present in `central_get_wlan_profiles()` response). A conflicting SSID name in Central blocks a clean migration. (source: `aos8_get_bss_table()` Batch 4 + `central_get_wlan_profiles()`)

If no AOS8 SSID names match any Central WLAN profile, emit a single INFO bullet: `INFO — No SSID conflicts detected against existing Central WLAN profiles. (source: aos8_get_bss_table() Batch 4 + central_get_wlan_profiles())`.

*If `central_get_wlan_profiles()` fails:* SSID conflict check (ENRICH-03) cannot complete. Fall back to A7 in the table below.
*If Batch 4 was unavailable:* AOS8 SSID list is unknown — operator paste of `show ap essid` required for ENRICH-03.

##### ENRICH-04 — Role and VLAN conflict detection (REGRESSION, one finding per conflict)

From the Batch 1 `aos8_get_effective_config()` response already in context, extract:
- distinct user-role names (from `user_role` / `aaa.user_role` objects)
- distinct named VLAN IDs (from `vlan` / `interface vlan` objects)

Call `central_get_roles()` with no `name` argument and `central_get_named_vlans()` with no `name` argument to retrieve the full Central role list and VLAN list. For every AOS8 role name that already appears in the Central role response, emit ONE finding:

- **REGRESSION** — Role `"<role_name>"` already exists in Central. A conflicting role name in Central blocks a clean migration. (source: `aos8_get_effective_config()` Batch 1 + `central_get_roles()`)

For every AOS8 VLAN ID that already appears as a named VLAN in the Central response, emit ONE finding:

- **REGRESSION** — Named VLAN ID `<vlan_id>` already mapped in Central (existing name: `"<central-vlan-name>"`). A conflicting VLAN ID in Central blocks a clean migration. (source: `aos8_get_effective_config()` Batch 1 + `central_get_named_vlans()`)

If no role names or VLAN IDs collide, emit a single INFO bullet: `INFO — No role or VLAN conflicts detected against existing Central roles / named VLANs. (source: aos8_get_effective_config() Batch 1 + central_get_roles() + central_get_named_vlans())`.

*If `central_get_roles()` fails:* role conflict check cannot complete. Fall back to A8 in the table below.
*If `central_get_named_vlans()` fails:* VLAN conflict check cannot complete. Fall back to A9 in the table below.
*If Batch 1 was unavailable:* AOS8 role names / VLAN IDs are unknown — operator paste of `show configuration effective detail` required for ENRICH-04.

After this sub-path, continue with the A1–A13 table below for any checks not superseded by ENRICH-01..04.

| # | Check | Tool | Severity if failing |
|---|---|---|---|
| A1 | Central reachability | `health(platform="central")` | **REGRESSION** |
| A2 | GreenLake workspace + AOS 10 / Central subscriptions | `greenlake_get_workspace()` + `greenlake_get_subscriptions()` | **REGRESSION** if missing AOS 10 / Central subscriptions |
| A3 | Central scope tree present (Sites + Site Collections if multi-site) | `central_get_scope_tree(view="committed")` | **DRIFT** if minimal — operator can pre-stage during preparation |
| A4 | APs already onboarded to Central (compare to operator's `show ap database long` count) | `central_get_aps()` | **INFO** — gap = source AP count − Central onboarded count |
| A5 | ClearPass NAD list includes the planned source-IP delta (per chosen target mode) | `clearpass_get_network_devices()` | **REGRESSION** if missing the new IPs |
| A6 | ClearPass server-cert NOT default (replace before production cutover) | `clearpass_get_server_certificates()` | **DRIFT** if default cert |
| A7 | Existing Central WLAN profiles match planned new SSID set (warns if Central already has conflicting profiles) | `central_get_wlan_profiles()` | **INFO** |
| A8 | Existing Central roles / policies — flag if migration would conflict with existing role names | `central_get_roles()` | **INFO** |
| A9 | Existing Central named VLANs — surface for operator's reuse-or-create planning | `central_get_named_vlans()` | **INFO** |
| A10 | Existing Central RADIUS server groups — flag for reuse | `central_get_server_groups()` | **INFO** |
| A11 | **RULES-03 cross-check** — Compare ClearPass local-user count against the AOS8 local-user count already collected in Stage 1 Batch 3 via `aos8_show_command(command='show local-user db')`. If both counts are non-zero, emit: **DRIFT** — AOS8 local users: `<X>`. ClearPass local users: `<Y>`. Dual-source-of-truth — consolidate to a single auth backend (AOS 10 has no Internal Auth Server per VSG §1134-§1136). (source: `aos8_show_command(command='show local-user db')` Batch 3 + `clearpass_get_local_users()`). If AOS8 Batch 3 was unavailable in this session, note "AOS8 count unknown — paste of `show local-user db` required for full cross-check" alongside the ClearPass count. | `clearpass_get_local_users()` | **DRIFT** if both non-zero |
| A12 | GreenLake device inventory shows the controllers / APs from the source platform (proves they're licensed and discoverable) | `greenlake_get_devices()` | **INFO** |
| A13 | Central firmware recommendation engine — what does Central recommend for the AP models in the inventory? | `central_recommend_firmware()` | **INFO** — guides target firmware |

### Stage 5 — Cutover sequencing + rollback validation

The VSG provides a single-site cutover sequence (VSG §2352-§2576). The audit walks through the operator's plan and validates each phase has prerequisites met. Map operator's cutover plan against:

#### AOS8 live-mode sub-path — cutover prerequisites (CUTOVER-01..03, used when Stage -1 announced "AOS8 API mode")

When AOS8 live mode is active, three cutover prerequisites — cluster L2-connected health, controller firmware version floor, and pre-cutover AP-count baseline — are evaluated before the operator walks through the Phase 0–8 cutover sequence below. Two checks reuse Stage 1 batch data already in context (no re-fetch); the firmware floor check makes one **fresh** `aos8_show_command(command='show version')` call because controller firmware version is not reliably surfaced by `show inventory` (Batch 3).

Each finding below uses the format **Severity — Description. (source: `tool_call(args)`, Batch N where applicable) (VSG §anchor when applicable)**.

##### CUTOVER-01 — Live cluster health (REGRESSION on anything other than L2-connected)

From the Batch 3 `aos8_get_cluster_state()` response already in context, inspect the cluster state field. If the state is anything other than `L2-connected`, emit:

- **REGRESSION** — Cluster not L2-connected: `<state>`. Resolve before single-controller upgrade. (source: `aos8_get_cluster_state()`, Batch 3)

If the state is `L2-connected`, emit a single INFO confirmation: `INFO — Cluster L2-connected (CUTOVER-01 PASS). (source: aos8_get_cluster_state(), Batch 3)`.

*If Batch 3 was unavailable:* cluster health (CUTOVER-01) cannot be evaluated from live data. Mark as **inconclusive — paste required** and consult any pasted `show lc-cluster group-membership` output.

##### CUTOVER-02 — Controller firmware floor (REGRESSION below 8.10.0.12 / 8.12.0.1, VSG §1643-§1649)

Make a **fresh** call to `aos8_show_command(command='show version')` here in Stage 5 — do NOT pull firmware from Batch 3 / `show inventory`, which does not reliably include the running OS firmware string. Parse the controller firmware version from the response. Compare against the prerequisite floor: the running version must be at least `8.10.0.12` on the 8.10 train OR at least `8.12.0.1` on the 8.12 train. If the running firmware is below both floors, emit:

- **REGRESSION** — Controller firmware `<running-version>` is below the 8.10.0.12 / 8.12.0.1 prerequisite. Upgrade the controller to a supported floor before AOS 10 migration. (source: `aos8_show_command(command='show version')`) (VSG §1643-§1649)

If the running firmware meets or exceeds the floor, emit a single INFO confirmation: `INFO — Controller firmware <running-version> meets the 8.10.0.12 / 8.12.0.1 prerequisite (CUTOVER-02 PASS). (source: aos8_show_command(command='show version')) (VSG §1643-§1649)`.

*If `aos8_show_command(command='show version')` fails:* firmware floor (CUTOVER-02) cannot be evaluated. Mark as **inconclusive — paste required** and consult any pasted `show version` output.

##### CUTOVER-03 — Pre-cutover AP-count baseline (INFO)

From the Batch 2 `aos8_get_ap_database()` response already in context, count total APs (call this `X`). Emit:

- **INFO** — Pre-cutover AP baseline: `X` APs. (source: `aos8_get_ap_database()`, Batch 2) Use this count for post-cutover diff.

*If Batch 2 was unavailable:* AP-count baseline (CUTOVER-03) cannot be captured from live data. Operator paste of `show ap database long` required for the baseline.

After this sub-path, continue with the Phase 0–8 cutover table below — those steps apply regardless of source path.

| Phase | What VSG specifies | Audit check |
|---|---|---|
| Phase 0 — Prerequisites | All upstream items: Central reachable, subscriptions, NAD list updated, switchports configured, firmware on controllers at min version, backup taken | All REGRESSION findings from stages 3-4 must be resolved. |
| Phase 1 — Verify cluster health (AOS 8 only) | `show lc-cluster group-membership` shows L2-connected; cluster operating as expected | Operator confirms via paste of pre-cutover output. |
| Phase 2 — Move APs to one controller | `apmove all target-v4 <peer-ctrl-IP>` on the to-be-upgraded controller (AOS 8) | INFO — operator action item. |
| Phase 3 — Upgrade first controller | Download AOS 10 from HPE Networking Support Portal; backup config; install via Maintenance > Software Management > Upgrade; reboot; verify ArubaOS 10.x on console | Operator follows VSG §2415-§2473. Audit confirms backup procedure documented. |
| Phase 4 — Test AP convert | One AP at a time: `ap convert add ap-name <ap-name>`, `ap convert pre-validate specific-aps`, verify "Pre Validate Success", then `ap convert active specific-aps server http common.cloud.hpe.com path ccssvc/ccs-system-firmware-registry/IAP <image-name>` | INFO — operator action items per VSG §2479-§2557. Audit reminds operator the AP appears as IAP in LLDP after convert. |
| Phase 5 — Upgrade remaining APs | `ap convert active all-aps` or per-group | INFO — operator action items. |
| Phase 6 — Upgrade second controller | After all APs are off it, repeat Phase 3 steps | INFO. |
| Phase 7 — Site validation | Compare post-cutover state to discovery baseline (client counts per SSID, AP counts per SSID, RF baseline) | Operator runs the audit again post-cutover for diff. |
| Phase 8 — Rollback contingency | Per VSG §2590-§2591, rollback commands are documented in the AOS 10 *Revert to AOS 8 Firmware Version* section. Operator must have rollback steps documented + tested. | DRIFT if no rollback plan. |

### Stage 6 — Combined readiness report

Aggregate findings from all stages into one verdict + structured report (see *Output formatting* below).

## Decision matrix

| Condition | Action |
|---|---|
| Operator hasn't picked source platform / target mode / scope / cluster type / HA mode | STOP. Don't proceed without all stage-0 answers. |
| Operator hasn't pasted the data bundle | Output **PARTIAL** verdict — Central-side checks complete, source-side blocked. List exactly what's needed. |
| Source = `iap` AND target mode ≠ `bridge` | **REGRESSION** — IAP migrates to Bridge Mode per VSG §672-§676. Reject the combination; operator must plan a Tunnel Mode migration as a separate gateway-cluster deployment. |
| AOS 8 controller firmware below `8.10.0.12` / `8.12.0.1` | **REGRESSION** — must upgrade controllers to the prerequisite version before AOS 10 swap (VSG §1643). |
| Static AP IP addressing detected | **REGRESSION** — AOS 10 requires DHCP for AP IP (VSG §1232, §475). |
| AAA FastConnect / Internal Auth Server in use | **REGRESSION** — not supported in AOS 10. |
| AP system profile uses individual controller IP for LMS (not VRRP virtual IP) | **REGRESSION** — APs will strand on first controller upgrade (VSG §1654-§1657). |
| Tunnel target mode + tunneled-SSID VLAN found on AP switch ports | **REGRESSION** — must prune (VSG §1213-§1223). |
| Tunnel target mode + VLAN 1 used for tunneled SSID clients | **REGRESSION** — AP uplink default VLAN is VLAN 1 (VSG §1224-§1227). |
| Bridge target mode + AP management subnet routed (not L2-adjacent) | **REGRESSION** — must collapse before migration (VSG §1247). |
| Bridge target mode + roaming domain > 500 APs / 5,000 clients | **DRIFT** — exceeds tested scaling; consider segmenting or moving to Tunnel Mode. |
| Bridge target mode + VC-managed WLANs without upstream NAT/DHCP plan | **REGRESSION** — APs don't provide NAT/DHCP in AOS 10 (VSG §907-§909). |
| Bridge target mode + Secure PAPI (UDP 8211) blocked between APs | **REGRESSION** — required for AOS 10 Bridge Mode (VSG §902-§905). |
| Mixed target mode + bridged and tunneled clients sharing a VLAN | **REGRESSION** — different VLANs required (VSG §1107). |
| ClearPass NAD list missing the new source IPs (Tunnel: gateway IPs; Bridge: AP IPs/subnet) | **REGRESSION** — auth will fail at cutover. |
| AOS 6 source + AP Override in use | **DRIFT** — plan a device-level-override mapping. |
| ARM / Dot11a/g / Regulatory Domain profiles in use | **DRIFT** — these are AirMatch-replaced. Document values for post-cutover comparison. |
| ClientMatch tunables relied on (Band Steering / Sticky / Load Balancing) | **DRIFT** — not adjustable in AOS 10; settings are fixed at Central WLAN Control & Services. |
| Cluster (AOS 8) currently not L2-connected at audit time | **REGRESSION** — `show lc-cluster group-membership` must report healthy before single-controller upgrade. |
| Default ClearPass server cert in use | **DRIFT** — replace before production cutover. |
| Internet block on source-platform management LAN AND not yet permitted to Central FQDNs | **REGRESSION** — TCP 443 to Central required. |
| L3 Mobility load-bearing in source design AND target = Bridge | **REGRESSION** — AOS 10 eliminates L3 Mobility. Either collapse to L2 roaming domain or pick Tunnel target mode. |
| WAN-served sites without Central RTT measurement | **DRIFT** — confirm < 500 ms target. |
| Backup procedure for source-platform configs not documented | **REGRESSION** — required pre-cutover step per VSG §2435. |
| Rollback plan not documented | **DRIFT** — VSG §2590-§2591 references rollback section in AOS 10 docs. |
| All REGRESSIONs resolved + DRIFTs noted | **GO**. |
| Any REGRESSION present | **BLOCKED**. Lead the report with the must-fix list. |
| Audit incomplete (operator hasn't pasted the bundle yet) | **PARTIAL** — output what's been validated so far + the action list. |

## Output formatting

Use the EXACT structure below. Every section heading must be present even if empty. Lead with the verdict, then REGRESSION → DRIFT → INFO. Include a suggested AOS 10 hierarchy mapping table and a phased cutover plan.

```
## AOS migration readiness — <source: aos6/aos8/iap> → AOS 10 <target: tunnel/bridge/mixed>
**Captured:** <ISO timestamp>
**Migration scope:** <single-site PoC | multi-site | fleet-wide>
**Cluster type (AOS 8):** <L2 / L3 / LMS / N/A>
**Target HA mode (AOS 10):** <Auto Group | Auto Site | Manual>
**L3 Mobility in source design:** <yes / no>
**Verdict:** GO / BLOCKED / PARTIAL

### Source-platform inventory (parsed from operator paste)
- Mobility Conductor / VC firmware: <version>
- Mobility Controller(s) / cluster member count: <N>
- AP count: <N> (models: <table>)
- AP IP addressing: <DHCP / static / mixed>
- Active SSIDs: <list with mode + VLAN>
- Active client baseline: <N total, breakdown per SSID>
- Local users (`show local-user db`): <count> — must migrate to ClearPass / Cloud Auth
- AP groups: <count + names>
- Configuration nodes: <count> (suggested AOS 10 mapping below)
- Cluster L2/L3 status (AOS 8): <healthy / unhealthy>
- AP system profile LMS IP: <VRRP VIP / individual controller IP>
- AP Override stanzas (AOS 6): <count if applicable>
- AirWave in path: <yes / no>

### Target-side state (Central API)
- Central reachable: ok / degraded
- GreenLake workspace_id: <value>
- AOS 10 / Central subscriptions: present / missing (subscription details)
- Central scope tree: <site count> sites, <collection count> collections, <device-group count> device groups
- APs already onboarded to Central: <N> (vs <M> in source — gap = <M-N>)
- ClearPass NAD list source-IP coverage: <complete | missing X.Y.Z entries>
- ClearPass server cert: default / replaced
- Central existing WLAN profiles that conflict with source SSIDs: <list>
- Central existing roles that conflict: <list>
- Central named VLANs available for reuse: <list>

### Suggested AOS 10 hierarchy mapping
| Source AOS node / IAP cluster | Suggested AOS 10 placement | Notes |
|---|---|---|
| <Mobility Conductor /md> | (root, not represented in AOS 10) | n/a |
| <md/<region>> | Site Collection: <name> | grouping |
| <md/<region>/<site>> | Site: <name> | one Site per discrete physical location |
| <md/<region>/<site>/<ap-group>> | Device Group: <name> | per-function device grouping |
| <IAP cluster> | Site: <name> + Device Group: <name> | IAP cluster collapses to one Site (Bridge Mode) |
| ... | ... | ... |

### REGRESSION findings (must fix before migration)
- **AOS 8 controller firmware below requirement**: <controllers + their version>. Required: 8.10.0.12 or 8.12.0.1+. (VSG §1643)
- **Static AP IP detected**: <list>. Convert to DHCP. (VSG §1232)
- **AAA FastConnect (EAP-Offload) in use**: <auth profiles using it>. Plan ClearPass-only termination. (VSG §1137)
- **Internal Auth Server in use**: <user count>. Migrate to ClearPass / Cloud Auth. (VSG §1134)
- **AP system profile uses individual controller IP for LMS**: APs will strand on first controller upgrade. Switch to VRRP VIP. (VSG §1654-§1657)
- **TCP 443 to Central blocked from <subnet>**: required for AOS 10 management. (VSG §312-§319)
- **Tunneled-SSID VLAN <X> present on AP switch port for SSID `<name>`**: must prune. (VSG §1213-§1223) [Tunnel target only]
- **VLAN 1 used for tunneled-SSID clients**: AP uplink default; choose another VLAN. (VSG §1224) [Tunnel target only]
- **AP management subnet routed (not L2-adjacent)**: required L2 for Bridge / IAP target. (VSG §1247)
- **Wireless user VLANs routed (L3-separated)** AND L3 Mobility was load-bearing: AOS 10 eliminates L3 Mobility. (VSG §897-§900) [Bridge target only]
- **Secure PAPI (UDP 8211) blocked between APs**: required for AOS 10 Bridge Mode roaming. (VSG §902-§905) [Bridge / Mixed target only]
- **ClearPass NAD list missing**: <list of expected new source IPs>. Will auth-fail at cutover. (VSG §1130)
- **AP cluster size or roaming-domain scaling exceeds tested limits**: <N> APs / <M> clients. (VSG §544-§548) [Bridge target only]
- **VC-managed (NAT'd) WLANs without upstream NAT/DHCP plan**: <list>. (VSG §907-§909) [IAP source]
- **Mixed Mode + bridged/tunneled VLAN reuse**: <list>. (VSG §1107) [Mixed target only]
- **Cluster not L2-connected at audit time** (AOS 8): `show lc-cluster group-membership` reports unhealthy. Cannot proceed safely.
- **Backup procedure not documented**: VSG §2435 requires backup before any upgrade.
- **Default ClearPass server cert in use**: replace before cutover.
- (or "No REGRESSION findings.")

### DRIFT findings (should address; not blocking)
- **AP Override in use** (AOS 6): map to device-level overrides. (VSG §422)
- **ARM / Dot11a/g / Regulatory Domain profiles in use**: AirMatch-replaced in AOS 10. Document values for post-cutover comparison. (VSG §1163)
- **ClientMatch tunables relied on**: not adjustable in AOS 10. (VSG §1167)
- **AirWave in path**: any monitoring tooling that depends on AirWave needs replacement. (VSG §312)
- **Central scope tree minimal** (no Site Collections): pre-create before migration day.
- **Roaming domain near scaling limit**: 480/500 APs or 4800/5000 clients.
- **Jumbo frames not enabled** between APs and Gateway cluster (Tunnel target).
- **No RTT measurement to Central** for WAN-served sites: confirm < 500 ms.
- **Local users present on both source platform AND ClearPass**: dual source-of-truth.
- **L3 Mobility load-bearing** AND target = Bridge: confirm Bridge Mode roaming domain consolidates.
- **Rollback plan not documented**: reference VSG §2590-§2591.
- (or "No DRIFT findings.")

### INFO findings (operational reference)
- **Cluster topology mapping** (AOS 8 → AOS 10): <existing L2/L3/LMS pattern> → recommended <Auto Group / Auto Site / Manual> per VSG §1161.
- **AP-to-switch wiring reference** (from `show ap lldp neighbors`): <table for cutover troubleshooting>.
- **Active client baseline**: <N> total, <M> per SSID — for post-cutover diff.
- **AP-per-SSID counts** (from `show ap essid`): <table>.
- **AP RF baseline** (from `show ap active`): channel, TX power, client count per AP — for post-cutover comparison.
- **Per-AP environment overrides** (IAP — `show ap-env`): <table> — these become device-level overrides in AOS 10.
- **APs already onboarded to Central**: <N> (gap = <M-N>).
- **Central-recommended firmware** for the AP models in inventory: <model → version table>.
- **Central existing roles / VLANs / WLAN profiles** that can be reused: <lists>.
- **Encrypt/Decrypt 802.11 frames** moves to AP in AOS 10: AP CPU load consideration. (VSG §471, §1228)

### Suggested cutover sequence (per VSG §2352-§2576)

| Phase | Action | Prerequisites |
|---|---|---|
| Phase 0 | Resolve every REGRESSION above | All audit blockers cleared |
| Phase 1 | Verify cluster L2-connected (AOS 8): `show lc-cluster group-membership` | Cluster healthy |
| Phase 2 | Move APs to one controller: `apmove all target-v4 <peer-IP>` on to-be-upgraded controller | Cluster healthy |
| Phase 3 | Upgrade first controller (download AOS 10, backup, install, reboot, verify) | Backup taken |
| Phase 4 | Test AP convert (one AP: `ap convert add` → `pre-validate` → `active`) | Verify "Pre Validate Success" |
| Phase 5 | Upgrade remaining APs (`ap convert active all-aps` or per-group) | Test AP successful + standard client testing complete |
| Phase 6 | Upgrade second controller (repeat Phase 3 steps) | All APs converted |
| Phase 7 | Site validation: compare to discovery baseline (clients/SSID, APs/SSID, RF) | Re-run this audit post-cutover for diff |
| Phase 8 | Rollback contingency available per VSG §2590-§2591 | Documented |

### Recommended next actions (ordered)
1. Resolve every REGRESSION above (in severity order).
2. Pre-stage Central scope tree to match the suggested hierarchy mapping.
3. Update ClearPass NAD list with the new source IPs (Tunnel: gateway IPs; Bridge: AP IPs/subnet; Mixed: both sets).
4. Run controller firmware upgrade to meet prerequisite (AOS 8 only).
5. Switch AP system profiles from individual controller IP to VRRP virtual IP (AOS 8 / AOS 6).
6. Configure AP switch ports per target mode (per VSG §1924-§2034).
7. Take configuration backup of every Mobility Controller / Conductor / VC.
8. Document rollback procedure (per VSG §2590-§2591).
9. Schedule maintenance window with all client/test devices ready.
10. Run this audit again post-fixes for clean GO verdict.

### PoC caveats (always include in the report)
- This audit was assembled from operator-pasted CLI output. Output completeness depends on what the operator pasted. For production migrations, use VALID8 (HPE channel-partner-only discovery + analysis tool) — see VSG §1563-§1575.
- PII / sanitization is operator-side. The skill does NOT auto-redact pasted content. Operators should redact MAC addresses, RADIUS shared secrets, customer-identifying SSID names, and local user data before pasting if those are sensitive.
- This output is not a substitute for a live engineer reviewing the migration plan. Engage HPE / partner SE for production migrations.
- Scaling values (500 APs / 5,000 clients per Bridge Mode roaming domain; /20 max subnet sizes) are current at VSG publication; confirm against latest AOS 10 documentation.
```

## Example queries that should trigger this skill

> "AOS 8 to AOS 10 migration readiness"
> "am I ready to migrate from AOS 8 to AOS 10?"
> "audit my AOS 6 environment for AOS 10 migration"
> "Instant AP to AOS 10 migration"
> "IAP to Bridge Mode migration audit"
> "migration readiness check"
> "validate my migration plan"
> "what do I need before AOS 10 cutover"
> "Central readiness for AOS 10"
> "Tunnel vs Bridge vs Mixed mode planning"
> "switchport configuration for AOS 10"
> "RADIUS NAD changes for AOS 10"
> "AirWave deprecation impact for AOS 10"
> "L3 Mobility migration to AOS 10"
