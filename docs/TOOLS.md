# Tool Reference

Complete reference for all tools registered by the HPE Networking MCP Server.
Tools are namespaced by platform: `mist_*` (Juniper Mist), `central_*` (Aruba Central),
and `greenlake_*` (HPE GreenLake).

## Overview

| Platform | Read-Only Tools | Write Tools | Prompts | Total |
|----------|----------------|-------------|---------|-------|
| Juniper Mist | 31 | 4 | 2 | 37 |
| Aruba Central | 42 | 3 | 12 | 57 |
| HPE GreenLake (static mode) | 10 | -- | -- | 10 |
| HPE GreenLake (dynamic mode) | 3 | -- | -- | 3 |

Write tools (`mist_update_*`, `mist_change_*`) are disabled by default. Set
`ENABLE_MIST_WRITE_TOOLS=true` or `ENABLE_CENTRAL_WRITE_TOOLS=true` to enable them per platform.

GreenLake supports two mutually exclusive tool modes controlled by
`GREENLAKE_TOOL_MODE`:

- **static** (default) -- 10 dedicated tools, one per API endpoint.
- **dynamic** -- 3 meta-tools that discover, inspect, and invoke any of the
  10 endpoints at runtime.

---

## Juniper Mist (35 tools + 2 prompts)

### Account and Organization

#### `mist_get_self`

> Retrieve information about the current user and account.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `account_info`, `api_usage`, or `login_failures`. |

#### `mist_get_org_or_site_info`

> Search information about the organizations or sites.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| info_type | str | Yes | `org` or `site`. |
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. If omitted with info_type=site, lists all sites. |

#### `mist_get_org_licenses`

> Retrieve information about the licenses of an organization.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| response_type | str | Yes | `claim_status`, `by_site`, or `summary`. |

#### `mist_get_site_health`

> Get a health overview across all sites in the organization.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |

#### `mist_get_next_page`

> Retrieve the next page of results using the `_next` URL from a previous response.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | str | Yes | The `_next` URL from a previous response. |

### Configuration

#### `mist_get_configuration_objects`

> Retrieve configuration objects (WLANs, profiles, templates, devices) from an org or site.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| object_type | str | Yes | Object type enum (e.g. `org_wlans`, `site_devices`). |
| site_id | UUID | No | Site ID. Required for `site_*` object types. |
| object_id | UUID | No | Retrieve a single object by ID. |
| name | str | No | Filter by name. Case-insensitive, supports `*` wildcards. |
| computed | bool | No | Include inherited settings. For `org_sites`, `site_devices`, `site_wlans`. |
| limit | int | No | Default: 20. Max: 1000. |

#### `mist_get_configuration_object_schema`

> Retrieve the JSON schema for a Mist configuration object type from the OpenAPI spec.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| schema_name | str | Yes | Name of the configuration object schema. |
| verbose | bool | No | Default: false. True returns full schema with all constraints. |

#### `mist_search_device_config_history`

> Search for entries in device config history to track configuration changes over time.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| query_type | str | Yes | `history` or `last_configs`. |
| device_type | str | Yes | `ap`, `switch`, or `gateway`. |
| device_mac | str | No | MAC address of the device. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

#### `mist_get_wlans`

> List WLANs/SSIDs configured in the organization or a specific site.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. If provided, returns WLANs for this site only. |

### Clients

#### `mist_search_client`

> Search for clients across an organization or site by type, MAC, hostname, IP, and more.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| client_type | str | Yes | `wan`, `wired`, `wireless`, or `nac`. |
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. |
| device_mac | str | No | MAC of the connected AP or switch. Supports `*` wildcards. |
| band | str | No | `24`, `5`, or `6`. Wireless clients only. |
| ssid | str | No | SSID name. Wireless or NAC clients only. |
| mac | str | No | Client MAC address. Supports `*` wildcards. |
| hostname | str | No | Client hostname. Supports `*` wildcards. Not for WAN/wired. |
| ip | str | No | Client IP address. Supports `*` wildcards. Not for NAC. |
| text | str | No | Free text search. Not for WAN clients. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

#### `mist_search_guest_authorization`

> Search for guest authorization entries in an organization or site.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scope | str | Yes | `org` or `site`. |
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. Required when scope is `site`. |
| guest_mac | str | No | MAC address of the guest. |
| wlan_id | UUID | No | WLAN ID to filter by. |
| auth_method | str | No | Authentication method to filter by. |
| ssid | str | No | SSID to filter by. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

### Device Management

#### `mist_search_device`

> Search for a device in the organization inventory by serial, model, MAC, type, or status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. |
| serial | str | No | Serial number filter. |
| model | str | No | Device model. Supports `*` wildcards. |
| mac | str | No | MAC address. Supports `*` wildcards. |
| version | str | No | Firmware version filter. |
| vc_mac | str | No | Virtual chassis MAC address filter. |
| device_type | str | No | `ap`, `switch`, or `gateway`. |
| status | str | No | `connected` or `disconnected`. |
| text | str | No | Free text search across device attributes. Supports `*` wildcards. |
| limit | int | No | Default: 20. |

#### `mist_get_ap_details`

> Get detailed AP information including model, firmware, radio config, IP, and status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| device_id | UUID | Yes | AP device ID (use `mist_search_device` to find it). |

#### `mist_get_switch_details`

> Get detailed switch information including model, firmware, port config, IP, and status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| device_id | UUID | Yes | Switch device ID (use `mist_search_device` to find it). |

#### `mist_get_gateway_details`

> Get detailed gateway information including model, firmware, interfaces, tunnels, and status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| device_id | UUID | Yes | Gateway device ID (use `mist_search_device` to find it). |

#### `mist_bounce_switch_port`

> Bounce ports on a Juniper EX switch to reset link state. Only bounce edge/access ports — never uplinks, stack, or aggregation ports.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| device_id | UUID | Yes | Device ID of the EX switch (use `mist_search_device` to find it). |
| ports | str | Yes | Comma-separated port names (e.g., `ge-0/0/0,ge-0/0/1`). Juniper format: `ge-0/0/0` (1G), `mge-0/0/0` (multi-gig). |

### Events, Alarms, and Audit Logs

#### `mist_search_events`

> Search for events from devices, MX Edge, clients, roaming, or rogue sources.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| event_source | str | Yes | `device`, `mxedge`, `wan_client`, `wireless_client`, `nac_client`, `roaming`, `rogue`. |
| org_id | UUID | Yes | Organization ID. |
| event_type | str | No | Comma-separated event types. Use `mist_get_constants` to discover types. |
| site_id | UUID | No | Site ID. Required for `roaming` and `rogue` sources. |
| mac | str | No | MAC address filter (device/WAN/NAC/rogue events). |
| text | str | No | Text search (device/NAC events only). |
| ssid | str | No | SSID filter (wireless/NAC/rogue events only). |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

#### `mist_search_audit_logs`

> Search audit logs for the current account or an organization.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scope | str | Yes | `self` or `org`. |
| org_id | UUID | No | Organization ID. Required when scope is `org`. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| message | str | No | Message text filter (partial search). |
| limit | int | No | Default: 20. |

#### `mist_search_alarms`

> Search for raised alarms in an organization or site with filtering by group, severity, and type.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| scope | str | Yes | `org`, `site`, or `suppressed`. |
| site_id | UUID | No | Site ID. Required when scope is `site`. |
| group | str | No | `infrastructure`, `marvis`, or `security`. org/site scope only. |
| severity | str | No | `critical`, `major`, `minor`, `warn`, or `info`. org/site scope only. |
| alarm_type | str | No | Comma-separated alarm types. Use `mist_get_constants` to discover types. |
| acked | bool | No | Filter acknowledged (true) or unacknowledged (false) alarms. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

### Marvis AI Troubleshooting

#### `mist_troubleshoot`

> Troubleshoot sites, devices, or clients using Marvis AI. Requires Marvis subscription license.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| troubleshoot_type | str | Yes | `wan`, `wired`, or `wireless`. |
| site_id | UUID | No | Site ID. |
| mac | str | No | MAC address of the client or device. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |

### Constants

#### `mist_get_constants`

> Retrieve Mist platform constants (event types, alarm definitions, device models, etc.).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| object_type | str | Yes | One of: `fingerprint_types`, `insight_metrics`, `license_types`, `webhook_topics`, `device_models`, `device_events`, `mxedge_models`, `alarm_definitions`, `client_events`, `mxedge_events`, `nac_events`. |

### NAC

#### `mist_search_nac_user_macs`

> Search for NAC user MAC addresses used for MAC Authentication with Juniper Mist NAC.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| usermac_id | str | No | ID of a specific User MAC to retrieve. |
| mac | str | No | Client MAC address. Supports `*` wildcards. |
| labels | list[str] | No | Labels to filter by (all must match). |
| limit | int | No | Default: 20. |

### Insight Metrics

#### `mist_get_insight_metrics`

> Get insight metrics for a site, client, AP, gateway, MX Edge, or switch.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| object_type | str | Yes | `site`, `client`, `ap`, `gateway`, `mxedge`, or `switch`. |
| metric | str | Yes | Metric name. Use `mist_get_constants` with `insight_metrics` to discover. |
| mac | str | No | MAC address. Required for client, ap, mxedge, switch. |
| device_id | UUID | No | Device ID. Required for gateway. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| duration | str | No | Duration shorthand (e.g. `1d`, `1h`, `10m`). |
| interval | str | No | Aggregation interval (e.g. `1h`, `1d`). |
| page | int | No | Page number for pagination. |
| limit | int | No | Default: 20. |

### Rogue Detection

#### `mist_list_rogue_devices`

> List rogue APs or clients detected at a site.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| rogue_type | str | Yes | `ap` or `client`. |
| rogue_ap_type | str | No | `honeypot`, `lan`, `others`, or `spoof`. AP type only. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

### Radio Resource Management (RRM)

#### `mist_get_site_rrm_info`

> Retrieve RRM information: channel planning, considerations, neighbors, or events.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| rrm_info_type | str | Yes | `current_channel_planning`, `current_rrm_considerations`, `current_rrm_neighbors`, or `events`. |
| device_id | UUID | No | AP device ID. Required for `current_rrm_considerations`. |
| band | str | No | `24`, `5`, or `6`. Required for considerations and neighbors. |
| start | int | No | Start of time range (epoch seconds). Events only. |
| end | int | No | End of time range (epoch seconds). Events only. |
| duration | str | No | Duration shorthand. Events only. |
| limit | int | No | Default: 200. Events only. |
| page | int | No | Default: 1. Events only. |

### Service Level Expectations (SLE)

#### `mist_get_site_sle`

> Get SLE data for a site scope including summaries, impact, impacted entities, and histograms.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| scope | str | Yes | `client`, `ap`, `gateway`, `mxedge`, `switch`, or `site`. |
| scope_id | str | Yes | ID of the scoped object. |
| metric | str | Yes | SLE metric name. |
| object_type | str | Yes | `summary`, `impact_summary`, `summary_trend`, `impacted_applications`, `impacted_aps`, `impacted_gateways`, `impacted_interfaces`, `impacted_switches`, `impacted_wireless_clients`, `impacted_wired_clients`, `impacted_chassis`, `histogram`, `classifier_summary_trend`, or `threshold`. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| classifier | str | No | Classifier name. Required for `classifier_summary_trend`. |
| duration | str | No | Duration shorthand (e.g. `1d`, `1h`). |

#### `mist_list_site_sle_info`

> List available SLE metrics or classifiers for a site scope.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| query_type | str | Yes | `metrics` or `classifiers`. |
| scope | str | Yes | `site`, `ap`, `client`, `gateway`, or `switch`. |
| scope_id | str | Yes | ID of the scoped object. |
| metric | str | No | SLE metric name. Required when query_type is `classifiers`. |

#### `mist_get_org_sle`

> Get organization-level SLE data (all/worst sites, MX Edges).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| metric | str | Yes | SLE metric name. |
| sle | str | No | SLE type to retrieve. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

#### `mist_get_org_sites_sle`

> Get SLE summary across all organization sites.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| sle | str | Yes | `wifi`, `wired`, or `wan`. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

### Statistics

#### `mist_get_stats`

> Retrieve statistics for org, sites, devices, MX Edges, BGP, OSPF, peer paths, ports, or clients.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| stats_type | str | Yes | `org`, `sites`, `org_mxedges`, `org_devices`, `org_bgp`, `org_ospf`, `org_peer_paths`, `org_ports`, `site_mxedges`, `site_wireless_clients`, `site_devices`, `site_bgp`, `site_ospf`, or `site_ports`. |
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. Required for `site_*` stats types. |
| device_type | str | No | `ap`, `switch`, or `gateway`. For `org_devices`/`site_devices` only. |
| object_id | str | No | Object ID or MAC to filter by (format varies by stats_type). |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

### Upgrades

#### `mist_list_upgrades`

> Retrieve upgrade jobs or available firmware versions for the organization.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| device_type | str | Yes | `ap`, `switch`, `srx`, `mxedge`, `ssr`, `available_device_versions`, or `available_ssr_versions`. |
| upgrade_id | UUID | No | Specific upgrade job ID. For ap/switch/srx/mxedge/ssr only. |
| firmware_type | str | No | `ap`, `switch`, or `gateway`. For `available_device_versions` only. |
| model | str | No | Device model filter. For `available_device_versions` only. |
| channel | str | No | `alpha`, `beta`, or `stable`. For `available_ssr_versions` only. |
| mac | str | No | SSR MAC address(es). For `available_ssr_versions` only. |

### Write Tools (disabled by default)

#### `mist_update_site_configuration_objects`

> Update or create a configuration object for a site. Requires `ENABLE_MIST_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| object_type | str | Yes | `devices`, `evpn_topologies`, `psks`, `webhooks`, `wlans`, `wxrules`, or `wxtags`. |
| object_id | UUID | No | ID of the object to update. Omit to create new. |
| body | dict | Yes | Configuration object body. |

#### `mist_update_org_configuration_objects`

> Update or create a configuration object for an organization. Requires `ENABLE_MIST_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| object_type | str | Yes | `alarmtemplates`, `sites`, `wlans`, `sitegroups`, `avprofiles`, `deviceprofiles`, `gatewaytemplates`, `idpprofiles`, `aamwprofiles`, `nactags`, `nacrules`, `networktemplates`, `networks`, `psks`, `rftemplates`, `services`, `servicepolicies`, `sitetemplates`, `vpns`, `webhooks`, `wlantemplates`, `wxrules`, or `wxtags`. |
| object_id | UUID | No | ID of the object to update. Omit to create new. |
| body | dict | Yes | Configuration object body. |

#### `mist_change_site_configuration_objects`

> Create, update, or delete a site-level configuration object. Requires `ENABLE_MIST_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, or `delete`. |
| site_id | UUID | Yes | Site ID. |
| object_type | str | Yes | `devices`, `evpn_topologies`, `psks`, `webhooks`, `wlans`, `wxrules`, or `wxtags`. |
| object_id | UUID | No | ID of the object to update or delete. |
| body | dict | No | Configuration object body. Required for create/update. |

#### `mist_change_org_configuration_objects`

> Create, update, or delete an org-level configuration object. Requires `ENABLE_MIST_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, or `delete`. |
| org_id | UUID | Yes | Organization ID. |
| object_type | str | Yes | `alarmtemplates`, `sites`, `wlans`, `sitegroups`, `avprofiles`, `deviceprofiles`, `gatewaytemplates`, `idpprofiles`, `aamwprofiles`, `nactags`, `nacrules`, `networktemplates`, `networks`, `psks`, `rftemplates`, `services`, `servicepolicies`, `sitetemplates`, `vpns`, `webhooks`, `wlantemplates`, `wxrules`, or `wxtags`. |
| object_id | UUID | No | ID of the object to update or delete. |
| body | dict | No | Configuration object body. Required for create/update. |

### Guided Prompts

| Prompt | Parameters | Description |
|--------|------------|-------------|
| `provision_site_from_template` | source_site_name, target_site_name, target_address | Clone a site's configuration using org-level templates. Never copies site-level WLANs. |
| `bulk_provision_sites` | source_site_name, site_list_description | Bulk provision multiple sites from a template site. Analyzes source config once, creates each site with template assignments. |

---

## Aruba Central (45 tools + 12 prompts)

### Sites

#### `central_get_sites`

> Returns detailed metrics for one or more sites. Prefer calling with a site_names filter.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_names | list[str] | No | Site names to filter by (exact match). Omit for all sites. |

#### `central_get_site_name_id_mapping`

> Returns a lightweight mapping of all site names to IDs, health scores, and counts.

No parameters. Returns a dict sorted by health score (worst first).

### Devices

#### `central_get_devices`

> Returns a filtered list of devices using OData v4.0 filter syntax.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | No | Site ID or comma-separated list. |
| device_type | str | No | `ACCESS_POINT`, `SWITCH`, or `GATEWAY`. Comma-separated for multiple. |
| device_name | str | No | Device display name. Comma-separated for multiple. |
| serial_number | str | No | Device serial number. Comma-separated for multiple. |
| model | str | No | Device model (e.g. `AP-735-RWF1`). |
| device_function | str | No | Device function classification. |
| is_provisioned | bool | No | True for provisioned devices only. |
| site_assigned | bool | No | True for devices assigned to a site only. |
| sort | str | No | Sort expression (e.g. `deviceName asc, model desc`). |

#### `central_find_device`

> Find a single device by serial number or name. Returns one device or an error message.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | No | Device serial number (preferred). |
| device_name | str | No | Device display name. Provide only one identifier. |

### Device Monitoring

#### `central_get_ap_details`

> Get detailed monitoring data for a specific AP (name, model, status, firmware, clients, radios).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |

#### `central_get_switch_details`

> Get detailed monitoring data for a specific switch (name, model, status, health reasons).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Switch serial number. |

#### `central_get_gateway_details`

> Get detailed monitoring data for a specific gateway (interfaces, tunnels, health).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |

### Clients

#### `central_get_clients`

> Returns a filtered list of clients using OData v4.0 filter syntax.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | No | Site ID. |
| site_name | str | No | Site name. |
| serial_number | str | No | Serial number of the connected device. |
| connection_type | str | No | `Wired` or `Wireless`. |
| status | str | No | `Connected` or `Failed`. |
| wlan_name | str | No | WLAN name filter (wireless only). |
| vlan_id | str | No | VLAN ID filter. |
| tunnel_type | str | No | `Port-based`, `User-based`, or `Overlay`. |
| start_query_time | str | No | Start of time window (ISO 8601). |
| end_query_time | str | No | End of time window (ISO 8601). |

#### `central_find_client`

> Find a single client by MAC address.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mac_address | str | Yes | Client MAC address. |

### Alerts

#### `central_get_alerts`

> Returns a filtered, paginated list of alerts for a specific site. Requires site_id.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | Yes | Site ID. Obtain from `central_get_sites`. |
| status | str | No | Default: `Active`. Also `Cleared` or `Deferred`. |
| device_type | str | No | `Access Point`, `Gateway`, `Switch`, or `Bridge`. |
| category | str | No | `Clients`, `System`, `LAN`, `WLAN`, `WAN`, `Cluster`, `Routing`, or `Security`. |
| sort | str | No | Default: `severity desc`. |
| limit | int | No | Default: 50. Max: 100. |
| cursor | int | No | Pagination cursor from previous `next_cursor`. |

### Events

#### `central_get_events`

> Retrieve events for a context (site, device, or client) within a time range.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| context_type | str | Yes | `SITE`, `ACCESS_POINT`, `SWITCH`, `GATEWAY`, `WIRELESS_CLIENT`, `WIRED_CLIENT`, or `BRIDGE`. |
| context_identifier | str | Yes | Site ID, device serial, or client MAC. |
| site_id | str | Yes | Site ID to scope events. |
| time_range | str | No | Default: `last_1h`. Options: `last_1h`, `last_6h`, `last_24h`, `last_7d`, `last_30d`, `today`, `yesterday`. |
| start_time | str | No | RFC 3339 format. Overrides time_range with end_time. |
| end_time | str | No | RFC 3339 format. Overrides time_range with start_time. |
| search | str | No | Search by name, serial, hostname, or MAC. |
| limit | int | No | Default: 50. Max: 100. |
| cursor | int | No | Pagination cursor from previous `next_cursor`. |

#### `central_get_events_count`

> Return event count breakdown for a context without fetching full details.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| context_type | str | Yes | `SITE`, `ACCESS_POINT`, `SWITCH`, `GATEWAY`, `WIRELESS_CLIENT`, `WIRED_CLIENT`, or `BRIDGE`. |
| context_identifier | str | Yes | Site ID, device serial, or client MAC. |
| site_id | str | Yes | Site ID to scope events. |
| time_range | str | No | Default: `last_1h`. |
| start_time | str | No | RFC 3339 format. |
| end_time | str | No | RFC 3339 format. |

### WLANs

#### `central_get_wlans`

> List all WLANs/SSIDs configured in Aruba Central.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | No | Filter WLANs by site ID. |
| serial_number | str | No | Filter WLANs served by a specific AP. |
| filter | str | No | OData filter string. |
| sort | str | No | Sort expression (e.g. `essid asc`). |
| limit | int | No | Default: 100. |

### Audit Logs

#### `central_get_audit_logs`

> Retrieve audit logs within a time window (user actions, config changes, system events).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| start_at | str | Yes | Start of time window in epoch milliseconds. |
| end_at | str | Yes | End of time window in epoch milliseconds. |
| filter | str | No | OData filter expression. |
| sort | str | No | Sort order (e.g. `+timestamp` or `-timestamp`). |
| limit | int | No | Default: 200. Max: 200. |
| offset | int | No | Default: 1. Page number. |

#### `central_get_audit_log_detail`

> Get the full detail of a single audit log entry.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | str | Yes | Audit log entry ID. |

### Statistics

#### `central_get_ap_stats`

> Get performance statistics for a specific AP (radio stats, client counts, throughput).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |
| start_time | str | No | Start of time window in epoch seconds. |
| end_time | str | No | End of time window in epoch seconds. |
| duration | str | No | Duration shorthand (e.g. `3H`, `1D`, `1W`). |

#### `central_get_ap_utilization`

> Get AP utilization data for CPU, memory, or PoE.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |
| metric | str | Yes | `cpu`, `memory`, or `poe`. |
| start_time | str | No | Start of time window in epoch seconds. |
| end_time | str | No | End of time window in epoch seconds. |
| duration | str | No | Duration shorthand (e.g. `3H`, `1D`, `1W`). |

#### `central_get_gateway_stats`

> Get performance statistics for a specific gateway (interface stats, tunnels, throughput).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| start_time | str | No | Start of time window in epoch seconds. |
| end_time | str | No | End of time window in epoch seconds. |
| duration | str | No | Duration shorthand (e.g. `3H`, `1D`, `1W`). |

#### `central_get_gateway_utilization`

> Get gateway utilization data for CPU or memory.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| metric | str | Yes | `cpu` or `memory`. |
| start_time | str | No | Start of time window in epoch seconds. |
| end_time | str | No | End of time window in epoch seconds. |
| duration | str | No | Duration shorthand (e.g. `3H`, `1D`, `1W`). |

#### `central_get_gateway_wan_availability`

> Get WAN availability data for a gateway (uplink percentages and downtime windows).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| start_time | str | No | Start of time window in epoch seconds. |
| end_time | str | No | End of time window in epoch seconds. |
| duration | str | No | Duration shorthand (e.g. `3H`, `1D`, `1W`). |

#### `central_get_tunnel_health`

> Get tunnel health summary for a gateway (VPN/overlay tunnel status and latency).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |

### Applications

#### `central_get_applications`

> Get application usage data for a site (traffic volume, client counts, categorization).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | Yes | Site ID. |
| start_query_time | str | Yes | Start of time window in epoch milliseconds. |
| end_query_time | str | Yes | End of time window in epoch milliseconds. |
| limit | int | No | Default: 1000. |
| offset | int | No | Default: 0. |
| client_id | str | No | Filter to a specific client ID. |
| filter | str | No | OData filter expression. |
| sort | str | No | Sort order. |

### Troubleshooting

#### `central_ping`

> Initiate a ping test from a device to a destination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Device serial number. |
| destination | str | Yes | IP address or hostname to ping. |
| device_type | str | Yes | `ap`, `cx`, or `gateway`. |
| count | int | No | Number of pings to send. |
| packet_size | int | No | Ping packet size in bytes. |

#### `central_traceroute`

> Initiate a traceroute from a device to a destination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Device serial number. |
| destination | str | Yes | IP address or hostname. |
| device_type | str | Yes | `ap`, `cx`, or `gateway`. |

#### `central_cable_test`

> Initiate a cable test on switch ports (cable status and length).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Switch serial number. |
| device_type | str | Yes | `aos-s` or `cx`. |
| ports | str | Yes | Comma-separated port list (e.g. `1/1/1,1/1/2`). |

#### `central_show_commands`

> Execute show commands on a device and return the output.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Device serial number. |
| device_type | str | Yes | `aos-s`, `cx`, or `gateways`. |
| commands | str | Yes | Comma-separated show commands (e.g. `show version,show interfaces`). |

#### `central_disconnect_users_ssid`

> Disconnect all users from a specific SSID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |
| ssid | str | Yes | SSID name to disconnect all users from. |

#### `central_disconnect_users_ap`

> Disconnect all users from a specific AP.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |

#### `central_disconnect_client_ap`

> Disconnect a specific client by MAC address from an AP.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |
| mac_address | str | Yes | Client MAC address. |

#### `central_disconnect_client_gateway`

> Disconnect a specific client by MAC address from a gateway.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| mac_address | str | Yes | Client MAC address. |

#### `central_disconnect_clients_gateway`

> Disconnect all clients from a gateway.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |

#### `central_port_bounce_switch`

> Bounce a port on a CX switch to reset link state.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Switch serial number. |
| ports | str | Yes | Comma-separated port list in CX format (e.g. `1/1/1,1/1/2`). |

#### `central_poe_bounce_switch`

> Cycle PoE power on a CX switch port to reset a connected PoE device.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Switch serial number. |
| ports | str | Yes | Comma-separated port list in CX format (e.g. `1/1/1,1/1/2`). |

#### `central_port_bounce_gateway`

> Bounce a port on a gateway to reset link state.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| ports | str | Yes | Comma-separated port list. |

#### `central_poe_bounce_gateway`

> Cycle PoE power on a gateway port to reset a connected PoE device.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| ports | str | Yes | Comma-separated port list. |

### Write Tools (disabled by default)

#### `central_manage_site`

> Create, update, or delete a site in Aruba Central. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, or `delete`. |
| payload | dict | Yes | Site payload. All values must use full names (no abbreviations). For create: `address`, `name`, `city`, `state`, `country`, `zipcode`, and `timezone` (object with `timezoneName`, `timezoneId`, `rawOffset` in ms) are required. |
| site_id | str | No | Site ID. Required for update and delete. |

#### `central_manage_site_collection`

> Create, update, or delete a site collection in Aruba Central. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, or `delete`. |
| payload | dict | Yes | Site collection payload. For create: `scopeName` required. Optional: `description`, `siteIds`. |
| collection_id | str | No | Collection ID. Required for update and delete. |

#### `central_manage_device_group`

> Create, update, or delete a device group in Aruba Central. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, or `delete`. |
| payload | dict | Yes | Device group payload. For create: `scopeName` required. Optional: `description`. |
| group_id | str | No | Group ID. Required for update and delete. |

### Guided Prompts

Prompts are pre-built workflows that chain multiple tools together. They guide the
LLM through a recommended sequence of tool calls for common network operations.

| Prompt | Parameters | Description |
|--------|-----------|-------------|
| `network_health_overview` | (none) | Full network health overview across all sites. |
| `troubleshoot_site` | site_name | Deep-dive troubleshooting for a specific site. |
| `client_connectivity_check` | mac_address | Investigate a client's connectivity and related site health. |
| `investigate_device_events` | serial_number, time_range | Investigate recent events for a specific device. |
| `site_event_summary` | site_name, time_range | Summarize all events at a site to identify patterns. |
| `failed_clients_investigation` | site_name | Find and diagnose all failed clients at a site. |
| `site_client_overview` | site_name | Overview of all client connectivity at a site. |
| `device_type_health` | site_name, device_type | Health check for all devices of a type at a site. |
| `critical_alerts_review` | (none) | Review all active critical alerts across the network. |
| `compare_site_health` | site_names (list) | Compare health metrics across multiple sites. |
| `scope_configuration_overview` | scope_name | View committed configuration resources at a scope with category grouping. |
| `scope_effective_config` | scope_name | View effective (inherited + committed) configuration as a layered inheritance view. |

---

## HPE GreenLake

### Dynamic Mode (3 tools)

When `GREENLAKE_TOOL_MODE=dynamic`, these three meta-tools replace the 10 static tools.
They allow the LLM to discover and invoke any GreenLake endpoint at runtime.

#### `greenlake_list_endpoints`

> List all available GreenLake API endpoints across all 5 services.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter | str | No | Case-insensitive keyword filter (e.g. `devices`). |

Returns endpoint identifiers in `METHOD:PATH` format.

#### `greenlake_get_endpoint_schema`

> Get detailed parameter schema for a specific GreenLake API endpoint.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| endpoint | str | Yes | Endpoint identifier (e.g. `GET:/audit-log/v1/logs`). |
| include_examples | bool | No | Default: false. Include example parameter values. |

#### `greenlake_invoke_endpoint`

> Execute any GreenLake GET API endpoint dynamically with parameter validation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| endpoint | str | Yes | Endpoint identifier (e.g. `GET:/devices/v1/devices`). |
| params | dict | No | Request parameters. Path params substituted into URL; query params appended. |

Available endpoints (10 total):

| Endpoint | Description |
|----------|-------------|
| `GET:/audit-log/v1/logs` | List audit logs |
| `GET:/audit-log/v1/logs/{id}/detail` | Get audit log detail |
| `GET:/devices/v1/devices` | List devices |
| `GET:/devices/v1/devices/{id}` | Get device by ID |
| `GET:/identity/v1/users` | List users |
| `GET:/identity/v1/users/{id}` | Get user by ID |
| `GET:/subscriptions/v1/subscriptions` | List subscriptions |
| `GET:/subscriptions/v1/subscriptions/{id}` | Get subscription by ID |
| `GET:/workspaces/v1/workspaces/{workspaceId}` | Get workspace |
| `GET:/workspaces/v1/workspaces/{workspaceId}/contact` | Get workspace contact |

### Static Mode (10 tools)

When `GREENLAKE_TOOL_MODE=static` (default), the following dedicated tools are registered.

#### `greenlake_get_audit_logs`

> Retrieve GreenLake audit logs with optional OData filtering and pagination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter | str | No | OData filter expression. Values in single quotes. |
| select | str | No | Comma-separated properties to include. |
| all | str | No | Free-text search across all properties. |
| limit | int | No | Default: 50. Max: 2000. |
| offset | int | No | Zero-based offset for pagination. |

#### `greenlake_get_audit_log_details`

> Get additional detail for a single GreenLake audit log entry.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | str | Yes | Audit log record ID (must have `hasDetails=true`). |

#### `greenlake_get_devices`

> List devices managed in a GreenLake workspace with filtering, sorting, and pagination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter | str | No | OData filter expression. Values in single quotes. |
| filter_tags | str | No | Tag filter expression. |
| sort | str | No | Sort expressions (e.g. `serialNumber,macAddress desc`). |
| select | list[str] | No | Property names to include. |
| limit | int | No | Default: 2000. |
| offset | int | No | Zero-based offset for pagination. |

#### `greenlake_get_device_by_id`

> Get details on a specific GreenLake device by its resource ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | str | Yes | Device resource ID. |

#### `greenlake_get_subscriptions`

> List subscriptions in a GreenLake workspace with filtering, sorting, and pagination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter | str | No | OData filter expression. Values in single quotes. |
| filter_tags | str | No | Tag filter expression. |
| sort | str | No | Sort expressions. |
| select | list[str] | No | Property names to include. |
| limit | int | No | Default: 50. |
| offset | int | No | Zero-based offset for pagination. |

#### `greenlake_get_subscription_details`

> Get detailed information for a single GreenLake subscription by ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | str | Yes | Subscription ID. |

#### `greenlake_get_users`

> List users in a GreenLake workspace with OData filtering and pagination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter | str | No | OData filter expression. Values in single quotes. |
| limit | int | No | Default: 300. Max: 600. |
| offset | int | No | Pagination offset (number of pages to skip). |

#### `greenlake_get_user_details`

> Retrieve a single GreenLake user by user ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | str | Yes | User ID. |

#### `greenlake_get_workspace`

> Retrieve basic workspace information for a given GreenLake workspace ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspaceId | str | Yes | Workspace ID. |

#### `greenlake_get_workspace_details`

> Retrieve contact information for a GreenLake workspace.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspaceId | str | Yes | Workspace ID. |
