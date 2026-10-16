---
name: mist-clearpass-guest-coa
title: Mist + ClearPass guest onboarding CoA — design, deploy and wire-validate
description: |
  TRIGGERS — call this when the user asks to design, deploy, audit or
  troubleshoot guest captive-portal onboarding on Juniper Mist APs with
  Aruba ClearPass as the RADIUS / policy engine, and specifically the
  Change of Authorization (CoA) that moves a guest from the pre-auth
  portal role to the post-registration role. Match phrases: "guest CoA",
  "ClearPass never sends the CoA", "nothing on udp/3799", "guest stuck in
  captive portal role after login", "Disconnect-Request", "Terminate
  Session", "Reauthenticate-Session", "vendor does not support action
  Reauthenticate-Session", "Mist guest WLAN with ClearPass", "Dynamic
  Authorization", "coa_servers". Uses the Juniper-native Disconnect
  (`[Juniper Terminate Session]`, NAD Vendor = Juniper) as the default
  design, with the Cisco-dialect reauthenticate as a documented
  alternative.
platforms: [mist, clearpass]
tags: [mist, clearpass, nac, guest, coa, captive-portal, radius, dynamic-authorization, change-management]
tools: [health, mist_get_self, mist_list_org_wlans, mist_get_org_wlan, mist_update_org_wlan, mist_list_org_templates, mist_get_site_setting, mist_search_org_alarms, mist_get_tool_schema, clearpass_get_network_devices, clearpass_manage_network_device, clearpass_get_services, clearpass_get_enforcement_policies, clearpass_manage_enforcement_policy, clearpass_get_enforcement_profiles, clearpass_manage_enforcement_profile, clearpass_get_radius_dynamic_authorization_template, clearpass_get_radius_dictionaries, clearpass_get_sessions, clearpass_get_system_events, clearpass_disconnect_session]
---

# Mist + ClearPass guest onboarding CoA — design, deploy and wire-validate

## Objective

Make guest self-registration on a ClearPass captive portal actually move
the guest on a Juniper Mist AP from the **pre-auth (redirect) role** to the
**post-registration (full-access) role**, and prove it on the wire.

The role change needs a RADIUS **Change of Authorization** (RFC 5176) from
ClearPass to the AP on **udp/3799**. The design decision this skill
encodes:

- ClearPass builds CoA actions **per NAD vendor**. Its built-in
  **Reauthenticate-Session** CoA template exists only for **Cisco** and
  **Tellabs**. Juniper, Aruba and HPE vendor entries ship only
  **Terminate-Session (Disconnect)** and **Bounce-Port**.
- **Default design (Option B): NAD Vendor = Juniper +
  `[Juniper Terminate Session]`.** ClearPass sends a **Disconnect-Request
  (RADIUS code 40)**; the client briefly re-associates and re-authenticates
  into the post-registration role. Vendor-honest, supported by every Mist
  AP. Trade-off: a short re-associate, which is acceptable for a one-time
  guest role change.
- **Alternative (Option A): NAD Vendor = Cisco + a reauthenticate
  profile.** Seamless in-place re-auth (CoA-Request, code 43), because
  Mist emulates Cisco-style CoA. It requires registering the Mist AP under
  a Cisco vendor profile — the Vendor field selects the CoA *dialect*, not
  a hardware claim. Use only if a strictly seamless transition is required
  and the operator accepts the Cisco label.

Both options have been observed working on the wire in a lab: Option B
produced a Disconnect-Request (code 40) on udp/3799 after a real guest
portal login; Option A produced a CoA-Request (code 43). With the
reauthenticate action and the NAD set to Juniper or Aruba, ClearPass logs
*"vendor does not support action Reauthenticate-Session"* and sends
**nothing**.

This skill is **change-making on two platforms**. Run `change-pre-check`
first and `change-post-check` afterwards; the Mist WLAN edit follows
`mist-template-rollout`.

## Prerequisites

- Mist and ClearPass reachable — `health(platform=["mist", "clearpass"])`.
- Operator has named the **Mist org_id** (resolve via `mist_get_self()`,
  never by org name — two orgs can share a name), the **guest WLAN**
  (`wlan_id` or its template), and the **ClearPass guest WEBAUTH service /
  enforcement policy**.
- For writes: `ENABLE_MIST_WRITE_TOOLS` and `ENABLE_CLEARPASS_WRITE_TOOLS`
  set, **and** explicit operator approval for this change on this tenant.
  Read-only until approved.
- The RADIUS shared secret is supplied **out-of-band** and must be
  identical on the Mist WLAN (auth, acct and CoA entries) and the ClearPass
  Network Device. Verify presence, never echo the value.
- A way to observe udp/3799 at the NAS (packet capture on a mirrored port,
  or a test NAS / listener in a lab). Without it you cannot meet the
  acceptance criterion in Step 9.

## Procedure

### Step 1 — Baseline both platforms

**Tool:** run the `change-pre-check` skill scoped to the guest WLAN and the
ClearPass enforcement policy; additionally capture
`mist_search_org_alarms(org_id=..., duration="1d")` and
`clearpass_get_system_events(limit=50)`.
**Why:** the before-state is the revert path for both platforms.
**Expected result:** snapshot containing the WLAN JSON, the ClearPass
Network Device record(s), the guest enforcement policy and its profiles.
**If anomaly:** do not proceed without a saved baseline.

### Step 2 — Read the Mist guest WLAN

**Tool:** `mist_list_org_wlans(org_id=...)` to find it, then
`mist_get_org_wlan(org_id=..., wlan_id=...)`. If it lives in a WLAN
template, `mist_list_org_templates(org_id=...)` to see where it applies.
**Why:** confirm RADIUS auth (udp/1812), acct (udp/1813) and the CoA
server entry.
**Expected result:**
- `auth_servers[]` / `acct_servers[]` point at ClearPass using the `host`
  key, ideally via a site variable (e.g. `{{auth_srv1}}`), not a literal.
  Variables live on the **Site Setting** object — check them with
  `mist_get_site_setting(site_id=...)` → `vars`, not the Site object.
- `coa_servers[]` contains a ClearPass entry with **`ip`** (not `host` —
  CoA servers use `ip`, auth/acct servers use `host`; the wrong key leaves
  CoA silently non-functional), `port: 3799`, `enabled: true`, and the
  shared secret present.
**If anomaly:** missing or mis-keyed `coa_servers` = the AP will not
accept the CoA. Fix in Step 6. Confirm the exact `coa_servers` shape with
`mist_get_tool_schema(name="mist_update_org_wlan")` before writing — the
OpenAPI declares `coa_servers[].ip` as an IPv4 field, so whether a site
variable is accepted there is **unverified**; check the schema / a lint
before using one.

### Step 3 — Read the ClearPass Network Device for the APs

**Tool:** `clearpass_get_network_devices(name=...)` (or `filter=` on the
NAS IP).
**Why:** ClearPass picks the CoA dialect from the device's Vendor.
**Expected result (Option B):** Vendor = **Juniper**, CoA capable =
true, CoA port = **3799**, RADIUS shared secret present.
**If anomaly:** Vendor mismatched to the chosen option (see Decision
matrix) is the second most common cause of "no CoA sent".

### Step 4 — Read the guest enforcement policy and its profiles

**Tools:** `clearpass_get_services(name=...)` for the WEBAUTH service →
`clearpass_get_enforcement_policies(policy_id=...)` →
`clearpass_get_enforcement_profiles(name="[Juniper Terminate Session]")`.
Optionally `clearpass_get_radius_dynamic_authorization_template(...)` and
`clearpass_get_radius_dictionaries(...)` to confirm which vendors carry a
reauthenticate vs terminate template on this ClearPass.
**Why:** the most common root cause of "ClearPass never sends the CoA" is
a guest rule that applies **only** a MAC-caching profile and **no CoA
profile** — registration succeeds, the MAC is cached, and nothing is
dispatched on udp/3799.
**Expected result:** the `[Guest]` rule of the WEBAUTH enforcement policy
applies the MAC-caching profile **and** `[Juniper Terminate Session]`
(type `RADIUS_DynAuthZ`) with attributes:

| Attribute type | Name | Value |
|---|---|---|
| Radius:IETF | Calling-Station-Id | `%{Radius:IETF:Calling-Station-Id}` |
| Radius:IETF | Acct-Session-Id | `%{Radius:IETF:Acct-Session-Id}` |

**If anomaly:** rule has no CoA profile → fix in Step 7.

### Step 5 — Platform prerequisites on ClearPass

**Tool:** `clearpass_get_sessions(limit=5)`.
**Why:** the session / CoA REST path depends on **Insight** being enabled
(Administration → Server Manager → Server Configuration). Modern
ClearPass also **silently drops Access-Requests without a RADIUS
Message-Authenticator** (Blast-RADIUS hardening) — never disable it.
**Expected result:** session records returned for active clients.
**If anomaly:** errors or no records while clients are known to be
connected → check Insight before anything else.

### Step 6 — Mist WLAN change (only with approval)

**Tool:** `mist_update_org_wlan(org_id=..., wlan_id=..., body={...})` (or
the WLAN-template equivalent). Follow `mist-template-rollout`: GET the
full object, change only the needed keys, send the full object, lint
before write, render-gate the page after.
**Why:** add or correct the `coa_servers[]` entry and point auth/acct at
ClearPass.
**Expected result:** read-back of the WLAN shows the CoA entry with `ip`,
`port: 3799`, `enabled: true`; org alarms unchanged.
**If anomaly:** revert from the Step 1 baseline.

### Step 7 — ClearPass change (only with approval)

**Tools:**
- `clearpass_manage_network_device(action_type="update", device_id=..., payload={...})`
  — Vendor = Juniper, CoA capable, CoA port 3799.
- `clearpass_manage_enforcement_profile(action_type="create", payload={...})`
  only if `[Juniper Terminate Session]` is missing (it normally ships
  built-in).
- `clearpass_manage_enforcement_policy(action_type="update", policy_id=..., payload={...})`
  — set the `[Guest]` rule's profiles to
  `["<MAC-caching profile>", "[Juniper Terminate Session]"]`.

**Why:** these are the two config gaps behind "CoA never sent".
**Expected result:** read-back shows the rule carrying both profiles.
**If anomaly:** revert = set the rule's profiles back to the baseline
list (and delete any profile you created).

### Step 8 — Ports

Confirm udp/1812–1813 AP → ClearPass and **udp/3799 ClearPass → AP** are
permitted on every firewall / ACL in the path. CoA flows in the
*opposite* direction to authentication and is often blocked when only
auth/acct were opened.

### Step 9 — Validate to the wire (definition of done)

**Method:** drive a **real guest captive-portal registration + Log In**
while capturing udp/3799 at the AP side.
**Expected result:** a **Disconnect-Request (code 40)** from ClearPass on
udp/3799 (code 43 CoA-Request for Option A); the client re-associates and
lands in the post-registration role; the session is visible via
`clearpass_get_sessions(...)`. Then run `change-post-check`.
**If anomaly:** see the Decision matrix. Configuration read-back alone is
**not** acceptance.

Notes from field validation:
- The portal login must reach ClearPass from the client's **real LAN
  source IP** — ClearPass correlates the web login to the MAC-auth session
  by source IP. A NAT'd or tunnelled path (VPN / overlay subnet routing)
  breaks the correlation and no CoA is generated.
- Triggering a disconnect through the API (`clearpass_disconnect_session`)
  against a synthetic / injected session was observed returning *"Error
  disconnecting session"* with no packet sent, regardless of vendor. Use
  the real portal flow as the acceptance trigger, not the API disconnect.
- ClearPass async CoA errors are logged by the async-netd service
  (`cmdctrl.log` in a PolicyManagerLogs dump) — that is where *"vendor does
  not support action ..."* appears.

## Decision matrix

| Observation | Cause | Action |
|---|---|---|
| Guest `[Guest]` rule has only a MAC-caching profile | No CoA action configured | Add `[Juniper Terminate Session]` (Step 7) |
| async-netd: *"vendor does not support action Reauthenticate-Session"*, 0 packets | Reauthenticate profile on a Juniper/Aruba/HPE-vendor NAD | Use Option B (Terminate Session), or set Vendor = Cisco for Option A |
| No packet on 3799, ClearPass shows CoA sent | Firewall/ACL blocking ClearPass → AP udp/3799 | Open udp/3799 in that direction |
| Packet arrives, AP ignores it | WLAN `coa_servers` missing / keyed `host` / disabled / secret mismatch | Fix WLAN CoA entry (Step 6); match secrets |
| Access-Requests silently dropped | Message-Authenticator missing | Keep Message-Authenticator on (both ends) |
| Session/CoA REST calls fail | Insight disabled | Enable Insight |
| CoA log: *"Failed to find finalValue for Calling-Station-Id / NAS-IP"* | Web-auth session not correlated to the MAC-auth session | Check WEBAUTH authorization sources (Endpoints Repository + Time Source) and role mapping per the Juniper Mist ↔ ClearPass guest integration guide; check source-IP path |
| Operator requires zero re-associate | Option B trade-off unacceptable | Option A: Vendor = Cisco + a copy of `[Cisco - Reauthenticate Session]` (Cisco-AVPair `subscriber:command=reauthenticate`, Calling-Station-Id, NAS-IP-Address, Event-Timestamp) on the `[Guest]` rule |
| Mist or ClearPass `unavailable` | — | Stop |

## Output formatting

```
## Guest CoA — <org_id> / <guest WLAN> / <ClearPass policy>
**Design:** Option B (Juniper Terminate Session) | Option A (Cisco-dialect reauth)
**Mode:** read-only audit | change applied (approved)

### Mist WLAN
- auth/acct servers: <host or {{var}}>  ok/✗
- coa_servers: ip=<..> port=3799 enabled=<bool> secret=present|absent  ok/✗

### ClearPass
- Network Device <name>: Vendor=<..> CoA capable=<bool> port=<..>  ok/✗
- [Guest] rule profiles: [<..>, <..>]  ok/✗ (CoA profile present?)
- Insight: enabled/unknown

### Wire validation
- Packet observed on udp/3799: code 40 | code 43 | none
- Client role after login: <post-registration role> | unchanged

### Verdict
WORKING | CONFIG GAP (<which>) | NOT VALIDATED (no capture)

### Revert
- <object> → <baseline value>
```

## Example

> "ClearPass guest login works but the client never leaves the captive-portal role on our Mist APs"
> "set up guest onboarding CoA between Mist and ClearPass"
> "why does ClearPass say vendor does not support action Reauthenticate-Session?"
