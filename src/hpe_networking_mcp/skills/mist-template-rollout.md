---
name: mist-template-rollout
title: Juniper Mist template rollout — golden object, lint, inert deploy, render gate, verify
description: |
  TRIGGERS — call this before creating or changing any Juniper Mist
  template or template-driven object: WLAN templates and WLANs, RF
  templates, switch / network templates, site templates, site variables,
  or switch device-level config. Also call it when a Mist config write
  "succeeded" but never took effect, or when a template / switch page in
  the Mist UI crashes or shows "unexpected error" after an API write.
  Match phrases: "deploy a Mist template", "push WLAN template", "create
  switch template", "set site variables", "Mist template page crashed",
  "Cannot convert undefined or null to object", "dynamic_vlan",
  "coa_servers", "config_revert_timer", "variables not resolving".
  Ordered path: golden object → lint → inert deploy → render gate →
  verify against the consuming object → activate site-by-site.
platforms: [mist]
tags: [mist, templates, wlan, switch, rf, site-variables, deployment, change-management, render-gate]
tools: [health, mist_get_self, mist_list_org_templates, mist_get_org_template, mist_create_org_template, mist_update_org_template, mist_clone_org_template, mist_delete_org_template, mist_list_org_wlans, mist_get_org_wlan, mist_create_org_wlan, mist_update_org_wlan, mist_delete_org_wlan, mist_list_org_rf_templates, mist_get_org_rf_template, mist_update_org_rf_template, mist_list_org_network_templates, mist_get_org_network_template, mist_update_org_network_template, mist_list_org_sites, mist_get_site_info, mist_update_site_info, mist_get_site_setting, mist_update_site_settings, mist_get_site_setting_derived, mist_list_site_wlans_derived, mist_get_site_device, mist_update_site_device, mist_get_site_device_config_cmd, mist_search_org_alarms, mist_list_org_audit_logs, mist_get_tool_schema]
---

# Juniper Mist template rollout — golden object, lint, inert deploy, render gate, verify

## Objective

The ordered, safe path for creating or changing a Mist template. It
prevents two failure classes:

- **(a) Silent no-op** — the API returns 200 and echoes your fields, but a
  field sits on the wrong object or has the wrong name, so the platform
  ignores it. Reading back the same field you wrote looks fine (false
  positive); the defect surfaces at bring-up.
- **(b) UI-render crash** — a schema-valid payload omits a sub-object the
  Mist UI assumes exists, so the template / switch page crashes and the
  operator cannot see or edit it.

Run `change-pre-check` before step 4 and `change-post-check` after step 7.
For a read-only audit of what already exists, use `mist-scope-audit`
instead.

## Prerequisites

- `health(platform="mist")` ok; `ENABLE_MIST_WRITE_TOOLS` set for writes.
- **Org addressed by `org_id`** resolved from `mist_get_self()`, never by
  name. Read-only until the operator approves writes to this org.
- Secrets (RADIUS shared secrets, passphrases, SNMPv3 / routing keys, claim
  codes) supplied out-of-band; verify presence, never echo values.
- A browser automation tool (or a human) available for the render gate in
  Step 5 — there is no API substitute for it.

## Procedure

### Step 1 — Build from a golden object, never sparse hand-written JSON

**Tools:** `mist_get_org_template` / `mist_get_org_wlan` /
`mist_get_org_rf_template` / `mist_get_org_network_template` on an object
created in the Mist UI (or a known-good template; `mist_clone_org_template`
clones a WLAN template within the org).
**Why:** UI-render crashes come from minimal payloads. A UI-made object
carries every sub-structure the UI renders (`dynamic_vlan.vlans`,
ratesets, portal bodies, `port_usages`, `networks`).
**Expected result:** a complete payload; swap concrete per-site values for
`{{variables}}` only in fields that support them (see Step 2).
**If anomaly:** confirm the field set with
`mist_get_tool_schema(name=...)` for the matching create tool (e.g.
`mist_create_org_wlan`) — its
`payload_schema` lists real field names and enums. Mist adds fields over
releases; the live object / schema wins over any skeleton.

### Step 2 — Pre-deploy lint (catch what schemas can't)

Validate every payload against the Mist OpenAPI (unknown and
**deprecated** fields) and against these flag-implies-sibling rules. Fix
every error before writing.

| If … | Require … | Else |
|---|---|---|
| `wlan.dynamic_vlan.enabled` | non-empty `dynamic_vlan.vlans` **or** `default_vlan_ids` | UI `Object.keys(undefined)` → template page crash |
| `wlan.dynamic_psk.enabled` | `wlan.auth_servers` | dynamic PSK is RADIUS-sourced → invalid |
| `wlan.auth.type == eap` | `wlan.auth_servers` | 802.1X with no RADIUS server |
| `wlan.portal.enabled` | a portal body | empty portal editor faults |
| any field | not `deprecated` in OpenAPI | UI may read only the successor field |
| switch `networks.<name>` | a `vlan_id` (required in the schema) | accepted by the API, then **switch/template page crash** |
| any config section | never set to `null` | Mist stores the null and the page crashes; omit or send the full object instead |

Field gotchas confirmed in the field:
- `coa_servers[]` uses **`ip`**; `auth_servers[]` / `acct_servers[]` use
  **`host`**. The wrong key leaves CoA silently non-functional.
- Site **variables** live on the **Site Setting** object
  (`/sites/{id}/setting` → `vars`), **not** the Site object. The Site
  object accepts them silently and the UI shows zero variables.
- `dynamic_vlan.default_vlan_id` is deprecated → use `default_vlan_ids`
  (array).
- Maps (`vars`, `port_usages`, `networks`) validate on their **values**,
  not their arbitrary keys.
- Site variables substitute only in fields the UI marks with a **VAR**
  indicator. The switch template's **Additional CLI Commands** box
  (`additional_config_cmds`) has no VAR indicator: in a lab test a
  `{{var}}` there was pushed to the switch literally and the commit failed
  ("Configuration Error in Additional CLI Commands"). Use native fields for
  variable values, or literal per-site values.
- Device-level `additional_config_cmds` **replace** the template's — they do
  not merge (confirmed from the rendered `config_cmd`).

Switch / network template rules:
- Ports apply through `switch_matching.rules` (with a
  `default_port_usage`); a top-level `port_config` on a template configures
  no ports.
- `switch_port_usage.networks` is trunk-only; a `mode: inet` (routed) port
  must not carry it. Model a routed uplink as a routed port, never as a
  network with a subnet and no `vlan_id`.
- `network_template` has **no L3 addressing fields** (no
  `other_ip_configs`, `dhcpd_config`, `router_id`, `ospf_config`). An L3
  core switch is therefore a documented hybrid: VLANs, port profiles and
  uplink matching in the template; routed-uplink IP / IRB addressing at
  device level. That device override is required — removing it takes the
  uplink down.
- Do not split one OSPF area between native `ospf_areas` and CLI: native
  OSPF attaches by network name and cannot cover a routed-uplink port, and
  two definitions of the same area stop the adjacency forming. Keep that
  area wholly in one place.
- Set `switch_mgmt.config_revert_timer` (integer minutes, default 10) to 5
  or less on every switch template / device. It auto-rolls back a Mist
  push only when the switch **loses cloud connectivity** — it does not
  protect a data-plane failure on a switch that stays cloud-connected via
  out-of-band management, and it does not protect changes typed in the
  device CLI / web shell.
- No full device-level copy of the template: a device should hold only
  genuine per-device values.

Site variables — reconcile before you mint:
- `mist_get_site_setting(site_id=...)` first. If a variable already covers
  the value (**case-insensitive** match), reuse that name; a case-variant
  duplicate is a collision to fix, not a new variable. Never change or
  shadow a variable that existing WLANs already consume.
- Don't write site variables for a template that is not yet bound — they
  only resolve when bound. If you must write them, baseline the Site
  Setting first.

### Step 3 — Baseline

**Tools:** `mist_search_org_alarms(org_id=..., duration="1d")`,
`mist_list_org_audit_logs(org_id=..., duration="1d")`, and a GET of every
object you will change (or `change-pre-check`).
**Why:** alarm delta and revert source.
**Expected result:** saved JSON for each object.

### Step 4 — Deploy inert

**Tools:** `mist_create_org_template` / `mist_create_org_wlan` /
`mist_update_org_rf_template` / `mist_update_org_network_template` /
`mist_update_site_settings` (bodies nested under `body`).
**Why:** nothing reaches a device until activation.
**Rules:** new WLANs `enabled: false`; templates unbound (no `applies`, no
site binding). Record every created object (name + id) in a revert
manifest. A PUT replaces whole nested objects — send the full nested
object with only the intended key changed (e.g. a site-setting PUT
carrying only one key inside `wifi` drops the rest of `wifi`).
**Expected result:** org alarms 0 → 0 new.
**If anomaly:** revert from the manifest / baseline.

### Step 5 — Render gate

A template is not done until its page renders.
1. List every affected template / switch page URL.
2. Open each in the Mist UI (browser automation), click into the row, and
   read console **errors only**.
3. Clean pass = no `TypeError`, no `Cannot convert undefined or null to
   object`, no "unexpected error". On a hit, the JS stack names the
   renderer and field — fix that field; hard-reload between fixes so cached
   JS does not mask the change.

Navigation note: deep links to switch-template pages can land on a "no
permissions" routing page; reach them through the Organization menu.

### Step 6 — Verify against the consuming object

**Tools:** `mist_get_site_setting` (vars),
`mist_get_site_setting_derived` / `mist_list_site_wlans_derived` (what the
site inherits once bound), `mist_get_site_device_config_cmd` (the Junos a
switch will actually receive), `mist_get_org_wlan` (the WLAN the UI
renders).
**Why:** a write succeeding proves nothing; read the object the platform
consumes, not the field you just wrote. Do not prove inheritance by
diffing a device GET against your template — the device GET returns a
merged view and templates can hold fields Mist accepts but never renders.
**Expected result:** consumer shows the intended values.
**If anomaly:** hardware-only behaviour (variable substitution on a live
device, LACP / STP / native VLAN) is **deferred to bring-up** — flag it,
don't mark it done.

### Step 7 — Activate site-by-site (approval required)

**Tools:** bind via the template's `applies` (`mist_update_org_template`),
the site's template references (`mist_update_site_info`), or enable WLANs
(`mist_update_org_wlan`).
**Why:** blast radius of one site.
**Rules:** maintenance window; revert manifest ready; one site at a time;
re-run the render gate and the alarm check after each. For switch
data-plane changes (routing, routed uplinks, IRBs) verify the data plane
directly (interface up with IP, routing neighbours) — the revert timer may
not fire.

## Decision matrix

| Condition | Action |
|---|---|
| Payload hand-written from scratch | Stop — rebuild from a GET of a UI-made object |
| Lint error (flag without sibling, deprecated / unknown field, network without `vlan_id`, `null` section) | Fix before any write |
| Variable needed in Additional CLI Commands | Use a native VAR-capable field or a literal value |
| Template not yet bound | Don't write site variables |
| Render gate shows a console error | Fix the named field; do not activate |
| Write returned 200 but behaviour unchanged | Read the consuming object (Site Setting, derived view, `config_cmd`) — field is likely on the wrong object or misnamed |
| Switch managed out-of-band and change is data-plane | Verify data plane directly; be ready to revert manually |
| Mist `unavailable` | Stop |

## Output formatting

```
## Mist template rollout — <org_id> / <template or object>
**Stage:** lint | inert deploy | render gate | verify | activate site <name>

### Pre-flight checklist
- [ ] Built from a UI-golden / cloned object
- [ ] Lint: 0 errors (siblings, deprecated, vlan_id, no nulls)
- [ ] coa_servers.ip / Site-Setting vars / default_vlan_ids checked
- [ ] Site variables reconciled (reuse / collision / new)
- [ ] Deployed inert; alarms <before> → <after>; revert manifest written
- [ ] Render gate clean on every affected page
- [ ] Verified on the consuming object; hardware items deferred: <list>
- [ ] Secrets out-of-band (presence only)
- [ ] Activation approved; site-by-site; revert ready

### Revert manifest
| Kind | Name | id | Action to revert |
|---|---|---|---|
```

## Example

> "push this new guest WLAN template to the Mist org"
> "I created a switch template via the API and now the page crashes"
> "my site variables don't show up in the Mist UI"
