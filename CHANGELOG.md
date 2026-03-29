# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Central tool count: 13 → 26 (+ 11 prompts)
- Total tools: 63 (dynamic mode) or 70 (static mode)

[v0.5.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.5.0

## [v0.4.0] - 2026-03-28

### Added
- `central_get_wlans` — List all WLANs/SSIDs with filtering by site or AP
- `central_get_ap_details` — Detailed AP monitoring (model, status, firmware, radio info)
- `central_get_switch_details` — Detailed switch monitoring (health, deployment, firmware)
- `central_get_gateway_details` — Detailed gateway monitoring (interfaces, tunnels, health)

### Changed
- Central tool count: 9 → 13 tools (+ 11 prompts)
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
