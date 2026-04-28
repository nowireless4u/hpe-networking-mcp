---
name: central-scope-audit
title: Aruba Central VSG-anchored configuration scope audit
description: |
  TRIGGERS — call this when the user asks: "Central config audit",
  "scope audit", "where are my Central WLAN profiles assigned", "is my
  Central config drifting", "Central scope hierarchy", "audit roles
  and policies", "audit Central authentication / VLANs / aliases",
  or anything about Central's Configuration Manager scope tree
  (Global → Site Collections → Sites → Device Groups). Walks ~25
  profile categories with **per-setting checks** within each, compares
  each finding to its VSG-recommended scope AND VSG-recommended
  values, and emits drift findings ranked by severity. Anchored on
  Aruba's Validated Solution Guide (Campus Design + Campus Deploy +
  Policy Design + Policy Deploy).
platforms: [central]
tags: [central, audit, configuration, scope, drift-detection, vsg]
tools: [health, central_get_scope_tree, central_get_scope_resources, central_get_effective_config, central_get_devices_in_scope, central_get_scope_diagram, central_get_config_assignments, central_get_wlan_profiles, central_get_wlans, central_get_roles, central_get_role_acls, central_get_role_gpids, central_get_policies, central_get_policy_groups, central_get_object_groups, central_get_net_services, central_get_net_groups, central_get_aliases, central_get_server_groups, central_get_named_vlans, central_get_devices, central_get_aps, central_get_sites]
---

# Aruba Central VSG-anchored configuration scope audit

## Objective

Walk Aruba Central's Configuration Manager hierarchy
(**Global → Site Collections → Sites → Device Groups → Devices**) and
produce a comprehensive drift report covering every major profile
category. Each finding is judged against the **Aruba Validated
Solution Guide (VSG) Campus + Policy** recommendations — the audit
calls out *"VSG recommends X, found at Y"* drift explicitly, AND
checks **per-setting values** within each profile against VSG-recommended
defaults.

**Read-only.** Identifies issues; does not correct them. Use the
appropriate `central_manage_*` tools after reviewing.

## Prerequisites

- Central must be reachable (`health(platform="central")` first).
- Operator picks an audit scope: **org-wide** (default), a specific
  **site collection**, or a specific **site**. Org-wide for a large
  deployment can produce 100+ findings — confirm with the operator
  before running. Offer site-collection scope as the cheaper option.

## Procedure — 14 audit checks across ~25 profile categories with per-setting depth

Run the steps in order. Each step pulls a slice of the catalog,
compares it to its VSG-recommended scope AND VSG-recommended values,
and adds findings to the running report. Steps that depend on earlier
output (e.g., role-policy linkage) are flagged.

### Step 0 — Reachability + scope-tree snapshot

**Tools (in order):**
- `health(platform="central")` — confirm reachable.
- `central_get_scope_tree(view="committed")` — what's directly assigned at each scope.
- `central_get_scope_tree(view="effective")` — full inherited+committed view.

**Why:** every later step references scopes by ID. The committed-vs-effective diff is the foundation for drift detection.

**Sanity check:** record total scopes walked, total site collections, total sites, total device groups. Surface in the report header.

**Decision aid:** the diff between `committed` and `effective` reveals where overrides exist:
- A scope that has `effective` config NOT in `committed` → inherited from an ancestor (good)
- A scope that has `committed` config NOT in `effective` → blocked by a more-specific override below
- A scope where both views disagree on a value → drift

### Step 1 — Authentication Servers (RADIUS sources)

**Tool:** discover via `central_get_config_assignments(profile_type="auth-server")` if filterable, otherwise traverse step 0's tree and call `central_get_scope_resources(scope_id=...)` per scope and pick auth-server entries.

**VSG-recommended scope:** **Global** (campus deploy guide §10703 — *"Profile Path: Security > Authentication Server ... Scope: Global"* for Access Switch + Campus Access Point).

**VSG-recommended values (per Auth Server entry):**
- IP / FQDN — should be production RADIUS, not test/lab IPs
- Shared secret — present + non-default (audit can detect "default" / "secret123" patterns if exposed; otherwise informational)
- Server timeout — standard RADIUS timeout (e.g. 5-10 seconds)
- Reachability port — UDP 1812 (auth) / 1813 (acct) standard

**Drift findings:**
- **REGRESSION**: any auth-server assigned at site, site collection, or device-group scope (should be Global per VSG).
- **REGRESSION**: server defined with default certificate (VSG §364, §370: *"It is best practice to replace the certificate with a valid certificate"*).
- **DRIFT**: Global auth-server defined but no AAA Authentication or Server Group references it.
- **DRIFT**: only one auth-server defined for production (no redundancy).

### Step 2 — Authentication Server Groups (RADIUS server groups)

**Tool:** `central_get_server_groups()` for the library; cross-reference with `central_get_config_assignments` for assignment scopes.

**VSG-recommended scope:** **Global** (deploy guide §10564 — *"Profile Path: Security > Authentication Server Group ... Scope: Global"*).

**VSG-recommended values:**
- VSG §5006: *"Best practice is to deploy 2 RADIUS servers and enable load balancing"* — server groups should contain 2+ servers.
- Load balancing should be enabled on multi-server groups.
- VSG §378: *"When following best practice and using more than one ClearPass Server for network authentication"* — implies redundancy is expected.

**Drift findings:**
- **REGRESSION**: server group assigned at site/collection scope.
- **REGRESSION**: server group with only 1 RADIUS server (no redundancy — VSG explicitly says 2+).
- **REGRESSION**: load balancing disabled on multi-server group.
- **DRIFT**: server group defined but no AAA Authentication profile references it (orphan server group).
- **DRIFT**: AAA Authentication profile references a server group that doesn't exist (broken reference).

### Step 3 — AAA Authentication profiles

**Tool:** discover via `central_get_config_assignments(profile_type="aaa-auth")` if available, otherwise per-scope traversal.

**VSG-recommended scope:** **Site** (deploy guide §11799 — *"Profile Path: Security > AAA Authentication ... Scope: Site"*).

**VSG-recommended values:**
- Authentication source: RADIUS (referencing a Global-scoped server group)
- TACACS+ for admin access (VSG §10601: *"Authentication Type: TACACS+"*)
- Fallback to local authentication enabled (VSG §10602)
- Critical-auth role: defined for RADIUS-unavailable scenarios (VSG §9321: `CRITICAL-AUTH` role)

**Drift findings:**
- **REGRESSION**: AAA Authentication references a server group that doesn't resolve (broken auth chain).
- **REGRESSION**: no fallback-to-local authentication configured (lockout risk if RADIUS dies).
- **REGRESSION**: no critical-auth role defined (clients can't authenticate during RADIUS outage).
- **DRIFT**: AAA Authentication profile assigned only at one site collection but auth servers are at Global and used across the whole org.

### Step 4 — Roles (with role ACLs and role GPIDs)

**Tools:**
- `central_get_roles()` — full role catalog.
- `central_get_role_acls()` — ACLs attached to roles.
- `central_get_role_gpids()` — role-to-GPID mappings (for fabric).

**VSG-recommended scope:** **Site** (per Campus Deploy §9337 the example uses `Scope: SMALL-CAMPUS-SITE` — site-scoped for the campus). Some roles can be **Global** if truly shared across all sites.

**VSG explicit rule (Policy Design):** *"A role is not pushed to an access point or switch unless it is referenced by at least one policy that is scoped to the device."*

**VSG explicit rule (Policy Design §1211):** *"Keep the number of roles as small as possible while still obtaining the desired security policy. The fewer roles in use, the easier it is to understand and maintain policy."*

**VSG-canonical role set** (Campus Deploy §9311-§9322):
- `EMPLOYEE` — corporate users
- `GUEST-USER` — internet-only
- `IT` — administrative
- `IOT` — restricted, limited destinations
- `BLACKHOLE` — default placeholder before 802.1X assignment (VSG §9319: *"Default placeholder prior to 802.1X role assignment"*)
- `REJECT-AUTH` — deny-all after 802.1X reject
- `CRITICAL-AUTH` — limited access during RADIUS outage
- `ARUBA-AP` — infrastructure role for APs (VSG §9534: *"automates assigning the complete set of VLANs needed on a trunk connected to a [the AP]"*)

**Per-role checks:**
- Each role must have ≥1 policy referencing it (else not pushed to any device).
- Department-specific roles (HR, FINANCE) should be defined as needed but not duplicated.
- The `ARUBA-AP` role should exist if APs are deployed (automates trunk VLAN assignment).
- The `BLACKHOLE` role should be the default for wireless until 802.1X assigns a real role.

**Drift findings:**
- **REGRESSION — orphan roles**: role defined but no policy references it (not pushed to any device per VSG rule).
- **REGRESSION — missing canonical roles**: APs deployed but no `ARUBA-AP` role; 802.1X enabled but no `REJECT-AUTH` / `CRITICAL-AUTH` / `BLACKHOLE` roles defined.
- **DRIFT — role count > 60**: heuristic — VSG advises minimal role count. Operator decides if intentional.
- **DRIFT — role count > 100**: stronger signal of role proliferation.
- **DRIFT — duplicate roles**: same purpose at different sites with slightly different ACL sets. Candidate for consolidation.
- **DRIFT — role assigned at multiple sites individually that should be promoted to a site collection or Global**.
- **DRIFT — role with empty ACL set**: defined but does nothing.
- **INFO**: roles + their ACLs + GPID mappings, listed in a table.

### Step 5 — Policies + Policy Groups

**Tools:**
- `central_get_policies()` — full policy catalog.
- `central_get_policy_groups()` — collection-level policy groupings.

**VSG-recommended scope:** **Site** typically; **Site Collection** when shared across collections; **Global** for org-wide policies. Policy Groups operate at the collection level.

**VSG explicit rules:**
- VSG §9978: *"It is best practice to explicitly permit required network services in a policy at the top of the policy set."* — first rules should be allow-services.
- VSG §10024: *"It is best practice to explicitly allow applications to avoid unintentionally blocking access by lower"* — explicit allow > implicit deny.
- VSG §10091: *"in a policy higher in the policy set. Administrators can assign all roles to the deny all rule, if the security"* — explicit deny-all at the bottom.
- VSG §5325: *"This line always must be the last entry in the Access Rules to prevent"* (referring to deny-rule placement).

**Per-policy checks:**
- Rule order: services first, applications second, role-based rules third, deny-all last.
- Last rule should be explicit deny-all (defense in depth).
- Rules referencing non-existent aliases / services / object groups → broken rule.
- "any/any allow" patterns → flag for review (potential security gap).
- Rules with no source role assigned → effectively all-roles allow (review).

**Drift findings:**
- **REGRESSION — orphan policies**: policy defined but assigned nowhere (waste).
- **REGRESSION — broken role references**: policy references a role that doesn't exist.
- **REGRESSION — broken alias/service references**: policy rule references deleted alias / net-service / net-group / object-group.
- **REGRESSION — missing explicit deny-all at end**: policy without a final deny rule (security gap per VSG §10091).
- **DRIFT — same policy at every site**: candidate for promotion to Site Collection or Global.
- **DRIFT — rule order**: services not at top, deny not at bottom (per VSG §9978/§10091).
- **DRIFT — overly permissive rules**: any/any allow with no role scoping.
- **INFO**: policy → role linkage table.

### Step 6 — Network Services (net-services), Network Groups (net-destinations), Object Groups

**Tools:**
- `central_get_net_services()`
- `central_get_net_groups()` (network groups / destinations)
- `central_get_object_groups()` (object groups for policy)

**VSG-recommended scope:** **Site** unless truly org-wide (Global).

**VSG canonical services** (Campus Deploy §9684-§9689):
- `svc-dhcp` (UDP 67-68)
- `svc-dns` (UDP 53)
- `svc-ntp` (UDP 123)
- `svc-https` (TCP 443)
- Plus pre-built catalogue of common services + cloud applications

**VSG canonical net-groups** (Campus Deploy §9660):
- `RFC-1918` for the three RFC 1918 ranges
- DNS / NTP server net-groups for org-specific addresses

**Per-entry checks:**
- Net-service should reference standard ports for known protocols.
- Net-group should not be empty.
- Object-group nesting should not be circular.

**Drift findings:**
- **DRIFT — orphan net-services**: defined but not referenced by any policy (waste).
- **DRIFT — orphan net-groups**: defined but not referenced.
- **DRIFT — orphan object-groups**: defined but not referenced.
- **DRIFT — same definition at every site**: candidate for promotion.
- **DRIFT — empty net-group / object-group**: defined but contains 0 entries.
- **INFO**: catalog summary by category.

### Step 7 — Aliases (SSID / PSK / server-host / VLAN IPv4 / Switchport)

**Tool:** `central_get_aliases()` — alias library; cross-reference with `central_get_config_assignments` for assignment scopes.

**Critical concept: aliases have a TWO-LAYER MODEL** — see Campus Deploy §11220-§11377:

1. **Alias DEFINITION** — created at **Site / Site Collection / Global** with a Device Function targeting (e.g., the `SC-SW-IP` alias is a `VLAN IPv4 Address` definition at site scope, Device Function: Access Switch + Aggregation Switch). This is the placeholder.
2. **Alias VALUE assignment** — assigned **per-device via "Save as local profile"** so each switch gets its unique value. Per VSG: *"At the device level of each switch, assign a static IP address to the alias created above"* — this is the canonical mechanism for unique-per-device values without breaking template inheritance.

**Per-device alias values are NOT drift** — they're how aliases are designed to be used. The same alias `SC-SW-IP` legitimately resolves to a different IP on each switch. Don't flag this.

**VSG-recommended DEFINITION scope:**
- **Site** for site-specific definitions (most common — per Campus Deploy §10876-§10891 the SC-SW-IP / SC-SW-TRUNKS pattern)
- **Global** for truly org-wide definitions (e.g., DNS server aliases referenced everywhere)

**VSG canonical alias types** (Campus Deploy §10880, §11251):
- **VLAN IPv4 Address** alias (per-device unique IP — `SC-SW-IP` example)
- **Switchport** alias (inter-switch trunk port lists — `SC-SW-TRUNKS` example)
- **Network destination** alias (RFC-1918 range, DNS server, NTP server)
- **Service** alias (port/protocol references)
- **User** alias (used in role mapping)

**Per-alias checks:**
- VLAN IPv4 Address aliases should have values for ALL devices in the assigned scope (incomplete coverage = profile push will fail on missing-value devices).
- Switchport aliases should have a non-empty list of trunks.
- Aliases referencing other aliases should not be circular.

#### Placeholder default values — MUST walk the hierarchy before flagging

The two-layer model (DEFINITION at Global/Collection/Site, VALUE assigned per-device or per-lower-scope) means an alias **legitimately** carries a placeholder default value at its definition scope when it's intended to be overridden. **An alias whose top-level (Global) value is `1.1.1.1`, `0.0.0.0`, `255.255.255.255`, `192.0.2.x`, `198.51.100.x`, `203.0.113.x` (any RFC-5737 documentation block), an obvious sentinel like `10.0.0.1` paired with the word `placeholder` / `default` / `template` in its name, or just an IP that is clearly not a routable production address — is a default placeholder, not a regression by itself.**

**Mandatory hierarchy lookup before flagging.** When you spot a placeholder default at a higher scope, you MUST trace every place the alias is consumed and verify whether each consumer has an override at scope-or-below before assigning severity:

1. **Identify consumers of the alias.** Search every profile / resource type that can reference an alias by name — primarily Static Routes (the canonical consumer for `Default Gateway -*` / `Next Hop` aliases per §12415–§12416), plus role ACLs, net-services, net-groups, server-host fields in WLAN profiles, AP Uplink profiles, and any `*-Address` / `*-NextHop` field. Use `central_get_scope_resources(scope_id=...)` and `central_get_effective_config(scope_id=..., include_details=true)` walking down from Global → Collections → Sites → Device Groups → Devices.
2. **For each consuming scope, check the alias's effective value.** An alias with a Global default of `1.1.1.1` may have been overridden at a Site Collection, Site, Device Group, or per-device via *Save as local profile*. The effective value at the consuming scope is what actually gets pushed to the device. If `central_get_effective_config(scope_id=<consuming-scope>)` resolves the alias to a real production address, the placeholder at Global is harmless.
3. **Severity follows coverage**, not the placeholder itself:
   - **REGRESSION — placeholder unoverridden at a consuming scope** (the actual bug). Example: `Default Gateway - SW = 1.1.1.1` at Global, referenced by a Global Static Route assigned to a Site that has *no* override → that site's switches will install a static route to 1.1.1.1 and break L3 forwarding. This is what to flag.
   - **DRIFT — placeholder unoverridden at a consuming scope but the consumer is itself unused / disabled / not pushed**: lower-impact (would break only if activated) but still cleanup-worthy.
   - **INFO — placeholder at definition scope is overridden at every consuming scope**: this is the *canonical* alias pattern. List each consumer→effective-value pairing so the operator can see the override is in place; do NOT flag as REGRESSION or DRIFT.
4. **Be explicit in the report.** When you cite a placeholder finding, name the alias, the placeholder value, the consuming profile + scope, AND whether each consumer has an override at scope-or-below. *Do not say "alias defaults to 1.1.1.1" without saying whether each consumer has overridden it* — that's the exact mistake this rule is meant to prevent.

**Drift findings:**
- **REGRESSION — alias definition at device scope only**: an alias whose top-level definition lives at a device (no Site/Collection/Global definition). Device should hold the VALUE, not the definition.
- **REGRESSION — alias missing values on referenced devices**: alias defined and referenced by a profile, but a subset of in-scope devices haven't had the value set via `Save as local profile`. Profile pushes will fail.
- **REGRESSION — placeholder alias unoverridden at a consuming scope**: the alias's higher-scope value is a sentinel (e.g. `1.1.1.1`, RFC-5737 block, etc.) AND a consumer (e.g. a Static Route, a profile) is assigned to a scope that has no override at-or-below. Devices in that scope receive the literal placeholder value. ← *This is the case where you flag REGRESSION.*
- **DRIFT — placeholder alias unoverridden at an inactive/unused consumer**: same shape as above but the consuming profile is not active / not pushed / disabled. Cleanup-worthy but not breaking.
- **DRIFT — conflicting alias definitions across scopes**: same alias name defined differently at Global, Site Collection, AND Site.
- **DRIFT — orphan aliases**: alias defined but no profile / policy references it (waste).
- **DRIFT — hardcoded values where alias exists**: a profile uses a hardcoded IP/port that matches an existing alias's purpose. Operator should switch the profile to reference the alias.
- **DRIFT — incomplete alias coverage**: VLAN IPv4 alias defined at site scope but only assigned to N of M switches.

**INFO findings:**
- **Per-device alias value table** — for each alias used per-device (e.g. `SC-SW-IP`), list the device→value mapping so operators can review without confusing it with drift.
- **Placeholder alias with full override coverage** — alias has a sentinel default at the definition scope but every consumer scope has an override at-or-below resolving to a real value. List the alias name, the placeholder, and each consumer→effective-value pair. **NOT drift; this is the canonical pattern.**

### Step 8 — WLAN Profiles + Named VLANs

**Tools:**
- `central_get_wlan_profiles()` — WLAN library
- `central_get_wlans()` — operational WLANs (sanity check)
- `central_get_named_vlans()` — named VLAN catalog

**VSG-recommended scope:** **Site** for the SMALL-CAMPUS-SITE deployment example. Larger orgs may push WLAN profiles to **Site Collection** (template-by-collection) or **Global** (all sites get the same SSID).

**VSG-recommended per-WLAN values:**
- **Security**: WPA3-Personal for personal SSIDs (VSG §5047), WPA3-Enterprise (802.1X) for corporate. WPA2 acceptable for legacy compatibility.
- **SSID name**: VSG §5083: *"For greatest compatibility with all client devices, do not use spaces or special characters in the [SSID]"*.
- **Min transmit rate**: VSG §4932 / §5094 / §5198: *"recommendation for a balanced environment is a minimum transmit rate of 12 Mbps"*. Lower rates (1, 2, 5.5 Mbps) cause airtime waste.
- **Pre-auth role / default role**: should reference a valid role; `BLACKHOLE` for unauthenticated traffic prior to 802.1X.
- **VLAN**: never VLAN 1 for production WLANs.
- **Captive portal cert**: VSG §364 / §370: *"This procedure uses the default certificate. It is best practice to replace the certificate with a valid certificate"*.
- **MAC randomization**: handle per the org's NAC strategy (most operators allow, with proper Mist NAC / ClearPass Profiler).

**Per-WLAN checks:**
- Open SSIDs (no security): allowed only for guest with captive portal; otherwise REGRESSION.
- WPA2-Personal with shared static PSK: should be considered for migration to MPSK or WPA3-SAE.
- 802.1X without server group: broken auth chain.
- Pre-auth role references deleted role: broken.

**Drift findings:**
- **REGRESSION — bare local-scope WLAN**: WLAN found in `central_get_wlans` for a site but NOT mapped via `central_get_config_assignments` at any scope (i.e., it's a bare local config, not a local profile — primary drift source per VSG).
- **REGRESSION — open SSID without captive portal**: any open SSID for non-guest must be REGRESSION.
- **REGRESSION — VLAN 1 for production WLAN**.
- **REGRESSION — default captive-portal certificate**: VSG explicitly says replace.
- **REGRESSION — broken role/ACL references** in pre-auth/default role.
- **REGRESSION — SSID name with spaces or special chars** (VSG §5083).
- **DRIFT — min transmit rate < 12 Mbps**: VSG-recommended baseline.
- **DRIFT — WLAN profile assigned at Global AND every collection**: redundant; promote or remove.
- **DRIFT — Named VLAN with no profile referencing it**: orphan VLAN.
- **DRIFT — Different VLAN ID for same Named VLAN across sites**: VLAN-naming inconsistency.

### Step 9 — Switch System Profile + System Administration + User Administration + Source Interface (+ auto-imported device-level profiles)

**Tools:** discover via `central_get_config_assignments` filtered by profile_type if filterable, otherwise per-scope traversal.

**VSG-recommended scope:**
- **System > User Administration**: **Site** (deploy guide §10388–10389) for site-scoped admin accounts.
- **System > System Administration**: **Global** for shared admin defaults; **Site** for site-specific.
- **System > Switch System**: **Site** (deploy guide §11659).
- **System > Source Interface**: **Site** (deploy guide §12466).

**VSG-recommended values for Switch System (§11662-§11670):**
- Name: descriptive
- Location: filled in
- Contact: filled in
- Timezone: local for switch
- 802.1X Authentication Server Group: references a Global-scoped server group
- MAC Authentication Server Group: same or different
- Loop Protect Re-Enable Time: VSG §3298: *"By default, the loop-protect re-enable timer is 0. When set to 0, ports disabled by the loop-protect function must be manually re-enabled. Setting the timer to a non-zero value automatically [re-enables]"*. **VSG-recommended: 300 seconds.**

**Critical: auto-imported device-level profiles must be deleted (per VSG §10620-§10625, §10960-§10965, §11024).**

When a switch is onboarded, Central auto-imports values for several profile types (System Administration, STP, Switch System, etc.) and stores them in **device-level profiles named `profile-<device serial>`** with `Inherits From: Self` and the device's internal Central ID as the assigned scope. The VSG explicitly directs operators to **delete these imported device-level profiles** so the higher-scope profile is inherited cleanly. Quote from §10623-§10625: *"The device-level profile blocks inheriting the profile values configured above. For each switch, the device-level profile must be deleted to allow inheriting the above profile settings."*

**Per-profile checks:**
- Switch System: Loop Protect Re-Enable Time = 300 (not 0).
- Switch System: Location/Contact filled in (operational hygiene).
- System Administration: TACACS+ for admin access (VSG §10601).
- System Administration: device-specific admin password set at device level (VSG §798: *"A device-specific Administrator password can be set at the device level"*).
- User Administration: minimal user accounts; operator + read-only roles distinguished.

**Drift findings:**
- **REGRESSION — auto-imported device-level profiles**: any device-level profile whose name starts with `profile-` followed by a device serial number, where `Inherits From: Self`. These should be deleted per VSG. Common types where this pattern occurs: System Administration, STP, Switch System.
- **REGRESSION — Loop Protect Re-Enable Time = 0**: VSG §3298 says set to non-zero. 300 recommended.
- **DRIFT — Switch System Location/Contact empty**: operational hygiene.
- **DRIFT — Switch System assigned at Global with no site-level override**: usually fine if intentional.
- **DRIFT — User Administration at Global**: site-level admin accounts at Global is unusual (privilege concern).
- **DRIFT — same Switch System config at every site**: candidate for Global if no site-specific deltas.

### Step 10 — Interface profiles (Port Profile + Interface Profile + Device Identity)

**Tools:** per-scope traversal via `central_get_scope_resources`. Look for resources of types: `port-profile`, `interface-profile`, `device-identity`.

**VSG-recommended scope:**
- **Interfaces > Port Profile**: **Site** per device-function (Aggregation Switch, Access Switch) — deploy guide §11948–12061, §12263 etc.
- **Interfaces > Interface Profile**: **Site** per device-function — deploy guide §12104, §12312 etc.
- **Interfaces > Device Identity**: **Global** (deploy guide §11753 — *"Scope: Global"*).

**VSG-recommended values for Port Profiles:**
- Default port speed: VSG §1135: *"the default port speed is 25 Gb/s and must be set to 10 Gb/s to"* — verify port speeds are intentional.
- DHCP snooping + ARP inspection set to **trust** on LAG interfaces (VSG §3495: *"DHCP snooping and ARP inspection must be set to trust on the LAG interface to allow clients to"*).
- BPDU Guard enabled on access (untrusted) ports.
- BPDU Filter NOT enabled (VSG §551: *"Using BPDU Filter is not recommended unless the network"*).
- Loop Protect enabled.
- Access VLAN should not be VLAN 1 — per VSG §11416 and §12259: BLACKHOLE VLAN as default for unauthenticated devices.
- Trunk port: VSG §661: *"Best practice for configuring the ISL LAG is to permit all VLANs"*.
- ARUBA-AP role applied to AP-facing trunks (VSG §9534).

**Per-profile checks:**
- Port Profile assigned to wrong device-function (e.g., a Port Profile scoped to Campus AP — Port Profile is for switches).
- Switchport-mode mismatches across redundant pair (one Access, peer Trunk).
- Inactivity / loop-protect timers: VSG §3298, §3279.
- Auto-MDIX: should remain enabled unless specific reason.

**Drift findings:**
- **REGRESSION — Device Identity at Site**: should be Global per VSG.
- **REGRESSION — DHCP snooping/ARP inspection trust missing on LAG** (VSG §3495).
- **REGRESSION — Port Profile assigned to wrong device-function**.
- **REGRESSION — BPDU Filter enabled** (VSG §551 says don't unless specific reason — flag for review).
- **REGRESSION — VLAN 1 as access VLAN** (VSG: BLACKHOLE for default).
- **DRIFT — Port Profile assigned at Global**: usually fine for very-uniform org but unusual; flag for review.
- **DRIFT — proliferation of nearly-identical Port Profiles**: same setting differing by VLAN only across sites; candidate for parameterization via aliases.
- **DRIFT — port-speed override** without justification.
- **DRIFT — ARUBA-AP role missing on AP-facing trunks** if APs deployed.

### Step 11 — Routing & Network Services (Static Routing, DHCP Snooping, AP Uplink, MTU, OSPF)

**Tools:** per-scope traversal.

**VSG-recommended scope:**
- **Routing & Overlays > Static Routing**: **Site** (deploy guide §12415–12416).
- **Network Services > DHCP Snooping**: **Site** (deploy guide §11179).
- **Interface > AP Uplink**: **Site** (deploy guide §10027 etc.).

**VSG-recommended values:**
- **MTU**: VSG §970, §1273: *"Setting the Layer 2 and Layer 3 MTU to 9198 bytes on CX switches is recommended"* AND *"recommends using an MTU value of 9198 on the AOS-10 gateways and AOS-CX"*. Adjacent devices must have matching MTU (VSG §8031).
- **OSPF**: point-to-point links between aggregation/access (VSG §1007). Loopback 0 = router-id (VSG §1581, §1589).
- **DHCP Snooping**: enabled globally on a switch and per-VLAN that has clients.

**Per-profile checks:**
- Static routes referencing deleted/nonexistent next-hops.
- Static routes referencing aliases (e.g. `Default Gateway - SW`, `Default Gateway - GW`, `Next Hop`, `MGMT Default Gateway`) — for each such route you MUST follow Step 7's *placeholder hierarchy lookup*: resolve the alias's effective value at the route's assigned scope (and at every scope below where the route is consumed) before deciding severity. A static route that references an alias whose only definition is `1.1.1.1` at Global, with no override at the consuming scope, is REGRESSION (the device will install the literal placeholder as its next hop). The same route referencing an alias that's overridden per-site or per-device is INFO — that's the canonical pattern.
- DHCP Snooping DISABLED on a client VLAN (security gap per VSG line 11170).
- AP Uplink: VLANs match site's expected VLANs.

**Drift findings:**
- **REGRESSION — DHCP Snooping not enabled on a site that has VLAN-aware ports**: missing security control.
- **REGRESSION — MTU mismatch across adjacent devices** (VSG §8031): OSPF won't form neighbor.
- **REGRESSION — MTU < 9198 on CX/AOS-10** (VSG-recommended): jumbo frames not enabled.
- **REGRESSION — OSPF on broadcast (not point-to-point) for inter-switch links** (VSG §1684: *"Set the OSPF network to point-to-point"*).
- **REGRESSION — Static route uses placeholder-valued alias at a consuming scope with no override**: e.g. `Default Gateway - SW = 1.1.1.1` at Global referenced by a Site-assigned route with no Site/Device-Group/Device-level override. Cross-reference Step 7's hierarchy-lookup procedure. *Do not flag this REGRESSION on the placeholder alone — it's REGRESSION specifically because no consumer overrode the placeholder.*
- **DRIFT — Static Routing at Global**: usually wrong (routes are typically site-specific to local gateways).
- **DRIFT — same AP Uplink profile re-defined at every site**: candidate for site collection.

### Step 12 — VLANs (per-VLAN security + naming)

**Tool:** per-scope traversal looking for `vlan` resources.

**VSG-recommended scope:** **Site** (deploy guide §11420-§11529).

**VSG-recommended values:**
- VSG §594: *"It is best practice to use named VLANs. This allows the grouping of multiple VLAN numbers within"* — use Named VLAN abstraction.
- VSG §11416: *"VLAN 1 is used to initially on-board switches, but it is best practice to move management to"* a dedicated management VLAN.
- VSG §2492: *"It is best practice to have a distinct infrastructure management subnet for switches and wireless"*.
- VSG §8798: *"VLAN 999 (BLACKHOLE) serves as the default VLAN assignment for all wired ports and WLANs to"* — restricted-by-default approach.

**Per-VLAN checks:**
- DHCP Snooping enabled per client VLAN (VSG §11170: *"DHCP snooping must be enabled globally on a switch and individually for each VLAN. The DHCP"*).
- ARP Inspection enabled per client VLAN.
- Source-guard enabled where appropriate.
- VLAN 1 used for management (REGRESSION per VSG).
- BLACKHOLE VLAN (e.g., 999) defined as default for unauthenticated.

**Drift findings:**
- **REGRESSION — VLAN 1 used as production / management VLAN** (VSG §11416).
- **REGRESSION — no BLACKHOLE VLAN defined** (VSG §8798 default for restrictive-by-default).
- **REGRESSION — DHCP Snooping/ARP Inspection disabled on a client VLAN**.
- **DRIFT — VLAN ID number reused for different purposes** at different sites (use Named VLAN).
- **DRIFT — VLAN without IP/SVI on aggregation switches** if it's expected to route.

### Step 13 — STP / Spanning Tree

**Tool:** discover via per-scope traversal looking for STP / MSTP resources.

**VSG-recommended scope:** **Global** for default STP profile, **Site** for per-site STP-priority adjustments.

**VSG-recommended values:**
- STP version: VSG §477: *"to standardize on a common version for predictable STP topology"*.
- Aggregation switches as STP root (VSG §10952: *"STP priority such that a pre-determined VSX pair or VSF stack of switches operates as the known STP root"*).
- STP priority 8 for default profile (VSG §10968).
- BPDU Guard enabled on access ports (VSG §543).
- BPDU Filter NOT enabled (VSG §551).
- Auto-imported device-level STP profiles deleted (VSG §10960-§10965).

**Per-STP checks:**
- Aggregation pair has STP priority lower than access switches (root election).
- BPDU Filter usage justified per the rule above.
- Loop-Protect timer non-zero (VSG §3298).

**Drift findings:**
- **REGRESSION — auto-imported STP device-level profile present**: VSG explicitly says delete (`profile-<serial>` pattern).
- **REGRESSION — BPDU Filter enabled** without justification.
- **REGRESSION — STP priorities don't put aggregation as root** (network instability).
- **DRIFT — STP version mixed across switches**.

### Step 14 — Cross-cutting consistency checks

After steps 1-13, run cross-cutting heuristics. **Three buckets** for any resource that appears at device scope (per VSG §11220-§11377 + §10620-§10625 + §11607-§11637):

| Pattern at device scope | Verdict |
|---|---|
| Resource named `profile-<serial>` with `Inherits From: Self` | **REGRESSION** — auto-imported, delete per VSG so higher-scope profile is inherited |
| Intentional override saved via `Save as local profile` (alias VALUE assignment, per-VLAN switch param tweak, etc.) | **INFO** — list, periodically review. NOT drift. |
| Resource at device scope that's neither of the above (bare local config without going through the local-profile mechanism) | **REGRESSION** — primary drift source |

**Visual cue from the Central UI** (per VSG §11635-§11637): *"A partially filled blue circle to the left of a profile indicates an override is applied, and the Assigned Scope... will show Central's internal device ID for the switch."*

Other cross-cutting heuristics:

- **Per-pair-of-peer-collections diff**: same profile categories assigned in one collection but not the peer? Surface as DRIFT (operator confirms intent).
- **Site count vs. assignment density**: if you have 50 sites and a profile is individually assigned to all 50, it should almost certainly be at the Site Collection or Global scope. Surface as DRIFT.
- **Effective vs committed inconsistency**: if `central_get_effective_config(scope)` shows a config element at a scope that doesn't show up in `central_get_scope_resources(scope, view="committed")` AND doesn't trace back to an ancestor either, that's a phantom config element — investigate.
- **VSX consistency**: VSG §675: *"so it is best practice to re-use the same active gateway MAC value for all active gateway IP"* and §2340: *"It is best practice to assign a unique system MAC to each VSX"*. Detect VSX pair config drift.
- **Device-group standardization**: VSG §1180: *"Best practice is to use the fewest groups necessary to provide logical organization for the network"*. Flag many small groups.
- **Single gateway model per group**: VSG §4413: *"best practice is to standardize a single gateway model within each group"*. Flag mixed-model gateway groups.

## Decision matrix

| Condition | Action |
|---|---|
| Central is `degraded` or `unavailable` | Stop. Audit cannot run reliably. |
| Tree returned 0 collections / sites | Surface this — likely empty org or wrong scope. Confirm with operator. |
| 50+ scopes in tree | Output a high-level summary first; offer to drill into specific collections. |
| User asked for single-site audit | Skip cross-cutting per-collection diff (no peers). |
| Step encounters an unfilterable tool (no profile_type filter) | Per-scope traversal via `central_get_scope_resources`. Each scope adds a round-trip; warn for orgs with 50+ scopes. |
| Bare local-scope config found at any scope (NOT a sanctioned local profile) | Lead REGRESSION section with this. |
| Auto-imported device-level profile (`profile-<serial>` naming) detected | REGRESSION; recommendation is to delete per VSG. |
| Per-device alias VALUE assignments (`Save as local profile`) detected | INFO only — VSG-canonical, NOT drift. List for review. |
| Auth servers / server groups found NOT at Global | Lead REGRESSION section with this. |
| Server group with only 1 RADIUS server | REGRESSION (VSG: 2+ with load balancing). |
| Role count > 60 | INFO finding; operator decides if intentional. |
| Role count > 100 | DRIFT — strong signal of role proliferation. |
| Role with no policy reference | REGRESSION (won't be pushed to any device per VSG rule). |
| Missing canonical roles (ARUBA-AP, BLACKHOLE, REJECT-AUTH, CRITICAL-AUTH) when 802.1X / APs deployed | REGRESSION — VSG-canonical role set incomplete. |
| Open SSID without captive portal | REGRESSION. |
| VLAN 1 as production / management VLAN | REGRESSION per VSG §11416. |
| MTU < 9198 on CX / AOS-10 | REGRESSION per VSG §970/§1273. |
| MTU mismatch across adjacent devices | REGRESSION — OSPF won't form neighbor. |
| Loop Protect Re-Enable Time = 0 | REGRESSION per VSG §3298. |
| BPDU Filter enabled without specific reason | REGRESSION per VSG §551. |
| DHCP snooping/ARP inspection NOT trust on LAG | REGRESSION per VSG §3495. |
| Default captive-portal certificate in use | REGRESSION per VSG §364/§370. |

## Output formatting

Use the EXACT structure below. Every section must be present even if its content is "no findings." Lead with REGRESSION, then DRIFT, then INFO. Keep findings terse; the report is meant to be scannable.

```
## Central VSG-anchored scope audit — <scope: org-wide | <collection> | <site>>
**Captured:** <ISO timestamp>
**Total scopes walked:** <N>
**Total site collections:** <N>
**Total sites:** <N>
**Total device groups:** <N>
**VSG anchor:** Aruba Validated Solution Guide — Campus Design + Campus Deploy + Policy Design + Policy Deploy

### Profile-category summary
| Category | Library count | Assignments count | Most-common scope | VSG-recommended scope | Match |
|---|---|---|---|---|---|
| Auth Servers | <N> | <M> | Global | Global | ✓ |
| Auth Server Groups | <N> | <M> | Global | Global | ✓ |
| AAA Authentication | <N> | <M> | Site | Site | ✓ |
| Roles | <N> | <M> | Site | Site | ✓ |
| Policies | <N> | <M> | Site | Site | ✓ |
| Network Services / Groups / Object Groups | <N>/<N>/<N> | <M>/<M>/<M> | Site | Site | ✓ |
| Aliases | <N> | <M> | Site | Site | ✓ |
| WLAN Profiles | <N> | <M> | Site | Site | ✓ |
| Named VLANs | <N> | <M> | Site | Site | ✓ |
| User Admin / System Admin / Switch System / Source Interface | <N>/<N>/<N>/<N> | <M>/<M>/<M>/<M> | mixed | Site / Global / Site / Site | ⚠ |
| Port / Interface Profile / Device Identity | <N>/<N>/<N> | <M>/<M>/<M> | Site / Site / Global | Site / Site / Global | ✓ |
| Static Routing / DHCP Snooping / AP Uplink | <N>/<N>/<N> | <M>/<M>/<M> | Site | Site | ✓ |
| VLANs / STP | <N>/<N> | <M>/<M> | Site / Global | Site / Global | ✓ |

### REGRESSION findings (lead with these)
- **Auto-imported device-level profiles** (`profile-<serial>` naming, blocks inheritance per VSG): <N> findings.
  - Device `<serial>`: imported `profile-<serial>` for System Administration / STP / Switch System. Recommendation: delete per VSG §10620-§10625, §10960-§10965 to allow inheritance.
- **Bare local-scope configs** (NOT sanctioned via `Save as local profile`): <N> findings.
  - Site `<name>`: VLAN config committed at site scope without going through a profile mechanism. Recommendation: convert to a local profile or push the canonical config up to a higher scope.
- **Auth servers / server groups not at Global**: <N> findings.
  - Server group `<name>` assigned at Site `<name>` (VSG: should be Global). Recommendation: lift to Global.
- **Server groups with only 1 RADIUS server**: <N> findings.
  - Server group `<name>` has 1 server (VSG §5006: 2+ with load balancing required for production).
- **Alias definition at device scope only**: <N> findings.
  - Alias `<name>` has no Site/Collection/Global definition. Recommendation: define at Site, keep per-device VALUE assignments.
- **Placeholder alias unoverridden at a consuming scope**: <N> findings.
  - Alias `<name>` defaults to `<placeholder>` at Global; consumer `<profile-type:profile-name>` is assigned to scope `<scope-name>` which has no override at-or-below. Effective value pushed to devices: `<placeholder>`. Recommendation: either override the alias at scope `<scope-name>` (or a device below it) via *Save as local profile*, or remove the consumer if it shouldn't be active there.
- **Orphan roles** (not pushed to any device): <N> findings.
- **Missing canonical roles** (per VSG): <list — e.g., no ARUBA-AP role despite APs deployed>.
- **Broken references**: <N> findings.
  - Policy `<name>` references role `<deleted-name>`; AAA profile `<name>` references server group `<deleted-name>`.
- **VLAN 1 as production / management VLAN**: <N> findings.
- **Open SSID without captive portal**: <N> findings.
- **Default captive-portal cert in use**: <N> findings.
- **Loop Protect Re-Enable Time = 0**: <N> findings.
- **DHCP snooping / ARP inspection not trust on LAG**: <N> findings.
- **MTU mismatches across adjacent devices**: <N> findings.
- **MTU < 9198 on CX/AOS-10**: <N> findings.
- **BPDU Filter enabled without justification**: <N> findings.
- **Port Profile mis-assigned to wrong device-function**: <N> findings.
- **STP root not at aggregation pair**: <N> findings.

### DRIFT findings
- **Profile redundantly assigned**: <N> findings.
- **Per-site assignments that should be at a collection**: <N> findings.
- **Orphan library entries** (aliases / net-services / net-groups / object-groups defined but unreferenced): <list>.
- **Role count > 60**: count + recommendation to consolidate.
- **Min transmit rate < 12 Mbps on a WLAN**: <N> findings.
- **VLAN naming inconsistencies** (same Named VLAN → different IDs across sites): <N> findings.
- **VSX inconsistencies** (active gateway MAC, system MAC): <N> findings.
- **Mixed gateway models in a group**: <N> findings.

### INFO findings
- **Sanctioned device-level local profiles** (intentional `Save as local profile` overrides — VSG-canonical, NOT drift; listed for periodic review): <N>.
- **Per-device alias VALUE assignments** (canonical aliases pattern — NOT drift): <N>.
  - Alias `SC-SW-IP` resolves to:
    - device `<serial-1>`: `10.6.15.11/24`
    - device `<serial-2>`: `10.6.15.12/24`
- **Placeholder alias with full override coverage** (canonical pattern — NOT drift): <N>.
  - Alias `<name>` defaults to `<placeholder>` at Global; every consumer scope has an override at-or-below resolving to a real value. Listed:
    - consumer `<profile-type:profile-name>` @ scope `<scope-name>` → effective value `<resolved-value>` (override at scope `<override-scope>`)
- **Role → policy → device-function linkage** (table).
- **Per-collection inconsistency**: e.g., WLAN `guest` at collection `HQ-East` but missing at peer `HQ-West`. Confirm intent.
- **Configuration that's likely intentionally site-specific** (no recommendation): <list>.

### Recommended next actions
- Bulleted list of operator actions, ordered by severity.
- Each action references which finding it addresses.
- (or "No actions — config is in good shape per VSG.")
```

## Example queries that should trigger this skill

> "audit Central scope"
> "where are my Central WLAN profiles assigned?"
> "is my Central config drifting?"
> "show me the Central scope hierarchy with VSG comparison"
> "audit Central roles and policies"
> "find orphan roles in Central"
> "Central configuration audit"
> "Central VSG audit"
> "audit Central STP / VLAN / DHCP snooping"
> "validate Central authentication chain"
