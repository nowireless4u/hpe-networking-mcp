# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.9.0.2] - 2026-04-17

### Fixed
- **ClearPass tools returning 403 after ~8 hours** (#130) — OAuth2 access tokens
  issued via `client_credentials` expire after 8 hours, but the server cached the
  startup token indefinitely. After the token aged out every `clearpass_*` tool
  returned `403 Forbidden` even for Super Administrator clients. Replaced the
  single-shot cache with a pycentral-style reactive refresh: on any 401/403 the
  token is invalidated, a fresh one is fetched from `/oauth`, and the original
  request is replayed once. Implemented as a class-level patch on
  `ClearPassAPILogin._send_request` since pyclearpass methods bypass
  instance-level overrides.

## [v0.9.0.0] - 2026-04-16

### Added — Aruba ClearPass Platform
- Complete ClearPass Policy Manager integration using `pyclearpass` SDK with OAuth2 client credentials
- 127 new tools (55 read + 72 write) across 16 read modules and 15 write modules
- **Network Devices** — list, get, create, update, delete, clone, configure SNMP/RadSec/CLI/on-connect
- **Guest Management** — guest user CRUD, credential delivery (SMS/email), digital pass generation, sponsor workflows
- **Guest Configuration** — pass templates, print templates, web login pages, authentication and manager settings
- **Endpoints** — endpoint CRUD, device profiler fingerprinting
- **Session Control** — active session listing, disconnect (by session/username/MAC/IP/bulk), Change of Authorization (CoA)
- **Roles & Enforcement** — roles, role mappings, enforcement policies, enforcement profiles
- **Authentication** — authentication sources (LDAP/AD/RADIUS) and methods, with backup/filter/attribute configuration
- **Certificates** — trust list, client/server/service certificates, CSR generation, enable/disable server certs
- **Audit & Insight** — login audit, system events, endpoint insights (by MAC/IP/time), Insight alerts and reports with enable/disable/mute/run
- **Identities** — API clients, local users, static host lists, devices, deny-listed users
- **Policy Elements** — configuration services (enable/disable), posture policies, device groups, proxy targets, RADIUS/TACACS/application dictionaries
- **Server Configuration** — admin users/privileges, operator profiles, licenses (online/offline activation), cluster parameters, password policies, attributes, data filters, backup servers, messaging, SNMP trap receivers, policy manager zones
- **Local Configuration** — server access controls, Active Directory domain join/leave, cluster server management, service start/stop
- **Integrations** — extensions (start/stop/restart), syslog targets, syslog export filters, endpoint context servers
- **Utilities** — random password/MPSK generation, connection testing
- Docker secrets: `clearpass_server`, `clearpass_client_id`, `clearpass_client_secret`, `clearpass_verify_ssl` (optional)
- Write tools gated behind `ENABLE_CLEARPASS_WRITE_TOOLS` (default: disabled)
- Token caching — single OAuth2 token acquired at startup, shared across all tool calls
- SSL verification configurable via `clearpass_verify_ssl` secret (default: true)

### Changed
- Platform count: 3 → 4 (Mist, Central, GreenLake, ClearPass)
- Total tool count: ~117 → ~244

[v0.9.0.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.9.0.0

## [v0.8.3.0] - 2026-04-16

### Added — Central Roles & Policy Tools
- `central_get_net_groups` / `central_manage_net_group` — netdestinations (hosts, FQDNs, subnets, IP ranges, VLANs, ports)
- `central_get_net_services` / `central_manage_net_service` — protocol/port definitions
- `central_get_object_groups` / `central_manage_object_group` — named collections for ACL references
- `central_get_role_acls` / `central_manage_role_acl` — role-based access control lists
- `central_get_policies` / `central_manage_policy` — firewall policies (ordered rule sets)
- `central_get_policy_groups` / `central_manage_policy_group` — policy evaluation ordering
- `central_get_role_gpids` / `central_manage_role_gpid` — role to policy group ID mapping
- All write tools support shared (library) and local (scoped) objects via scope_id and device_function params
- Central tool count: 58 → 72

### Fixed
- Docker publish workflow now supports 4-digit versioning. Switched from `type=semver` (3-digit only) to `type=ref,event=tag` which uses the git tag as-is.

[v0.8.3.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.3.0

## [v0.8.2.0] - 2026-04-15

### Added — Central Role Management
- `central_get_roles` — read role configurations (VLAN, QoS, ACLs, bandwidth contracts, classification rules)
- `central_manage_role` — create, update, delete roles. Supports shared (library) and local (scoped) roles via `scope_id` and `device_function` params.
- Central tool count: 56 → 58

[v0.8.2.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.2.0

## [v0.8.1.0] - 2026-04-15

### Added — New Central Monitoring Tools
- `central_get_aps` — filtered AP listing with AP-specific filters (status, model, firmware, deployment type, cluster, site). Uses `MonitoringAPs.get_all_aps()` with OData filters.
- `central_get_ap_wlans` — get WLANs currently active on a specific AP by serial number. Uses `MonitoringAPs.get_ap_wlans()`. Supports optional `wlan_name` filter.
- `central_get_wlan_stats` — WLAN throughput trends (tx/rx time-series in bps) over a time window. Uses `GET /network-monitoring/v1/wlans/{name}/throughput-trends`. Supports predefined time ranges and custom RFC 3339 start/end.
- Central tool count: 53 → 56

### Added — Integration Test Scaffolding
- `tests/integration/conftest.py` — live API fixtures using Docker secrets. Creates real Central connection, skips gracefully if credentials missing.
- `tests/integration/test_ap_monitoring_live.py` — 6 live tests for AP listing, details, and WLAN-per-AP tools
- `tests/integration/test_wlans_live.py` — 5 live tests for WLAN listing, throughput stats, and time window filtering

### Added — Utility Functions
- `format_rfc3339()` — format datetime as RFC 3339 string with millisecond precision
- `resolve_time_window()` — resolve predefined time ranges or pass-through custom start/end times

### Changed — Versioning
- Moved to 4-digit versioning: `v0.MAJOR.MINOR.PATCH`

[v0.8.1.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.1.0

## [v0.8.7] - 2026-04-15

### Fixed
- Data rate mapping in manage_wlan workflow — AI was setting custom rates instead of using standard Central profiles (high-density, no-legacy, compatible). Workflow now includes exact rate values for both directions.
- Expanded all field mappings in workflow instructions to be fully explicit (RF bands, VLAN, roaming, EHT, ARP filter, isolation, performance fields).

## [v0.8.6] - 2026-04-15

### Added
- `central_get_config_assignments` — read which profiles are assigned to which scopes, filtered by scope_id and device_function (`GET /network-config/v1alpha1/config-assignments`)
- `central_manage_config_assignment` — assign or remove a profile at a scope (`POST`/`DELETE /network-config/v1alpha1/config-assignments`). Completes the WLAN sync workflow — profiles can now be assigned to scopes programmatically.
- Central tool count: 51 → 53

### Fixed
- manage_wlan Mist→Central Step 6 now calls `central_manage_config_assignment` to assign the profile instead of looping
- manage_wlan both-platforms workflow returns full configs and requires user to choose source

## [v0.8.5] - 2026-04-15

### Fixed
- Removed `source_platform` parameter from `central_manage_wlan_profile` and `mist_change_org_configuration_objects` — conflicted with unified `manage_wlan_profile` tool. The AI followed the workflow correctly but got blocked when the platform tool rejected the call.

## [v0.8.4] - 2026-04-15

### Added
- `manage_wlan_profile` — unified cross-platform entry point for all WLAN operations. Checks both Mist and Central for the SSID and returns the correct sync workflow automatically. Registered when both platforms are enabled.

## [v0.8.3] - 2026-04-15

### Added
- Mist org_id validation — server resolves the real org_id at startup. `validate_org_id()` catches fabricated org_ids before API calls.

## [v0.8.2] - 2026-04-15

### Fixed
- Sync prompt now enforces `mist_get_self` as mandatory first step with "Do NOT use any org_id from memory"
- Sync prompt Step 2 looks up WLAN template assignment: `template_id` → `sitegroup_ids` + `site_ids` → names
- Sync prompt Step 9 (REQUIRED) reports assignment mapping based on template assignment
- Added explicit opmode mapping table in sync prompt

## [v0.8.1] - 2026-04-15

### Fixed
- Added all 22 valid `opmode` enum values to `central_manage_wlan_profile` tool description — prevents invalid values like `WPA2_PSK_AES`
- Added valid enum values for `rf-band`, `forward-mode`, `vlan-selector`, `out-of-service`, `broadcast-filter-ipv4`
- Strengthened cross-platform WLAN sync guidance in INSTRUCTIONS.md

[v0.8.7]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.7
[v0.8.6]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.6
[v0.8.5]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.5
[v0.8.4]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.4
[v0.8.3]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.3
[v0.8.2]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.2
[v0.8.1]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.1

## [v0.8.0] - 2026-04-14

### Fixed — Central Write Tools (#99)
- Central delete operations now use bulk endpoint (`DELETE {path}/bulk` with `{"items": [{"id": "..."}]}`) instead of appending ID to URL path
- Central update operations now pass `scopeId` in request body instead of URL path
- Confirmation loop fix: added `confirmed` parameter to all write tools (Mist + Central). When `confirmed=true`, skips re-prompting. The AI sets this after the user confirms in chat.

### Added — Cross-Platform WLAN Sync (#94-98)
- `central_get_wlan_profiles` — read WLAN SSID profiles from Central's config library (`GET /network-config/v1alpha1/wlan-ssids`)
- `central_manage_wlan_profile` — create, update, delete WLAN SSID profiles in Central
- `central_get_aliases` — read alias configurations used in WLAN profiles, server groups, and VLANs (`GET /network-config/v1alpha1/aliases`)
- `central_get_server_groups` — read RADIUS/auth server group definitions (`GET /network-config/v1alpha1/server-groups`)
- `central_get_named_vlans` — read named VLAN configurations (`GET /network-config/v1alpha1/named-vlan`)
- `wlan_mapper.py` + `_wlan_helpers.py` — field translation modules between Central and Mist WLAN formats, supporting all mapped fields: opmode with pairwise arrays (WPA2/WPA3/transition), RADIUS with server group and template variable resolution, dynamic VLAN with airespace interface names, data rate profiles (MBR → rateset template), MAC auth, NAS ID/IP, CoA, RadSec, EHT/11be, and RF bands as arrays
- 3 cross-platform sync prompts: `sync_wlans_mist_to_central`, `sync_wlans_central_to_mist`, `sync_wlans_bidirectional` — registered as shared prompts (requires both Mist and Central enabled), with alias resolution, template variable creation, and comparison/diff workflows
- WLAN field mapping reference at `docs/mappings/WLAN.md` (~38 mapped fields)
- Tunneled SSIDs automatically excluded from migration
- Central tool count: 48 → 51 (+ 3 new read-only tools), Central prompt count: 15 → 12 (3 sync prompts moved to cross-platform)
- 81 new unit tests for `wlan_mapper.py` and `_wlan_helpers.py`

### Added — Site Collection Management
- `add_sites` and `remove_sites` action types for `central_manage_site_collection`
- Uses `POST /network-config/v1/site-collection-add-sites` and `DELETE /network-config/v1/site-collection-remove-sites`

[v0.8.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.0

## [v0.7.21] - 2026-04-14

### Added
- `central_get_sites` — new tool returning site configuration data (address, timezone, scopeName) from `network-config/v1/sites` with OData filter and sort support

### Changed
- Renamed old `central_get_sites` → `central_get_site_health` to accurately reflect it returns health metrics, not site config data
- Central tool count: 45 → 46 (+ 12 prompts)

### Fixed
- `central_get_site_health` crash (`KeyError: 'name'`) when sites returned from the health API lack a `name` field (e.g. newly created sites)

[v0.7.21]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.21

## [v0.7.20] - 2026-04-14

### Fixed
- Central site creation payload: timezone is required, all field values must use full names (no abbreviations). Updated tool description, INSTRUCTIONS.md, and TOOLS.md with correct format.

[v0.7.20]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.20

## [v0.7.19] - 2026-04-14

### Fixed
- Central write tools sending payload as query params instead of JSON body — pycentral `command()` uses `api_data` for request body, not `api_params`
- Added `api_data` parameter to `retry_central_command` for POST/PUT body support

[v0.7.19]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.19

## [v0.7.18] - 2026-04-14

### Fixed
- Central write tools using wrong API version (`v1` instead of `v1alpha1`) for sites, site-collections, and device-groups endpoints, causing DNS resolution failures

[v0.7.18]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.18

## [v0.7.17] - 2026-04-14

### Changed — Write Tool Confirmation
- Create operations now execute immediately without confirmation
- Update and delete operations require user confirmation (via elicitation prompt or AI chat confirmation)
- Matches the expected behavior: creates are safe, updates/deletes need approval

[v0.7.17]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.17

## [v0.7.16] - 2026-04-14

### Fixed — Write Tool Confirmation
- When `DISABLE_ELICITATION=false` and the client doesn't support elicitation prompts, write tools now return a `confirmation_required` response instructing the AI to confirm with the user in chat before re-calling the tool
- Previously, write tools auto-accepted silently when the client lacked elicitation support, bypassing user confirmation entirely

### Changed
- Elicitation middleware now tracks three modes: `disabled` (auto-accept), `prompt` (elicitation dialog), `chat_confirm` (AI asks user in conversation)

[v0.7.16]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.16

## [v0.7.15] - 2026-04-14

### Changed — Central Dynamic Registration (Issue #80)
- Converted Central tool registration from explicit imports to dynamic `TOOLS` dict + `importlib` pattern, matching Mist
- All 15 Central tool modules now use `_registry.mcp` decorator pattern instead of `register(mcp)` wrapper functions

### Fixed — Write Tool Visibility
- ElicitationMiddleware no longer overrides write tool visibility when client lacks elicitation support — write tools stay visible when enabled by config
- In-tool `elicitation_handler` now auto-accepts gracefully when client can't prompt (instead of throwing ToolError)
- Mist and Central write tools conditionally skip registration when their platform write flag is disabled

### Removed
- `ENABLE_WRITE_TOOLS` global flag — replaced by per-platform `ENABLE_MIST_WRITE_TOOLS` and `ENABLE_CENTRAL_WRITE_TOOLS`

[v0.7.15]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.15

## [v0.7.14] - 2026-04-13

### Added — Central Write Tools
- `central_manage_site` — create, update, and delete sites via `network-config/v1/sites`
- `central_manage_site_collection` — create, update, and delete site collections via `network-config/v1/site-collections`
- `central_manage_device_group` — create, update, and delete device groups via `network-config/v1/device-groups`
- All write tools gated behind `ENABLE_WRITE_TOOLS=true` with elicitation confirmation

### Fixed
- Write tool visibility: server.py Visibility transform and elicitation middleware now handle both `write` and `write_delete` tags consistently

### Changed
- Central tool count: 42 → 45 (+ 12 prompts)

[v0.7.14]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.14

## [v0.7.13] - 2026-04-13

### Added — Mist Best-Practice Guardrails
- `guardrails.py` validation module — inspects write tool payloads and warns when operations violate Mist best practices (site-level WLAN creation, hardcoded RADIUS IPs, fixed RF channels/power, static PSKs)
- Guardrails integrated into all 4 Mist write tools — warnings in elicitation message, suggestions in tool response
- `provision_site_from_template` prompt — guided workflow for cloning a site using templates
- `bulk_provision_sites` prompt — guided workflow for bulk site creation with source config analysis done once
- Mist Best Practices section in INSTRUCTIONS.md

### Added — Central Scope Tool Improvements
- Enriched scope tree output with `persona_count`, `resource_count`, `child_scope_count`, `device_count`, per-persona `categories` breakdown
- `include_details` parameter on `central_get_effective_config` — exposes full resource configuration data
- `inheritance_path` in effective config output — ordered path from Global to target scope
- `scope_configuration_overview` and `scope_effective_config` guided prompts
- Split `scope_builder.py` into `scope_builder.py` + `scope_queries.py`
- Mermaid diagram device labels now use hostnames instead of model numbers

### Changed
- Mist tool count: 35 tools + 2 prompts
- Central tool count: 42 tools + 12 prompts (was 10)
- Test count: 176 (was 119)

[v0.7.13]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.13

## [v0.7.12] - 2026-04-13

### Fixed
- Site update/delete calling nonexistent `mistapi.api.v1.orgs.sites.updateOrgSite` / `deleteOrgSite` — fixed to `mistapi.api.v1.sites.sites.updateSiteInfo(site_id)` and `deleteSite(site_id)`

[v0.7.12]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.12

## [v0.7.11] - 2026-04-13

### Added
- `sites` object type for `mist_change_org_configuration_objects` and `mist_update_org_configuration_objects` — enables site create, update, and delete via write tools

### Fixed
- Write tools failing with "AI App does not support elicitation" when both `ENABLE_WRITE_TOOLS=true` and `DISABLE_ELICITATION=true` — missing `ctx.set_state("disable_elicitation", True)` in the elicitation middleware

### Changed
- `__version__` now reads dynamically from package metadata instead of being hardcoded
- `pyproject.toml` is the single source of truth for version

[v0.7.11]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.11

## [v0.7.0] - 2026-04-03

### Added — Central Scope & Configuration Tools
- `central_get_scope_tree` — Full scope hierarchy (Global → Collections → Sites → Devices) with committed or effective view
- `central_get_scope_resources` — Configuration resources at a specific scope level, filterable by persona (AP, Switch, Gateway)
- `central_get_effective_config` — Show what configuration a device inherits and from which scope level
- `central_get_devices_in_scope` — List devices within a scope, filterable by device type
- `central_get_scope_diagram` — Pre-built Mermaid flowchart of the scope hierarchy with color-coded device types

### Added — Dependencies
- `treelib>=1.7.0` — Tree data structure for scope hierarchy building

### Changed
- Central tool count: 37 → 42 (+ 10 prompts)
- Total tools: 80 (dynamic mode) or 87 (static mode)

[v0.7.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.0

## [v0.6.6] - 2026-04-03

### Added
- `central_get_switch_hardware_trends` — Time-series hardware data per switch member (CPU, memory, temp, PoE capacity/consumption, power). Returns all stack members.
- `central_get_switch_poe` — Per-port PoE data showing powerDrawnInWatts per interface

### Improved
- PoE bounce: hardware-trends pre-check skips entire switch if total PoE consumption is zero (faster, avoids unnecessary per-port checks)
- PoE bounce: includes `total_poe_watts` in response for reporting

### Fixed
- Stack PoE reporting: `hardware-trends` returns all stack members, solving the conductor-only data issue

### Changed
- Central tool count: 35 → 37 (+ 10 prompts)
- Total tools: 75 (dynamic mode) or 82 (static mode)

[v0.6.6]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.6.6

## [v0.6.0] - 2026-04-02

### Added — Central
- `central_disconnect_users_ssid` — Disconnect all users from a specific SSID
- `central_disconnect_users_ap` — Disconnect all users from an AP
- `central_disconnect_client_ap` — Disconnect client by MAC from an AP
- `central_disconnect_client_gateway` — Disconnect client by MAC from a gateway
- `central_disconnect_clients_gateway` — Disconnect all clients from a gateway
- `central_port_bounce_switch` — Port bounce on CX switch
- `central_poe_bounce_switch` — PoE bounce on CX switch
- `central_port_bounce_gateway` — Port bounce on gateway
- `central_poe_bounce_gateway` — PoE bounce on gateway

### Added — Mist
- `mist_bounce_switch_port` — Port bounce on Juniper EX switch

### Added — Safety
- Port safety rules in INSTRUCTIONS.md — AI must check interfaces before bouncing
- Platform-specific port naming guidance (Aruba CX vs Juniper EX)

### Changed
- Mist tool count: 34 → 35
- Central tool count: 26 → 35 (+ 10 prompts)
- Total tools: 73 (dynamic mode) or 80 (static mode)

[v0.6.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.6.0

## [v0.5.1] - 2026-04-02

### Fixed
- `mist_search_device`: removed `vc_mac` parameter not supported by installed `mistapi` SDK version — fixes 503 errors on device search
- `mist_search_device`: use kwargs dict to only pass non-None parameters to SDK — prevents unexpected keyword argument errors
- Claude Desktop: switched from `mcp-remote` to `supergateway` for stdio-to-HTTP bridging — fixes tool call timeouts and session loss after system sleep
- Docker health check: use `uv run --no-sync python` instead of bare `python` to find httpx in the virtual environment — fixes persistent "unhealthy" status
- Docker Compose: default to local `build: .` instead of GHCR image for Apple Silicon / ARM compatibility

### Changed
- README: Claude Desktop setup now uses `supergateway` bridge with full troubleshooting guide
- README: Added troubleshooting for Claude Desktop configuration errors and tool timeouts

[v0.5.1]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.5.1

## [v0.5.0] - 2026-03-29

### Added — Central
- `central_get_audit_logs` — Retrieve audit logs with time range, OData filtering, and pagination
- `central_get_audit_log_detail` — Get detailed audit log entry by ID
- `central_get_ap_stats` — AP performance statistics with optional time range
- `central_get_ap_utilization` — AP CPU, memory, or PoE utilization trends
- `central_get_gateway_stats` — Gateway performance statistics
- `central_get_gateway_utilization` — Gateway CPU or memory utilization trends
- `central_get_gateway_wan_availability` — Gateway WAN uplink availability
- `central_get_tunnel_health` — IPSec tunnel health summary
- `central_ping` — Ping test from AP, CX switch, or gateway
- `central_traceroute` — Traceroute from AP, CX switch, or gateway
- `central_cable_test` — Cable test on switch ports
- `central_show_commands` — Execute show commands on devices
- `central_get_applications` — Application visibility per site (usage, risk, experience)

### Added — Mist
- `mist_get_wlans` — List WLANs/SSIDs at org or site level
- `mist_get_site_health` — Organization-wide site health overview
- `mist_get_ap_details` — Detailed AP info by device ID
- `mist_get_switch_details` — Detailed switch info by device ID
- `mist_get_gateway_details` — Detailed gateway info by device ID

### Changed
- Mist tool count: 29 → 34
- Central tool count: 13 → 26 (+ 10 prompts)
- Total tools: 63 (dynamic mode) or 70 (static mode)

[v0.5.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.5.0

## [v0.4.0] - 2026-03-28

### Added
- `central_get_wlans` — List all WLANs/SSIDs with filtering by site or AP
- `central_get_ap_details` — Detailed AP monitoring (model, status, firmware, radio info)
- `central_get_switch_details` — Detailed switch monitoring (health, deployment, firmware)
- `central_get_gateway_details` — Detailed gateway monitoring (interfaces, tunnels, health)

### Changed
- Central tool count: 9 → 13 tools (+ 10 prompts)
- Total tools across all platforms: 45 (dynamic mode) or 52 (static mode)

[v0.4.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.4.0

## [v0.3.3] - 2026-03-28

### Fixed
- All CI/CD pipeline failures (lint, format, mypy, bandit)
- Set `MCP_TOOL_MODE` default to `dynamic`

[v0.3.3]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.3.3

## [v0.2.0] - 2026-03-28

### Added
- Unified MCP server combining Juniper Mist, Aruba Central, and HPE GreenLake
- 49 tools: 29 Mist + 10 Central + 10 GreenLake
- 11 guided prompts for Central troubleshooting workflows
- Streamable HTTP transport on port 8000
- Docker Compose secrets for secure credential management (per-credential files at `/run/secrets/`)
- Elicitation middleware for write tool safety (user confirmation before mutations)
- NullStrip middleware for MCP client compatibility
- Write tools disabled by default (`ENABLE_WRITE_TOOLS=true` to enable)
- Platform auto-disable when credentials are missing
- Multi-stage Dockerfile with non-root user (`mcpuser`, uid 1000)
- `secrets/*.example` template files for all 9 credentials
- PRD and PRP documentation

### Platforms
- **Juniper Mist**: Account info, configuration objects (CRUD), device/client search, events, alarms, SLE metrics, RRM, rogue detection, firmware upgrades, Marvis troubleshooting
- **Aruba Central**: Site health, device inventory, client connectivity, alerts, events, 11 guided troubleshooting prompts
- **HPE GreenLake**: Audit logs, device inventory, subscriptions, user management, workspace management

[v0.2.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.2.0
