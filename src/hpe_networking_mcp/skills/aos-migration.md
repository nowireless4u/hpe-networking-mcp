---
name: aos-migration
title: AOS 8 → AOS 10 migration (PoC) — readiness + config translation plan
description: |
  PRIMARY TRIGGER — invoke this skill whenever the operator mentions
  AOS 8 → AOS 10 / Aruba Central migration in any phrasing. Do NOT
  improvise or skip the skill: it carries the live AOS 8 collection
  pattern, the per-object disposition matrix, and the cluster-aware
  inventory walk that free-form analysis cannot reproduce.

  AOS 6 and Instant AP (IAP) are out of scope. AOS 6 has a different
  migration path; IAP customers usually flow through classic Central.
  If the operator names either one, redirect — do not run this skill.

  Trigger phrases include but are not limited to: "AOS 8 to 10
  migration", "AOS 8 to AOS 10", "AOS 8 migration to Central",
  "migration readiness", "am I ready to upgrade to AOS 10", "audit my
  AOS 8 environment for migration", "validate my migration plan",
  "check Central readiness for AOS 10 cutover", "Tunnel vs Bridge vs
  Mixed mode planning", "switchport configuration for AOS 10", "RADIUS
  NAD changes for AOS 10", "translate AOS 8 config to AOS 10",
  "AOS 10 config mapping", "AOS 8 to Central object mapping",
  "build me an AOS 10 migration plan", "generate Central API call
  sequence for migration", "what objects do I need to recreate in
  Central".

  Anchored on Aruba Validated Solution Guide — Campus Migrate
  (AOS 8 sections, VSG §934-§1336). Two-act workflow: Act I =
  readiness (live AOS 8 API collection across the full /md hierarchy,
  feature-parity + orchestration prerequisite checks, GO / BLOCKED /
  PARTIAL / EMPTY-SOURCE verdict, cutover sequence). Act II = config
  translation plan (hierarchy mapping, per-object disposition matrix
  covering EVERY configured object regardless of whether it is in
  active use, Central API call sequence with dependencies, validation
  checklist). Act II only fires after a non-BLOCKED verdict and
  explicit operator confirmation.

  No operator interview. The skill detects AOS 8 reachability via
  health-probe, walks the entire /md hierarchy for inventory, and
  derives every other input (target SSID forwarding mode, cluster
  topology, AirWave presence, L3 Mobility usage) from the collected
  config. Operator drives changes interactively from the report.

  PoC — in-chat workflow for SE pre-engagement use; production
  migration cutovers follow the customer's standard change-management
  process and partner-tool guidance.
platforms: [central, aos8]
tags: [central, migration, aos8, aos10, readiness, audit, vsg, translation]
tools: [health, central_get_scope_tree, central_get_devices, central_get_aps, central_get_sites, central_get_site_name_id_mapping, central_recommend_firmware, central_get_config_assignments, central_get_server_groups, central_get_wlan_profiles, central_get_roles, central_get_role_acls, central_get_net_groups, central_get_net_services, central_get_named_vlans, central_get_aliases, central_manage_site, central_manage_site_collection, central_manage_device_group, central_manage_role, central_manage_role_acl, central_manage_net_group, central_manage_net_service, central_manage_wlan_profile, central_manage_config_assignment, clearpass_get_network_devices, clearpass_get_device_groups, clearpass_get_server_certificates, clearpass_get_local_users, greenlake_get_subscriptions, greenlake_get_workspace, greenlake_get_devices, aos8_get_md_hierarchy, aos8_get_effective_config, aos8_get_ap_database, aos8_get_cluster_state, aos8_show_command, aos8_get_clients, aos8_get_bss_table, aos8_get_active_aps, aos8_get_ap_wired_ports]
---

# AOS 8 → AOS 10 migration (PoC) — readiness + config translation plan

## Objective

Two-act workflow for **AOS 8 → AOS 10 / Aruba Central** migration. AOS 6 and Instant AP (IAP) are out of scope (different migration paths).

- **Act I — Readiness.** Walk the entire AOS 8 `/md` hierarchy via API, inventory every configured object (in active use or not), and emit a structured report with feature-parity findings, orchestration-prerequisite findings, and a cutover sequence. Verdict: **GO / BLOCKED / PARTIAL / EMPTY-SOURCE**.
- **Act II — Translation plan.** Conditional on a non-BLOCKED verdict and explicit operator confirmation: produce a per-object disposition matrix mapping each AOS 8 object (AAA / roles / ACLs / AP profiles / WLAN profiles / VAPs / 802.1X / captive portals) to its AOS 10 / Central equivalent, an ordered Central API call sequence, and a post-translation validation checklist. **Every configured object is in scope — including unused / orphaned ones — because what is or is not "in use" today is the customer's call, not the skill's.**

Anchored on **Aruba Campus Migrate VSG §934-§1336** (AOS 8 sections).

Act I uses live AOS 8 API collection (`aos8_*` tools). The skill walks the full `/md` hierarchy; configuration that lives at `/md/<region>` or `/md/<region>/<site>` does **not** always inherit up to `/md` root, so a root-only collection silently misses customer-specific config. The hierarchy walk is mandatory.

Cluster-offline tolerance: if the source clusters are unreachable at audit time (cluster members down for maintenance, lab environment with controllers off, etc.), live-state checks (`aos8_get_cluster_state`, `aos8_get_active_aps` per-MD) return degraded data. The skill **proceeds** — static config is still parsed normally; live-state checks are marked `inconclusive` rather than failing the audit.

Act II reuses everything Act I already collected — does NOT re-fetch effective-config or hierarchy — and produces a translation **plan**, not executed writes.

**Read-only.** The skill never calls `central_manage_*` write tools — execution is deferred to a future Phase 3 (issue #240). PoC — in-chat workflow intended for SE pre-engagement readiness + plan generation.

## Scope boundaries (what this skill is and is NOT)

The skill IS:

- A **full-hierarchy AOS 8 inventory** — walks every node in `/md` and collects every object type at every scope. No root-only assumptions.
- A **feature-parity finding generator** — flags AOS 8 features that AOS 10 doesn't support (Internal Auth Server, AAA FastConnect, L3 Mobility, AirWave dependency) so the operator knows what changes pre- or during cutover.
- A **migration-orchestration prerequisite checker** — controller firmware floor, Central reachability, GreenLake AP-license capacity, ClearPass NAD coverage for new AP subnets.
- A **per-object disposition mapper** — emits one row per configured object regardless of usage state. Maps each to its Central equivalent or flags `[Central API gap — manual UI]` for the three known gaps (AAA servers, AAA server-groups, AP system profiles).
- A **Central API call sequencer** — emits an ordered call plan with dependency annotations.
- A **cutover sequencer** — phased plan from VSG §2352-§2576.

The skill is NOT:

- A **filter for "in use" config.** The customer's running config is the source of truth. Whether something is currently assigned, referenced, or actively serving traffic is **metadata** (`usage_state` column on disposition rows), not a basis for excluding it from the migration plan. Orphaned AAA server groups, unassigned captive portal profiles, AP system profiles configured but not bound to an AP group — all map and get translated.
- A **legacy controller-plumbing validator.** Rules around LMS-IP, Backup-LMS-IP, AP Fast Failover that flag *"this internal AOS 8 controller-AP wiring is non-ideal"* do NOT fire as REGRESSION. AP-to-controller plumbing dissolves at migration — APs go to Central via TCP 443. These values still get **inventoried** so they can inform target HA mode recommendations, but they don't gate the verdict.
- An **operator interview.** No Stage-0 questions. The skill detects AOS 8 reachability (Stage -1), walks the hierarchy (Stage 1), and derives every input it needs from the collected config — target SSID forwarding mode is auto-recommended from the source pattern, cluster topology comes from `aos8_get_cluster_state`, AirWave presence comes from config grep, L3 Mobility usage comes from effective-config. The operator can override any auto-derived value when reviewing the report.
- A **migration executor.** Never calls `central_manage_*` write tools. Plan only; Phase 3 (issue #240) is the execution capability.
- A **rollback engine.** Rollback is captured as text in the cutover stage; not auto-generated as reversible API calls.
- A **gap-filler for missing Central write tools.** Three known gaps (AAA RADIUS/TACACS server, AAA server-group, AP system profile) get `[Central API gap — manual UI action required]` placeholders. No invented tool names.
- An **automatic VSG-anchor fabricator.** Object types the VSG doesn't cover (TACACS / LDAP server config, MAC-auth profile, captive portal, MAC randomization) get `vsg-anchor: none` and emit `OPERATOR-MAP` findings.
- An **AOS 6 / IAP migration tool.** If the operator names AOS 6 or IAP, redirect: *"AOS 6 has a different migration path; IAP customers usually flow through classic Central. Engage Aruba SE for those scenarios."*

If the operator asks for execution (running the plan against Central), point them at issue #240 (Phase 3 deferred) and stop.

## PoC scope + roadmap caveat

Live AOS 8 API collection means the skill receives effective-config and cluster state directly from the controller — no operator paste. The output may include customer-identifiable data (server IPs, MAC addresses, RADIUS shared secrets when explicitly returned by AOS 8, local user databases). PII tokenization (when enabled in the MCP server) covers most of this; some fields may slip through. Operators reviewing the report should be aware before sharing it externally.

The skill's job is to prove the in-chat workflow produces credible readiness findings + a translation plan. Sanitization layers and Phase-3 execution are tracked separately.

## Procedure — 10 stages across two acts

**Act I (Stages -1 through 6) — readiness audit.** Always runs. Ends with a verdict + combined report.

**Gate — operator confirmation.** After Stage 6, the AI emits the verdict report THEN literally prints the prompt: *"Verdict: <V>. Proceed to AOS 10 translation plan? (yes / no / edit-context)"* and stops. No Act II execution without operator `yes`.

- If verdict is **BLOCKED**, the gate does not appear. The report ends with *"Translation locked until REGRESSIONs are resolved. Re-run the audit after fixes."*
- If verdict is **PARTIAL**, the gate appears but warns which translation rows will be marked `inconclusive` (any object class where Stage 1 collection failed).
- If verdict is **GO**, the gate appears with no caveat.

**Act II (Stages 7 through 10) — translation plan.** Only fires on operator `yes` after a non-BLOCKED verdict. Reuses everything Act I already collected; no re-fetching, no second operator paste. Output is the **plan** (disposition matrix + ordered API call sequence + validation checklist), not executed `central_manage_*` writes.

If the operator answers `no`, end the session with the Act I report unchanged.
If the operator answers `edit-context` (e.g. "actually we're doing Bridge Mode not Tunnel"), update the corresponding Stage 0 / Stage 1 context fields, re-run Stage 3 + Stage 6 to re-verdict, and re-emit the gate prompt.

---

### Stage -1 — AOS 8 reachability gate (DETECT-01)

Call `health()` once and inspect `aos8.status`.

**If `aos8.status == "ok"`** — proceed to Stage 1 silently. No announcement, no operator interview.

**If `aos8.status == "degraded"`** — proceed to Stage 1 with cluster-offline tolerance enabled. Announce to the operator: *"AOS 8 reachable but reporting degraded — proceeding with config collection; live-state checks (active APs, cluster health, client baseline) will be marked inconclusive in the report."*

**If `aos8` is not configured (status missing) or the operator names AOS 6 / IAP** — stop. Emit:

```
AOS 8 not configured on this MCP server. This skill covers AOS 8 → AOS 10 migration only.
- AOS 6 has a different migration path; engage Aruba SE.
- Instant AP customers usually flow through classic Central; engage Aruba SE.
```

No further stages run.

### Stage 0 — (deleted)

There is no operator interview. Every input the skill needs is derived from collected config:

- **Target SSID forwarding mode** — auto-recommended by Stage 3 from the source pattern (tunneled VAPs → recommend Tunnel; bridge VAPs → recommend Bridge; mixed → recommend Mixed). Operator can override when reviewing the report.
- **Cluster topology** — pulled from `aos8_get_cluster_state` (Batch 3) plus cluster-profile config (Batch 1).
- **AirWave presence** — detected from effective-config (`mgmt-server`, `ams-ip`, AMP profile entries).
- **L3 Mobility usage** — detected from effective-config (`mobility l3-mobility` lines).
- **HA mode mapping** — derived from cluster topology.

### Stage 1 — Live AOS 8 inventory across the full /md hierarchy (COLLECT-01..04)

The skill is in code mode — collection runs as Python orchestration inside the `execute()` sandbox, NOT as a fixed sequence of skill-prescribed tool calls. The pattern below is the goal + data shape; the AI composes the actual calls.

#### COLLECT-01 — Hierarchy walk (mandatory; no `/md`-root-only shortcut)

The biggest historical bug in this skill was Stage 1 collecting only at `/md` root. AOS 8 inheritance does **not** always roll customer-specific config up to root — objects defined at `/md/<region>` or `/md/<region>/<site>` are invisible to a `/md`-only call. Always walk the full hierarchy.

```python
# Goal: produce config_by_scope = {scope: {object_type: response, ...}, ...}
# covering EVERY node in the /md tree.

# Object names are the AOS 8 REST schema names (NOT the CLI nouns).
# Live-verified against an AOS 8.12 Mobility Conductor — earlier versions
# of this list mixed CLI nouns with REST names and 13 of 20 silently
# returned {"ERROR": "Invalid Object"}. See issue #250 for the audit.
OBJECT_TYPES = [
    # WLAN / radio
    "ssid_prof", "virtual_ap", "ht_radio_prof", "reg_domain_prof",
    "arm_prof", "ap_sys_prof",
    # Authentication / AAA
    "aaa_prof", "rad_server", "tacacs_server", "ldap_server",
    "server_group_prof", "dot1x_auth_profile", "mac_auth_profile",
    "cp_auth_profile",
    # RBAC / ACLs
    "role", "acl_sess", "acl_eth", "acl_mac",
    # Cluster (paired — cluster_prof defines the profile, group_membership
    # binds devices to it)
    "cluster_prof", "group_membership",
]

hierarchy = await call_tool("aos8_get_md_hierarchy", {})
# Parse the tree; flatten to a list of every scope path:
#   ["/md", "/md/USE", "/md/USE/dallas-hq", "/md/USE/dallas-hq/floor-3", ...]
# Walk every node — root, regions, sites, ap-groups.
scopes = flatten_hierarchy_paths(hierarchy)

config_by_scope = {}
for scope in scopes:
    config_by_scope[scope] = {}
    for obj_type in OBJECT_TYPES:
        try:
            # entry_type="user" strips factory defaults and inherited
            # entries — for migration audits, defaults are noise. Reduces
            # response size by ~93% on this Conductor; the AI sees only
            # customer-defined config.
            response = await call_tool(
                "aos8_get_effective_config",
                {
                    "object_name": obj_type,
                    "config_path": scope,
                    "entry_type": "user",
                },
            )
            # Surface "Invalid Object" loudly — the AOS 8 REST schema may
            # drift between versions, and a silently-dropped object means
            # the migration plan is materially incomplete.
            inner = response.get("result") if isinstance(response, dict) and "result" in response else response
            if isinstance(inner, dict) and inner.get("ERROR") == "Invalid Object":
                config_by_scope[scope][obj_type] = {
                    "_collection_error": f"Invalid Object — REST schema may have renamed {obj_type!r} on this AOS build"
                }
            else:
                config_by_scope[scope][obj_type] = response
        except Exception as exc:
            config_by_scope[scope][obj_type] = {"_collection_error": str(exc)}
```

If the hierarchy walk yields zero customer-defined objects across all scopes (only AOS 8 system defaults), Stage 6 should emit verdict **EMPTY-SOURCE** rather than running rule checks against defaults.

If `aos8_get_md_hierarchy` fails or returns degraded data (clusters offline), fall back to `config_path="/md"` only and tag the entire collection result with `_partial: "hierarchy unreachable"`. Continue — don't block.

#### COLLECT-02 — AP inventory

```python
ap_database = await call_tool("aos8_get_ap_database", {})
```

If the database is empty (`AP Database: []`), don't gate the audit — record it and continue. An empty AP database means no APs are deployed yet; the migration plan still translates the configured ap-groups, ssid profiles, etc. (those translate regardless of whether APs are present).

#### COLLECT-03 — Cluster + running-config + local users + inventory + ports

```python
cluster_state = await call_tool("aos8_get_cluster_state", {})
running_config = await call_tool("aos8_show_command", {"command": "show running-config"})
local_users = await call_tool("aos8_show_command", {"command": "show local-user db"})
inventory = await call_tool("aos8_show_command", {"command": "show inventory"})
port_status = await call_tool("aos8_show_command", {"command": "show port status"})
trunks = await call_tool("aos8_show_command", {"command": "show trunk"})
```

`cluster_state` may return `{"_global_result": {"status": "1", ...}}` or empty list when no cluster is currently active. **Look for `lc_cluster_profile` rows in `config_by_scope` first** — a cluster *profile* defined at any scope (commonly `/md/<region>` or `/md/<region>/<site>`, NOT `/md` root) is the source of truth even when live cluster membership is empty (controllers offline). Live cluster state is supplementary.

#### COLLECT-04 — Client baseline + BSS table + active APs + per-AP wired ports

```python
clients = await call_tool("aos8_get_clients", {})
bss_table = await call_tool("aos8_get_bss_table", {})
active_aps = await call_tool("aos8_get_active_aps", {})

ap_names = [ap["ap_name"] for ap in ap_database.get("AP Database", [])]
ap_wired_ports = {}
for ap_name in ap_names:
    ap_wired_ports[ap_name] = await call_tool(
        "aos8_get_ap_wired_ports", {"ap_name": ap_name}
    )
```

For empty / offline environments, `clients`, `bss_table`, `active_aps` may be empty or report degraded. Mark live-state findings as `inconclusive` and continue.

#### After Stage 1

Compile and emit a brief inventory summary before Stage 2:

```
Hierarchy: <N> scopes walked (root + <N-1> sub-nodes)
Configured objects: <total count> across the hierarchy
APs in database: <N> (<active>: <N>, offline: <N>)
Cluster profiles: <names from config_by_scope>; live cluster: <state or "offline">
Local users: <N>
SSIDs: <N> ssid profiles, <N> active in BSS table
```

This summary is shown to the operator BEFORE Stage 2 runs so the operator can sanity-check that the hierarchy walk found what they expect. If the hierarchy walk missed something the operator knows is configured (e.g. customer says *"I have a cluster at /md/ACX but you didn't find it"*), they can intervene before rules fire on incomplete data.

### Stage 2 — Parse the live-collected inventory + auto-derive interview-equivalent inputs

Stage 1 collected raw API responses across the full hierarchy. Stage 2 normalizes those responses into a structured inventory and derives the inputs the old skill used to ask the operator for. **No paste parsing — Stage 1 is API-only.**

#### Normalize the inventory

For each scope in `config_by_scope`, group responses into:

```python
inventory = {
    "scopes": [...],                                # /md tree paths
    "ap_database": [...],                           # one entry per AP
    "active_aps": [...],                            # subset that are currently up (may be [] if offline)
    "clients": {...},                               # aggregate per-SSID counts
    "bss_table": [...],                             # one entry per ESSID broadcast
    "cluster_profiles": [...],                      # lc_cluster_profile rows (any scope)
    "live_cluster_state": {...},                    # aos8_get_cluster_state result
    "ap_groups": [...],                             # virtual_ap and ap_sys_prof
    "ssid_profiles": [...],
    "user_roles": [...],
    "session_acls": [...],
    "aaa_servers": {radius: [...], tacacs: [...], ldap: [...], internal_db: [...]},
    "aaa_server_groups": [...],
    "auth_profiles": {dot1x: [...], mac_auth: [...], captive_portal: [...]},
    "ap_system_profiles": [...],
    "rf_profiles": {arm: [...], reg_domain: [...], dot11a: [...], dot11g: [...]},
    "local_users": [...],
    "controller_inventory": {serials, macs, mgmt_ips},
    "controller_firmware_versions": [...],
    "ports_and_trunks": [...],
}
```

Each entry tagged with `source_scope` (which `/md/...` node defined it). The same logical object (e.g. an `ssid_prof` named "CorpNet") may appear at multiple scopes — preserve all instances; do not dedupe.

#### Auto-derive inputs (replaces deleted Stage 0 interview)

The old skill asked the operator 7 questions before proceeding. With the live inventory in hand, derive every one of them:

| Input | Derive from |
|---|---|
| **Source platform** | Always `aos8` — the skill's only supported source |
| **Target SSID forwarding mode** (`tunnel` / `bridge` / `mixed`) | Inspect `forward-mode` in `virtual_ap` rows. All `tunnel` → recommend Tunnel. All `bridge` → recommend Bridge. Mix → recommend Mixed. The recommendation appears in the report; operator can override at any time. |
| **AirWave in path** | Look in `running_config` for `mgmt-server` / `ams-ip` / `mobility-manager` lines. Present → emit DRIFT finding. |
| **Cluster topology** (L2 / L3 / standalone) | Inspect `lc_cluster_profile` rows. `controller-l2-only` flag → L2; cross-VLAN members → L3; no cluster profiles → standalone. **Default L2** when ambiguous (per project guidance: L3 is rare). |
| **L3 Mobility usage** | Look in `running_config` for `mobility l3-mobility` lines. |
| **HA mode mapping recommendation** | Cluster-topology-derived: L2 cluster → recommend Auto Group; L2 cluster + LMS pattern → recommend Auto Site; standalone → recommend Manual. |
| **AP-group → forwarding-mode mapping** | Per `virtual_ap` row's `forward-mode`, grouped by `ap-group` reference. Drives mixed-mode finding granularity. |

These derivations feed Stage 3 rules. The **report** explicitly shows the derived value and how it was derived (e.g. *"Target SSID forwarding mode: Tunnel (auto-recommended — 4 of 4 virtual_ap rows have forward-mode=tunnel)"*) so the operator can override with confidence.

#### Cluster-offline tolerance

When `aos8_get_cluster_state()` returns degraded data (clusters offline at audit time), prefer **`lc_cluster_profile` config rows** as the source of truth. Examples:

- Live cluster state empty + `lc_cluster_profile` rows present → cluster IS configured but currently offline; emit *"Cluster `<name>` is configured at scope `<source_scope>` but live cluster membership is empty (members offline at audit time). Static config is parsed normally."*
- Live cluster state empty + no cluster profiles found at any scope → no cluster configured. Note in inventory; no rules fire.

The audit MUST proceed in either case. Don't refuse to verdict.

### Stage 3 — Apply rules with applicability gates

Rules fall into three buckets:

1. **INVENTORY** — record what's there; never fires as REGRESSION/DRIFT. Includes legacy AOS 8 controller plumbing (LMS-IP, Backup-LMS-IP, AP Fast Failover, cluster topology) that dissolves at migration but informs Act II translation. Drives the report's inventory section, not its findings list.
2. **Feature-parity findings** — fire as REGRESSION/DRIFT/INFO when the source uses a feature AOS 10 doesn't support or handles differently. **Each rule has an applicability gate** — no rule fires on an empty source surface.
3. **Orchestration prerequisites** — fire as REGRESSION when the operator can't successfully run the cutover (Central unreachable, GreenLake under-licensed, controllers below firmware floor).

Each finding format: **Severity — Description (VSG §anchor when one exists; else literal `none`) (source: <inventory key>)**.

#### Applicability principle

Before a rule fires, evaluate its `requires` clause. If the gate isn't met, the rule emits **no finding**.

```python
applicability_gates = {
    "U2_static_ap_ip": ap_count > 0,
    "U5_NAD_list":     ap_count > 0 OR new_subnets_planned,
    "U6_FastConnect":  fastconnect_in_config,
    "U7_internal_auth_server": local_user_count > 0,
    "U10_backup":      controller_count > 0,
    "B/T/M_*":         target_mode_recommended in {bridge, tunnel, mixed},
    "AirWave_DRIFT":   airwave_in_config,
    "L3_mobility":     l3_mobility_in_config,
}
```

If **all** gates are false (zero APs, zero local users, zero AAA infrastructure, no clusters, no AirWave) → Stage 6 emits **EMPTY-SOURCE** verdict with no rule findings; Act II is still offered (translation plan for whatever defaults exist).

#### INVENTORY rows (record only — do NOT fire as findings)

These describe the source's controller-AP plumbing. Post-migration APs go to Central via TCP 443 — every value below either translates to AOS 10 Central HA mode or vanishes entirely. Each row appears in the inventory table; **none** fire as REGRESSION/DRIFT.

| Row | What | Why inventory-only |
|---|---|---|
| LMS-IP per `ap_sys_prof` | Record the value + which scope it was defined at + which `ap-group` it's bound to (or "unbound") | APs go to Central post-migration; LMS-IP is legacy controller plumbing |
| Backup-LMS-IP per `ap_sys_prof` | Same | Same |
| Cluster topology (L2 / L3 / standalone) per `lc_cluster_profile` | Cluster name, scope, member list, VRRP VIP(s) | Drives target HA mode auto-recommendation |
| AP Fast Failover config | Record presence/absence | No AOS 10 equivalent — APs reconnect to Central, not via Fast Failover |
| VRRP VIPs configured | Record values + member controllers | Inputs to disposition matrix; drives hierarchy translation |

#### Feature-parity findings (fire only when applicability gate is met)

| # | Rule | Gate | Severity if triggered | Anchor |
|---|---|---|---|---|
| F1 | **AAA FastConnect / EAP-Offload in use** — not supported in AOS 10 | `fastconnect_in_config` | REGRESSION | VSG §1137-§1141 |
| F2 | **Internal Authentication Server in use with local users** — no Internal Auth Server in AOS 10 | `local_user_count > 0` | REGRESSION; operator plans ClearPass / Cloud Auth migration | VSG §1134-§1136 |
| F3 | **L3 Mobility load-bearing in source design** — eliminated in AOS 10 | `l3_mobility_in_config AND target_mode_recommended in {bridge, mixed}` | REGRESSION (Bridge target) / DRIFT (Tunnel target) | VSG §897-§900 |
| F4 | **VC-managed (NAT'd) WLANs** depending on controller-side NAT/DHCP — AOS 10 Bridge APs don't provide NAT/DHCP | `vc_managed_wlans_present AND target_mode_recommended in {bridge, mixed}` | REGRESSION | VSG §854-§857 |
| F5 | **Static AP IPs detected** — AOS 10 requires DHCP | `any_ap_has_static_ip` | REGRESSION | VSG §1232-§1234 |
| F6 | **AirWave-dependent monitoring** in path (`mgmt-server` / `ams-ip` / AMP profile) — AirWave deprecated | `airwave_in_config` | DRIFT | VSG §312-§313 |
| F7 | **ARM / 802.11 radio / regulatory-domain profiles in active use** — replaced by RF Profiles in AOS 10 | `arm_or_radio_or_reg_domain_profile_present` | DRIFT — record values for post-cutover comparison | VSG §1163-§1166 |
| F8 | **ClientMatch tunables** (Band Steering / Sticky / Load Balancing) currently tuned away from defaults — fixed at WLAN Control & Services in Central | `clientmatch_tunables_modified` | DRIFT | VSG §1167-§1169 |
| F9 | **Captive Portal default certificate** in use | `captive_portal_uses_default_cert` | REGRESSION | VSG §364, §370 |
| F10 | **Internal management LAN blocks Internet** + cutover requires TCP 443 outbound to Central | `internet_blocked_from_mgmt_lan` | REGRESSION | VSG §315-§317 |

#### Orchestration prerequisite findings (fire regardless of source surface)

| # | Rule | Severity | Anchor |
|---|---|---|---|
| O1 | **Mobility Conductor firmware** at `8.10.0.12` / `8.12.0.1` or later (required for AOS 10 image push) | REGRESSION if below | VSG §1643-§1649 |
| O2 | **TCP 443 outbound from AP / controller management to Aruba Central reachable** | REGRESSION if blocked | VSG §312-§319 |
| O3 | **GreenLake workspace + AOS 10 / Central subscriptions present** | REGRESSION if missing | VSG §1619-§1620 |
| O4 | **Central scope tree pre-created** (Sites + Site Collections + Device Groups) | DRIFT if not pre-created | VSG §30-§34 |
| O5 | **Backup procedure documented** for source-platform configuration | DRIFT if not documented | VSG §2435 |
| O6 | **Rollback procedure documented** for each cutover stage | DRIFT if not documented | VSG §1624, §2590-§2591 |

#### Per-target-mode findings (fire only when target_mode_recommended matches)

##### When target_mode_recommended = Tunnel (VSG §340-§357, §1102-§1110, §1213-§1227, §1930-§1953)

Applicability gate: `target_mode_recommended == "tunnel" AND ap_count > 0`.

| # | Rule | Severity | Anchor |
|---|---|---|---|
| T1 | **NAD source IP changes to Gateway management address**. ClearPass NAD list must include the AOS 10 Gateway management IP(s). | REGRESSION if missing | VSG §1130-§1133 |
| T2 | **AP switch ports in access mode** (or trunk with native VLAN = AP management VLAN). | REGRESSION if currently misconfigured | VSG §342-§346, §1930-§1953 |
| T3 | **Tunneled-SSID data VLANs pruned from AP switch ports** | REGRESSION if not pruned | VSG §1213-§1223 |
| T4 | **VLAN 1 NOT used for tunneled-SSID clients** | REGRESSION if currently configured | VSG §1224-§1227 |
| T5 | **Gateway cluster sizing** | INFO | VSG §410-§411 |
| T6 | **Jumbo frames** between APs and Gateway cluster | DRIFT if not enabled | VSG §294-§295 |

##### When target_mode_recommended = Bridge (VSG §486-§556, §891-§932, §1239-§1336, §1956-§2003)

Applicability gate: `target_mode_recommended == "bridge" AND ap_count > 0`.

| # | Rule | Severity | Anchor |
|---|---|---|---|
| B1 | **NAD source IP changes to individual AP management address**. | REGRESSION if missing | VSG §1259-§1264 |
| B2 | **AP management subnet L2-adjacent across the roaming domain** | REGRESSION if currently routed | VSG §1247-§1248 |
| B4 | **AP switch ports in trunk mode** with appropriate data VLANs | REGRESSION if access-mode-only | VSG §1956-§1972 |
| B5 | **East/west AP-to-AP traffic permitted** (Secure PAPI UDP 8211) | REGRESSION if blocked | VSG §902-§905 |
| B6 | **Roaming domain scaling within limits**: max 500 APs, 5,000 clients | DRIFT if exceeded | VSG §544-§548 |
| B7 | **AP management subnet sizing**: max `/20` | DRIFT if exceeded | VSG §544 |
| B8 | **User VLAN sizing**: max `/20`; consider Tunnel Mode if exceeded | DRIFT if exceeded | VSG §545-§546 |
| B10 | **QoS prioritization** for AP management traffic | DRIFT if not configured | VSG §537-§538 |
| B11 | **Authentication latency** target < 500 ms RTT to Central from APs | DRIFT if WAN sites unmeasured | VSG §919-§920 |

##### When target_mode_recommended = Mixed (VSG §347-§357, §556-§584, §1102-§1110, §1975-§2003)

Applicability gate: `target_mode_recommended == "mixed" AND ap_count > 0`.

All Tunnel rules apply to tunneled-mode SSIDs; all Bridge rules apply to bridge-mode SSIDs. Plus:

| # | Rule | Severity | Anchor |
|---|---|---|---|
| M2 | **VLAN segmentation strict**: bridged + tunneled clients cannot share the same VLAN | REGRESSION if reused | VSG §1107 |
| M3 | **AP switch port = trunk** with native VLAN for AP management + tagged for bridged + pruned tunneled VLANs | REGRESSION if not exact | VSG §1975-§1993 |
| M4 | **NAD registration per mode**: gateways for tunnel SSIDs, APs for bridge SSIDs | REGRESSION if either set missing | VSG §576-§580 |
| M5 | **AP management VLAN as native (untagged)** on AP switch ports | DRIFT if not set | VSG §575 |

### Stage 4 — Central-side API checks (orchestration prerequisites only)

Stage 4 is **trimmed**. The previous version conflated three distinct concerns:

1. **Migration orchestration prerequisites** — Central reachable, GreenLake AP-license capacity covering the source AP count, NAD list extending to new AP subnets. KEPT.
2. **Translation enrichment** — what Central / ClearPass already has that the disposition matrix should flag for conflict. KEPT, scoped to translation (Stages 7-10), not Stage 6 verdict.
3. **General platform health** — ClearPass certificate validity, GreenLake subscription enumeration, Central WLAN profile inventory. **MOVED OUT** — these are infrastructure-readiness concerns that belong in `infrastructure-health-check` or a future `central-readiness-audit` skill, not in migration audit.

#### Stage 4a — Migration orchestration prerequisites

| # | Check | Tool | Applicability gate | Severity if failing |
|---|---|---|---|---|
| A1 | **Central reachability** | `health(platform="central")` | always | REGRESSION |
| A2 | **GreenLake AOS subscription capacity** ≥ source AP count | `greenlake_get_workspace()` + `greenlake_get_subscriptions()` | always | REGRESSION if AP count > active AP-license count |
| A3 | **AP onboarding gap** (source APs not yet in Central) | `central_get_aps()` + `aos8_get_ap_database()` | `ap_count > 0` | INFO — emit gap value as a single integer (no per-AP enumeration) |
| A4 | **NAD list coverage for new AP subnets** | `clearpass_get_network_devices()` | `ap_count > 0` AND `target_mode_recommended in {bridge, mixed}` AND `is_clearpass_used` | REGRESSION if missing |
| A5 | **NAD list coverage for cluster gateways/VRRP VIPs** | `clearpass_get_network_devices()` | `cluster_profile_present` AND `is_clearpass_used` | REGRESSION if any cluster VRRP VIP missing from NAD list |

`is_clearpass_used` = the source's `aaa_server_group` references at least one `rad_server` whose host matches a configured ClearPass instance OR the operator runs ClearPass per inventory. If false, A4 / A5 don't fire — the source uses non-ClearPass RADIUS or none at all.

#### Stage 4b — Translation enrichment (feeds Act II disposition matrix)

Findings in this section are NOT used to compute the Stage 6 verdict. They populate the disposition matrix in Stage 8 — when an AOS 8 object collides with a same-named Central object, the disposition row notes the collision and proposes a target name suffix or rename.

| # | Enrichment | Tool | Used by Stage 8 to |
|---|---|---|---|
| E1 | Central WLAN-profile name collision check | `central_get_wlan_profiles()` | Tag `wlan_ssid_profile` rows where the AOS 8 ESSID already exists as a Central WLAN profile. |
| E2 | Central role-name collision check | `central_get_roles()` | Tag `user_role` rows where the AOS 8 role name already exists in Central. |
| E3 | Central named-VLAN ID collision check | `central_get_named_vlans()` | Tag VLAN rows where the AOS 8 VLAN ID already maps in Central under a different name. |
| E4 | Central server-group collision check | `central_get_server_groups()` | Tag `aaa_server_group` rows where the same name already exists in Central. |
| E5 | Per-AP-model AOS 10 firmware recommendation | `central_recommend_firmware()` | Append a "Recommended AOS 10 firmware" column to the inventory's AP-model summary. INFO only — never gates the verdict. |

Each enrichment emits **at most one INFO bullet** in the Act I report ("Found N name collisions; see disposition matrix for per-row detail in Act II"). No per-collision bullets in Act I — they belong in Act II.

#### What's deliberately not in Stage 4 anymore

- **ClearPass server certificate validity** — out of scope. Cert health is a ClearPass operations concern, not a migration predictor.
- **GreenLake subscription enumeration** — A2 reduces to a single comparison (license capacity vs AP count). The previous skill enumerated 32 of 34 subscriptions one-by-one as theater; the only number that matters is `active_AP_license_count >= source_ap_count`.
- **Central RADIUS server-group inventory** — moved to E4 (translation enrichment), not a separate finding.
- **A11 dual-source-of-truth local-user cross-check** — folded into rule F2 (Internal Authentication Server in use). If F2 fires, the report mentions ClearPass as the recommended migration target; no separate Stage 4 entry.

### Stage 5 — Cutover sequencing + rollback validation

The VSG provides a single-site cutover sequence (VSG §2352-§2576). Reuse Stage 1 collected data — do NOT re-fetch except where called out below. Three cutover prerequisites first, then walk the Phase 0–8 sequence.

#### Cutover prerequisites

| # | Check | From | Severity |
|---|---|---|---|
| C-01 | **Live cluster health** — when `lc_cluster_profile` rows exist (cluster is configured), `aos8_get_cluster_state()` should report `L2-connected`. If degraded, the audit notes it but does NOT block — clusters can be brought to L2-connected before cutover. | `live_cluster_state` from Stage 1 COLLECT-03 | DRIFT if degraded; INFO if L2-connected; INFO with `cluster offline at audit time` note if `lc_cluster_profile` exists but live state empty |
| C-02 | **Mobility Conductor firmware floor** — running version on Conductor must be `8.10.0.12` / `8.12.0.1` or later (prerequisite for AOS 10 image push). One **fresh** call: `aos8_show_command(command='show version')` (cannot rely on `show inventory` — running firmware not reliably surfaced there). | fresh call in Stage 5 | REGRESSION if below |
| C-03 | **Pre-cutover AP-count baseline** — record `len(ap_database)` for post-cutover diff. | Stage 1 COLLECT-02 | INFO |

If `lc_cluster_profile` rows are absent (no cluster configured), C-01 doesn't fire and C-02 still runs. C-03 always runs.

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

This stage produces the Act I report. Once the report is emitted, fire the Act-I → Act-II gate (next).

---

## Act I → Act II gate

After emitting the Stage 6 readiness report, decide:

- **Verdict = BLOCKED** — emit the literal sentence: *"Translation locked until REGRESSIONs are resolved. Re-run the audit after fixes."* Stop. Do NOT print the proceed prompt; do NOT run Stages 7-10.
- **Verdict = GO** — emit the literal prompt: *"Verdict: GO. Proceed to AOS 10 translation plan? (yes / no / edit-context)"* and stop. Wait for the operator's reply.
- **Verdict = PARTIAL** — emit the literal prompt: *"Verdict: PARTIAL — <N> Stage-1 collection items were inconclusive. Translation rows for those object classes will be marked `inconclusive — paste required`. Proceed to AOS 10 translation plan? (yes / no / edit-context)"* and stop. Wait for the operator's reply.

On `yes` → proceed to Stage 7.
On `no` → end the session with the Act I report unchanged.
On `edit-context` → operator names which Stage 0 / Stage 1 field(s) to update, the AI updates the audit context, re-runs Stage 3 + Stage 6, re-emits the Act I report, and re-emits the gate prompt. (This is how the operator changes target mode mid-session, for example.)

Do NOT run Stages 7-10 silently or pre-emptively.

---

### Stage 7 — Hierarchy translation (TRANSLATE-01)

Promote the readiness-stage hierarchy mapping table (Stage 6 inventory section) into a translation stage with explicit rules. Reuse the Stage 1 COLLECT-01 effective-config or pasted `show configuration node-hierarchy` output already in context — do NOT re-fetch.

**Rules** (anchor: VSG §1529-§1535 *"Mapping AOS-8 Hierarchy to AOS-10 Configuration Model"* + §1834-§1835):

| Source node | AOS 10 placement | Disposition |
|---|---|---|
| `/md` (Mobility Conductor root) | (none — Central org root is implicit) | `drop` |
| `/md/<region>` | Site Collection | `direct-translate` |
| `/md/<region>/<site>` | Site | `direct-translate` |
| `/md/<region>/<site>/<ap-group>` | Device Group | `direct-translate` |

**Output:** the existing 3-column hierarchy table from the Stage 6 report, **extended to 5 columns**:

| Source AOS node | Source path | Disposition | Target type (AOS 10) | Target name (operator-named) | Notes |
|---|---|---|---|---|---|
| `<Mobility Conductor /md>` | `/md` | `drop` | (none) | n/a | Central org root is implicit |
| `<region>` | `/md/USE` | `direct-translate` | Site Collection | `USE` (or operator override) | grouping |
| `<site>` | `/md/USE/dallas-hq` | `direct-translate` | Site | `dallas-hq` | one Site per discrete physical location |
| `<ap-group>` | `/md/USE/dallas-hq/floor-3` | `direct-translate` | Device Group | `dallas-hq-floor-3` | per-function device grouping |

**Skip / inconclusive:** if Stage 1 paste-fallback was used and node hierarchy was not pasted, mark each row's disposition `inconclusive — paste required` and emit one INFO finding noting the gap.

**Findings produced:**

- For every proposed target name (Site Collection / Site / Device Group), check it against the Stage 4 Central scope-tree response. If a same-named node already exists at the same level: emit `DRIFT — proposed Site name '<X>' already exists in Central scope tree as <type>; rename or merge before translation.` (One finding per collision.)
- If the source `/md` tree exceeds the AOS 10 *"per-Site Collection limits"* (out of scope per VSG; operator may need to flatten), emit one INFO bullet flagging the operator decision.

---

### Stage 8 — Per-object translation matrix (TRANSLATE-02)

For **every AOS 8 object discovered in Stage 1's full hierarchy walk** (regardless of whether it is in active use, assigned, referenced, or orphaned), emit one row of the disposition matrix. **Reuse Stage 1 collected data already in context** — do NOT re-fetch.

**Critical principle (this is the rule, not a guideline):** the customer's running config is the source of truth. Whether something is "in use" today is metadata on the row (`usage_state` column), not a basis for excluding it from the migration plan. Orphaned AAA server groups, unassigned captive portal profiles, AP system profiles configured but not bound to any AP group — every one gets a row.

#### 8.1 — Disposition rules per object type

The VSG **does not** contain per-object translation tables for most object types. The deepest concrete rules live in two worked SSID examples (CorpNet 802.1X at VSG §2127-§2219, OpsNet WPA3-Personal at §2222-§2308) plus the gestural feature-comparison table for AOS 8 (§1121-§1175). Outside those anchors, dispositions for AAA / roles / ACLs / AP profiles are marked `operator-driven` with `vsg-anchor: none` — the skill does not fabricate VSG citations.

| Object type | VSG anchor | Disposition guidance |
|---|---|---|
| **AAA RADIUS server** (`rad_server`) | §1121-§1141 | `transform` — IP / port / shared-secret carry over; NAS-IP source must change per target mode (Tunnel = gateway IP; Bridge = AP subnet; Mixed = both). VSG describes the source-IP shift; field-mapping into Central is operator-driven. **Central API gap — no `central_manage_server` tool exists today.** Mark target tool as `[Central API gap — manual UI: Network Services → Servers]`. |
| **AAA TACACS server** (`tacacs_server`) | (none) | `operator-driven` — VSG has no TACACS translation rule. Emit `OPERATOR-MAP` finding. **Central API gap — no manage tool.** Target tool: `[Central API gap — manual UI]`. |
| **AAA LDAP server** (`ldap_server`) | (none) | `operator-driven` — VSG silent. **Central API gap.** |
| **AAA Internal Auth Server** (`internal_db_server`) | §1134-§1136 | `drop` — *"Local user authentication service is not supported."* If `local-userdb` has entries, emit `REGRESSION — <N> local users must migrate to ClearPass / Cloud Auth before cutover.` (Already covered by Act I rule F2; cross-link rather than re-emit.) |
| **AAA FastConnect / EAP-Offload** | §1137-§1141 | `drop` — *"Not supported."* If active, emit `REGRESSION — AAA FastConnect / EAP-Offload in use; plan ClearPass-only EAP termination.` (Cross-link to Act I rule F1.) |
| **AAA server-group** (`aaa server-group`) | §2076-§2092 (worked example) | `transform` — group name + ordered server list. **Central API gap — no `central_manage_server_group` tool.** Target tool: `[Central API gap — manual UI: Network Services → Server Groups]`. |
| **802.1X auth profile** (`aaa authentication dot1x`) | §1121-§1141 + §2159-§2208 (CorpNet 802.1X worked example) | `operator-driven` — folded into WLAN profile creation in Central; ESSID is in the WLAN SSID profile, allowed-bands and VLAN ID are in the VAP (collapsed into the WLAN profile in Central), key-management is in the SSID profile, primary/secondary RADIUS pointers are under authentication servers. No automatic field map; emit `OPERATOR-MAP`. Target tool: `central_manage_wlan_profile` (the auth profile is collapsed into it). |
| **MAC-auth profile** (`aaa authentication mac`) | (none) | `operator-driven` — VSG silent. Emit `OPERATOR-MAP`. Target tool: `central_manage_wlan_profile` (mac-auth opmodes are flags inside it). |
| **Captive portal profile** (`aaa authentication captive-portal`) | (none, passing mention only) | `operator-driven` — assigned through a role's `captive-portal` field on `central_manage_role`. Emit `OPERATOR-MAP`. Target tool: `central_manage_role` (captive-portal field). |
| **User role** (`user_role`) | §1173-§1176 (AOS 8 supported-features list) | `transform` — role name + VLAN + ACL + bandwidth-contract + qos + captive-portal + session-timeout map directly. Per-attribute mapping is operator-driven; VSG only confirms roles "are supported." Emit `OPERATOR-MAP` per role. Target tool: `central_manage_role`. |
| **Session ACL / role ACL** (`ip access-list session ...`) | (none — implied via role) | `transform` — split into Central primitives: `central_manage_net_group` (network-destination aliases referenced by ACL rules) + `central_manage_net_service` (port/protocol service aliases) + `central_manage_role_acl` (the ACL rule list itself). Per-rule mapping is operator-driven; emit `OPERATOR-MAP`. Target tools: `central_manage_net_group`, `central_manage_net_service`, `central_manage_role_acl`. |
| **AP system profile** (`ap system-profile`) | §1651-§1657 (LMS prerequisite), §412-§415 (regulatory domain replaced) | Mixed: LMS-IP `transform` (must be VRRP VIP, not individual controller IP — already enforced as Act I REGRESSION rule); regulatory-domain-profile `deprecated`; ARM / Dot11a / Dot11g profiles `deprecated` (replaced by RF Profiles in AOS 10); syslog targets `operator-driven` (mapped to Central UI). **Central API gap — no `central_manage_ap_system_profile` tool today.** Target tool: `[Central API gap — manual UI]`. |
| **WLAN SSID profile** (`wlan ssid-profile`) | §2127-§2219 (CorpNet 802.1X), §2222-§2308 (OpsNet WPA3-Personal) | `direct-translate` — ESSID, opmode, VLAN, forwarding-mode, key-management, RADIUS pointers map to the `central_manage_wlan_profile` payload schema. The two VSG worked examples are the gold-standard reference for field-by-field mapping; emit per-WLAN-profile rows that cite them. Target tool: `central_manage_wlan_profile`. |
| **VAP profile** (`wlan virtual-ap`) | §2169-§2192 (Allowed bands "in the VAP", VLAN ID "in the VAP") | `transform` — AOS 8 VAP fields collapse INTO the WLAN profile in AOS 10; VAP is not a standalone object. Mark as `transform → folded into WLAN profile`. Target tool: `central_manage_wlan_profile` (collapsed). |
| **MAC randomization handling** (per-SSID) | (none) | `operator-driven` — flag as a known AOS 10 behavioural difference. VSG does not address. Emit `OPERATOR-MAP`. |
| **ARM / Dot11a / Dot11g / Regulatory Domain profiles** | §1163-§1166 | `deprecated` — ARM is replaced by **RF Profiles** in AOS 10 / Central. AirMatch already exists in AOS 8 and continues in Central — it is not the AOS 10 ARM replacement. Already raised as DRIFT in Act I; emit one summary `drop` row per profile family in the matrix. |
| **ClientMatch tunables** | §416-§418, §1167-§1169 | `deprecated` — *"Settings cannot be tuned."* Already raised as DRIFT in Act I; emit one summary `drop` row in the matrix. |

#### 8.2 — Output: the disposition matrix

Emit a **single master table** with one row per legacy object discovered, **including unused / orphaned / unassigned ones**. Columns:

| Source name | Source type | Source scope | Usage state | Disposition | Target name | Target type | Central tool | VSG anchor | Notes |
|---|---|---|---|---|---|---|---|---|---|

- **Source name** — name as it appears in the source config (`corp-radius-1`, `corp-employee-role`, `corp-ssid-prof`).
- **Source type** — one of: `rad_server`, `tacacs_server`, `ldap_server`, `internal_db_server`, `aaa_server_group`, `dot1x_authentication_profile`, `mac_authentication_profile`, `captive_portal_auth_profile`, `user_role`, `ip_access_list`, `ap_sys_prof`, `wlan_ssid_profile`, `virtual_ap`, `arm_profile`, `dot11a_radio_prof`, `dot11g_radio_prof`, `reg_domain_profile`, `lc_cluster_profile`.
- **Source scope** — the `/md/...` node where the object is defined (e.g. `/md`, `/md/ACX`, `/md/ACX/dallas-hq/floor-3`). Captured during the Stage 1 hierarchy walk; **never assume an object lives at `/md` root**.
- **Usage state** — one of: `assigned-and-active` (referenced by an ap-group or other object that's currently bound to active devices), `assigned-but-inactive` (referenced but the binding scope has no active devices), `configured-but-unassigned` (defined but not referenced by any other object), `orphaned` (referenced only by objects that are themselves unused). **This is metadata only — never a basis for excluding the row from migration.** Customers regularly migrate unused config because *"unused right now"* is a different statement from *"won't be needed after migration."*
- **Disposition** — one of: `direct-translate` / `transform` / `drop` / `deprecated` / `operator-driven` / `inconclusive`.
- **Target name** — the AOS 10 / Central object name. For `direct-translate` / `transform` rows, default to source name (with `_<scope>` suffix when the same name appears at multiple scopes — operator can rename). For `drop` / `deprecated`, leave blank or `n/a`. For `operator-driven`, leave blank.
- **Target type** — Central object type: `Site Collection` / `Site` / `Device Group` / `WLAN profile` / `Role` / `Role ACL` / `Net group` / `Net service` / `Server` / `Server group` / `(none)` / `(folded into WLAN profile)`.
- **Central tool** — the `central_manage_*` tool that creates the object, OR the literal string `[Central API gap — manual UI: <area>]` for the three known gaps (servers, server-groups, AP system profiles).
- **VSG anchor** — `§####-§####` if a real anchor exists. Literal string `none` if no per-object VSG rule exists; do NOT fabricate.
- **Notes** — one short clause per row (e.g. *"NAS-IP source must change to gateway IP for Tunnel target"*, *"folded into WLAN profile per VSG §2169"*, *"manual UI required: Central API gap"*, *"orphaned in source — operator may choose to skip in target"*).

#### 8.3 — Findings produced

For each row in the matrix:

- `direct-translate` rows produce no separate finding (the matrix row IS the finding). Counted in the Act II summary as `<N> direct-translate`.
- `transform` rows produce no separate finding unless the transform requires operator decisions (NAS-IP source for AAA, role attribute mapping, ACL rule re-emission). When operator decisions exist, emit one `OPERATOR-MAP` finding per object.
- `drop` and `deprecated` rows produce no separate finding (already raised in Act I if applicable). Counted in the Act II summary as `<N> dropped`.
- `operator-driven` rows produce **one `OPERATOR-MAP` finding per row** so the operator can scan only the manual-mapping work items independently of the matrix.

`OPERATOR-MAP` finding format:

> `OPERATOR-MAP — <object_type> '<source_name>' has no automated translation in this skill. Map manually: <one-sentence operator guidance>. (VSG §anchor when applicable; otherwise none) (source: <Stage 1 batch reference>)`

Examples:

> `OPERATOR-MAP — User role 'corp-employee' requires per-attribute mapping. Set role's VLAN, ACL list, captive-portal, session-timeout in the Central role payload. (VSG §1173) (source: aos8_get_effective_config(object_name='user_role', config_path='/md'), Batch 1)`

> `OPERATOR-MAP — TACACS server 'tacacs-mgmt' has no automated translation rule. Configure manually in Central UI under Network Services → Servers. (VSG §none) (source: aos8_get_effective_config(object_name='tacacs_server', config_path='/md'), Batch 1)`

#### 8.4 — Skip / inconclusive

If a Stage 1 batch failed and an object class can't be enumerated, emit ONE row per missing object class with disposition `inconclusive — paste required`, target left blank, notes `*"Stage 1 Batch <N> failed; paste `<exact CLI command>` to enumerate."*`. Do NOT guess at object counts or names.

---

### Stage 9 — Central API call sequence (TRANSLATE-03)

For every row of the Stage 8 disposition matrix where Disposition is `direct-translate` or `transform` AND Central tool is **not** a `[Central API gap]`, compute a topological order respecting these dependency rules:

1. **Hierarchy first.** `central_manage_site_collection` → `central_manage_site` → `central_manage_device_group`. All three must exist before any scoped object.
2. **ACL primitives before role-acls.** `central_manage_net_group` and `central_manage_net_service` BEFORE `central_manage_role_acl` (role ACLs reference net-group / net-service aliases).
3. **Role-acls before roles.** `central_manage_role_acl` BEFORE `central_manage_role` (a role's `access-list` field references role-acls by name).
4. **Roles before WLAN profiles** when a WLAN profile references a default role.
5. **WLAN profiles after roles + ACLs** but BEFORE `central_manage_config_assignment`.
6. **`central_manage_config_assignment` last** — assigns the library objects to scopes (Site Collections / Sites / Device Groups). Without this step, objects exist in the Central library but aren't pushed to devices.
7. **`[Central API gap]` rows** — emit as a placeholder step (`[manual UI step]`) at the position they would otherwise occupy in the dependency order. Subsequent steps that would reference the gap-filled object include the literal warning *"depends on prior manual UI step <step #> being completed."*

**Output:** an ordered numbered list. One step per row of Stage 8 matrix where the row produces a Central API call (skip `drop` / `deprecated` / pure `operator-driven` rows that have no API target). Each step includes:

- **Step #**
- **Target object** (e.g. *"Role 'corp-employee'"*)
- **Central tool** (e.g. `central_manage_role`)
- **Payload sketch** (3-5 key fields; **NOT** a full JSON payload — operators don't need the AI to invent payload details, they need to know which fields matter): *"name='corp-employee', vlan_id=200, access_list_session=['employee-acl'], captive_portal=null"*.
- **Depends on:** comma-separated list of prior step #s (or `none`).
- **Notes** — one short clause per step (operator decisions, gotchas, links to VSG anchor for the disposition).

**Skip:** if all dispositions in Stage 8 are `drop` / `deprecated` / `operator-driven` (zero `direct-translate` or `transform` rows reach a Central tool), output: *"No Central API calls required — the migration is purely a deletion / decommission of legacy features plus operator-driven manual configuration. See the disposition matrix above for manual work items."*

**Findings produced:** none new. Stage 9's value is the ordered plan, not new findings.

---

### Stage 10 — Validation checklist (TRANSLATE-04)

For every Stage 9 step that creates a Central object (i.e. excludes `[Central API gap]` placeholder steps), emit one row of a validation checklist mapping the create call to its corresponding read-back call.

**Read-back mapping** (every `central_manage_*` has a corresponding `central_get_*`):

| Created via | Verify via | Expected attributes |
|---|---|---|
| `central_manage_site_collection` | `central_get_scope_tree` | name, parent_id (root) |
| `central_manage_site` | `central_get_sites` (also `central_get_scope_tree`) | name, parent collection name |
| `central_manage_device_group` | `central_get_scope_tree` | name, parent site name |
| `central_manage_role` | `central_get_roles` | name, vlan, access-list, captive-portal, session-timeout |
| `central_manage_role_acl` | `central_get_role_acls` | name, rule list, ordering |
| `central_manage_net_group` | `central_get_net_groups` | name, member list |
| `central_manage_net_service` | `central_get_net_services` | name, protocol, port range |
| `central_manage_wlan_profile` | `central_get_wlan_profiles` | name, ssid, opmode, VLAN, RADIUS server-group reference |
| `central_manage_config_assignment` | `central_get_config_assignments` | scope_id, profile names assigned |

**Output:** the validation checklist table — one row per Stage 9 create-step:

| Step # (from Stage 9) | Target object | Verify with | Expected attributes |
|---|---|---|---|

**This stage emits the checklist but does NOT execute the reads.** Execution is operator-driven (or Phase 3 territory — see issue #240).

**Findings produced:** none. Stage 10's output is purely a checklist.

**Skip:** if Stage 9 had no create-steps, output *"No Central objects created — validation checklist is empty."*

---

## Decision matrix

| Condition | Action |
|---|---|
| AOS 8 not configured on this MCP server (Stage -1 gate fails) | STOP. Skill does not run. Emit the AOS 6 / IAP redirect message. |
| Operator names AOS 6 or IAP source | STOP. Same redirect. |
| Stage 1 hierarchy walk completes; zero customer-defined objects across all scopes (only AOS 8 system defaults) | **EMPTY-SOURCE** verdict. Act II is still offered (translation plan for whatever defaults exist) but no rule findings — the source has nothing to migrate. |
| Stage 1 hierarchy walk fails entirely (`aos8_get_md_hierarchy` errors) | **PARTIAL** — fall back to `/md` root-only collection; emit one INFO bullet listing what the operator should re-run when the controller is reachable. |
| Stage 1 partial (e.g. cluster state degraded; live-state checks inconclusive) | **PARTIAL** — config-side findings still emit; live-state findings are tagged `inconclusive — clusters offline at audit time`. Do NOT block on cluster-offline. |
| Any REGRESSION fires (only feature-parity rules F1–F10 and orchestration rules O1–O3 can trigger this) | **BLOCKED**. Lead the report with the must-fix list. |
| Only DRIFT / INFO findings present, no REGRESSION | **GO**. |
| Stage 6 verdict gates the Act II gate prompt | BLOCKED → no prompt; GO → standard prompt; PARTIAL → prompt with inconclusive-rows caveat; EMPTY-SOURCE → prompt with "minimal translation plan" caveat. |

**Rules removed from the decision matrix in v2.5.0.1:**

- LMS-IP rules (controller plumbing — moved to inventory; APs go to Central post-cutover, LMS-IP is not migration-predictive).
- Cluster-not-L2-connected REGRESSION (now DRIFT with cluster-offline tolerance).
- AOS 6 / IAP-specific gates (out of scope).
- Stage 0 interview gate ("STOP without all 7 answers" — there is no Stage 0).
- ClearPass cert default REGRESSION (out of scope — ClearPass cert health is its own concern).
- Internet-block-from-mgmt-LAN REGRESSION (folded into O2 — TCP 443 reachability check).

## Output formatting

The skill emits one or two reports:

- **Act I report** — always emitted. Includes the verdict + readiness inventory + REGRESSION / DRIFT / INFO findings + hierarchy mapping + cutover sequence. Use the *Act I template* below.
- **Act II report** — emitted only after operator `yes` at the gate. Includes the per-object disposition matrix + Central API call sequence + validation checklist + OPERATOR-MAP findings. Use the *Act II template* below.

Use the EXACT structure shown. Every section heading must be present even if empty.

### Output hygiene (mandatory)

These rules apply to every finding across Stages 3, 4, 5, 6, 7, 8, 9, 10:

1. **No raw JSON blobs.** When citing an API response, extract and quote only the specific field value relevant to the finding. Never dump the full response dict.
2. **No tool-call syntax in finding text.** Tool names belong in the `(source: tool_name(), Batch N)` attribution at the end of the finding — never inside the finding sentence itself.
3. **No stack traces.** If a tool call raises an exception, emit a brief one-line error note and the fallback CLI command. Never include a Python traceback.
4. **No ellipsis or truncation markers.** Do not write `...`, `[truncated]`, or similar. Extract the relevant fields explicitly; if a response is large, summarise the salient values in prose.
5. **No fabricated VSG anchors.** If the disposition matrix row has no real VSG anchor, the cell reads literally `none`. Do not invent `§####-§####` ranges.
6. **No invented Central tool names.** If a `central_manage_*` tool does not exist for a row, use the literal placeholder `[Central API gap — manual UI: <area>]`. Three known gaps: AAA servers (RADIUS/TACACS/LDAP individual server config), AAA server-groups, AP system profiles.

### Output format is mandatory — do NOT substitute alternatives

Every output element specified below — verdict paragraph, inventory section, hierarchy mapping table, finding lists, cutover sequence, **disposition matrix, API call sequence, validation checklist** — must be produced in **exactly the format shown**. Do NOT substitute:

- **Diagrams, charts, ASCII art, or rendered visualizations** in place of the markdown tables. The output is meant to be paste-able into customer emails / Slack threads / change-management tickets — formats that don't render as plain text are out of scope.
- **Prose paragraphs** in place of finding lists. Findings are bullets so an SE can scan + cite each one independently.
- **Collapsed multi-finding rows** (e.g. "These 4 SSIDs all conflict") in place of one bullet per finding. Each finding is its own row so each can be acted on independently.
- **Reframed verdicts** (e.g. "tentatively GO" or "GO with caveats"). Verdicts are the literal three values: **GO**, **BLOCKED**, or **PARTIAL**.
- **Combined Act I + Act II output** when the operator has not yet answered the gate prompt. Act II is gated; do NOT pre-emit translation rows alongside the Act I report.

If you believe a different format would be more legible, the answer is no — the operator wants paste-ability and consistency across runs more than they want artistic legibility. The hierarchy mapping table is a table specifically because operators read mapping pairs left-to-right; a tree diagram makes them mentally re-pivot.

### Act I template

```
> Open the Act I report with this paragraph (plain prose, 2–4 sentences, never a bullet list, never a table). Three elements in order:
>   1. Verdict in bold caps — **GO** / **BLOCKED** / **PARTIAL** / **EMPTY-SOURCE**.
>   2. Finding counts — exact integers for REGRESSION, DRIFT, INFO. (OPERATOR-MAP findings are part of Act II; do NOT count them in the Act I header. EMPTY-SOURCE has zero findings.)
>   3. One SE-ready sentence — AP count, controller count, and the key action a human SE can paste verbatim into a customer email.
>
> For PARTIAL verdict, append: *"Stage 1 partial — <N> live-state checks were inconclusive (clusters offline at audit time / hierarchy walk degraded). Static config was parsed normally."*
> For EMPTY-SOURCE verdict, replace the action sentence with: *"Source has only AOS 8 system defaults — no customer-defined objects to migrate. Translation plan in Act II will be minimal."*
>
> Template (AI fills the angle-bracket placeholders at runtime; do NOT hard-code values):

**<VERDICT>** — <X> REGRESSION / <Y> DRIFT / <Z> INFO findings. This AOS 8 deployment (<N> APs, <M> controllers, <K> scopes walked) <one plain-English action sentence>. <Optional PARTIAL or EMPTY-SOURCE note if applicable.>

## AOS 8 → AOS 10 migration audit
**Captured:** <ISO timestamp>
**Target SSID forwarding mode (auto-recommended):** <tunnel | bridge | mixed> — derived from <X virtual_ap rows: forward-mode breakdown>. Operator can override.
**Cluster topology (auto-detected):** <L2 cluster <name> at <scope> | L3 cluster | standalone | offline-at-audit-time>
**Target HA mode (auto-recommended):** <Auto Group | Auto Site | Manual> — derived from cluster topology
**L3 Mobility detected in source:** <yes / no>
**AirWave detected in source:** <yes / no>
**Verdict:** GO / BLOCKED / PARTIAL / EMPTY-SOURCE

### Source inventory (live AOS 8 collection — full /md hierarchy walk)
- Hierarchy: <K> scopes walked (root + <K-1> sub-nodes)
- Mobility Conductor firmware: <version>
- Mobility Controller(s) / cluster member count: <N>
- AP count: <N> (models: <table>; static IPs: <Y>; DHCP: <N>)
- Active SSIDs: <list with mode + VLAN>
- Active client baseline: <N total, breakdown per SSID> (or "live-state inconclusive" if clusters offline)
- Local users: <count>
- AP groups: <count + names>
- Configuration nodes: <K> (suggested AOS 10 mapping below)
- Cluster L2/L3 status: <state> (or "configured but offline at audit time" if `lc_cluster_profile` rows present + live cluster empty)
- AP system profile LMS-IPs (inventory only — not a finding): <list of value, scope, ap-group binding>
- AirWave in path: <yes / no>

### Target-side state (Central API)
- Central reachable: ok / degraded
- GreenLake workspace_id: <value>
- AOS 10 / Central subscriptions: AP-license capacity = <N>; source AP count = <M> (sufficient | INSUFFICIENT)
- Central scope tree: <site count> sites, <collection count> collections, <device-group count> device groups
- APs already onboarded to Central: <N> (vs <M> in source — gap = <M-N>)
- ClearPass NAD list coverage for new AP/Gateway IPs: <complete | missing X.Y.Z entries> (only present when ClearPass is in use AND target mode requires new NADs)
- Central name collisions detected (translation enrichment): <count, see Act II disposition matrix>

### Suggested AOS 10 hierarchy mapping
| Source AOS node | Suggested AOS 10 placement | Notes |
|---|---|---|
| <Mobility Conductor /md> | (root, not represented in AOS 10) | n/a |
| <md/<region>> | Site Collection: <name> | grouping |
| <md/<region>/<site>> | Site: <name> | one Site per discrete physical location |
| <md/<region>/<site>/<ap-group>> | Device Group: <name> | per-function device grouping |
| ... | ... | ... |

### REGRESSION findings (must fix before migration)
Findings only fire when their applicability gate is met (see Stage 3). Possible REGRESSIONs include:
- **Mobility Conductor firmware below 8.10.0.12 / 8.12.0.1**: <conductor + running version>. (O1, VSG §1643)
- **TCP 443 to Central blocked from <subnet>**: required for AOS 10 management. (O2, VSG §312-§319)
- **GreenLake AP-license capacity insufficient**: source has <M> APs; GreenLake reports <N> active AP licenses. (O3, VSG §1619-§1620)
- **Static AP IP detected**: <list>. Convert to DHCP. (F5, VSG §1232)
- **AAA FastConnect (EAP-Offload) in use**: <auth profiles using it>. Plan ClearPass-only termination. (F1, VSG §1137)
- **Internal Auth Server in use with local users**: <user count>. Migrate to ClearPass / Cloud Auth. (F2, VSG §1134)
- **L3 Mobility load-bearing AND target = Bridge**: AOS 10 eliminates L3 Mobility. (F3, VSG §897-§900)
- **VC-managed (NAT'd) WLANs without upstream NAT/DHCP plan**: APs don't provide NAT/DHCP in AOS 10 Bridge. (F4, VSG §854-§857)
- **Captive Portal default certificate in use**: replace before cutover. (F9, VSG §364)
- **Internal management LAN blocks Internet**: TCP 443 to Central required. (F10, VSG §315-§317)
- **Tunneled-SSID VLAN present on AP switch port** [Tunnel target]: prune. (T3)
- **VLAN 1 used for tunneled-SSID clients** [Tunnel target]. (T4)
- **AP management subnet routed (not L2)** [Bridge / Mixed target]. (B2)
- **AP switch ports access-mode-only** [Bridge target]: should be trunk. (B4)
- **Secure PAPI (UDP 8211) blocked between APs** [Bridge target]. (B5)
- **Mixed Mode + bridged/tunneled VLAN reuse** [Mixed target]. (M2)
- (or "No REGRESSION findings.")

### DRIFT findings (should address; not blocking)
- **AirWave in path**: monitoring tooling that depends on AirWave needs replacement. (F6, VSG §312)
- **ARM / Dot11a/g / Regulatory Domain profiles in use**: ARM is replaced by **RF Profiles** in AOS 10 / Central. AirMatch already exists in AOS 8 and continues in Central — it is not the AOS 10 ARM replacement. Document existing values for post-cutover comparison. (F7, VSG §1163)
- **ClientMatch tunables relied on**: not adjustable in AOS 10. (F8, VSG §1167)
- **Central scope tree minimal** (no Site Collections): pre-create before migration day. (O4)
- **Backup procedure not documented**: pre-cutover step. (O5, VSG §2435)
- **Rollback plan not documented**: reference VSG §2590-§2591. (O6)
- **Cluster degraded at audit time** (cluster profile present + live members offline): note for cutover prerequisites. (C-01)
- **Roaming domain near scaling limit**: 480/500 APs or 4800/5000 clients. (B6)
- **Jumbo frames not enabled** between APs and Gateway cluster (Tunnel target). (T6)
- **No RTT measurement to Central** for WAN-served sites: confirm < 500 ms. (B11)
- (or "No DRIFT findings.")

### INFO findings (operational reference)
- **AP onboarding gap**: <N> source APs not yet in Central. (A3)
- **AP-per-SSID counts**: <table> — baseline for post-cutover diff.
- **Active client baseline**: <N> total, breakdown per SSID — for post-cutover diff (or "live-state inconclusive — clusters offline at audit time").
- **AP RF baseline**: channel, TX power, client count per AP — for post-cutover comparison.
- **Cluster topology** (auto-detected): <L2 cluster / L3 cluster / standalone / offline> at scope <X> → recommended target HA mode <Y>.
- **Central name collisions** (translation enrichment): <N> collisions detected; full per-row detail appears in Act II disposition matrix.
- **Central-recommended firmware** for the AP models in inventory: <model → version table>.

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
5. (Optional, for legacy controller plumbing) — confirm AP system profile LMS-IPs reference VRRP VIPs; this matters only if you choose to keep APs on AOS 8 alongside the migration. Post-cutover, APs go to Central via TCP 443 and LMS-IP becomes irrelevant.
6. Configure AP switch ports per target mode (per VSG §1924-§2034).
7. Take configuration backup of every Mobility Controller / Conductor / VC.
8. Document rollback procedure (per VSG §2590-§2591).
9. Schedule maintenance window with all client/test devices ready.
10. Run this audit again post-fixes for clean GO verdict.

### PoC caveats (always include in the report)
- This audit was assembled from operator-pasted CLI output (or live AOS 8 API calls when the platform is configured). Output completeness depends on what the operator pasted / what the AOS 8 batches collected. Production migration cutovers should follow the customer's standard change-management process and partner-tool guidance — see VSG §1563-§1575 for the production discovery checklist.
- PII / sanitization is operator-side. The skill does NOT auto-redact pasted content. Operators should redact MAC addresses, RADIUS shared secrets, customer-identifying SSID names, and local user data before pasting if those are sensitive.
- This output is not a substitute for a live engineer reviewing the migration plan. Engage HPE / partner SE for production migrations.
- Scaling values (500 APs / 5,000 clients per Bridge Mode roaming domain; /20 max subnet sizes) are current at VSG publication; confirm against latest AOS 10 documentation.
```

### Gate prompt — emit verbatim after the Act I report

Choose ONE of the following based on the Act I verdict and emit it verbatim. Then stop. Wait for the operator's reply before doing anything else.

```
> If verdict = BLOCKED:
Translation locked until REGRESSIONs are resolved. Re-run the audit after fixes.

> If verdict = GO:
Verdict: GO. Proceed to AOS 10 translation plan? (yes / no / edit-context)

> If verdict = PARTIAL:
Verdict: PARTIAL — <N> Stage-1 collection items were inconclusive. Translation rows for those object classes will be marked `inconclusive — paste required`. Proceed to AOS 10 translation plan? (yes / no / edit-context)
```

### Act II template (only after operator answers `yes` at the gate)

```
> Open the Act II report with this paragraph (plain prose, 2–4 sentences). Three elements in order:
>   1. The literal phrase "Act II — translation plan."
>   2. Disposition counts — exact integers for direct-translate, transform, drop, deprecated, operator-driven, inconclusive.
>   3. Central API gap callout if any, e.g. "<K> object rows require manual UI configuration (no central_manage_* tool exists for: AAA servers, AAA server-groups, AP system profiles)."
>
> Template (AI fills the angle-bracket placeholders at runtime; do NOT hard-code values):

**Act II — translation plan.** <D> direct-translate / <T> transform / <X> drop / <P> deprecated / <O> operator-driven / <I> inconclusive rows produced. <Optional Central-API-gap sentence.> <Optional one-line cross-reference to the Act II findings count, e.g. "<O+gap-count> OPERATOR-MAP findings require manual mapping decisions — see findings list below.">

## AOS 8 → AOS 10 translation plan
**Captured:** <ISO timestamp>
**Reuses Act I context captured at:** <ISO timestamp from Act I report>
**Target SSID forwarding mode:** <tunnel | bridge | mixed> (Act-I-recommended; operator confirmed/overrode)

### Hierarchy translation (Stage 7)
| Source AOS node | Source path | Disposition | Target type (AOS 10) | Target name | Notes |
|---|---|---|---|---|---|
| <Mobility Conductor /md> | `/md` | drop | (none) | n/a | Central org root is implicit |
| <region> | `/md/<region>` | direct-translate | Site Collection | <name> | grouping |
| <site> | `/md/<region>/<site>` | direct-translate | Site | <name> | one Site per discrete physical location |
| <ap-group> | `/md/<region>/<site>/<ap-group>` | direct-translate | Device Group | <name> | per-function device grouping |
| ... | ... | ... | ... | ... | ... |

### Per-object disposition matrix (Stage 8)
| Source name | Source type | Source scope | Usage state | Disposition | Target name | Target type | Central tool | VSG anchor | Notes |
|---|---|---|---|---|---|---|---|---|---|
| corp-radius-1 | rad_server | /md/ACX | assigned-and-active | transform | corp-radius-1 | Server | [Central API gap — manual UI: Network Services → Servers] | §1121 | NAS-IP source must change to gateway IP for Tunnel target |
| CPPM-PUB-ONLY | aaa_server_group | /md/ACX | configured-but-unassigned | transform | CPPM-PUB-ONLY | Server group | [Central API gap — manual UI: Network Services → Server Groups] | §2076 | Orphan in source — operator may choose to skip |
| corp-employee | user_role | /md/ACX | assigned-and-active | transform | corp-employee | Role | central_manage_role | §1173 | per-attribute mapping required (VLAN, ACL list, captive-portal, session-timeout) |
| ACX_apsys_ui | ap_sys_prof | /md/ACX | configured-but-unassigned | transform | ACX_apsys_ui | (none — folded into Device Group config) | [Central API gap — manual UI] | §1651 | Profile not bound to any active ap-group, but still translates per principle |
| corp-ssid-prof | wlan_ssid_profile | /md/ACX | assigned-and-active | direct-translate | corp-ssid-prof | WLAN profile | central_manage_wlan_profile | §2127-§2219 | direct field map per CorpNet 802.1X worked example |
| arm-default | arm_profile | /md | configured-but-unassigned | deprecated | n/a | (none) | (none) | §1163 | Replaced by RF Profiles in AOS 10 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### OPERATOR-MAP findings (manual mapping work items)
- **OPERATOR-MAP** — User role 'corp-employee' requires per-attribute mapping. Set role's VLAN, ACL list, captive-portal, session-timeout in the Central role payload. (VSG §1173) (source: aos8_get_effective_config(object_name='user_role', config_path='/md'), Batch 1)
- **OPERATOR-MAP** — TACACS server 'tacacs-mgmt' has no automated translation rule. Configure manually in Central UI under Network Services → Servers. (VSG none) (source: aos8_get_effective_config(object_name='tacacs_server', config_path='/md'), Batch 1)
- **OPERATOR-MAP** — Session ACL 'employee-acl' has 14 rules; per-rule translation to Central role-acl is operator-driven. Map net-destinations to net-groups, ports to net-services, then re-emit ordered rule list. (VSG none) (source: aos8_get_effective_config(object_name='ip_access_list', config_path='/md'), Batch 1)
- ... (one bullet per `operator-driven` row in the matrix)
- (or "No OPERATOR-MAP findings.")

### Central API call sequence (Stage 9)
1. **Site Collection 'USE'** — `central_manage_site_collection` — payload sketch: name='USE', parent=root — depends on: none — notes: hierarchy first.
2. **Site 'dallas-hq'** — `central_manage_site` — payload sketch: name='dallas-hq', parent_collection='USE' — depends on: 1 — notes: standard.
3. **Device Group 'dallas-hq-floor-3'** — `central_manage_device_group` — payload sketch: name='dallas-hq-floor-3', parent_site='dallas-hq' — depends on: 2 — notes: standard.
4. **Net group 'corp-internal-subnets'** — `central_manage_net_group` — payload sketch: name='corp-internal-subnets', members=['10.10.0.0/16', '10.20.0.0/16'] — depends on: none — notes: ACL primitive.
5. **Net service 'rdp'** — `central_manage_net_service` — payload sketch: name='rdp', protocol='tcp', port=3389 — depends on: none — notes: ACL primitive.
6. **Role ACL 'employee-acl'** — `central_manage_role_acl` — payload sketch: name='employee-acl', rules=[{src=any, dst='corp-internal-subnets', svc='rdp', action=permit}, ...] — depends on: 4, 5 — notes: rules in original AOS 8 ordering.
7. **Role 'corp-employee'** — `central_manage_role` — payload sketch: name='corp-employee', vlan=200, access_list_session=['employee-acl'], captive_portal=null, session_timeout=86400 — depends on: 6 — notes: per-attribute mapping operator-driven.
8. **[Manual UI step]** — Server 'corp-radius-1' (RADIUS) — Central UI: Network Services → Servers → Add — payload sketch: name='corp-radius-1', host='10.50.10.7', shared_secret=<copy from source>, NAS-IP=<gateway_ip per Tunnel target> — depends on: 2 — notes: Central API gap; subsequent step 9 depends on this manual action.
9. **[Manual UI step]** — Server group 'corp-radius-grp' — Central UI: Network Services → Server Groups — payload sketch: name='corp-radius-grp', servers=['corp-radius-1'] — depends on: 8 — notes: Central API gap.
10. **WLAN profile 'corp-ssid-prof'** — `central_manage_wlan_profile` — payload sketch: name='corp-ssid-prof', ssid='CorpNet', opmode='wpa3-aes-ccm-128', vlan=200, server_group='corp-radius-grp' — depends on: 7, 9 — notes: per VSG §2127-§2219 worked example.
11. **Config assignment** — `central_manage_config_assignment` — payload sketch: scope_id=<dallas-hq-floor-3 device-group ID>, profiles=['corp-ssid-prof'] — depends on: 3, 10 — notes: pushes WLAN to AP scope.
... (one step per Stage 9 row)

(or "No Central API calls required — the migration is purely a deletion / decommission of legacy features plus operator-driven manual configuration.")

### Validation checklist (Stage 10)
| Step # | Target object | Verify with | Expected attributes |
|---|---|---|---|
| 1 | Site Collection 'USE' | central_get_scope_tree | name='USE', parent_id=root |
| 2 | Site 'dallas-hq' | central_get_sites | name='dallas-hq', parent='USE' |
| 3 | Device Group 'dallas-hq-floor-3' | central_get_scope_tree | name, parent='dallas-hq' |
| 6 | Role ACL 'employee-acl' | central_get_role_acls | name, rule list, ordering |
| 7 | Role 'corp-employee' | central_get_roles | name, vlan=200, access-list=['employee-acl'], session-timeout=86400 |
| 10 | WLAN profile 'corp-ssid-prof' | central_get_wlan_profiles | name, ssid='CorpNet', opmode, vlan, server_group |
| 11 | Config assignment | central_get_config_assignments | scope_id, profile names |

(Manual UI steps 8 + 9 are not in the validation checklist — they are operator-verified in the Central UI.)

### Act II PoC caveats (always include in the Act II report)
- The skill emits the **plan**. It does NOT execute `central_manage_*` write tools. Execution is operator-driven (or Phase 3 territory — see issue #240). Subsequent operator runs of `central_manage_*` tools fire the standard write-tool elicitation flow.
- The disposition matrix represents AOS 8 → AOS 10 mapping at PoC quality. Per-object accuracy depends on the depth of Stage 1 collection (and the gestural nature of the VSG's per-object guidance — most rows are `operator-driven` because the VSG itself stops short of field-by-field rules outside the two worked SSID examples).
- Three known Central API gaps (AAA servers, AAA server-groups, AP system profiles) require manual UI action. The plan steps marked `[Manual UI step]` are not optional — they are real prerequisites for downstream API calls in the same plan.
- This translation plan is not a substitute for review by an Aruba SE.
```

## Example queries that should trigger this skill

> "AOS 8 to AOS 10 migration"
> "AOS 8 migration to Central"
> "am I ready to migrate from AOS 8 to AOS 10?"
> "audit my AOS 8 environment for AOS 10 migration"
> "migration readiness check"
> "validate my migration plan"
> "what do I need before AOS 10 cutover"
> "Central readiness for AOS 10"
> "Tunnel vs Bridge vs Mixed mode planning"
> "switchport configuration for AOS 10"
> "RADIUS NAD changes for AOS 10"
> "AirWave deprecation impact for AOS 10"
> "L3 Mobility migration to AOS 10"
> "translate AOS 8 config to AOS 10"
> "AOS 10 config mapping"
> "AOS 8 to Central object mapping"
> "build me an AOS 10 migration plan"
> "generate Central API call sequence for migration"
> "what objects do I need to recreate in Central"
