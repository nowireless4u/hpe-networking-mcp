---
name: mist-scope-audit
title: Juniper Mist comprehensive configuration scope audit
description: |
  TRIGGERS — call this when the user asks: "Mist config audit", "Mist
  scope audit", "where are my Mist WLAN templates assigned", "is my
  Mist config drifting", "find bare site-level WLANs", "audit Mist
  RF templates", "audit Mist switch templates", "audit Mist port
  profiles", "audit Mist firmware policy", "audit MPSK / Cloud PSK",
  "audit Mist site variables", or anything about Mist's org → site
  group → site → device hierarchy. Walks WLAN templates (with
  per-WLAN setting checks), RF templates (with per-band checks),
  switch configuration templates (org/site/device hierarchy), site
  variables (Mist's alias-equivalent), port profiles (static +
  dynamic), AP-port best practices, virtual chassis, site templates,
  site groups, per-site overrides, device profiles, firmware
  auto-upgrade, and PSK strategy. Anchored on Mist best-practices doc
  + Juniper Mist Wired Assurance Configuration Guide + Juniper Mist
  Wireless Assurance Configuration Guide + Juniper AI-Driven
  Wired & Wireless Network Deployment Guide.
platforms: [mist]
tags: [mist, audit, configuration, scope, drift-detection, vsg]
tools: [health, mist_get_self, mist_get_configuration_objects, mist_get_wlans, mist_get_org_or_site_info, mist_get_org_licenses, mist_list_upgrades, mist_get_site_health, mist_get_constants]
---

# Juniper Mist comprehensive configuration scope audit

## Objective

Walk Mist's configuration hierarchy
(**Org → Site Groups → Sites → Device Profiles → Devices**) and produce a
comprehensive drift report covering WLAN templates, RF templates,
switch configuration templates, site templates, site variables, site
groups, per-site overrides, device profiles, port profiles, firmware
policy, and PSK strategy.

Anchored on:
- **Mist best-practices doc** (`docs/mist/vsg/mist-best-practices.docx`)
- **Mist Wired Assurance Configuration Guide** (Juniper)
- **Mist Wireless Assurance Configuration Guide** (Juniper)
- **Juniper AI-Driven Wired & Wireless Network Deployment Guide**

Each finding is judged against vendor recommendations:

> *"Template everything. Override nothing unless you have to."*

The audit calls out *"Mist recommends X, found at Y"* drift explicitly,
AND checks **per-setting values** within each profile against
recommended defaults.

**Read-only.** Identifies issues; does not correct them. Use the
appropriate `mist_change_org_configuration_objects` /
`mist_change_site_configuration_objects` tools after reviewing.

## Prerequisites

- Mist must be reachable (`health(platform="mist")` first).
- Operator picks an audit scope: **org-wide** (default), a specific
  **site group**, or a specific **site**.
- For orgs with 50+ sites, the per-site WLAN inspection in step 5 is
  N+1 calls — warn the operator and offer site-group scope as the
  cheaper option.

## Procedure — 14 audit checks across ~25 categories with per-setting depth

Run the steps in order. Each step pulls a slice of the catalog and
adds findings to the running report.

### Step 0 — Reachability + org_id

**Tools (in order):**
- `health(platform="mist")` — confirm reachable.
- `mist_get_self(action_type="account_info")` — get `org_id`.

**Why:** every later call needs `org_id`. If the user has access to
multiple orgs, ask which one to audit.

### Step 1 — WLAN templates + assignment scope

**Tool:** `mist_get_configuration_objects(org_id=..., object_type="wlantemplates")`

**Mist best practice:** WLAN templates are assigned at the appropriate scope:
- `applies.org_id` set → org-wide
- `applies.sitegroup_ids` non-empty → site groups (preferred for templates that apply to multiple sites)
- `applies.site_ids` non-empty → individual sites (for genuinely site-specific templates)
- **Never** at the device level
- **Never** create a bare site-level WLAN (a WLAN at a site without going through a template)

**Per-template structural checks (per the best-practices doc §2.2):**

Templates should be organized by function — Mist explicitly recommends separating by audience:

| Template | Purpose / Contents |
|---|---|
| Corporate / Dot1X | 802.1X EAP WLANs for employees; RADIUS auth; WPA3/WPA2 |
| MPSK / IoT | Multi-PSK WLANs for IoT devices, AV equipment, managed endpoints |
| Guest | Captive portal or open WLANs for visitors; isolated VLAN |
| Onboarding | Temporary SSID for device enrollment (Mist NAC / MDM) |

**Drift findings:**
- **REGRESSION — broken applies reference**: template's `applies.site_ids` or `applies.sitegroup_ids` references a deleted site/group.
- **DRIFT — monolithic template**: single template containing 5+ SSIDs spanning multiple functions (e.g., guest + corporate + IoT in one template) — split by function per §2.2.
- **DRIFT — per-site assignment that should be site-group**: template individually assigned to 5+ sites that share a site group — recommend moving to the site-group level.
- **DRIFT — applies has both site and sitegroup**: redundant assignment; pick one.
- **INFO — template count + assignment-scope distribution**: surface in the summary.

### Step 2 — Per-WLAN settings audit (within each template)

For each WLAN inside each template, check Mist's recommended per-SSID settings (best-practices doc §2.5 + Mist Wireless guide):

| Setting | Mist recommendation | Drift signal |
|---|---|---|
| Auth server values | Use template variables (`{{auth_srv1}}`, `{{auth_srv2}}`) | Hardcoded IP address (REGRESSION) |
| VLAN | Always per-SSID; NEVER VLAN 1 for production | VLAN 1 in production WLAN (REGRESSION) |
| PSK source | Cloud PSK / MPSK preferred over static shared PSK | Static shared PSK on personal-WLAN (DRIFT — recommend MPSK) |
| Band Steering | Enable on dual/tri-band SSIDs | Disabled on dual-band SSID (DRIFT) |
| Fast Roaming (11r) | Enable on WPA3/WPA2 enterprise | Disabled on WPA3-Enterprise (DRIFT) |
| 11r without Enterprise | 11r requires WPA2/WPA3 Enterprise | 11r enabled on Personal SSID (REGRESSION — won't work) |
| Bonjour / mDNS | Per-service (AirPlay/AirPrint/Chromecast) scoped to `same_site` or `same_ap` | mDNS scope is `all` (DRIFT) |
| ARP Filter | Enable on high-density / IoT SSIDs | Disabled on IoT (DRIFT) |
| Limit Bcast | Enable on guest SSIDs | Disabled on guest (DRIFT) |
| Hidden SSID | Use only when justified | Hidden + 802.1X (DRIFT — usually wrong combination) |
| Mist NAC | Enable on onboarding SSIDs | Disabled on onboarding (DRIFT) |
| Open SSID | Only with captive portal redirect | Open SSID, no captive portal (REGRESSION) |
| Schedule | Optional — for guest / business-hours-only SSIDs | (INFO — list for review) |

**Per-WLAN security checks:**
- **WPA3-Personal** preferred for personal SSIDs (Mist Wireless guide §5047 equivalent: WPA3-Personal allows authentication using PSK on devices that don't support).
- **WPA3-Enterprise** for corporate.
- **WPA2 acceptable** for legacy compatibility.
- **WEP / WPA** anything older — REGRESSION.

**Drift findings:**
- **REGRESSION — VLAN 1 in production WLAN**.
- **REGRESSION — hardcoded RADIUS server IPs** instead of `{{auth_srv1}}` template variables.
- **REGRESSION — open SSID without captive portal**.
- **REGRESSION — 11r enabled on non-Enterprise SSID** (won't function).
- **REGRESSION — WEP / WPA1 (deprecated security)**.
- **DRIFT — band steering disabled** on dual/tri-band SSID.
- **DRIFT — 11r disabled** on a WPA3/WPA2 enterprise SSID.
- **DRIFT — `mDNS scope: all`** on an SSID where `same_site` would suffice.
- **DRIFT — ARP filter disabled** on an IoT SSID.
- **DRIFT — static shared PSK** on a WLAN where Cloud PSK / MPSK would fit.
- **DRIFT — broadcast limit disabled** on guest SSID.

### Step 3 — Bare site-level WLANs (primary drift source)

**Tool:** for each site, `mist_get_wlans(site_id=<site_id>)` — check each returned WLAN's `template_id` field.

**Mist best practice:** every WLAN should be in a template; bare site-level WLANs (i.e. WLANs created without going through a template) are explicitly discouraged because they cannot be centrally managed and create drift.

**Drift findings:**
- **REGRESSION — bare site-level WLAN**: WLAN at a site with empty/null `template_id`. **Lead the report with this — primary drift source.**

**Performance:** N+1 calls (one per site). For 50+ sites the audit warns up front; offer site-group-scoped audit instead.

### Step 4 — Org-level WLAN reconciliation

**Tool:** `mist_get_configuration_objects(org_id=..., object_type="wlans")`

Cross-reference org-level WLANs with templates from step 1. Every org-level WLAN should have a `template_id` matching one of those templates.

**Drift findings:**
- **REGRESSION — orphan WLAN**: WLAN exists in `wlans` but its `template_id` references a deleted template. Broken reference.

### Step 5 — RF templates + per-band settings

**Tool:** `mist_get_configuration_objects(org_id=..., object_type="rftemplates")`

**Mist best practice (§3 of best-practices doc + Mist Wireless guide):**
- Start with Mist AI RRM. Don't lock channels or fix TX power without specific justification.
- Assign a baseline RF template at **org level or site-group level** for consistent defaults.
- Override at **site level** only for genuinely unique RF requirements.
- Use **separate templates for indoor vs. outdoor**.
- **Don't create a unique RF template per site** — defeats the management benefit.

**Per-band recommendations (§3.3 of best-practices doc):**

| Band | Channel width | TX power | Notes |
|---|---|---|---|
| 2.4 GHz | 20 MHz only | 12–17 dBm typical | Use channels 1, 6, 11. Disable on dense deployments if 5/6 GHz coverage is enough. |
| 5 GHz | 40 or 80 MHz | 17–23 dBm acceptable | Let Mist AI select from full non-DFS or DFS+non-DFS pool |
| 6 GHz (Wi-Fi 6E) | 80 MHz typical, 160 for very high throughput | (let Mist AI decide) | Use PSC (Preferred Scanning Channels) for discovery |

**Per-template structural checks:**
- Channel-width per band matches recommendations.
- TX power range NOT fixed; min-max range allowed for AI RRM.
- Band-steering threshold (RSSI) tuned for the deployment density.
- Indoor vs outdoor template differentiation present.

**Valid reasons to override** (per §3.2 of best-practices doc — these are NOT drift):
- High-density environments (venues, classrooms) requiring fixed cell sizing
- Outdoor deployments where terrain / distance require manual power
- Regulatory compliance requiring channel exclusion
- Co-existence with legacy equipment that can't handle wider channel widths

**Drift findings:**
- **REGRESSION — fixed channels on 2.4 GHz beyond {1, 6, 11}**: only those are non-overlapping.
- **REGRESSION — channel width > 20 MHz on 2.4 GHz**: never use bonded channels on 2.4 GHz.
- **DRIFT — fixed TX power on any band**: should let Mist AI RRM manage power; flag for justification.
- **DRIFT — fixed channels on 5/6 GHz**: should let Mist AI RRM select; flag.
- **DRIFT — RF template proliferation**: ≥ N RF templates where N approaches the site count (suggests per-site templates instead of a small set of base + outdoor + dense templates).
- **DRIFT — no RF template assigned at org or site-group level**: missing baseline.
- **DRIFT — same RF template used for indoor and outdoor**: should be split.

### Step 6 — Switch configuration templates (Mist Wired)

**Tool:** `mist_get_configuration_objects(org_id=..., object_type="networktemplates")` (or "switchtemplates" depending on API).

**Mist Wired guide (§Configure Switches Using Templates):** explicitly documents the hierarchy:

> *"organization-level template > site-level configuration > device-level configuration. The narrower settings override the broader settings. When a conflict between the organization-level template settings and site-level configuration settings occurs, the narrower settings override the broader settings."*

> *"We recommend that all switches in an organization be managed exclusively through the Juniper Mist cloud, and not from the device's CLI."*

**Mist Wired guide — Configuration template structure:**
- **All Switches Configuration**: applies to all switches in the org under the template
- **Select Switches Configuration**: applies to specific switch model(s) — Info / Port Config / IP Config / IP Config (OOB) / STP Bridge Priority / Port Mirroring / CLI Config tabs
- **Site Variables**: per-site values (covered in step 7)

**VAR-labeled fields**: any field with a `VAR` label can use site variables — the resolved value displays beneath. Hardcoded values where a VAR field exists are drift.

**Per-template checks:**
- Org-level template covers most settings; site-level config has minimal overrides.
- Additional CLI commands semantics: at site-level → OR logic with template; at device-level → AND logic with template (operator should understand).
- Mist explicitly says **"Unless required, do not override the settings at the site level. Use site variables, ..."**. So site-level overrides should be the exception.
- **All switches** in the org should be managed by Mist (Mist Wired §1315), NOT via the device CLI. Detect any logged CLI changes as drift.

**Drift findings:**
- **REGRESSION — switch managed via CLI**: any switch with CLI changes detected (Mist Wired explicitly forbids — *"the changes you make on a switch through the CLI don't get included in the [config]"*, §3597-§3598). REGRESSION class.
- **REGRESSION — bare site-level switch config**: switch config at a site without going through a template (analog to bare site-level WLANs).
- **REGRESSION — broken applies reference**: template's site assignment references a deleted site/group.
- **DRIFT — site-level overrides for fields that have VAR labels**: should use site variables instead.
- **DRIFT — extensive site-level CLI Config additions**: AND/OR logic gets confusing; consolidate at template level if possible.
- **DRIFT — All Switches Configuration empty**: template doesn't actually centralize config; mostly per-site overrides.

### Step 7 — Site Variables (Mist's alias-equivalent)

**Tool:** site variables live in site settings; `mist_get_org_or_site_info(info_type="setting", site_id=<site_id>)` returns the `vars` dict per site.

**Mist Wired guide (§1279-§1292):**

> *"Mist also provides an option to use site variables to streamline the switch configuration. Site variables, configured at Organization > Site Configuration > Site Variables, provide a way to use tags to represent real values so that the value can vary according to the context where you use the variable."*

> *"This means the same variable can configure different values in different sites."*

**This is Mist's equivalent of Central aliases** — same definition-vs-value pattern:

1. **Variable DEFINITION** — at Organization > Site Configuration (org level), or referenced in a switch template. The variable is the placeholder.
2. **Variable VALUE** — assigned per-site (each site fills in its own value for the variable).

**Per-site values are NOT drift** — that's the whole point. The same variable `{{vlan_data}}` legitimately resolves to a different VLAN ID at each site if that's the design.

**Mist Wired guide explicit rule (§1423):** *"Unless required, do not override the settings at the site level. **Use site variables**, ..."* — site variables are the canonical mechanism for site-specific values.

**Per-variable checks:**
- Variable referenced by a template but no value defined at some sites → push will fail at those sites.
- Variable defined but not referenced anywhere → orphan.
- Hardcoded values in templates where a variable would centralize the pattern → drift.

**Drift findings:**
- **REGRESSION — variable referenced but no value at a site** that uses the template: incomplete coverage.
- **DRIFT — orphan site variables**: defined at org but not referenced by any template.
- **DRIFT — hardcoded values where a variable exists**: a template hardcodes a value (e.g., a specific RADIUS IP) that's already defined as a site variable. Operator should switch to the variable.
- **DRIFT — VAR-labeled fields not using a variable**: a field that supports variables uses a hardcoded value instead.

**INFO findings:**
- **Per-site variable resolution table** — for each variable, list the per-site value mapping. NOT drift; reference for operators.

### Step 8 — Site templates + new-site provisioning

**Tool:** `mist_get_configuration_objects(org_id=..., object_type="sitetemplates")`

**Mist best practice (§4.3):** create at least one site template that represents the standard deployment baseline. Apply at site creation time so defaults are set automatically.

**Per-template checks:**
- Timezone defined.
- Country code defined.
- Auto-upgrade settings present.
- Default RF template referenced.
- Default WLAN template referenced.

**Drift findings:**
- **DRIFT — no site templates defined**: org has no consistent new-site baseline.
- **DRIFT — multiple site templates with overlapping purposes**: consolidate.
- **DRIFT — site template missing timezone / country code**: incomplete baseline.
- **INFO — site template count + their settings**: list timezone, country code, auto-upgrade defaults.

### Step 9 — Site groups + site membership

**Tools:**
- `mist_get_configuration_objects(org_id=..., object_type="sitegroups")` — site groups.
- `mist_get_org_or_site_info(info_type="site")` — site list.

**Mist best practice (§4.4):** site groups reflect operational topology (region, site type, security zone). Templates are assigned to site groups whenever possible.

**Drift findings:**
- **DRIFT — sites not in any site group**: list them. They only inherit org-wide templates or templates assigned individually.
- **DRIFT — site group with 0 sites**: orphan group.
- **DRIFT — site group with 1 site**: defeats the grouping purpose.
- **INFO — site group → site membership table**.

### Step 10 — Site-level overrides audit (only specific overrides are valid)

For each site, check `mist_get_org_or_site_info(info_type="site")` and the site's `setting` info.

**Mist best practice (§4.2 of best-practices doc):** site-level config should be **site-specific overrides only**:
- Local gateway IP
- Timezone
- Country code
- Guest portal redirect URL tied to a local server
- Unique VLANs not shared with other sites

**Anything else at site level is drift.** Specifically:
- Site-level RADIUS server settings → should be in org-level WLAN template + site variables resolving `{{auth_srv1}}`
- Site-level syslog targets → should be at org level
- Site-level NTP / SNMP → should be at org level

**Mist Wired guide (§1423):** *"Unless required, do not override the settings at the site level. Use site variables, ..."*

**Per-site checks:**
- Compare each site's `setting.vars` to the templates that reference variables — incomplete coverage where templates expect a var but the site doesn't set it.
- Detect site-level config that should have come from a template.

**Drift findings:**
- **DRIFT — site-level config that should be at org**: e.g., site overriding RADIUS server settings (should be variables), syslog targets, NTP, SNMP — these belong at org per best practices.
- **DRIFT — site-level RADIUS hardcoded** (instead of via `{{auth_srv1}}` site variable).
- **INFO — per-site override summary**: list each site's overrides + flagged drift.

### Step 11 — Device profiles + per-device-type settings

**Tool:** `mist_get_configuration_objects(org_id=..., object_type="deviceprofiles")` (or per-device-type variants if available).

**Mist best practice (§4.2):** device profiles handle per-device-type settings (radio power overrides for specific AP models, switch port profiles, PoE settings). Device-level config is the **last resort**.

**What's NOT drift** — these per-device values are inherent identification, not configuration overrides:
- Per-device **hostname** (each switch / AP has a unique name)
- Per-device **management IP** (each switch needs a unique IP)
- Per-device **serial number / MAC** binding (intrinsic device identity)
- Per-device **role assignment** (per Mist Wired §1262: "switch role" is configured at device level)
- Per-device **IRB interfaces** (per Mist Wired §1262)

These are not "config that breaks the template model" — they're below the template's purview. Don't flag them.

**What IS drift** — device-level config that competes with template / device-profile / site config:
- Device-level radio settings overriding a site-group RF template (without a documented exception reason)
- Device-level VLAN config that should come from a site
- Device-level WLAN config (effectively a bare site-level WLAN scoped to one device — creates drift across the fleet)
- Device-level firmware target overriding the org-wide auto-upgrade policy

**Drift findings:**
- **REGRESSION — device-level radio overrides without justification**: AP with manually-pinned channel or TX power that the site-group RF template would otherwise manage.
- **REGRESSION — device-level WLAN config**: WLANs scoped to a single device.
- **DRIFT — device-level firmware override**: device pinned to a firmware version that diverges from the org auto-upgrade policy without documented reason.
- **DRIFT — device-level VLAN override**: VLAN config at device scope that should inherit from site.
- **INFO — device profile count + assignment**.
- **INFO — per-device hostname / IP / name / role table** (NOT drift; legitimate per-device identification — listed for operator visibility).

### Step 12 — Port profiles (static + dynamic) + AP-port best practices

**Tool:** `mist_get_configuration_objects(org_id=..., object_type="portprofiles")` (or per-template variants).

**Mist Wired guide (§3666 onwards):** port profiles can be **static** (manually assigned to a port) or **dynamic** (auto-assigned via LLDP / RADIUS / MAC matching).

**Best Practices in Port Configuration (Mist Wired §4007-§4012):**

> *"Here are a few recommendations for your switch ports to work seamlessly with the Mist APs:
> - Simple configuration should be on the port. Since the APs do not save the configuration by default, APs need configuration delivered via the port.
> - We do not recommend port security (MAC address limit), except in the case where all WLANs are bridged."*

**Per-port-profile structural checks:**

| Setting | Mist recommendation | Drift signal |
|---|---|---|
| Speed | Auto (default) | Hardcoded speed without reason (DRIFT) |
| Duplex | Auto (default) | Hardcoded half-duplex (DRIFT) |
| PoE on uplink ports | Disabled | PoE enabled on switch-to-switch link (Mist Wired §2738: "We recommend disabling PoE for ports that are connected to other switch ports") |
| MAC-based dynamic profile | NOT on 802.1X-enabled ports | MAC matching + 802.1X both enabled (Mist Wired §3001, §3853 — REGRESSION) |
| RADIUS-tracking | Recommended for dynamic profiles | Disabled (DRIFT) |
| BPDU Guard | Enable on access ports | Disabled (DRIFT) |
| Native VLAN | Should not be VLAN 1 in production | VLAN 1 (DRIFT) |
| MAC address limit / port security | Only when all WLANs bridged | Enabled on AP ports (REGRESSION per §4016) |
| RADIUS interim-update | 21600-43200 seconds (Mist Wired §2662: *"recommended value is 6 to 12 hours"*) | Outside that range (DRIFT) |

**Static vs Dynamic — per Mist Wired guidance:**
- Static port profiles: manually pin a port to a profile. Fine for stable infrastructure (uplinks, AP ports).
- Dynamic port profiles: auto-assign based on LLDP advertisement (e.g., AP discovers, port auto-configures), MAC OUI, or RADIUS attributes.

**Per-DPC (Dynamic Port Configuration) rules:**
- Mist Wired §3799: *"We recommend that you create a restricted network profile that can be assigned to unknown"*. Catch-all for unrecognized devices.
- §3847: *"we do not recommend using dynamic port profiles when RADIUS server"*. RADIUS-driven port assignment + DPC may conflict.
- §3001 / §3853: *"Do not use MAC-based matching on ports enabled with 802.1X authentication."*

**Drift findings:**
- **REGRESSION — port security on AP ports**: Mist Wired §4016 says port security only OK if all WLANs bridged.
- **REGRESSION — MAC-based dynamic match on 802.1X-enabled port** (§3001).
- **REGRESSION — switch-level port override** that competes with the template's port profile (creates drift).
- **DRIFT — PoE enabled on uplink-to-switch port** (§2738).
- **DRIFT — Speed/duplex hardcoded** without reason.
- **DRIFT — VLAN 1 as native** on a production trunk.
- **DRIFT — RADIUS interim-update outside 6-12 hour window** (§2662).
- **DRIFT — no restricted network profile** for unrecognized devices on DPC-enabled ports.
- **INFO — DPC rule audit table**: rules + matching criteria + assigned profile.

### Step 13 — Firmware policy (auto-upgrade + version tags)

**Tools:**
- `mist_get_configuration_objects(org_id=..., object_type="upgrades")` if available, OR
- `mist_list_upgrades()` (general)
- `mist_get_org_or_site_info(info_type="org")` for org-level firmware policy

**Mist best practice (§4.5):**
- Auto-upgrade enabled at **org level** with a defined maintenance window
- Maintenance window avoids business hours (e.g., 2-4 AM local)
- Use firmware compliance tracking
- Test on a pilot site group before rolling org-wide

**Mist Wireless guide (§Firmware Version Tags for Juniper Mist Access Points, §3690-§3811):**
- **SSR** (Serviceable Supported Release) — older, patched
- **LSR** (Latest Supported Release) — newest, recommended
- Apply specific firmware to specific models supported

**Per-policy checks:**
- Auto-upgrade enabled at org.
- Maintenance window: not 09:00-17:00 local.
- Pilot site group exists for testing before fleet-wide rollout.
- Firmware compliance tracking enabled.

**Drift findings:**
- **REGRESSION — no auto-upgrade enabled**: org-level policy missing.
- **DRIFT — maintenance window during business hours**: review.
- **DRIFT — no pilot site group**: all sites get firmware on the same day; risky for fleets > 50 sites.
- **DRIFT — devices behind on firmware**: list devices that haven't picked up the latest org-recommended firmware.
- **DRIFT — per-device firmware pin** that diverges from the policy.

### Step 14 — PSK / MPSK strategy

**Tool:** `mist_get_configuration_objects(org_id=..., object_type="psks")` for org-level PSK store.

**Mist best practice (§4.6):**
- Use **Cloud PSK** / **MPSK** (per-user / per-device unique passphrase with VLAN assignment) over static shared PSK
- Set **expiration dates** on guest PSKs
- Use the **VLAN assignment** in the PSK record for per-device segmentation

**Per-PSK-record checks:**
- Expiration date present (especially for guest PSKs).
- VLAN assignment populated.
- Role assignment populated.
- Owner / contact info populated (for revocation).

**Drift findings:**
- **DRIFT — static shared PSK on a personal-WLAN context**: should be Cloud PSK / MPSK.
- **DRIFT — guest PSK with no expiration**: orphan credentials.
- **DRIFT — PSK without VLAN assignment**: missing per-device segmentation opportunity.
- **DRIFT — same PSK passphrase reused across multiple records**: defeats per-device tracking.
- **INFO — PSK count + types in use**: tabulate Cloud PSK vs MPSK vs static.
- **INFO — expiring-soon PSKs**: list (within 7 days).

## Decision matrix

| Condition | Action |
|---|---|
| Mist is `degraded` or `unavailable` | Stop. Audit cannot run reliably. |
| Org has 50+ sites | Warn user about per-site WLAN inspection cost (step 3); offer site-group scope. |
| User asked for single-site audit | Skip step 9 (site groups) and step 10 cross-site analysis. |
| Bare site-level WLANs found | Lead REGRESSION section with this — primary drift. |
| Switch managed via CLI (Mist Wired explicitly forbids) | REGRESSION. |
| VLAN 1 found in any production WLAN | REGRESSION — Mist best practices explicitly forbid. |
| Hardcoded RADIUS IPs in WLAN templates | REGRESSION — should use `{{auth_srv1}}` template variables. |
| 11r enabled on non-Enterprise SSID | REGRESSION (won't function). |
| WEP / WPA1 on any WLAN | REGRESSION — deprecated. |
| Open SSID without captive portal | REGRESSION. |
| Port security on AP ports | REGRESSION (Mist Wired §4016). |
| MAC-based dynamic match on 802.1X-enabled port | REGRESSION (Mist Wired §3001). |
| No org-level firmware auto-upgrade enabled | REGRESSION — Mist strongly recommends this. |
| Device-level radio / WLAN / VLAN / firmware overrides found | REGRESSION (these compete with template / site-group / org config). |
| Per-device hostname / IP / name (legitimate identification) | INFO only — NOT drift. Listed for operator visibility. |
| RF template proliferation (per-site templates) | DRIFT — defeats template management. |
| RF template uses fixed channels/power without justification | DRIFT — Mist AI RRM should manage. |
| Static shared PSK on a personal WLAN | DRIFT — recommend Cloud PSK or MPSK. |
| Hardcoded value in a VAR-labeled field | DRIFT — should use a site variable. |
| Site variable referenced but not defined at all sites that use the template | REGRESSION — push fails at uncovered sites. |
| Channel width > 20 MHz on 2.4 GHz | REGRESSION. |
| 2.4 GHz channels other than 1, 6, 11 | REGRESSION. |

## Output formatting

Use the EXACT structure below. Every section must be present even if its content is "no findings." Lead with REGRESSION, then DRIFT, then INFO. Keep findings terse; the report is meant to be scannable.

```
## Mist comprehensive scope audit — <scope: org-wide | site group <name> | site <name>>
**Captured:** <ISO timestamp>
**org_id:** <id>
**Total sites:** <N>
**Total site groups:** <M>
**Total WLAN templates:** <K>
**Total RF templates:** <L>
**Total switch templates:** <S>
**Total site templates:** <P>
**Total site variables defined:** <V>
**Anchored on:** Mist best-practices doc + Mist Wired Assurance guide + Mist Wireless Assurance guide + Juniper AI-Driven Wired & Wireless Network Deployment Guide

### Profile-category summary
| Category | Count | Most-common scope | Recommendation match |
|---|---|---|---|
| WLAN templates | <K> | site groups | ✓ |
| Org-level WLANs | <count> (all should have template_id) | n/a | ✓/✗ |
| Bare site-level WLANs | <N> (should be 0) | n/a | ✓/✗ |
| RF templates | <L> | site groups / site | ✓/✗ |
| Switch templates | <S> | org | ✓/✗ |
| Site templates | <P> | applied at new-site creation | ✓/✗ |
| Site groups | <M> | reflects operational topology | ✓/✗ |
| Site variables | <V> | org-defined, per-site values | ✓/✗ |
| Device profiles | <Q> | per-device-type | ✓/✗ |
| Port profiles | <PP> (static <a>, dynamic <b>) | per-template | ✓/✗ |
| Firmware auto-upgrade | enabled/disabled, maintenance window | org-wide | ✓/✗ |
| PSK records (Cloud + MPSK + static) | <a>/<b>/<c> | org PSK store | ✓/✗ |

### REGRESSION findings (lead with these)
- **Bare site-level WLANs**: <N> findings.
  - Site `HOME`: 2 bare site-level WLANs (`legacy-corp`, `guest-test`) — created without a template. Recommendation: move into an org-level WLAN template + delete site-level copies.
- **Switch managed via CLI** (Mist Wired explicitly forbids): <N> findings.
  - Switch `<name>`: CLI changes detected outside Mist management. Recommendation: re-import config into a template + revert CLI.
- **Hardcoded RADIUS IPs**: <N> findings.
  - WLAN template `Corporate` SSID `corp-dot1x` has `auth_servers[0].host = 10.0.0.1` — should be `{{auth_srv1}}`.
- **VLAN 1 in production WLAN**: <N> findings.
- **11r on non-Enterprise SSID**: <N> findings (won't function).
- **WEP/WPA1 in use**: <N> findings.
- **Open SSID without captive portal**: <N> findings.
- **Port security on AP ports** (Mist Wired §4016): <N> findings.
- **MAC-based dynamic match on 802.1X port** (Mist Wired §3001): <N> findings.
- **Device-level config overrides** (radio / WLAN / VLAN / firmware): <N> findings.
- **No firmware auto-upgrade policy**: org-level policy missing or disabled.
- **Channel width > 20 MHz on 2.4 GHz**: <N> findings.
- **2.4 GHz channels other than 1/6/11**: <N> findings.
- **Broken applies references**: <N> findings.
- **Orphan WLANs**: WLAN with `template_id` pointing to a deleted template.
- **Site variable referenced but no value at site** that uses the template: <N> findings.

### DRIFT findings
- **Per-site assignments that should be site-group**: <N> findings.
- **RF template proliferation / bad RF settings**: <N> findings.
- **Monolithic WLAN templates**: <N> findings.
- **Per-WLAN setting drift**: <N> findings (band steering / 11r / mDNS / ARP / broadcast).
- **Hardcoded values in VAR-labeled fields**: <N> findings.
- **Orphan site variables**: <N> findings.
- **Site-level config that belongs at org**: <N> findings.
- **Sites not in any site group**: <list>.
- **Site groups with 0 sites or 1 site**: <list>.
- **Static shared PSK in personal WLAN**: <N> findings.
- **Guest PSK with no expiration**: <N> findings.
- **Device-level firmware pin**: <N> findings.
- **PoE on switch-to-switch ports**: <N> findings.
- **Speed/duplex hardcoded**: <N> findings.
- **RADIUS interim-update outside 6-12 hour range**: <N> findings.
- **Maintenance window during business hours**: 1 finding.
- **No pilot site group for firmware**: 1 finding.

### INFO findings
- **Per-device identification** (hostname / IP / name — NOT drift; legitimate per-device values, listed for operator visibility): table of device → hostname, IP, role.
- **Per-site variable resolution** (NOT drift; legitimate per-site values): table of variable → site → value.
- **Site groups → templates assigned table**: ...
- **Per-site override summary**: ...
- **Firmware compliance**: <N> devices behind on firmware (list).
- **Site templates and what they contain**: ...
- **DPC (Dynamic Port Configuration) rule audit**: rules + matching criteria + assigned profile.
- **Expiring-soon PSKs** (within 7 days): <list>.

### Recommended next actions
- Bulleted list of operator actions, ordered by severity.
- (or "No actions — config is in good shape per Mist best practices and Wired/Wireless guides.")
```

## Example queries that should trigger this skill

> "audit Mist scope"
> "where are my Mist WLAN templates assigned?"
> "is my Mist config drifting?"
> "find bare site-level WLANs"
> "audit Mist RF templates"
> "audit Mist switch templates"
> "audit Mist port profiles"
> "audit Mist site variables"
> "audit Mist firmware policy"
> "audit Mist PSK strategy"
> "audit Mist site overrides"
> "Mist comprehensive configuration audit"
> "Mist VSG-style configuration audit"
> "find Mist switches managed via CLI"
> "audit Mist dynamic port configuration"
