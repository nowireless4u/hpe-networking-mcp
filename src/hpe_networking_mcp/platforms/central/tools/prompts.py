def register(mcp):

    @mcp.prompt
    def network_health_overview() -> str:
        """Full network health overview using the recommended tool workflow."""
        return """
Provide a full network health overview by following these steps:

1. Call `central_get_site_name_id_mapping` to get all sites with health scores, \
device/client/alert counts.
2. Identify sites with poor or fair health, or notably high alert counts.
3. Call `central_get_site_health` with only those site names(maximum 5) to get detailed \
metrics.
4. Summarize per site: health score, device/client/alert totals, and any notable \
issues.
5. End with an overall network health assessment and flag any sites requiring \
immediate attention.
        """.strip()

    @mcp.prompt
    def troubleshoot_site(site_name: str) -> str:
        """Deep-dive troubleshooting workflow for a specific site."""
        return f"""
Troubleshoot the site "{site_name}" by following these steps:

1. Call `central_get_site_name_id_mapping` to verify the site name and get its \
site_id and current health score.
2. Call `central_get_site_health` with site_names=["{site_name}"] to get detailed site \
metrics.
3. Call `central_get_alerts` with the site_id and status="Active" to get all \
active alerts. Prioritize by severity (Critical > High > Medium > Low).
4. Call `central_get_devices` with the site_id to get all devices at the site.
5. Summarize: site health, active alert breakdown by category and severity, \
device status overview, and recommended next steps.
        """.strip()

    @mcp.prompt
    def client_connectivity_check(mac_address: str) -> str:
        """Investigate a client's connectivity status and health of their site."""
        return f"""
Check connectivity for the client with MAC address "{mac_address}":

1. Call `central_find_client` with mac_address="{mac_address}" to get the \
client's current status and connected device serial number.
2. If found, note the site_id from the response.
3. Call `central_get_alerts` with the site_id and status="Active" to check \
for site-level issues that may affect the client.
4. Call `central_find_device` with the serial_number of the connected device \
to check device health.
5. Summarize: client status, connection details (type, VLAN, WLAN if wireless), \
related site/device alerts, and likely root cause if connectivity is failed.
        """.strip()

    @mcp.prompt
    def investigate_device_events(serial_number: str, time_range: str = "last_24h") -> str:
        """Investigate recent events for a specific device."""
        return f"""
Investigate recent events for device with serial number \
"{serial_number}" over the {time_range} window:

1. Call `central_find_device` with serial_number="{serial_number}" to confirm \
the device exists and get its site_id and device_type.
2. Map device_type to the matching context_type: ACCESS_POINT -> ACCESS_POINT, \
SWITCH -> SWITCH, GATEWAY -> GATEWAY.
3. Call `central_get_events_count` with context_type=<mapped type>, \
context_identifier="{serial_number}", site_id=<site_id>, \
time_range="{time_range}" to get a breakdown of event types and volumes.
4. If total > 0, call `central_get_events` with the same parameters to fetch \
full event details.
5. Summarize: event timeline, dominant event types, any recurring or critical \
events, and recommended next steps.
        """.strip()

    @mcp.prompt
    def site_event_summary(site_name: str, time_range: str = "last_24h") -> str:
        """Summarize all events at a site to identify patterns."""
        return f"""
Summarize events at site "{site_name}" over the {time_range} window:

1. Call `central_get_site_name_id_mapping` to verify the site name and get \
its site_id.
2. Call `central_get_events_count` with context_type="SITE", \
context_identifier=<site_id>, site_id=<site_id>, \
time_range="{time_range}" to get the event breakdown by type and category.
3. If total > 0, call `central_get_events` with the same parameters to fetch \
full event details.
4. Group events by category and name. Highlight any spikes, repeated errors, \
or critical events.
5. Summarize: total event count, top event types, notable patterns, and any \
suggested follow-up actions.
        """.strip()

    @mcp.prompt
    def failed_clients_investigation(site_name: str) -> str:
        """Find and diagnose all failed clients at a site."""
        return f"""
Investigate failed client connections at site "{site_name}":

1. Call `central_get_site_name_id_mapping` to verify the site name and get \
its site_id.
2. Call `central_get_clients` with site_id=<site_id> and status="Failed" to \
get all failed clients.
3. If no failed clients are found, report the site is clean.
4. For each failed client (up to 5), call `central_find_device` with the \
connected device serial number to check device health.
5. Call `central_get_alerts` with site_id=<site_id> and category="Clients" \
to check for site-level client alerts.
6. Summarize: number of failed clients, connection types affected (wired vs \
wireless), common failure patterns, related device or site alerts, and likely \
root causes.
        """.strip()

    @mcp.prompt
    def site_client_overview(site_name: str) -> str:
        """Overview of all client connectivity at a site."""
        return f"""
Provide a client connectivity overview for site "{site_name}":

1. Call `central_get_site_name_id_mapping` to verify the site name and get \
its site_id.
2. Call `central_get_clients` with site_id=<site_id> to get all clients at \
the site.
3. Break down clients by: connection type (Wired vs Wireless), status \
(Connected vs Failed), and VLAN.
4. For wireless clients, note WLAN distribution and any clients on unusual \
bands or security types.
5. Summarize: total client count, connected vs failed breakdown, any \
anomalies, and recommendations.
        """.strip()

    @mcp.prompt
    def device_type_health(site_name: str, device_type: str) -> str:
        """Health check for all devices of a specific type at a site."""
        return f"""
Check the health of all {device_type} devices at site "{site_name}":

1. Call `central_get_site_name_id_mapping` to verify the site name and get \
its site_id.
2. Call `central_get_devices` with site_id=<site_id> and \
device_type="{device_type}" to list all matching devices.
3. Call `central_get_alerts` with site_id=<site_id> and device_type matching \
the {device_type} display name to get relevant active alerts.
4. For any device with associated alerts, call `central_get_events_count` \
with the device serial number and time_range="last_24h" to check recent \
event activity.
5. Summarize: total device count, provisioned vs unprovisioned, active alert \
breakdown by severity, devices with high event activity, and recommended \
actions.
        """.strip()

    @mcp.prompt
    def critical_alerts_review() -> str:
        """Review all active critical alerts across the network."""
        return """
Review all active critical alerts across the network:

1. Call `central_get_site_name_id_mapping` to get all sites with their \
site_ids and alert counts.
2. For each site with total_alerts > 0, call `central_get_alerts` with \
the site_id and status="Active" to get all active alerts.
3. Filter to Critical severity only. Group by site and category.
4. Identify sites with the highest concentration of critical alerts.
5. Summarize: total critical alert count across the network, top affected \
sites, most common alert names by category, and recommended immediate actions.
        """.strip()

    @mcp.prompt
    def compare_site_health(site_names: list[str]) -> str:
        """Compare health metrics across multiple sites side by side."""
        sites_str = ", ".join(f'"{s}"' for s in site_names)
        return f"""
Compare health across sites: {sites_str}

1. Call `central_get_site_name_id_mapping` to verify all site names and get \
their site_ids and health scores.
2. Call `central_get_site_health` with site_names={list(site_names)} to get \
detailed metrics for each site.
3. For each site, call `central_get_alerts` with the site_id and \
status="Active" to get active alert counts by severity.
4. Present a side-by-side comparison table: site name, health score, device \
count, client count, alert breakdown (Critical/High/Medium/Low).
5. Rank sites from worst to best health.
        """.strip()

    @mcp.prompt
    def scope_configuration_overview(scope_name: str) -> str:
        """View committed configuration resources at a scope in the hierarchy."""
        return f"""
Show the committed configuration at scope "{scope_name}":

1. Call `central_get_scope_tree(view="committed")` to get the full hierarchy.
2. Search the tree for the scope matching "{scope_name}" by scope_name. \
Note its scope_id.
3. Call `central_get_scope_resources(scope_id=<scope_id>)` for that scope.
4. Present the results as follows:
   - Show the scope name, type, and position in the hierarchy.
   - For each persona, show the persona name, total resource count, and \
category breakdown (e.g. policy: 5, vlan: 3, profile: 2).
   - List resources grouped by category, not as a flat list.
   - Use a table or indented list for readability.
5. Summarize: total resource count across all personas, dominant persona, \
and any notable patterns (e.g. shared policies, unique resources).
6. Suggest using `central_get_effective_config` if the user wants to see \
inherited configuration, or `central_get_scope_diagram` for a visual map.
        """.strip()

    @mcp.prompt
    def scope_effective_config(scope_name: str) -> str:
        """View effective (inherited + committed) configuration at a scope."""
        return f"""
Show the effective configuration at scope "{scope_name}":

1. Call `central_get_scope_tree(view="committed")` to get the hierarchy.
2. Search for the scope matching "{scope_name}" by scope_name. Note its \
scope_id.
3. Call `central_get_effective_config(scope_id=<scope_id>)` for that scope.
4. Present the inheritance path first: show each level from Global down to \
this scope with how many resources each level contributes.
5. Then group resources by origin scope. For each origin:
   - Show the scope name and type (e.g. "Global", "Site Collection").
   - List the resources contributed at that level, grouped by category.
6. Highlight any resources that appear at multiple inheritance levels \
(overrides). When the same resource name appears from different origins, \
note which level takes precedence (closest scope wins).
7. Summarize: total effective resource count, how many are inherited vs \
committed locally, and the inheritance depth.
        """.strip()

    @mcp.prompt
    def sync_wlans_mist_to_central() -> str:
        """Sync WLAN profiles from Mist to Central."""
        return """
Sync WLAN profiles from Juniper Mist to Aruba Central:

1. Call `mist_get_self(action_type=account_info)` to get org_id.
2. Call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_wlantemplates)` to list all WLAN templates.
3. For each template, call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_wlans)` and filter WLANs by template_id to get WLANs \
in that template.
4. Only sync WLANs that are part of a template (skip site-level WLANs).
5. Deduplicate: if the same SSID name appears in multiple templates, \
only process it once.
6. Skip tunneled SSIDs (interface field set to tunnel modes).
7. For each unique WLAN:
   a. Call `central_get_wlan_profiles(ssid=<ssid_name>)` to check if \
it already exists in Central.
   b. If it EXISTS in Central: compare the mapped fields between \
the Mist WLAN and the Central profile. Show the user a table of \
differences (field name, Mist value, Central value). If there are \
differences, ask the user: "Use Mist as source (overwrite Central)?", \
"Keep Central as-is?", or "Skip this SSID?". If no differences, \
report as "in sync" and skip.
   c. If it does NOT exist in Central: map the Mist WLAN fields to \
Central format. Key mappings: ssid→essid.name, auth.type→opmode, \
auth.psk→personal-security.wpa-passphrase, dynamic_psk→mpsk settings, \
vlan_id→vlan-name, bands→rf-band, dtim→dtim-period, \
isolation→client-isolation, rateset→data rate profile, \
arp_filter→broadcast-filter-ipv4, roam_mode→dot11r. \
Resolve RADIUS servers from Mist auth_servers to Central server groups. \
Resolve VLANs from Mist VLAN IDs to Central named VLANs. \
Call `central_manage_wlan_profile` to create the profile.
8. Assignment mapping:
   - Mist template applies to org → Note: assign at Central Global scope
   - Mist template assigned to site group → Note: assign to matching \
Central site collection (create if missing, prompt user)
   - Mist template assigned to specific sites → Note: assign to those \
Central sites (create if missing, prompt user)
9. Report summary: WLANs created, updated, in sync, skipped (tunneled), \
and assignment recommendations.
        """.strip()

    @mcp.prompt
    def sync_wlans_central_to_mist() -> str:
        """Sync WLAN profiles from Central to Mist."""
        return """
Sync WLAN profiles from Aruba Central to Juniper Mist:

1. Call `central_get_wlan_profiles` to list all WLAN SSID profiles.
2. Skip tunneled SSIDs (forward-mode != FORWARD_MODE_BRIDGE).
3. For each Central WLAN profile, resolve the actual SSID name: \
if essid.use-alias is set, call `central_get_aliases(alias_name=...)` \
to get the broadcasted SSID name. Otherwise use essid.name.
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
vlan-name→dynamic_vlan (resolve named VLAN via central_get_named_vlans), \
rf-band→bands, dtim-period→dtim, client-isolation→isolation, \
data rates→rateset template (compatible/no-legacy/high-density based on MBR), \
broadcast-filter-ipv4→arp_filter, dot11r→roam_mode. \
Resolve RADIUS from Central server groups via central_get_server_groups. \
Use the Central profile name as the Mist WLAN template name. \
Create the template, then create the WLAN inside it.
6. Assignment mapping:
   - Central Global assignment → Assign Mist template at org level
   - Central site collection → Assign Mist template to matching site \
group (create if missing, prompt user)
   - Central specific sites → Assign Mist template to those sites \
(create if missing, prompt user)
7. Report summary: WLANs created, updated, in sync, skipped (tunneled), \
and assignment recommendations.
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
   d. For Central profiles with aliases, resolve via `central_get_aliases`.
2. Filter out tunneled SSIDs from both sides.
3. Compare by SSID name (using resolved alias for Central):
   - WLANs in both platforms with identical mapped fields → "in sync"
   - WLANs in both platforms with differences → "out of sync" — show \
a table of differences for each (field, Mist value, Central value)
   - WLANs only in Mist → "missing in Central"
   - WLANs only in Central → "missing in Mist"
4. Present a summary table: SSID Name, In Mist, In Central, Status \
(in sync / out of sync / missing).
5. For "out of sync" WLANs, ask the user for each one:
   - "Use Mist as source" (update Central to match Mist)
   - "Use Central as source" (update Mist to match Central)
   - "Skip"
6. For "missing" WLANs, ask the user:
   - "Sync missing to both platforms" (create on the platform where missing)
   - "Sync Mist → Central only"
   - "Sync Central → Mist only"
   - "Skip missing WLANs"
7. Execute the chosen actions using the field mapping and resolution \
workflows (alias, server group, named VLAN, data rate profile).
8. Report final summary: created, updated, in sync, skipped.
        """.strip()
