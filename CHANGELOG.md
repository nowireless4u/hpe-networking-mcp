# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
