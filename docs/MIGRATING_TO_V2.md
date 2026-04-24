# Migrating to v2.0.0.0

Released 2026-04-23. Umbrella issue: [#157](https://github.com/nowireless4u/hpe-networking-mcp/issues/157).

## The short version

The default tool surface drops from 261 static tools to **18 exposed tools**. Every per-platform tool still exists — it's just discovered on demand via three meta-tools per platform instead of advertised up front. Behavior and return shapes are unchanged when invoked. Small local LLMs (gpt-oss:20b / 32K context) now fit the tool schema in their context window with room to spare.

Set `MCP_TOOL_MODE=static` in `docker-compose.yml` to restore v1.x behavior.

## Why this changed

The v1.x static surface was ~64,000 tokens of tool schema. A 32K-context local model couldn't even load the tools array, let alone have room for conversation and results. In dynamic mode the exposed surface is **~2,900 tokens** — a 95.5% reduction.

**How it was measured.** Counted against `cl100k_base` (OpenAI's tokenizer; closest approximation to what a chat model sees when the tools array is passed in the system prompt), summing the JSON-serialized `{name, description, input_schema}` for every tool returned by `list_tools()`. Both modes measured with all 5 platforms registered using dummy secret values — enough to populate the tool registry without needing live vendor creds. Reproduce by setting `MCP_TOOL_MODE=static` or `MCP_TOOL_MODE=dynamic` in `docker-compose.yml` and running `list_tools()` against a tokenizer of your choice.

## What you see in v2.0 dynamic mode (the default)

**18 tools exposed at session start:**

- `health(platform=...)` — cross-platform reachability probe
- `site_health_check(site_name=...)` — cross-platform site health aggregator
- `manage_wlan_profile(...)` — cross-platform WLAN entry point
- `<platform>_list_tools(filter=...)` — list available tools for a platform
- `<platform>_get_tool_schema(name=...)` — retrieve a tool's parameter schema
- `<platform>_invoke_tool(name=..., arguments={...})` — call a tool by name

The three per-platform meta-tools exist for each of `apstra`, `mist`, `central`, `clearpass`, `greenlake` — 5 × 3 = 15 meta-tools + 3 cross-platform static = 18.

## Discovery pattern the AI follows

```
1. <platform>_list_tools(filter="<keyword>")     → list of candidates
2. <platform>_get_tool_schema(name="...")        → exact parameter schema
3. <platform>_invoke_tool(name=..., arguments=.) → run it
```

See `src/hpe_networking_mcp/INSTRUCTIONS.md` for the full discovery-pattern playbook that ships to every session.

## What stays

- Every tool's **behavior** and **return shape** is unchanged when invoked.
- Every env var you configure in `docker-compose.yml` (`ENABLE_*_WRITE_TOOLS`, `DISABLE_ELICITATION`, etc.) keeps its meaning.
- Write-tool elicitation prompts the same way.
- Secrets, Docker image tagging, and deployment workflow are unchanged.
- `MCP_TOOL_MODE=static` remains a supported opt-out — every v1.x tool is still there.

## Opt-out (keep v1.x static surface)

Set this in your `docker-compose.yml` under `environment:`:

```yaml
- MCP_TOOL_MODE=static
```

Then `docker compose up -d` restarts with the full tool surface (every `<platform>_*` tool visible individually). Existing write-tool gating (`ENABLE_*_WRITE_TOOLS`) still applies.

## Removed tools

The following v1.x tools are **gone** in v2.0. AI agents that hard-coded these names get `tool not found`:

| Removed in v2.0 | Replacement |
|---|---|
| `apstra_health` | `health(platform="apstra")` |
| `apstra_formatting_guidelines` | Content migrated into `src/hpe_networking_mcp/INSTRUCTIONS.md` (Juniper Apstra section). Per-response helpers (`get_base_guidelines`, `get_device_guidelines`, etc.) still fire inside Apstra tool bodies. |
| `greenlake_list_endpoints` | `greenlake_list_tools` |
| `greenlake_get_endpoint_schema` | `greenlake_get_tool_schema` |
| `greenlake_invoke_endpoint` | `greenlake_invoke_tool` |

The GreenLake renaming is the biggest practical break — v1.x had endpoint-dispatch meta-tools that took a REST path; v2.0's tool-dispatch meta-tools take a tool name instead. The naming now matches every other platform's meta-tools.

### Still present, but hidden in default dynamic mode

- `clearpass_test_connection` — still registered (category `utilities`); reachable via `clearpass_invoke_tool(name="clearpass_test_connection")`. `health(platform="clearpass")` is the preferred path and what the AI sees up front.

## Phase progress (complete)

- [x] Phase 0 PR A — shared `_common/` infrastructure, cross-platform `health` tool, `tool_mode` config
- [x] Phase 0 PR B — Apstra migrates to dynamic mode (pilot); `apstra_health` and `apstra_formatting_guidelines` removed
- [x] Phase 1 — Mist migrates
- [x] Phase 2 — Central migrates
- [x] Phase 3 — ClearPass migrates
- [x] Phase 4 — GreenLake dynamic mode generalizes to the new meta-tool pattern
- [x] Phase 5 — token-budget validation (95.5% reduction measured against cl100k_base)
- [x] Phase 6 — `MCP_TOOL_MODE=dynamic` becomes the default; tagged `v2.0.0.0`

## Rollback

v1.1.0.0 remains available in GHCR. If v2.0.0.0 misbehaves, pin the image in `docker-compose.yml`:

```yaml
image: ghcr.io/nowireless4u/hpe-networking-mcp:1.1.0.0
```

File an issue with logs so we can fix whatever broke for you.
