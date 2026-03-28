# Product Requirements Document (PRD)

## HPE Networking MCP Server

**Version:** 1.0.0
**Date:** 2026-03-27
**Status:** Draft
**License:** MIT

---

## 1. Overview

### 1.1 Problem Statement

Network engineers managing HPE networking infrastructure today must configure and interact with **three separate MCP servers** to cover their full stack:

- **Juniper Mist** (Wi-Fi, SD-WAN, Wired)
- **Aruba Central** (Campus networking, device management)
- **HPE GreenLake** (Platform services, subscriptions, workspaces)

Each server has its own installation process, credential management, transport configuration, and Docker setup. This fragmentation creates operational overhead, inconsistent tooling experiences, and unnecessary complexity for end users.

### 1.2 Solution

**HPE Networking MCP Server** is a unified MCP server that consolidates Mist, Aruba Central, and HPE GreenLake into a single deployable service. Users configure one Docker container, one secrets file, and one MCP endpoint to access the full breadth of HPE networking tools.

### 1.3 Target Audience

The open-source community — network engineers, DevOps teams, and AI-assisted operations practitioners managing HPE, Juniper, and/or Aruba networking infrastructure.

---

## 2. Goals and Non-Goals

### 2.1 Goals

| # | Goal | Success Metric |
|---|------|----------------|
| G1 | Single MCP endpoint for all three platforms | One URL (`/mcp`) serves Mist, Central, and GreenLake tools |
| G2 | Docker-first deployment | `docker compose up` with a secrets file is all that's needed |
| G3 | Streamable HTTP transport | Server uses MCP streamable HTTP transport for broad client compatibility |
| G4 | Secure secrets management | All credentials stored in a `secrets.json` file, never baked into images |
| G5 | Platform-selective enablement | Users enable only the platforms they need; missing credentials auto-disable a platform |
| G6 | Read + Write with safety controls | Write/mutation tools gated behind user confirmation (elicitation) |
| G7 | Tool namespacing | Tools are prefixed by platform (`mist_*`, `central_*`, `greenlake_*`) to avoid collisions |

### 2.2 Non-Goals

- **GUI / Web dashboard** — This is a headless MCP server. No web UI is planned for v1.
- **Multi-tenancy** — Each container instance serves one set of credentials (one org per platform).
- **Custom API proxy** — The server wraps platform APIs as MCP tools; it does not expose raw REST endpoints.
- **Platform-to-platform orchestration** — Tools operate independently per platform. Cross-platform workflows are left to the AI client.

---

## 3. Architecture

### 3.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              MCP Clients                                      │
│  (Claude Desktop, Claude Code, VS Code, GitHub Copilot)      │
└────────────────────────┬─────────────────────────────────────┘
                         │  Streamable HTTP (/mcp)
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                 HPE Networking MCP Server                     │
│                    (Docker Container)                         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  FastMCP Server Core                                   │  │
│  │  ├─ Transport: Streamable HTTP (0.0.0.0:8000)         │  │
│  │  ├─ Middleware: Elicitation, NullStrip, Logging        │  │
│  │  └─ Tool Registry (dynamic, per-platform loading)     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Mist Module  │  │Central Module│  │ GreenLake Module │   │
│  │  (30+ tools)  │  │ (13+ tools)  │  │  (5+ services)   │   │
│  │              │  │              │  │                  │   │
│  │  mistapi SDK │  │ pycentral   │  │  httpx + OAuth2  │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                 │                    │             │
└─────────┼─────────────────┼────────────────────┼─────────────┘
          │                 │                    │
          ▼                 ▼                    ▼
   ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐
   │  Mist Cloud  │  │Aruba Central│  │  HPE GreenLake   │
   │     API      │  │    API      │  │      API         │
   └─────────────┘  └─────────────┘  └──────────────────┘
```

### 3.2 Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.12+ | All three source servers use Python |
| MCP Framework | FastMCP >= 3.1.0 | Native streamable HTTP support, middleware, tool registry |
| Mist API Client | `mistapi` >= 0.60.4 | Official Juniper Mist SDK |
| Central API Client | `pycentral` == 2.0a17 | Official HPE Aruba Central SDK |
| GreenLake API Client | `httpx` >= 0.28.0 | Async HTTP with OAuth2 token management |
| Secrets | Docker Compose secrets | Per-credential files at `/run/secrets/`, never in env vars or image |
| Container Runtime | Docker + Docker Compose | Single-command deployment |
| Package Manager | `uv` | Fast, reproducible Python dependency management |

### 3.3 Transport

The server uses **MCP Streamable HTTP** as its sole transport method:

- **Endpoint:** `http://<host>:8000/mcp`
- **Port:** `8000` (configurable via environment variable)
- **Bind address:** `0.0.0.0` (all interfaces within the container)

This is the modern MCP transport that supersedes SSE and provides bidirectional streaming over HTTP, compatible with Claude Desktop, Claude Code, VS Code, and other MCP clients.

---

## 4. Secrets Management

### 4.1 Docker Compose Secrets

All credentials use **Docker Compose secrets** — each credential is a separate file mounted read-only at `/run/secrets/` inside the container.

```
secrets/
├── mist_api_token              # Mist API token
├── mist_host                   # Mist API host (e.g., api.mist.com)
├── central_base_url            # Central API gateway URL
├── central_client_id           # Central OAuth2 client ID
├── central_client_secret       # Central OAuth2 client secret
├── greenlake_api_base_url      # GreenLake API base URL
├── greenlake_client_id         # GreenLake OAuth2 client ID
├── greenlake_client_secret     # GreenLake OAuth2 client secret
└── greenlake_workspace_id      # GreenLake workspace ID
```

### 4.2 Secrets Loading Behavior

1. The server reads individual secret files from `/run/secrets/` at startup (configurable via `SECRETS_DIR` env var).
2. Each platform's credentials are validated independently.
3. If a platform's secret files are **missing**, that platform is **auto-disabled** with an info log — the server continues with the remaining platforms.
4. If **no platforms** have valid credentials, the server exits with an error.

### 4.3 Secrets Security Rules

- Secrets are mounted **read-only** by Docker Compose at `/run/secrets/`.
- Secrets are **never** exposed in `docker inspect`, environment variables, or Docker image layers.
- The `Dockerfile` and `docker-compose.yml` never contain credential values.
- Only `.example` template files are committed to version control; real secret files are git-ignored.
- Pre-commit hooks (e.g., `detect-secrets`, `gitleaks`) scan for accidentally committed secrets.

---

## 5. Platform Modules

### 5.1 Mist Module

**Source:** Adapted from `original-mcp-servers/mist-mcp-server/`

| Aspect | Detail |
|--------|--------|
| Tool prefix | `mist_*` |
| Tool count | ~30 tools across 15 categories |
| API Client | `mistapi` SDK |
| Auth method | API token (Bearer) |
| Capabilities | Device management, client search, SLE metrics, alarms, events, RRM, rogue detection, firmware upgrades, Marvis troubleshooting, configuration objects (CRUD) |
| Write support | Yes — gated behind elicitation middleware |

### 5.2 Central Module

**Source:** Adapted from `original-mcp-servers/central-mcp-server/`

| Aspect | Detail |
|--------|--------|
| Tool prefix | `central_*` |
| Tool count | ~13 tools + 10 guided prompts |
| API Client | `pycentral` SDK |
| Auth method | OAuth2 client credentials |
| Capabilities | Site health, device inventory, client connectivity, alerts, events, guided troubleshooting prompts |
| Write support | Read-only in source; write tools can be added in future phases |

### 5.3 GreenLake Module

**Source:** Adapted from `original-mcp-servers/greenlake-mcp-server/`

| Aspect | Detail |
|--------|--------|
| Tool prefix | `greenlake_*` |
| Tool count | Dynamic (list_endpoints, get_endpoint_schema, invoke_dynamic_tool) + static per-service tools |
| API Client | `httpx` with custom OAuth2 token manager |
| Auth method | OAuth2 client credentials |
| Capabilities | Audit logs, device inventory, subscriptions, user management, workspace management |
| Write support | Yes — dynamic tool invocation supports all HTTP methods |

---

## 6. Docker Deployment

### 6.1 Container Specification

| Property | Value |
|----------|-------|
| Base image | `python:3.12-slim-bookworm` |
| Package manager | `uv` (pinned version) |
| Runtime user | Non-root (`mcpuser`, uid 1000) |
| Exposed port | `8000` |
| Health check | HTTP GET to `/mcp` every 30s |
| Entry command | `uv run --no-sync python -m hpe_networking_mcp` |
| Secrets | Docker Compose secrets at `/run/secrets/` (read-only) |

### 6.2 Docker Compose

```yaml
services:
  hpe-networking-mcp:
    build: .
    ports:
      - "8000:8000"
    secrets:
      - mist_api_token
      - mist_host
      - central_base_url
      - central_client_id
      - central_client_secret
      - greenlake_api_base_url
      - greenlake_client_id
      - greenlake_client_secret
      - greenlake_workspace_id
    environment:
      - MCP_PORT=8000
      - LOG_LEVEL=info
    restart: unless-stopped

secrets:
  mist_api_token:
    file: ./secrets/mist_api_token
  # ... (one entry per secret file)
```

### 6.3 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/<org>/hpe-networking-mcp.git
cd hpe-networking-mcp

# 2. Create secret files from templates
cp secrets/mist_api_token.example secrets/mist_api_token
cp secrets/mist_host.example secrets/mist_host
# Edit each file with your real credentials

# 3. Start the server
docker compose up -d

# 4. Verify
docker compose logs
```

---

## 7. Write Safety Model

Write/mutation tools across all platforms follow a consistent safety model:

### 7.1 Elicitation (User Confirmation)

- All write tools require **user confirmation** before execution via MCP elicitation.
- The server detects whether the connected MCP client supports elicitation.
- If the client does not support elicitation, write tools are **hidden** from the tool list.

### 7.2 Configuration Flags

| Flag / Config | Effect |
|---------------|--------|
| `enable_write_tools: true` | Exposes write tools in the tool registry (default: `false`) |
| `disable_elicitation: true` | Bypasses confirmation prompts (**danger zone**, for automation only) |

These flags can be set via environment variables (`ENABLE_WRITE_TOOLS`, `DISABLE_ELICITATION`) or in the secrets/config file.

### 7.3 Tool Annotations

All tools carry MCP tool annotations:

```python
{
    "readOnlyHint": True/False,
    "destructiveHint": True/False,
    "idempotentHint": True/False,
    "openWorldHint": True
}
```

---

## 8. Client Integration

### 8.1 Claude Desktop

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

### 8.2 Claude Code

```bash
claude mcp add hpe-networking --transport http http://localhost:8000/mcp
```

### 8.3 VS Code / GitHub Copilot

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

## 9. Milestones and Phases

### Phase 1 — Foundation (v0.1.0)

- [ ] Project scaffolding (Python + FastMCP + uv + Docker)
- [ ] Secrets management (`secrets.json` loading, validation, per-platform enablement)
- [ ] Streamable HTTP transport on port 8000
- [ ] Mist module: Migrate all read tools with `mist_*` prefix
- [ ] Central module: Migrate all read tools with `central_*` prefix
- [ ] GreenLake module: Migrate all tools with `greenlake_*` prefix
- [ ] Docker build (multi-stage, non-root user, health check)
- [ ] Docker Compose with secrets bind mount
- [ ] Basic README and setup documentation

### Phase 2 — Write Safety (v0.2.0)

- [ ] Elicitation middleware (write tool confirmation)
- [ ] Mist write tools (configuration object CRUD)
- [ ] `ENABLE_WRITE_TOOLS` / `DISABLE_ELICITATION` flags
- [ ] Tool annotations on all tools
- [ ] Pre-commit hooks (gitleaks, detect-secrets, ruff, mypy)

### Phase 3 — Prompts and Polish (v0.3.0)

- [ ] Central guided prompts (10 troubleshooting workflows)
- [ ] GreenLake static tool mode
- [ ] Comprehensive logging and error handling
- [ ] Integration tests per platform
- [ ] CI/CD pipeline (GitHub Actions)

### Phase 4 — Production Readiness (v1.0.0)

- [ ] End-to-end testing with all three platforms
- [ ] Performance benchmarking and optimization
- [ ] Security audit (bandit, pip-audit, trivy for container)
- [ ] Documentation: full tool reference, troubleshooting guide
- [ ] Published Docker image (GitHub Container Registry or Docker Hub)
- [ ] Release automation (semantic versioning, changelog)

---

## 10. Open Questions

| # | Question | Status |
|---|----------|--------|
| 1 | Should the server support running multiple instances with different credential sets behind a load balancer? | Deferred to post-v1 |
| 2 | Should there be an optional authentication layer on the MCP endpoint itself (e.g., API key for the MCP server)? | Needs discussion |
| 3 | Should GreenLake services be individually toggleable (audit-logs, devices, subscriptions, users, workspaces)? | Needs discussion |
| 4 | What is the tool count limit for optimal MCP client performance? Should we support tool filtering? | Needs investigation |

---

## 11. Success Criteria

1. A user with valid credentials for at least one platform can go from `git clone` to a working MCP server in **under 5 minutes**.
2. All tools from the three source servers are accessible through a **single MCP endpoint**.
3. No credentials are ever persisted in the Docker image, logs, or version control.
4. Write operations **never execute** without explicit user confirmation (unless intentionally disabled).
5. The server gracefully degrades — a failing platform does not bring down the other platforms.
