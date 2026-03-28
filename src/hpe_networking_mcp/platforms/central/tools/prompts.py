def register(mcp):

    @mcp.prompt
    def network_health_overview() -> str:
        """Full network health overview using the recommended tool workflow."""
        return """
Provide a full network health overview by following these steps:

1. Call `central_get_site_name_id_mapping` to get all sites with health scores, device/client/alert counts.
2. Identify sites with poor or fair health, or notably high alert counts.
3. Call `central_get_sites` with only those site names(maximum 5) to get detailed metrics.
4. Summarize per site: health score, device/client/alert totals, and any notable issues.
5. End with an overall network health assessment and flag any sites requiring immediate attention.
        """.strip()

    @mcp.prompt
    def troubleshoot_site(site_name: str) -> str:
        """Deep-dive troubleshooting workflow for a specific site."""
        return f"""
Troubleshoot the site "{site_name}" by following these steps:

1. Call `central_get_site_name_id_mapping` to verify the site name and get its site_id and current health score.
2. Call `central_get_sites` with site_names=["{site_name}"] to get detailed site metrics.
3. Call `central_get_alerts` with the site_id and status="Active" to get all active alerts. Prioritize by severity (Critical > High > Medium > Low).
4. Call `central_get_devices` with the site_id to get all devices at the site.
5. Summarize: site health, active alert breakdown by category and severity, device status overview, and recommended next steps.
        """.strip()

    @mcp.prompt
    def client_connectivity_check(mac_address: str) -> str:
        """Investigate a client's connectivity status and the health of their site and connected device."""
        return f"""
Check connectivity for the client with MAC address "{mac_address}":

1. Call `central_find_client` with mac_address="{mac_address}" to get the client's current status and connected device serial number.
2. If found, note the site_id from the response.
3. Call `central_get_alerts` with the site_id and status="Active" to check for site-level issues that may affect the client.
4. Call `central_find_device` with the serial_number of the connected device to check device health.
5. Summarize: client status, connection details (type, VLAN, WLAN if wireless), related site/device alerts, and likely root cause if connectivity is failed.
        """.strip()

    @mcp.prompt
    def investigate_device_events(
        serial_number: str, time_range: str = "last_24h"
    ) -> str:
        """Investigate recent events for a specific device to diagnose issues."""
        return f"""
Investigate recent events for device with serial number "{serial_number}" over the {time_range} window:

1. Call `central_find_device` with serial_number="{serial_number}" to confirm the device exists and get its site_id and device_type.
2. Map device_type to the matching context_type: ACCESS_POINT → ACCESS_POINT, SWITCH → SWITCH, GATEWAY → GATEWAY.
3. Call `central_get_events_count` with context_type=<mapped type>, context_identifier="{serial_number}", site_id=<site_id>, time_range="{time_range}" to get a breakdown of event types and volumes.
4. If total > 0, call `central_get_events` with the same parameters to fetch full event details.
5. Summarize: event timeline, dominant event types, any recurring or critical events, and recommended next steps.
        """.strip()

    @mcp.prompt
    def site_event_summary(site_name: str, time_range: str = "last_24h") -> str:
        """Summarize all events at a site to identify patterns and anomalies."""
        return f"""
Summarize events at site "{site_name}" over the {time_range} window:

1. Call `central_get_site_name_id_mapping` to verify the site name and get its site_id.
2. Call `central_get_events_count` with context_type="SITE", context_identifier=<site_id>, site_id=<site_id>, time_range="{time_range}" to get the event breakdown by type and category.
3. If total > 0, call `central_get_events` with the same parameters to fetch full event details.
4. Group events by category and name. Highlight any spikes, repeated errors, or critical events.
5. Summarize: total event count, top event types, notable patterns, and any suggested follow-up actions.
        """.strip()

    @mcp.prompt
    def failed_clients_investigation(site_name: str) -> str:
        """Find and diagnose all failed clients at a site."""
        return f"""
Investigate failed client connections at site "{site_name}":

1. Call `central_get_site_name_id_mapping` to verify the site name and get its site_id.
2. Call `central_get_clients` with site_id=<site_id> and status="Failed" to get all failed clients.
3. If no failed clients are found, report the site is clean.
4. For each failed client (up to 5), call `central_find_device` with the connected device serial number to check device health.
5. Call `central_get_alerts` with site_id=<site_id> and category="Clients" to check for site-level client alerts.
6. Summarize: number of failed clients, connection types affected (wired vs wireless), common failure patterns, related device or site alerts, and likely root causes.
        """.strip()

    @mcp.prompt
    def site_client_overview(site_name: str) -> str:
        """Overview of all client connectivity at a site, broken down by type and status."""
        return f"""
Provide a client connectivity overview for site "{site_name}":

1. Call `central_get_site_name_id_mapping` to verify the site name and get its site_id.
2. Call `central_get_clients` with site_id=<site_id> to get all clients at the site.
3. Break down clients by: connection type (Wired vs Wireless), status (Connected vs Failed), and VLAN.
4. For wireless clients, note WLAN distribution and any clients on unusual bands or security types.
5. Summarize: total client count, connected vs failed breakdown, any anomalies, and recommendations.
        """.strip()

    @mcp.prompt
    def device_type_health(site_name: str, device_type: str) -> str:
        """Health check for all devices of a specific type at a site."""
        return f"""
Check the health of all {device_type} devices at site "{site_name}":

1. Call `central_get_site_name_id_mapping` to verify the site name and get its site_id.
2. Call `central_get_devices` with site_id=<site_id> and device_type="{device_type}" to list all matching devices.
3. Call `central_get_alerts` with site_id=<site_id> and device_type matching the {device_type} display name to get relevant active alerts.
4. For any device with associated alerts, call `central_get_events_count` with the device serial number and time_range="last_24h" to check recent event activity.
5. Summarize: total device count, provisioned vs unprovisioned, active alert breakdown by severity, devices with high event activity, and recommended actions.
        """.strip()

    @mcp.prompt
    def critical_alerts_review() -> str:
        """Review all active critical alerts across the network."""
        return """
Review all active critical alerts across the network:

1. Call `central_get_site_name_id_mapping` to get all sites with their site_ids and alert counts.
2. For each site with total_alerts > 0, call `central_get_alerts` with the site_id and status="Active" to get all active alerts.
3. Filter to Critical severity only. Group by site and category.
4. Identify sites with the highest concentration of critical alerts.
5. Summarize: total critical alert count across the network, top affected sites, most common alert names by category, and recommended immediate actions.
        """.strip()

    @mcp.prompt
    def compare_site_health(site_names: list[str]) -> str:
        """Compare health metrics across multiple sites side by side."""
        sites_str = ", ".join(f'"{s}"' for s in site_names)
        return f"""
Compare health across sites: {sites_str}

1. Call `central_get_site_name_id_mapping` to verify all site names and get their site_ids and health scores.
2. Call `central_get_sites` with site_names={list(site_names)} to get detailed metrics for each site.
3. For each site, call `central_get_alerts` with the site_id and status="Active" to get active alert counts by severity.
4. Present a side-by-side comparison table: site name, health score, device count, client count, alert breakdown (Critical/High/Medium/Low).
5. Rank sites from worst to best health.
        """.strip()
