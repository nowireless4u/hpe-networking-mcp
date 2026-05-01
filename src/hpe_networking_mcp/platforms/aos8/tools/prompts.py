"""AOS8 guided prompts for operator workflows."""

from __future__ import annotations


def register(mcp):
    """Register all 9 AOS8 guided prompts with the FastMCP instance.

    Mirrors the central/tools/prompts.py registration pattern. Called once
    from aos8/__init__.py inside a try/except block.
    """

    @mcp.prompt
    def aos8_triage_client(mac_address: str) -> str:
        """Triage a wireless client connectivity problem by MAC address."""
        return f"""
Triage AOS8 client connectivity for MAC "{mac_address}":

1. Call `aos8_find_client` with mac_address="{mac_address}" to locate the client and capture
   the associated AP name, BSSID, SSID, VLAN, and user role.
2. Call `aos8_get_client_detail` with mac_address="{mac_address}" for full association,
   authentication, and encryption detail plus failed-auth counters.
3. Call `aos8_get_ap_detail` with the AP name from step 1 — capture radio state, channel,
   power, last-reboot time, and any AP-level alerts.
4. Call `aos8_get_client_history` with mac_address="{mac_address}" to look for repeated
   association flapping, auth failures, or roam thrash.
5. Call `aos8_get_events` filtered to the client MAC or AP scope to surface auth and
   association event timeline.
6. Call `aos8_get_alarms` filtered to the AP's scope to capture controller- or AP-level
   issues that may be the upstream cause.

Summarize: client current state (associated/auth-failed/roaming), AP health, auth event
timeline, likely root cause (auth failure, RF issue, AP outage, roaming), and the
recommended next operator action.
        """.strip()

    @mcp.prompt
    def aos8_triage_ap(ap_name: str) -> str:
        """Deep-dive a specific AOS8 AP: radio, clients, alarms, ARM, events."""
        return f"""
Deep-dive AOS8 access point "{ap_name}":

1. Call `aos8_get_ap_detail` with ap_name="{ap_name}" — capture model, status, IP,
   uptime, AP group, and last-reboot reason.
2. Call `aos8_get_radio_summary` filtered to "{ap_name}" — note channel, bandwidth,
   TX power, channel utilization, and noise floor on each band.
3. Call `aos8_get_bss_table` filtered to "{ap_name}" to enumerate active BSSIDs and
   per-radio client counts.
4. Call `aos8_get_alarms` filtered to AP "{ap_name}" — list active alarms by severity.
5. Call `aos8_get_arm_history` filtered to "{ap_name}" — list recent channel and power
   adjustments; flag radios that changed >3 times in 24h.
6. Call `aos8_get_events` filtered to AP "{ap_name}" — surface reboot, link, and
   association events.

Summarize: AP up/down state, per-radio health, client load, active alarm count by severity,
ARM stability, recent event timeline, and one recommended next action.
        """.strip()

    @mcp.prompt
    def aos8_health_check() -> str:
        """Network-wide AOS8 health assessment across Conductor and MDs."""
        return """
Provide a network-wide AOS8 health overview:

1. Call `aos8_get_controllers` to enumerate every controller and MD with role and status.
2. Call `aos8_get_version` to capture firmware on the Conductor and each MD; flag any
   version drift.
3. Call `aos8_get_active_aps` to count up-APs and association totals.
4. Call `aos8_get_ap_database` to capture total provisioned AP count for up/down delta.
5. Call `aos8_get_clients` to retrieve total connected client count.
6. Call `aos8_get_alarms` to pull active alarms; group by severity (Critical > Major >
   Minor > Warning) and category.
7. Call `aos8_get_controller_stats` for the master and standby Conductors — capture CPU,
   memory, uptime, and session counts.

Summarize: controller count by role, AP up/down totals, client total, alarm breakdown by
severity, firmware drift if any, controller resource health, and one recommended next
action per risk area.
        """.strip()

    @mcp.prompt
    def aos8_audit_change() -> str:
        """Review recent AOS8 audit trail entries and flag risky changes."""
        return """
Review recent AOS8 configuration changes:

1. Call `aos8_get_audit_trail` to fetch recent audit-log entries (who changed what, when,
   and at which config_path).
2. Call `aos8_get_events` filtered to configuration/management events to cross-reference
   the audit trail with system-side acknowledgements.
3. Group changes by config_path and by user; flag any change touching:
   - SSID profile, virtual AP, or AP group definitions
   - User roles or AAA configuration
   - VLAN or ACL definitions
   - netdestination objects
   These are high-blast-radius categories.

Summarize: total change count, top changers, top changed config_paths, list of
high-risk changes flagged with rationale, and one recommended follow-up (e.g., review
diff, rollback candidate, schedule peer review).
        """.strip()

    @mcp.prompt
    def aos8_rf_analysis(config_path: str = "/md") -> str:
        """RF environment report for an AOS8 scope: channels, co-channel, ARM history."""
        return f"""
Produce an RF environment report scoped to config_path "{config_path}":

1. Call `aos8_get_radio_summary` with config_path="{config_path}" — collect channel,
   bandwidth, TX power, channel utilization, and noise floor per radio per AP.
2. Group radios by band (2.4 / 5 / 6 GHz) and by channel; flag any channel with >3 APs
   in the same scope (co-channel cluster).
3. Call `aos8_get_arm_history` with config_path="{config_path}" — list recent ARM-driven
   channel and power changes; flag radios that have changed >3 times in 24h
   (oscillation).
4. Call `aos8_get_rf_monitor` with config_path="{config_path}" to capture interference
   sources and rogue detections.
5. Call `aos8_get_bss_table` with config_path="{config_path}" to compute BSSID density
   per AP per band.

Summarize: channel-distribution histogram per band, co-channel cluster list, top
oscillating radios, top interferers/rogues, and recommended channel-plan or
power-adjustment actions.
        """.strip()

    @mcp.prompt
    def aos8_wlan_review() -> str:
        """Inventory AOS8 SSID/VAP/AP-group/role config; flag inconsistencies."""
        return """
Review the AOS8 WLAN configuration surface end-to-end:

1. Call `aos8_get_ssid_profiles` to list every SSID profile with its essid, opmode,
   encryption, and key settings.
2. Call `aos8_get_virtual_aps` to list every virtual AP profile and the SSID profile +
   AAA profile each binds.
3. Call `aos8_get_ap_groups` to list every AP group with its applied virtual-AP list and
   member-AP count.
4. Call `aos8_get_user_roles` to list every user role and its session ACL / VLAN /
   bandwidth-contract assignment.
5. Cross-reference: flag (a) SSID profiles not bound to any virtual AP, (b) virtual APs
   not applied to any AP group, (c) AP groups with zero member APs, (d) user roles not
   referenced by any AAA profile or virtual AP.

Summarize: counts per object type, list of orphaned/unused profiles, any SSIDs with
encryption weaker than wpa2-aes, and one recommended cleanup action per finding.
        """.strip()

    @mcp.prompt
    def aos8_client_flood(config_path: str = "/md") -> str:
        """Investigate high client counts or failed connections at an AOS8 scope."""
        return f"""
Investigate client-flood / failed-connection conditions at config_path "{config_path}":

1. Call `aos8_get_clients` with config_path="{config_path}" — capture total connected
   client count and per-AP distribution.
2. Call `aos8_get_active_aps` with config_path="{config_path}" — compute average and
   max clients-per-AP; flag APs above 1.5x the scope average.
3. Call `aos8_get_radio_summary` with config_path="{config_path}" — for the top loaded
   APs, capture channel utilization and note any radio above 70% utilization.
4. Call `aos8_get_events` filtered to authentication and association failure events at
   "{config_path}" — count failures per AP and per SSID over the recent window.
5. Call `aos8_get_alarms` with config_path="{config_path}" — surface AAA, RADIUS,
   capacity, or DHCP-pool alarms that correlate with failed connections.

Summarize: scope client total, top-N overloaded APs with their utilization and client
count, dominant failure reasons (auth-fail / DHCP / association-reject), and one
recommended remediation per cause (load-balance, channel-plan, AAA config, DHCP scope).
        """.strip()

    @mcp.prompt
    def aos8_compare_md_config(md_path_1: str, md_path_2: str) -> str:
        """Side-by-side comparison of effective config between two AOS8 MDs/AP-groups."""
        return f"""
Compare AOS8 effective configuration between "{md_path_1}" and "{md_path_2}":

1. Call `aos8_show_command` with command="show configuration effective" and
   config_path="{md_path_1}" — capture the effective config for the first scope.
2. Call `aos8_show_command` with command="show configuration effective" and
   config_path="{md_path_2}" — capture the effective config for the second scope.
3. Call `aos8_get_ssid_profiles` once with config_path="{md_path_1}" and once with
   config_path="{md_path_2}" — diff the SSID profile lists.
4. Call `aos8_get_virtual_aps` for each scope — diff the virtual AP bindings.
5. Call `aos8_get_ap_groups` for each scope — diff the AP-group list and member counts.

Summarize: side-by-side delta table for SSIDs/VAPs/AP-groups, list of objects only on
"{md_path_1}", list of objects only on "{md_path_2}", attribute-level diffs for
common-name objects, and a recommendation on whether the two scopes should be
re-aligned.
        """.strip()

    @mcp.prompt
    def aos8_pre_change_check(config_path: str) -> str:
        """Pre-maintenance checklist before any AOS8 change at a config_path."""
        return f"""
Pre-change checklist for config_path "{config_path}". Run BEFORE any planned
configuration change or maintenance window:

1. Call `aos8_get_alarms` and confirm there are no active Critical or Major alarms at
   or below "{config_path}". If there are, recommend the operator address them first
   or proceed only with explicit acknowledgement.
2. Call `aos8_get_controller_stats` for the master Conductor and any MD under
   "{config_path}" — confirm CPU < 80%, memory < 80%, and uptime is reasonable.
3. Call `aos8_get_audit_trail` for "{config_path}" over the last 24h — surface any
   recent changes the operator may not be aware of (someone else mid-change?).
4. Call `aos8_show_command` with command="show configuration committed" and
   config_path="{config_path}" to capture the current committed-config baseline.
5. Call `aos8_show_command` with command="show configuration pending" and
   config_path="{config_path}" — if there are pending changes, WARN the operator that
   the planned change will be persisted alongside someone else's staged work when
   `aos8_write_memory` is called.

Summarize: GO / NO-GO recommendation, current alarm state, controller resource state,
recent change history, pending-change warning if applicable, and a final reminder that
after the change the operator MUST explicitly call `aos8_write_memory` with the
affected config_path(s) — `aos8_write_memory` is never called automatically; this is
the WRITE-12 contract.
        """.strip()
