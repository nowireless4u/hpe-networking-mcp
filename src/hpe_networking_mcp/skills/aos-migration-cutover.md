---
name: aos-migration-cutover
title: AOS 8 → AOS 10 migration — execution, cutover and post-conversion triage
description: |
  EXECUTION companion to the plan-only `aos-migration` skill. Run
  `aos-migration` first for the readiness verdict and the config
  translation plan; then run THIS skill to carry the plan out: GreenLake
  claim + entitlement, persona, AOS 10 group + site placement, rebuilding
  WLAN / RADIUS / role config in the Central config model, the
  controller-side `ap convert` flow, cutover, and post-conversion
  verification and triage.

  Trigger phrases include: "convert the APs", "ap convert", "pre-validate",
  "cutover to AOS 10", "converted AP is Out of Sync", "converted AP
  broadcasts nothing", "No group(Central)", "No license(Central)",
  "API_ACCESS_RESTRICTED_IN_HYBRID_CLUSTER", "CONFIG_PUSH_FAILURES",
  "Reason Code 48 after conversion", "role assigned was Deny All",
  "Config eliminated", "Downlink Packet Drops on eth1", "casting stopped
  working after migration", "AirGroup after AOS 10", "roll back a
  converted AP", "pre-stage the estate", "monitor-only switches in
  Central".

  Also covers bringing AOS-CX / AOS-S switches into Central in
  MONITORING-ONLY mode alongside the wireless migration. Most writes are
  gated (ENABLE_GREENLAKE_WRITE_TOOLS / ENABLE_CENTRAL_WRITE_TOOLS); several
  steps have no MCP tool and are given as the documented REST endpoint or
  UI path.
platforms: [central, greenlake, aos8]
tags: [central, greenlake, aos8, aos10, migration, cutover, conversion, onboarding, airgroup, radius, verification, rollback, switches, monitor-only]
tools: [health, skills_load, greenlake_bulk_add_devices, greenlake_post_devices_v1_devices, greenlake_get_devices_v1_devices, greenlake_get_devices_v1_async_operations_id, greenlake_patch_devices_v1beta1_devices, greenlake_get_subscriptions_v1_subscriptions, greenlake_get_service_catalog_v1_service_manager_provisions, central_manage_persona_assignment, central_manage_device_group, central_create_device_group_with_devices, central_add_devices_to_device_group, central_add_devices_to_site, central_manage_site, central_get_sites, central_get_scope_tree, central_get_system_info, central_get_gateway_clusters, central_get_wlan_profiles, central_manage_wlan_profile, central_get_config_assignments, central_manage_config_assignment, central_get_auth_servers, central_manage_auth_servers, central_manage_server_groups, central_get_roles, central_manage_roles, central_get_role_gpids, central_manage_role_gpids, central_get_policies, central_manage_policies, central_get_policy_groups, central_manage_policy_groups, central_get_captive_portal, central_get_airgroup_system, central_manage_airgroup_system, central_get_airgroup_service_definitions, central_get_device_config_issues, central_get_devices_config_health, central_get_wlans_monitoring, central_resync_device_config, central_show_commands, central_list_supported_show_commands, central_get_audit_logs, central_get_audit_log_detail, central_get_switch_stack_members, aos8_show_command, aos8_get_active_aps, aos8_get_ap_database, aos8_get_effective_config, aos8_parse_config, central_invoke_tool, greenlake_invoke_tool]
---

# AOS 8 → AOS 10 migration — execution, cutover and post-conversion triage

## Objective

Take controller-managed AOS 8 campus APs from "the translation plan is
approved" to "converted, serving every SSID, authenticating correctly, and
verified" in HPE Aruba Networking Central — and triage the failure modes that
only appear after conversion. The runbook covers the GreenLake and Central
prerequisite chain, a bulk pre-stage for an estate, rebuilding configuration
in the Central config model, the controller-side `ap convert` flow, per-AP
rollback, the post-conversion checks, and (optionally) onboarding the
switching estate in monitoring-only mode.

**Plan with `aos-migration`, execute with this skill.** `aos-migration` is the
assessment and planning half: the `/md` hierarchy walk, per-object translation
rules, feature-parity findings, the target-architecture questionnaire and the
ordered Central API call sequence. It is read-only and describes the cutover
phases as operator actions. This skill starts where it stops — claiming
devices, creating groups, running `ap convert`, and diagnosing an AP that is
online and silent. Where both skills cover a step, `aos-migration` wins.
For the GreenLake add / subscribe / assign mechanics, `greenlake-device-onboarding`
is the primary runbook; this skill adds only the ordering, the batch ceilings
and the read-backs an estate-sized run needs.

Mobility Gateway system-IP, gateway clusters and tunnel anchoring are out of
scope.

### Evidence labels

Each step carries how well it is evidenced. Keep the label when quoting a step
to a customer.

| Label | Meaning |
|---|---|
| `[doc-grounded]` | Stated in vendor documentation (source given) |
| `[proven]` | Observed in a lab rehearsal or in production migrations, with read-back |
| `[observed]` | Seen, but in one environment or one release only |
| `[unverified]` | Not established — do not present as fact |

## Prerequisites

- `aos-migration` has been run: readiness verdict is not BLOCKED and the
  operator has an approved translation plan (`skills_load('aos-migration')`).
- Platforms reachable: `health(platform='central')`,
  `health(platform='greenlake')`, `health(platform='aos8')`.
- Write tools enabled where this skill writes: `ENABLE_GREENLAKE_WRITE_TOOLS`
  and `ENABLE_CENTRAL_WRITE_TOOLS`. Every write is a change to the customer's
  production tenant — confirm scope with the operator before each phase.
- SSH (interactive, PTY-capable) to the AOS 8 controller / Mobility Conductor
  for `ap convert`. `ap convert` is exec-only and is not exposed as an `aos8_*`
  tool.
- For hybrid tenants: a **Classic Central API token**. The Classic API gateway
  is a separate host with a separate OAuth token; a New Central / GreenLake
  token returns 401 there. Mint it from Classic Central → API Gateway → My Apps
  & Tokens → Add Apps & Tokens → Generate (TTL about 2 hours; a refresh-token
  grant can renew it). Keep it out of chat; delete the app afterwards to revoke.
- The AOS 8 configuration you are migrating from (running-config or
  `aos8_get_effective_config` output) — several gates below compare against it.

**Authoritative references** (read the vendor procedure before running a step;
the lab confirms the doc, it does not replace it):

- Validated Solution Guide — ESP Campus Migrate, AOS 8 to 10 upgrade steps:
  `arubanetworks.com/techdocs/VSG/docs/035-campus-migrate/esp-campus-migrate-060-aos8to10upgrade-steps/`
- Migrating APs to AOS 10: `.../content/aos10x/cfg/aps/ap-migration.htm`
- Migrating to AOS 10 (index): `arubanetworking.hpe.com/techdocs/aos/aos10/migrate/`
- New Central hierarchy: `developer.arubanetworks.com/new-central/docs/new-central-hierarchy`
- Official onboarding workflow: `github.com/aruba/central-python-workflows` → `device-onboarding/onboarding.py`

**Hard signal:** if satisfying a prerequisite requires token gymnastics — CORS
dodges, browser-window bridges, swagger hacks — stop; you are off the
documented procedure. (The Classic `devices/move` call below is documented: the
vendor's own onboarding workflow performs it.)

**Config is recreated in the Central config model, never cloned verbatim from
the controller.** A verbatim clone produces "Custom mode" WLANs full of
`no <field>` lines that AOS 10 rejects, plus country-code and AP-system profile
churn. `[proven]`

## Procedure

### Phase 0 — Establish the deployment mode

#### Step 0.1 — Standalone, hybrid or on-premises

**Tool:** Central UI (look for a "Classic Central" toggle); `central_get_scope_tree()` to confirm New Central reads work.
**Why:** `[doc-grounded]` There are three documented deployment modes
([Deployment Modes in HPE Aruba Networking Central](https://arubanetworking.hpe.com/techdocs/CNX-CNXOP-NewHelp/HPE%20Aruba%20Networking%20Central/GUID-B0D6E537-6A53-4BBB-9EEF-ADB1C20AEB7C.html)):
**Standalone** ("supports all features natively without switching back to the
HPE Classic Central interface"), **Hybrid** ("certain operations still require
switching to the HPE Classic Central interface… used during the transition
period"), and **On-Premises** (a standalone single-node setup is not supported
on-premises). Every Classic-API fallback in this skill applies to **hybrid
tenants only**.
**Expected result:** mode recorded before any planning. The hybrid tell is the
Classic Central toggle.
**If anomaly:** that vendor page is client-rendered — a plain HTTP fetch returns
an empty body. An empty fetch is a rendering artifact, not vendor silence.

What changes in hybrid `[proven]`:

| Operation | Standalone New Central | Hybrid |
|---|---|---|
| Device → group membership | `central_add_devices_to_device_group` | Classic `POST configuration/v1/devices/move` only |
| Group create | `central_manage_device_group` | Classic `POST configuration/v3/groups` (Step 1.5) |
| Site create | `central_manage_site` | `central_manage_site` (works) |
| Site device-assign | `central_add_devices_to_site` | Classic API / CSV upload / Classic UI (Step 4.1) |
| Config-model writes (WLAN, VLAN, AAA, role) | works | **works — not blocked** |

On a hybrid tenant the New Central membership APIs return HTTP 400
`API_ACCESS_RESTRICTED_IN_HYBRID_CLUSTER`. That is membership only — do not
conclude the whole config API is blocked.

### Phase 1 — Prerequisite chain and estate pre-stage (no window needed)

Everything in this phase happens **before** any conversion window. Nothing
here touches a controller or interrupts a live AP. For an estate, run it days
ahead; conversion day then only runs Phase 3.

The order matters `[proven]`:

```
claim → assign to the Central application → subscription → persona → group → site
```

A handoff that says "the AP is onboarded, just set persona / move the group" is
a claim, not a fact — verify the whole chain from the top; the real blocker is
usually further upstream.

#### Step 1.1 — Claim the devices into the GreenLake workspace

**Tool:** preferred `greenlake_bulk_add_devices(...)` via the `greenlake-device-onboarding` runbook (add + subscribe + assign in one call, resumable). Where driving the API phases directly: `greenlake_post_devices_v1_devices` (`POST /devices/v1/devices`, serial + MAC).
**Why:** nothing downstream accepts a serial the workspace does not hold.
**Expected result:** every serial present in `greenlake_get_devices_v1_devices`.
**If anomaly:**
- **Batch ceiling** `[proven]`: claims in batches of **5** returned `202 ACCEPTED`;
  batches of 10, 25 and 50 all returned
  `400 HPE_GL_DM_TOO_MANY_DEVICES_CLAIMED` ("Claim device count limit
  exceeded") and **nothing** was claimed. A script that logs the 400 and
  continues "finishes" having done nothing. Probe one batch and read the answer
  before an estate-sized run. These are server-side limits and not in vendor
  documentation — re-probe rather than trusting the number.
- **A 202 is not a claim** `[proven]`. The only evidence is the device in
  inventory. Read back more than once: one serial appeared only on a read-back
  roughly 15 minutes after its batch. Another never appeared across two 202s;
  its transaction id returned **404** from
  `greenlake_get_devices_v1_async_operations_id`, so the API audit trail was
  empty. Claiming that serial **by hand in the GreenLake UI** printed
  *"Device(s) with serial number: `<serial>` is blocked or invalid."* — an
  HPE-side condition cleared by HPE support. When a serial will not land, the
  UI claim is the diagnostic, not the API; do not hunt for a typo.
- A **used / second-hand AP** is locked to the prior owner's GreenLake account
  and must be released there first; it also carries the prior owner's config
  and credentials. The serial is not on the wire (LLDP gives the MAC) — you
  need the label or a factory reset.

#### Step 1.2 — Assign to the Central application, then attach the subscription (two PATCHes, in that order)

**Tool:** `greenlake_patch_devices_v1beta1_devices` — first `{"application":{"id":"<service-manager UUID>"},"region":"<region>"}`, then a **second** call `{"subscription":[{"id":"<subscription resource id>"}]}`. Resolve the service-manager id with `greenlake_get_service_catalog_v1_service_manager_provisions`. UI alternative: Asset Explorer → Actions → Assign to service → HPE Aruba Networking Central + region (lands in New Central inventory in about 2 minutes).
**Why:** `[proven]` reversed, the subscription PATCH is accepted (HTTP **202**)
and does nothing at all — a silent no-op found only on read-back.
**Expected result:** read-back shows the application, region and subscription on every serial. Batches of 25 returned 202 (higher not probed).
**If anomaly:**
- **Verify the subscription is VALID, not merely available.** Check
  `subscriptionStatus` / `endTime` in `greenlake_get_subscriptions_v1_subscriptions`,
  never `availableQuantity`. An expired evaluation still reports seats; the
  assignment then fails asynchronously with no reason, the UI says "no
  subscription available to select", and `ap convert pre-validate` later fails
  `No license(Central)`. `[proven]`
- The bulk-add path has been observed to return 500 and not enrich an
  already-claimed device; use the two direct PATCHes for that case.

#### Step 1.3 — Persona (Device Function) = Campus Access Point

**Tool:** `central_manage_persona_assignment(...)` (`POST /network-config/v1alpha1/persona-assignment` with `CAMPUS_AP`); read back the Device Function in New Central Device Inventory. UI: New Central → Device Inventory → select AP → Assign → Campus Access Point.
**Why:** `[doc-grounded]` persona is the API name for the UI's Device Function
([Device Function and Persona](https://developer.arubanetworks.com/new-central/docs/device-function-and-persona)).
The UI panel sets function **only** — it offers no group or site control.
**Expected result:** `200 SUCC_001` per batch.
**If anomaly:** `[proven]` batches of **50** succeed; 100 returns `400` "Device
function assignment API cannot have more than 50 requests". One estate run
failed here after claim, application and subscription had all succeeded — a run
can be mostly correct and still leave the estate unusable.

#### Step 1.4 — Decide the group construct

**Tool:** none — decision.
**Why:** `ap convert pre-validate` **hard-requires** Central group membership
(Phase 3). Persona plus subscription is not enough; pre-validate returns
`No group(Central)` until the AP is in a group. Staging config at Global scope
does not get around it: Global helps config *apply* after the AP joins, but the
controller blocks *conversion* on group membership. `[proven]`
**Expected result:** standalone tenant → New Central device group
(`central_manage_device_group` / `central_create_device_group_with_devices`);
hybrid tenant → Classic group, Step 1.5.
**If anomaly:** see Step 1.6 — the group construct determines whether config ever deploys.

#### Step 1.5 — Create the AOS 10 AP group (hybrid: via the Classic API)

**Tool:** no MCP tool for Classic groups — `POST configuration/v3/groups`:

```
{
  "group_attributes": {
    "group_properties": {
      "Architecture": "AOS10",
      "ApNetworkRole": "Standard",
      "NewCentral": true,
      "AllowedDevTypes": ["AccessPoints"]
    }
  },
  "template_info": { "Wired": false }
}
```

**Why:** the most expensive silent failure in this migration is an AP that is
online, in a group, and **Out of Sync with no SSIDs on air**, because the New
Central device-collection `deviceCount` stayed 0 and group config never
deployed. A Classic `devices/move` genuinely puts the AP in the Classic group
but does **not** populate the New Central device-collection if the group was
created without these attributes (for example a UI-made group). `[proven]`
**Expected result:** the group appears in `GET network-config/v1/device-groups`.
**If anomaly:** a group built in the UI that stays at `deviceCount` 0 after a
successful move is the known-bad case — rebuild it via the API.

#### Step 1.6 — Move the APs into the group and confirm `deviceCount`

**Tool:** Classic `POST configuration/v1/devices/move` `{"group":"<AOS10 group>","serials":["<serial>", ...]}`; standalone: `central_add_devices_to_device_group`.
**Why:** group membership is the pre-validate gate.
**Expected result:** `200 Success` (batches of 50 succeeded). The response has
no per-device detail — read back `group_name` on Classic `GET monitoring/v2/aps`.
**Confirm New Central `deviceCount` > 0 on the first AP you convert.**
**If anomaly:** `[proven]` a bulk-staged AP that has **never** connected reads
`deviceGroupName: None` in New Central and the group's `deviceCount` does not
rise, even though Classic reports the group correctly. That is **expected** and
resolves on first connection — it is not the Step 1.5 failure. The two look
identical on the read; they are distinguished only by whether the device has
ever checked in. The `deviceCount` check is therefore a post-connection check on
the first converted AP.

#### Step 1.7 — Site assignment for devices that have never checked in (bulk CSV)

**Tool:** UI — New Central → **Global → Device Inventory → Assign by CSV Upload → Upload CSV File**. Required columns `Serial Number` and `Site`; `Device Function` optional (persona can ride along).

```
Serial Number,Site
<serial>,<site>
<serial>,<site>
```

**Why:** `[proven]` for claimed-but-never-connected serials, the Classic site
API returns per-device `SITE_ASSOC_ERR_DEVICE_NOT_PRESENT` and Classic Manage
Sites does not list them. The CSV is the only path that reaches them. It is a
real file picker — budget a human at the keyboard.
**Expected result:** one Central job, status COMPLETED. Read back on
`GET network-config/v1alpha1/devices` paged at `limit=100` (larger returns 400)
and compare per-site counts with the CSV. That endpoint lists **sited devices
only** — before the upload a fully staged estate reads as nearly empty, which is
not a failure.
**If anomaly:** for devices Central already knows, use Step 4.1.

#### Step 1.8 — Report the gap by name

**Tool:** read-backs from Steps 1.1–1.7.
**Why:** a staging run should not abort an estate on one bad serial, and must
not report a bare count either.
**Expected result:** each phase re-reads inventory, operates on present serials,
and ends with e.g. *"of N: in workspace N-1, assigned N-1, subscribed N-1, NOT
in workspace 1"* followed by the missing serial. Re-running picks it up later.
**If anomaly:** missing after ~10 minutes and on a second read → UI claim
(Step 1.1).

### Phase 2 — Recreate the configuration in Central

Follow the `aos-migration` translation plan for object placement. The steps
below are the execution gates that plan does not cover.

#### Step 2.1 — Understand the scope model before placing config

**Tool:** `central_get_scope_tree()`, `central_get_config_assignments(...)`.
**Why:** `[doc-grounded]` hierarchy is **Library > Global > Site Collection >
Site > Device**, device-level config has the highest precedence, and "Device
Groups are an optional parameter in Central that cuts across the entire
hierarchy… devices can only belong to one group". Device groups apply
**device-level** config. `[proven]` WLANs defined at a site scope did not reach
an AP because the AP's WLAN-bearing device group overrode them. To run a
site / collection-scoped model, APs must not sit in a WLAN-bearing device group.
**Expected result:** a placement decision per object.
**If anomaly:**
- A scoped GET returns **shared / effective** objects (inherited, merely
  visible), not objects defined there; editing at that scope then fails
  `... name='X' doesn't exist`. Confirm an object's real home via
  `aruba-annotation:scope_device_function` on a `detailed=True` read.
- The patchable instance is the **device-collection-scoped** one. A shared WLAN
  can be assigned at a site-collection scope (it inherits and broadcasts) but
  its fields cannot be patched there via the API — use the UI.
- Scoped API reads have failed to reflect freshly created profiles; verify WLAN
  placement in the UI (Device Group scope → Wireless → WLAN Manage).
- Rehoming SSIDs to a shared collection-level model: assign `wlan-ssids` + its
  `layer2-vlan` + (802.1X) `auth-servers` and `server-groups` at the collection,
  fix the `no <field>` rejections that appear on the other sites' APs via the
  UI, then remove per-site duplicates. Removing a `wlan-ssids` assignment
  auto-removes its dependent `roles` / `role-gpids` (removing them separately
  400s `not scope-mapped`); the row action is **Delete** for a scope-local
  object and **Unassign** for a shared one.

#### Step 2.2 — Create each WLAN with the fields that stop `no <field>` emission

**Tool:** `central_manage_wlan_profile(...)`, then bind with `central_manage_config_assignment(...)` (explicit config-assignment).
**Why:** `[proven]` Central emits `no <field>` for WLAN fields left unset, AOS 10
rejects the whole block, and the AP goes `CONFIG_PUSH_FAILURES` / `OUT_OF_SYNC`
(sometimes while the SSID is still on air). Include in the **create** payload:

```
dtim-period: 1
broadcast-filter-ipv4: BCAST_FILTER_ARP
dmo: { "channel-utilization-threshold": 70 }   # must be non-default; a default
                                               # value is optimized away and
                                               # re-emits `no`
```

**Expected result:** WLAN created and assigned. `dmo` is an exposed container
(in the UI its threshold is read-only until the DMO checkbox is ticked).
**If anomaly:** a resync does not fix this — it re-pushes the same `no` lines.
Do not attribute these failures to AP firmware; that theory was tested and
disproved (the failures persisted after an AP upgrade).

#### Step 2.3 — Enable each WLAN

**Tool:** `central_manage_wlan_profile(...)` or UI: Config (device-group scope) → Wireless → WLAN → row kebab → Enable → confirm. Per SSID.
**Why:** `[proven]` New Central creates WLAN profiles **Disabled** by default.
Symptom: AP online, Configuration Status Out of Sync, no SSIDs, empty
`show ap bss-table`. A valid country code is necessary but not sufficient.
**Expected result:** `central_get_wlans_monitoring` shows status ENABLED (about a minute of lag).
**If anomaly:** the WLAN editor blocks Save **silently** on an invalid field deep
in Advanced — usually an empty *Max Clients (Per Radio, Per AP)*, visible only
after scrolling. WPA2-Enterprise / legacy key management stays greyed out until
the 6 GHz band and Wi-Fi 7 are disabled.

#### Step 2.4 — RADIUS servers, server groups, and the shared secret

**Tool:** `central_manage_auth_servers(...)` (address, ports, `type: RADIUS`, `radius-server-mode: AUTH_AND_COA`, CoA), `central_manage_server_groups(...)`.
**Why:** `[proven]` the `auth-server` object exposes no shared-secret / key field
in the config-model API — the secret is a UI / out-of-band step.
**Expected result:** `server-group` carries
`servers: [{"server-name":"<auth-server>","position":1}]` — `position` is
mandatory or the WLAN config-assignment fails; the auth-server must exist first.
**If anomaly:**
- In the WLAN editor the Server Group dropdown offers only "Primary And Backup
  Only" / "Central NAC"; an API-created server group does not appear. Bind the
  RADIUS server via **Primary Server**.
- **A secret mismatch is silent.** ClearPass masks the secret on every read and,
  per RFC, discards mismatched packets: zero hit count, no Access Tracker entry.
  That is indistinguishable from "the AP isn't sending". Set the same secret on
  both ends, then prove with a real client.
- "Client authenticates but gets no IP" is a DHCP / VLAN item, not auth.

#### Step 2.5 — Carry the RADIUS attributes the conversion drops

**Tool:** `aos8_get_effective_config(...)` or the raw config for every `aaa authentication-server radius` block; `central_get_auth_servers`; `central_manage_wlan_profile(...)` for the per-WLAN fix.
**Why:** `[proven]` the conversion carries host, port, key and NAS-IP and little
else. Two drops break authentication the moment the first AP converts, and both
are visible in the AOS 8 config you already hold. Compare the whole block
attribute by attribute.

**(a) `called-station-id` moves from the server to the WLAN.** AOS 8 sets it once
per auth server, so every SSID inherited it:

```
aaa authentication-server radius "<server>"
   called-station-id type macaddr include-ssid enable delimiter colon
```

New Central's `auth-server` has no such field; it is per WLAN:

```
PATCH /network-config/v1alpha1/wlan-ssids/<wlan>
{"called-station-id": {"type": "MAC_ADDRESS", "include-ssid": true}}
```

It renders on the AP as `called-station-id include-ssid` in the SSID profile —
read back about two minutes after the PATCH (not present at one minute). The
default is a bare MAC, so **a RADIUS policy keyed on SSID stops matching at
conversion**. Windows NPS signature: event **6273**, Called Station Identifier =
AP MAC alone, Network Policy `-`, **Reason Code 48** ("did not match any
configured network policy"). Set it on every WLAN that used that server, or
establish per NPS policy whether it conditions on Called Station ID — absence of
the symptom on one SSID says nothing about the next. Other candidates for the
same class of break: RADIUS-client friendly name and NAS-Identifier conditions.

**(b) The RADIUS client list moves from the controllers to every AP.**
`[doc-grounded]` Campus Migrate VSG feature table: *"Bridge Mode: Source IP is
the individual AP's management address."* A server that lists only the
controllers drops everything else silently (Windows NPS does). The AP-management
subnet is **per campus** — one estate had 13 distinct pairs, readable from each
campus's AP port profile and core SVIs. Every one must be a RADIUS client with
the existing shared secret, and any filter must allow UDP 1812, **before** that
campus converts. This is the customer's change — raise it earliest.

**Expected result:** after conversion, `show ap debug radius-statistics` (Step 4.3)
shows responses and the per-server line `Up`.
**If anomaly:** `[proven]` signature of (b): requests in the dozens, **responses 0**,
timeouts climbing, and **Invalid Secret, Access-Accept and Access-Reject all 0**,
per-server line `Down but trying`. Zero responses with zero Invalid Secret means
"the server never answered" — not a secret mismatch and not "the AP isn't
sending". It flips to `Up` within a minute or two of the server-side fix.

**Lab caveat:** a RADIUS stand-in pre-provisioned with the lab AP's own subnet
cannot reproduce (b). Build every simulated dependency to match what the
customer's real server knows **today**.

#### Step 2.6 — Check AOS 8 dot1x termination before making a certificate claim

**Tool:** `aos8_get_effective_config(...)` / raw config — grep `aaa authentication dot1x` profiles for `termination enable`.
**Why:** `[doc-grounded]` AOS 8 CLI reference, `aaa authentication dot1x`:
`termination enable` — "Enables 802.1X termination on the managed device.
**Default: disabled**". `termination eap-type ...` / `inner-eap-type ...` lines
alone parameterise a mode that is not switched on.
**Expected result:** a count of `termination enable` hits, each named to its profile, before asserting whose certificate clients saw.
**If anomaly:** `[unverified]` whether AOS 8 terminates on `eap-type` alone. In
bridged AOS 10 the AP passes PEAP through, so the server's certificate is what
clients see; the fix is server- or client-side (push the CA or a Wi-Fi profile
via GPO / MDM). AP-side EAP termination in AOS 10 is not established — do not
offer it.

#### Step 2.7 — Assign each role AND its policy at the same sites

**Tool:** `central_get_config_assignments(...)` for the role and for its policy; `central_manage_policy_groups(...)`, `central_manage_policies(...)`, `central_manage_roles(...)`, `central_manage_role_gpids(...)`, `central_manage_config_assignment(...)`.
**Why:** `[proven]` a role assigned at a site whose policy is **not** assigned
there renders with **no rules**. Central accepts each half independently and
returns 200 for both. Symptom: client authenticates, gets the right role name,
has no access; client event *"authenticated and the role assigned was Deny All"*;
on the AP, `show running-config` has the SSID's `set-role-default <role>` and no
`wlan access-rule <role>` block. In one estate the role was assigned at 19 sites
and its policy at one — the lab site, which is why the lab could not show it.
**Expected result:** identical site sets for each role / policy pair, checked in
both directions (no role without its policy; no role-based policy without its role).
**If anomaly:**
- A policy must be in the global `policy-groups` list before it can be assigned,
  else `400 "Policy ... not part of Policy Group"`. Add it, then assign.
  A UI policy delete also removes the policy-group entry; an API `DELETE` of a
  policy still listed is refused *"still part of Policy Group"*, and
  `PUT policy-groups` was not allowed — do that step in the UI.
- Removal order: `roles` **before** `role-gpids`. Deleting `role-gpids` first
  leaves an undeletable `roles` row (`not scope-mapped`); recover by re-adding
  the role-gpid, deleting the roles row, then the role.
- Before deleting anything, search **every** object type for references,
  including system-generated ones (a role delete was refused by a reference
  from `sys_cnac_<wlan>`, see Reference). Capture a `config-assignments`
  backup first — it makes a restore one script.
- Objects cannot be renamed in place: create new, add to policy-groups, assign,
  verify on an AP, then unassign and delete the old. A rename re-pushes rules to
  every converted AP twice — schedule it after hours.

#### Step 2.8 — Re-express punch-through rules as role-sourced rules

**Tool:** `central_get_policies(...)`; after conversion, the AP's rendered `wlan access-rule` block (Step 4.3, `show running-config`).
**Why:** `[proven]` AOS 10 does not render **network-sourced / host-sourced**
rules, `any -> role` rules, or IPv6 rules from a role-based policy (Central logs
"Config eliminated … Policy Rule 'N' … unsupported"). A role-sourced
`deny 10/8` renders; the network-sourced permits written above it for internal
resolvers and management hosts do not — so clients in that role lose DNS while
the policy reads correct in Central.
**Expected result:** every punch-through rewritten as a role-sourced rule above the deny, and the rendered order confirmed on the AP.
**If anomaly:** the audit's rule numbers do not map to policy positions (one
notice named rule 9 while position 9 was present on the AP). Read the rendered
block, not the numbers. A lab client resolving via a public resolver will not
show this.

#### Step 2.9 — Migrate AirGroup explicitly

**Tool:** read the AOS 8 `airgroupprofile` service list from the source config (`aos8_get_effective_config(...)` or the raw config); read Central with `central_get_airgroup_system(...)` and `central_get_airgroup_service_definitions(...)`; write with `central_manage_airgroup_system(...)` or the Central UI. `[unverified]` which config-model scope the tool write maps to for an AP-group enable — read back in the UI.
**Why:** `[observed]` in Central, **AirGroup is off at the Global level**.
Nothing in the conversion carries it across. Enable AirGroup on the **AP group**
and match the AOS 8 `airgroupprofile` service list — at minimum **AirPlay,
Googlecast, DLNA Media and DIAL**.
**DIAL is what Chromebook and Android casting apps use to discover smart panels
and TVs.** With DIAL off, AirPlay discovery still works but casting to panels
fails.
**Expected result:** AirGroup enabled on the AP group with the full service list from the source config, DIAL included.
**If anomaly:** casting to panels fails while AirPlay works → check DIAL. Evidence:
`show airgroup debug statistics` on the AP shows a high
**"unsupported ssdp query pkt dropped"** count. A K-12 customer reported casting
fixed after enabling DIAL (customer-reported fix, one environment). Verification
is Step 5.5.

### Phase 3 — Pre-window gates

#### Step 3.1 — The access-switch port profile the AP depends on

**Tool:** on the access switch, `show lldp neighbor-info <port>` and `show port-access clients` (or `central_show_commands(device_type='cx', ...)`).
**Why:** `[proven]` if AP ports get their VLANs from an AOS-CX LLDP
device-profile, its `match sys-desc` pattern was written for the AOS 8 string —
and conversion changes it. Read from a lab AOS-CX 6300 (FL.10.07.0020) on a
converted AP's port:

```
Neighbor Chassis-Description : AOS-10 (MODEL: <model>), Aruba AP, Version:<ver> LSR, serial:<serial>
```

The word `ArubaOS` is gone. A profile keyed on `match sys-desc ArubaOS` stops
matching when the AP returns; the port falls back to static config, and where
that is a bare native VLAN the AP loses its management VLAN and every bridged
client VLAN. This is per port, for every conversion in such an estate, and a
pilot on a static trunk will not show it.
**Expected result:** a second profile matching the AOS 10 string, so AOS 8 APs are untouched and a mixed estate serves both:

```
port-access lldp-group AP10-lldp-group
    seq 10 match sys-desc AOS-10
port-access role lldp-AP10
    vlan trunk native <mgmt-vlan>
    vlan trunk allowed <mgmt-vlan>,<client-vlans>
port-access device-profile AP10-lldp-devprofile
    enable
    associate role lldp-AP10
    associate lldp-group AP10-lldp-group
```

Lab result (6300, with negative control and clean revert): without the AP10
profile the converted AP raised **no** port-access client (so
`show port-access clients` is the whole diagnostic); with it, the profile applied
immediately with no relink and clients got DHCP on two SSIDs; after a PoE cycle
it re-applied unaided within about 80 seconds; with the AP10 profile disabled,
clients associated but got no IP — so the client VLANs arrive only through the
new profile.
**If anomaly:**
- `[unverified]` the AOS 8 side of the string was not captured. Read the live AOS
  8 AP's neighbour entry before the window and record the literal string.
- Not covered by that proof: a live AOS 8 → AOS 10 transition on a port running
  both profiles (the test forced relearn with a power cycle), other AOS-CX
  trains, and `vlan trunk allowed all` ports. The result was lab-observed and
  not independently re-verified.
- Do not write `match sys-desc IAP` or `CAP`: the captured string contains
  neither. Match on `AOS-10` and read the literal string for your release.

#### Step 3.2 — Resolve the AP image filename

**Tool:** no MCP tool. Version and build from Central: Maintain > Firmware for the group, or Classic `GET firmware/v1/versions?device_type=IAP`; then the 64-byte check below.
**Why:** `[proven]` `server http` names the image file explicitly and nothing on
the AOS 8 controller tells you its name (`show upgrade info` and
`show ap image-info` do not exist on 8.10.0.21; `show ap details` gives only the
numeric AP type). A literal-execution test stalled at exactly this command.
The filename is `ArubaOS_<image class>_<version>_<build>`; the class is a
codename shared by several models `[doc-grounded]` (Instant OS 8.12.0.4 release
notes image table; class names carry to AOS 10, prefix `ArubaInstant_` →
`ArubaOS_`):

| Image class | AP models |
|---|---|
| `Gemini`  | AP-503H, AP-504, AP-505, AP-505H, AP-565, AP-567 |
| `Draco`   | AP-344, AP-345, AP-514, AP-515, AP-518, AP-574, AP-575, AP-575EX, AP-577, AP-577EX |
| `Scorpio` | AP-534, AP-535, AP-555, AP-584, AP-585, AP-585EX, AP-587, AP-587EX |
| `Norma`   | AP-635 |

`Scorpio` is additionally proven on hardware (AP-555 converted on
`ArubaOS_Scorpio_10.4.0.3_87961` and `ArubaOS_Scorpio_10.8.1.1_96846`).

**Expected result:** each filename passes:

```
REPO=https://common.cloud.hpe.com/ccssvc/ccs-system-firmware-registry/IAP
curl -s -r 0-63 "$REPO/ArubaOS_<class>_<ver>_<build>" | grep -qa ARUB && echo OK || echo WRONG
```

**If anomaly:**
- **`curl -I` is not a check** — every URL under that path returns HTTP 200 with
  an app shell, including invented names. The 64-byte check returns
  `<!DOCTYPE html>` for a wrong name and correctly rejected a deliberately wrong
  build.
- Version lists move — re-read them. Older builds stay in the repository, and
  older images use the `ArubaInstant_` prefix (e.g.
  `ArubaInstant_Draco_10.1.0.0_76943`).
- The Supported Devices page never names an image class, and the image binaries
  contain no model list — do not search there.
- Several classes in one command: semicolon-delimited
  (`ArubaOS_Gemini_<v>;ArubaOS_Scorpio_<v>`) or one TAR.
- Local alternative: `ap convert active specific-aps local-flash <image>`;
  `show ap convert-image-list` (AOS 8.6.0.0+) lists what is staged and is empty
  on an unstaged controller. Staging is per controller in a cluster, which is
  the reason to prefer `server http`.

#### Step 3.3 — Clear leftover convert state and confirm what will run

**Tool:** controller SSH: `show ap convert-status`; `aos8_get_active_aps(...)` for the AP list.
**Why:** `[proven]` `ap convert cancel` clears only engine state, not the AP
list; a previous session's APs survive and `ap convert add` answers
`AP name "<name>" is already listed`. Leftover state turned up at the start of
three separate tests.
**Expected result:** a clean list. Clear with `ap convert delete ap-name <name>` / `ap convert delete ap-group <g>` / `ap convert clear-all`.
**If anomaly:** "Status reads Active" means the `Status` field; `Current Status`
prints `Not Start` / `Pre-Validating` / `Updating APs` / `Update Done` and never
says `Active`.

#### Step 3.4 — Establish rollback access for the first AP of each phase

**Tool:** none — plan.
**Why:** `[proven]` rollback is **per AP** and needs the AP's own CLI (serial
console, SSH, or Central Remote Console under Analyze > Tools > Console, which
asks for the AP's username and password). There is no group-level or
Central-side revert. The post-conversion AP credential is **not deterministic**:
the serial number in two straight conversions, the AOS 10 factory default once
on an AP factory-erased first (where the serial was rejected without warning).
**Expected result:** convert one AP per phase first, establish its CLI, record what worked, then continue.
**If anomaly:** an AP you cannot log into cannot be rolled back — stop the phase.

### Phase 4 — Conversion (controller-side, in the window)

#### Step 4.1 — Run `ap convert`

**Tool:** interactive SSH to the controller with a PTY (a one-shot command cannot answer `[y/n]`). Prerequisites per the docs: controller on 8.7.1.9 / 8.10.0.5 or later, APs on 8.7.1.0+, each AP able to reach the cloud. `aos8_show_command(...)` is fine for read-only `show` polls.

```
ap convert add ap-name <ap-name|mac>          # or: ap convert add ap-group <group>
ap convert pre-validate specific-aps          # answer y — non-destructive readiness check
show ap convert-status                        # want: Pre Validate Success + Central Group populated
ap convert cancel                             # REQUIRED, else 'active' says "already executed"
ap convert active specific-aps server http common.cloud.hpe.com \
    path ccssvc/ccs-system-firmware-registry/IAP <image filename>
                                              # destructive: downloads AOS 10 and restarts the AP;
                                              # answer the country-code prompt y
show ap convert-status                        # Downloading Image -> Update Done
```

**Why:** `[doc-grounded]` the vendor migration page: *"A third option,
'activate', is available but not currently recommended for use."* `activate`
still worked in five lab runs and is the fallback only if the filename cannot be
resolved.
**Expected result:** `Pre Validate Success` (6–7 seconds in lab runs) with the
Central group populated, then `Update Done` and zero failures.
**If anomaly:**
- `No group(Central)` → Phase 1 Steps 1.5–1.6. `No license(Central)` → Step 1.2
  subscription validity.
- `[proven]` the controller's own NTP state does **not** gate pre-validate: a lab
  controller with no upstream NTP (stratum 16) passed every run. Pre-validate
  tests each AP's NTP reachability. Fix controller NTP because it is right, not
  as a conversion gate.
- Do not hold one SSH session across the `[y/n]` prompts and then poll it: the
  shell stops returning output after two prompts, which looks like a stalled
  conversion. Reconnect per poll. An empty poll during `Downloading Image` is
  also normal.
- The per-AP `Updated` row is not a signal in any direction (it has appeared and
  stayed, never appeared, and appeared then vanished). Judge by top-level
  `Update Done` plus zero failures, then confirm on the AP (Step 5.2).

#### Step 4.2 — Time the window on command-to-serving, not on `Update Done`

**Tool:** ping the AP every 5 seconds and read the shape of the log.
**Why:** `[proven]` `Update Done` is a control-plane milestone only: it arrived
1m15s, 1m21s and 4–5 minutes into runs, sometimes before the AP restarted and
sometimes after it was back. Command-to-AP-serving was 4m22s and 4m31s.
The down-window was 1.5 to 3.5 minutes across five conversions (longest 3m22s).
In one of five runs the AP answered for ~40 s, dropped again for ~110 s, then
stayed up.
**Expected result:** budget **6–8 minutes per batch**; wait for **60 seconds of
unbroken response** before starting the next batch.
**If anomaly:** a not-yet-converted AP appears only in the pre-provisioning
inventory, not in Central's operational Devices / Groups / Sites lists — "0
devices in Classic" before conversion is expected.

### Phase 5 — Post-conversion: placement and verification

#### Step 5.1 — Assign the AP to a site (devices Central already knows)

**Tool:** standalone: `central_add_devices_to_site(...)` (`network-config/v1/site-add-devices`). Hybrid: Classic `POST central/v2/sites/associations` `{"site_id": <n>, "device_type": "IAP", "device_ids": [<serials>]}`.
**Why:** `[proven]` an AP with no site connects (`Login_done`) and sits
factory-default broadcasting nothing; Provisioning State = Yes needs site +
license + persona. On a hybrid tenant `site-add-devices` returns 400
`API_ACCESS_RESTRICTED`; the Classic call works headlessly with per-device
results.
**Expected result:** per-device success.
**If anomaly:**

| The AP… | Path |
|---|---|
| is known to Central (has checked in, even if down now) | Classic `central/v2/sites/associations` — **add-only**: an already-sited device is rejected `SITE_ERR_MAX_NO_ALREADY_ASSIGNED` |
| is claimed but has **never** checked in | CSV upload (Step 1.7); the API returns `SITE_ASSOC_ERR_DEVICE_NOT_PRESENT` |
| either, with no API credentials | Classic UI: Global > Maintain > Organization > Network Structure > Sites > "Unassigned" (drag) |

A re-provisioned or re-converted AP lands Unassigned again. Browser automation
cannot perform these HTML5 drags — hand the drag to a human.

#### Step 5.2 — The green signature

**Tool:**

```
central_get_device_config_issues      -> all four arrays empty
central_get_devices_config_health     -> configStatus SYNCHRONIZED, activeIssues []
central_get_wlans_monitoring          -> status ENABLED (about 1 min lag after a change)
show ap bss-table                     -> BSS present per SSID / band
show network                          -> SSIDs Enabled
show ap debug cloud-server            -> Aruba Central status: Login_done
```

**Why:** never declare done on a single signal, or from an earlier check. The AP's
own CLI output is authoritative; Central monitoring lags (after a delete,
`central_get_wlans_monitoring` can show the old count for a minute; per-AP
`wlanCount` lags too).
**Expected result:** all six green.
**If anomaly:** `Out of Sync` with push failures → Step 2.2 fields, then
`central_resync_device_config(serials=[...])` to re-push.

#### Step 5.3 — Run AP commands without the AP password

**Tool:** `[proven]` Classic troubleshooting service (the device's **Commands** panel in the UI; no MCP tool):

```
GET  troubleshooting/v1/commands?device_type=IAP          # whitelist with command_ids
POST troubleshooting/v1/devices/{serial}  {"device_type":"IAP","commands":[{"command_id":N}]}
GET  troubleshooting/v1/devices/{serial}?session_id=N     # COMPLETED on the first 4 s poll
```

Relevant ids observed: **24** `show ap bss-table`, **54** `show network`, **126**
`show running-config`, **53** `show ap-env`, **116** `show uplink status`.
`central_show_commands(serial_number=..., device_type='aps', commands=...)` is the
New Central route (`central_list_supported_show_commands` lists what it accepts);
its `device_type` enum is lowercase plural — `aos-s | aps | cx | gateways` —
and `GATEWAY` / `MOBILITY_GW` return 422, which looks like an unreachable device.
**Why:** removes AP SSH from every verification step. `convert-aos-ap` is not in
the whitelist, so rollback still needs the AP's CLI (Step 3.4).
**Expected result:** command output per AP.
**If anomaly:** AP SSH when you need it (rollback): on 10.4.0.3 the AP offers only
`ssh-rsa` and OpenSSH ≥ 8.8 refuses (`no matching host key type found`); on
10.8.1.1 it negotiates `rsa-sha2-512` with no flags. Where needed:
`-o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa` (harmless on
builds that do not need it). The session must be interactive — a one-shot
`ssh host "cmd"` is refused *"Only cli connections are allowed to the AP"* —
and a live AOS 8 campus AP does not expose TCP 22, so AP SSH cannot be
pre-flighted. Do not tell a customer on current firmware that AP SSH is broken.

#### Step 5.4 — Wait out the configuration sync before judging

**Tool:** Step 5.3 `show ap bss-table`.
**Why:** `[proven]` a converted AP comes up on its factory AOS 10 image, registers,
then pulls config: nine SSIDs across 18 BSSs within ~72 seconds in two runs,
**more than twenty minutes** in another on the same AP. While waiting it
advertises only `SetMeUp-<last 6 of MAC>` and `show ap bss-table` reads
`Num APs:0` — a migration in progress, not a failure.
**Expected result:** production SSIDs on air on the first AP of the phase before the next batch converts.
**If anomaly:** **order of trust for "is this still a CAP"**: the controller's
`show ap active` (`aos8_get_active_aps`), then the live Commands probe, then the
inventory row last. The stored inventory record (Global > Device Inventory,
Classic `monitoring/v2/aps`) goes stale — after a rollback it kept reporting the
AP Down on AOS 10 while the controller showed it Up as an AOS 8 CAP.
An AP's LLDP neighbour entry on its switch also changes at conversion — a useful
progress signal from the wiring closet (Step 3.1 for the string).

#### Step 5.5 — Pilot acceptance: authentication, roles, and casting

**Tool:** Step 5.3 commands (`show ap debug radius-statistics`, `show running-config`, `show airgroup debug statistics`); Classic Central UI for AirGroup clients.
**Why:** a checker that compares SSIDs, sites and VLANs ran green through three
authentication defects in two days (Steps 2.5 and 2.7). Aim acceptance at
behaviour.
**Expected result:** on the pilot AP —
1. a real 802.1X client authenticates per SSID; RADIUS statistics show responses and the server `Up` (Step 2.5);
2. each role's `wlan access-rule` block is present and in the intended order (Steps 2.7–2.8);
3. **AirGroup casting test:** from a Chromebook or Android device, cast to a
   smart panel / TV, and confirm AirPlay discovery too. Then check
   **Classic Central > Applications > AirGroup > Clients** and click the client's
   MAC to see the servers that client can see.
**If anomaly:** casting fails with AirPlay working → DIAL is missing from the
AP-group AirGroup services (Step 2.9); confirm with a high
"unsupported ssdp query pkt dropped" count in `show airgroup debug statistics`.

#### Step 5.6 — Rollback (per AP)

**Tool:** the AP's CLI (Step 3.4): `convert-aos-ap cap <controller-ip>`.
**Why:** `[proven]` re-images back to an AOS 8 campus AP in its original ap-group
with both radios serving, in about 1m25s–1m40s.
**Expected result:** AP in `show ap active` on the controller.
**If anomaly:** the command prints nothing and the session stays at a live prompt;
the AP keeps answering ping for 35–45 s before it drops. Do not retype it and do
not treat your own session closing as the signal. `ap wipe out flash` is
FIPS-only.

### Phase 6 — After the first batch, before the next campus

#### Step 6.1 — Read the audit log for what changed in the tenant

**Tool:** `central_get_audit_logs(...)` (`GET network-services/v1/audits`; `start-at`, `end-at`, `limit` max 200, `offset` 1-based).
**Why:** `[proven]` this answers "what did the customer change?" during a
customer-run conversion — read it before asking. The signal is a handful of
non-system rows (WLAN saves, alert clears, restarts, visitor accounts, WLANs
unassigned and parked) among thousands of system entries.
**Expected result:** a short list of human changes.
**If anomaly:**
- `sort=-timestamp` returned 500 — omit it.
- The per-id detail route (`central_get_audit_log_detail`,
  `network-services/v1/audit/{id}`) returned **404 "Route Not Found"** in the
  tenants observed; the text you need is in the list entry's `description`.
- A guessed Classic path (`/auditlogs/v1/logs`) returns 404 — a wrong path, not a
  missing capability.
- A UI save appears as before/after differing only by default keys written out —
  not a behaviour change and not drift.

#### Step 6.2 — Explain the "Config eliminated" notices

**Tool:** `central_get_audit_logs(...)`.
**Why:** `[proven]` every newly converted AP generates them (180 entries across 57
devices in one window). Two kinds: **captive portal "non-compatibility with
AP(diatype ext)"** against the generated portal's Default Role and Server Group
— expected (see Reference: `sys_cnac_<wlan>`); and **role-based policy "Policy
Rule 'N' … unsupported"** — rules AOS 10 will not render (Step 2.8).
**Expected result:** each notice classified.
**If anomaly:** dropping the non-rendering rules is cosmetic and a customer-tenant
write — do not do it just to quieten a log.

#### Step 6.3 — Dual-uplink APs: "Downlink Packet Drops" on eth1

**Tool:** Step 5.3 commands: `show interface counters`, `show port status`, `show lacp status`, `show ap debug lldp neighbor`.
**Why:** `[doc-grounded]` AOS 10 design, *Access point port usage*
(`arubanetworking.hpe.com/techdocs/aos/aos10/design/ap-ports/`): with no LACP from
the switch the AP runs active/standby — E1 *"in a standby state and will not
transmit or receive management or user traffic"*. `[proven]` on four dual-cabled
APs: both ports up at 1G to the same switch (confirmed by the LLDP chassis MAC),
eth1 receiving roughly what eth0 receives, transmitting almost nothing, and
discarding 10–12%; clients unaffected. The alert counts the standby port doing
what the doc says.
**Expected result:** the customer is told this before their monitoring finds it.
**If anomaly:** options — acknowledge / clear (returns); LACP on both switch ports
for active/active (**a LAG change on live ports, not lab-proven — not low-risk**);
disable or unpatch eth1 (loses the standby uplink). Do not pre-emptively unplug
second cables before a window.

#### Step 6.4 — Run the auth-side comparisons (GET-only)

**Tool:** `aos8_get_effective_config(...)` / `aos8_parse_config(...)` against `central_get_auth_servers`, `central_get_wlan_profiles`, `central_get_roles`, `central_get_role_gpids`, `central_get_config_assignments`, `central_get_captive_portal`.
**Why:** compare what broke, not only SSID / site / VLAN sets:
1. every attribute on each AOS 8 `aaa authentication-server radius` block against
   its Central `auth-server`, with `called-station-id` compared **per WLAN**;
   secrets as **presence only** (the value is not in the config-model API);
2. per SSID: opmode, dot1x on/off, EAP termination directives, server group;
3. default-role and pre-auth role assigned as **both** `roles` and `role-gpids`
   at every site offering the WLAN, policy coverage wherever the source role
   carried real ACL rules (filter AOS 8 boilerplate ACLs), and the Step 2.7
   orphan check both ways;
4. the generated `sys_cnac_<wlan>` default-role and the live auth-profile id in
   the portal URL.
**Expected result:** a GET-only report. Make the checker unable to emit any other
verb, asserted in code — it runs against production.
**If anomaly:**
- Resolve renamed objects through the conversion chain — ESSID → virtual-AP →
  aaa-profile → dot1x-default-role / initial-role — **never by name**; a
  name-based lookup reported "no policy is due" for exactly the Step 2.7 defect.
- A batch of `ABSENT-OR-MISNAMED` results sharing one key name is a **checker**
  bug — fix it before reporting.
- Controller configs differing only in `key` / `wpa-passphrase` ciphertext are not
  different configurations (each controller encrypts under its own key) — and
  identical ciphertext classes do not prove plaintexts match.

### Phase 7 (optional) — AOS-CX / AOS-S switches into Central, monitoring only

Keep this a separate workstream from the wireless migration, with separate
words. **Monitoring-only means Central observes the switches and pushes no
configuration.** Say *monitoring*, never *management*, to a customer who bought
the former. Nothing here writes switch configuration except the checkpoint in
Step 7.1, which is a revert point.

#### Step 7.1 — Prechecks on each switch, before anything is claimed

**Tool:** switch CLI, or `central_show_commands(device_type='cx'|'aos-s', ...)` for switches already in Central.
**Why / Expected result:**
- **Cloud reachability is DNS plus a route, per switch.** Resolve and ping the
  Central / Activate endpoint **by name** from each switch. `[proven]` a fleet
  with one shared DNS server had six switches with no `ip dns` line at all.
- **`show aruba-central`**: `[proven]` on an AOS-CX 6300M (FL.10.07.0020) an
  unclaimed switch reads admin state `enabled`, source `activate`, status
  `connection_failure` — that is "not claimed anywhere", not a fault.
  `[unverified]` later AOS-CX trains may rename it `show hpe-anw-central`;
  confirm with `show ?` on the train in front of you.
- **`show system`** for model and running version, per member.
- **Checkpoint first, and prove it is a revert point** `[proven]`:
  ```
  copy running-config checkpoint <name>
  checkpoint diff <name> running-config        -> "No difference in configs."
  ```
- **Firmware floor per family**, against each switch's actual version. When an
  inventory sheet and the device disagree, the device wins.

#### Step 7.2 — Gather serial + MAC per physical switch

**Tool:** `show vsf detail` on a reachable AOS-CX stack (`techdocs/AOS-CX/10.16/HTML/vsf/Content/VSF_cmds/sho-vsf-det.htm`) — per member ID, type, model, status and **serial**; `central_get_switch_stack_members(...)` for stacks already in Central.
**Why:** `[doc-grounded]` GreenLake add is serial + MAC, **one row per physical
switch** — every stack member. The stack member number is not needed.
`[proven]` serials and MACs are not in configuration files (73 files, zero hits)
— make one request for a sheet with hostname, model, serial and MAC per
physical switch.
**Expected result:** member count reconciled from the **configs'** VSF stanzas,
not the sheet. `[proven]` reconciling a 165-row sheet against 68 configs found
two stacks one member short.
**If anomaly:** the sheet's model column may contradict the serial; GreenLake
identifies the model from the serial, so it does not block the claim — but do
not use the sheet's model as the subscription class key. Exclude non-Central
rows (other vendors, no serial, spares) explicitly and by name.

#### Step 7.3 — Create the monitoring-only group in Classic

**Tool:** no MCP tool — `central_manage_device_group` / `central_create_device_group_with_devices` create **New Central** device groups, not Classic monitor-only groups. Classic `POST configuration/v3/groups`:

```
"group_properties": {"AllowedDevTypes": ["Switches"],
                     "AllowedSwitchTypes": ["AOS_S", "AOS_CX"],
                     "MonitorOnlySwitch": true,
                     "MonitorOnly": ["AOS_S", "AOS_CX"]}
```

**Why:** `[doc-grounded]` monitoring-only is a **Classic group property**
(Classic Central, *Configuring AOS-CX Switches in Monitoring-Only Mode*,
`techdocs/central/2.5.8/content/nms/aos-cx/get-started/cx-mon-mode.htm`: a
"Monitoring only for AOS-CX" box, and a separate one for AOS-S). HPE Central's
*Quick Start – Onboarding Standalone AOS-CX Switch* also places group creation in
Classic. The New Central onboarding docs describe no monitor-only mode.
**Expected result:** read-back shows `MonitorOnly ["AOS_S","AOS_CX"]` and `MonitorOnlySwitch true`.
**If anomaly:**
- `[proven]` creating with `"MonitorOnly": ["AOS_CX"]` alone succeeded but read
  back `MonitorOnlySwitch: false`; it only took with **both** `AOS_S` and
  `AOS_CX` listed. Always verify the read-back.
- `[proven]` **monitor-only cannot be changed after creation**:
  `PATCH configuration/v2/groups/{group}/properties` returns
  `400 "Existing setting for Monitor only mode cannot be changed"`. The only fix
  is delete and recreate — safe only while the group is empty.
- `[proven]` the tenant `default` group allows switches with `MonitorOnlySwitch`
  false — a switch that reaches `default` sits in a config-bearing group.

#### Step 7.4 — Claim → assign → move → subscribe (in that order)

**Tool:** `greenlake_post_devices_v1_devices` (claim) → `greenlake_patch_devices_v1beta1_devices` (application + region) → Classic `POST configuration/v1/devices/move` into the monitor-only group → verify the group → `greenlake_patch_devices_v1beta1_devices` (subscription).
**Why:** `[proven]` factory-default AOS-CX has its Central connection enabled
(source: Activate), so a switch connects within about a minute of being claimed,
assigned and subscribed. Move it into the monitor-only group **after** the service
assignment and **before** the subscription, so it never sits licensed in
`default`. Never let a switch transit `default`. The application-before-subscription
trap of Step 1.2 applies identically. The AP batch ceilings were probed for APs —
re-probe them for switches.
**Expected result:** each switch's Config Status reads **`Monitoring only`** — that
read-back is the whole assurance nothing can be pushed.
**If anomaly:** subscriptions are per **physical** switch and per **class**:
- Every stack member consumes a seat.
- `[doc-grounded]` licences are not interchangeable across device types or switch
  families (`techdocs/central/2.5.8/content/nms/subscriptions/overview-licensing.htm`).
  `[proven]` a Class-2 subscription (SKU text "62/29xx") attached to a 6300 failed:
  500 from the bulk tool, async FAILED from a direct PATCH — neither says
  "wrong class".
- Count the gap **per class**, keyed on the **SKU description** text (`62/29xx`,
  `63/38xx`, `CL1`, `CL5`). An all-class total can be positive while the class you
  need is empty. `[observed]` model → class from SKU text: 6200 / 2930 → Class 2,
  6300 / 3800 → Class 3, 6100 → Class 1, 8360 → Class 5 — confirm against the
  licensing doc.
- Check `subscriptionStatus` and `endTime`, never `availableQuantity`.

#### Step 7.5 — Site association for switches

**Tool:** Classic `POST central/v2/sites/associations` with `device_type` **`SWITCH`**.
**Why:** `[proven]` `CX` is rejected as a `device_type` value.
**Expected result:** per-device success.
**If anomaly:** same add-only and never-checked-in rules as Step 5.1.

#### Step 7.6 — Prove nothing was pushed

**Tool:** switch CLI `checkpoint diff <name> running-config`.
**Expected result:** "No difference in configs."
**If anomaly:** stop and investigate before onboarding further switches.

**What is not proven for Phase 7, and must be said that way:**
- `[unverified]` whether monitor-only switches appear in New Central monitoring
  views — do not promise a New Central dashboard.
- `[unverified]` whether the monitor-only → managed move happens without a config
  push beyond what is documented below.
- AOS-S differs from AOS-CX in onboarding, telemetry and lifecycle; decide on a
  few small AOS-S units deliberately rather than letting them ride along.

**What a later move to a Central-managed group imports** `[doc-grounded]` (HPE
Central quick start above). Managed means a Classic group with *"Allow New Central
to overwrite all configuration for this group"*; on the move, configuration is
auto-imported for:

> Static route, Interfaces, Management Interface, VLAN, VLAN Interface, Port
> Channel Interface, Local Management (SSH and Web servers), HTTP Proxy, DNS,
> Remote Management, IP Source Interface, VRF, VSF, NTP, Speed-System Interface
> Group, Spanning Tree, Hostname

> "VSX-related connectivity configurations will not be auto-imported."
>
> "Automatic configuration migration from HPE Classic Central group to HPE Aruba
> Networking Central group is currently not supported."

Quote the list; do not summarise it as "basic connectivity" — VLANs, interfaces,
port channels, spanning tree and VRF are on it. VSX is the named exception. Treat
monitor-only → managed as a move into a managed group, not a property flip.

## Reference — platform behaviour that changes the plan

**Connector observations on a hybrid tenant** `[observed]` (re-check on the
current release):
- `central_get_system_info`, `central_get_config_assignments(scope_id=<device>)`
  and `central_get_gateway_clusters(scope_id=<site>)` returned empty for objects
  that existed (corroborated against `central_get_scope_tree`). Use the scope tree
  to enumerate; treat an empty result from these as a statement about the
  instrument.
- Some management-plane writes returned `null` — a silent no-op (GreenLake
  device-add, floor / building create, report create). Re-read to verify.
  `central_manage_site` create / update / delete returned real success.
- Schema introspection: a 400 ending `valid body fields: ...` lists a node's direct
  children. Probe with one write per execute block — the sandbox aborts the block
  on the first write error.
- `aos8_parse_config` was observed to truncate quoted object names containing
  spaces (`"some name"` → `"some`) in definitions and references with no warning;
  diff its output against the raw stanzas for such objects. It does not model
  `bw-contract` (it emits a `_warnings` entry) — carry bandwidth contracts by hand.
  When pasting config, restrict the paste to the modelled classes (`user-role`,
  `ip access-list session`, `netdestination`) so PSKs and RADIUS secrets never
  enter context.

**The Central NAC generated captive portal `sys_cnac_<wlan>`** `[proven]`:
1. It copies the WLAN's `default-role` once, when the **auth profile** is created.
   Later WLAN changes do not propagate; a direct PATCH is refused (system object);
   a UI re-save of the auth profile does not refresh it.
2. That copied default-role never reaches an AOS 10 AP — the AP's
   `wlan external-captive-portal sys_cnac_<wlan>` block carries server / port / url
   and no default-role; the post-login role is the WLAN's `set-role-default`.
   A stale value is cosmetic: it blocks deleting that role object in Central and
   changes nothing a client sees.
3. **Deleting the auth profile deletes the portal AND disables the WLAN** (`enable`
   false — the SSID leaves the air at every site offering it). Recreating the
   profile in the UI regenerates the portal with the current default-role and
   re-enables the WLAN; the portal URL contains the auth-profile id, so it changes.
4. Confirm `sys_cnac_<wlan>` is **gone** before recreating; if not, delete the
   profile again. A one-site mirror cost under two minutes of guest downtime;
   in production with the portal assigned at 19 sites, it survived the first
   delete and the outage was about 10 minutes. Site count is the suspected
   difference `[unverified]`. `DELETE captive-portal/sys_cnac_<wlan>` is refused
   ("system created. Cannot be deleted.").
5. MAC-cached guests return without re-signing-in; existing identity-store accounts
   work through a recreated profile.
- Tear Central NAC test objects down by deleting the **auth profile** in the UI,
  not the generated roles by API — the API path orphaned pre-auth rules inside the
  global system policy `sys_central_nac`. Use a name prefix for test objects and
  verify teardown with a search proven able to match.
- Deleting a visitor account ends that guest's session immediately — say so first.

**Deployment-mode and feature-parity guidance** `[doc-grounded]`:
- Deployment mode is the management plane; Foundation vs Advanced is the feature
  licence — separate axes.
- On-premises is a real option for data-residency / regulatory constraints.
- Where adoption hinges on monitoring views (RAPIDS, client connectivity, Reports,
  Floorplans), verify per-view GA in the customer's own tenant before promising
  standalone or hybrid.
- Do not declare a feature gated from a config-model API error alone — an AP
  firmware upgrade "gated" by API was fully available in the Firmware Management
  UI (Global → Firmware Management → Create Firmware Policy).

## Decision matrix

| Condition | Action |
|---|---|
| Tenant is standalone (no Classic toggle) | Use New Central group / site tools; skip Classic fallbacks |
| Tenant is hybrid | Classic `v3/groups` + `devices/move`; Classic site associations or CSV |
| Estate rather than one AP | Phase 1 as an unattended pre-stage days ahead; probe batch ceilings first |
| Serial missing after two read-backs | Claim in GreenLake UI; "blocked or invalid" → HPE support |
| Pre-validate `No group(Central)` | Steps 1.5–1.6 |
| Pre-validate `No license(Central)` | Step 1.2: check `subscriptionStatus` / `endTime` |
| AP online, Out of Sync, no SSIDs | Steps 2.2–2.3, then `deviceCount` (1.6) and site (5.1) |
| AP shows only `SetMeUp-…` | Configuration sync in progress (Step 5.4) — wait |
| AP ports use an LLDP device-profile | Step 3.1 before the window |
| 802.1X fails after conversion, NPS Reason Code 48 | Step 2.5(a) `called-station-id` |
| RADIUS responses 0, Invalid Secret 0 | Step 2.5(b) RADIUS client subnet / UDP 1812 |
| Client gets Deny All | Step 2.7 role / policy site sets |
| Clients lose internal DNS in a role | Step 2.8 punch-through rules |
| Casting to panels fails, AirPlay works | Step 2.9: enable DIAL on the AP-group AirGroup services |
| eth1 Downlink Packet Drops | Step 6.3 — explain; LACP is not low-risk |
| Need to roll back | Step 5.6 on the AP's CLI; no group-level revert |
| Switching estate coming into Central | Phase 7, separate workstream, monitoring only |
| Gateway / tunnel / cluster work | Out of scope |

## Output formatting

Report per phase, in this shape:

1. **Status line** — phase, count of devices in scope, verdict
   (DONE / BLOCKED / PARTIAL).
2. **Read-back table** — per phase, counts of *present / assigned / subscribed /
   persona / grouped / sited / converted / green*, followed by **each missing
   device named** (serial, or the tokenized form the tool returns).
3. **Gates** — each gate from this runbook that applied, with its evidence label
   and the command or tool output that satisfied it.
4. **Customer actions** — items only the customer can do (RADIUS client subnets,
   secrets, switch port profiles), one line each, per campus where relevant.
5. **Open items** — anything `[unverified]`, stated as unverified.

Never declare a migration complete from a single signal or from an earlier check.

## Example

> "pre-validate says No group(Central) on the APs I just onboarded"
> "the converted AP is online but broadcasting nothing"
> "casting to the classroom panels stopped working after we moved to AOS 10"
> "stage 400 APs into Central before next week's conversion window"
> "onboard our CX switches into Central for monitoring only"
