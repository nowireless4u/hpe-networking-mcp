# Tool Reference

Complete reference for all tools registered by the HPE Networking MCP Server.
Tools are namespaced by platform: `mist_*` (Juniper Mist), `central_*` (Aruba Central),
`greenlake_*` (HPE GreenLake), `clearpass_*` (Aruba ClearPass), and `apstra_*`
(Juniper Apstra).

## Overview

| Platform | Read-Only Tools | Write Tools | Prompts | Total |
|----------|----------------|-------------|---------|-------|
| Juniper Mist | 31 | 4 | 2 | 37 |
| Aruba Central | 60 | 13 | 12 | 85 |
| Aruba ClearPass | 55 | 72 | -- | 127 |
| Juniper Apstra | 12 | 7 | -- | 19 |
| Cross-Platform | 2 | 1 | 3 | 6 |
| HPE GreenLake (static mode) | 10 | -- | -- | 10 |
| HPE GreenLake (dynamic mode) | 3 | -- | -- | 3 |

Write tools are disabled by default per platform. Enable them with environment variables:
`ENABLE_MIST_WRITE_TOOLS=true`, `ENABLE_CENTRAL_WRITE_TOOLS=true`,
`ENABLE_CLEARPASS_WRITE_TOOLS=true`, or `ENABLE_APSTRA_WRITE_TOOLS=true`.

## Tool modes (`MCP_TOOL_MODE`)

Two tool-exposure modes, selectable via the `MCP_TOOL_MODE` env var:

- **`static`** (current default) — every platform tool is registered as its own
  FastMCP tool. Easiest to browse and pin; largest tool-list footprint.
- **`dynamic`** — platforms that have migrated to the shared meta-tool pattern
  expose exactly three tools per platform: `<platform>_list_tools`,
  `<platform>_get_tool_schema`, `<platform>_invoke_tool`. The model discovers
  tools at call time rather than having every schema dumped into the system
  prompt. Saves context tokens, especially on local LLMs.

Dynamic-mode migration status (phased per [#157](https://github.com/nowireless4u/hpe-networking-mcp/issues/157)):

| Platform | Dynamic mode available |
|---|---|
| Juniper Apstra | ✅ yes (Phase 0) |
| Juniper Mist | ✅ yes (Phase 1) |
| Aruba Central | ✅ yes (Phase 2) |
| Aruba ClearPass | ✅ yes (Phase 3) |
| HPE GreenLake | ✅ yes (Phase 4 — unified with the shared tool-name-dispatch pattern) |

When a platform that has **not** migrated yet runs under `MCP_TOOL_MODE=dynamic`,
its individual tools stay visible (no Visibility transform hides them) so the
server stays usable until every migration lands in Phase 6.

## Cross-platform static tools

Always registered regardless of `MCP_TOOL_MODE`:

- **`health`** — reports per-platform status in one call. Accepts
  `platform: str | list[str] | None`. Replaces `apstra_health` (removed
  in Phase 0) and `clearpass_test_connection` (to be removed in Phase 3).
- **`site_health_check`** — cross-platform site aggregator.
- **`manage_wlan_profile`** — cross-platform WLAN orchestrator.

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

## Aruba Central (73 tools + 12 prompts)

### Sites

#### `central_get_sites`

> Returns site configuration data (address, timezone, scopeName) from the network-config API. Use for site details. For health metrics, use `central_get_site_health`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter | str | No | OData 4.0 filter on scopeName, address, city, state, country, zipcode, collectionName. |
| sort | str | No | Sort by scopeName, address, state, country, city, deviceCount, collectionName, zipcode, timezone, longitude, latitude. |
| limit | int | No | Results per page (1-100, default 100). |
| offset | int | No | Pagination offset (default 0). |

#### `central_get_site_health`

> Returns health metrics and device/client counts for sites. For site config data, use `central_get_sites`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_name | str \| list[str] | No | One site name or a list of site names to filter by (exact match). Omit for all sites. |

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

### AP Monitoring

#### `central_get_aps`

> List access points with AP-specific filters (status, model, firmware, deployment, cluster, site).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | No | Filter by site ID. |
| site_name | str | No | Filter by site name. |
| serial_number | str | No | AP serial (comma-separated for multiple). |
| device_name | str | No | AP name (comma-separated for multiple). |
| status | str | No | `ONLINE` or `OFFLINE`. |
| model | str | No | AP model (comma-separated). |
| firmware_version | str | No | Firmware version (comma-separated). |
| deployment | str | No | `Standalone`, `Cluster`, or `Unspecified`. |
| sort | str | No | Sort expression (e.g. `deviceName asc`). |

#### `central_get_ap_wlans`

> Get WLANs currently active on a specific AP. Useful for troubleshooting which SSIDs an AP is broadcasting.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |
| wlan_name | str | No | Filter by exact WLAN name (client-side). |

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

#### `central_get_wlan_stats`

> Get throughput trend data (tx/rx time-series in bps) for a specific WLAN over a time window.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| wlan_name | str | Yes | WLAN name (SSID) to get stats for. |
| time_range | str | No | `last_1h` (default), `last_6h`, `last_24h`, `last_7d`, `last_30d`, `today`, `yesterday`. |
| start_time | str | No | RFC 3339 format. Overrides time_range when combined with end_time. |
| end_time | str | No | RFC 3339 format. |

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

### WLAN Profiles

#### `central_get_wlan_profiles`

> Read WLAN SSID profiles from Central's configuration library. Returns full config data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ssid | str | No | Specific SSID name. If omitted, returns all profiles. |

#### `central_manage_wlan_profile`

> Create, update, or delete a WLAN SSID profile. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`.
>
> **For cross-platform WLAN sync, use the sync prompts instead of calling this tool directly.**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ssid | str | Yes | SSID name (used as identifier in API path). |
| action_type | str | Yes | `create`, `update`, or `delete`. |
| payload | dict | Yes | WLAN profile config. For `update` (default), pass only the fields you want to change — the tool issues a `PATCH` and Central merges. For `create`, pass a full profile. For `delete`, payload is ignored. |
| replace_existing | bool | No | Destructive flag. When True, `update` issues a `PUT` that replaces the entire profile — fields not in the payload will be dropped. Default False (safe partial-patch). |
| confirmed | bool | No | Set to true after user confirms update/delete in chat. |

**Update semantics:** By default, `action_type="update"` issues `PATCH /network-config/v1alpha1/wlan-ssids/{ssid}` and the Central API merges the payload with the existing profile server-side. Pass only the fields you want to change; everything else is preserved. The elicitation prompt fetches the current profile and shows a per-field `before → after` diff before applying the change. Set `replace_existing=True` only when you have the complete profile in `payload` and genuinely want a wholesale swap (uses `PUT`).

**Valid `opmode` values** (do NOT invent values — use only these):

`OPEN`, `WPA2_PERSONAL`, `WPA3_SAE`, `WPA2_ENTERPRISE`, `WPA3_ENTERPRISE_CCM_128`,
`WPA3_ENTERPRISE_GCM_256`, `WPA3_ENTERPRISE_CNSA`, `WPA_ENTERPRISE`, `WPA_PERSONAL`,
`WPA2_MPSK_AES`, `WPA2_MPSK_LOCAL`, `ENHANCED_OPEN`, `DPP`, `WPA2_PSK_AES_DPP`,
`WPA2_AES_DPP`, `WPA3_SAE_DPP`, `WPA3_AES_CCM_128_DPP`, `WPA3_AES_GCM_256_DPP`,
`BOTH_WPA_WPA2_PSK`, `BOTH_WPA_WPA2_DOT1X`, `STATIC_WEP`, `DYNAMIC_WEP`

**Other key enums**: `forward-mode`: `FORWARD_MODE_BRIDGE`, `FORWARD_MODE_L2` |
`rf-band`: `BAND_ALL`, `24GHZ_5GHZ`, `5GHZ_6GHZ`, `24GHZ`, `5GHZ`, `6GHZ`, `BAND_NONE` |
`vlan-selector`: `NAMED_VLAN` (with `vlan-name`), `VLAN_RANGES` (with `vlan-id-range`) |
`out-of-service`: `NONE`, `UPLINK_DOWN`, `TUNNEL_DOWN`

### Aliases, Server Groups, Named VLANs

These tools resolve named references used in WLAN profiles. Used by sync prompts
to translate between Central's named/aliased config and Mist's inline config.

#### `central_get_aliases`

> Get alias configurations from Aruba Central. Aliases are named references used in WLAN profiles (SSID aliases, PSK aliases), server groups, and VLAN definitions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| alias_name | str | No | Specific alias name. If omitted, returns all aliases. |

#### `central_get_server_groups`

> Get RADIUS/auth server group configurations. Resolve a server group name (from a WLAN profile's auth-server-group field) to its actual server addresses and settings.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | str | No | Specific server group name. If omitted, returns all groups. |

#### `central_get_named_vlans`

> Get named VLAN configurations. Resolve a named VLAN (from a WLAN profile's vlan-name field) to its actual VLAN ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | str | No | Specific named VLAN name. If omitted, returns all named VLANs. |

### Write Tools (disabled by default)

#### `central_manage_site`

> Create, update, or delete a site in Aruba Central. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, or `delete`. |
| payload | dict | Yes | Site payload. All values must use full names (no abbreviations). For create: `address`, `name`, `city`, `state`, `country`, `zipcode`, and `timezone` (object with `timezoneName`, `timezoneId`, `rawOffset` in ms) are required. |
| site_id | str | No | Site ID. Required for update and delete. |

#### `central_manage_site_collection`

> Create, update, delete, or manage sites within a site collection. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, `delete`, `add_sites`, or `remove_sites`. |
| payload | dict | Yes | For create: `scopeName` required, optional `description`, `siteIds`. For add_sites/remove_sites: `siteIds` list required. |
| collection_id | str | No | Collection ID. Required for update, delete, add_sites, remove_sites. |
| confirmed | bool | No | Set to true after user confirms update/delete in chat. |

#### `central_manage_device_group`

> Create, update, or delete a device group in Aruba Central. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, or `delete`. |
| payload | dict | Yes | Device group payload. For create: `scopeName` required. Optional: `description`. |
| group_id | str | No | Group ID. Required for update and delete. |

### Config Assignments

#### `central_get_config_assignments`

> Read which configuration profiles are assigned to which scopes and device functions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scope_id | str | No | Scope ID to filter. Get from `central_get_scope_tree`. |
| device_function | str | No | Device function filter. `CAMPUS_AP` for WLANs, `ACCESS_SWITCH` for switches, etc. |

#### `central_manage_config_assignment`

> Assign or remove a configuration profile at a scope in Central's hierarchy. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`. This is how WLAN profiles, roles, and policies get applied to scopes.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `assign` or `remove`. |
| scope_id | str | Yes | Scope ID. Get from `central_get_scope_tree`. |
| device_function | str | Yes | `CAMPUS_AP` for WLANs. Others: `ACCESS_SWITCH`, `BRANCH_GW`, `MOBILITY_GW`, `ALL`, etc. |
| profile_type | str | Yes | Profile type: `wlan-ssids`, `roles`, `policies`, `auth-server-groups`, `named-vlans`, `aliases`. |
| profile_instance | str | Yes | Profile name (e.g. the SSID name for WLAN profiles). |
| confirmed | bool | No | Set to true after user confirms. |

### Roles

#### `central_get_roles`

> Get role configurations. Roles define network access (VLAN, QoS, ACLs, bandwidth contracts) for clients and are used in WLAN profiles, switch ports, NAC policies, and firewall rules.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | str | No | Specific role name. If omitted, returns all roles. |

#### `central_manage_role`

> Create, update, or delete a role. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`. Roles can be shared (library) or local (scoped to a site/collection).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | str | Yes | Role name (identifier in API path). |
| action_type | str | Yes | `create`, `update`, or `delete`. |
| payload | dict | Yes | Role config (VLAN, ACLs, QoS, bandwidth, etc.). Empty dict for delete. |
| scope_id | str | No | Scope ID for local roles. Omit for shared/library roles. |
| device_function | str | No | `CAMPUS_AP`, `ACCESS_SWITCH`, `BRANCH_GW`, etc. Required with scope_id. |
| confirmed | bool | No | Set to true after user confirms update/delete. |

### Security & Policy

All tools below follow the same CRUD pattern. Read tools accept an optional `name` to get a specific
resource or omit for all. Write tools accept `name`, `action_type` (create/update/delete), `payload`,
and optional `scope_id` + `device_function` for local (scoped) objects.

#### `central_get_net_groups` / `central_manage_net_group`

> Network groups (netdestinations) — reusable named objects defining hosts, FQDNs, subnets, IP ranges, VLANs, ports for use in ACLs and policies.

#### `central_get_net_services` / `central_manage_net_service`

> Network service definitions — protocol and port combinations (TCP/443, UDP/53, etc.) for identifying traffic types in policies.

#### `central_get_object_groups` / `central_manage_object_group`

> Object groups — named collections of addresses, services, or other objects for ACL references.

#### `central_get_role_acls` / `central_manage_role_acl`

> Role ACLs — access control lists with ordered permit/deny rules referencing net-groups and net-services.

#### `central_get_policies` / `central_manage_policy`

> Firewall policies — ordered rule sets that match traffic and apply actions (permit, deny, NAT, redirect, policy-based routing).

#### `central_get_policy_groups` / `central_manage_policy_group`

> Policy groups — define the evaluation sequence for all firewall policies. Collection-level resource (no per-name path).

#### `central_get_role_gpids` / `central_manage_role_gpid`

> Role GPIDs — map roles to policy group IDs. Controls which policy group is assigned to each role.

### Firmware

#### `central_recommend_firmware`

> Applies an LSR-preferred upgrade policy on top of Central's built-in `recommendedVersion`. The LSR/SSR classification comes directly from the `firmwareClassification` field in the firmware-details API response — no hand-maintained mapping. For devices classified as SSR, the "next LSR" target is mined live from the same response: the highest LSR version observed across the fleet for that device type.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | No | Narrow to one device. |
| device_type | str | No | `ACCESS_POINT`, `SWITCH`, or `GATEWAY`. Filtering this narrows the pool used to mine the newest LSR target for SSR devices — leave unset for best SSR recommendations. |
| site_id | str | No | Limit to a site by ID. |
| site_name | str | No | Limit to a site by exact name. |
| include_up_to_date | bool | No | If True, include devices already on Central's recommended version. Default False. |
| max_pages | int | No | Safety cap on paginated fetches (1000 items × max_pages). Default 10. |

**Policy:**

- Classified **LSR** → upgrade in place to Central's recommended version (latest in same train).
- Classified **SSR** → move to the newest LSR version seen in the fleet for that device type (mined live).
- Classified **empty / unclassified** (typically AOS 8) → pass Central's recommendation through.
- No LSR device of the same type in the fleet → SSR devices fall back to Central's recommendation with a note.

**Returned report:**

- `discovered_lsr_targets` — `{device_type: newest LSR version}` mined from the response. Empty if no LSR devices were observed.
- `total_devices_scanned`, `up_to_date`, `on_lsr`, `on_ssr`, `unclassified`, `needs_action` — fleet-level counts.
- `recommendations[]` — per-device records: current version, release type (`LSR`/`SSR`/`UNCLASSIFIED`), Central's recommendation, our recommendation, action (`upgrade_in_place`, `move_to_lsr_train`, `follow_central`, `up_to_date`), and a rationale string.

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

## Cross-Platform (2 tools + 3 prompts)

Tools that span multiple platforms. Each replaces several individual tool calls with a single aggregated response.

### `site_health_check`

> **One-call site health snapshot across every enabled platform.** Aggregates Mist, Central, and (optionally) ClearPass into a single compact report. Replaces ~8–12 separate tool calls. Registered when at least Mist or Central is enabled; ClearPass is additive.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_name | str | Yes | Exact site name as shown in Mist and/or Central. |
| time_window_hours | int | No | Lookback window for alarms, sessions, and events (1–168, default 24). |

**What it returns:**

- `overall_status` — `healthy`, `degraded`, `critical`, or `unknown`.
- `headline` — One-line summary suitable for the user.
- `mist` — Site stats (device/client counts, connected/offline), top alarms, critical count.
- `central` — Health score, device/client totals, active alerts, critical count, top alerts.
- `clearpass` — NADs matched to the site's device IPs, active session count, recent auth-failure count (when ClearPass is configured).
- `recommendations` — Concrete follow-up tool calls with the right site_id already filled in, targeting only the platforms and categories that showed issues.

**Typical use:** "How is site X doing?", "Is site X healthy?", "Give me a status on site X." After reviewing the summary, follow the recommendations for deeper investigation — do not re-query the per-platform health tools unless needed.

### `manage_wlan_profile`

> **Primary entry point for all WLAN operations.** Automatically checks both Mist and Central for the SSID and returns the correct workflow. Detects cross-platform scenarios without relying on AI instructions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ssid | str | Yes | The SSID name to create, update, delete, or sync. |
| action_type | str | Yes | `create`, `update`, `delete`, or `sync`. |
| target_platform | str | No | `central`, `mist`, or `both` (default). |
| payload | dict | No | WLAN profile payload for create/update. Empty dict for sync/delete. |

**Behavior by scenario:**

| Scenario | Response |
|----------|----------|
| SSID in Mist only, target Central | Mist→Central sync workflow with field mapping and scope assignment |
| SSID in Central only, target Mist | Central→Mist sync workflow with alias resolution |
| SSID on both platforms | Returns both configs, asks user to choose source |
| New SSID (neither platform) | Directs to platform-specific create tool |
| action_type="sync" | Compares both platforms regardless of target |

### Prompts

| Prompt | Parameters | Description |
|--------|-----------|-------------|
| `sync_wlans_mist_to_central` | (none) | Sync WLAN profiles from Mist to Central with full field mapping and scope assignment. |
| `sync_wlans_central_to_mist` | (none) | Sync WLAN profiles from Central to Mist with alias resolution and template variables. |
| `sync_wlans_bidirectional` | (none) | Compare WLANs across both platforms, show field-level differences, sync in either direction. |

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

---

## Aruba ClearPass (127 tools)

ClearPass tools use the `pyclearpass` SDK with OAuth2 client credentials. Write tools require
`ENABLE_CLEARPASS_WRITE_TOOLS=true`. Update/delete operations require user confirmation.

### Network Devices (4 read + 1 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_network_devices` | List or get NADs (RADIUS/TACACS+ clients) by ID or name |
| `clearpass_get_network_device_stats` | Get detailed device record by ID |
| `clearpass_test_device_connectivity` | Fetch device record for connectivity review |
| `clearpass_validate_device_config` | Validate device configuration for missing fields |
| `clearpass_manage_network_device` | Create, update, delete, clone, configure SNMP/RadSec/CLI/on-connect |

### Guest Management (1 read + 4 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_guest_users` | List or get guest users by ID or username |
| `clearpass_manage_guest_user` | Create, update, delete guest users |
| `clearpass_send_guest_credentials` | Send credentials via SMS or email (`delivery_method`: sms/email) |
| `clearpass_generate_guest_pass` | Generate digital pass or receipt (`pass_type`: digital/receipt) |
| `clearpass_process_sponsor_action` | Approve or reject guest sponsorship requests |

### Guest Configuration (5 read + 4 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_pass_templates` | List or get digital pass templates |
| `clearpass_get_print_templates` | List or get print receipt templates |
| `clearpass_get_weblogin_pages` | List or get captive portal web login pages |
| `clearpass_get_guest_auth_settings` | Get guest authentication global settings |
| `clearpass_get_guest_manager_settings` | Get guest manager global settings |
| `clearpass_manage_pass_template` | Create, update, replace, delete pass templates |
| `clearpass_manage_print_template` | Create, update, replace, delete print templates |
| `clearpass_manage_weblogin_page` | Create, update, replace, delete web login pages |
| `clearpass_manage_guest_settings` | Update guest authentication and manager settings |

### Endpoints (2 read + 1 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_endpoints` | List or get endpoints by ID or MAC address |
| `clearpass_get_endpoint_profiler` | Get device profiler fingerprint data |
| `clearpass_manage_endpoint` | Create, update, delete endpoints |

### Session Control (3 read + 2 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_sessions` | List active sessions or get session by ID |
| `clearpass_get_session_action_status` | Check status of disconnect/CoA action |
| `clearpass_get_reauth_profiles` | Get reauthorization profiles for a session |
| `clearpass_disconnect_session` | Disconnect session(s) — `target_type`: session_id/username/mac/ip/bulk |
| `clearpass_perform_coa` | Change of Authorization — `target_type`: session_id/username/mac/ip/bulk |

### Roles & Role Mappings (2 read + 2 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_roles` | List or get roles by ID or name |
| `clearpass_get_role_mappings` | List or get role mappings by ID or name |
| `clearpass_manage_role` | Create, update, delete roles |
| `clearpass_manage_role_mapping` | Create, update, delete role mappings |

### Enforcement (3 read + 2 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_enforcement_policies` | List or get enforcement policies |
| `clearpass_get_enforcement_profiles` | List or get enforcement profiles |
| `clearpass_get_profile_templates` | Reference list of common enforcement profile patterns |
| `clearpass_manage_enforcement_policy` | Create, update, delete enforcement policies |
| `clearpass_manage_enforcement_profile` | Create, update, delete enforcement profiles |

### Authentication (4 read + 2 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_auth_sources` | List or get authentication sources (LDAP/AD/RADIUS) |
| `clearpass_get_auth_source_status` | Get auth source connection status and statistics |
| `clearpass_test_auth_source` | Fetch auth source details for connectivity review |
| `clearpass_get_auth_methods` | List or get authentication methods (EAP, certificates) |
| `clearpass_manage_auth_source` | Create, update, delete, configure_backup, configure_filters, configure_radius_attrs |
| `clearpass_manage_auth_method` | Create, update, delete authentication methods |

### Certificates (4 read + 2 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_trust_list` | List or get certificate trust list entries |
| `clearpass_get_client_certificates` | List or get client certificates |
| `clearpass_get_server_certificates` | List or get server certificates |
| `clearpass_get_service_certificates` | List service certificates |
| `clearpass_manage_certificate` | Import/delete trust list, delete client cert, enable/disable server cert |
| `clearpass_create_csr` | Generate Certificate Signing Request |

### Audit & Insight (5 read + 3 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_audit_logs` | Get admin login audit records by username |
| `clearpass_get_system_events` | List system events with filtering |
| `clearpass_get_insight_alerts` | List or get Insight alert configurations |
| `clearpass_get_insight_reports` | List or get Insight report configurations |
| `clearpass_get_endpoint_insights` | Endpoint insights by MAC, IP, IP range, or time range |
| `clearpass_manage_insight_alert` | Create, update, delete, enable, disable, mute, unmute alerts |
| `clearpass_manage_insight_report` | Create, delete, enable, disable, run reports |
| `clearpass_create_system_event` | Create a custom system event |

### Identities (5 read + 5 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_api_clients` | List or get API clients |
| `clearpass_get_local_users` | List or get local users |
| `clearpass_get_static_host_lists` | List or get static host lists |
| `clearpass_get_devices` | List or get devices by ID or MAC |
| `clearpass_get_deny_listed_users` | List or get deny-listed users |
| `clearpass_manage_api_client` | Create, update, delete API clients |
| `clearpass_manage_local_user` | Create, update, delete local users |
| `clearpass_manage_static_host_list` | Create, update, delete static host lists |
| `clearpass_manage_device` | Create, update, delete devices |
| `clearpass_manage_deny_listed_user` | Create, delete deny-listed users |

### Policy Elements (7 read + 7 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_services` | List or get configuration services |
| `clearpass_get_posture_policies` | List or get posture policies |
| `clearpass_get_device_groups` | List or get network device groups |
| `clearpass_get_proxy_targets` | List or get proxy targets |
| `clearpass_get_radius_dictionaries` | List or get RADIUS dictionaries |
| `clearpass_get_tacacs_dictionaries` | List or get TACACS+ service dictionaries |
| `clearpass_get_application_dictionaries` | List or get application dictionaries |
| `clearpass_manage_service` | Create, update, delete, enable, disable config services |
| `clearpass_manage_device_group` | Create, update, delete device groups |
| `clearpass_manage_posture_policy` | Create, update, delete posture policies |
| `clearpass_manage_proxy_target` | Create, update, delete proxy targets |
| `clearpass_manage_radius_dictionary` | Create, update, delete, enable, disable RADIUS dictionaries |
| `clearpass_manage_tacacs_dictionary` | Create, update, delete TACACS+ dictionaries |
| `clearpass_manage_application_dictionary` | Create, update, delete application dictionaries |

### Server Configuration (13 read + 12 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_admin_users` | List or get admin users |
| `clearpass_get_admin_privileges` | List or get admin privilege sets |
| `clearpass_get_operator_profiles` | List or get operator profiles |
| `clearpass_get_licenses` | List licenses, get details, or get summary |
| `clearpass_get_cluster_params` | Get cluster parameters |
| `clearpass_get_password_policies` | Get admin and local user password policies |
| `clearpass_get_attributes` | List or get custom attributes |
| `clearpass_get_data_filters` | List or get data filters |
| `clearpass_get_file_backup_servers` | List or get file backup servers |
| `clearpass_get_messaging_setup` | Get messaging (email/SMS) configuration |
| `clearpass_get_snmp_trap_receivers` | List or get SNMP trap receivers |
| `clearpass_get_policy_manager_zones` | List or get policy manager zones |
| `clearpass_get_oauth_privileges` | Get OAuth privileges |
| `clearpass_manage_admin_user` | Create, update, delete admin users |
| `clearpass_manage_admin_privilege` | Create, update, delete admin privileges |
| `clearpass_manage_operator_profile` | Create, update, delete operator profiles |
| `clearpass_manage_license` | Create, delete, activate_online, activate_offline |
| `clearpass_manage_cluster_params` | Update cluster parameters |
| `clearpass_manage_password_policy` | Update admin or local user password policies |
| `clearpass_manage_attribute` | Create, update, delete attributes |
| `clearpass_manage_data_filter` | Create, update, delete data filters |
| `clearpass_manage_file_backup_server` | Create, update, delete backup servers |
| `clearpass_manage_messaging_setup` | Create, update, delete messaging config |
| `clearpass_manage_snmp_trap_receiver` | Create, update, delete SNMP trap receivers |
| `clearpass_manage_policy_manager_zone` | Create, update, delete policy manager zones |

### Local Configuration (6 read + 4 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_access_controls` | Get server access controls by UUID and/or resource |
| `clearpass_get_ad_domains` | List or get Active Directory domains |
| `clearpass_get_server_version` | Get ClearPass version, cluster info |
| `clearpass_get_fips_status` | Get server FIPS status |
| `clearpass_get_server_services` | List or get server services |
| `clearpass_get_server_snmp` | Get server SNMP configuration |
| `clearpass_manage_access_control` | Update, delete server access controls |
| `clearpass_manage_ad_domain` | Join, leave, configure_password_servers for AD domains |
| `clearpass_manage_cluster_server` | Update cluster server configuration |
| `clearpass_manage_server_service` | Start, stop server services |

### Integrations (6 read + 4 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_extensions` | List or get extension instances |
| `clearpass_get_syslog_targets` | List or get syslog targets |
| `clearpass_get_syslog_export_filters` | List or get syslog export filters |
| `clearpass_get_event_sources` | List or get event sources |
| `clearpass_get_context_servers` | List or get context server actions |
| `clearpass_get_endpoint_context_servers` | List or get endpoint context servers |
| `clearpass_manage_extension` | Start, stop, restart, delete extensions |
| `clearpass_manage_syslog_target` | Create, update, delete syslog targets |
| `clearpass_manage_syslog_export_filter` | Create, update, delete syslog export filters |
| `clearpass_manage_endpoint_context_server` | Create, update, delete, trigger_poll context servers |

### Utilities (2 tools)

| Tool | Description |
|------|-------------|
| `clearpass_generate_random_password` | Generate random password or MPSK |
| `clearpass_test_connection` | Test ClearPass connectivity and get server version |

---

## Juniper Apstra (21 tools)

Ported from a standalone Apstra MCP server. Requires Apstra credentials in
Docker secrets (`apstra_server`, `apstra_username`, `apstra_password`, plus
optional `apstra_port` (default 443) and `apstra_verify_ssl` (default true)).
Write tools require `ENABLE_APSTRA_WRITE_TOOLS=true` and go through the
elicitation confirmation flow.

### Health and Meta (2 tools)

| Tool | Description |
|------|-------------|
| `apstra_health` | Server health plus live login probe of the configured Apstra server |
| `apstra_formatting_guidelines` | Full formatting guidance for Apstra output |

### Blueprints (2 tools)

| Tool | Description |
|------|-------------|
| `apstra_get_blueprints` | List all blueprints (id, label, design, status) |
| `apstra_get_templates` | List design templates available for new blueprints |

### Topology (3 tools)

| Tool | Description |
|------|-------------|
| `apstra_get_racks` | All racks in a blueprint (`blueprint_id`) |
| `apstra_get_routing_zones` | Security zones / VRFs in a blueprint (`blueprint_id`) |
| `apstra_get_system_info` | Systems (spines, leafs, redundancy groups) in a blueprint (`blueprint_id`) |

### Virtual Networks (2 tools)

| Tool | Description |
|------|-------------|
| `apstra_get_virtual_networks` | VNs with bound systems and VLAN IDs (`blueprint_id`) |
| `apstra_get_remote_gateways` | Remote EVPN gateways in a blueprint (`blueprint_id`) |

### Connectivity Templates (2 tools)

| Tool | Description |
|------|-------------|
| `apstra_get_connectivity_templates` | Policy templates visible for assignment (`blueprint_id`) |
| `apstra_get_application_endpoints` | Interfaces available as CT attachment points (`blueprint_id`) |

### Status (3 tools)

| Tool | Description |
|------|-------------|
| `apstra_get_anomalies` | Active anomalies in a blueprint (`blueprint_id`) |
| `apstra_get_diff_status` | Staging vs active-version diff (`blueprint_id`) |
| `apstra_get_protocol_sessions` | BGP and other protocol sessions (`blueprint_id`) |

### Management (write, destructive)

| Tool | Description |
|------|-------------|
| `apstra_deploy` | Deploy a staged version to the fabric (`blueprint_id`, `description`, `staging_version`, `confirmed`) |
| `apstra_delete_blueprint` | Permanently delete a blueprint (`blueprint_id`, `confirmed`) |

### Management (write, create)

| Tool | Description |
|------|-------------|
| `apstra_create_datacenter_blueprint` | Instantiate a new datacenter blueprint from a template |
| `apstra_create_freeform_blueprint` | Create a new freeform blueprint |
| `apstra_create_virtual_network` | Create a VXLAN or VLAN virtual network via `virtual-networks-batch` |
| `apstra_create_remote_gateway` | Create a remote EVPN gateway |
| `apstra_apply_ct_policies` | Apply or remove connectivity-template policies on interfaces |
