# HPE Networking MCP Server

[![CI](https://github.com/nowireless4u/hpe-networking-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/nowireless4u/hpe-networking-mcp/actions/workflows/ci.yml)
[![Security](https://github.com/nowireless4u/hpe-networking-mcp/actions/workflows/security.yml/badge.svg)](https://github.com/nowireless4u/hpe-networking-mcp/actions/workflows/security.yml)

A unified [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that brings **Juniper Mist**, **Aruba Central**, and **HPE GreenLake** together into a single, deployable service. One container. One endpoint. All your HPE networking tools.

---

## Why?

Managing HPE networking infrastructure with AI assistants today means juggling three separate MCP servers — each with its own setup, credentials, and quirks. This project consolidates them into one:

| Category | Mist | Central | GreenLake |
|----------|:----:|:-------:|:---------:|
| **Sites / Health Overview** | ✅ | ✅ | — |
| **WLANs / SSIDs** | ✅ | ✅ | — |
| **Device Inventory** | ✅ | ✅ | ✅ |
| **Device Details (AP/Switch/GW)** | ✅ | ✅ | — |
| **Device Stats & Utilization** | ✅ | ✅ | — |
| **Client Connectivity** | ✅ | ✅ | — |
| **Events** | ✅ | ✅ | — |
| **Alerts / Alarms** | ✅ | ✅ | — |
| **Audit Logs** | ✅ | ✅ | ✅ |
| **Application Visibility** | — | ✅ | — |
| **SLE / Performance Metrics** | ✅ | — | — |
| **Troubleshooting (Ping/Traceroute/Bounce)** | ✅ | ✅ | — |
| **Client Disconnect** | — | ✅ | — |
| **Configuration Management** | ✅ | — | — |
| **Configuration Write (CRUD)** | ✅ | — | — |
| **Radio Resource Management** | ✅ | — | — |
| **Rogue AP Detection** | ✅ | — | — |
| **Firmware Management** | ✅ | — | — |
| **Subscriptions / Licensing** | — | — | ✅ |
| **User Management** | — | — | ✅ |
| **Workspaces** | — | — | ✅ |
| **Scope & Configuration Hierarchy** | — | ✅ | — |
| **Guided Prompts** | ✅ | ✅ | — |
| **Dynamic API Discovery** | — | — | ✅ |
| **Tools** | **35 + 2 prompts** | **53 + 12 prompts** | **3 or 10** |
| **Cross-Platform** | **1 tool + 3 prompts** | **1 tool + 3 prompts** | — |

> **GreenLake tool count**: 3 tools in **dynamic mode** (default) — a meta-tool system that can discover and invoke any GreenLake API endpoint. 10 tools in **static mode** — dedicated tools for each endpoint. Set via `MCP_TOOL_MODE` environment variable.

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

### Cross-Platform WLAN Sync

1 unified tool + 3 prompts for WLAN migration between Juniper Mist and Aruba Central. Registered when both platforms are enabled.

- **Manage WLAN Profile** (`manage_wlan_profile`) — The primary entry point for all WLAN operations. Automatically checks both Mist and Central for the SSID and returns the correct sync workflow. Detects cross-platform scenarios without relying on the AI to follow instructions.
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

Create secret files from the provided templates — only for the platforms you use:

```bash
# Mist
cp secrets/mist_api_token.example secrets/mist_api_token
cp secrets/mist_host.example secrets/mist_host
# Edit each file with your real credentials

# Aruba Central (optional)
cp secrets/central_base_url.example secrets/central_base_url
cp secrets/central_client_id.example secrets/central_client_id
cp secrets/central_client_secret.example secrets/central_client_secret

# HPE GreenLake (optional)
cp secrets/greenlake_api_base_url.example secrets/greenlake_api_base_url
cp secrets/greenlake_client_id.example secrets/greenlake_client_id
cp secrets/greenlake_client_secret.example secrets/greenlake_client_secret
cp secrets/greenlake_workspace_id.example secrets/greenlake_workspace_id
```

Each file contains a single value (e.g., your API token). The server auto-disables platforms with missing secret files.

> **Only create files for the platforms you use.** If you only manage Mist networks, you only need `mist_api_token` and `mist_host`. Comment out unused platforms in `docker-compose.yml`.

### 3. Start

```bash
docker compose up -d
```

### 4. Verify

```bash
docker compose logs
```

Look for lines like `Mist: registered 35 tools` and `Uvicorn running on http://0.0.0.0:8000`. Your MCP server is running at `http://localhost:8000/mcp`. Mist also registers 2 guided prompts for site provisioning workflows.

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

You don't need credentials for all three platforms. The server automatically detects which platforms have valid secrets and only enables those:

- **All three platforms configured** → All tools available (Mist + Central + GreenLake)
- **Only Mist configured** → Only `mist_*` tools available; Central and GreenLake disabled
- **Only Central configured** → Only `central_*` tools available; Mist and GreenLake disabled
- **No valid credentials** → Server refuses to start with a clear error message

This means you can start with just one platform and add others later by creating their secret files and restarting the container. The server logs which platforms are enabled at startup:

```
Mist: credentials loaded (token: abcd...wxyz, host: api.mist.com)
Central: disabled (missing secrets: central_client_id, central_client_secret)
GreenLake: disabled (missing secrets: greenlake_client_id)
Enabled platforms: mist
```

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

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│              MCP Client (Claude, VS Code, etc.)       │
└──────────────────────┬───────────────────────────────┘
                       │ Streamable HTTP
                       ▼
┌──────────────────────────────────────────────────────┐
│           HPE Networking MCP Server (:8000)           │
│                                                      │
│   ┌────────────┐ ┌────────────┐ ┌────────────────┐  │
│   │   Mist     │ │  Central   │ │   GreenLake    │  │
│   │  mist_*    │ │ central_*  │ │  greenlake_*   │  │
│   │ 35+2 prmt  │ │ 48+15 prmt │ │  3/10 tools    │  │
│   └─────┬──────┘ └─────┬──────┘ └───────┬────────┘  │
│         │              │                │            │
└─────────┼──────────────┼────────────────┼────────────┘
          ▼              ▼                ▼
   Mist Cloud API   Aruba Central   GreenLake API
                       API
```

**Key design decisions:**

- **FastMCP** framework with Python 3.12+
- **Streamable HTTP** transport (modern MCP standard)
- **Tool namespacing** — `mist_*`, `central_*`, `greenlake_*` prefixes prevent collisions
- **Platform isolation** — each module manages its own API client and auth; a failing platform doesn't affect the others
- **Non-root container** — runs as `mcpuser` (uid 1000)

---

## Write Operations and Safety

Write/mutation tools (e.g., creating WLANs in Mist, modifying configurations) are supported with safety controls:

- **Disabled by default** — enable per-platform with `ENABLE_MIST_WRITE_TOOLS=true` or `ENABLE_CENTRAL_WRITE_TOOLS=true`
- **Elicitation required** — write tools prompt for user confirmation before executing
- **Annotation-based** — all tools carry MCP annotations (`readOnlyHint`, `destructiveHint`, etc.)

| Environment Variable | Default | Effect |
|---------------------|---------|--------|
| `ENABLE_MIST_WRITE_TOOLS` | `false` | Enable Mist write/mutation tools |
| `ENABLE_CENTRAL_WRITE_TOOLS` | `false` | Enable Central write/mutation tools |
| `DISABLE_ELICITATION` | `false` | Skip user confirmation for write tools (**use with caution**) |

---

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `MCP_PORT` | `8000` | Port the MCP server listens on |
| `SECRETS_DIR` | `/run/secrets` | Directory containing Docker secret files |
| `LOG_LEVEL` | `info` | Logging level (`debug`, `info`, `warning`, `error`) |
| `ENABLE_MIST_WRITE_TOOLS` | `false` | Enable Mist write/mutation tools |
| `ENABLE_CENTRAL_WRITE_TOOLS` | `false` | Enable Central write/mutation tools |
| `DISABLE_ELICITATION` | `false` | Disable write confirmation prompts |
| `MCP_TOOL_MODE` | `dynamic` | GreenLake tool mode: `dynamic` (3 meta-tools) or `static` (10 dedicated tools) |

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
│   ├── middleware/              # Elicitation and null-strip middleware
│   └── platforms/
│       ├── mist/                # 35 Mist tools + 2 prompts + API client
│       ├── central/             # 48 Central tools + 15 prompts + API client
│       └── greenlake/           # 3 dynamic or 10 static tools + OAuth2 client
├── tests/                       # Unit and integration tests (176 tests)
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

If a platform shows as disabled, its secret files are missing or empty:

```
Mist: disabled (mist_api_token secret not found)
Central: disabled (missing secrets: central_client_id, central_client_secret)
```

**Fix:** Verify the secret files exist in `secrets/` and contain valid values (no extra whitespace or newlines). Each file should contain exactly one value.

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

### Connection Refused on Port 8000

```bash
docker compose ps                          # Check container is running
docker compose restart                     # Restart the container
```

If port 8000 is already in use by another service, change the port in `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"    # Map to port 8080 instead
```

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

### GreenLake Tools Missing

If you expect 10 GreenLake tools but only see 3 (or vice versa), check the `MCP_TOOL_MODE` setting:

```bash
docker compose logs | grep "GreenLake"
# "GreenLake: registered 3 tools (mode=dynamic)"  → dynamic mode
# "GreenLake: registered 10 tools (mode=static)"  → static mode
```

Change the mode in `docker-compose.yml` under `environment`:
```yaml
- MCP_TOOL_MODE=static    # 10 dedicated tools
- MCP_TOOL_MODE=dynamic   # 3 meta-tools (default)
```

### Write Tools Not Visible

Write tools are disabled by default. Enable them in `docker-compose.yml`:

```yaml
- ENABLE_WRITE_TOOLS=true
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
