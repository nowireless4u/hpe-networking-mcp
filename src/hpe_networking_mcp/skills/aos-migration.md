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

  One upfront question — the data SOURCE (Stage -2): (1) AOS 8 direct via
  API, (2) configuration upload, or (3) pasted configuration snippet — a
  delivery-mechanism choice. On the API path the skill then detects AOS 8
  reachability via health-probe, walks the entire /md hierarchy for
  inventory, and DETECTS the target-architecture signals (per-SSID
  forward mode, SSID→cluster map, cluster topology, AirWave presence,
  L3 Mobility usage) from the collected config. Those detections are
  recommendations. After the readiness verdict, a target-architecture
  questionnaire (Stage 6.5) presents them and the operator DECIDES the
  per-SSID forward mode and gateway topology — the source says what is,
  the operator says what they want (e.g. going controllerless). The
  upload / paste paths parse an offline config via aos8_parse_config
  (policy / role / net-destination subset — see Stage -2 coverage note).

  PoC — in-chat workflow for SE pre-engagement use; production
  migration cutovers follow the customer's standard change-management
  process and partner-tool guidance.
platforms: [central, aos8]
tags: [central, migration, aos8, aos10, readiness, audit, vsg, translation]
tools: [health, central_get_scope_tree, central_get_devices, central_get_aps, central_get_sites, central_get_site_name_id_mapping, central_recommend_firmware, central_get_config_assignments, central_get_server_groups, central_get_wlan_profiles, central_get_roles, central_get_role_acls, central_get_net_groups, central_get_net_services, central_get_named_vlan, central_get_aliases, central_get_gw_cluster_intent_config, central_get_gateway_clusters, translate_config_preview, translate_config_apply, translate_wlan_preview, translate_wlan_apply, central_manage_site, central_manage_site_collection, central_manage_device_group, central_manage_roles, central_manage_role_acls, central_manage_net_groups, central_manage_net_services, central_manage_wlan_profile, central_manage_config_assignment, central_manage_gw_cluster_intent_config, central_manage_gateway_clusters, clearpass_get_network_devices, clearpass_get_device_groups, clearpass_get_server_certificates, clearpass_get_local_users, greenlake_get_subscriptions, greenlake_get_workspace, greenlake_get_devices, aos8_get_md_hierarchy, aos8_get_effective_config, aos8_get_ap_database, aos8_get_cluster_state, aos8_show_command, aos8_get_clients, aos8_get_bss_table, aos8_get_active_aps, aos8_get_ap_wired_ports, aos8_parse_config, file_manager, read_file]
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
- An **upfront configuration interview.** Act I (Stages -1 through 6) asks **no** config questions — it's a read-only audit. The one upfront question is the data *source* (Stage -2: API / upload / paste), a delivery-mechanism choice. The skill walks the hierarchy and **detects** every target-architecture signal from the source (per-SSID `forward-mode`, the SSID→cluster map, cluster-mode signals from AP-adoption + multizone, AirWave presence, L3 Mobility usage). Those detections become **recommendations**, not silent decisions: after the readiness verdict, the **target-architecture questionnaire (Stage 6.5)** presents them per SSID and the operator confirms or changes them (forward mode per SSID, gateway topology). The source says what *is*; the operator decides what they *want* (e.g. going controllerless) — so the architecture decisions are an explicit post-verdict questionnaire, never inferred-and-applied.
- A **migration executor.** Never calls `central_manage_*` write tools. Plan only; Phase 3 (issue #240) is the execution capability.
- A **rollback engine.** Rollback is captured as text in the cutover stage; not auto-generated as reversible API calls.
- A **gap-filler for missing Central write tools.** Three known gaps (AAA RADIUS/TACACS server, AAA server-group, AP system profile) get `[Central API gap — manual UI action required]` placeholders. No invented tool names.
- An **automatic VSG-anchor fabricator.** Object types the VSG doesn't cover (TACACS / LDAP server config, MAC-auth profile, captive portal, MAC randomization) get `vsg-anchor: none` and emit `OPERATOR-MAP` findings.
- An **AOS 6 / IAP migration tool.** If the operator names AOS 6 or IAP, redirect: *"AOS 6 has a different migration path; IAP customers usually flow through classic Central. Engage Aruba SE for those scenarios."*

If the operator asks for execution (running the plan against Central), point them at issue #240 (Phase 3 deferred) and stop.

## PoC scope + roadmap caveat

Live AOS 8 API collection means the skill receives effective-config and cluster state directly from the controller — no operator paste. The output may include customer-identifiable data (server IPs, MAC addresses, RADIUS shared secrets when explicitly returned by AOS 8, local user databases). PII tokenization (when enabled in the MCP server) covers most of this; some fields may slip through. Operators reviewing the report should be aware before sharing it externally.

The skill's job is to prove the in-chat workflow produces credible readiness findings + a translation plan. Sanitization layers and Phase-3 execution are tracked separately.

## Procedure — 10 numbered stages across two acts (plus the Stage 6.5 questionnaire between the acts)

**Data-source gate (Stage -2) — ALWAYS FIRST.** Before any collection, ask the operator how to obtain the AOS 8 config — (1) API, (2) upload, (3) paste — and route accordingly. See Stage -2.

**Act I (Stages -1 through 6) — readiness audit.** Runs in full on the **API path** (Stage -1 → Stage 1). On the **upload / paste paths** it runs in reduced form against the offline-parsed subset (Stage 1-ALT replaces Stage -1 + Stage 1; object classes the parser doesn't cover are marked `inconclusive — offline source`). Ends with a verdict + combined report.

**Gate — operator confirmation.** After Stage 6, the AI emits the verdict report (stating whether the devices are Central-ready) THEN literally prints the prompt: *"Verdict: <V>. Proceed to AOS 10 translation plan? (yes / no / edit-context)"* and stops. No Act II execution without operator `yes`.

- If verdict is **BLOCKED**, the gate does not appear. The report ends with *"Translation locked until REGRESSIONs are resolved. Re-run the audit after fixes."*
- If verdict is **PARTIAL**, the gate appears but warns which translation rows will be marked `inconclusive` (any object class where Stage 1 collection failed).
- If verdict is **GO**, the gate appears with no caveat.
- If verdict is **EMPTY-SOURCE** (only AOS 8 defaults found), the gate appears with a no-customer-config caveat and, on `yes`, **skips Stage 6.5** (nothing to decide) — there are no SSIDs/clusters, so Act II runs on defaults only.

**Stage 6.5 — Target-architecture questionnaire.** On operator `yes`, BEFORE the translation plan, run the questionnaire (Stage 6.5): the per-SSID forward-mode decision + the gateway-topology decision, pre-filled from Act I detection. This is where the operator decides what they *want* (the source only told us what *is*). The answers populate the Act II `runtime_values`. See Stage 6.5.

**Act II (Stages 7 through 10) — translation plan.** Fires after Stage 6.5. Reuses everything Act I already collected; no re-fetching, no second operator paste. Output is the **plan** (disposition matrix + ordered API call sequence + validation checklist), not executed `central_manage_*` writes.

If the operator answers `no`, end the session with the Act I report unchanged.
If the operator answers `edit-context` (e.g. "actually our readiness inputs are wrong"), update the corresponding Stage 1 context fields, re-run Stage 3 + Stage 6 to re-verdict, and re-emit the gate prompt. (Forward-mode / topology *target* choices are made in Stage 6.5, not here — `edit-context` is for correcting detected source facts that change the verdict.)

---

### Stage -2 — Data source selection (SOURCE-00) — ALWAYS FIRST

This is the skill's only *upfront* question — it chooses the *delivery mechanism* for the AOS 8 config, not a config value. (The architecture decisions come later, in the Stage 6.5 questionnaire, after the readiness verdict.) Present exactly these three options and STOP for the operator's choice:

```
How should I pull the AOS 8 configuration?

  1. AOS 8 direct via API  — I collect live from the controller across the full
                             /md hierarchy. Highest fidelity: full two-act audit
                             (cluster topology, AP / SSID / AAA inventory, live state)
                             + translation plan.
  2. Configuration upload  — you upload an AOS 8 running-config file; I parse it
                             offline (policy / role / net-destination subset).
  3. Pasted snippet        — you paste AOS 8 CLI config; I parse it offline
                             (policy / role / net-destination subset).

Reply 1, 2, or 3.
```

Route on the reply:

- **1 (API)** → Stage -1 (reachability gate) → Stage 1 (live hierarchy collection) → Stage 2 → the full pipeline.
- **2 (upload)** → Stage 1-ALT (offline parse, upload branch). Skip Stage -1 + Stage 1.
- **3 (paste)** → Stage 1-ALT (offline parse, paste branch). Skip Stage -1 + Stage 1.

**Coverage — state this to the operator when they pick 2 or 3.** The constraint is what the parser *models today*, NOT what offline can see — the operator can include any `show` output in the upload/paste:

- `show running-config` already carries `wlan ssid-profile`, `wlan virtual-ap` (forward-mode), `aaa` profiles, `lc-cluster profile`, and `ap system-profile` as config stanzas; operational data lives in separate commands (`show ap database`, `show lc-cluster group-membership`, `show ap active`).
- `aos8_parse_config` **currently models only** `netdestination` / `netdestination6`, `ip access-list session`, and `user-role` (the inputs to the Central `policy` / `role` / `net_group` translations). Everything else the operator includes surfaces in `_warnings` rather than being parsed — coverage grows as the parser gains handlers, it is not blocked by the offline path.

For the richest offline result, ask the operator to bundle `show running-config` **plus** `show ap database`, `show lc-cluster group-membership`, and `show ap active` into the upload. Object classes the parser hasn't yet modeled are marked `inconclusive — not yet parsed (include the relevant show output / extend parser)`; readiness rules whose data is absent don't fire. The API path (option 1) is still the zero-parser-gap route.

**Availability of option 2 (upload):** requires the server's MCP-Apps capability (`MCP_APP_ENABLE=true`) AND an MCP-Apps-capable client (Claude Desktop / ChatGPT) to render the upload widget. If `file_manager` is not present in the catalog, tell the operator option 2 is unavailable on this server and offer option 3 (paste) instead.

### Stage -1 — AOS 8 reachability gate (DETECT-01)

Reached only on the **API path** (operator chose option 1 at Stage -2).

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

### Stage 0 — (deleted; no upfront config interview)

Act I asks **no** config questions — the one upfront question (Stage -2) selects the data source, not config values. Act I **detects** the target-architecture signals from the source so the audit can run and so the **Stage 6.5 questionnaire** (after the readiness verdict) has informed defaults. Detection ≠ decision: the operator confirms or changes the architecture in Stage 6.5.

- **Per-SSID forward mode (detected)** — Stage 2 reads each `virtual_ap.forward_mode` (`tunnel` / `bridge` / `split-tunnel` / `decrypt-tunnel`) and recommends a per-SSID AOS 10 target (`tunnel`+`decrypt-tunnel`→Tunnel, `bridge`→Bridge, `split-tunnel`→Hybrid). This is a **recommendation that pre-fills the Stage 6.5 per-SSID question** — the operator decides the actual target (and may go controllerless / change any SSID).
- **SSID→cluster map (detected)** — which cluster each SSID's ap-group anchors to; same essid spanning clusters / same-ap-group-to-different-clusters flags a DMZ pattern. Feeds the Stage 6.5 gateway-topology question.
- **Cluster topology** — `aos8_get_cluster_state` (Batch 3) + cluster-profile config (Batch 1). The cluster-mode recommendation derivation (AP-adoption + multizone; algorithm at Stage 7 Step 4) runs during Stage 2 detection and becomes the Stage 6.5 recommendation.
- **AirWave presence** — detected from effective-config (`mgmt-server`, `ams-ip`, AMP profile entries).
- **L3 Mobility usage** — detected from effective-config (`mobility l3-mobility` lines).
- **HA mode mapping** — recommended from cluster topology; confirmed in Stage 6.5.

### Stage 1 — Live AOS 8 inventory across the full /md hierarchy (COLLECT-01..04)

The skill is in code mode — collection runs as Python orchestration inside the `execute()` sandbox, NOT as a fixed sequence of skill-prescribed tool calls. The pattern below is the goal + data shape; the AI composes the actual calls.

#### Envelope helper — define once, reuse everywhere (USE UNMODIFIED)

Define `_unwrap()` at the top of every `execute()` block in Stages 1, 4, 5, 7 and reuse it. **Do NOT paraphrase this helper into a one-liner** — AIs that did so crashed when an AOS 8 read tool returned a string error at `data` (issue [#269](https://github.com/nowireless4u/hpe-networking-mcp/issues/269)).

```python
def _unwrap(response):
    """Strip the v3.0.0.0 envelope + optional inner {"result": ...} wrapper.

    Tolerates any shape: returns ``response`` unchanged when not enveloped,
    a string payload when ``data`` is a string (AOS 8 read tools are typed
    ``dict | str`` and return strings on error/timeout), and the inner
    payload when the tool double-wraps in ``{"result": ...}``.
    """
    if not isinstance(response, dict):
        return response
    payload = response.get("data", response)
    if isinstance(payload, dict) and "result" in payload:
        return payload["result"]
    return payload
```

Every `call_tool(...)` result in Stages 1-7 should be passed through `_unwrap()` before further indexing. The contract is: `_unwrap()` always returns a value safe to test with `isinstance(x, (dict, list, str))` — the *caller* still has to branch on the return type before calling `.get()` or iterating.

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
    # RBAC / ACLs (acl_eth / acl_mac excluded — unique-use cases not encountered
    # in real migrations; see issue #298). netdst / netdst6 are the IPv4 / IPv6
    # netdestination aliases referenced by acl_sess rules via salias / dalias
    # discriminators; central:net_group translation creates them in Central
    # before central:policy POSTs the rules that reference them by name.
    "role", "acl_sess", "netdst", "netdst6",
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
            inner = _unwrap(response)
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

`cluster_state` may return `{"_global_result": {"status": "1", ...}}` or empty list when no cluster is currently active. **Look for `cluster_prof` rows in `config_by_scope` first** — a cluster *profile* defined at any scope (commonly `/md/<region>` or `/md/<region>/<site>`, NOT `/md` root) is the source of truth even when live cluster membership is empty (controllers offline). Live cluster state is supplementary.

#### COLLECT-04 — Client baseline + BSS table + active APs + per-AP wired ports

```python
clients = await call_tool("aos8_get_clients", {})
bss_table = await call_tool("aos8_get_bss_table", {})
active_aps = await call_tool("aos8_get_active_aps", {})

ap_db_payload = _unwrap(ap_database)
ap_names = [
    ap["Name"]
    for ap in (ap_db_payload.get("AP Database", []) if isinstance(ap_db_payload, dict) else [])
]
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

### Stage 1-ALT — Offline config parse (PARSE-01) — upload / paste branches

Runs **instead of** Stage -1 + Stage 1 when the operator chose option 2 or 3 at Stage -2. Produces the same canonical records the translation engine consumes, via `aos8_parse_config`.

**Option 2 — Configuration upload:**

1. Invoke `file_manager` to render the upload widget. Tell the operator: *"Drop or pick your AOS 8 running-config file (the output of `show running-config`, or any file containing `netdestination` / `ip access-list session` / `user-role` stanzas)."*
2. After the operator uploads, the file is held in the server's session store. Parse it:
   - **Preferred (context-clean):** `aos8_parse_config(filename="<uploaded filename>")` — the tool reads the file *inside the server* so the raw config never enters the model context.
   - **Fallback** (if this server's `aos8_parse_config` does not accept `filename`): `read_file(name="<uploaded filename>")` to retrieve the text, then `aos8_parse_config(cli_text="<that text>")`.

**Option 3 — Pasted snippet:**

1. Ask the operator to paste the AOS 8 CLI config (the relevant `netdestination` / `ip access-list session` / `user-role` stanzas, or a full `show running-config`).
2. `aos8_parse_config(cli_text="<pasted text>")`.

All branches return `{netdst, acl_sess, role, _warnings}`. These keys feed the Central translations **directly** — `acl_sess` → `central:policy`, `role` → `central:role`, `netdst` (+ `netdst6`) → `central:net_group` — no inventory normalization required for those classes.

Seed the Stage 2 `inventory` with what was parsed and mark everything else inconclusive:

- `inventory["session_acls"]     = acl_sess`
- `inventory["user_roles"]       = role`
- `inventory["net_destinations"] = netdst (+ netdst6)`
- `inventory["_offline_source"]  = True`
- `inventory["_parse_warnings"]  = _warnings`  — surface as a coverage note; unmodelled clauses are visible, not silently dropped
- every other inventory class (`ap_database`, `cluster_profiles`, `ssid_profiles`, `aaa_*`, live state) → `inconclusive — offline source`

Then skip to **Stage 3**. Applicability gates there naturally suppress the rules whose data is missing — most feature-parity / orchestration rules will not fire on the offline subset. The Act II translation (Stages 7-10) runs for the parsed object classes (policy / role / net_group); rows for unparsed classes are marked `inconclusive — offline source / API or paste required`.

### Stage 2 — Parse the live-collected inventory + detect target-architecture signals

Stage 1 collected raw API responses across the full hierarchy. Stage 2 normalizes those responses into a structured inventory and derives the inputs the old skill used to ask the operator for. **API path only** — the upload / paste paths populate `inventory` from the offline parse in Stage 1-ALT instead and skip the normalization below.

#### Normalize the inventory

For each scope in `config_by_scope`, group responses into:

```python
inventory = {
    "scopes": [...],                                # /md tree paths
    "ap_database": [...],                           # one entry per AP
    "active_aps": [...],                            # subset that are currently up (may be [] if offline)
    "clients": {...},                               # aggregate per-SSID counts
    "bss_table": [...],                             # one entry per ESSID broadcast
    "cluster_profiles": [...],                      # cluster_prof DEFINITION rows only —
                                                    # filter out entries where _flags.inherited == True.
                                                    # entry_type="user" keeps user-config but does NOT
                                                    # strip the inherited copies that AOS 8 surfaces at
                                                    # every descendant scope; the SAME profile re-appears
                                                    # at /md/<region>, /md/<region>/<site>, etc. Dedupe
                                                    # by keeping only the row at the scope that defines
                                                    # it. (issue #270)
    "live_cluster_state": {...},                    # aos8_get_cluster_state result
    "ap_groups": [...],                             # virtual_ap and ap_sys_prof
    "ssid_profiles": [...],                                        # ssid_prof rows
    "user_roles": [...],                                            # role rows
    "session_acls": [...],                                          # acl_sess rows
    "aaa_servers": {radius: [...], tacacs: [...], ldap: [...]},   # internal_db dropped — Central replaces internal-DB auth entirely
    "aaa_server_groups": [...],                                    # server_group_prof rows
    "auth_profiles": {dot1x: [...], mac_auth: [...], captive_portal: [...]},  # dot1x_auth_profile / mac_auth_profile / cp_auth_profile
    "ap_system_profiles": [...],                                   # ap_sys_prof rows
    "rf_profiles": {arm: [...], reg_domain: [...], ht_radio: [...]},  # arm_prof / reg_domain_prof / ht_radio_prof (single combined object since AOS 8.4)
    "local_users": [...],
    "controller_inventory": {serials, macs, mgmt_ips},
    "controller_firmware_versions": [...],
    "ports_and_trunks": [...],
}
```

Each entry tagged with `source_scope` (which `/md/...` node defined it). The same logical object (e.g. an `ssid_prof` named "CorpNet") may appear at multiple scopes — preserve all instances; do not dedupe.

#### Detect target-architecture signals (feeds Stage 3 rules + pre-fills the Stage 6.5 questionnaire)

With the live inventory in hand, detect the signals the audit rules need and that the post-verdict questionnaire will present for operator decision. **These are recommendations, not applied decisions** — the operator confirms/changes them in Stage 6.5.

| Signal | Detect from |
|---|---|
| **Source platform** | Always `aos8` — the skill's only supported source |
| **Per-SSID forward mode (recommendation)** | Read `forward_mode` on each `virtual_ap` (`tunnel` / `bridge` / `split-tunnel` / `decrypt-tunnel`; absent = `tunnel` default). Recommend the AOS 10 target per SSID: `tunnel`+`decrypt-tunnel`→Tunnel, `bridge`→Bridge, `split-tunnel`→Hybrid. **Pre-fills the Stage 6.5 per-SSID question.** |
| **SSID → cluster map** | For each `virtual_ap`, the cluster its ap-group anchors to (via ap-system-profile / cluster membership). Same essid across clusters, or one ap-group's SSIDs anchoring to different clusters → **DMZ pattern** flag. Feeds the Stage 6.5 gateway-topology question. |
| **Aggregate forward-mode mode** (`tunnel` / `bridge` / `mixed`) | All SSIDs tunnel → tunnel; all bridge → bridge; mix → mixed. Drives the Stage 3 per-target-mode rule gates (the rules still run on the *recommended* mode pre-questionnaire). |
| **AirWave in path** | `running_config` `mgmt-server` / `ams-ip` / `mobility-manager` lines. Present → DRIFT finding. |
| **Cluster topology** (L2 / L3 / standalone) | `cluster_prof` + `group_membership`. `controller-l2-only` → L2; cross-VLAN members → L3; none → standalone. **Default L2** when ambiguous. |
| **L3 Mobility usage** | `running_config` `mobility l3-mobility` lines. |
| **Cluster-strategy recommendation** | **Run the cluster-mode recommendation derivation here** (the algorithm is documented at Stage 7 Step 4 but executes during *this* detection pass — it reads only Stage 1 data, and its output is needed by Stage 6.5 which runs before Stage 7). From the SSID→cluster map + AP-adoption/multizone: no DMZ → `intent_site`@global; campus + DMZ → `intent_site`(campus) + `intent_manual`(DMZ); DMZ-only/few → `ha_only`. Pre-fills the Stage 6.5 gateway-topology question. |

These detections feed Stage 3 rules (which run against the *recommended* target mode) and pre-fill Stage 6.5. The **report** shows each detected value + how it was derived (e.g. *"SSID `CORP`: tunnel today (forward-mode=tunnel) → recommend Tunnel"*) so the operator decides Stage 6.5 with full context.

#### Cluster-offline tolerance

When `aos8_get_cluster_state()` returns degraded data (clusters offline at audit time), prefer **`cluster_prof` config rows** as the source of truth. Examples:

- Live cluster state empty + `cluster_prof` rows present → cluster IS configured but currently offline; emit *"Cluster `<name>` is configured at scope `<source_scope>` but live cluster membership is empty (members offline at audit time). Static config is parsed normally."*
- Live cluster state empty + no cluster profiles found at any scope → no cluster configured. Note in inventory; no rules fire.

The audit MUST proceed in either case. Don't refuse to verdict.

### Stage 3 — Apply rules with applicability gates

Rules fall into four buckets:

1. **INVENTORY** — record what's there; never fires as REGRESSION/DRIFT. Includes legacy AOS 8 controller plumbing (LMS-IP, Backup-LMS-IP, AP Fast Failover, cluster topology) that dissolves at migration but informs Act II translation. Drives the report's inventory section, not its findings list.
2. **Source-readiness findings (verdict-gating)** — target-architecture-INDEPENDENT feature-parity findings: the source uses something AOS 10 can't represent at all, regardless of forward mode. These compute the **pre-questionnaire verdict** (a REGRESSION here → BLOCKED). **Each rule has an applicability gate** — no rule fires on an empty source surface.
3. **Orchestration prerequisites (verdict-gating)** — fire as REGRESSION when the operator can't run the cutover at all (Central unreachable, GreenLake under-licensed, controllers below firmware floor). Target-independent → contribute to the pre-questionnaire verdict.
4. **Target-architecture-dependent findings (PROVISIONAL — do NOT gate the pre-questionnaire verdict)** — any rule whose applicability depends on the *target* architecture: those gated on `target_mode_recommended` (F3, F4, and the per-target-mode T\*/B\*/M\* blocks below) **and the Stage 4a orchestration checks A4 + A5** (A4 gated on `target_mode_recommended`; A5 on cluster presence, which is moot if the operator goes all-Bridged). These are scored against the *recommended* mode only as a preview. **They must NOT force a BLOCKED verdict before Stage 6.5**, because the operator may choose a different target mode (e.g. Bridged / controllerless) that makes them moot. They are re-evaluated against the operator's actual Stage 6.5 choices and surfaced in the Act II plan — see Stage 6.5's re-score step. The Stage 6 verdict is computed from buckets 2 + 3 only.

> **INVARIANT (do not break in future edits):** Bucket-4 (target-architecture-dependent) findings must **never** be included in the pre-questionnaire verdict count. The Stage 6 verdict = buckets 2 + 3 only. Breaking this lets a target-mode finding BLOCK the gate and lock the operator out of Stage 6.5 — the exact dead-end this design removes.

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
| Cluster topology (L2 / L3 / standalone) per `cluster_prof` | Cluster name, scope, member list, VRRP VIP(s) | Drives the target HA-mode recommendation (confirmed in Stage 6.5) |
| AP Fast Failover config | Record presence/absence | No AOS 10 equivalent — APs reconnect to Central, not via Fast Failover |
| VRRP VIPs configured | Record values + member controllers | Inputs to disposition matrix; drives hierarchy translation |

#### Feature-parity findings (fire only when applicability gate is met)

| # | Rule | Gate | Severity if triggered | Anchor |
|---|---|---|---|---|
| F1 | **AAA FastConnect / EAP-Offload in use** — not supported in AOS 10 | `fastconnect_in_config` | REGRESSION | VSG §1137-§1141 |
| F2 | **Internal Authentication Server in use with local users** — no Internal Auth Server in AOS 10 | `local_user_count > 0` | REGRESSION; operator plans ClearPass / Cloud Auth migration | VSG §1134-§1136 |
| F3 | **L3 Mobility load-bearing in source design** — eliminated in AOS 10 | `l3_mobility_in_config AND target_mode_recommended in {bridge, mixed}` | REGRESSION (Bridge target) / DRIFT (Tunnel target) | VSG §897-§900 |
| F4 | **VC-managed (NAT'd) WLANs** depending on controller-side NAT/DHCP — AOS 10 Bridge APs don't provide NAT/DHCP | `vc_managed_wlans_present AND target_mode_recommended in {bridge, mixed}` | REGRESSION | VSG §854-§857 |
| F5 | **Static AP IPs detected** — APs need **DHCP during initial Central onboarding** (Aruba Activate + first call-home to Central require DHCP-supplied IP / DNS / default-gateway). Operator may switch APs back to static IPs **after** they're adopted into Central. Constraint is AP-specific — gateways and switches do NOT have this onboarding-DHCP requirement and can be brought in static. | `any_ap_has_static_ip` | DRIFT (operator must ensure AP onboarding window has DHCP available; not a permanent requirement) | VSG §1232-§1234 |
| F6 | **AirWave-dependent monitoring** in path (`mgmt-server` / `ams-ip` / AMP profile) — AirWave deprecated | `airwave_in_config` | DRIFT | VSG §312-§313 |
| F7 | **ARM / HT radio / regulatory-domain profiles in active use** (`arm_prof` / `ht_radio_prof` / `reg_domain_prof`) — replaced by RF Profiles in AOS 10 | `arm_or_ht_radio_or_reg_domain_profile_present` | DRIFT — record values for post-cutover comparison | VSG §1163-§1166 |
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

#### Per-target-mode findings (PROVISIONAL — bucket 4; do NOT gate the pre-questionnaire verdict)

These are scored against `target_mode_recommended` as a **preview only**. A REGRESSION here must **not** produce a BLOCKED verdict before Stage 6.5 — surface it in the report as *"provisional (recommended target = <mode>); re-scored after you choose in Stage 6.5"*. After the operator picks per-SSID modes in Stage 6.5, re-run these against the **chosen** modes and fold the results into the Act II plan (Stage 6.5 re-score step). An operator flipping every SSID to Bridged makes the Tunnel/Mixed-mode REGRESSIONs disappear — which is exactly why they can't pre-block the gate.

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
| A4 | **NAD list coverage for new AP subnets** | `clearpass_get_network_devices()` | `ap_count > 0` AND `target_mode_recommended in {bridge, mixed}` AND `is_clearpass_used` | **PROVISIONAL** REGRESSION (bucket 4 — see note) |
| A5 | **NAD list coverage for cluster gateways/VRRP VIPs** | `clearpass_get_network_devices()` | `cluster_profile_present` AND `is_clearpass_used` | **PROVISIONAL** REGRESSION (bucket 4 — see note) |

`is_clearpass_used` = the source's `server_group_prof` references at least one `rad_server` whose host matches a configured ClearPass instance OR the operator runs ClearPass per inventory. If false, A4 / A5 don't fire — the source uses non-ClearPass RADIUS or none at all.

**A1–A3 are bucket 3: target-architecture-INDEPENDENT** (Central reachable, GreenLake capacity, AP-onboarding gap apply no matter what the operator chooses). A1 and A2 are REGRESSIONs → they compute into the pre-questionnaire verdict; **A3 is INFO-only** (the AP-onboarding gap is reported, never blocks). So the verdict-gating Stage 4a checks are **A1–A2**. **A4 and A5 are target-architecture-DEPENDENT → bucket 4 (PROVISIONAL):** A4 is gated on the *recommended* `target_mode`, and A5's gateway/VRRP NAD requirements evaporate if the operator chooses all-Bridged/controllerless in Stage 6.5. They must **NOT** force a BLOCKED verdict pre-questionnaire (same dead-end the bucket split removes), and are **re-scored after Stage 6.5** against the chosen `target_mode` / surviving gateway clusters — see the Stage 6.5 re-score step. Surface them pre-questionnaire as *"provisional (recommended target = X)"*, not as a verdict-gating REGRESSION.

#### Stage 4b — Translation enrichment (feeds Act II disposition matrix)

Findings in this section are NOT used to compute the Stage 6 verdict. They populate the disposition matrix in Stage 8 — when an AOS 8 object collides with a same-named Central object, the disposition row notes the collision and proposes a target name suffix or rename.

| # | Enrichment | Tool | Used by Stage 8 to |
|---|---|---|---|
| E1 | Central WLAN-profile name collision check | `central_get_wlan_profiles()` | Tag `ssid_prof` rows where the AOS 8 ESSID already exists as a Central WLAN profile. |
| E2 | Central role-name collision check | `central_get_roles()` | Tag `role` rows where the AOS 8 role name already exists in Central. |
| E3 | Central named-VLAN ID collision check | `central_get_named_vlan()` | Tag VLAN rows where the AOS 8 VLAN ID already maps in Central under a different name. |
| E4 | Central server-group collision check | `central_get_server_groups()` | Tag `server_group_prof` rows where the same name already exists in Central. |
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
| C-01 | **Live cluster health** — when `cluster_prof` rows exist (cluster is configured), `aos8_get_cluster_state()` should report `L2-connected`. If degraded, the audit notes it but does NOT block — clusters can be brought to L2-connected before cutover. | `live_cluster_state` from Stage 1 COLLECT-03 | DRIFT if degraded; INFO if L2-connected; INFO with `cluster offline at audit time` note if `cluster_prof` exists but live state empty |
| C-02 | **Mobility Conductor firmware floor** — running version on Conductor must be `8.10.0.12` / `8.12.0.1` or later (prerequisite for AOS 10 image push). One **fresh** call: `aos8_show_command(command='show version')` (cannot rely on `show inventory` — running firmware not reliably surfaced there). | fresh call in Stage 5 | REGRESSION if below |
| C-03 | **Pre-cutover AP-count baseline** — record `len(ap_database)` for post-cutover diff. | Stage 1 COLLECT-02 | INFO |

If `cluster_prof` rows are absent (no cluster configured), C-01 doesn't fire and C-02 still runs. C-03 always runs.

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

After emitting the Stage 6 readiness report, decide. **The verdict is computed from source-readiness + orchestration findings (Stage 3 buckets 2 + 3) ONLY** — target-architecture-dependent findings (bucket 4, gated on `target_mode_recommended`) are provisional and never produce BLOCKED here, so they can never lock the operator out of Stage 6.5. (If the source is genuinely un-migratable in any mode, that's a bucket-2 source-readiness REGRESSION and BLOCKED is correct.)

- **Verdict = BLOCKED** — emit the literal sentence: *"Translation locked until REGRESSIONs are resolved. Re-run the audit after fixes."* Stop. Do NOT print the proceed prompt; do NOT run Stages 7-10.
- **Verdict = GO** — emit the literal prompt: *"Verdict: GO. Proceed to AOS 10 translation plan? (yes / no / edit-context)"* and stop. Wait for the operator's reply.
- **Verdict = PARTIAL** — emit the literal prompt: *"Verdict: PARTIAL — <N> Stage-1 collection items were inconclusive. Translation rows for those object classes will be marked `inconclusive — paste required`. Proceed to AOS 10 translation plan? (yes / no / edit-context)"* and stop. Wait for the operator's reply.
- **Verdict = EMPTY-SOURCE** — the hierarchy held only AOS 8 system defaults (no customer-defined objects). Emit the literal prompt: *"Verdict: EMPTY-SOURCE — no customer-defined config found; there is nothing to translate beyond AOS 8 defaults. Proceed anyway to see the default-only plan? (yes / no)"* and stop. On `yes`, **skip Stage 6.5** (there are no SSIDs/clusters to decide) and run Stages 7-10 for whatever defaults exist; on `no`, end with the Act I report. (`edit-context` is not offered — there are no detected facts to correct.)

On `yes` (GO / PARTIAL) → proceed to **Stage 6.5** (the target-architecture questionnaire), then Stage 7. On `yes` (EMPTY-SOURCE) → skip Stage 6.5, go straight to Stage 7.
On `no` → end the session with the Act I report unchanged.
On `edit-context` → operator names which detected Stage 1 source fact to correct (one that changes the verdict), the AI updates the audit context, re-runs Stage 3 + Stage 6, re-emits the Act I report, and re-emits the gate prompt. Target-architecture *choices* (forward mode, topology) are NOT made here — they're the Stage 6.5 questionnaire.

Do NOT run Stage 6.5 or Stages 7-10 silently or pre-emptively.

---

### Stage 6.5 — Target-architecture questionnaire (DECIDE-01)

Runs only after the operator answers `yes` at the gate (non-BLOCKED verdict). This is the skill's one configuration interview, and it is deliberately **after** the readiness verdict: the operator first learns whether the devices are Central-ready, then decides the target architecture. Stage 2 detection (including the cluster-mode recommendation derivation, which runs there — not deferred to Stage 7) supplies the **defaults**; the operator confirms or changes each. Ask via `elicit()` (the same mechanism as the Stage -2 data-source question). Keep it adaptive — only ask what's relevant.

**Precondition — inventory coverage.** Stage 6.5 needs `virtual_ap` + `ssid_prof` (Q1) and `cluster_prof` (Q2). The **offline upload / paste path (Stage 1-ALT) does not collect those** — it parses only `netdst` / `acl_sess` / `role`. So if there are **no translatable VAPs** (offline source, or the API walk genuinely found none): **skip Stage 6.5 entirely** and proceed to Act II for the object classes that *were* collected (policy / role / net-group), emitting a Translation-gaps note — *"Stage 6.5 (SSID forward-mode + gateway-topology decisions) skipped: requires `virtual_ap` / `ssid_prof` / `cluster_prof` coverage, which the offline parser does not provide. Re-run on the API path (or paste a full `show configuration effective` covering WLAN) to drive the SSID/cluster translations."* Do not ask Q1/Q2 against an empty VAP set.

**Question 1 — per-virtual-AP forward mode (always).** Ask once **per `virtual_ap` instance**, NOT per ESSID — multiple VAPs can broadcast the same ESSID at different scopes (e.g. one `CORP` VAP per region) and each is its own profile with its own forward mode. Key every decision by the **composite identity `<source_scope>/<vap-name>`** so same-named VAPs across scopes never collide. (`Bridged and Tunneled` is the distinct case where *one* VAP intentionally becomes two profiles sharing an essid alias — that's a single decision with a scope split, not two VAPs.) A VAP is **translatable** (and so gets a question) when it matches the Stage 9b 2g preview filter **exactly**: not `_flags.system`, not `_flags.default`, and its `virtual_ap.ssid_prof` reference resolves to an `ssid_prof` **at the VAP's OWN `_source_scope`** — the same scoped join 2g uses (`s._source_scope == vap._source_scope`), NOT merely "exists somewhere in the collected list" (a same-name profile at another scope that 2g won't use). Skip system/default VAPs and ones whose SSID profile is missing **at their scope** — do NOT ask the operator about records the preview loop will skip; note them under Translation gaps (e.g. *"VAP `<scope>/<name>` references ssid-profile `<x>` not present at that scope — not translatable"*). For each translatable VAP, present its detected current mode + the recommended AOS 10 target, and ask the operator to pick one of:

| Option | Meaning | Drives `wlan_ssid` `target_mode` |
|---|---|---|
| **Bridged** | AP local breakout; no gateway | `bridged` |
| **Tunneled** | gateway-terminated | `tunneled` |
| **Bridged and Tunneled** | the same SSID in BOTH modes across locations (campus tunneled, branches bridged) → essid alias + two profiles | `bridged_and_tunneled` (also ask the bridge-vs-tunnel **scope split** — detected default, operator adjusts → collect each scope's **identity** `bridge_scope_name`+`bridge_scope_type` / `tunnel_scope_name`+`tunnel_scope_type` (+path when known), resolved to ids/`<TBD>` in 9b — a bare name isn't unique) |
| **Hybrid** | split-tunnel (one SSID, corporate tunneled + Internet local) | `hybrid` |

**Display label → engine value (do not confuse the two):** the left column is the operator-facing label; the **right column is the exact string that must go into `runtime_values["target_mode"]`** — `Bridged`→`bridged`, `Tunneled`→`tunneled`, `Bridged and Tunneled`→`bridged_and_tunneled`, `Hybrid`→`hybrid`. Store/pass the lowercase engine value, never the display label (the engine rejects unknown `target_mode` strings). Same for the Stage 3 re-score vocabulary mapping (`tunnel`/`bridge`/`mixed` blocks) at the re-score step.

Pre-fill the recommendation from the detected `forward_mode` (`tunnel`/`decrypt-tunnel`→Tunneled, `bridge`→Bridged, `split-tunnel`→Hybrid). The operator may pick anything — e.g. flipping every SSID to **Bridged** to go controllerless. The source tells us what *is*; the operator decides what they *want*.

**Question 2 — gateway topology (only if any SSID is Tunneled / Hybrid / Bridged-and-Tunneled).** Skip entirely if every SSID is Bridged (no gateways survive → no clustering). Otherwise present the detected topology (from Stage 2 detection — the SSID→cluster map + the cluster-mode recommendation derivation) and ask:

| Option | `gateway_cluster` `cluster_strategy` | Scope |
|---|---|---|
| **Campus gateways, no DMZ clusters** | `intent_site` | global / site / site-collection |
| **Campus gateways + DMZ clusters** | `intent_site` (campus) **and** `intent_manual` (DMZ) | site/site-collection + device-group |
| **DMZ controllers only (few)** | `ha_only` | device-group |

Default the selection to the detected pattern (same-ap-group-to-different-clusters → "campus + DMZ"; single regional cluster → "no DMZ"; few/DMZ-only → "DMZ only").

**Strategy and placement are separate — collect both.** The topology option above fixes the `cluster_strategy`; it does NOT fix *where* the cluster lands. For each surviving cluster, also confirm the **intended Central scope identity** — collect the scope **name AND type** (`target_scope_type` ∈ `global` / `site` / `site_collection` / `device_group`), plus the **full path** (`target_scope_path`, e.g. `USW/West`) when the operator can give it. A bare scope *name* is **not** globally unique (a Site, Site-Collection, and Device-Group can share a name; the same name can recur under different parents), so name-only resolution can bind the wrong scope — always carry the type, and prefer the path. Collect the identity, **not** a numeric `scope_id` (the Central scope may not exist yet — Stage 7 maps/creates the hierarchy as the first cutover step), so resolution → `scope_id`/`<TBD:...>` happens later in Stage 9b. Record `cluster_strategy` + `target_scope_name` + `target_scope_type` (+ optional `target_scope_path`) in `decisions["per_cluster"]`, keyed by the composite **`<source_scope>/<cluster-name>`** (a bare cluster name would apply one cluster's decision to another scope's cluster). Stage 9b calls `resolve_scope_id(target_scope_name, target_scope_type, target_scope_path)` → `scope_id` / `<TBD:...>` / `<AMBIGUOUS:...>` (when name+type still match several — the operator must supply a path) and **never** defaults a *missing* scope to Global — a cluster with no chosen scope skips with a `skip_reason`.

**Outputs → Act II preview inputs.** Record the answers and feed them into the Stage 9b previews — the per-VAP `target_mode` + cluster decisions drive the `translate_wlan_preview` (§2g) params, and the per-cluster `cluster_strategy` becomes `translate_config_preview`'s `extra_ctx` (§2f):

```
decisions = {
  # keyed by composite "<source_scope>/<vap-name>" — NOT bare vap-name / ESSID,
  # so same-ESSID VAPs across scopes can't collide.
  "per_vap": { "<source_scope>/<vap-name>": {"target_mode": "...",      # Q1
                                             # cluster_refs holds the composite per_cluster keys this VAP
                                             # tunnels to — for collision-safe LOOKUP only (NOT the engine
                                             # payload). 2g resolves each via per_cluster into the Central
                                             # overlay gw_cluster_list object shape before previewing.
                                             "cluster_refs": ["<source_scope>/<cluster-name>", ...],
                                             # dual-mode scope split: scope IDENTITY (name+type, +optional
                                             # path) resolved to ids/<TBD> in 9b — like target_scope_*; a
                                             # bare name isn't unique, so carry the type:
                                             "bridge_scope_name": "...", "bridge_scope_type": "...",  # +bridge_scope_path? (dual only)
                                             "tunnel_scope_name": "...", "tunnel_scope_type": "..."}, # +tunnel_scope_path? (dual only)
               ... },
  # keyed by composite "<source_scope>/<cluster-name>" — same collision-safety as per_vap.
  # Scope IDENTITY (name + type, +optional path), resolved to scope_id/<TBD> in 9b — a bare
  # name isn't unique across types/parents, so carry the type (and a path when known).
  "per_cluster": { "<source_scope>/<cluster-name>": {"cluster_strategy": "...",
                                                     "target_scope_name": "<scope-name>",
                                                     "target_scope_type": "global|site|site_collection|device_group",
                                                     "target_scope_path": "<optional/full/path>"} },  # Q2
}
```

**Re-score the provisional findings (bucket 4) against the chosen architecture.** After the operator answers, re-evaluate **every** bucket-4 finding — the per-target-mode Tunnel / Bridge / Mixed blocks, F3 / F4, **and the Stage 4a NAD checks A4 / A5** — against each SSID's **chosen** `target_mode` (and, for A5, the surviving gateway clusters) — not the recommendation. The Stage 3 rule blocks use the vocabulary `tunnel` / `bridge` / `mixed`; the Stage 6.5 answers use `bridged` / `tunneled` / `hybrid` / `bridged_and_tunneled`. Normalize per SSID before re-scoring:

| Stage 6.5 `target_mode` | Stage 3 block(s) to apply |
|---|---|
| `tunneled` | the **Tunnel** block (+ F3/F4 where their tunnel-target severity applies) |
| `bridged` | the **Bridge** block (+ F3/F4 bridge-target severity) |
| `hybrid` (split-tunnel) | the **Mixed** block + any split-tunnel-specific rules |
| `bridged_and_tunneled` | **both** the Bridge block (at the bridge scope) **and** the Tunnel block (at the tunnel scope) — it's two real profiles |

**F3 / F4 are deployment-level, not per-SSID** (L3 Mobility being load-bearing; VC-managed NAT'd WLANs depending on controller-side NAT/DHCP). Their original aggregate gate was `{bridge, mixed}` = "some traffic bridges locally." Post-questionnaire, re-trigger them as **REGRESSION if ANY SSID's chosen mode bridges traffic locally** — `bridged`, `hybrid` (split-tunnel keeps Internet local), or the bridge half of `bridged_and_tunneled`. If **every** SSID is pure `tunneled`, F3 downgrades to DRIFT and F4 does not apply (all client traffic terminates on the gateway). Evaluate F3/F4 once over the whole set of chosen modes, not per SSID.

The old **aggregate** `mixed` (a whole-deployment "some SSIDs tunnel, some bridge" recommendation) only existed pre-questionnaire to gate the provisional preview; post-questionnaire there is no aggregate mode — per-target-mode block re-scoring is strictly **per SSID** by the table above, so a deployment with a mix of bridged + tunneled SSIDs is just each SSID scored under its own block (no SSID is "mixed" unless it's `hybrid`/split-tunnel). Findings whose mode the operator chose away from simply disappear; findings that still apply fold into the Act II disposition matrix / Translation gaps for the chosen design. This re-score does **not** re-open the Act I verdict (that gate already passed on source-readiness); it informs the *plan*. If it surfaces a hard REGRESSION for the architecture the operator just chose, state it plainly and offer to revisit Stage 6.5 (e.g. *"your chosen Tunnel mode for `CORP` still has REGRESSION X; pick a different mode for it, or proceed and handle X manually"*) — the operator decides, having been told.

If verdict was EMPTY-SOURCE (no SSIDs/clusters), skip Stage 6.5 — there's nothing to decide — and proceed to Stage 7 for whatever defaults exist.

---

### Stage 7 — Hierarchy translation (TRANSLATE-01)

Promote the readiness-stage hierarchy mapping table (Stage 6 inventory section) into a translation stage with explicit rules. Reuse the Stage 1 COLLECT-01 effective-config or pasted `show configuration node-hierarchy` output already in context — do NOT re-fetch.

**Resolving Stage 7 mapping rows to Central `scope_id`s:** when Stage 9's API call sequence needs a `scope_id` (e.g. for `central_manage_config_assignment`), use the `central-scope-walker` skill — paste the operator-confirmed Central name (`USE`, `dallas-hq`, etc.) into its snippet to get the `scope_id` plus parent path. Don't author tree-recursion in `execute()`; the walker is a one-shot primitive that handles exact name / path / scope_id / substring matches uniformly.

**Stage 7 mapping contract (each row carries a full scope IDENTITY, not just a name).** Because a bare Central scope name is not unique (Sites / Site-Collections / Device-Groups can share a name; names recur under different parents — see Stage 9b's `resolve_scope_id`), every Stage 7 mapping row must retain enough to resolve unambiguously: the **Target name**, the **Target type** (the row's Site / Site-Collection / Device-Group classification), AND the **full Central path** derived from the confirmed hierarchy (e.g. `USW/West`). Stage 9b's `stage7_central_scope_for(<source_scope>)` returns that identity as `{"name", "type", "path"}` and resolves by path → name+type. Do NOT collapse a mapping row to a bare name — that's how the cross-scope-collision bug gets rebuilt.

**Rules** (anchor: VSG §1529-§1535 *"Mapping AOS-8 Hierarchy to AOS-10 Configuration Model"* + §1834-§1835; Central scope semantics per the Aruba Central VSG *Configuration Model* section).

AOS 10 / Central has **5 scopes**: `Global` (implicit root), `Site Collection`, `Site`, `Device`, and `Device Group`. The first four form a top-down hierarchy (`Global → Site Collection → Site → Device`); `Device Group` is parallel and lets administrators logically group devices outside the hierarchy. **Personas are NOT a scope** — they are filtered via a separate dimension called **Device Functions** (Campus Access Point, Mobility Gateway, VPNC, Microbranch, Core Switch, Aggregation Switch, Access Switch, etc.) that limit which device types receive a profile within a given scope. Earlier revisions of this skill incorrectly described "device persona scope" as a fifth placement; that was wrong, and Stage 7 now uses Device Functions to filter rather than as a target placement.

The skill produces a draft classification per `/md/<path>` Group node using the rules below; **operator confirms low-confidence rows before Stage 7 emits its final mapping.**

**Step 1 — Drop conductor / mobility-manager scope:**
- `/md` → `drop` (Central org root is implicit; root-defined objects become Global-scope assignments — see *Per-scope configuration inventory* below)
- `/mm` and descendants → `drop` (Mobility Manager scope; not part of the migrated tree)

**Step 2 — Determine the Device Function for each Device child** by cross-referencing the Stage 1 inventory (`aos8_get_controllers`, `aos8_get_ap_database`, controller-model lookups). Device Functions in scope for the wireless-focused migration:
- `MOBILITY_GW` (Mobility Gateway) — WLAN gateway. **Default for AOS 8 Mobility Controllers (MDs).**
- `VPNC` — VPN Concentrator. Never has APs. Rare in 8.x.
- `BRANCH_GW` (Branch Gateway) — SD-Branch CPE. Never has APs. Rare in 8.x.
- `MICROBRANCH_AP` — Microbranch / RAP.
- `CAMPUS_AP` (Campus Access Point) — typical campus AP.

Out-of-scope Device Functions (`ACCESS_SWITCH`, `AGG_SWITCH`, `CORE_SWITCH`, `BRIDGE`, `HYBRID_NAC`) — flag the row as `out-of-scope (wired/NAC migration not in this skill)` and skip.

The Device Function travels with the device into Central; profiles assigned at any scope can be filtered to a Device Function so they apply only to (e.g.) the Mobility Gateways at that Site, not the switches.

**Step 3 — Classify each Group node by structure + naming + persona** (rules in priority order; first match wins):

| Signal | Inferred placement | Confidence | Notes |
|---|---|---|---|
| Has child Group nodes (no Devices directly) | Site Collection | high | structural — pure container |
| Plural noun in node name (`Branch_Sites`, `Stores`, `Floors`) | Site Collection | medium | naming heuristic; operator confirms if children later contradict |
| `_Static` suffix in name | Device Group | medium | naming heuristic for config-pinned device groupings |
| Children include APs (CAMPUS_AP or MICROBRANCH_AP) | Site (auto-clustering re-enabled in AOS 10) | high | AP-bearing scopes always become Sites |
| Persona token in name (`VPNC`, `BGW`, `Microbranch`) AND children uniformly that persona | Device Group, with **Device Function** = the persona token (VPNC / BRANCH_GW / MICROBRANCH_AP) | medium | VPNC/BRANCH_GW never have APs; Device Function filters which device types receive profiles |
| Children uniformly MOBILITY_GW (no APs — DMZ pattern) AND cluster_prof present at scope | apply the Stage-6.5-confirmed cluster mode (recommended via the Step-4 derivation in Stage 2 detection); CM_SITE → Site, CM_MANUAL → Device Group | medium | DMZ MGW cluster pattern |
| Geographic / cardinal noun (`East`, `West`, `Dallas`, three-letter region codes) at leaf or near-leaf | Site | high | naming heuristic for true sites |
| No matching signal | Device Group (default fallback) | low | operator review required |

**Step 4 — Cluster-mode recommendation derivation (algorithm definition; RUNS in Stage 2 detection, APPLIED here in Stage 7):**

> **Ordering note (data dependency):** this derivation is the source of the Stage 6.5 Q2 *defaults*, and Stage 6.5 runs **before** Stage 7. So the algorithm below is **executed during Stage 2 detection** (it reads only Stage 1 data — `config_by_scope`, `ap_database`, `ap_multizone_prof` — all available then), producing the per-cluster `cluster-mode recommendation`. Stage 7 does **not** re-derive it: by the time Stage 7 runs, the operator has already confirmed/overridden the recommendation in Stage 6.5, and Stage 7 **applies that confirmed decision** to hierarchy placement. The algorithm is documented here only because Stage 7 is its conceptual home; nothing about it requires Stage 7 to have run.

AOS 8 has no `cluster-mode` knob. The AOS 10 cluster-mode (`CM_SITE` / `CM_MANUAL`) is **derived** from three Stage 1 signals to produce the per-cluster *recommendation* that pre-fills the Stage 6.5 gateway-topology question — the operator confirms or overrides it there (CM_SITE primary-zone + CM_MANUAL DMZ-anchor together = the "campus + DMZ" topology option). Signals, all already in `config_by_scope`:

1. `cluster_prof.cluster_controller[].ip` — cluster member IPs (from COLLECT-01). **Use the `ip` field, NOT `vrrp_ip`** — AP `Switch IP` / `Standby IP` is the per-controller management address (matches `cluster_controller[].ip`); `vrrp_ip` is the VRRP virtual address and never appears as an AP's adoption target. Live-verified against AOS 8.13 cluster_prof — see [issue #270](https://github.com/nowireless4u/hpe-networking-mcp/issues/270).
2. `ap_database.Switch IP` and `ap_database.Standby IP` — each AP's adoption controller (from COLLECT-02)
3. `ap_multizone_prof.controller[].ip` — multizone tunnel anchor IPs per AP-group (from COLLECT-01)

**Iterate EVERY deduped cluster_prof in `inventory["cluster_profiles"]`** — emit one row per profile. The Stage 2 normalization already filtered `_flags.inherited == True` entries; do not skip, dedupe-by-name, or short-circuit on the first profile. AOS 8 commonly carries multiple distinct cluster_profs at sibling scopes (e.g. an `East` cluster at `/md/Campus` PLUS a `site-cluster` at `/md/Campus/West`); the AP's adoption controller may match the second one even when the first is "closer" alphabetically.

Skip any cluster whose `cluster_controller[].ip` set includes the Mobility Conductor's own management IP — clusters are between MDs, not MM.

```python
for cluster_prof in inventory["cluster_profiles"]:           # iterate ALL — see note above
    member_ips = {c["ip"] for c in cluster_prof["cluster_controller"]}

    if conductor_mgmt_ip in member_ips:
        continue                                             # MM is not a cluster member

    # Primary zone test
    primary_aps = [
        ap for ap in ap_database
        if ap.get("Switch IP") in member_ips
           or ap.get("Standby IP") in member_ips
    ]

    if primary_aps:
        cluster.aos10_mode = "CM_SITE"
        cluster.aos10_target = "Site"
        cluster.notes = f"primary zone for {len(primary_aps)} APs"
    else:
        cluster.aos10_mode = "CM_MANUAL"
        cluster.aos10_target = "Device Group"
        # Enrichment: distinguish multizone anchor from DMZ
        multizone_for = [
            ag["profile-name"] for ag in ap_groups_in_use
            if ag.get("ap_multizone_prof", {}).get("profile-name")
            and any(
                c["ip"] in member_ips
                for c in resolve_multizone_prof(ag["ap_multizone_prof"]["profile-name"]).get("controller", [])
            )
        ]
        cluster.notes = (
            f"tunnel anchor (multizone data zone) for AP-groups: {multizone_for}"
            if multizone_for
            else "active cluster with no APs adopted (DMZ pattern or unused)"
        )

    cluster.aos10_scope = cluster.origin_scope               # /md/<region>/<site> per Stage 1 hierarchy walk
```

**Why this works:** AOS 8 multizone splits an AP's traffic across multiple controllers — the *primary zone* is the cluster the AP is adopted to (determined by `Switch IP` / `Standby IP`), and *data zones* are additional clusters acting as tunnel anchors for specific VAPs. AOS 10 represents primary zones as Sites with auto-clustering (`CM_SITE`); data-zone anchors and unused-active clusters become Device Groups (`CM_MANUAL`). The decision is binary and fully derivable.

**External multizone targets** (a multizone profile references a controller IP that is NOT in any source `cluster_prof` AND NOT in the conductor's `aos8_get_controllers` list) emit a separate INFO finding in Stage 8:

> *"AP-group `<X>` multizone profile `<Y>` references `<ip>` — not in any source `cluster_prof`, not managed by this conductor. External standalone controller; migrates to a single Central gateway, not a `gw-cluster`. Operator confirms placement."*

Multizone targets that ARE managed by this conductor but aren't part of any cluster (a non-clustered MD) emit no finding — they translate normally as single Central gateways elsewhere in the disposition matrix.

**Output:** the existing 3-column hierarchy table from the Stage 6 readiness report is **promoted to a 9-column translation table** that captures the inferred placement, persona, cluster signal, confidence, and target name:

| Source AOS node | Source path | Disposition | Target type (AOS 10) | Inferred Device Function | Cluster mode signal | Target name (operator-named) | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|
| `<Mobility Conductor /md>` | `/md` | `drop` | (none) | n/a | n/a | n/a | high | Central org root is implicit |
| `<region with child Groups>` | `/md/USE` | `direct-translate` | Site Collection | n/a (container) | n/a | `USE` | high | child Group nodes present |
| `<plural-named region>` | `/md/Branch/Branch_Sites` | `direct-translate` | Site Collection | n/a (container) | n/a | `Branch_Sites` | medium | plural-noun naming heuristic |
| `<site with APs adopted to cluster X>` | `/md/USE/dallas-hq` | `direct-translate` | Site | CAMPUS_AP | CM_SITE (derived: primary zone for N APs) | `dallas-hq` | high | AP children + cluster_prof matched via Switch IP |
| `<DMZ cluster — no APs adopted, multizone anchor>` | `/md/DMZ` | `direct-translate` | Device Group | MOBILITY_GW | CM_MANUAL (derived: multizone anchor for `<ap-group>`) | `DMZ-MGW-Cluster` | medium | cluster_prof present, no Switch IP match, multizone reference found |
| `<active cluster — no APs, no multizone reference>` | `/md/StagingCluster` | `direct-translate` | Device Group | MOBILITY_GW | CM_MANUAL (derived: active cluster, no APs adopted, no multizone reference) | `Staging-MGW-Cluster` | medium | cluster_prof present, no APs, no multizone — DMZ or unused |
| `<persona-named VPNC node>` | `/md/Branch/Branch_VPNC` | `direct-translate` | Device Group | VPNC | n/a (no cluster_prof) | `Branch_VPNC` | medium | VPNC token in name; no APs — Device Group with Device Function = VPNC filters which device types receive profiles |
| `<_Static-suffix node>` | `/md/Branch/Branch_Sites_Static` | `direct-translate` | Device Group | MOBILITY_GW | n/a | `Branch_Sites_Static` | medium | `_Static` suffix → device group |
| `<unsignaled node>` | `/md/Foo123` | `inconclusive — operator confirm` | Device Group (default) | n/a | n/a | (operator names) | low | no naming or structural signal — operator review required |

**AOS 10 / Central scope notation:** Central has **no `/md/` prefix** in its scope tree. The five Central scopes are `Global` (implicit root), `Site Collection`, `Site`, `Device`, and `Device Group`; the first four form the top-down hierarchy and Device Group is parallel. Whenever this skill references a scope in the **Target name** column, `X` is the AOS 10 / Central name (operator-confirmable), NOT the AOS 8 source path. Source paths (`/md/...`) appear only in the **Source path** column for cross-reference. The **Inferred Device Function** column is a filter dimension (Campus Access Point, Mobility Gateway, VPNC, etc.), not a scope.

**Skip / inconclusive:** if Stage 1 paste-fallback was used and node hierarchy was not pasted, mark each row's disposition `inconclusive — paste required` and emit one INFO finding noting the gap.

#### Per-scope configuration inventory (REQUIRED — emit alongside the mapping table)

The mapping table above shows *where* each AOS 8 node lands in Central. The operator also needs to know *what configuration objects live at each scope* so they can plan per-scope translation work. Without this, the operator has the destination but no manifest of what travels there.

Iterate `inventory["scopes"]` (Stage 2 normalization output, with `_flags.inherited == True` rows already filtered) and for each scope emit one row counting the **definition-scope** instances of every object class collected in COLLECT-01. **Inherited copies do not count** — they live at their definition scope and travel with it.

```
| Source scope | AOS 10 target | cluster_prof | ssid_prof | virtual_ap | role | acl_sess | server_group_prof | rad/tacacs/ldap | dot1x | mac_auth | cp_auth | ap_sys_prof | rf_prof family (arm/ht_radio/reg_domain) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `/md` | (drop — root implicit) | 0 | … | … | … | … | … | … | … | … | … | (definitions present here, e.g. `ACX_apsys_ui`) | … |
| `/md/<region>` | `<region>` (Site Collection) | … | … | … | … | … | … | … | … | … | … | … | … |
| `/md/<region>/<site>` | `<site>` (Site, CM_SITE) | (definition rows only — e.g. `site-cluster`) | … | … | … | … | … | … | … | … | … | … | … |
```

For each non-zero cell, emit a follow-up bullet listing the object **names** (not just counts) so the operator can spot which scope owns which named profile. Example:

> `/md/Campus/West` → `West` Site:
> - cluster_prof (1): `site-cluster`
> - ap_sys_prof (1): `west-aps`
> - acl_sess (2): `guest-preauth`, `Windows-Policy`

Object names are the source-of-truth artifacts the operator carries forward into Stage 8's per-object translation matrix; this per-scope view is the index from "Stage 7 placement" to "Stage 8 row".

When `/md` (root) carries customer-defined objects (e.g. `ap_sys_prof: ACX_apsys_ui` defined at root in the operator's transcript), call it out explicitly — the AOS 10 root is implicit and there is **no** Central scope to pin those to. Each root-defined object becomes a `(global)`-scope row in Stage 8 OR an operator decision to re-pin it under a specific Site / Device Group at translation time. Flag this as `OPERATOR-MAP — /md root carries definitions; Central root is implicit; choose target scope for each.`

**Findings produced:**

- For every proposed target name (Site Collection / Site / Device Group), check it against the Stage 4 Central scope-tree response. If a same-named node already exists at the same level: emit `DRIFT — proposed Site name '<X>' already exists in Central scope tree as <type>; rename or merge before translation.` (One finding per collision.)
- If the source `/md` tree exceeds the AOS 10 *"per-Site Collection limits"* (out of scope per VSG; operator may need to flatten), emit one INFO bullet flagging the operator decision.

---

### Stage 8 — Per-object translation matrix (TRANSLATE-02)

For **every AOS 8 object discovered in Stage 1's full hierarchy walk** (regardless of whether it is in active use, assigned, referenced, or orphaned), emit one row of the disposition matrix. **Reuse Stage 1 collected data already in context** — do NOT re-fetch.

**Critical principle (this is the rule, not a guideline):** the customer's running config is the source of truth. Whether something is "in use" today is metadata on the row (`usage_state` column), not a basis for excluding it from the migration plan. Orphaned AAA server groups, unassigned captive portal profiles, AP system profiles configured but not bound to any AP group — every one gets a row.

#### Central scope placement: precedence + additive rules

When deciding which AOS 10 / Central scope each translated object lands in, apply these Central scope semantics (per the Central VSG *Configuration Model* section):

- **Hierarchy + propagation.** Objects assigned at one scope propagate down: `Global → Site Collection → Site → Device`. `Device Group → Device` is a parallel propagation path. An object at Global reaches every site collection / site / device; at Site Collection it reaches member sites + devices; at Site it reaches devices in that site; at Device it reaches only that device.
- **Configuration precedence (single-value profiles).** When the same profile is assigned at multiple scopes, the more-specific scope wins:
  ```
  Device > Device Group > Site > Site Collection > Global
  ```
  Precedence applies at the **profile level**, not the individual parameter level. The single profile at the highest-precedence scope is what gets pushed; lower-scope assignments are not "merged in."
- **Additive profiles** (WLAN, VLAN, role, security policy). Assignments at multiple scopes **add together** rather than overriding. A Global WLAN `OWL_EMPLOYEE` plus a Site Collection WLAN `BRANCH_GUEST` plus a Site WLAN `BRANCH3_CONTRACTOR` results in all three being broadcast at devices under that site.
- **Device Functions filter within a scope.** A profile assigned to a scope can be limited to specific Device Functions (e.g. Mobility Gateway, Campus Access Point, VPNC) so only matching device types receive it. Device Functions are NOT a scope — they're a filter dimension applied on top of any scope assignment.

**Default placement strategy for the disposition matrix:** place each AOS 8 object at the **lowest Central scope that preserves its source intent**. Concrete defaults:

- AOS 8 object defined at `/md` root and applied broadly → Central **Global** scope (additive profiles like WLAN/role). For non-additive shared objects (e.g. an AP system profile defined at root), default to Global with an `OPERATOR-MAP` flag asking the operator whether to push it down to specific Sites / Device Groups.
- AOS 8 object defined at `/md/<region>` (a Site Collection in the Stage 7 mapping) → **Site Collection** scope.
- AOS 8 object defined at `/md/<region>/<site>` (a Site) → **Site** scope.
- AOS 8 object defined at an AP-group node → **Device Group** scope when the operator has a same-named Device Group in the Stage 7 mapping; otherwise Site scope with a Device Function filter.
- Device-individual overrides (rare in AOS 8) → **Device** scope.

When an AOS 8 object is duplicated at multiple sibling scopes (same name and content at `/md/<regionA>` AND `/md/<regionB>`), the operator can choose to **promote** it to the parent (e.g. Global) so it propagates everywhere. The disposition row notes the duplication and emits `OPERATOR-MAP — duplicated across N sibling scopes; consider promoting to parent for single source of truth.`

#### 8.1 — Disposition rules per object type

The VSG **does not** contain per-object translation tables for most object types. The deepest concrete rules live in two worked SSID examples (CorpNet 802.1X at VSG §2127-§2219, OpsNet WPA3-Personal at §2222-§2308) plus the gestural feature-comparison table for AOS 8 (§1121-§1175). Outside those anchors, dispositions for AAA / roles / ACLs / AP profiles are marked `operator-driven` with `vsg-anchor: none` — the skill does not fabricate VSG citations.

| Object type | VSG anchor | Disposition guidance |
|---|---|---|
| **AAA RADIUS server** (`rad_server`) | §1121-§1141 | `transform` — IP / port / shared-secret carry over; NAS-IP source must change per target mode (Tunnel = gateway IP; Bridge = AP subnet; Mixed = both). VSG describes the source-IP shift; field-mapping into Central is operator-driven. **Central API gap — no `central_manage_server` tool exists today.** Mark target tool as `[Central API gap — manual UI: Network Services → Servers]`. |
| **AAA TACACS server** (`tacacs_server`) | (none) | `operator-driven` — VSG has no TACACS translation rule. Emit `OPERATOR-MAP` finding. **Central API gap — no manage tool.** Target tool: `[Central API gap — manual UI]`. |
| **AAA LDAP server** (`ldap_server`) | (none) | `operator-driven` — VSG silent. **Central API gap.** |
| **AAA FastConnect / EAP-Offload** | §1137-§1141 | `drop` — *"Not supported."* If active, emit `REGRESSION — AAA FastConnect / EAP-Offload in use; plan ClearPass-only EAP termination.` (Cross-link to Act I rule F1.) |
| **AAA server-group** (`server_group_prof`) | §2076-§2092 (worked example) | `transform` — group name + ordered server list. **Central API gap — no `central_manage_server_group` tool.** Target tool: `[Central API gap — manual UI: Network Services → Server Groups]`. |
| **802.1X auth profile** (`dot1x_auth_profile`) | §1121-§1141 + §2159-§2208 (CorpNet 802.1X worked example) | `operator-driven` — folded into WLAN profile creation in Central; ESSID is in the WLAN SSID profile, allowed-bands and VLAN ID are in the VAP (collapsed into the WLAN profile in Central), key-management is in the SSID profile, primary/secondary RADIUS pointers are under authentication servers. No automatic field map; emit `OPERATOR-MAP`. Target tool: `central_manage_wlan_profile` (the auth profile is collapsed into it). |
| **MAC-auth profile** (`mac_auth_profile`) | (none) | `operator-driven` — VSG silent. Emit `OPERATOR-MAP`. Target tool: `central_manage_wlan_profile` (mac-auth opmodes are flags inside it). |
| **Captive portal profile** (`cp_auth_profile`) | (none, passing mention only) | `operator-driven` — assigned through a role's `captive-portal` field on `central_manage_roles`. Emit `OPERATOR-MAP`. Target tool: `central_manage_roles` (captive-portal field). |
| **User role** (`role`) | §1173-§1176 (AOS 8 supported-features list) | `transform` — role name + VLAN + ACL + bandwidth-contract + qos + captive-portal + session-timeout map directly. Per-attribute mapping is operator-driven; VSG only confirms roles "are supported." Emit `OPERATOR-MAP` per role. Target tool: `central_manage_roles`. |
| **Session ACL** (`acl_sess`) | (none — implied via role) | `transform` — the `central:policy` translation (engine-driven) emits `/policies` POSTs with rule bodies that reference Central `net-group` and `net-service` aliases. `net-group` aliases ship via the `central:net_group` translation (see the row below — sourced from AOS 8 `netdst` / `netdst6`). `net-service` aliases (sourced from AOS 8 `netsvc`) are **deferred** pending live shape verification; `central:policy` rules that reference a `netsvc` name today will fail at Central with an unknown-service error unless the operator has pre-populated matching service names. Per-rule mapping is engine-handled; operator decisions only when LLD-skip reasons surface. (Note: `acl_eth` and `acl_mac` are intentionally out of scope — issue #298.) Target tool: `central_manage_policies`. |
| **Network destination alias** (`netdst`, `netdst6`) | (none) | `transform` — the `central:net_group` translation emits one `POST /net-groups/{name}` + config-assignment per source record. Per-entry mapping is engine-handled (host / network / FQDN → Central `HOST` / `NETWORK` / `FQDN` items). Must run BEFORE `central:policy` because policy rule bodies reference these aliases by name. AOS 8 system defaults (`_flags.default=true` — e.g. `localip`, `controller`, `mswitch`) are filtered per-entry by the reader; record-level inherited/default copies must be filtered by the consumer at definition scope. (Note: AOS 8 `netsvc` — service aliases — is deferred to a future release; see the `acl_sess` row.) Preview via `translate_config_preview` (`kind="net_group"`); apply via `translate_config_apply`. |
| **AP system profile** (`ap_sys_prof`) | §1651-§1657 (LMS prerequisite), §412-§415 (regulatory domain replaced) | Mixed: LMS-IP `transform` (must be VRRP VIP, not individual controller IP — already enforced as Act I REGRESSION rule); `reg_domain_prof` `deprecated`; `arm_prof` / `ht_radio_prof` `deprecated` (replaced by RF Profiles in AOS 10); syslog targets `operator-driven` (mapped to Central UI). **Central API gap — no `central_manage_ap_system_profile` tool today.** Target tool: `[Central API gap — manual UI]`. |
| **WLAN SSID profile** (`ssid_prof`) | §2127-§2219 (CorpNet 802.1X), §2222-§2308 (OpsNet WPA3-Personal) | `direct-translate` — ESSID, opmode, VLAN, forwarding-mode, key-management, RADIUS pointers map to the `central_manage_wlan_profile` payload schema. The two VSG worked examples are the gold-standard reference for field-by-field mapping; emit per-WLAN-profile rows that cite them. Target tool: `central_manage_wlan_profile`. |
| **VAP profile** (`virtual_ap`) | §2169-§2192 (Allowed bands "in the VAP", VLAN ID "in the VAP") | `transform` — AOS 8 VAP fields collapse INTO the WLAN profile in AOS 10; VAP is not a standalone object. Mark as `transform → folded into WLAN profile`. Target tool: `central_manage_wlan_profile` (collapsed). |
| **MAC randomization handling** (per-SSID) | (none) | `operator-driven` — flag as a known AOS 10 behavioural difference. VSG does not address. Emit `OPERATOR-MAP`. |
| **ARM / HT radio / Regulatory Domain profiles** (`arm_prof`, `ht_radio_prof`, `reg_domain_prof`) | §1163-§1166 | `deprecated` — ARM is replaced by **RF Profiles** in AOS 10 / Central. AirMatch already exists in AOS 8 and continues in Central — it is not the AOS 10 ARM replacement. The pre-AOS-8.4 band-split (`dot11a_radio_prof` / `dot11g_radio_prof`) was consolidated into `ht_radio_prof` upstream; the skill collects the single combined object. Already raised as DRIFT in Act I; emit one summary `drop` row per profile family in the matrix. |
| **Cluster profile + group membership** (`cluster_prof`, `group_membership`) | (none — implied via cluster topology) | `transform` — cluster topology and member binding fold into Central GCIS (`gw-cluster-intent` profile + realized `gw-cluster`). The AOS 10 cluster-mode (`CM_SITE` / `CM_MANUAL`) is **recommended** by the cluster-mode derivation during Stage 2 detection (algorithm at Stage 7 Step 4), **confirmed/overridden by the operator in Stage 6.5**, and **applied** here in Stage 7/8. Each cluster_prof becomes a `gw-cluster` profile in Central with its `cluster_controller[].ip` translating to `ipv4-gateways[].mac` (gateways added by MAC; resolve IP→MAC via Central inventory). VRRP / heartbeat / multicast-VLAN fields map directly. Target tools: `central_manage_gw_cluster_intent_config` (intent — sets cluster-mode at scope, persona, multicast VLAN, etc.) + `central_manage_gateway_clusters` (realized profile with explicit member MACs). For CM_SITE clusters, GCIS auto-creates the realized profile (`auto_*` naming); operators only need the intent. For CM_MANUAL clusters, both calls are needed. |
| **ClientMatch tunables** | §416-§418, §1167-§1169 | `deprecated` — *"Settings cannot be tuned."* Already raised as DRIFT in Act I; emit one summary `drop` row in the matrix. |

#### 8.2 — Output: the disposition matrix

Emit a **single master table** with one row per legacy object discovered, **including unused / orphaned / unassigned ones**. Columns:

| Source name | Source type | Source scope | Usage state | Disposition | Target name | Target type | Central tool | VSG anchor | Notes |
|---|---|---|---|---|---|---|---|---|---|

- **Source name** — name as it appears in the source config (`corp-radius-1`, `corp-employee-role`, `corp-ssid-prof`).
- **Source type** — AOS 8 REST schema name (verified against developer.arubanetworks.com/aos8/reference). One of: `rad_server`, `tacacs_server`, `ldap_server`, `server_group_prof`, `dot1x_auth_profile`, `mac_auth_profile`, `cp_auth_profile`, `role`, `acl_sess`, `netdst`, `netdst6`, `ap_sys_prof`, `ssid_prof`, `virtual_ap`, `arm_prof`, `ht_radio_prof`, `reg_domain_prof`, `cluster_prof`, `group_membership`. (Notes: REST schema names differ from CLI nouns — e.g. CLI `netdestination` is REST `netdst`. `internal_db_server` is intentionally absent — Central replaces internal-DB auth entirely; the F2 REGRESSION finding flags local-user migration via the `local-userdb` text dump, not via a REST-object lookup. `acl_eth` and `acl_mac` are also intentionally absent — see issue #298. `netsvc` — AOS 8 service aliases — is also absent pending live-shape verification; once captured, will be added with the corresponding `central:net_service` translation.)
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

> `OPERATOR-MAP — User role 'corp-employee' requires per-attribute mapping. Set role's VLAN, ACL list, captive-portal, session-timeout in the Central role payload. (VSG §1173) (source: aos8_get_effective_config(object_name='role', config_path='/md', entry_type='user'), Batch 1)`

> `OPERATOR-MAP — TACACS server 'tacacs-mgmt' has no automated translation rule. Configure manually in Central UI under Network Services → Servers. (VSG §none) (source: aos8_get_effective_config(object_name='tacacs_server', config_path='/md', entry_type='user'), Batch 1)`

#### 8.4 — Skip / inconclusive

If a Stage 1 batch failed and an object class can't be enumerated, emit ONE row per missing object class with disposition `inconclusive — paste required`, target left blank, notes `*"Stage 1 Batch <N> failed; paste `<exact CLI command>` to enumerate."*`. Do NOT guess at object counts or names.

---

### Stage 9 — Central API call sequence (TRANSLATE-03)

For every row of the Stage 8 disposition matrix where Disposition is `direct-translate` or `transform` AND Central tool is **not** a `[Central API gap]`, compute a topological order respecting these dependency rules:

1. **Hierarchy first.** `central_manage_site_collection` → `central_manage_site` → `central_manage_device_group`. All three must exist before any scoped object.
2. **Cluster intent before realized clusters.** For each cluster_prof from Stage 7: emit `central_manage_gw_cluster_intent_config` (sets cluster-mode, persona, multicast VLAN, heartbeat at the appropriate scope). For CM_SITE clusters this is sufficient — Central GCIS auto-creates the realized `auto_*` cluster profile. For CM_MANUAL clusters, follow with `central_manage_gateway_clusters` to create the realized profile and add member gateways by MAC. Both must precede any object scoped to the cluster's gateways.
3. **ACL primitives before role-acls.** `central_manage_net_groups` BEFORE `central_manage_role_acls` (role ACLs reference net-group aliases). **Net-services are DEFERRED** — `central:net_service` has not shipped (no Stage 8 source row; AOS 8 `netsvc` is not collected). Until it ships, custom service aliases are **operator-pre-populated in Central**; do NOT emit `central_manage_net_services` steps. Built-in `svc-*` services (svc-http/svc-https/…) work today and need no step.
4. **Role-acls before roles.** `central_manage_role_acls` BEFORE `central_manage_roles` (a role's `access-list` field references role-acls by name).
5. **Roles before WLAN profiles** when a WLAN profile references a default role.
6. **WLAN profiles after roles + ACLs** but BEFORE `central_manage_config_assignment`.
7. **`central_manage_config_assignment` last** — assigns the library objects to scopes (Site Collections / Sites / Device Groups). Without this step, objects exist in the Central library but aren't pushed to devices.
8. **`[Central API gap]` rows** — emit as a placeholder step (`[manual UI step]`) at the position they would otherwise occupy in the dependency order. Subsequent steps that would reference the gap-filled object include the literal warning *"depends on prior manual UI step <step #> being completed."*

**Output:** an ordered numbered list. One step per row of Stage 8 matrix where the row produces a Central API call (skip `drop` / `deprecated` / pure `operator-driven` rows that have no API target). Each step includes:

- **Step #**
- **Target object** (e.g. *"Role 'corp-employee'"*)
- **Central tool** (e.g. `central_manage_roles`)
- **Payload sketch** (3-5 key fields; **NOT** a full JSON payload — operators don't need the AI to invent payload details, they need to know which fields matter): *"name='corp-employee', vlan_id=200, access_list_session=['employee-acl'], captive_portal=null"*.
- **Depends on:** comma-separated list of prior step #s (or `none`).
- **Notes** — one short clause per step (operator decisions, gotchas, links to VSG anchor for the disposition).

**Skip:** if all dispositions in Stage 8 are `drop` / `deprecated` / `operator-driven` (zero `direct-translate` or `transform` rows reach a Central tool), output: *"No Central API calls required — the migration is purely a deletion / decommission of legacy features plus operator-driven manual configuration. See the disposition matrix above for manual work items."*

**Findings produced:** none new. Stage 9's value is the ordered plan, not new findings.

---

### Stage 9b — Engine-driven translation preview (TRANSLATE-03b, read-only)

**Run this stage when the operator asks for a deterministic, engine-produced preview of what the migration will emit per object — e.g. "give me a breakdown of what the policies will look like in Central and where they'll land."** Stage 9 (above) is the *narrative* AI-authored API call sequence; Stage 9b is the *deterministic* engine output. Operators reviewing migration impact should read both — Stage 9 for the ordered cutover plan, Stage 9b for the actual JSON bodies and rule-by-rule per-object detail.

**This stage uses the `translate_config_preview` tool** — a read-only bridge to the canonical translation engine that runs server-side and returns the ordered Central calls per object. **Read-only — no API writes** (the gated `translate_config_apply` is the write path). The bridge is **per-record**: one call per source object, returning `{canonical, calls, unresolved, preview}` (call **bodies are omitted** for PII safety — read counts/fields off the PII-safe `canonical` instead). The WLAN SSID preview (§2g) uses the sibling `translate_wlan_preview` tool.

**Preconditions (soft — Stage 9b runs against partial inputs):**

- Stage 1 has collected the AOS 8 inventory (effective-config dump). If the operator jumps straight to Stage 9b without Act I, run a **minimal Stage 1 collection** first — pull `role`, `acl_sess`, `vlan_id`, `vlan_name`, `vlan_name_id`, `netdst`, `netdst6` from the AOS 8 path the operator named (e.g. `/md/Campus/West`). Do NOT do the full Act I hierarchy walk — that's overkill for a preview. **Build the `stage1_<obj>_records` lists via Step 2's `_flatten` even on this path** (so the 2a–2e snippets' variable names resolve and records carry `_source_scope`); a single-scope minimal collection is just a one-entry `config_by_scope`.
  - **This minimal path covers only 2a–2e** (VLANs / roles / policies / net-groups) — the bare-`record_id`, decision-free translations. **Sections 2f (gateway clusters) and 2g (WLAN SSIDs) do NOT run on the minimal path**: they additionally need `cluster_prof` / `virtual_ap` / `ssid_prof` collected **with `_source_scope` stamping across the hierarchy** (Step 2's `_flatten`) *and* the **Stage 6.5 decisions** (`per_vap` / `per_cluster`). Run 2f/2g only after a **full Act I walk + Stage 6.5**; on the minimal path, emit a note that the SSID/cluster previews require the full flow rather than producing empty/"no decision" output. **Section 2h (the AAA chain) also does NOT run on the minimal path** — it needs the AAA objects (`rad_server` / `tacacs_server` / `server_group_prof` / `dot1x_auth_profile` / `mac_auth_profile` / `cp_auth_profile` / `aaa_prof`) collected — but unlike 2f/2g it needs **no Stage 6.5 decision**; run it after a full Act I walk (or extend the minimal collection to pull those kinds).
- Stage 7 has produced the operator-confirmed AOS 8 → Central hierarchy mapping. **If Stage 7 was not run, target Global as a fallback** with a clearly-marked placeholder note in the output (see Step 1 below). The preview is engine output regardless of where the operator plans to land it; making Stage 9b strict on Stage 7 would defeat its purpose.
- The target Central hierarchy does NOT need to exist in Central yet. Stage 9 builds the hierarchy as the FIRST cutover step; Stage 9b previews the per-object work that follows. Walker may legitimately return no match for a Stage-7 Central scope name — in that case use a placeholder scope_id (see Step 1).

**Config kinds shipped today (canonical engine):**

Each is a `kind` passed to `translate_config_preview` (`source_platform="aos8"`, `target_platform="central"`). Kind-specific reader inputs go in `extra_ctx`; the resolved Central scope goes in `scope_id`.

| kind | AOS 8 source | Central target | Notes |
|---|---|---|---|
| `vlan_id` | `vlan_id` (bare or rich) | layer2-vlan profile | Per-record. Optional sub-fields drop when absent. |
| `named_vlan` | composite: `vlan_name` ⨝ `vlan_name_id` on `name` | named-VLAN + alias chain (6 calls) | Composite source — pre-merge before passing one record per name. Optional `extra_ctx["alias_name"]` overrides the default lower-cased alias. |
| `role` | `role` (Gateway-targeted) | role profile + config-assignment | ~25 fields. Skip `_flags.default=true` system roles. |
| `net_group` | `netdst` (IPv4) or `netdst6` (IPv6) | net-group profile + config-assignment | Address family inferred from source record. Per-entry host/network/FQDN mapped to Central HOST/NETWORK/FQDN items. Must run BEFORE `policy`. |
| `policy` | `acl_sess` | /policies POST + policy-group registration + config-assignment | `extra_ctx["role_records"]` (FULL role list) drives the role-attribution reverse-index. References `net-group` aliases by name (created by `net_group`); `net-service` aliases pending. Emits a policy-group-list registration (#420) so the policy is effective; fail-closes unmapped actions to `ACTION_DENY` + flags `unresolved`. |
| `gateway_cluster` | `cluster_prof` | `gateway-clusters` (HA) + `gw-cluster-intent-config` | **Preview wired in §2f.** `extra_ctx["cluster_strategy"]` (`ha_only` / `intent_site` / `intent_manual`) from Stage 6.5 Q2; `scope_id` per cluster. Needs full Act I + Stage 6.5. |
| (WLAN SSID) | `virtual_ap` ⨝ `ssid_prof` (by name) | `wlan-ssids` (+ `overlay-wlan` cluster binding) | **Preview wired in §2g via the separate `translate_wlan_preview` tool** (not `translate_config_preview`). `target_mode` (4 modes) from Stage 6.5 Q1 + the VAP's **own-scope** `ssid_profiles` + `gateway_cluster_list`. Needs full Act I + Stage 6.5. |
| `auth_server` | `rad_server` + `tacacs_server` | auth-server profile + config-assignment | **Preview wired in §2h.** Per-record; `scope_id` only (+ optional `extra_ctx["coa_servers"]` for AUTH_AND_COA correlation). Foundational — run FIRST. Shared-secret (`rad_key`/`tacacs_key`) is PII — **`translate_config_apply` BLOCKS this kind** until secret tokenization ships. |
| `server_group` | `server_group_prof` | server-group profile + config-assignment | **Preview wired in §2h.** Per-record; `scope_id` only. Depends on `auth_server` (members reference auth-servers by name). |
| `dot1x_auth` | `dot1x_auth_profile` | dot1x-auth profile + config-assignment | **Preview wired in §2h.** Per-record; `scope_id` only. Foundational profile referenced by the aaa-profile. |
| `mac_auth` | `mac_auth_profile` | mac-auth profile + config-assignment | **Preview wired in §2h.** Per-record; `scope_id` only. Foundational profile referenced by the aaa-profile. |
| `captive_portal` | `cp_auth_profile` | captive-portal profile + config-assignment | **Preview wired in §2h.** Per-record; `scope_id` only. References a server-group + roles by name (run those first / alongside). |
| `aaa_profile` | `aaa_prof` | aaa-profile + config-assignment | **Preview wired in §2h.** Per-record; `scope_id` only. Depends on auth-server, server-group, dot1x/mac/captive profiles, and roles — run the whole §2h chain in order. Gateway-terminated model. |

All 12 config kinds above ship on the canonical engine (plus WLAN via `translate_wlan_preview`). The **AAA chain** (`auth_server` → `server_group` → `dot1x_auth` / `mac_auth` / `captive_portal` → `aaa_profile`) is driven directly (per-record, no Stage 6.5 decision) — see §2h.

#### Step 1 — Scope resolution (walker-optional, fall back to placeholder)

For each distinct Central scope name from the Stage 7 mapping (or each AOS 8 binding scope if Stage 7 wasn't run), try `central-scope-walker` to resolve it to a real Central scope_id. **If walker returns no match — the target scope doesn't exist in Central yet — use a placeholder scope_id of the form `<TBD:Central-name>` and continue.** Stage 9b is a preview; the engine substitutes whatever string is passed and the resulting body's `scope-id` field surfaces as `<TBD:...>`, which is exactly the right "this scope must be created before execution" signal.

> **Scope-resolution principle (applies to every 2a–2g snippet):** pass the **resolved scope** for the object's binding, and a **`<TBD:...>`** placeholder when it can't be resolved — **never a silent `scope_lookup["Global"]` as if it were authoritative.** Resolve via `resolve_scope_id(name, type, path)`, which disambiguates because a **bare scope name is not unique** (Sites / Site-Collections / Device-Groups can share a name; the same name recurs under different parents): it matches by path when given, else name+type, and returns **`<AMBIGUOUS:...>`** rather than guessing when several scopes still match. The literal `scope_lookup["Global"]` shown in the 2a–2e examples is shorthand for "the resolved scope for this object"; on a real run substitute the object's resolved scope (2f/2g/dual resolve the operator-confirmed scope **identity** — name+type+path — from Stage 6.5; the SSID scope comes from the Stage-7 mapping's identity for the VAP's `_source_scope`). Global is correct only when Global is genuinely the chosen target.

```python
# Inside execute(): one walker pass for the Central scopes you need.
# See central-scope-walker.md for the full walker snippet — paste verbatim.

scope_tree_resp = await call_tool("central_get_scope_tree", {"view": "committed"})
envelope = scope_tree_resp.get("data", scope_tree_resp)
root = envelope.get("result", envelope) if isinstance(envelope, dict) and "result" in envelope else envelope

# Iterative DFS via stack — sandbox parser rejects `yield`/`yield from`.
all_nodes = []
stack = [(root, [])]
while stack:
    node, path = stack.pop()
    here = path + [node.get("scope_name") or node.get("scope_id") or "?"]
    all_nodes.append({
        "scope_id": node.get("scope_id"),
        "scope_name": node.get("scope_name"),
        "type": node.get("type"),
        "path": "/".join(here),
    })
    for child in (node.get("children") or []):
        stack.append((child, here))

def resolve(name: str, scope_type: str | None = None, scope_path: str | None = None) -> tuple[str, str]:
    """Resolve a Central scope to (scope_id, status). status ∈ resolved / placeholder / ambiguous.

    A bare display NAME is NOT unique — a Site, Site-Collection, and Device-Group can share
    a name, and the same name can recur under different parents. So disambiguate by the most
    specific identity available, and NEVER silently pick the first of several matches:
      1. scope_path given  -> match by full path (unique).
      2. else name (+ scope_type when given, normalized to the tree's type tokens).
      3. exactly one match -> resolved; several -> <AMBIGUOUS:...> (operator must give path/type);
         none -> <TBD:...> (scope not created yet).
    """
    if scope_path:
        m = [n for n in all_nodes if n["path"].lower() == scope_path.lower()]
        if m:
            return m[0]["scope_id"], "resolved"
        return f"<TBD:{scope_path}>", "placeholder"
    ql = (name or "").lower()
    m = [n for n in all_nodes if (n.get("scope_name") or "").lower() == ql or n["path"].lower() == ql]
    if scope_type:
        # Normalize the user-facing Stage 6.5 type to the actual central_get_scope_tree
        # token before comparing. Live tree tokens (verified): GLOBAL / SITE_COLLECTION /
        # SITE / DEVICE / DEVICE_COLLECTION. The mismatch that bites is "device_group"
        # (operator/skill term) vs the tree's "DEVICE_COLLECTION".
        TYPE_ALIASES = {
            "global": "global",
            "site": "site",
            "site_collection": "site_collection", "site-collection": "site_collection",
            "device_group": "device_collection", "device-group": "device_collection",
            "device_collection": "device_collection",
        }
        wanted = TYPE_ALIASES.get(scope_type.lower(), scope_type.lower())
        m = [n for n in m if (n.get("type") or "").lower() == wanted]
    if len(m) == 1:
        return m[0]["scope_id"], "resolved"
    if len(m) > 1:
        return f"<AMBIGUOUS:{name} ({scope_type or 'no type'})>", "ambiguous"
    return f"<TBD:{name}>", "placeholder"

def resolve_scope_id(name, scope_type=None, scope_path=None):
    """Thin wrapper returning just the scope_id (or <TBD>/<AMBIGUOUS> placeholder)."""
    return resolve(name, scope_type, scope_path)[0]

# Build the lookup ONCE for every Stage-7 Central name you need; default to "Global"
# if Stage 7 wasn't run. (For decisions that carry a type/path — clusters, dual SSID
# split scopes — call resolve_scope_id(name, type, path) directly so same-name scopes
# don't collide.)
scope_lookup = {}
scope_status = {}
for name in {"Global"}:  # ← replace with the set of Stage-7-confirmed Central names
    scope_lookup[name], scope_status[name] = resolve(name)
```

When rendering the final report, surface `scope_status` so the operator sees which scopes resolved vs which are placeholders.

#### Step 2 — Run the engine-driven preview per translation

`translate_config_preview` is **per-record** — one call per source object. Define this adapter once and reuse it in every §2x section; it loops a record list through the bridge and aggregates into the report shape (record count + per-record `canonical` / `calls` / `unresolved`). Bodies are omitted from `calls` for PII safety, so read field/rule/item counts off `canonical`.

```python
async def preview_kind(kind, records, scope_id, extra_ctx=None):
    """Run translate_config_preview per record; aggregate into a batch summary.

    Returns {kind, record_count, translatable, results:[{id, canonical, calls,
    unresolved, call_count}]}. `translatable` = records whose plan has no
    unresolved scopes/clusters/actions (i.e. apply would proceed).
    """
    results = []
    for rec in records:
        args = {
            "source_platform": "aos8", "target_platform": "central",
            "kind": kind, "source_record": rec, "scope_id": scope_id,
        }
        if extra_ctx:
            args["extra_ctx"] = extra_ctx
        resp = await call_tool("translate_config_preview", args)
        p = resp.get("data", resp)
        canon = p.get("canonical") or {}
        # primary identity per kind (vlan_id has no `name`; everything else does)
        rid = canon.get("name") or canon.get("vlan_name") or canon.get("vlan_id") or "<unknown>"
        results.append({
            "id": rid, "canonical": canon, "calls": p.get("calls", []),
            "unresolved": p.get("unresolved", []), "call_count": len(p.get("calls", [])),
        })
    return {
        "kind": kind, "record_count": len(records),
        "translatable": sum(1 for r in results if not r["unresolved"]),
        "results": results,
    }
```

**The `stage1_<obj>_records` flat lists are derived from `config_by_scope` by flattening — and each record MUST be stamped with its origin scope as `_source_scope`** so identity keys stay collision-safe:

```python
def _flatten(obj_type):
    out = []
    for scope, objs in config_by_scope.items():
        resp = objs.get(obj_type)
        rows = resp if isinstance(resp, list) else (resp or {}).get("_data", []) if isinstance(resp, dict) else []
        for r in (rows or []):
            if isinstance(r, dict):
                out.append({**r, "_source_scope": scope})
    return out

stage1_virtual_ap_records  = _flatten("virtual_ap")
stage1_cluster_prof_records = _flatten("cluster_prof")
stage1_ssid_prof_records   = _flatten("ssid_prof")   # ... and likewise for vlan_id / role / acl_sess / netdst / etc.
```

Without the `_source_scope` stamp, the composite `<source_scope>/<vap-name>` and `<source_scope>/<cluster-name>` keys collapse to bare names and the cross-scope collisions return. (Translations keyed by bare `record_id` — VLANs / roles / policies / net-groups — don't need the stamp, but it's harmless.)

##### 2a — VLANs (`central:vlan_id`)

```python
# Stage 1 collected aos8_get_effective_config(object_name="vlan_id") records.
# Filter inherited copies (consumer responsibility per the translation JSON).
# Note: AOS 8 vlan_id records at descendant scopes carry _flags.inherited=true
# even with entry_type="user". Always filter — without this, root-scope VLANs
# (typically VLAN 1) get re-emitted at every site/site-collection scope.
vlan_records = [r for r in stage1_vlan_id_records if not (r.get("_flags") or {}).get("inherited")]

batch = await preview_kind("vlan_id", vlan_records, scope_lookup["Global"])  # or your Stage-7 Central scope_id
result = {
    "kind": "vlan_id",
    "record_count": batch["record_count"],
    "translatable": batch["translatable"],
    "summary": [
        {"id": r["id"], "calls": r["call_count"], "unresolved": r["unresolved"]}
        for r in batch["results"]
    ][:30],   # cap for small models
}
result
```

##### 2b — Named VLANs (`central:named_vlan`)

**Composite source — REQUIRED pre-merge.** AOS 8 stores named VLANs as two separate objects: `vlan_name` registers the symbolic name (carries no VLAN-ID information) and `vlan_name_id` binds the name to one or more VLAN IDs. The engine expects ONE merged record per name with both `name` and `vlan-ids` populated. Skipping the merge step produces silent skips (records without `vlan-ids` fail required-field validation in the engine).

Per `named_vlan_v1.json`'s `merge_rule`: join key is `name`; only emit a record when BOTH a `vlan_name` registration AND a corresponding `vlan_name_id` binding exist (a name without a binding produces an unresolvable Central named-VLAN profile and per `unmapped_fields` should NOT be migrated). Drop `_flags.inherited == True` rows from BOTH source arrays before the join.

```python
# Stage 1 collected both objects. Filter inherited copies on each side
# (consumer responsibility per named_vlan_v1.json's merge_rule).
vlan_names = [r for r in stage1_vlan_name_records if not (r.get("_flags") or {}).get("inherited")]
vlan_id_bindings = [r for r in stage1_vlan_name_id_records if not (r.get("_flags") or {}).get("inherited")]

# Merge: one record per name with name + vlan-ids combined.
# Names without a binding are surfaced as a "Skipped per LLD" finding —
# per named_vlan_v1.json's unmapped_fields: a vlan_name with no vlan_name_id
# is non-functional in Central (no VLAN to resolve to).
binding_by_name = {b["name"]: b for b in vlan_id_bindings}
merged = []
unbound_names = []
for vn in vlan_names:
    nm = vn.get("name")
    if not nm:
        continue
    if nm in binding_by_name:
        merged.append({**vn, **binding_by_name[nm]})  # carries 'name' + 'vlan-ids'
    else:
        unbound_names.append(nm)

batch = await preview_kind("named_vlan", merged, scope_lookup["Global"])  # or your Stage-7 Central scope_id
result = {
    "kind": "named_vlan",
    "record_count": batch["record_count"],
    "translatable": batch["translatable"],
    "skipped_per_lld": unbound_names,   # names registered but never bound to a VLAN ID
    "summary": [
        {"name": r["id"], "calls": r["call_count"], "unresolved": r["unresolved"]}
        for r in batch["results"]
    ][:30],
}
result
```

##### 2c — Roles (`central:role`)

```python
# Filter system / default roles (consumer responsibility per role_v1.json).
role_records = [
    r for r in stage1_role_records
    if not (r.get("_flags") or {}).get("default")
    and not (r.get("_flags") or {}).get("inherited")
]

# While iterating, note any role binding an Ethernet ACL — these are out of scope
# for central:policy and need OPERATOR-MAP follow-up. Surface them in the report.
roles_with_eth_acl = [
    r["rname"] for r in role_records
    if any((b.get("acl_type") == "eth") for b in (r.get("role__acl") or []))
]

batch = await preview_kind("role", role_records, scope_lookup["Global"])  # or your Stage-7 Central scope_id
result = {
    "kind": "role",
    "record_count": batch["record_count"],
    "translatable": batch["translatable"],
    "roles_with_eth_acl": roles_with_eth_acl,   # surface in Translation gaps section
    "summary": [
        {"name": r["id"], "calls": r["call_count"], "unresolved": r["unresolved"]}
        for r in batch["results"]
    ][:30],
}
result
```

##### 2d — Policies (`central:policy`)

Policy translation reverse-indexes role records — pass the FULL role list (post system-default filtering) via `extra_ctx["role_records"]`. The reader does the per-ACL lookup internally.

**Pre-filter empty ACLs.** Per the translation JSON's `ignored_variants`: *"Empty ACL will NOT be migrated"* and *"ACL by itself will NOT be migrated"*. These are documented LLD rules. Filter them out of the engine call AND surface them in a "Skipped per LLD" subsection so the operator sees what was excluded and why. Common offenders in real tenants: AppRF system-companion ACLs (`apprf-*-sacl`) that exist as paired-with-role plumbing with no rules, plus user-defined ACLs that were created but never populated (typically `transition`, `blacklisted` placeholders).

```python
# Same role_records as 2c (already system-default-filtered).

# Filter inherited / system ACLs first.
candidate_acls = [
    r for r in stage1_acl_sess_records
    if not (r.get("_flags") or {}).get("inherited")
    and not (r.get("_flags") or {}).get("system")
]

# Per central:policy_v1.json's ignored_variants: empty ACLs are not migrated.
def _has_rules(r: dict) -> bool:
    return bool((r.get("acl_sess__v4policy") or []) or (r.get("acl_sess__v6policy") or []))

acl_records = [r for r in candidate_acls if _has_rules(r)]
empty_acls = [r.get("accname", "<unknown>") for r in candidate_acls if not _has_rules(r)]

# role_records drives the role-attribution reverse-index (extra_ctx, not a body field).
batch = await preview_kind(
    "policy", acl_records, scope_lookup["Global"], extra_ctx={"role_records": role_records}
)
result = {
    "kind": "policy",
    "record_count": batch["record_count"],
    "translatable": batch["translatable"],
    "skipped_per_lld": empty_acls,   # surface these in the report
    "summary": [
        {
            "acl": r["id"],
            "calls": r["call_count"],
            # bodies are omitted from `calls`; rule count comes off the PII-safe canonical.
            "rules": len(r["canonical"].get("rules", [])),
            # an unmapped action fail-closes to ACTION_DENY + flags unresolved — surface it.
            "unmapped_actions": r["canonical"].get("unmapped_actions", []),
            "unresolved": r["unresolved"],
        }
        for r in batch["results"]
    ][:30],
}
result
```

##### 2e — Net groups (`central:net_group`)

Aliases referenced by `acl_sess` rules via the `salias` / `dalias` discriminator. **Despite appearing last in the preview, this translation runs FIRST in execution** — `central:policy` rule bodies reference these aliases by name and Central rejects the policy POST if the alias doesn't exist.

```python
# Stage 1 collected both netdst (IPv4) and netdst6 (IPv6) records.
# Filter inherited / system / default aliases — consumer responsibility per
# net_group_v1.json's ignored_variants.
def _is_translatable(r: dict) -> bool:
    flags = r.get("_flags") or {}
    if flags.get("inherited") or flags.get("system") or flags.get("default"):
        return False
    # Skip empty aliases (no entries — Central rejects empty items[]).
    entries = r.get("netdst__entry") or r.get("netdst6__entry") or []
    return bool(entries)

netdst_records = [r for r in (stage1_netdst_records + stage1_netdst6_records) if _is_translatable(r)]
empty_or_system = [
    r.get("dstname", "<unknown>")
    for r in (stage1_netdst_records + stage1_netdst6_records)
    if not _is_translatable(r)
]

batch = await preview_kind("net_group", netdst_records, scope_lookup["Global"])  # or your Stage-7 Central scope_id
result = {
    "kind": "net_group",
    "record_count": batch["record_count"],
    "translatable": batch["translatable"],
    "skipped_per_lld": empty_or_system,   # surface in Translation gaps
    "summary": [
        {
            "alias": r["id"],
            "calls": r["call_count"],
            # counts/family from the PII-safe canonical (bodies omitted from `calls`).
            "items": len(r["canonical"].get("items", [])),
            "family": r["canonical"].get("address_family"),
            "unresolved": r["unresolved"],
        }
        for r in batch["results"]
    ][:30],
}
result
```

**Note on Ethernet/MAC ACL bindings.** AOS 8 roles can technically reference `acl_eth` or `acl_mac` entries via `role__acl[]` with `acl_type="eth"` / `acl_type="mac"`. Those ACL types are out of scope for this skill (issue #298 — unique-use cases). If you encounter a role binding one, leave the binding noted in the disposition matrix row's notes column but do NOT attempt to translate it; Stage 1 collection no longer enumerates these ACL types.

**Note on `netsvc` (AOS 8 service aliases).** AOS 8 `acl_sess` rules may reference custom service aliases via `service-name` plus the AOS 8 `netsvc` schema. `central:net_service` is **deferred** to a future release pending live shape verification — Central rejects policy POSTs that reference unknown service aliases. If preview surfaces policy rules using non-`svc-*` service names (`svc-http` / `svc-https` / etc. come from Central's built-in catalog and work today), surface those in Translation gaps under "Service aliases pending translation" so the operator knows to pre-populate Central or wait for the translation to ship.

##### 2f — Gateway clusters (`central:gateway_cluster`) — consumes Stage 6.5 Q2

Only when at least one SSID is Tunneled / Hybrid / Bridged-and-Tunneled (otherwise skip — no gateways). For each source `cluster_prof`, look up the operator's decision by the composite `<source_scope>/<cluster-name>` key (same collision-safety as VAPs), then pass the chosen `cluster_strategy` and the scope **identity** (`target_scope_name` + `target_scope_type` + optional `target_scope_path`) resolved to a `scope_id`/`<TBD>` via `resolve_scope_id` (the scope may not exist yet, and a bare name isn't unique).

```python
cluster_records = [
    c for c in stage1_cluster_prof_records
    if not (c.get("_flags") or {}).get("system") and not (c.get("_flags") or {}).get("default")
]
cluster_previews = []
for c in cluster_records:
    # Composite key — the same cluster_prof name can exist at multiple AOS scopes,
    # so a bare name would apply one cluster's decision to another's.
    cluster_key = f"{c.get('_source_scope', '<scope>')}/{c['profile-name']}"
    # Only clusters that survive into the chosen topology have a Stage 6.5 decision.
    # If all SSIDs were Bridged (Q2 skipped) or this cluster is unused, there's no
    # decision — skip with a clear reason instead of indexing a missing key.
    dec = decisions.get("per_cluster", {}).get(cluster_key)
    if not dec:
        cluster_previews.append({
            "source": cluster_key,
            "skip_reason": "no Stage 6.5 gateway-cluster decision (not referenced by the chosen topology / no tunneled SSID binds it)",
        })
        continue
    # Strategy and placement are SEPARATE decisions. Stage 6.5 collected the intended
    # Central scope NAME (target_scope_name), not an id; resolve it to a scope_id here via
    # the walker, falling back to <TBD:...> (the scope may not exist yet — Stage 9
    # builds the hierarchy first). Do NOT default a MISSING scope to Global: if the
    # operator never chose a scope, skip with a reason rather than silently mis-placing.
    if not dec.get("target_scope_name"):
        cluster_previews.append({
            "source": cluster_key,
            "skip_reason": "Stage 6.5 recorded a cluster_strategy but no target_scope_name — confirm the Central scope for this cluster before previewing",
        })
        continue
    # Resolve by name+type (+path) — never bare name (ambiguous across types/parents).
    cluster_scope_id = resolve_scope_id(dec["target_scope_name"], dec.get("target_scope_type"), dec.get("target_scope_path"))
    response = await call_tool(
        "translate_config_preview",
        {
            "source_platform": "aos8",
            "target_platform": "central",
            "kind": "gateway_cluster",
            "source_record": c,
            "scope_id": cluster_scope_id,
            "extra_ctx": {"cluster_strategy": dec["cluster_strategy"]},  # ha_only / intent_site / intent_manual
        },
    )
    cluster_previews.append({"source": cluster_key, **response.get("data", response)})
```

##### 2g — WLAN SSIDs (`central:wlan_ssid`) — consumes Stage 6.5 Q1

WLAN uses the dedicated `translate_wlan_preview` tool (not `translate_config_preview`). One source record = one `virtual_ap`, passed as `source_override`; pass **only the VAP's own scope's** `ssid_prof` records via `context_override={"reader_ctx": {"ssid_profiles": [...]}}` (the engine joins by name, so a scope-filtered list prevents a same-name profile at another scope from binding — never pass the full flat list). Per **VAP instance**, look up the operator's decision by the composite `<source_scope>/<vap-name>` key (Q1), pass `target_mode`, and **resolve the decision's `cluster_refs` (composite per_cluster keys) into the `gateway_cluster_list` param — the Central overlay object shape `[{cluster, cluster-type, tunnel-type, cluster-redundancy-type, cluster-scope-id}]`**, not the raw key strings (the writer substitutes it whole into the overlay body). For `bridged_and_tunneled`, confirm the decision's `bridge_scope_name` / `tunnel_scope_name` are present before previewing.

```python
vap_records = [
    v for v in stage1_virtual_ap_records
    if not (v.get("_flags") or {}).get("system") and not (v.get("_flags") or {}).get("default")
]
ssid_previews = []
for v in vap_records:
    vap_key = f"{v.get('_source_scope', '<scope>')}/{v['profile-name']}"   # composite identity
    # SCOPE-AWARE ssid_prof join: a VAP resolves its ssid_prof within its OWN scope
    # (effective-config surfaces the inherited copy at that scope). Same-name ssid_prof
    # objects at different scopes can differ, so pass the engine ONLY this VAP's scope's
    # ssid_profiles — never the full flat list (a bare-name join over all scopes could
    # bind the wrong profile). This is the same cross-scope collision guard used for
    # the VAP/cluster decision keys.
    scoped_ssid_profiles = [
        s for s in stage1_ssid_prof_records if s.get("_source_scope") == v.get("_source_scope")
    ]
    scoped_ssid_names = {s.get("profile-name") for s in scoped_ssid_profiles}
    # Match the Q1 "translatable" definition: a VAP whose ssid_prof reference doesn't
    # resolve at its scope is not translatable — surface the specific missing-profile gap.
    sp_ref = (v.get("ssid_prof") or {}).get("profile-name")
    if sp_ref not in scoped_ssid_names:
        ssid_previews.append({"source": vap_key, "skip_reason": f"references ssid-profile '{sp_ref}' not present at scope {v.get('_source_scope')} — not translatable"})
        continue
    dec = decisions.get("per_vap", {}).get(vap_key)                         # from Stage 6.5
    if not dec:
        ssid_previews.append({"source": vap_key, "skip_reason": "no Stage 6.5 forward-mode decision for this VAP"})
        continue
    # Resolve the AP broadcast scope from the VAP's source scope via the Stage 7
    # AOS8->Central hierarchy mapping — do NOT default to Global (that would preview
    # at the wrong scope after the operator confirmed placement in Stage 7). If the
    # Stage 7 mapping / walker can't resolve it, use a <TBD:...> placeholder (Step 1
    # convention) so the gap is visible rather than authoritative-looking.
    # The Stage 7 mapping yields the AP's Central scope IDENTITY (name + type + path) for the
    # VAP's source scope — resolve by it, not a bare name (a path from the mapping is unambiguous).
    mapped = stage7_central_scope_for(v.get("_source_scope"))   # {"name":..., "type":..., "path":...}
    ssid_scope_id = resolve_scope_id(mapped.get("name"), mapped.get("type"), mapped.get("path")) \
        if mapped else f"<TBD:{v.get('_source_scope')}>"

    # Resolve the VAP's cluster_refs (composite per_cluster KEYS — for lookup only)
    # into the Central overlay payload shape the engine actually expects:
    #   [{cluster, cluster-type, tunnel-type, cluster-redundancy-type, cluster-scope-id}]
    # central:wlan_ssid substitutes gw_cluster_list WHOLE into the overlay body, so it
    # must already be Central objects, NOT decision-key strings.
    gw_cluster_list, cluster_gap = [], None
    for idx, cref in enumerate(dec.get("cluster_refs", [])):
        cdec = decisions.get("per_cluster", {}).get(cref)
        if not cdec or not cdec.get("target_scope_name"):
            cluster_gap = f"cluster {cref} has no confirmed Stage 6.5 decision/scope — can't build the overlay binding"
            break
        # resolve by name+type (+path) — never bare name (ambiguous across types/parents).
        cluster_scope_id = resolve_scope_id(cdec["target_scope_name"], cdec.get("target_scope_type"), cdec.get("target_scope_path"))
        gw_cluster_list.append({
            "cluster": cref.split("/")[-1],            # Central gateway-cluster profile name
            "cluster-type": "GATEWAY",
            "tunnel-type": "L2",                       # tunnel binding; refine per design if L3
            # cluster-redundancy-type is MANDATORY in the overlay schema (enum PRIMARY/BACKUP).
            # The VAP's first/anchor cluster is PRIMARY; any additional (e.g. DMZ) clusters are
            # BACKUP. cluster_refs order encodes this (anchor first); operator confirms for
            # multi-cluster designs.
            "cluster-redundancy-type": "PRIMARY" if idx == 0 else "BACKUP",
            "cluster-scope-id": cluster_scope_id,
        })
    if cluster_gap:
        ssid_previews.append({"source": vap_key, "skip_reason": cluster_gap})
        continue

    if dec["target_mode"] == "bridged_and_tunneled" and (
        not dec.get("bridge_scope_name") or not dec.get("tunnel_scope_name")
    ):
        # Dual mode needs both scope NAMES confirmed in Stage 6.5 — guard on the names,
        # don't index (a partial decision must surface as the promised gap, not a KeyError).
        ssid_previews.append({
            "source": vap_key,
            "skip_reason": "bridged_and_tunneled needs both bridge_scope_name and tunnel_scope_name — confirm the scope split in Stage 6.5",
        })
        continue
    # WLAN uses the dedicated translate_wlan_preview bridge (NOT translate_config_preview):
    # source_override = this VAP; the engine joins ssid_prof by name within the VAP's own
    # scope (scoped_ssid_profiles). gateway_cluster_list is the resolved Central overlay
    # objects the tunneled/hybrid/dual SSID binds to (built above).
    response = await call_tool(
        "translate_wlan_preview",
        {
            "source_platform": "aos8",
            "target_platform": "central",
            "ssid": v.get("profile-name") or sp_ref,
            "target_mode": dec["target_mode"],            # bridged / tunneled / hybrid / bridged_and_tunneled
            "gateway_clusters": [cref.split("/")[-1] for cref in dec.get("cluster_refs", [])],
            "gateway_cluster_list": gw_cluster_list,      # Central overlay objects
            "source_override": v,
            "context_override": {"reader_ctx": {"ssid_profiles": scoped_ssid_profiles}},
        },
    )
    ssid_previews.append({"source": vap_key, "intended_scope": ssid_scope_id, **response.get("data", response)})
```

Surface each VAP's emitted calls (the wlan-ssids profile(s) + any overlay-wlan binding) in the consolidated report; a `skip_reason` here is a Stage 6.5 input gap (e.g. dual mode missing a scope) — surface it verbatim. `translate_wlan_preview` returns `{canonical, calls, unresolved, preview}` (same shape as `translate_config_preview`); `unresolved` flags a tunneled SSID whose gateway-cluster binding couldn't be built.

##### 2h — AAA chain (`central:auth_server` → `server_group` → `dot1x_auth` / `mac_auth` / `captive_portal` → `aaa_profile`)

These six kinds preview via `translate_config_preview`. Unlike 2f/2g they are **driven directly** — per-record, `scope_id` only, **no Stage 6.5 decision** — so they need the AAA objects from Stage 1 but **not** the questionnaire. They model the **gateway-terminated (tunnel / hybrid) AAA**: the gateway `aaa-profile` a tunnel-mode `wlan-ssid` binds to. For a fully **bridged / controllerless** design the AAA folds inline into the `wlan-ssid` instead (deferred — see §2g notes / the bridge-mode AAA backlog item); if **every** surviving SSID is Bridged, run §2h for completeness but mark it **informational** in the report (the gateway aaa-profile won't be referenced).

**Where "every surviving SSID is Bridged" comes from:** read it off the **Stage 6.5 Q1 decisions** that §2g consumes — the gateway AAA is referenced only when at least one VAP's `target_mode` is `tunneled` / `hybrid` / `bridged_and_tunneled`. **Distinguish three states** (do NOT collapse the last two — "all Bridged" and "Stage 6.5 never ran" are different operator situations):

```python
per_vap = decisions.get("per_vap", {})
gateway_modes = {"tunneled", "hybrid", "bridged_and_tunneled"}
if not per_vap:
    aaa_status = "data-gap"      # Stage 6.5 didn't run / no VAP decisions collected — we CANNOT
                                 # conclude the AAA is unused; flag the precondition gap and still
                                 # preview the chain, but do NOT label it 'informational'.
elif any(d.get("target_mode") in gateway_modes for d in per_vap.values()):
    aaa_status = "live"          # ≥1 gateway-terminated SSID — its aaa-profile is what the §2g
                                 # overlay SSIDs authenticate against.
else:
    aaa_status = "informational" # decisions exist AND every one is Bridged — the gateway
                                 # aaa-profile genuinely won't be referenced.
```

Tag the §2h result with `aaa_status` so the report says *why* (live vs intentionally-unused vs missing-data), rather than silently marking it informational when Stage 6.5 simply hasn't run.

**Dependency order is also the preview order** (so the operator reads prerequisites first): `auth_server` → `server_group` → {`dot1x_auth`, `mac_auth`, `captive_portal`} → `aaa_profile`. Server-groups reference auth-servers by name; the aaa-profile references server-groups + the dot1x/mac/captive profiles + roles by name — each prerequisite must exist in Central before the object that references it.

> **PII — handled by the bridge, but stay alert:** the `auth_server` Central body carries the shared secret (`rad_key` / `tacacs_key` → `shared-secret-config.plaintext-value`). `translate_config_preview` already protects this two ways: it **omits call bodies** entirely and **redacts the secret in `canonical`** (you'll see `***REDACTED***`). So preview output is safe to render as-is. Two hard rules remain:
> - In summaries, show **presence only** (e.g. `shared_secret: present`), never the value — and never reconstruct the secret from the source record into the report.
> - The **write path is PII-gated at the tool layer**: `translate_config_apply` returns a 403 for `kind="auth_server"` until secret tokenization ships. Don't try to route around it — create auth-servers manually for now.

```python
def _aaa_translatable(r: dict) -> bool:
    # Same consumer-side filter as every other family: drop system / default /
    # inherited-at-descendant-scope copies; the engine translates the rest.
    flags = r.get("_flags") or {}
    return not (flags.get("inherited") or flags.get("system") or flags.get("default"))

# (kind, source record list) in EXECUTION = PREVIEW order. auth_server combines both
# REST source shapes (RADIUS + TACACS) — the reader tags the type per record.
aaa_chain = [
    ("auth_server",    stage1_rad_server_records + stage1_tacacs_server_records),
    ("server_group",   stage1_server_group_prof_records),
    ("dot1x_auth",     stage1_dot1x_auth_profile_records),
    ("mac_auth",       stage1_mac_auth_profile_records),
    ("captive_portal", stage1_cp_auth_profile_records),
    ("aaa_profile",    stage1_aaa_prof_records),
]
aaa_previews = []
for kind, records in aaa_chain:
    recs = [r for r in records if _aaa_translatable(r)]
    if not recs:
        # No user-defined records at this scope is normal (e.g. no TACACS, or AAA
        # lives at a parent scope). Record it so the report shows the family ran.
        aaa_previews.append({"kind": kind, "record_count": 0, "translatable": 0,
                             "note": "no user-defined records at this scope (all system/default/inherited, or none configured)"})
        continue
    # Resolve the binding scope the SAME way as every other object — the gateway-terminated
    # AAA profiles land at the gateway's Central scope (where the cluster lands). This is the
    # resolved scope / <TBD:...> from resolve_scope_id() (via the Stage-7 mapping), NEVER a
    # silent Global default. Substitute the real resolved id on your run.
    resolved_central_scope_id = resolve_scope_id(*aaa_landing_scope_identity)   # (name, type, path)
    # auth_server: optionally correlate co-located CoA via the matching aaa_prof's
    # rfc3576_client[] → extra_ctx={"coa_servers": [...]} (folds AUTH_AND_COA). Omitted
    # here for brevity; pass it when you have the aaa_prof CoA list for these servers.
    batch = await preview_kind(kind, recs, resolved_central_scope_id)
    aaa_previews.append({
        "kind": kind,
        "record_count": batch["record_count"],
        "translatable": batch["translatable"],
        # auth_server secrets are redacted in `canonical` by the bridge and apply is
        # PII-blocked — show presence only, never the value.
        "summary": [
            {"id": r["id"], "calls": r["call_count"], "unresolved": r["unresolved"]}
            for r in batch["results"]
        ][:30],
    })
aaa_previews
```

Surface each family's emitted calls in the consolidated report under an **AAA chain** subsection, in the order above. A `skip_reason` on a record is a translation gap (e.g. an `aaa_prof` referencing a server-group that wasn't collected) — surface it verbatim; a record that references a not-yet-created prerequisite is an **ordering** note, not a failure (the chain creates prerequisites first).

**Minimal-path note:** §2h needs the AAA objects (`rad_server` / `server_group_prof` / `dot1x_auth_profile` / `mac_auth_profile` / `cp_auth_profile` / `aaa_prof`) collected in Stage 1. They are **not** part of the 2a–2e minimal collection, but — unlike 2f/2g — they need **no Stage 6.5 decision**. Run §2h after a **full Act I walk**, or extend the minimal collection to pull these object kinds; do not emit empty AAA previews silently on the 2a–2e minimal path — note that the AAA chain requires the AAA objects.

#### Step 3 — Render the consolidated preview report

Combine all preview result dicts from Step 2 (VLANs / named-VLANs / roles / policies / net-groups, plus gateway-clusters and WLAN-SSIDs when the full Act I + Stage 6.5 flow ran, plus the §2h AAA chain when the AAA objects were collected) into a single operator-facing report. The report has THREE parts: (a) summary table, (b) per-record detail tables, (c) **sample call bodies** as JSON code blocks (each preview record's `calls[i]["body"]` — the actual Central POST payload, already PII-scrubbed by the bridge). Operators reviewing the migration need (c) — the JSON the migration will POST — not just counts.

```
## Engine-driven translation preview (read-only)

**Source scope:** /md/Campus/West (AOS 8)
**Target scope_id:** `197674231` (Central Site `USW/West`, resolved from the Stage 7 mapping) — _resolved_
   ← OR: `<TBD:USW/West>` _placeholder; target scope not yet created in Central_ (the source scope resolves to its mapped Central scope, NOT a Global default)
**Kinds run:** vlan_id, named_vlan, role, policy
**Tool:** translate_config_preview (+ translate_wlan_preview for §2g) — read-only; no API writes

### Summary

| Kind | Records | Translatable | Skipped per LLD | Calls (sum) |
|---|---|---|---|---|
| vlan_id | 8 | 8 | 0 | 16 |
| named_vlan | 6 | 4 | 2 (unbound names: USER-VLAN, IOT-VLAN) | 24 |
| role | 6 | 6 | 0 | 12 |
| policy | 13 | 6 | 7 (empty rule lists: apprf-*, transition, blacklisted) | 18 |

### Per-record detail

#### Policies (6 translatable, 7 skipped per LLD)
| ACL | Rules | Calls | Skip |
|---|---|---|---|
| captiveportalbridge | 6 | 2 | — |
| logon-control-bridge | 6 | 2 | — |
| parent | 14 (incl. 2 from any-any expansion) | 2 | — |
| ... | ... | ... | ... |

**Skipped per LLD (empty rule lists):** `apprf-blacklisted-sacl`, `apprf-unregistered_role-sacl`, `apprf-transition-sacl`, `apprf-camera-sacl`, `apprf-test-guest2-guest-logon-sacl`, `transition`, `blacklisted` — per central:policy_v1.json's ignored_variants, "Empty ACL will NOT be migrated".

#### Roles (6 translatable)
| Role | Calls | Notes |
|---|---|---|
| parent | 2 | binds session ACL `parent`; carries bandwidth contracts |
| blacklisted | 2 | binds session ACL `deny-all`; **also binds Ethertype ACL `deny_all_ethertype` — out of scope for central:policy, see Translation gaps** |
| ... | ... | ... |

### Sample TargetCall bodies

For at least the FIRST record of each kind, emit that preview record's `calls[0]["body"]` as a JSON code block (the create call's payload — already PII-scrubbed by the bridge). This shows the operator the actual wire payload.

#### Policy: `captiveportalbridge` (representative)

```json
{
  "name": "captiveportalbridge",
  "type": "POLICY_TYPE_SECURITY",
  "association": "ASSOCIATION_ROLE",
  "security-policy": {
    "type": "SECURITY_POLICY_TYPE_DEFAULT",
    "policy-rule": [
      {
        "address-family": "IPV4",
        "rule-type": "RULE_NET_SERVICE",
        "condition": { ... },
        "action": { "type": "ACTION_DUAL_NAT", ... }
      }
    ]
  }
}
```

#### Role: `parent` (representative)
... (similar JSON block) ...

#### Named VLAN: `vlan20` (representative)
... (similar JSON block) ...

#### VLAN ID: `108` (representative)
... (similar JSON block) ...

### Write hazards (target collisions)

The per-record bridge doesn't cross-check records, so detect collisions client-side: scan every preview record's `calls` for **distinct source records that POST the same non-assignment path** (e.g. two named-VLANs whose names case-fold to one `/aliases/<name>`, or two server-groups folding to one name). The shared `/config-assignments` collection is NOT a collision (its object identity is in the body, not the path), so exclude it. Distinct records hitting one path overwrite/409 each other at execution — list them verbatim so the operator renames or merges before cutover. Omit the section when no path collides.

```python
from collections import defaultdict
hits = defaultdict(list)
for batch in all_preview_batches:                     # every preview_kind result you produced
    for r in batch["results"]:
        for c in r["calls"]:
            if c["path"].endswith("/config-assignments"):
                continue
            hits[c["path"]].append((batch["kind"], r["id"]))
collisions = {p: v for p, v in hits.items() if len({rid for _, rid in v}) > 1}
```

| Target object | Colliding source records | Hazard |
|---|---|---|
| `/aliases/user-vlan` (named_vlan alias) | `USER-VLAN`, `user-vlan` | both fold to alias `user-vlan` — second POST overwrites the first |

### Drill-down available

- *"Show me the body for ACL `<name>`"* — re-run that single record; dump `calls[0]["body"]` (and `calls[i]["body"]` for the policy-group + config-assignment if relevant).
- *"Dump all bodies for `<kind>`"* — emit every record's `calls` bodies. May be large; warn the operator first if `record_count > 10`.
- *"Show me the diff between two records"* — run preview for both, dump body fields side-by-side.
```

**Output rules:**

- **Use the deterministic counts** — never hand-fabricate. `record_count` / `translatable` from `preview_kind` are exact; do not narrate "approximately 8".
- **Surface every `unresolved` entry verbatim** — these are the engine's signals about what can't execute yet (unresolved scope, unbound gateway cluster, unmapped policy action). Surface `skipped_per_lld` lists separately (these are pre-engine consumer filters; the engine never saw them).
- **Cap the per-record detail table at ~30 rows per kind.** Bodies appear in the "Sample call bodies" section, not in the table. The drill-down prompts let the operator request specific bodies.
- **Always emit at least 1 sample body per kind** in Step 3 unless the kind had 0 records. Picking the FIRST record's `calls[0]["body"]` is fine; the goal is a concrete sense of what gets POSTed. `auth_server` bodies are already secret-redacted by the bridge (`***REDACTED***`) — render as-is; never reconstruct the secret from the source record.
- **For runs with `record_count == 0` for a given kind,** emit a one-line note (e.g. *"vlan_id: 0 records at this scope"*) instead of an empty section.
- **Surface path collisions as write hazards.** Run the collision scan above; if any non-assignment path is POSTed by distinct records, render the "Write hazards" section — they overwrite/409 each other at execution and must be reconciled before cutover.
- **Mark every placeholder scope loudly.** A call whose `unresolved` flags a `<TBD:...>` / missing scope is NOT executable — say so in the report header so the operator knows the target hierarchy must be created first.

**Findings produced:** if any kind has records with non-empty `unresolved` OR a non-empty `skipped_per_lld` (pre-filtered), surface those reasons as a finding under Act II's "Translation gaps" subsection.

---

For every Stage 9 step that creates a Central object (i.e. excludes `[Central API gap]` placeholder steps), emit one row of a validation checklist mapping the create call to its corresponding read-back call.

**Read-back mapping** (every `central_manage_*` has a corresponding `central_get_*`):

| Created via | Verify via | Expected attributes |
|---|---|---|
| `central_manage_site_collection` | `central_get_scope_tree` | name, parent_id (root) |
| `central_manage_site` | `central_get_sites` (also `central_get_scope_tree`) | name, parent collection name |
| `central_manage_device_group` | `central_get_scope_tree` | name, parent site name |
| `central_manage_gw_cluster_intent_config` | `central_get_gw_cluster_intent_config` | name, cluster-mode (CM_SITE / CM_MANUAL), device-type, multicast-vlan, heartbeat-threshold, scope binding |
| `central_manage_gateway_clusters` | `central_get_gateway_clusters` | name, ipv4-gateways[].mac (member list), auto-cluster (false for manual), heartbeat-threshold |
| `central_manage_roles` | `central_get_roles` | name, vlan, access-list, captive-portal, session-timeout |
| `central_manage_role_acls` | `central_get_role_acls` | name, rule list, ordering |
| `central_manage_net_groups` | `central_get_net_groups` | name, member list |
| `central_manage_net_services` *(DEFERRED — `central:net_service` not yet shipped; net-services are operator-pre-populated until it lands, so this read-back applies only once that translation exists)* | `central_get_net_services` | name, protocol, port range |
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
| A **verdict-gating** REGRESSION fires — i.e. a **target-architecture-INDEPENDENT** one: feature-parity **F1, F2, F5–F10** (NOT F3/F4), orchestration **O1–O3**, or Stage 4a **A1–A2** (A3 is INFO-only — never a REGRESSION). (Bucket-4 findings — F3, F4, the per-target-mode T\*/B\*/M\* blocks, and A4/A5 — are provisional and **never** trigger BLOCKED; see the bucket-4 INVARIANT.) | **BLOCKED**. Lead the report with the must-fix list. |
| No verdict-gating REGRESSION (only DRIFT / INFO, or only provisional bucket-4 findings) | **GO**. |
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
- **Reframed verdicts** (e.g. "tentatively GO" or "GO with caveats"). Verdicts are the literal four values: **GO**, **BLOCKED**, **PARTIAL**, or **EMPTY-SOURCE**.
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
**Per-SSID forward mode (detected → decided in Stage 6.5):** <per-SSID forward-mode breakdown from the virtual_ap rows>. These are the recommendations the operator confirms/changes in the Stage 6.5 questionnaire.
**Cluster topology (auto-detected):** <L2 cluster <name> at <scope> | L3 cluster | standalone | offline-at-audit-time>
**Target HA mode (recommended → confirmed in Stage 6.5):** <Auto Group | Auto Site | Manual> — derived from cluster topology
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
- Cluster L2/L3 status: <state> (or "configured but offline at audit time" if `cluster_prof` rows present + live cluster empty)
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

### Suggested AOS 10 hierarchy mapping (operator-confirmable draft)

The skill produces a draft inference per `/md/<path>` Group node using naming heuristics, structural signals, Device-Function cross-reference, and **cluster-mode derivation** (see Stage 7 rules). Rows marked `medium` or `low` confidence may need operator review for placement / target-name corrections. The derived cluster mode is the **recommendation** shown in the Stage 6.5 gateway-topology question — the operator confirms it or overrides the topology there.

| Source AOS node | Inferred placement | Inferred Device Function | Confidence | Cluster mode (derived) | Reason | Operator action |
|---|---|---|---|---|---|---|
| `/md` | (none — root) | n/a | high | n/a | Conductor root, dropped | — |
| `<row per Group node>` | Site Collection / Site / Device Group | MOBILITY_GW / VPNC / BRANCH_GW / MICROBRANCH_AP / CAMPUS_AP / n/a | high / medium / low | n/a / **CM_SITE** / **CM_MANUAL** | <which rule fired — child Group nodes \| plural noun \| `_Static` \| persona token \| AP children \| geographic noun \| cluster_prof matched via Switch IP \| cluster_prof + multizone anchor \| cluster_prof + no APs \| no signal> | confirm placement / target name |

**Device Function key** (Central's filter dimension — limits which device types receive a profile within a scope; NOT a scope itself):
- `MOBILITY_GW` (Mobility Gateway) — WLAN gateway. Default for AOS 8 Mobility Controllers (MDs).
- `VPNC` / `BRANCH_GW` — gateway-only Device Functions; never have APs. Place under a Device Group with the matching Device Function so profiles applied at parent scopes can filter to them.
- `MICROBRANCH_AP` / `CAMPUS_AP` — wireless AP Device Functions.
- (out of scope) `ACCESS_SWITCH`, `AGG_SWITCH`, `CORE_SWITCH`, `BRIDGE`, `HYBRID_NAC` — flagged as wired/NAC migration not in this skill's scope; not translated.

**Cluster mode column (detected default):** every row's cluster mode is computed by the cluster-mode derivation (run during Stage 2 detection; algorithm documented at Stage 7 Step 4) from `ap_database.Switch IP` / `Standby IP` matching against `cluster_prof.cluster_controller[].ip`, with multizone enrichment from `ap_multizone_prof.controller[].ip`. `CM_SITE` = primary zone (APs adopted to this cluster). `CM_MANUAL` = no APs adopted (multizone anchor or DMZ/unused). This is the **recommendation**; the operator confirms or overrides the gateway topology in the Stage 6.5 questionnaire (and confirms the AOS 10 *target name* / placement classification when a heuristic misfires).

### REGRESSION findings (verdict-gating — must fix before migration)
These are the **target-architecture-INDEPENDENT** (bucket 2/3) REGRESSIONs that compute the verdict. Findings only fire when their applicability gate is met (see Stage 3). Possible verdict-gating REGRESSIONs include:
- **Mobility Conductor firmware below 8.10.0.12 / 8.12.0.1**: <conductor + running version>. (O1, VSG §1643)
- **TCP 443 to Central blocked from <subnet>**: required for AOS 10 management. (O2, VSG §312-§319)
- **GreenLake AP-license capacity insufficient**: source has <M> APs; GreenLake reports <N> active AP licenses. (O3, VSG §1619-§1620)
- **Central unreachable** / **GreenLake capacity** (Stage 4a A1 / A2). (A1, A2)
- **AAA FastConnect (EAP-Offload) in use**: <auth profiles using it>. Plan ClearPass-only termination. (F1, VSG §1137)
- **Internal Auth Server in use with local users**: <user count>. Migrate to ClearPass / Cloud Auth. (F2, VSG §1134)
- **Captive Portal default certificate in use**: replace before cutover. (F9, VSG §364)
- **Internal management LAN blocks Internet**: TCP 443 to Central required. (F10, VSG §315-§317)
- (or "No verdict-gating REGRESSION findings.")

### Provisional (target-dependent) findings — re-scored after Stage 6.5, NOT verdict-gating
These are bucket-4 findings scored against the **recommended** target only. They do **NOT** count toward the verdict and never produce BLOCKED — they're re-evaluated against the operator's Stage 6.5 choices and folded into the Act II plan (an operator who picks a different mode makes the relevant ones vanish). Surface each as *"provisional (recommended target = <mode>); re-scored after Stage 6.5"*:
- **L3 Mobility load-bearing** [recommended Bridge/Mixed → REGRESSION; Tunnel → DRIFT]. (F3, VSG §897-§900)
- **VC-managed (NAT'd) WLANs without upstream NAT/DHCP plan** [Bridge/Mixed]. (F4, VSG §854-§857)
- **Tunneled-SSID VLAN present on AP switch port** [Tunnel]. (T3) · **VLAN 1 used for tunneled-SSID clients** [Tunnel]. (T4)
- **AP management subnet routed (not L2)** [Bridge/Mixed]. (B2) · **AP switch ports access-mode-only** [Bridge]. (B4) · **Secure PAPI (UDP 8211) blocked between APs** [Bridge]. (B5)
- **Mixed Mode + bridged/tunneled VLAN reuse** [Mixed]. (M2)
- **ClearPass NAD coverage** for new AP subnets [Bridge/Mixed] (A4) / cluster gateways+VRRP VIPs [gateways survive] (A5).
- (or "No provisional target-dependent findings.")

### DRIFT findings (should address; not blocking)
- **AirWave in path**: monitoring tooling that depends on AirWave needs replacement. (F6, VSG §312)
- **Static AP IPs detected** (AP-only): <list>. APs need DHCP for the initial Central onboarding window (Aruba Activate + first call-home); operator can re-pin static IPs **after** APs are adopted. Gateways and switches do not share this constraint. (F5, VSG §1232)
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
- **Cluster mode classification** (detected per Stage 7 Step 4; confirmed in Stage 6.5): <one bullet per source `cluster_prof`, e.g. "`<cluster-name>` at `<scope>` → CM_SITE (primary zone for N APs)" or "`<cluster-name>` at `<scope>` → CM_MANUAL (multizone anchor for AP-group `<X>`)" or "`<cluster-name>` at `<scope>` → CM_MANUAL (active cluster, no APs adopted)">.
- **External multizone target**: AP-group `<X>` multizone profile `<Y>` references `<ip>` — not in any source `cluster_prof`, not managed by this conductor. External standalone controller; migrates to a single Central gateway, not a `gw-cluster`. Operator confirms placement. (One bullet per external IP; emit nothing when the multizone target is in `cluster_prof` member list or in the conductor's own `aos8_get_controllers` list.)
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

> If verdict = EMPTY-SOURCE (note: yes/no only — no edit-context, and Stage 6.5 is skipped):
Verdict: EMPTY-SOURCE — no customer-defined config found; there is nothing to translate beyond AOS 8 defaults. Proceed anyway to see the default-only plan? (yes / no)
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
**Per-SSID target forward mode (Stage 6.5 decisions):** <one line per SSID: `<source_scope>/<vap-name>` → Bridged | Tunneled | Bridged-and-Tunneled | Hybrid (recommended: <X>; operator <confirmed | changed to Y>)>. There is no single deployment-wide mode — each SSID carries its own decision (a mix of Bridged + Tunneled SSIDs is normal).

### Hierarchy translation (Stage 7)
| Source AOS node | Source path | Disposition | Target type (AOS 10) | Inferred Device Function | Cluster mode signal | Target name | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|
| <Mobility Conductor /md> | `/md` | drop | (none) | n/a | n/a | n/a | high | Central org root is implicit |
| <region with child Groups> | `/md/<region>` | direct-translate | Site Collection | n/a (container) | n/a | <name> | high | child Group nodes present |
| <site with APs adopted to cluster X> | `/md/<region>/<site>` | direct-translate | Site | CAMPUS_AP | CM_SITE (derived: primary zone for N APs) | <name> | high | cluster_prof.cluster_controller[].ip matched ap_database Switch IP |
| <DMZ cluster — multizone anchor> | `/md/<region>/<dmz-cluster>` | direct-translate | Device Group | MOBILITY_GW | CM_MANUAL (derived: multizone anchor for `<ap-group>`) | <name> | medium | cluster_prof present, no Switch IP match, multizone reference found |
| <active cluster — no APs, no multizone> | `/md/<region>/<unused-cluster>` | direct-translate | Device Group | MOBILITY_GW | CM_MANUAL (derived: no APs adopted, no multizone reference) | <name> | medium | cluster_prof present, no Switch IP match, no multizone — DMZ or unused |
| <persona-named VPNC node> | `/md/<region>/<vpnc-node>` | direct-translate | Device Group | VPNC | n/a (no cluster_prof) | <name> | medium | persona token in name; Device Group with Device Function = VPNC filters which device types receive profiles |
| <ap-group / static device group> | `/md/<region>/<site>/<ap-group>` | direct-translate | Device Group | CAMPUS_AP | n/a | <name> | medium | per-function device grouping |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Per-object disposition matrix (Stage 8)
| Source name | Source type | Source scope | Usage state | Disposition | Target name | Target type | Central tool | VSG anchor | Notes |
|---|---|---|---|---|---|---|---|---|---|
| corp-radius-1 | rad_server | /md/ACX | assigned-and-active | transform | corp-radius-1 | Server | [Central API gap — manual UI: Network Services → Servers] | §1121 | NAS-IP source must change to gateway IP for Tunnel target |
| CPPM-PUB-ONLY | server_group_prof | /md/ACX | configured-but-unassigned | transform | CPPM-PUB-ONLY | Server group | [Central API gap — manual UI: Network Services → Server Groups] | §2076 | Orphan in source — operator may choose to skip |
| corp-employee | role | /md/ACX | assigned-and-active | transform | corp-employee | Role | central_manage_roles | §1173 | per-attribute mapping required (VLAN, ACL list, captive-portal, session-timeout) |
| ACX_apsys_ui | ap_sys_prof | /md/ACX | configured-but-unassigned | transform | ACX_apsys_ui | (none — folded into Device Group config) | [Central API gap — manual UI] | §1651 | Profile not bound to any active ap-group, but still translates per principle |
| corp-ssid-prof | ssid_prof | /md/ACX | assigned-and-active | direct-translate | corp-ssid-prof | WLAN profile | central_manage_wlan_profile | §2127-§2219 | direct field map per CorpNet 802.1X worked example |
| arm-default | arm_prof | /md | configured-but-unassigned | deprecated | n/a | (none) | (none) | §1163 | Replaced by RF Profiles in AOS 10 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### OPERATOR-MAP findings (manual mapping work items)
- **OPERATOR-MAP** — User role 'corp-employee' requires per-attribute mapping. Set role's VLAN, ACL list, captive-portal, session-timeout in the Central role payload. (VSG §1173) (source: aos8_get_effective_config(object_name='role', config_path='/md', entry_type='user'), Batch 1)
- **OPERATOR-MAP** — TACACS server 'tacacs-mgmt' has no automated translation rule. Configure manually in Central UI under Network Services → Servers. (VSG none) (source: aos8_get_effective_config(object_name='tacacs_server', config_path='/md', entry_type='user'), Batch 1)
- **OPERATOR-MAP** — Session ACL 'employee-acl' has 14 rules; per-rule translation to Central role-acl is operator-driven. Map net-destinations to net-groups, ports to net-services, then re-emit ordered rule list. (VSG none) (source: aos8_get_effective_config(object_name='acl_sess', config_path='/md', entry_type='user'), Batch 1)
- ... (one bullet per `operator-driven` row in the matrix)
- (or "No OPERATOR-MAP findings.")

### Central API call sequence (Stage 9)
1. **Site Collection 'USE'** — `central_manage_site_collection` — payload sketch: name='USE', parent=root — depends on: none — notes: hierarchy first.
2. **Site 'dallas-hq'** — `central_manage_site` — payload sketch: name='dallas-hq', parent_collection='USE' — depends on: 1 — notes: standard.
3. **Device Group 'dallas-hq-floor-3'** — `central_manage_device_group` — payload sketch: name='dallas-hq-floor-3', parent_site='dallas-hq' — depends on: 2 — notes: standard.
4. **Net group 'corp-internal-subnets'** — `central_manage_net_groups` — payload sketch: name='corp-internal-subnets', members=['10.10.0.0/16', '10.20.0.0/16'] — depends on: none — notes: ACL primitive.
5. **[Operator pre-populate] Net service 'rdp'** — `central:net_service` is DEFERRED, so a custom service alias like `rdp` (tcp/3389) must be pre-created in Central by the operator (Network Services → Services) before the role-ACL references it. No `central_manage_net_services` step is emitted. (Built-in `svc-*` services need nothing.) — depends on: none — notes: net-service translation pending.
6. **Role ACL 'employee-acl'** — `central_manage_role_acls` — payload sketch: name='employee-acl', rules=[{src=any, dst='corp-internal-subnets', svc='rdp', action=permit}, ...] — depends on: 4 (and the operator-pre-populated 'rdp' service from step 5) — notes: rules in original AOS 8 ordering.
7. **Role 'corp-employee'** — `central_manage_roles` — payload sketch: name='corp-employee', vlan=200, access_list_session=['employee-acl'], captive_portal=null, session_timeout=86400 — depends on: 6 — notes: per-attribute mapping operator-driven.
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
