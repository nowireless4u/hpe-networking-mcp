# Migrating to v2.0.0.0

Work in progress. This document lands its final form in the v2.0.0.0 default-flip PR (umbrella [#157](https://github.com/nowireless4u/hpe-networking-mcp/issues/157)). Today it exists as a stub so later phases have a canonical place to accumulate migration notes.

---

## What v2.0 changes

The default tool-exposure surface drops from 261 static tools to ~18. Every per-platform tool becomes discoverable via three meta-tools per platform (`<platform>_list_tools`, `<platform>_get_tool_schema`, `<platform>_invoke_tool`) plus three cross-platform static tools (`health`, `site_health_check`, `manage_wlan_profile`). Driven by the context-budget problem on small local LLMs (Zach Jennings' original report).

## What stays

- Every tool's **behavior** and **return shape** is unchanged when invoked.
- Every env var you configure in `docker-compose.yml` (`ENABLE_*_WRITE_TOOLS`, `DISABLE_ELICITATION`, etc.) keeps its meaning.
- Write-tool elicitation prompts you the same way.
- Secrets, Docker image tagging, and deployment workflow are unchanged.

## Opt out

Set `MCP_TOOL_MODE=static` in your `docker-compose.yml` to restore v1.x behavior. The env var name is unchanged from v1.x (where it used to apply to GreenLake only); in v2.0 it applies to every platform.

## Removed tools

_(Finalized in the v2.0 default-flip PR. The list below is what the plan calls for; treat it as advisory until v2.0.0.0 ships.)_

| Removed in v2.0 | Replacement |
|---|---|
| `apstra_health` | `health(platform="apstra")` |
| `clearpass_test_connection` | `health(platform="clearpass")` |
| `apstra_formatting_guidelines` | Content migrates into `src/hpe_networking_mcp/INSTRUCTIONS.md` under the Juniper Apstra section |

AI agents that hard-coded these names will get "tool not found" on v2.0.

## Progress tracker

- [x] Phase 0 PR A — shared `_common/` infrastructure, cross-platform `health` tool, `tool_mode` config
- [x] Phase 0 PR B — Apstra migrates to dynamic mode (pilot); `apstra_health` and `apstra_formatting_guidelines` removed
- [x] Phase 1 — Mist migrates
- [x] Phase 2 — Central migrates
- [x] Phase 3 — ClearPass migrates
- [ ] Phase 4 — GreenLake dynamic mode generalizes to the new meta-tool pattern
- [ ] Phase 5 — local-LLM validation
- [ ] Phase 6 — `MCP_TOOL_MODE=dynamic` becomes the default; tag `v2.0.0.0`

See [issue #157](https://github.com/nowireless4u/hpe-networking-mcp/issues/157) for the live status.
