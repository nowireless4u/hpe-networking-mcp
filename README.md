# HPE Networking MCP Server

[![CI](https://github.com/nowireless4u/hpe-networking-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/nowireless4u/hpe-networking-mcp/actions/workflows/ci.yml)
[![Security](https://github.com/nowireless4u/hpe-networking-mcp/actions/workflows/security.yml/badge.svg)](https://github.com/nowireless4u/hpe-networking-mcp/actions/workflows/security.yml)

> **Unofficial / community project.** This repository is an independent, community-driven project. It is not affiliated with, endorsed by, sponsored by, or supported by Hewlett Packard Enterprise, Aruba Networks, or Juniper Networks. "HPE", "Aruba", "Aruba Central", "Aruba ClearPass", "HPE GreenLake", "Juniper", and "Juniper Mist" are trademarks of their respective owners and are used here only to describe what this software interoperates with. Please direct support and licensing questions about those products to the respective vendors.

A unified [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that brings **Juniper Mist**, **Aruba Central**, **HPE GreenLake**, **Aruba ClearPass**, **Juniper Apstra**, and **Axis Atmos Cloud** together into a single, deployable service. One container. One endpoint. All your HPE networking tools.

---

## Why?

Managing HPE networking infrastructure with AI assistants today means juggling multiple separate MCP servers — each with its own setup, credentials, and quirks. This project consolidates them into one:

| Category | Mist | Central | GreenLake | ClearPass | Apstra | Axis | AOS8 |
|----------|:----:|:-------:|:---------:|:---------:|:------:|:----:|:----:|
| **Sites / Health Overview** | ✅ | ✅ | — | — | — | — | ✅ |
| **WLANs / SSIDs** | ✅ | ✅ | — | — | — | — | ✅ |
| **Device Inventory** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Device Details (AP/Switch/GW)** | ✅ | ✅ | — | — | — | — | ✅ |
| **Device Stats & Utilization** | ✅ | ✅ | — | — | — | ✅ | ✅ |
| **Client Connectivity** | ✅ | ✅ | — | — | — | — | ✅ |
| **Events** | ✅ | ✅ | — | ✅ | — | — | ✅ |
| **Alerts / Alarms** | ✅ | ✅ | — | ✅ | ✅ | — | ✅ |
| **Audit Logs** | ✅ | ✅ | ✅ | ✅ | — | — | ✅ |
| **Application Visibility** | — | ✅ | — | — | — | ✅ | — |
| **SLE / Performance Metrics** | ✅ | — | — | — | — | — | — |
| **Troubleshooting (Ping/Traceroute/Bounce)** | ✅ | ✅ | — | — | — | — | ✅ |
| **Session Control / Client Disconnect** | — | ✅ | — | ✅ | — | — | ✅ |
| **Configuration Management** | ✅ | — | — | ✅ | ✅ | ✅ | ✅ |
| **Configuration Write (CRUD)** | ✅ | — | — | ✅ | ✅ | ✅ | ✅ (gated) |
| **Radio Resource Management** | ✅ | — | — | — | — | — | ✅ |
| **Rogue AP Detection** | ✅ | — | — | — | — | — | ✅ |
| **Firmware Management** | ✅ | — | — | — | — | — | ✅ |
| **Subscriptions / Licensing** | — | — | ✅ | ✅ | — | — | ✅ |
| **User Management** | — | — | ✅ | ✅ | — | ✅ | — |
| **Workspaces** | — | — | ✅ | — | — | — | — |
| **Scope & Configuration Hierarchy** | — | ✅ | — | — | — | ✅ | ✅ |
| **Guest Management** | — | — | — | ✅ | — | — | — |
| **NAC / Policy Management** | — | — | — | ✅ | — | — | — |
| **Endpoint Profiling** | — | — | — | ✅ | — | — | — |
| **Certificates** | — | — | — | ✅ | — | — | — |
| **Datacenter Blueprints / Templates** | — | — | — | — | ✅ | — | — |
| **Virtual Networks / EVPN / Routing Zones** | — | — | — | — | ✅ | — | — |
| **Connectivity Templates / Policy Apply** | — | — | — | — | ✅ | — | — |
| **Fabric Deploy / Diff Status** | — | — | — | — | ✅ | — | — |
| **BGP / Protocol Session Monitoring** | — | — | — | — | ✅ | — | — |
| **SASE Cloud Connectors / Tunnels** | — | — | — | — | — | ✅ | — |
| **URL / Web Category Filtering** | — | — | — | — | — | ✅ | — |
| **SSL Inspection Exclusions** | — | — | — | — | — | ✅ | — |
| **Staged Writes + Commit Workflow** | — | — | — | — | ✅ | ✅ | — |
| **Guided Prompts** | ✅ | ✅ | — | — | — | — | ✅ |
| **Dynamic Tool Discovery** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Underlying tools** | **35 + 2 prompts** | **87 + 12 prompts** | **10** | **140** | **19** | **25** | **47 + 9 prompts** |
| **Exposed meta-tools (dynamic mode)** | **3** | **3** | **3** | **3** | **3** | **3** | **3** |
| **Cross-Platform** | **3 tools + 3 prompts** | **3 tools + 3 prompts** | — | **1 tool** | — | — | — |

> **Default tool surface (v3.0.0.0+)**: ships with `MCP_TOOL_MODE=code` by default. Code mode exposes only `execute` + 5 discovery tools (`tags`, `search`, `get_schema`, `skills_list`, `skills_load`); all 367 underlying tools are reachable via `await call_tool(name, params)` inside a sandboxed Python `execute()` block. Smallest initial token cost (~minimal context); best for orchestrators driving small / local LLMs. Set `MCP_TOOL_MODE=dynamic` to use the v2.x default behavior — each platform exposes 3 meta-tools (`<platform>_list_tools`, `<platform>_get_tool_schema`, `<platform>_invoke_tool`) plus the 4 cross-platform static tools and 2 skills tools (24 total surface, ~3,700 tokens). The `static` mode was REMOVED in v3.0.0.0. Every tool's response is wrapped in a uniform envelope `{ok, status, data, message, tool, platform}`. v2.3.0.0 introduces **Skills** — markdown-defined multi-step procedures discoverable via `skills_list` / `skills_load`; see [docs/TOOLS.md#skills](docs/TOOLS.md). v2.4.0.0 adds **AOS8** (47 tools + 9 prompts) — see [INSTRUCTIONS.md](INSTRUCTIONS.md) for AOS8-specific operator guidance. See [docs/MIGRATING_TO_V2.md](docs/MIGRATING_TO_V2.md).

### Aruba Central Guided Prompts

The Central module includes 12 guided prompts — multi-step workflow templates that walk the AI through common network operations tasks using the available tools. These prompts orchestrate multiple tool calls in the correct order, so you can simply invoke the prompt and let the AI handle the rest.

- **Network Health Overview** — Assess the health of all sites across your network, flagging those with poor scores or high alert counts for deeper investigation.
- **Troubleshoot Site** — Deep-dive into a specific site: check health metrics, review active alerts by severity, list all devices, and recommend next steps.
- **Client Connectivity Check** — Investigate a client by MAC address: find the client, check the connected device's health, review site-level alerts, and identify the likely root cause.
- **Investigate Device Events** — Pull recent events for a specific device to build a timeline of what happened, highlight recurring issues, and suggest follow-up actions.
- **Site Event Summary** — Summarize all events at a site over a time window, grouped by category and type, to spot patterns and anomalies.
- **Failed Clients Investigation** — Find all failed client connections at a site, check the health of the devices they were connected to, and identify common failure patterns.
- **Site Client Overview** — Get a breakdown of all clients at a site by connection type, status, VLAN, and WLAN to understand the connectivity landscape.
- **Device Type Health** — Check the health of all devices of a specific type (AP, switch, or gateway) at a site, including alerts and recent event activity.
- **Critical Alerts Review** — Review all active critical alerts across the entire network, grouped by site and category, with recommended immediate actions.
- **Compare Site Health** — Side-by-side comparison of health scores, device counts, client counts, and alert breakdowns across multiple sites.
- **Scope Configuration Overview** — View committed configuration resources at a scope level, grouped by persona and category.
- **Scope Effective Config** — View effective (inherited + committed) configuration at a scope, showing what each level contributes.

### AOS8 Guided Prompts

The AOS8 module includes 9 guided prompts for common Mobility Conductor operator workflows. See [INSTRUCTIONS.md](INSTRUCTIONS.md) for the complete parameter reference and workflow descriptions.

- **Triage Client** (`aos8_triage_client`) — Find a client by MAC, check AP health, review auth/association events, identify likely root cause.
- **Triage AP** (`aos8_triage_ap`) — Deep-dive an AP: radio state, clients, alarms, ARM history, event timeline.
- **Health Check** (`aos8_health_check`) — Network-wide health: controllers, AP counts, clients, alarms, firmware drift.
- **Audit Change** (`aos8_audit_change`) — Recent audit-trail review with high-risk-change flagging.
- **RF Analysis** (`aos8_rf_analysis`) — Channel distribution, co-channel clusters, ARM oscillation, interferers/rogues.
- **WLAN Review** (`aos8_wlan_review`) — SSID/VAP/AP-group/role inventory and consistency check.
- **Client Flood** (`aos8_client_flood`) — High-client-count / failed-connection investigation at a scope.
- **Compare MD Config** (`aos8_compare_md_config`) — Side-by-side effective-config diff between two MDs or AP groups.
- **Pre-Change Check** (`aos8_pre_change_check`) — Pre-maintenance checklist: alarms, controller stats, audit trail, pending changes, write_memory reminder.

### Cross-Platform Tools

Tools that span multiple platforms and return pre-aggregated results — each one replaces several individual tool calls, so the AI gets a compact answer instead of paging through raw responses.

- **Site Health Check** (`site_health_check`) — One call returns a unified health report for a site across every enabled platform: Mist site stats and alarms, Central site health and active alerts, and (when ClearPass is configured) session and auth-failure counts for the site's network access devices. Replaces ~8–12 separate tool calls with a compact report including overall status, top alerts, and concrete next-step recommendations. Registered when at least Mist or Central is enabled; ClearPass is additive.
- **Site RF Check** (`site_rf_check`) — One call returns per-AP, per-band radio state from Mist AND Central in parallel: current channel, bandwidth, TX power, channel utilization, and noise floor for every AP at a site. Aggregates the channel distribution per band (2.4 / 5 / 6 GHz), flags co-channel clusters and high utilization, and ships a pre-rendered ASCII RF dashboard so even clients that don't draw charts get a visual report. When `site_name` is omitted the tool returns a list of selectable sites with AP counts per platform — pick one and call back. Registered when at least Mist or Central is enabled.
- **Manage WLAN Profile** (`manage_wlan_profile`) — The primary entry point for all WLAN operations. Automatically checks both Mist and Central for the SSID and returns the correct sync workflow. Detects cross-platform scenarios without relying on the AI to follow instructions. Requires both Mist and Central.

#### Cross-Platform WLAN Sync Prompts

- **Sync WLANs Mist → Central** — Resolve Mist template variables, map fields, create Central WLAN profiles, assign to matching scopes.
- **Sync WLANs Central → Mist** — Resolve Central aliases, server groups, and named VLANs, create Mist WLANs with template variables.
- **Sync WLANs Bidirectional** — Compare WLANs across both platforms, show field-level differences, and sync in either direction.

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Get the Project

```bash
git clone https://github.com/nowireless4u/hpe-networking-mcp.git
cd hpe-networking-mcp
```

> **No build required.** The `docker-compose.yml` pulls a pre-built image from GitHub Container Registry by default. To build from source instead, edit `docker-compose.yml` and swap `image:` for `build: .`.

### 2. Configure Secrets

The repo ships with `.example` template files only — **no real secret files**. You create the real files yourself by copying the examples and editing them with your values.

**Important:** `docker-compose.yml` declares every platform's secrets and bind-mounts each of them into the container at startup. If a listed secret file doesn't exist on disk, the container fails immediately with an `invalid mount config` error — **before the app ever runs.** That means you need to pick one of two paths:

- **Path A (most users):** populate every `.example` → real-name pair for every platform listed in the compose file, even the platforms you don't currently use (put dummy content in the unused ones — the app will disable the platform at runtime, see below).
- **Path B (recommended if you only use some platforms):** create a `docker-compose.override.yml` that removes the unused platforms' secret references so compose stops trying to bind them. See **Disabling platforms you don't use** below.

For the platforms you actually want enabled, copy the templates and edit them with real values:

```bash
# Mist (required for this example; do the same for every platform you're using)
cp secrets/mist_api_token.example secrets/mist_api_token
cp secrets/mist_host.example secrets/mist_host
# Edit each file with your real credentials

# Aruba Central
cp secrets/central_base_url.example secrets/central_base_url
cp secrets/central_client_id.example secrets/central_client_id
cp secrets/central_client_secret.example secrets/central_client_secret

# HPE GreenLake
cp secrets/greenlake_api_base_url.example secrets/greenlake_api_base_url
cp secrets/greenlake_client_id.example secrets/greenlake_client_id
cp secrets/greenlake_client_secret.example secrets/greenlake_client_secret
cp secrets/greenlake_workspace_id.example secrets/greenlake_workspace_id

# ClearPass
cp secrets/clearpass_server.example secrets/clearpass_server
cp secrets/clearpass_client_id.example secrets/clearpass_client_id
cp secrets/clearpass_client_secret.example secrets/clearpass_client_secret
cp secrets/clearpass_verify_ssl.example secrets/clearpass_verify_ssl

# Juniper Apstra
cp secrets/apstra_server.example secrets/apstra_server
cp secrets/apstra_port.example secrets/apstra_port
cp secrets/apstra_username.example secrets/apstra_username
cp secrets/apstra_password.example secrets/apstra_password
cp secrets/apstra_verify_ssl.example secrets/apstra_verify_ssl

# Axis Atmos Cloud
cp secrets/axis_api_token.example secrets/axis_api_token
```

> **Axis token note**: Generate the token in the Axis admin portal at *Settings → Admin API → New API Token*. Pick read or read+write scope and an expiration. The MCP server decodes the JWT's `exp` claim at startup and logs a warning when the token has fewer than 30 days remaining; the `health` tool also surfaces a `token_expires_in_days` countdown when inside that window. There is no refresh — regenerate the token in the portal before it lapses.

Each file contains a single value (e.g., your API token). **Do not leave placeholder contents** (like `apstra.example.com` or `replace-with-real-password`) in a file for a platform you're not using — the server will try to authenticate with those fake values at startup and fill your logs with failed-login errors. If you're not using a platform, use Path B below (override file) or leave the secret file empty — the app treats an empty file as "not configured" and disables the platform.

### 3. Disable platforms you don't use (recommended)

Create a `docker-compose.override.yml` alongside `docker-compose.yml`. Compose auto-merges it at startup, and the committed `docker-compose.yml` stays untouched. A ready-to-copy template is shipped in the repo:

```bash
cp docker-compose.override.yml.example docker-compose.override.yml
# edit to match the platforms you actually use
```

The template shows a Mist-only deployment with `!reset` directives dropping every other platform's secret references — both the service-level `secrets:` list **and** the top-level `secrets:` block, which you need to do both halves of for Compose to stop trying to bind-mount the unused files. Adjust the `secrets: !reset - <names>` under `services:` to keep whichever platforms you need, and `!reset` only the top-level entries you're actually dropping. The template also has examples for per-platform write-tool flags, log level, and tool mode overrides.

`docker-compose.override.yml` is already in `.gitignore`, so your per-deployment tailoring never ends up in git. With the Mist-only override in place, you only need `secrets/mist_api_token` and `secrets/mist_host` on disk — every other secret file can be absent.

> **Compose version required:** `!reset` needs Docker Compose v2.24 or newer. If you're on an older Compose, either upgrade (recommended) or skip the override file and edit `docker-compose.yml` directly, commenting out the unused platform's service-level and top-level secret entries.

### 4. Start

```bash
docker compose up -d
```

### 5. Verify

```bash
docker compose logs
```

Look for lines like `Mist: 35 underlying tools registered (code mode)`, `ClearPass: 140 underlying tools registered (code mode)`, `Axis: 25 underlying tools registered (code mode)`, `AOS8: 47 underlying tools (code mode)`, `Tool mode: code`, and `Uvicorn running on http://0.0.0.0:8000`. Your MCP server is running at `http://localhost:8000/mcp`. In the default code mode (since v3.0.0.0), only `execute` + 5 discovery tools (`tags`, `search`, `get_schema`, `skills_list`, `skills_load`) are exposed at the top level; all 367 underlying tools are reachable via `await call_tool(name, params)` inside a sandboxed Python `execute()` block. Set `MCP_TOOL_MODE=dynamic` to use the v2.x meta-tool surface instead. Mist registers 2 guided prompts; Central registers 12; AOS8 registers 9.

### Docker Image

The pre-built image is available on GitHub Container Registry:

```
ghcr.io/nowireless4u/hpe-networking-mcp:latest
ghcr.io/nowireless4u/hpe-networking-mcp:0.6.0
```

You can also pull it directly:

```bash
docker pull ghcr.io/nowireless4u/hpe-networking-mcp:latest
```

---

## Platform Auto-Disable

You don't need credentials for all seven platforms. The server detects which platforms have valid secret content at startup and only enables those. A platform is disabled if any of its required secret files is **empty or absent** from `SECRETS_DIR` (inside the container) — which, under Docker Compose, means the file on disk was empty or you used a `docker-compose.override.yml` to drop that platform's secrets entirely (see [Disable platforms you don't use](#3-disable-platforms-you-dont-use-recommended)).

- **All seven platforms configured** → All tools available (Mist + Central + GreenLake + ClearPass + Apstra + Axis + AOS8)
- **Only Mist configured** → Only `mist_*` tools available; other platforms disabled
- **Only AOS8 configured** → Only `aos8_*` tools available; other platforms disabled
- **Only ClearPass configured** → Only `clearpass_*` tools available; other platforms disabled
- **No valid credentials** → Server refuses to start with a clear error message

Add a platform later by populating its secret files (or removing the override's `!reset` lines) and restarting the container. The server logs which platforms are enabled at startup:

```
Mist: credentials loaded (token: abcd...wxyz, host: api.mist.com)
Central: disabled (missing secrets: central_client_id, central_client_secret)
GreenLake: disabled (missing secrets: greenlake_client_id)
AOS8: disabled (missing secrets: aos8_host)
Enabled platforms: mist
Tool mode: code
```

> **Heads up:** auto-disable triggers on **empty or absent secret content**, not on placeholder/example values. If you copy `apstra_server.example` → `apstra_server` and leave the contents as `apstra.example.com`, the server thinks Apstra is configured and tries to authenticate against the fake host — your logs fill with login errors. Either empty those files, drop the platform via `docker-compose.override.yml`, or fill in real values.

---

## Connect Your AI Client

### Claude Desktop

Claude Desktop doesn't natively support streamable HTTP, so it needs a stdio-to-HTTP bridge called `supergateway`. This bridge translates between Claude Desktop's stdio protocol and the MCP server's HTTP endpoint.

**Prerequisites:** [Node.js](https://nodejs.org/) must be installed on your machine. Verify with `npx --version` in your terminal.

**Step 1:** Open the Claude Desktop configuration file in a text editor:

| OS | File Location |
|----|---------------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |

> **Tip:** You can also open this file from within Claude Desktop: go to **Settings** (gear icon) > **Developer** > **Edit Config**.

**Step 2:** If the file is empty or doesn't exist, paste this entire block as-is:

```json
{
  "mcpServers": {
    "hpe-networking": {
      "command": "npx",
      "args": ["-y", "supergateway", "--streamableHttp", "http://localhost:8000/mcp"]
    }
  }
}
```

If you **already have other MCP servers** configured, add the `"hpe-networking"` entry inside the existing `"mcpServers"` object. Do **not** create a second `"mcpServers"` key. For example, if you already have a server called `"my-other-server"`:

```json
{
  "mcpServers": {
    "my-other-server": {
      "command": "some-command",
      "args": ["some-args"]
    },
    "hpe-networking": {
      "command": "npx",
      "args": ["-y", "supergateway", "--streamableHttp", "http://localhost:8000/mcp"]
    }
  }
}
```

> **Common mistakes:**
> - Missing comma between server entries (add a `,` after the closing `}` of the previous server)
> - Duplicate `"mcpServers"` keys (only one is allowed — merge your servers into it)
> - Trailing comma after the last entry (JSON does not allow trailing commas)
> - Editing the wrong file or creating a new file instead of editing the existing one

**Step 3:** Save the file and **fully restart Claude Desktop** (quit and reopen, not just close the window). MCP servers are discovered at startup — changes won't take effect until you restart.

**Step 4:** Verify the server connected. In Claude Desktop, look for the MCP server icon (hammer) in the chat input area. Click it — you should see `hpe-networking` listed with its tools.

### Claude Code

No config file needed — run this single command:

```bash
claude mcp add hpe-networking --transport http http://localhost:8000/mcp
```

### VS Code / GitHub Copilot

Add to your `.vscode/mcp.json` (create the file if it doesn't exist) or VS Code MCP settings:

```json
{
  "servers": {
    "hpe-networking": {
      "type": "streamable-http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

---

## PII Tokenization (v2.3.1.0+)

Tool responses are walked before reaching the AI:

- **MAC normalization (always-on, no toggle)** — every MAC address in tool responses is rewritten to canonical `aa:bb:cc:dd:ee:ff` form (lowercase, colon-separated). Mist's API returns MACs in four different formats across endpoints; consistent format means the AI can correlate `aa:bb:cc:dd:ee:ff` to itself across audits.
- **PII tokenization (opt-in via `ENABLE_PII_TOKENIZATION=true`)** — sensitive fields (PSKs, RADIUS secrets, certificates) and customer-identifying values (hostnames, FQDNs, emails, usernames, hardware serials) are replaced with session-stable `[[KIND:uuid]]` tokens before reaching the AI. The AI can pass tokens back into write tools and the inbound side substitutes plaintext before the API call. Storage is in-memory only; the keymap is keyed by `Mcp-Session-Id` and never touches disk.

**Deliberately NOT tokenized:**
- **MAC addresses** — observable to anyone in radio range (BSSID broadcast, client probe requests). Normalized only.
- **SSIDs / ESSIDs** — broadcast in beacon frames (refined in v2.3.1.1).
- **Platform UUIDs** like `org_id`, `site_id`, `device_id`, `template_id` — already opaque random identifiers in Mist's API; replacing one UUID with another adds no privacy (refined in v2.3.1.1).
- **Geographic data** — `address`, `city`, `state`, `zip`, `latitude`, `longitude`, `room`, `building` — typically findable on the company's website (refined in v2.3.1.1).
- **All IP addresses** (v2.3.1.2) — internal RFC1918, public WAN, CIDR ranges. Internal subnet topology is generally known to anyone on-network, and CIDR / route analysis is a core audit task.

**Always tokenized regardless of field name (v2.3.1.2):**
- **Email addresses** — caught even when the field is named `name`, `username`, or anything else. Mist's MPSK pattern of using the user's email as the PSK display name was a leak before this.
- **AWS-signed URL credentials** — any string containing `X-Amz-Security-Token`, `X-Amz-Credential`, or `X-Amz-Signature` is treated as a temporary AWS credential and tokenized whole as `APITOKEN`. Catches the `portal_template_url` leak from Mist's S3-backed captive-portal previews.

**Central coverage (v2.3.1.3):** the ruleset now also covers Central response shapes — `user_name`, `updated_by`, `created_by` (audit-log fields) tokenize as `USER`; hyphenated keys like `wpa-passphrase` and `shared-secret` match the same secret rules as their snake_case equivalents. Central organizational structure (`device_group_name`, `scope_name`) passes through as cleartext.

**Round-trip works for every kind.** Same plaintext → same token within a session. WLAN sync, AOS 8 → AOS 10 migration, and mass PSK rotation all work because tokenization is round-trippable.

**What the AI never sees in its context window:** WPA / SAE / WEP keys; RADIUS / RadSec / SNMP / admin / VPN secrets; API tokens (including AWS-signed URLs); certificates and private keys; hostnames / FQDNs / device names; **email addresses (anywhere they appear)**; usernames and personal names; phone numbers; hardware serial numbers / IMEI / IMSI / ICCID; embedded secrets in description/notes fields. **What it does see:** tokens for those values, MACs (normalized), SSIDs, platform UUIDs, geographic data, **all IP addresses (internal + public)**, and unchanged metric/enum/timestamp fields.

Audit logging fires on every tokenize/detokenize event in `docker compose logs` — kind, token ID, value-hash (SHA-256 truncated), but never the plaintext.

> **Limitations:** Mist ruleset only this release; Central / GreenLake / ClearPass / Apstra / Axis follow in the next minor. Anything the user pastes into the AI prompt is outside our threat model — that turn already has the literal in conversation context. The keymap dies on server restart; saved chat references to old tokens become unresolvable.

## Network Security

The MCP HTTP transport ships with two layers of defense out of the box:

1. **Loopback-only port publish** — `docker-compose.yml` publishes `127.0.0.1:8000:8000`, so only processes on the host can reach the MCP endpoint. No LAN host can connect, even if it knows the IP. (Inside the container the app still binds `0.0.0.0` — that's the container's *own* network namespace and is what Docker's port-forwarder forwards into; do not change it.)
2. **`Origin` header allowlist** — required by the MCP Streamable HTTP spec to defend against browser-driven DNS rebinding. The server rejects any request whose `Origin` is set to a value outside `ALLOWED_ORIGINS` (default: `localhost` and `127.0.0.1`). Non-browser clients (supergateway, curl, native MCP clients) don't send `Origin` and pass through.

If you put the server behind an authenticating reverse proxy that already validates origins, set `ALLOWED_ORIGINS=*` to bypass the in-process check. See the [Configuration](#configuration) table for details.

> **Multi-host / remote access is not a supported configuration.** The server has no built-in authentication on `/mcp` — anyone who can reach the port has full admin of every connected platform. If you need remote access, terminate at a reverse proxy (nginx + mTLS / OIDC, Cloudflare Access, Tailscale Funnel, etc.) and never expose the published port directly.

## Secrets

This project uses **Docker Compose secrets** for credential management — the most secure native Docker approach:

- Each credential is a **separate file** in the `secrets/` directory
- Files are mounted **read-only** at `/run/secrets/` inside the container
- Secrets are **never** baked into the Docker image, exposed in `docker inspect`, or stored as environment variables
- Real secret files are **git-ignored** — only `.example` templates are committed

### How It Works

```
secrets/
├── mist_api_token.example      # Template (committed to git)
├── mist_api_token              # Your real secret (git-ignored)
├── mist_host.example
├── mist_host
└── ...
```

Docker Compose reads these files and mounts them at `/run/secrets/<name>` inside the container. The server reads each file at startup.

### Platform Credentials

#### Juniper Mist

| Secret File | Description | How to Obtain |
|-------------|-------------|---------------|
| `mist_api_token` | Mist API token | Mist Dashboard > Organization > Settings > API Token |
| `mist_host` | Mist API host | `api.mist.com` (Global), `api.eu.mist.com` (EU), `api.gc1.mist.com` (GovCloud) |

#### Aruba Central

| Secret File | Description | How to Obtain |
|-------------|-------------|---------------|
| `central_base_url` | Central API gateway URL | HPE GreenLake Platform > Aruba Central > API Gateway |
| `central_client_id` | OAuth2 client ID | HPE GreenLake Platform > API Clients |
| `central_client_secret` | OAuth2 client secret | HPE GreenLake Platform > API Clients |

#### HPE GreenLake

| Secret File | Description | How to Obtain |
|-------------|-------------|---------------|
| `greenlake_api_base_url` | GreenLake API base URL | Typically `https://global.api.greenlake.hpe.com` |
| `greenlake_client_id` | OAuth2 client ID | HPE GreenLake Platform > API Clients |
| `greenlake_client_secret` | OAuth2 client secret | HPE GreenLake Platform > API Clients |
| `greenlake_workspace_id` | GreenLake workspace ID | HPE GreenLake Platform > Workspaces |

#### Aruba ClearPass

| Secret File | Description | How to Obtain |
|-------------|-------------|---------------|
| `clearpass_server` | ClearPass API URL | `https://your-clearpass-server/api` — the CPPM server hostname with `/api` path |
| `clearpass_client_id` | OAuth2 client ID | ClearPass Admin > API Clients > Create API Client |
| `clearpass_client_secret` | OAuth2 client secret | ClearPass Admin > API Clients > Client Secret |
| `clearpass_verify_ssl` | SSL verification (optional) | `true` (default) or `false` for self-signed certificates |

#### Aruba OS 8 / Mobility Conductor

| Secret File | Required | Default | Purpose |
|---|---|---|---|
| `aos8_host` | yes | — | Conductor or standalone controller hostname/IP |
| `aos8_username` | yes | — | API username with sufficient role |
| `aos8_password` | yes | — | API password |
| `aos8_port` | no | `4343` | HTTPS port (Mobility Conductor API port) |
| `aos8_verify_ssl` | no | `true` | Set to `false` for self-signed certs (logged as WARNING) |

Set `ENABLE_AOS8_WRITE_TOOLS=true` to expose the 12 AOS8 write tools (gated by elicitation middleware; default `false`).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                       MCP Client (Claude, VS Code, etc.)                                │
└───────────────────────────────────────┬─────────────────────────────────────────────────┘
                                        │ Streamable HTTP
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│      HPE Networking MCP Server (:8000)  —  MCP_TOOL_MODE=code (default since v3.0.0.0) │
│                                                                                         │
│   Exposed to the AI  (6 tools in code mode):                                            │
│     • execute (sandboxed Python; await call_tool(name, params) inside)                  │
│     • 5 discovery tools: tags, search, get_schema, skills_list, skills_load             │
│   Set MCP_TOOL_MODE=dynamic to use the v2.x meta-tool surface (24 tools).               │
│                                                                                         │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │
│ │  Mist  │ │Central │ │GreenLk │ │ClrPass │ │ Apstra │ │  Axis  │ │  AOS8  │           │
│ │ mist_* │ │centrl_*│ │grnlake │ │clrpass │ │apstra_*│ │ axis_* │ │ aos8_* │           │
│ │35 tools│ │87 tools│ │10 tools│ │140 tool│ │19 tools│ │25 tools│ │47 tools│           │
│ │+2 prmt │ │+12prmt │ │        │ │        │ │        │ │        │ │+9 prmt │           │
│                                                                                         │
│  All 367 underlying tools reachable via call_tool() in code mode or via                 │
│  per-platform meta-tools (<platform>_list_tools / get_schema / invoke) in dynamic mode. │
│ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘           │
│     │          │          │          │          │          │          │                 │
└─────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┘
      ▼          ▼          ▼          ▼          ▼          ▼          ▼
  Mist Cloud  Aruba    GreenLake  ClearPass    Apstra      Axis    Mobility
     API      Central     API       CPPM API  Fabric API  Atmos   Conductor
              API                                          Cloud      API
```

**Key design decisions:**

- **FastMCP** framework with Python 3.12+
- **Streamable HTTP** transport (modern MCP standard)
- **Code tool mode by default (since v3.0.0.0)** — only `execute` + 5 discovery tools exposed; all 367 underlying tools reachable via `await call_tool(name, params)` inside the sandbox. Smallest initial token cost; best for orchestrators driving small / local LLMs. Set `MCP_TOOL_MODE=dynamic` for the v2.x meta-tool surface (24 tools, ~3,700 tokens).
- **Tool namespacing** — `mist_*`, `central_*`, `greenlake_*`, `clearpass_*`, `apstra_*`, `axis_*` prefixes prevent collisions
- **Platform isolation** — each module manages its own API client and auth; a failing platform doesn't affect the others
- **Non-root container** — runs as `mcpuser` (uid 1000)

---

## Write Operations and Safety

Write/mutation tools (e.g., creating WLANs in Mist, modifying configurations) are supported with safety controls:

- **Disabled by default** — enable per-platform with `ENABLE_MIST_WRITE_TOOLS=true`, `ENABLE_CENTRAL_WRITE_TOOLS=true`, `ENABLE_CLEARPASS_WRITE_TOOLS=true`, `ENABLE_APSTRA_WRITE_TOOLS=true`, `ENABLE_AXIS_WRITE_TOOLS=true`, or `ENABLE_AOS8_WRITE_TOOLS=true`
- **Elicitation required** — write tools prompt for user confirmation before executing
- **Annotation-based** — all tools carry MCP annotations (`readOnlyHint`, `destructiveHint`, etc.)

| Environment Variable | Default | Effect |
|---------------------|---------|--------|
| `ENABLE_MIST_WRITE_TOOLS` | `false` | Enable Mist write/mutation tools |
| `ENABLE_CENTRAL_WRITE_TOOLS` | `false` | Enable Central write/mutation tools |
| `ENABLE_CLEARPASS_WRITE_TOOLS` | `false` | Enable ClearPass write/mutation tools |
| `ENABLE_APSTRA_WRITE_TOOLS` | `false` | Enable Apstra write/mutation tools |
| `ENABLE_AXIS_WRITE_TOOLS` | `false` | Enable Axis Atmos Cloud write/mutation tools (every write stages — call `axis_commit_changes` to apply) |
| `ENABLE_AOS8_WRITE_TOOLS` | `false` | Enable AOS8 write tools (12 tools; every write returns `requires_write_memory_for` — call `aos8_write_memory` explicitly) |
| `DISABLE_ELICITATION` | `false` | Skip user confirmation for write tools (**use with caution**) |

---

## Reliability

The server transparently retries transient API failures so the AI doesn't have to reason about flakey upstream services.

- **5xx errors on read tools** — auto-retried with exponential backoff (1s, 2s, 4s — 3 attempts total)
- **429 rate-limit responses** — retried on both reads and writes (always safe — the server is asking us to slow down). Honors the `Retry-After` response header when present, capped at 60s
- **Write tools (5xx)** — never auto-retried for idempotency safety. The error surfaces to the AI which can decide whether to re-issue
- **4xx errors (other than 429)** — never retried; surface immediately

The retry logic detects transient failures in two patterns: response-dict (Mist/Central/ClearPass return `{"status_code": 503, ...}`) and httpx exception (GreenLake/Apstra/Axis raise `httpx.HTTPStatusError`). Read/write classification is via the underlying tool's tags — anything tagged `*_write` or `*_write_delete` is treated as a write.

| Environment Variable | Default | Effect |
|---------------------|---------|--------|
| `RETRY_MAX_ATTEMPTS` | `3` | Max attempts including the first call. Set to `1` to disable retry entirely |
| `RETRY_INITIAL_DELAY` | `1.0` | Initial backoff delay in seconds (doubles per attempt up to `RETRY_MAX_DELAY`) |
| `RETRY_MAX_DELAY` | `60.0` | Cap on a single sleep — also caps `Retry-After` header values |

---

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `MCP_PORT` | `8000` | Port the MCP server listens on |
| `MCP_HOST` | `0.0.0.0` | Bind address **inside the container's namespace** — leave at `0.0.0.0` so Docker's port-forwarder can reach the app. Restrict who can reach the host port via `ports:` in compose, not this. |
| `ALLOWED_ORIGINS` | `http://localhost:<MCP_PORT>,http://127.0.0.1:<MCP_PORT>` | Comma-separated allowlist for the `Origin` request header (DNS-rebinding defense per MCP spec). Browsers always send `Origin`; non-browser clients (supergateway, curl) don't and pass through. Set to `*` to disable the check (use only behind an auth proxy). |
| `SECRETS_DIR` | `/run/secrets` | Directory containing Docker secret files |
| `LOG_LEVEL` | `info` | Logging level (`debug`, `info`, `warning`, `error`) |
| `ENABLE_MIST_WRITE_TOOLS` | `false` | Enable Mist write/mutation tools |
| `ENABLE_CENTRAL_WRITE_TOOLS` | `false` | Enable Central write/mutation tools |
| `ENABLE_CLEARPASS_WRITE_TOOLS` | `false` | Enable ClearPass write/mutation tools |
| `ENABLE_APSTRA_WRITE_TOOLS` | `false` | Enable Apstra write/mutation tools |
| `ENABLE_AXIS_WRITE_TOOLS` | `false` | Enable Axis write/mutation tools (staged; commit with `axis_commit_changes`) |
| `ENABLE_AOS8_WRITE_TOOLS` | `false` | Enable AOS8 write tools (call `aos8_write_memory` after each change to persist) |
| `DISABLE_ELICITATION` | `false` | Disable write confirmation prompts |
| `MCP_TOOL_MODE` | `code` | Tool exposure: `code` (default since v3.0.0.0 — 6 tools at top level: `execute` + 5 discovery; all 367 underlying tools reachable via `call_tool()` inside the sandbox) or `dynamic` (24 tools — 4 cross-platform + 21 per-platform meta-tools + 2 skills tools; underlying tools hidden until invoked via `<platform>_invoke_tool`). The `static` value was REMOVED in v3.0.0.0 |
| `RETRY_MAX_ATTEMPTS` | `3` | Max retry attempts on transient failures (5xx reads, 429 reads+writes). Set to `1` to disable retry |
| `RETRY_INITIAL_DELAY` | `1.0` | Initial retry backoff seconds (exponential: 1s, 2s, 4s) |
| `RETRY_MAX_DELAY` | `60.0` | Cap on a single retry sleep (also caps `Retry-After` header values) |
| `ENABLE_PII_TOKENIZATION` | `false` | Tokenize sensitive fields (PSKs, RADIUS secrets, hostnames, emails, etc.) in tool responses before they reach the AI. Round-trips: AI passes tokens back into write tools and the middleware substitutes plaintext. MAC normalization is always-on regardless of this toggle. See [PII Tokenization](#pii-tokenization-v2310) above. |
| `PII_MAX_TOKENS_PER_SESSION` | `10000` | Soft cap on the per-session keymap size. Cap-hit logs a warning and falls through with plaintext rather than erroring out the call. |

---

## Development

All development happens inside Docker containers.

### Build from Source

Edit `docker-compose.yml` — comment out `image:` and uncomment `build:`:

```yaml
services:
  hpe-networking-mcp:
    # image: ghcr.io/nowireless4u/hpe-networking-mcp:latest
    build: .
```

Then rebuild:

```bash
docker compose up -d --build
```

### Running Tests

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm \
  hpe-networking-mcp uv run pytest tests/ -v
```

### Full CI Check

Run this before pushing to catch issues early:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm \
  hpe-networking-mcp sh -c \
  "uv run ruff check . && uv run ruff format --check . && \
   uv run mypy src/ --ignore-missing-imports && uv run pytest tests/ -q"
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full development workflow.

---

## Project Structure

```
hpe-networking-mcp/
├── src/hpe_networking_mcp/
│   ├── __main__.py              # CLI entry point
│   ├── server.py                # FastMCP server setup and lifespan
│   ├── config.py                # Docker secrets loading and validation
│   ├── INSTRUCTIONS.md          # LLM instructions for all platforms
│   ├── middleware/              # null-strip, validation-catch, sandbox-error-catch, elicitation, retry
│   ├── skills/                  # Markdown-defined multi-step procedures + skills engine
│   └── platforms/
│       ├── _common/             # Shared tool registry + meta-tool factory (dynamic mode)
│       ├── health.py            # Cross-platform health probe tool
│       ├── mist/                # 35 Mist tools + 2 prompts + API client
│       ├── central/             # 87 Central tools + 12 prompts + API client
│       ├── greenlake/           # 10 GreenLake tools + OAuth2 client
│       ├── clearpass/           # 140 ClearPass tools + pyclearpass SDK client
│       ├── apstra/              # 19 Apstra tools + async httpx client
│       ├── axis/                # 25 Axis Atmos Cloud tools + httpx client (JWT bearer)
│       ├── aos8/                # 47 AOS8 tools + 9 prompts + UIDARUBA session client
│       ├── manage_wlan.py       # Cross-platform WLAN management tool
│       ├── sync_prompts.py      # Cross-platform WLAN sync prompts
│       ├── site_health_check.py # Cross-platform site health aggregator
│       └── site_rf_check.py     # Cross-platform Wi-Fi RF dashboard
├── tests/                       # Unit and integration tests (964+ unit tests)
├── docs/                        # PRD, PRP, tool reference
├── secrets/                     # Secret files (only .example committed)
├── .github/workflows/           # CI, security, Docker publish
├── Dockerfile                   # Multi-stage build, non-root user
├── docker-compose.yml           # Production (pulls GHCR image)
└── docker-compose.dev.yml       # Development (mounts tests)
```

---

## Troubleshooting

### Viewing Logs

Always start here when something isn't working:

```bash
docker compose logs                        # All logs
docker compose logs --tail 50              # Last 50 lines
docker compose logs -f                     # Follow live
```

### Platform Disabled at Startup

If a platform shows as disabled, the relevant secret file is either absent or empty from the container's perspective:

```
Mist: disabled (mist_api_token secret not found)
Central: disabled (missing secrets: central_client_id, central_client_secret)
```

**Fix:** Populate the missing secret files in `secrets/` with real values (no extra whitespace or newlines — each file should contain exactly one value). If you *intended* to disable that platform, ignore the message — the server continues running with the platforms that do have credentials.

### Container exits immediately with `invalid mount config for type "bind"`

```
Error response from daemon: invalid mount config for type "bind":
bind source path does not exist: .../secrets/apstra_verify_ssl
```

This means `docker-compose.yml` references a secret file that doesn't exist on disk, and Docker failed the bind mount *before* the app started. Two fixes:

- **If you want that platform enabled:** run `cp secrets/<name>.example secrets/<name>` and populate the file with your real values.
- **If you don't want that platform:** drop the platform's secret references via a `docker-compose.override.yml` (see [Disable platforms you don't use](#3-disable-platforms-you-dont-use-recommended)).

Do **not** create an empty file with placeholder contents left over from the `.example` template — the app will boot but fail authentication against the fake values, as explained in [Platform Auto-Disable](#platform-auto-disable).

### Authentication Failures

**Mist** — `Permission Denied` or `401 Unauthorized`:
- Verify your API token is valid in the Mist Dashboard
- Check that `mist_host` matches your region (`api.mist.com`, `api.eu.mist.com`, `api.gc1.mist.com`)

**Central** — `Login Failed` or token errors:
- Verify `central_base_url` matches your Central instance (e.g., `https://us5.api.central.arubanetworks.com`)
- Ensure the OAuth2 client ID and secret are correct and not expired
- Check that the API client has the correct scopes in HPE GreenLake Platform

**GreenLake** — `Access token acquisition failed`:
- Verify `greenlake_api_base_url` (typically `https://global.api.greenlake.hpe.com`)
- Check that the client credentials are valid and the workspace ID is correct
- Token refresh happens automatically — if it fails, check the logs for details

**ClearPass** — `ClearPass: failed to initialize`:
- Verify `clearpass_server` is the correct CPPM hostname with `/api` path (e.g., `https://clearpass.example.com/api`)
- Ensure the OAuth2 API client has been created in ClearPass Admin with `client_credentials` grant type
- For self-signed certificates, set `clearpass_verify_ssl` to `false`
- Check the logs for the specific error: `docker compose logs | grep ClearPass`

**Apstra** — `Apstra: failed to initialize` or login errors:
- Verify `apstra_server` is just the hostname (no scheme, no port), e.g., `apstra.example.com`
- Set `apstra_port` only if your Apstra server listens somewhere other than `443`
- Ensure `apstra_username` and `apstra_password` belong to an Apstra account that can reach `/api/user/login`
- For self-signed Apstra certificates, set `apstra_verify_ssl` to `false` (defaults to `true`)
- Check the logs for the specific error: `docker compose logs | grep Apstra`

### Connection Refused on Port 8000

```bash
docker compose ps                          # Check container is running
docker compose restart                     # Restart the container
```

If port 8000 is already in use by another service, change the port in `docker-compose.yml` (keep the `127.0.0.1:` prefix):
```yaml
ports:
  - "127.0.0.1:8080:8000"    # Map to port 8080 instead, loopback-only
```

If you change the host port, also update `ALLOWED_ORIGINS` so it matches (e.g. `ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080`) — the default tracks `MCP_PORT` (which is the *container* port, 8000), not the host port.

### Tools Not Appearing in AI Client

1. Check the server is running: `docker compose logs | grep "registered"`
2. Verify the endpoint is reachable: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/mcp` (expect `406` — this is normal for a plain GET)
3. **Restart your AI client** after adding or changing the MCP server config — tools are discovered at session start

### Claude Desktop: "Not a valid MCP server configuration"

Claude Desktop doesn't natively support streamable HTTP — it requires a stdio bridge. Use `supergateway`:

```json
{
  "mcpServers": {
    "hpe-networking": {
      "command": "npx",
      "args": ["-y", "supergateway", "--streamableHttp", "http://localhost:8000/mcp"]
    }
  }
}
```

If tools time out after ~4 minutes, check that:
- The Docker container is running and healthy: `docker compose ps`
- Node.js is installed: `npx --version`
- The container didn't lose connectivity after sleep: `docker compose restart`

### Tool Surface Looks Wrong (6 tools vs. 367)

Since v3.0.0.0, the server defaults to `MCP_TOOL_MODE=code`: only `execute` + 5 discovery tools (`tags`, `search`, `get_schema`, `skills_list`, `skills_load`) are visible at the top level. All 367 underlying tools are reachable via `await call_tool(name, params)` inside a sandboxed Python `execute()` block. A correctly configured server with all 7 platforms enabled will advertise **6 tools** to the AI client.

Check the mode in the logs:

```bash
docker compose logs | grep "Tool mode"
# "Tool mode: code"      → default since v3.0.0.0 (6 exposed tools, 367 underlying via call_tool)
# "Tool mode: dynamic"   → opt-in to v2.x meta-tool surface (24 exposed: 21 per-platform + 4 cross-platform + 2 skills)
```

To use the v2.x meta-tool discovery surface (each platform exposes `<platform>_list_tools`, `<platform>_get_tool_schema`, `<platform>_invoke_tool`), set `MCP_TOOL_MODE=dynamic` in `docker-compose.yml` under `environment`:
```yaml
- MCP_TOOL_MODE=dynamic   # 24 exposed; per-platform meta-tools + cross-platform + skills
- MCP_TOOL_MODE=code      # 6 exposed; sandboxed call_tool() reaches all 367 (default since v3.0.0.0)
```

The `static` mode (every underlying tool visible up front) was REMOVED in v3.0.0.0 — at 367 tools / ~64K tokens it was no longer practical. Setting `MCP_TOOL_MODE=static` now raises an error at startup with a migration message.

See [docs/MIGRATING_TO_V2.md](docs/MIGRATING_TO_V2.md) for the v1.x → v2.x meta-tool history.

### Write Tools Not Visible

Write tools are disabled by default. Enable them per-platform in `docker-compose.yml`:

```yaml
- ENABLE_MIST_WRITE_TOOLS=true
- ENABLE_CENTRAL_WRITE_TOOLS=true
- ENABLE_CLEARPASS_WRITE_TOOLS=true
```

Then restart: `docker compose restart`

### Container Crashes or Restarts

Check the exit code and logs:

```bash
docker compose ps -a                       # Check exit code
docker compose logs --tail 100             # Check recent logs
```

Common causes:
- **No valid credentials** — the server exits if zero platforms can be initialized
- **Port conflict** — another service is using port 8000
- **Out of memory** — increase Docker's memory allocation

---

## Contributing

Contributions are welcome! The `main` branch is protected — all changes go through pull requests with CI checks. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full development workflow.

For a complete list of every tool and its parameters, see [docs/TOOLS.md](docs/TOOLS.md).

---

## License

[MIT](LICENSE)
