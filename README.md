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
| **Troubleshooting (Ping/Traceroute)** | ✅ | ✅ | — |
| **Configuration Management** | ✅ | — | — |
| **Configuration Write (CRUD)** | ✅ | — | — |
| **Radio Resource Management** | ✅ | — | — |
| **Rogue AP Detection** | ✅ | — | — |
| **Firmware Management** | ✅ | — | — |
| **Subscriptions / Licensing** | — | — | ✅ |
| **User Management** | — | — | ✅ |
| **Workspaces** | — | — | ✅ |
| **Guided Prompts** | — | ✅ | — |
| **Dynamic API Discovery** | — | — | ✅ |
| **Tools** | **34** | **26 + 10 prompts** | **3 or 10** |

### Aruba Central Guided Prompts

The Central module includes 10 guided prompts — multi-step workflow templates that walk the AI through common network operations tasks using the available tools. These prompts orchestrate multiple tool calls in the correct order, so you can simply invoke the prompt and let the AI handle the rest.

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

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone

```bash
git clone https://github.com/<org>/hpe-networking-mcp.git
cd hpe-networking-mcp
```

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
curl http://localhost:8000/mcp
```

That's it. Your MCP server is running at `http://localhost:8000/mcp`.

---

## Connect Your AI Client

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hpe-networking": {
      "type": "streamable-http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Claude Code

```bash
claude mcp add hpe-networking --transport http http://localhost:8000/mcp
```

### VS Code / GitHub Copilot

Add to your `.vscode/mcp.json` or MCP settings:

```json
{
  "mcpServers": {
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
│   │  34 tools  │ │ 26+10 prmt │ │  3/10 tools    │  │
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

- **Disabled by default** — set `ENABLE_WRITE_TOOLS=true` to expose write tools
- **Elicitation required** — write tools prompt for user confirmation before executing
- **Annotation-based** — all tools carry MCP annotations (`readOnlyHint`, `destructiveHint`, etc.)

| Environment Variable | Default | Effect |
|---------------------|---------|--------|
| `ENABLE_WRITE_TOOLS` | `false` | Expose write/mutation tools in the tool registry |
| `DISABLE_ELICITATION` | `false` | Skip user confirmation for write tools (**use with caution**) |

---

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `MCP_PORT` | `8000` | Port the MCP server listens on |
| `SECRETS_DIR` | `/run/secrets` | Directory containing Docker secret files |
| `LOG_LEVEL` | `info` | Logging level (`debug`, `info`, `warning`, `error`) |
| `ENABLE_WRITE_TOOLS` | `false` | Enable write/mutation tools |
| `DISABLE_ELICITATION` | `false` | Disable write confirmation prompts |

---

## Development

### Local Setup (without Docker)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Create secret files for local dev
mkdir -p secrets
cp secrets/mist_api_token.example secrets/mist_api_token
cp secrets/mist_host.example secrets/mist_host
# Edit with your real credentials

# Run the server (point to local secrets dir)
SECRETS_DIR=./secrets uv run python -m hpe_networking_mcp
```

### Running Tests

```bash
uv run pytest
```

### Linting and Formatting

```bash
uv run ruff check .
uv run ruff format .
uv run mypy .
```

---

## Project Structure

```
hpe-networking-mcp/
├── src/
│   └── hpe_networking_mcp/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── server.py            # FastMCP server setup
│       ├── config.py            # Secrets loading and validation
│       ├── middleware/          # Elicitation, logging, etc.
│       ├── platforms/
│       │   ├── mist/           # Mist tools and API client
│       │   ├── central/        # Central tools and API client
│       │   └── greenlake/      # GreenLake tools and API client
│       └── utils/              # Shared utilities
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── secrets/                     # Secret files (only .example committed)
│   ├── mist_api_token.example
│   ├── mist_host.example
│   ├── central_*.example
│   └── greenlake_*.example
├── .gitignore
├── .dockerignore
├── PRD.md
└── README.md
```

---

## Troubleshooting

### Server starts but a platform is disabled

Check the logs for credential validation errors:

```bash
docker compose logs hpe-networking-mcp
```

The server logs which platforms were enabled and which were skipped due to missing or invalid credentials.

### Connection refused on port 8000

Ensure the container is running and the port mapping is correct:

```bash
docker compose ps
```

### Tools not appearing in your AI client

1. Verify the server is reachable: `curl http://localhost:8000/mcp`
2. Check that your client config uses `streamable-http` as the transport type
3. Restart your AI client after adding the MCP server config

### Write tools not visible

Write tools are disabled by default. Set `ENABLE_WRITE_TOOLS=true` in your `docker-compose.yml` environment section and restart the container.

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Ensure tests pass (`uv run pytest`)
4. Ensure linting passes (`uv run ruff check .`)
5. Open a pull request

---

## License

[MIT](LICENSE)
