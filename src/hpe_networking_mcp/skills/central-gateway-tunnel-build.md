---
name: central-gateway-tunnel-build
title: AOS 10 Mobility Gateway + tunnel-mode WLAN in New Central — build, verify, troubleshoot
description: |
  Build, change, or troubleshoot an HPE Aruba AOS 10 Mobility Gateway and a
  tunnel-mode WLAN managed by New Central: gateway System IP / controller-ip,
  gateway onboarding after ZTP, gateway clusters, AP-to-gateway tunnel
  anchoring, client roles and role-based policies on the gateway.

  Match phrases include: "AOS 10 gateway", "Mobility Gateway", "controller-ip",
  "system IP", "tunnel mode WLAN", "tunnel orchestrator", "OTO", "ipsec-map",
  "bucket map", "Isoleader", "cluster member IP", "VLAN 4094", "local override",
  "Reset Config", "show ap active is empty", "SM_STATE_CONNECTING",
  "overlay-wlan", "Primary Gateway Cluster", "gw-cluster-list", "dtunnel",
  "WLAN will not anchor", "gateway has no virtual-AP", "RADIUS sourced from the
  AP", "CONFIG FAILURE on the gateway", "Unknown access-list", "SSID flaps".

  Carries field-proven fault signatures, a forced rebuild order, and a list of
  Central read instruments that return EMPTY on objects that exist. Writes are
  gated by ENABLE_CENTRAL_WRITE_TOOLS and elicitation.
platforms: [central]
tags: [central, aos10, gateway, mobility-gateway, tunnel, wlan, overlay, cluster, troubleshooting, config-model, write]
tools:
  - health
  - central_get_devices
  - central_get_scope_tree
  - central_get_effective_config
  - central_get_config_assignments
  - central_manage_config_assignment
  - central_show_commands
  - central_get_gw_system
  - central_manage_gw_system
  - central_get_layer2_vlan
  - central_manage_layer2_vlan
  - central_get_vlan_interfaces
  - central_manage_vlan_interfaces
  - central_get_ethernet_interfaces
  - central_manage_ethernet_interfaces
  - central_get_static_route
  - central_manage_static_route
  - central_get_dns
  - central_manage_dns
  - central_get_management_users
  - central_get_local_management
  - central_get_system_info
  - central_manage_system_info
  - central_get_gateway_clusters
  - central_manage_gateway_clusters
  - central_get_cluster_members
  - central_get_wlan_profiles
  - central_manage_wlan_profile
  - central_get_overlay_wlan
  - central_manage_overlay_wlan
  - central_get_roles
  - central_manage_roles
  - central_get_policies
  - central_manage_policies
  - central_get_server_groups
---

# AOS 10 Mobility Gateway + tunnel-mode WLAN in New Central

## Objective

Bring an AOS 10 campus Mobility Gateway to a state where it terminates AP
tunnels and anchors tunnel-mode WLAN clients, and diagnose it when it does not.
The procedure enforces a build order whose dependencies are real (getting it
wrong strands an ACP-managed gateway that has no writable CLI), verifies every
write on the device rather than trusting the API, and gives the fault
signatures that distinguish the common failures.

Claims below carry a confidence label where it matters:

| Label | Meaning |
|---|---|
| `[doc-grounded]` | Stated in vendor documentation |
| `[proven]` | Observed on a device, repeatedly or with captured output |
| `[observed-once]` | One observation on one tenant/firmware — treat as a hypothesis and verify before acting |

An untagged claim is not validated. Several earlier versions of these findings
were wrong because a single observation was written as a universal fact; keep
that in mind before generalising anything here.

## Prerequisites

- Central reachable: run `health(platform="central")` first.
- Write tools enabled (`ENABLE_CENTRAL_WRITE_TOOLS`) for any build/change step.
  Diagnosis is read-only.
- The gateway's serial number, its site scope id, and (for WLAN work) the AP
  device group / site that serves the SSID. Resolve scope ids from
  `central_get_scope_tree`, never from a display name.
- For any change to the gateway's reachability set (Step 2) or a Reset Config
  (Step 3): console or physical access available, or a confirmed DHCP recovery
  path on the same switch port. Central has **no auto-revert** — a bad push is
  not backed out, the device simply drops off.
- Use the **New Central** documentation set. URLs must contain
  `techdocs/new-central/`. Classic Central pages (for example "Provisioning
  Gateways", Gateway Pools) describe a different product path and will send you
  down dead ends. Key pages:
  - Onboarding: https://arubanetworking.hpe.com/techdocs/new-central/content/get-started/onboard-gws.htm
  - Hierarchy: https://developer.arubanetworks.com/new-central/docs/new-central-hierarchy
  - Rename hostnames: https://developer.arubanetworks.com/new-central/docs/rename-hostnames
  - AOS 10 tunnel orchestrator (OTO), cluster formation/planning, and the
    *AOS-10 APs and Mobility Gateways Configuration* guide.
- Read the onboarding doc before diagnosing a gateway you did not build — it
  explains where VLAN 4094 comes from, what auto-import does, and names the
  remedy for a stuck device.

## The two facts that explain most failures

### Fact 1 — the System IP must be a VLAN interface, never a loopback  `[proven]`

A loopback has no linktag, so the datapath cannot resolve a VLAN for the
tunnel-termination IP and the IPsec map is never packed. The API and the
orchestrator stay green while the tunnel is dead.

Fault signature (`show log errorlog` on the gateway):

```
ipopulate_vlan_from_linktag 558 IPv4 VLAN is not learnt from FPAPPS configured ip <loopback-ip>
pack error
fpapps procIkeIpsecMsg: Unable to find the ipsec map for ap-ipsecmap-<ap-mac> ... TUN_DOWN
dim handle_device_reg_msg: No device entry found for <ap-mac>
```

Corroborating:
- `show crypto-local ipsec-map` -> `Sos Program: Ingress: Yes Egress: NO`, `Peer gateway: 0.0.0.0`, `Interface: VLAN 0`
- `show datapath ipsec-map` -> 0 entries
- `show crypto oto` -> `BG-SRC Err SPI/Map/Vlan/B-Mesh` with the **Vlan** column climbing
- AP `show ata endpoint` -> HBT Rcv 0, state `SM_STATE_CONNECTING`
- `show controller-ip` says *"configured to be loopback interface"* — that IS the fault.

Do **not** diagnose from `show crypto isakmp sa`. Per the OTO doc, AOS 10
skips IKE phase 1/2 — the orchestrator generates SPIs and keys.
`% No active ISAKMP SA` and the CPSEC/mode-config counters are expected.
`[doc-grounded]`

### Fact 2 — a tunnel-mode WLAN needs a gateway-cluster BINDING  `[proven]`

A WLAN can sit at `forward-mode: FORWARD_MODE_L2` (that is tunnel; the enum
has only `FORWARD_MODE_BRIDGE` and `FORWARD_MODE_L2`) with an empty Primary
Gateway Cluster and **no `overlay-wlan` object**. Nothing warns you; it
broadcasts and no client ever anchors. The binding is a separate object:

```
central_get_overlay_wlan(view_type="LOCAL", scope_id="<site-scope-id>", device_function="CAMPUS_AP")
-> {}   NO BINDING — this is the fault

healthy:
{"profile": "<ssid>", "overlay-profile-type": "WIRELESS_PROFILE", "essid-name": "<ssid>",
 "gw-cluster-list": [{"cluster": "<cluster-name>", "cluster-redundancy-type": "PRIMARY",
                      "cluster-scope-id": "<site-scope-id>", "cluster-type": "CLUSTER_ID",
                      "tunnel-type": "GRE"}]}
```

Fault signature — the tunnel infrastructure is fully healthy (Step 8 passes),
but:
- gateway `show wlan virtual-ap` -> `Virtual AP profile "default" undefined.`
- gateway `show wlan ssid-profile` -> `SSID Profile "default" undefined.`
- gateway `show aaa profile` -> no AAA profile for the SSID (a healthy one
  appears automatically as `<ssid>_<digits>_`)
- gateway RADIUS counters never move during a client attempt
- client events show `Client 802.1x Radius Reject` / `Client EAP Failure`,
  and the RADIUS server logs the request **sourced from the AP's IP**, not the
  gateway's system IP — the AP has fallen back to terminating 802.1X itself.

## Procedure

### Step 1 — Read the device, not just Central

**Tool:** `central_show_commands(serial_number="<serial>", device_type="gateways", commands="show switches,show controller-ip,show configuration failure")`
**Why:** Central config reads return Central's intent. A push failure is
usually state Central does not know about. Every diagnosis starts on the device.
**Expected result:** Command output for each command.
**If anomaly:**
- `device_type` for this tool is **lowercase plural** — `aps` / `cx` /
  `aos-s` / `gateways`. `central_get_devices` uses `ACCESS_POINT` / `SWITCH` /
  `GATEWAY`. Using the wrong enum returns an error or `null`, which is easily
  misread as "this device type cannot be instrumented". It works for APs too.
  `commands` is one comma-separated string, not a list.
- Direct SSH to the gateway: plain non-interactive SSH returns an **empty**
  result. Allocate a pty (`ssh -tt`); the gateway may also need legacy
  algorithms (`-o KexAlgorithms=+diffie-hellman-group14-sha1 -o HostKeyAlgorithms=+ssh-rsa`).
  Never conclude a line is absent from an empty non-pty SSH result.
- An ACP-managed gateway refuses both `configure terminal` and exec `write`
  (*"This controller is managed by an ACP"*), but every `show` command works.
  Budget for no CLI changes before planning a device-level fix.

Reading `show switches` and `show configuration failure`:
- `show configuration failure` is a **history, newest first** (24+ entries
  observed). Read the head, not the tail.
- Correlate ConfigIds: `Configuration State: CONFIG FAILURE(118)` with
  `Config ID: 119` means the latest push succeeded — the state string is a
  sticky label naming the last failed id. Central's `topPriorityIssue` flattens
  this history, mixing stale and current errors.
- Config Rollback with **Total Failures 0** is a commit-confirm timeout, not a
  bad config: look in `show log errorlog` for `cfgm_rollback_timeout` /
  `cfgm_rollback_is_bad_config` (the ACP web-socket did not re-establish inside
  the rollback window). Total Failures > 0 means a command was really rejected.
- When a push error names an object, read that object on the device before
  changing Central again:

```
show running-config | include <object-in-the-error>
show aaa rfc-3576-server | show aaa server-group | show rights
show aaa profile <name>
```

Worked example `[proven]`: `RFC 3576 Server "<ip>" is in use` on every push
touching one WLAN, while Central showed that server unused. The real holder was
a *different* SSID's AAA profile: its `primary-auth-server` drives
`rfc3576-server-list`. The gateway AAA profile is system-created and the
binding is stored, not recomputed — repoint the source field on the WLAN. If you
have changed Central more than once without a fresh device reading, you are
poking, not diagnosing.

### Step 2 — Enumerate what lives at each scope (and which instruments lie)

**Tool:** `central_get_scope_tree()` — walk to the gateway's device node and read its `resources`.
**Why:** It is the enumerator that proved reliable. Several scoped reads return
EMPTY on objects that demonstrably exist.  `[proven]`
**Expected result:** On a pre-provisioned gateway the device scope typically
holds `layer2-vlan/*`, `vlan-interfaces/*`, `static-route/*`,
`ethernet-interfaces/*`, `aliases/sys_vlan_ipv4_4094`,
`system-info/sys-system-info-profile`, `gw-system/*`.
**If anomaly:** Treat an empty result from the calls below as a statement
about the instrument, not the device:

| Call | Returned | Truth |
|---|---|---|
| `central_get_config_assignments(scope_id=<device-scope>)` | `{"config-assignment": []}` | 9 resources at that device scope (the same call returns rows at site scope — it does not enumerate device scope) |
| `central_get_system_info(...)` — scope only; +device_function; +object_type=LOCAL; library | `{}` every time | `system-info/sys-system-info-profile` present at the device scope |
| `central_get_gateway_clusters(scope_id=<site>, device_function="MOBILITY_GW")` | `{}` | the cluster object present at that site |

Local vs inherited: use
`central_get_effective_config(scope_id=<scope>, persona=<persona>, include_details=True)`
and read `instances[].origin_scope_name` — **two origins = a LOCAL override
shadowing a parent; one origin = inherited**. `include_details=True` returns no
config payload; it proves *where*, not *what*. Do **not** classify with
`metadata.count_objects_in_module.LOCAL` (reported 0 with two local overrides
present) or by diffing a scoped read against the parent (a scoped read returns
the effective set, so a zero diff means inherited, not duplicate). Positive proof
of a local object: divergent field values or vault handle. `central_get_effective_config`
also reported device-group contents as absent when they existed.
`[proven]`

Central scope model `[doc-grounded]`: five scopes each with its own config
database (Global, Site Collection, Site, Device, Device Group); three parallel
pathways reach a device — `Global > Site Collection > Site > Device`,
`Global > Site > Device`, `Global > Device Groups > Device`. Device Group is
parallel to Site, not beneath it; a sweep of one path that finds nothing is not
evidence of absence. Onboarding, site/group assignment, group creation and
persona configuration are Classic Central functions, not in the New Central
config API. Use the **CLI Viewer** (scope configuration page) to see what objects
render into instead of inferring it from device output.

### Step 3 — Know which onboarding path the gateway took

**Tool:** `central_get_scope_tree()` plus `central_get_dns(...)` / `central_get_management_users(...)` at site/global scope.
**Why:** DNS, User Administration and System Information land at different
scopes depending on onboarding path, and that decides what a Reset Config wipes.  `[doc-grounded]`

| Path | Where DNS / User Administration / System Information land |
|---|---|
| **Auto-import** (gateway had connectivity config and was moved into a New Central group) | **Device scope.** *"Auto-imported configurations are pushed only at the device level."* The doc's sample table lists `mgmt-user admin root …`, `ip name-server …`, `hostname …` |
| **Pre-provision** (step 7 of the onboarding doc) | Global / Site Collection / Site, *"assign to Global, Site Collections, or Site scope as required"* |

**Expected result:** You know, for this gateway, which objects are device-owned.
**If anomaly:** Do not assume either path. The doc also warns: *"Any
configurations made at higher scopes for the same device will be overridden at
the device level during auto-import. If you want to move the configuration of
the same object to a higher scope, you must first create the same object at
higher scope and then delete the device-level object."*

Other facts: all ZTP ports land in **VLAN 4094** and the ZTP uplink is a DHCP
client there — normal.

### Step 4 — Build the reachability set, in this order

The reachability set — every item a Central-managed gateway needs to stay
reachable. Items 1-5 are device-scope on a normally built gateway and **are wiped
by Reset Config / factory reset**, so each is rebuild work, not a "check and
proceed" item:

| # | Element | Object / tool |
|---|---|---|
| 1 | Uplink port VLAN membership (trunk + native VLAN) | `ethernet-interfaces`, device scope — `central_manage_ethernet_interfaces` |
| 2 | VLAN with L3 static address | `central_manage_layer2_vlan` + `central_manage_vlan_interfaces` |
| 3 | Default gateway | Static Routing > Device-Specific Parameters > Gateway/AOS-S Parameters > Default Gateways — `central_manage_static_route` |
| 4 | DNS Server profile | `central_manage_dns` (site or device scope) |
| 5 | System IP VLAN | Gateway System profile — `central_manage_gw_system` |
| 6 | Management pointer (`mgmt-server ... default-acp`) | auto-import / local override; regenerates |

**Build order (dependencies are real):**

1. **Uplink port trunk + native VLAN.** Until this, the VLAN owns no port and
   stays protocol DOWN.
2. **VLAN L3 static address.** Enable L3 and set a static IP. Set **IPv6 Address
   Assignment to DHCP** if the profile exposes it — it defaults to
   Static-with-empty-address, commits `ipv6 address static` with no address,
   and puts the device into Config Rollback.  `[proven]`
3. **Default gateway** — via the Default Gateways device-specific parameter. The
   generic *IP Routes* row does NOT render on a gateway. The device-scope object
   is a `default-gateway` structure:
   ```json
   "default-gateway": [{"dg-name": "1", "forwarding-type": "NEXTHOP",
                        "ipv4-address": "<default-gw-ip>", "metric": 1}]
   ```
4. **DNS** — mandatory; without a resolver the gateway cannot resolve the
   Central FQDN. Most often forgotten, because on a fresh gateway DNS arrives by
   DHCP on VLAN 4094 and silently vanishes when the uplink becomes a static trunk.
5. **Gateway System profile — System IP VLAN = the VLAN from step 2. No
   loopback.** A VLAN appears in the *IPv4 System IP VLAN* drop-down **only once
   it has a static IP**; an empty drop-down means step 2 has not taken, not a
   platform limit. Use the drop-down as a progress indicator.
6. **User Administration** (`mgmt-user admin`) — at device scope on an
   auto-imported gateway, at a higher scope if pre-provisioned (Step 3).
7. The cluster re-forms on its own once the member IP matches the system IP.

**Tool (verify):** `central_show_commands(serial_number="<serial>", device_type="gateways", commands="show ip route,show ip domain-name,show switches,show controller-ip")`
**Expected result:** `S* 0.0.0.0/0` present; at least one name server;
`UPDATE SUCCESSFUL` and **not** `(Conductor Unreachable)`;
`configured to be vlan interface: N`.
**If anomaly:**
- `(Conductor Unreachable)` is an emergency. A gateway can show correct system
  IP, trunk, VLAN and cluster while losing its control plane.
  Diagnostic split:

  | Observation | Fault |
  |---|---|
  | ping default gw OK + ping a public IP OK + manager unreachable | DNS (item 4) |
  | ping a public IP fails | default route (item 3) |
  | VLAN protocol DOWN | uplink port (item 1) |

- **Step 2 before step 1 fails reproducibly** `[proven]`: while the uplink is
  still in VLAN 4094 on DHCP, the lease often holds the very address you are
  setting statically, and the push fails:
  ```
  profmgr_app_cmd_failure: App error: "Error: IP address conflicts with another interface "
    executing "ip address <uplink-ip> 255.255.255.0 "
  fpapps: switchVlanIpAddrCfg: ADD request failed for address <uplink-ip> on vlan 1, error 15
  cfgm: update_failed_state: State(ACP(UP):CONFIG FAILURE:CFGID-<n>:...)
  ```
- **If the gateway is already cut off, fix the manager, not the device.**
  `configure terminal` is refused, so nothing is repairable locally. Complete
  the Central-side config while the device is offline, then recover it, so the
  config it pulls is self-sufficient — otherwise recovery loops as the device
  keeps pulling a config that re-strands it. A plain `reload` does not return an
  ACP gateway to the factory DHCP posture; `write erase all` does, and it is
  accepted (unlike `configure terminal`).  `[proven]`

### Step 5 — Carry tagged client VLANs out of the uplink

**Tool:** `central_get_ethernet_interfaces(name="<port>", view_type="LOCAL", scope_id="<device-scope>", device_function="MOBILITY_GW")`, then `central_manage_ethernet_interfaces(...)`
**Why:** A tunnel-mode WLAN whose client VLAN cannot reach the wire makes the
VAP appear and vanish on a ~1 Hz cycle (the SSID flaps). It is not a DHCP
failure — that leaves the SSID up with no address.
**Expected result:** The uplink is a trunk carrying the client VLANs. All three
must be true; missing any one produces the same flap:
1. The VLAN is assigned to the **MOBILITY_GW** persona, not only CAMPUS_AP.
   Check `central_get_config_assignments(profile_type="layer2-vlan")` and the
   device-function column.
2. The VLAN is **enabled** (`"enable": true`, compare with VLAN 1). A VLAN
   created by assignment alone may have no enable flag.
3. The uplink port is a **trunk**. Monitoring showing `portType: Access, vlan: 1`
   means the port untags everything `[doc-grounded]` — an access uplink cannot
   emit a tagged client VLAN.

Payload — the trunk field is **`trunk-vlan-ranges`**; there is no
`allowed-vlans` node under `switchport` (guessing it gives a YANG parse error):

```json
"switchport":    {"interface-mode": "TRUNK", "native-vlan": 1, "trunk-vlan-ranges": ["1", "<client-vlan>"]}
"trusted-vlans": ["1", "<client-vlan>"]
```

Keep native VLAN 1 (or whatever carries management untagged) so the conversion
is a non-event — observed 0% loss on the gateway and upstream switch.
**If anomaly:** Learn the accepted payload shape on an **unused port first**,
read it back, then apply the proven shape to the live uplink. A wrong field name
is rejected server-side, but a *valid but wrong* payload on the only uplink
strands an ACP-locked box with no CLI to recover it.

Do **not** validate tunnel mode with the upstream switch MAC table. Client
traffic rides the AP-to-gateway GRE tunnel, so `No MAC entries found` for the
client VLAN on the access switch is expected. Bridge mode: the switch MAC table
is a valid check. Tunnel mode: check the gateway — `show datapath tunnel`,
`show user-table`, `show datapath vlan` (is the VLAN on the tunnel ports).

### Step 6 — Cluster

**Tool:** `central_get_gateway_clusters(name="<cluster>")`, `central_get_cluster_members(cluster_name="<cluster>")`, and on the device `show lc-cluster group-membership`, `show controller-ip`
**Why:** The cluster member IP must equal the gateway's system IP.  `[proven]`
**Expected result (single-node):**
```
show lc-cluster group-membership
  Cluster Enabled, Profile Name = "<cluster-name>"
  Heartbeat Threshold = 900 msec
  self <gw-system-ip>   128   N/A   ISOLATED (Leader)
show controller-ip
  Switch IPv4 Address: <gw-system-ip>
  Switch IPv4 is configured to be vlan interface: <N>
```
**If anomaly:**
- A member written without its `ip` field rendered `controller-ip 0.0.0.0` and
  `Cluster Disabled` while the Central object read back clean. Restarting does
  NOT fix a member-IP mismatch — correct the member.  `[proven]`
- `ISOLATED (Leader)` ("Isoleader" in the UI) on a lone node is normal. A
  single-node cluster is valid and documented.  `[proven]` / `[doc-grounded]`
- An all-zero STM bucket map on a single-node cluster is not a fault — values
  are UAC indices and with one gateway every bucket is `00`. Only with more than
  one member and an expected spread are zeros a fault.
- A gateway MAC belongs to exactly one cluster; emptying `ipv4-gateways` does not
  release it — delete the old cluster profile.  `[observed-once]`
- Auto group clustering is the default; auto clusters are named `auto_group_XXX`
  `[doc-grounded]`. A cluster not named that way was created manually. A manual
  cluster at site-collection scope is accepted by the model but is not the
  documented shape — call it out. `auto-cluster` cannot be enabled on a manually
  created cluster (HTTP 400), so the choice is made at creation.

### Step 7 — Tunnel-mode WLAN and its overlay binding

**Tool:** `central_get_wlan_profiles(ssid="<ssid>")`, `central_get_overlay_wlan(detailed=True)`, `central_manage_wlan_profile(...)`, `central_manage_overlay_wlan(...)`
**Why:** The WLAN profile and the cluster binding (`overlay-wlan`) are separate
objects; both must exist and be assigned.
**Expected result:** WLAN at `FORWARD_MODE_L2`; `overlay-wlan` with a
`gw-cluster-list` PRIMARY entry; both `wlan-ssids` and `overlay-wlan` assigned
to `CAMPUS_AP`.

Rules `[doc-grounded]` unless marked:
- **A tunnel-mode WLAN must be a Library (shared) profile**, assigned to the
  **device groups containing the APs** that serve the ESSID (*"Future updates
  will add support to assign WLAN profiles to any scope"*). In the UI, ticking
  *Create as a local profile* removes the Tunnel and Mixed options. Site-scope
  assignment has been seen to work, but the doc lists it as future — call the
  deviation out.
- A shared WLAN **cannot reference a site-LOCAL server group**:
  `Cannot find in library '<name>' of type 'aruba-auth-server-group' referred in '<ssid>' of type 'aruba-wlan'`.
  Promote the AAA objects to the Library.
- **Forwarding mode:** *"You must select Tunnel for AP and Mobility Gateway
  deployments. The Bridge option is for AP-only deployments. The Mixed option is
  for AP and Mobility Gateway, but allows some VLAN to be trunked to the
  switching fabric based on user session VLAN assignment."* Mixed is the
  documented answer to "some sessions local, some tunnelled".
- APs need **not** be in the cluster's device group: *"it is not mandatory for
  the APs to be in the same device group as the cluster"*. Group membership is
  not the binding; the WLAN's cluster reference is.
- The vendor *Configure Tunneled SSID* workflow's prerequisite: *"Underlay is
  configured with Gateways in established cluster and any VLANs configured &
  assigned to the appropriate scopes"* — the cluster must exist before the
  overlay WLAN.
- Give tunnelled SSIDs their own client VLAN (see the underlay-VLAN note in the
  troubleshooting reference).

**`cluster-scope-id` — use the SITE scope id.**  `[proven]` A vendor reference
workflow carries the comment `# Change the cluster-scope-id to match your AP
Device Group`. Following it took a working SSID off air (it vanished from
`show ap bss-table`; other SSIDs on the same AP were unaffected). Central renders
the field red but accepts the write. Copy the value from a known-working sibling:
`central_get_overlay_wlan(detailed=True)` and compare
`gw-cluster-list[].cluster-scope-id`.

**The binding cannot be edited in place.**  `[proven]`
- `central_manage_overlay_wlan(action_type="create")` returned **HTTP 500** on a
  payload the parser accepted, at every scope; update returned "profile doesn't
  exist". The undocumented required sub-fields (`cluster-scope-id`,
  `cluster-type`, `tunnel-type`) are implicated.
- Update fails on an SSID with a Central NAC captive portal:
  `Profile not found in library for aruba-aaa-captive-portal/sys_cnac_<ssid>` —
  updating `overlay-wlan` revalidates every referenced profile, and the
  system-generated portal is not in the library view. An SSID with no portal
  updates fine.
- In the UI, Traffic Forwarding Mode and Primary/Secondary Gateway Cluster are
  greyed out on an existing WLAN at site and Library scope.

**Repair = delete and recreate:**
1. Baseline the full WLAN profile, the `overlay-wlan`, and every config
   assignment naming the SSID.
2. Delete `overlay-wlan`, then the WLAN profile.
3. Recreate the WLAN as a **library** object (no `object_type` / `scope_id`).
4. Recreate `overlay-wlan` with the correct `cluster-scope-id` (or use the UI
   Create WLAN flow if the API create keeps returning 500).
5. Re-assign **both** `wlan-ssids` and `overlay-wlan` to `CAMPUS_AP`
   (`central_manage_config_assignment`).
6. The gateway AAA profile regenerates with a **new** id (`<ssid>_<epoch>_`);
   re-point anything that referenced the old one.

UI traps when recreating `[doc-grounded]`:
- The Primary Server drop-down lists only library auth servers; use the inline
  *New Authentication Server* link.
- WPA2-Enterprise (and WPA-Enterprise, Both, Dynamic WEP) is greyed out until
  you **uncheck 6 GHz and Wi-Fi 7 (802.11be)**.
- Auth Server Mode must be **RADIUS with CoA** for Change-of-Authorization, and
  Dynamic Authorization must also be enabled in the Authentication Server Global
  profile — a separate object.
- A healthy push is observable: the gateway grows an AAA profile
  `<ssid>_<digits>_` (with 802.1X profile, default role and an `..._auth_svg`
  server group) and `show switches` Config ID advances. Config ID moving without
  the AAA profile appearing means the binding did not take.

**Are forwarding mode / Primary Gateway Cluster create-only?**
`[observed-once]`, **contested**. The UI greys them out on an existing WLAN.
But `central_manage_wlan_profile` exposes `forward-mode` as an ordinary PATCH
field and `central_manage_overlay_wlan` accepts `action_type="update"` — neither
is marked create-only in the schema. Two vendor docs describe only the create
path and neither forbids conversion. This cannot be settled from documentation;
only a test on a tenant you are permitted to experiment on can close it. Do not
use "the WLAN would have to be recreated" as a cost estimate in a rebuild
decision until it is tested.

### Step 8 — Roles and policies on the gateway

**Tool:** `central_get_roles(name="<role>", view_type="LIBRARY")`, `central_manage_roles(...)`, `central_get_policies(...)`, `central_manage_policies(...)`, then device `show rights <ROLE>`
**Why:** A role in Central is not a role on the device.
**Expected result:** `show rights <ROLE>` lists the role with an ACL named
`sys_policy_<ROLE>` containing your rules.
**If anomaly:**
- **Unfiltered lists omit objects that exist — query by name.**  `[proven]`
  `central_get_roles()` omitted an object that `central_get_roles(name="X", view_type="LIBRARY")`
  returned in full. Causes: default page size (25 against 59 objects) and
  library objects missing from scoped list reads. If still in doubt, a create
  returning `Cannot create duplicate config … already exists in Library` proves
  existence.
- **A `LOCAL` create can silently become a Library object.**  `[proven]`
  `central_manage_roles` with `object_type="LOCAL"` + `scope_id` +
  `device_function` returned `SUCC_001` and produced a role that existed only in
  the Library, assigned to no scope. The client fell through to the 802.1X
  default role and `authorization.default-vlan-id`. After creating a role,
  verify it is **assigned** at the scope that serves the gateway.
- **A role renders only if something references it** — a WLAN
  `auto-default-role`, `pre-auth-role`, or a Role Assignment Rule. An
  unreferenced role never appears in `show rights`, so a RADIUS-returned role
  name resolves to nothing. Cheap test of a role attribute: add it to a role
  that already renders.
- **`Unknown access-list '<policy-name>'` may be spurious.** Central compiles an
  intent policy into `sys_policy_<ROLE>` and also emits a raw
  `access-list session <policy-name>` binding the device rejects. Check before
  acting:
  ```
  show rights <ROLE>
  show running-config | include "ip access-list session"
  show running-config | include <policy-name>     # empty => push-time only
  ```
  If `sys_policy_<ROLE>` holds your rules, the policy is live.
- **A policy with no substantive rules emits no ACL** (e.g. only
  `role -> any: permit`), giving a self-inflicted `Unknown access-list`. A
  placeholder policy needs one real match — a deny to an RFC 5737 prefix such as
  `192.0.2.0/24` is a safe no-op.
- **Never delete a policy a role references** — the dangling reference makes
  every subsequent push to the device fail (recorded under PATCH semantics; not
  re-tested with PUT). To neutralise in place, repoint its deny destinations at
  `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`.
- **Role Assignment Rules are in the config model** (not UI-only):
  ```json
  "assignment-rules": {"assignment-rule": [
    {"sequence-id":1,"attribute":"CLASS","operator":"VALUE_OF","assign-action":"ASSIGN_ROLE"},
    {"sequence-id":2,"attribute":"CLASS","operator":"MATCH_EQUAL","operand":"<value>",
     "assign-action":"ASSIGN_ROLE","role":"<ROLE>"}
  ]}
  ```
  `VALUE_OF` = UI "Is the Role" (AOS 8 `set role condition <attr> value-of`);
  `MATCH_EQUAL` needs `operand` and `role`. They render as server-group
  Role/VLAN derivation rules. Writing them to a WLAN propagates to the gateway
  server group; removing them from the WLAN does **not** — update both.
- **`ARUBA_USER_VLAN` as a role-derivation condition does not derive a role.**
  It is accepted, renders, reads `Validated: Yes`; the client gets the VLAN via
  the VSA and stays in the 802.1X default role. AOS 8
  `set role condition Aruba-User-Vlan equals "<vlan>" set-value <ROLE>` does not
  port — use `Aruba-User-Role` or `Class`.  `[proven]`
- ACL numbers in `show rights` change across config generations and site moves —
  never cite or reuse one.

### Step 9 — Verify a healthy tunnel

**Tool:** `central_show_commands(serial_number="<gw-serial>", device_type="gateways", commands="show controller-ip,show crypto-local ipsec-map,show datapath ipsec-map,show crypto ipsec sa,show datapath tunnel,show crypto oto,show lc-cluster group-membership")`
and `central_show_commands(serial_number="<ap-serial>", device_type="aps", commands="show ata endpoint,show ap debug stm-bucketmap")`
**Why:** The real proof of tunnel health on both ends.
**Expected result:**
```
GATEWAY
show controller-ip                -> "configured to be vlan interface: N"   (NOT loopback)
show crypto-local ipsec-map       -> Peer gateway: <ap-ip>, Interface: VLAN N, Key Valid: Yes,
                                     Sos Program: Ingress: Yes Egress: Yes, Boot-Strap State: Done
show datapath ipsec-map           -> >= 1 entry
show crypto ipsec sa              -> Total IPSEC SAs >= 1
show datapath tunnel              -> Current Entries (AP GRE) >= 1
show crypto oto                   -> Channel state CONNECTED, BG-SRC Err .../Vlan/... = 0
show lc-cluster group-membership  -> Cluster Enabled, self <system-ip>
AP
show ata endpoint                 -> IP ADDR = gateway system IP, SM_STATE_CONNECTED, HBT Rcv non-zero, Missed 0
show ap debug stm-bucketmap       -> UAC = gateway system IP
```
Central UI: Devices > Gateways > Clusters > cluster > Summary (VLAN Mismatch:
No), Gateways (node Up), Tunnels (Status Up).
**If anomaly:** Fact 1 signature -> System IP. Tunnel healthy but no client
anchors -> Fact 2 signature.

**`show ap active`, `show ap database` and `show ap bss-table` run ON THE
GATEWAY are not success tests.**  `[proven]` AOS 10 gateways do not manage APs;
these AOS 8 constructs read `Num APs: 0` on a healthy gateway carrying a live
tunnelled client. (`show ap bss-table` run **on the AP** remains the right
check that a WLAN change landed.)

### Step 10 — Verify a real client (the only real proof)

**Tool:** `central_show_commands(..., device_type="aps", commands="show ap bss-table,show ap association")` then `central_show_commands(..., device_type="gateways", commands="show user-table,show datapath station table")`
**Why:** Every tunnel datapath counter reads empty when nothing is associated,
and empty looks identical to broken. Config correct at every layer proves only
that it should work.
**Expected result:**
```
show user-table
IP <ip>  MAC <client-mac>  Name <user>  Role <role>  Auth 802.1x
Essid/Bssid <ssid>/<ap-mac>  Profile <ssid>_<digits>_  Forward mode: dtunnel
User Entries: 1/1
show datapath station table   -> <client-mac>  TunId <id>  VLAN <n>
RADIUS statistics             -> Raw Rq >0, Chal >0, Acc >=1, Bad Auth 0
```
`dtunnel` = the client is tunnelled. A client that gets service but never
appears here is being bridged at the AP.
**If anomaly:**
- `User Entries: 0/0` and `show ap association` empty on every SSID = an idle
  network, not a fault. Get a client associated before reading further.
- **Client VLAN:** `show datapath station table` reports the association/VAP
  VLAN, not the derived one. Use `show aaa debug vlan user mac <mac>`:
  ```
  VLAN types present for this User
    Default VLAN                     : 1
    Dot1x Server Rule Role Contained : <vlan>
  Current VLAN : <vlan> (Dot1x Server Rule Role Contained)
  ```
  The source string names the winner (`Dot1x Server Rule Role Contained`,
  `Dot1x Aruba VSA`, `Default VLAN`, …).
- **Clean re-test:** a gateway user entry survives disconnect. Before re-testing
  a role: `aaa user delete mac <client-mac>` (exec; works on an ACP-locked
  gateway), then `show user-table | include <mac>` must return nothing.
- **Probe RADIUS without a client:** `aaa test-server pap <server-name> <user> <deliberately-wrong-credential>`.
  AOS prints `Authentication failed` for both reject and timeout — read counters
  (`show aaa authentication-server radius statistics`). `Rej` incrementing with
  `Bad Auth 0` / `Mismatch Rsp 0` = PASS (transport, shared key, NAS client, and
  source IP all correct). `Tmout` = wrong shared key, undefined NAS client, or
  unreachable. Ignore the first request's ~5000 ms latency on a new server
  (cold socket); read `ExpAuthTm`, not cumulative `AvgRspTm`.

## Verify every write on the device

An API `SUCC_001` / HTTP 200 means Central accepted the object, not that the
device rendered it.

- After a WLAN change: `show ap bss-table` on the AP — the BSS should drop and
  return and the `tot-t` uptime should reset. Continuous uptime = the change
  never landed.
- After a gateway change: `show switches` (Config ID advances, `UPDATE
  SUCCESSFUL`) and `show configuration failure` (Total Failures 0, or the newest
  entry predates the current Config ID).
- Use **CLI Viewer > Candidate Config** at device scope to see the CLI Central
  intends to push and diff it against the running config.
- **Write to the scope where the object is assigned.** Updating the library copy
  does nothing if a scoped copy serves the device. Find it in the profile list's
  *Assigned Device Scope* column or the *References* tab — never infer
  assignment from a scoped GET (it returns the effective view at any scope_id).
- **A Config ID that advances is not proof your intent applied.** A write that
  duplicates the existing object byte-for-byte advances Config ID with nothing to
  push. Give every write a real, visible difference.
- **Canary field** — to tell "never pushed" from "pushed but the platform ignores
  the field": add a second, independently observable field to the same object
  (a timeout, description or banner — never anything that changes forwarding or
  security posture). Example `[proven]`: a `local-management` profile with
  `"mgmt-auth-uname-pwd": true` plus `"login-session-timeout": 22`;
  `show running-config | include loginsession` showed the 22 (object landed),
  while `ssh mgmt-auth` was unchanged (field inert on MOBILITY_GW).
- **The config model accepting a field is not evidence the platform implements
  it for that device function.** Seen inert on MOBILITY_GW: `mgmt-auth-public-key`
  / `mgmt-auth-uname-pwd` on `local-management`; `authorized-key` on
  `management-users` (reads back, produces no config generation, never reaches
  the device).

### PATCH merges, PUT replaces  `[proven]`

```
PATCH {object without the field} -> field / list entries SURVIVE   (merge)
PUT   {object without the field} -> field REMOVED                  (full replace)
```
Verified on `management-users`, `wlan-ssids`, `server-groups`. For WLANs,
`central_manage_wlan_profile(action_type="update", replace_existing=True)`
issues the PUT. For other objects, where the manage tool only PATCHes, the PUT is
`PUT /network-config/v1alpha1/<object-type>/<name>` with the same
addressing parameters. Round-trip safely: GET the full object, save it, PUT it
back with only the intended difference, GET again and diff every field.
Removal can need a **second push cycle** — the device may render the old value at
the current Config ID and clear it on the next generation.

### Scoped GET vs PATCH addressing on `wlan-ssids`  `[proven]`

| Op | Correct | Wrong parameter does |
|---|---|---|
| GET `/network-config/v1alpha1/wlan-ssids/<ssid>` | `view_type=LOCAL` + `scope_id` + `device_function` | `object_type` -> 200 with the **library** object — SILENT |
| PATCH | `object_type=LOCAL` + `scope_id` + `persona` | `view_type` -> 400 "ssid doesn't exist" — LOUD |

The silent case hands you a plausible baseline of the wrong object (observed
`WPA2_PERSONAL` returned for an override that was `WPA3_SAE`). Read a scoped
override with `central_get_wlan_profiles(ssid=..., view_type="LOCAL", scope_id=..., device_function=...)`.

## Reset Config (Classic Central local override) — device-config rebuild

**When it is the remedy** `[doc-grounded]`: when New Central "cannot" change the
gateway's uplink or System IP, look for a Classic Central **local override**. The
onboarding doc names its removal as a required step: *"Onboarding gateways
requires an additional step of clicking Reset Config in the Configuration Audit
> Local Overrides page in Classic Central WebUI."* Path: Classic Central toggle >
Devices > Gateways > the device > Device > Config Audit > *Manage local
overrides* > select the row > **Reset config**. The override typically holds
`controller-ip loopback`, `interface loopback <ip>`, `vlan 4094`,
`switchport access vlan 4094`, `hostname`, `country`, `mgmt-server`,
cp-bandwidth-contracts. Do not author configuration in Classic; use it only for
this removal.

It is also the fix for an **SSH `mgmt-auth` lockout** `[proven]`: the
`local-management` fields are inert (above), the default `default_GW_profile`
cannot be edited, the `ssh mgmt-auth` lines are absent from flash and from the
override and survive a power cycle, and SSH negotiates
`publickey,keyboard-interactive` so a password attempt is refused with
`Permission denied`. After Reset Config the device rebuilt with
`Mgmt User Authentication Method  username/password public-key`. Console does
not help — vendor doc: *"Any other tasks such as configuration, management, or
device upgrade for a Gateway can be performed only from the Aruba Central UI."*
Ask "did this ever work, and what changed?" — the trigger is almost always a
site move, group move, or cluster rebuild, where the model is right and the
device has drifted.

**Costs — weigh before using:**
- It **wipes every device-scope object** and reloads the device. Checking that
  the Step 4 prerequisites exist proves nothing if they are device-scope — the
  reset deletes them. Gate: before any action that wipes a scope, verify which
  prerequisites live at a scope the action will NOT touch (Global / site
  collection / site / group survive; device scope dies), and plan to rebuild the
  rest. In the UI, "Inherits From: Self" = device scope = dies.
- A factory erase regenerates the gateway's **field certificates**. Certificates
  are not config, not in any fingerprint, and not restorable by re-pushing
  (`cpsec: check_local_cert -> Invalid cluster role: 1`). Do **not** use those log
  lines to diagnose a RADIUS/NAC fault — see the RADSec counter rule below.
- Every anchored tunnel drops and re-anchors.

**Capture before you reset** (store the baseline somewhere durable):
```
show switches                 show controller-ip           show ip interface brief
show ip route                 show vlan                    show ip domain-name
show mgmt-user                show lc-cluster group-membership
show ap database              show rights <ROLE>           show datapath tunnel
```
`show vlan` is the one people skip and then need — it records which physical
ports belong to which VLAN. Confirm the device can reach Central over DHCP on the
same switch port after it boots blank.

**State you will find afterwards** `[proven]`:
```
show controller-ip        -> <loopback-ip>, configured to be LOOPBACK interface
show ip interface brief   -> vlan 4094 <uplink-ip> up/up (DHCP); vlan 1 unassigned up/DOWN; loopback <loopback-ip>
show vlan                 -> 1: GE0/0/1-0/3     4094: GE0/0/0
show switches             -> Config ID 0, UPDATE REQUIRED
device-scope assignments  -> EMPTY
```
The device reverts to the auto-import posture — the Fact 1 and Step 5 faults,
re-created by the recovery action itself. Rebuild in Step 4 order: uplink trunk
first, then VLAN static IP, then Gateway System profile, then remove the leftover
Loopback Profile and VLAN 4094 device-scope objects; the cluster re-forms on its
own.

**Verify the end state:** `show controller-ip` (vlan interface), `show ip
interface brief` (VLAN holds the address), `show switches` (`UPDATE SUCCESSFUL`,
non-zero Config ID), `show lc-cluster group-membership` (self = system IP),
`show log system <n>` (no `profmgr` App error lines for the new generation —
`CONFIG FAILURE(<id>)` names the generation; profmgr gives the reason).

**Do not use Reset Config:** to remove one line (it is a whole-device rebuild —
read the override diff first); at a customer site before doing it on a device you
have rebuilt before; without console/physical access or a confirmed DHCP
recovery path; while APs are anchored unless the outage is planned.

**Gateway config is not persisted to flash.**  `[proven]` `show configuration`
reads `# Factory default config` on a fully working gateway; the running config
is re-pulled from Central on every boot. You cannot pre-stage a new system IP and
then relocate the hardware — relocation requires DHCP + internet reachability on
the new port at first plug-in. If the gateway loses its path to Central and the
CLI is ACP-locked, a power cycle may recover it; otherwise factory reset from the
LCD or console. Both need hands on the box.

## Troubleshooting reference by symptom

**Persistent CONFIG FAILURE across many generations on the same error.**
`[proven]` A gateway rejected seventeen consecutive generations on the spurious
`Unknown access-list` attach; a **hard power-cycle cleared it in under two
minutes** (back at the same Config ID with `UPDATE SUCCESSFUL` and more config
than the stuck state). Before engineering around it: (1) capture a baseline —
running-config size, `ip access-list session` count, `user-role` count, VLAN IPs,
`controller-ip`, `show switches`, `show rights <ROLE>`, `show user-table`,
`show datapath tunnel`, `show configuration`; (2) confirm the recovery path
(DHCP/ZTP to Central, hands for console or LCD reset); (3) power-cycle and diff.
Do it in a lab first, never first at a customer site.

**Tunnel SSID flaps (~1 Hz appear/vanish).** A tunnel WLAN carries
`out-of-service: TUNNEL_DOWN`; when the tunnel cannot serve the SSID's VLAN the
AP pulls the VAP and retries. Find why the tunnel cannot carry that VLAN (Step 5).
Distinguish from a client problem with `show ap bss-table` on the AP: large,
unbroken `tot-t` = the SSID never went down.

**Additional client VLANs on the shared tunnel.** One GRE tunnel carries many
802.1Q-tagged client VLANs `[doc-grounded]`: *"Each tunneled client is … assigned
to a VLAN, which is present on all the gateways within the primary cluster."*
`gre0` reading `VLANs 1` is not a limit — it reads that while a second client VLAN
forwards correctly. Two dead ends: the AP `show vlan` "Vlan Mapping Table" is the
**named-VLAN** table (empty by design without Named VLANs); the cluster VLAN probe
(etype `0x88b5`) is peer-gateway detection, empty on a single node. The "VLANs …
are learned by the APs and tagged in the GRE tunnels" wording is from the **Mixed**
forwarding page — do not carry it onto tunnel mode.

**Overlay SSID on the AP's underlay VLAN.**  `[proven]`, bounded:

| SSID | VLAN source | VLAN | Result |
|---|---|---|---|
| Open + cloud-NAC portal | VAP-derived | underlay (VLAN 1) | FAILS — `Underlay VLAN on overlay SSID` |
| Open + cloud-NAC portal | VAP-derived | dedicated client VLAN | works |
| 802.1X | role/RADIUS-assigned | underlay (VLAN 1) | WORKS — `dtunnel` confirmed |

Instrument, **on the AP**: `show ap debug vlan` ("VLAN Assignment Failure
Table") — reason string names `derive_vlan_from_vp`. Hypothesis, NOT
established: the VAP-derived and RADIUS-derived paths are validated differently
against the underlay VLAN. Practical rule: give tunnelled SSIDs their own client
VLAN; do not tell anyone an 802.1X SSID is broken because it sits on the underlay.

**A site move silently orphans site-LOCAL WLAN overrides.**  `[proven]` The AP
falls back to the parent definition; Central still shows the override. Signature:
Central says one security type, the air says another (confirm with a client scan,
e.g. `nmcli dev wifi list`). Classify with `origin_scope_name` (Step 2), then
delete the orphan or recreate it at the scope that now serves the APs. The same
event class (site/group move, cluster rebuild) causes the `mgmt-auth` drift above.

**Guest portal "Login error".** First, from the **associated client**:
```
curl -s -o /dev/null -w '%{http_code}\n' https://<portal-fqdn>   # 000 = client never reached the portal; stop here
curl -i http://<any-off-net-ip>/                                 # the gateway's live 302 = the real capture URL
ip neigh <client-gateway>                                        # L2 sanity
```
Two traps that look like a server fault: a guest subnet moved to new addressing
needs a **return route** (and NAT awareness) on the site edge — interception works
but the portal is unreachable; and a **saved capture URL is stale state** —
re-derive it from the live 302 and diff its portal id against the profile.

**RADSec / NAC counters.**  `[proven]`
`Raw Rq 3  Rej 3  Tmout 0  AvgRspTm 150ms` — `Tmout 0` with a measured response
time means the server **answered**; an Access-Reject cannot arrive over RADSec
unless TLS established, which requires the device certificate to have been
accepted. A certificate/trust failure presents as timeouts or a TLS error, never
as answered rejects. And guest MAC-auth rejects are **designed**: NAC rejects the
unknown MAC, the client lands in the pre-auth role, the portal runs. `CoA Req 0`
is expected until a portal login succeeds. A client in
`sys_cnac_<...>-guest-auth` with `dtunnel` and a portal presented is healthy.
Establish what a counter reads in the healthy state before building a root cause
on it.

**Central NAC captive portal cannot be detached** by setting Captive Portal Type
= None — the `sys_cnac_*` profile is system-generated and the update fails:
`Delete for unexpected req_xpath="/aruba-aaa-captive-portal:captive-portal/profile[name='<sys_cnac_profile>']"`.
The "unsaved data" dialog on exit is the tell that nothing was written.

**Guest captive portal options in AOS 10**  `[doc-grounded]`:
- The AP is the authenticator; the gateway is an authentication **proxy**.
  Interception/redirect happens at the AP even on a tunnelled SSID.
- Only two splash page profiles: **External Captive Portal** and **Cloud Guest**.
  No on-prem AP- or gateway-hosted portal on campus. The `securelogin.hpe.com`
  cert terminates the intercepted TLS session; it does not serve portal content.
- The gateway `show aaa authentication captive-portal` profile is the **Branch
  Gateway** (SD-Branch) path, not campus tunnel-mode WLAN.
- New Central WLAN security levels are Enterprise, Personal, Open — no
  "Visitors" level (that is Classic). Guest portal on New Central = Central NAC
  or External.
- A Central-NAC SSID cannot be localised at any scope:
  `For LOCAL SSID, Can not use Central NAC server as the server group.` A per-site
  guest VLAN must then exist on the wired side, or the portal must be External.

**WPA3-Enterprise and 6 GHz on a tunnel SSID**  `[doc-grounded]`:
- 6 GHz forbids WPA2 and mandates PMF.
- Valid enterprise opmodes: `WPA3_ENTERPRISE_CCM_128` (widest compatibility) and
  `WPA3_ENTERPRISE_GCM_256` (transition not allowed). Transition is a separate
  boolean (`"wpa3-transition-mode-enable": true`), not an opmode.
- **Version floor:** transition mode is supported from **AOS 8.11 and 10.5**. On
  8.10 / 10.4, *"Transition mode configuration has no effect … AKM:5 is not
  advertised with CCM 128"* — every client connects as WPA2 and nothing errors.
  Check AP firmware before claiming a WPA3 result; converted AOS 10 APs have been
  seen landing on 10.4.
- On 6 GHz, CCM 128 is automatically WPA3-only — one SSID with `BAND_ALL` and
  transition enabled is correct on every band; no separate 6 GHz SSID needed.
- Vendor guidance: consider disabling transition mode; consider separate VAPs for
  WPA3 and WPA2 Enterprise; prefer EAP-TLS. Adding 6 GHz later: upgrade first
  (8.11.2.1+ / 10.5+), switch to CCM 128 with transition disabled, then enable
  6 GHz.

**Renaming a gateway**  `[doc-grounded]`: the hostname lives in the **System
Information profile** (`sys-system-info-profile` at the device scope). The
vendor *Rename Hostnames* workflow is keyed on serial numbers, not device type —
it applies to gateways (the `central_manage_system_info` description mentions
APs). UI: Devices scope > gateway > System > System Information > edit hostname.
Because `central_get_system_info` reads empty (Step 2), you cannot baseline or
read back through it — verify on `central_get_devices(serial_number=...)` and the
scope tree, and do not treat an unreadable object as permission to write it blind.

**Inherited handoff notes** are claims to verify, not facts. Real examples that
were wrong: "the gateway has no VLAN 1", "no ISAKMP SA means the AP isn't forming
IPsec", "the scratch SSID was removed". Re-verify on the device, and validate that
the success criterion itself indicates what you want (see Step 9).

## Decision matrix

| Condition | Action |
|---|---|
| `show controller-ip` says loopback | Fact 1. Build Step 4 items, then Reset Config to remove the local override; rebuild in order |
| Tunnel healthy, no client anchors, RADIUS sourced from AP | Fact 2. Read `overlay-wlan`; delete/recreate per Step 7 |
| SSID flaps ~1 Hz | Step 5 three-way check (MOBILITY_GW assignment, enable flag, trunk uplink) |
| SSID vanished after an `overlay-wlan` edit | Check `cluster-scope-id` = site scope id of a working sibling |
| `(Conductor Unreachable)` | Reachability split table (Step 4) — DNS / default route / uplink |
| `CONFIG FAILURE(n)` with Config ID > n | Latest push succeeded; read newest failure only |
| Rollback, Total Failures 0 | Commit-confirm timeout; read errorlog, not the config |
| Same error across many generations | Baseline, confirm recovery path, power-cycle, diff |
| `Unknown access-list '<policy>'` | Check `show rights <ROLE>` for `sys_policy_<ROLE>` before acting |
| Role exists in Central, client lands in default role | Verify assignment at the gateway's scope and that something references the role |
| Central read returns empty | Corroborate with `central_get_scope_tree` before concluding absence |
| `mgmt-auth` lockout after a site/group move | Reset Config (weigh costs); console will not help |
| Portal "Login error" | `curl` from the associated client first |
| Answered rejects with `Tmout 0` | Transport/cert fine; look at policy, not trust |
| WPA3 clients connect as WPA2 | Check AP firmware vs the 10.5 floor |

## Output formatting

Report in this order:
1. **Verdict** — one line: healthy / which fault signature matched.
2. **Evidence table** — `| Check | Command/tool | Expected | Observed | Pass |`
   for each device-side check run (Steps 4, 6, 9, 10). Quote the observed line,
   not a paraphrase.
3. **Scope findings** — which reachability items are device-scope (will die on
   Reset Config) vs inherited.
4. **Proposed changes** — in build order, each with the tool call, the baseline
   captured, and the device-side read that will verify it. Mark any step relying
   on an `[observed-once]` claim.
5. **Not verified** — anything concluded from a Central read without device
   corroboration, labelled as such.

Use placeholders for serials, IPs and scope ids in anything shared outside the
operator's own session.

## Example

> "My tunnel-mode SSID broadcasts but no client ever gets an address, and ClearPass sees the requests coming from the AP"
> "The AOS 10 gateway's system IP is a loopback and New Central won't let me change it"
> "Build a new Mobility Gateway cluster and a tunnelled 802.1X SSID in Central"
