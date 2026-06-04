# Tool Annotation & Confirmation Rubric

The single standard every platform's tools are classified against. **One**
classification per tool — `capability=` on the `@tool` decorator — drives four
things consistently: the MCP client hints, **confirmation gating**,
visibility/enablement, and the discovery/search facet.

Implemented by `platforms/_common/annotations.py` (`Capability`, `classify`) and
applied by the shared `make_tool_decorator` factory in
`platforms/_common/tool_registry.py`. Never hand-write `ToolAnnotations` or the
governance tags per tool.

## Three decoupled axes (do not conflate)

1. **Capability category** — one per tool, the source of truth.
2. **MCP hints** (`ToolAnnotations`) — *derived* from the category; advisory, for clients.
3. **Tags** — the `<platform>_write[_delete]` enable tag (visibility, gated by
   `ENABLE_<PLATFORM>_WRITE_TOOLS`) **and** the `requires_confirmation` tag.

The universal confirmation gate reads **only** the `requires_confirmation` tag —
never `readOnlyHint`/`destructiveHint`.

## The five categories

| Category | Definition | readOnly / destructive / idempotent | enable tag | gated (default) |
|---|---|---|---|---|
| **READ** | Returns data, no environment change (GET). | T / F / T | — | No |
| **DIAGNOSTIC** | Triggers a test/probe returning live results, **no persistent change** (cable test, iperf, ranging scan, connectivity probe). | F / F / T | — | No |
| **WRITE** | Creates or updates persistent config. | F / F / F | `<platform>_write` | Yes |
| **WRITE_DELETE** | Deletes, or a destructive/irreversible update. | F / **T** / F | `<platform>_write_delete` | Yes |
| **OPERATIONAL** | Triggers a disruptive real-world action without creating config (reboot, commit/apply, failover, regenerate credentials, clear/defer alerts). | F / F / T | — by default; opt in with `enable_gated=True` | Yes\* |

`DIAGNOSTIC` and `OPERATIONAL` share identical hints (F/F/T) — they differ
**only** by the `requires_confirmation` tag. The hints are for clients; the tag
is for the gate.

\* **`gated` is per-tool overridable.** `classify(..., gated=False)` drops
`requires_confirmation` (e.g. a benign `central_clear_alerts` — operational but
no prompt). Disruptive operational actions keep it.

## Enable-gating is independent of category

By default `OPERATIONAL` tools are **not** behind the write flag — they ride
alongside reads (e.g. reboot). But a destructive operational action that should
not be reachable on a read-only deployment passes `enable_gated=True` to keep
the `<platform>_write_delete` enable tag (e.g. `axis_regenerate_connector`
regenerates credentials; `axis_commit_changes` applies staged writes). `WRITE`
and `WRITE_DELETE` are always enable-gated; `READ`/`DIAGNOSTIC` never are.

## Gate predicate

The universal gate (at the `*_invoke_tool` dispatch chokepoint) confirms **iff**
the tool carries `requires_confirmation`. **Fail-closed:** a tool with no
recognizable capability is treated as gated.

## Classification decision tree

1. Only reads/returns data, no side effects → **READ**
2. Triggers a test/probe returning live results, **no persistent change** (even
   if POST/PATCH) → **DIAGNOSTIC**
3. Creates/updates persistent config → deletes or destructive? **WRITE_DELETE**
   : else **WRITE**
4. Disruptive action without creating config (reboot, commit, failover,
   regenerate, alert clear/defer) → **OPERATIONAL**
   - benign/reversible (e.g. clear an alert) → `gated=False`
   - destructive and not coupled to staged writes → `enable_gated=True`

## Rules

- **CREATE is gated.** `WRITE` includes create (matches AOS8; supersedes
  Central's old `action_type != "create"` skip).
- **Multi-action tools** (`*_manage_*` doing create/update/delete) classify at
  their most-destructive action → **WRITE_DELETE**.
- **Required human-judgment inputs** (e.g. a Central alert-clear `reason`) are
  collected via `ctx.elicit()` with a structured `response_type` (e.g.
  `Literal[...]`) when absent. This is **input collection, not gating** — it does
  not imply `requires_confirmation`. (Do not use `ctx.sample()` for judgment
  inputs — the connected clients don't support sampling, and a value the human
  alone knows must come from the human.)

## Usage

```python
from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.<platform>._registry import tool

@tool(name="<platform>_get_things", capability=Capability.READ)
@tool(name="<platform>_manage_thing", capability=Capability.WRITE_DELETE)
@tool(name="<platform>_reboot_device", capability=Capability.OPERATIONAL, enable_gated=True)
@tool(name="central_clear_alerts", capability=Capability.OPERATIONAL, gated=False)
```

`tags=` is reserved for functional/discovery tags; the governance tags are
derived. Tools not yet migrated may still pass `annotations=`/`tags=` directly
(legacy path) — `capability` is recorded as `None` and they are not yet covered
by the capability facet.

## Rollout

Per-platform annotation PRs migrate each platform's tools to `capability=`
against this rubric, then a single PR adds the universal gate that reads
`requires_confirmation` at the dispatch chokepoint. No release ships in a
half-migrated state.
