"""Cross-platform WLAN sync prompts.

These prompts orchestrate workflows that span both Juniper Mist and
Aruba Central. They are registered after both platforms are loaded
so they can reference tools from either platform.
"""


def register(mcp):

    @mcp.prompt
    def sync_wlans_mist_to_central() -> str:
        """Sync WLAN profiles from Mist to Central."""
        return """
Sync WLAN profiles from Juniper Mist to Aruba Central:

**STEP 1 — Get Mist org_id (MANDATORY FIRST STEP)**
Call `mist_get_self(action_type=account_info)` to get the correct org_id. \
Do NOT use any org_id from memory or previous conversations. The org_id \
returned by this call is the ONLY valid org_id.

**STEP 2 — Find the WLAN and its template assignment**
a. Call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_wlans, name=<ssid_name>)` to find the target WLAN. \
Note the `template_id` field — this tells you which WLAN template it \
belongs to.
b. If `template_id` is present: call \
`mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_wlantemplates, object_id=<template_id>)` to get the \
template. Note the template `name`, `sitegroup_ids` array (site groups \
the template is assigned to), and `site_ids` array (specific sites \
the template is assigned to).
c. If `sitegroup_ids` is not empty: for each sitegroup_id, call \
`mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_sitegroups, object_id=<sitegroup_id>)` to get the \
site group name. Record the site group names for assignment mapping.
d. If `site_ids` is not empty: for each site_id, call \
`mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_sites, object_id=<site_id>)` to get the site name. \
Record the site names for assignment mapping.
e. If no `template_id` — this is a site-level WLAN. Note this for \
the user but still proceed if they want to sync it.

**STEP 3 — Skip tunneled SSIDs**
If the WLAN has `interface` set to a tunnel mode (not "all" or \
"ethernet"), skip it and tell the user.

**STEP 4 — Resolve Mist template variables**
a. **RADIUS servers**: for each entry in `auth_servers` and \
`acct_servers`, check if `host` uses a template variable \
(e.g. `{{auth_srv1}}`). If so, call \
`mist_get_org_or_site_info(org_id=<org_id>, site_id=<site_id>, \
info_type=setting)` for a representative site to get `vars` and \
resolve the variable to the actual FQDN or IP address.
b. **PSK**: get `auth.psk` directly (Mist PSKs are inline values).
c. **VLAN**: get VLAN IDs from `dynamic_vlan` or `vlan_id` directly.

**STEP 5 — Check if SSID already exists in Central**
Call `central_get_wlan_profiles(ssid=<ssid_name>)` to check.
a. If it EXISTS: compare mapped fields. Show the user a table of \
differences (field name, Mist value, Central value). Ask: \
"Use Mist as source (overwrite Central)?", "Keep Central as-is?", \
or "Skip?". If no differences, report "in sync" and skip.
b. If it does NOT exist: proceed to create.

**STEP 6 — Map fields from Mist to Central format**
Key opmode mappings (use ONLY these valid Central values):
- Mist auth.type="psk" + pairwise=["wpa2-ccmp"] → opmode="WPA2_PERSONAL"
- Mist auth.type="psk" + pairwise=["wpa3"] → opmode="WPA3_SAE"
- Mist auth.type="eap" + pairwise=["wpa2-ccmp"] → opmode="WPA2_ENTERPRISE"
- Mist auth.type="eap" + pairwise=["wpa3","wpa2-ccmp"] → opmode="WPA3_ENTERPRISE_CCM_128"
- Mist dynamic_psk.enabled=true → opmode="WPA2_MPSK_AES"
Other field mappings: ssid→essid.name, auth.psk→personal-security.wpa-passphrase, \
vlan_id→vlan-id-range, bands→rf-band, dtim→dtim-period, \
isolation→client-isolation, rateset→data rate profile, \
arp_filter→broadcast-filter-ipv4, roam_mode="11r"→dot11r=true.

**STEP 7 — RADIUS server mapping**
a. Check if a matching server group exists: call \
`central_get_server_groups` and compare server addresses.
b. If no match: note that a server group needs to be created.
c. Map NAS ID/IP, CoA, and RadSec settings directly.

**STEP 8 — Create the Central WLAN profile**
Call `central_manage_wlan_profile` with the mapped payload.

**STEP 9 — Assignment mapping (REQUIRED — do not skip)**
Based on the template assignment found in Step 2:
- If Mist template has no `sitegroup_ids` and no `site_ids` (org-wide) \
→ tell user to assign at Central Global scope
- If Mist template has `sitegroup_ids` → for each site group name \
found in Step 2c, check if a matching Central site collection exists. \
Tell the user which site collections to assign the profile to. If \
a matching collection doesn't exist, tell the user it needs to be created.
- If Mist template has `site_ids` → for each site name found in \
Step 2d, check if a matching Central site exists. Tell the user which \
Central sites to assign the profile to.
- Report: "In Mist, this WLAN is in template '<name>' assigned to \
site groups: <list> and/or sites: <list>. In Central, assign the \
profile to matching site collections: <list> and/or sites: <list>."

**STEP 10 — Report summary**
WLANs created, updated, in sync, skipped (tunneled), variables \
resolved, and assignment recommendations.
        """.strip()

    @mcp.prompt
    def sync_wlans_central_to_mist() -> str:
        """Sync WLAN profiles from Central to Mist."""
        return """
Sync WLAN profiles from Aruba Central to Juniper Mist:

1. Call `central_get_wlan_profiles` to list all WLAN SSID profiles.
2. Skip tunneled SSIDs (forward-mode != FORWARD_MODE_BRIDGE).
3. Resolve Central aliases and named references for each profile:
   a. **SSID name**: if essid.use-alias is set, call \
`central_get_aliases(alias_name=<alias>)` to get the broadcasted SSID \
name. Otherwise use essid.name.
   b. **PSK**: if personal-security.wpa-passphrase-alias is set, call \
`central_get_aliases(alias_name=<alias>)` to get the actual passphrase.
   c. **RADIUS servers**: if auth-server-group is set, call \
`central_get_server_groups(name=<group>)` to get server list. For each \
server, check if the host (FQDN or IP) uses an alias — if so, call \
`central_get_aliases(alias_name=<alias>)` to resolve to the actual address.
   d. **Accounting servers**: same resolution for acct-server-group.
   e. **VLAN**: if vlan-name is set, call \
`central_get_named_vlans(name=<vlan_name>)` to resolve the VLAN ID. \
If the named VLAN uses an alias, resolve via `central_get_aliases`.
4. Call `mist_get_self(action_type=account_info)` to get org_id.
5. For each Central WLAN profile:
   a. Call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_wlans)` and check if SSID already exists in Mist \
(match by resolved SSID name).
   b. If it EXISTS in Mist: compare the mapped fields between \
the Central profile and the Mist WLAN. Show the user a table of \
differences (field name, Central value, Mist value). If there are \
differences, ask the user: "Use Central as source (overwrite Mist)?", \
"Keep Mist as-is?", or "Skip this SSID?". If no differences, \
report as "in sync" and skip.
   c. If it does NOT exist in Mist: map the Central WLAN fields to \
Mist format. Key mappings: essid.name (or resolved alias)→ssid, \
opmode→auth.type+auth.pairwise, personal-security→auth.psk, \
vlan-name→dynamic_vlan (use resolved VLAN ID), \
rf-band→bands, dtim-period→dtim, client-isolation→isolation, \
data rates→rateset template (compatible/no-legacy/high-density based on MBR), \
broadcast-filter-ipv4→arp_filter, dot11r→roam_mode.
6. RADIUS server mapping (use template variables, never hardcode):
   a. For each resolved RADIUS auth server, map to a Mist \
`auth_servers` entry using template variables: \
`{"host": "{{auth_srv1}}", "port": <port>, "secret": "<secret>"}`.
   b. Same for accounting: `acct_servers` with `{{acct_srv1}}` etc.
   c. Define the resolved addresses in each Mist site's vars: \
call `mist_get_org_or_site_info(info_type=setting)` to check existing \
vars, then update site settings with vars like \
`{"auth_srv1": "<resolved_address>", "acct_srv1": "<resolved_address>"}`.
   d. Map NAS ID/IP, CoA, and RadSec settings directly.
7. Use the Central profile name as the Mist WLAN template name. \
Create the template, then create the WLAN inside it.
8. Assignment mapping:
   - Central Global assignment → Assign Mist template at org level
   - Central site collection → Assign Mist template to matching site \
group (create if missing, prompt user)
   - Central specific sites → Assign Mist template to those sites \
(create if missing, prompt user)
9. Report summary: WLANs created, updated, in sync, skipped (tunneled), \
aliases resolved, template variables created, and assignment recommendations.
        """.strip()

    @mcp.prompt
    def sync_wlans_bidirectional() -> str:
        """Compare and sync WLANs between Mist and Central."""
        return """
Compare and sync WLAN profiles between Juniper Mist and Aruba Central:

1. Gather WLANs from both platforms:
   a. Call `mist_get_self(action_type=account_info)` for org_id.
   b. Call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_wlantemplates)` and then `org_wlans` to get all \
template-based Mist WLANs.
   c. Call `central_get_wlan_profiles` to get all Central profiles.
2. Resolve all aliases, variables, and named references:
   a. **Central SSID aliases**: for profiles with essid.use-alias, call \
`central_get_aliases(alias_name=<alias>)` to get broadcasted SSID names.
   b. **Central PSK aliases**: for profiles with wpa-passphrase-alias, \
call `central_get_aliases(alias_name=<alias>)` to get passphrase values.
   c. **Central RADIUS server groups**: for profiles with auth-server-group \
or acct-server-group, call `central_get_server_groups(name=<group>)` to \
get server lists. Resolve any aliased server hosts via `central_get_aliases`.
   d. **Central named VLANs**: for profiles with vlan-name, call \
`central_get_named_vlans(name=<vlan>)` to get VLAN IDs. Resolve any \
aliased VLAN IDs via `central_get_aliases`.
   e. **Mist template variables**: for Mist WLANs with `{{variable}}` \
patterns in auth_servers/acct_servers host fields, call \
`mist_get_org_or_site_info(org_id=<org_id>, site_id=<site_id>, \
info_type=setting)` for a representative site to resolve vars to \
actual FQDN or IP addresses.
3. Filter out tunneled SSIDs from both sides.
4. Compare by SSID name (using resolved alias for Central):
   - WLANs in both platforms with identical mapped fields → "in sync"
   - WLANs in both platforms with differences → "out of sync" — show \
a table of differences for each (field, Mist value, Central value). \
For RADIUS comparisons, compare the resolved addresses (not the \
alias/variable names).
   - WLANs only in Mist → "missing in Central"
   - WLANs only in Central → "missing in Mist"
5. Present a summary table: SSID Name, In Mist, In Central, Status \
(in sync / out of sync / missing).
6. For "out of sync" WLANs, ask the user for each one:
   - "Use Mist as source" (update Central to match Mist)
   - "Use Central as source" (update Mist to match Central)
   - "Skip"
7. For "missing" WLANs, ask the user:
   - "Sync missing to both platforms" (create on the platform where missing)
   - "Sync Mist → Central only"
   - "Sync Central → Mist only"
   - "Skip missing WLANs"
8. Execute the chosen actions using the field mapping and resolution \
workflows. When syncing RADIUS servers:
   - Central → Mist: use template variables ({{auth_srv1}} etc.) in \
Mist WLANs, define resolved addresses in site vars.
   - Mist → Central: create/match server groups, create aliases for \
per-site variation matching Mist variable names.
9. Report final summary: created, updated, in sync, skipped, \
aliases/variables resolved.
        """.strip()
