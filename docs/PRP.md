# Product Requirements Proposal (PRP)

## HPE Networking MCP Server

**Date:** 2026-03-27
**Author:** Jon Adams
**Status:** Proposed
**Related:** [PRD.md](PRD.md)

---

## 1. Problem

Network engineers using AI assistants (Claude, Copilot, etc.) to manage HPE networking infrastructure must currently install and maintain **three separate MCP servers**:

| Server | Platform | Transport | Auth Method |
|--------|----------|-----------|-------------|
| Mist MCP Server | Juniper Mist (Wi-Fi, SD-WAN, Wired) | stdio / HTTP | API Token |
| Central MCP Server | Aruba Central (Campus, Device Mgmt) | Streamable HTTP | OAuth2 |
| GreenLake MCP Server | HPE GreenLake (Platform Services) | stdio | OAuth2 |

Each has its own Docker setup, credential format, port, and transport method. For a user managing all three platforms, this means:

- **3 containers** to deploy and monitor
- **3 credential systems** to configure and secure
- **3 endpoints** to register in every AI client
- **Inconsistent behavior** across transport methods and tool naming

This friction discourages adoption and increases the risk of misconfiguration.

---

## 2. Proposal

Build a **single, unified MCP server** — `hpe-networking-mcp` — that merges all three platform modules into one Docker container with one endpoint.

**One container. One secrets file. One MCP endpoint.**

```
Before:                              After:
┌──────────┐  :8000                  ┌─────────────────────┐
│ Mist MCP │◄─── Client 1           │                     │
└──────────┘                         │  HPE Networking MCP │  :8000
┌──────────┐  :8001                  │                     │◄─── All Clients
│Central MCP│◄─── Client 2          │  ├─ Mist (30+ tools)│
└──────────┘                         │  ├─ Central (13+)   │
┌──────────┐  stdio                  │  └─ GreenLake (5+)  │
│GreenLake │◄─── Client 3           │                     │
└──────────┘                         └─────────────────────┘
3 containers, 3 configs              1 container, 1 config
```

---

## 3. Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Language** | Python 3.12+ with FastMCP | All source servers are Python; FastMCP has native streamable HTTP support |
| **Transport** | Streamable HTTP | Modern MCP standard; works with all major AI clients without adapters |
| **Deployment** | Docker container | Single `docker compose up` for the full stack |
| **Secrets** | Docker Compose secrets | Per-credential files at `/run/secrets/`; never in env vars, inspect, or image |
| **Platform enablement** | Auto-disable on missing credentials | Users only configure the platforms they use |
| **Write operations** | Supported, disabled by default | Gated behind elicitation (user confirmation) for safety |
| **Tool naming** | Platform-prefixed (`mist_*`, `central_*`, `greenlake_*`) | Prevents name collisions across 50+ tools |
| **License** | MIT | Permissive, matches source projects |

---

## 4. Scope

### In Scope (v1.0)

- All read tools from Mist, Central, and GreenLake servers
- Write tools from Mist and GreenLake with elicitation safety
- Central guided prompts (10 troubleshooting workflows)
- Docker + Docker Compose deployment
- `secrets.json`-based credential management
- Streamable HTTP transport
- Per-platform enable/disable
- Documentation (README, setup guide)

### Out of Scope

- Web UI or dashboard
- Multi-tenancy (multiple orgs per container)
- Cross-platform orchestration workflows
- Authentication on the MCP endpoint itself (assumes trusted network)
- Non-Docker deployment packaging (e.g., standalone binaries)

---

## 5. Target Users

The open-source community — specifically:

- **Network engineers** managing HPE/Juniper/Aruba infrastructure who want AI-assisted operations
- **DevOps/NetOps teams** looking to integrate network management into AI workflows
- **Solution architects** evaluating MCP-based network automation

---

## 6. Expected Outcomes

| Outcome | Metric |
|---------|--------|
| Simplified deployment | From 3 containers + 3 configs to 1 + 1 |
| Faster time-to-value | Under 5 minutes from clone to working server |
| Broader adoption | Single setup lowers the barrier for users of any one platform to discover the others |
| Consistent experience | Unified transport, naming, and safety model across all platforms |
| Secure by default | Read-only out of the box; credentials never in image or VCS |

---

## 7. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Tool count exceeds MCP client limits | Medium | High | Support tool filtering by platform; test with major clients |
| Upstream SDK breaking changes (`mistapi`, `pycentral`) | Medium | Medium | Pin dependency versions; automated CI tests |
| OAuth2 token refresh race conditions with concurrent requests | Low | Medium | Singleton token managers per platform with thread-safe refresh |
| Users expose the endpoint to untrusted networks | Medium | High | Document security recommendations; consider optional API key auth in v2 |

---

## 8. Effort Estimate

| Phase | Scope | Estimated Effort |
|-------|-------|-----------------|
| Phase 1 — Foundation | Scaffolding, secrets, all read tools, Docker | Large |
| Phase 2 — Write Safety | Elicitation middleware, write tools, flags | Medium |
| Phase 3 — Prompts & Polish | Guided prompts, logging, tests, CI/CD | Medium |
| Phase 4 — Production | E2E tests, security audit, published image | Medium |

---

## 9. Next Steps

1. Review and approve this PRP
2. Proceed to implementation using the detailed [PRD](PRD.md)
3. Begin Phase 1 — project scaffolding and platform module migration
