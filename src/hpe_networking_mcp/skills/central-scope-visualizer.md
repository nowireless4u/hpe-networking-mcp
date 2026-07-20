---
name: central-scope-visualizer
title: Aruba Central scope hierarchy visualizer — where config is committed, with shared/local/overridden/orphaned classification, rendered live
description: |
  PRIMARY TRIGGER — invoke whenever the operator asks to visualize, render,
  diagram, draw, walk, or map the Aruba Central scope hierarchy (Global →
  site-collections → sites → device-collections → devices) AND see WHERE
  configuration profiles are committed at each level — by their real names, and
  classified as shared / local / overridden / orphaned.

  Match phrases include:

  - "visualize the Central scope hierarchy", "draw / render the scope tree",
    "map where config is committed", "show the scope map with profiles"
  - "which profiles are assigned at each scope", "show me the committed config
    across scopes by name"
  - "find orphaned configurations", "which profiles are local vs shared",
    "which profiles are overridden", "audit for local overrides / orphans"

  What it produces: the scope hierarchy as a collapsible tree with a profile
  count on every node, plus a per-scope breakdown of the actual profile NAMES
  grouped by type, each labeled with its class:

  - **shared** — a library object (inherits down)
  - **local** — a standalone object at that scope, of a type that has no shared
    library at all (device-intrinsic, e.g. system-info); this is normal
  - **overridden** ⚠ — a LOCAL object whose name matches a SHARED profile
    assigned upstream; the local copy supersedes the shared one and will NOT
    receive library edits
  - **orphaned (local)** ⚠ — a LOCAL object of a type that DOES have a shared
    library, but whose name has no SHARED match upstream (stray local, shared
    source gone)
  - **orphaned (unnamed)** ⚠ — a config-assignment with an empty
    profile-instance (assigned but nameless); a safe cleanup candidate

  Rendered through the `generate_prefab_ui` Generative-UI tool (collapsible
  Accordion tree + color-coded Badge chips). NOT a Mermaid diagram. Global-level
  alerts are ignored — this is a config-placement view, not a health view.

  For single-site health/devices/clients use central-site-dashboard; for
  compliance drift use central-scope-audit; to resolve a name → scope_id use
  central-scope-walker.

  **Read-only.** Does not mutate any Central config.
platforms: [central]
tags: [central, scope, hierarchy, visualization, config, assignments, shared, local, overridden, orphaned, audit, generative-ui]
tools: [central_get_scope_tree, central_get_config_assignments, central_get_aliases, central_invoke_tool, generate_prefab_ui, search_prefab_components]
---

# Aruba Central scope hierarchy visualizer

## Objective

Show, in one interactive view, WHERE every configuration profile is committed
across the Central scope hierarchy — by its **real name**, grouped by type, and
classified **shared / local / overridden / orphaned**. Two layers:

1. **Hierarchy** — Global → site-collections → sites → device-collections →
   devices, as a collapsible tree with a profile count on each node.
2. **Per-scope profiles** — the actual profile names committed at each scope,
   as color-coded chips, with overrides and orphans flagged.

This is the tool for "map my config placement and find orphans/overrides", not a
health board and not a name→id lookup.

## The classification model (read first — this is the whole point)

`local` vs `shared` is a property of the **object**, not where it is assigned.
It is the object's own `aruba-annotation:object_type` (`SHARED` | `LOCAL`) on a
`detailed=True` read. It is NOT `scope-type` (that's only *where* an assignment
sits) and NOT `profile-type` (that's the object *kind*).

**Detection gotcha (do not skip):** the annotation lives in the object's `@`
field, which Central serializes two ways — a parsed dict, or a **single-quoted
stringified blob**. Match it **quote-agnostically** or you will falsely report
everything as SHARED:

```python
import re
_OT = re.compile(r"""['"]aruba-annotation:object_type['"]\s*:\s*['"](\w+)['"]""")
def object_type(obj):        # obj is one config object from a detailed read
    m = _OT.findall(str(obj))
    return m[0] if m else None
```

Classify each committed profile named `X` of type `T`:

| Class | Condition |
|---|---|
| **shared** | `X` exists as a SHARED object of type `T` (in the library) and no LOCAL `X` overrides it here |
| **overridden** ⚠ | a LOCAL `X` exists at this scope AND a SHARED `X` of type `T` exists upstream (the local supersedes the shared) |
| **orphaned (local)** ⚠ | a LOCAL `X` exists AND type `T` has a shared library, but no SHARED `X` upstream |
| **local** | a LOCAL `X` exists AND type `T` has NO shared library at all (device-intrinsic, e.g. `system-info`) — normal, not an orphan |
| **orphaned (unnamed)** ⚠ | a `config-assignments` record with empty `profile-instance` |

The single discriminator between **overridden** and **orphaned-local** is
whether a same-named SHARED profile exists upstream: match → overridden, no
match (but the type has a library) → orphaned.

## Prerequisites & rules

- Central configured and reachable (`health(platform="central")` if unsure).
- **Ignore Global-level alerts.** A tenant often has 250+ alerts sitting at
  Global; they are noise for a config-placement view. Never fetch or surface
  alerts in this skill.
- **PII:** device names/serials are tokenized when `ENABLE_PII_TOKENIZATION` is
  on; render whatever the reads return. The skill only surfaces profile
  **names + object_type + scope** (metadata), not config bodies — so it is safe
  under a "no payload" instruction. Read config bodies only if the operator
  explicitly asks to inspect values.
- **Generative UI renders only in an MCP-Apps host** (Claude Desktop /
  claude.ai / ChatGPT). In a non-apps client (e.g. Claude Code) `generate_prefab_ui`
  is a no-op visual — the Step 4 text summary is then the deliverable, so ALWAYS
  emit it.

## Response-shape contract (unwrap these)

Every `central_*` read returns the standard `{ok, status, data, ...}` envelope;
read the inner `data`. Inside `execute()`, `await call_tool(name, params)`
returns the already-unwrapped value for most reads, but be defensive:

```python
def unwrap(resp):
    d = resp.get("data", resp) if isinstance(resp, dict) else resp
    return d.get("result", d) if isinstance(d, dict) and "result" in d else d

def rows(m, *keys):
    """Rows for a config read — first list value found (Central nests under a
    kind-keyed dict like {"config-assignment":[...]} / {"role":[...]})."""
    if isinstance(m, dict):
        for k in keys:
            if isinstance(m.get(k), list):
                return m[k]
        for v in m.values():
            if isinstance(v, list):
                return v
    return m if isinstance(m, list) else []
```

Key shapes:

```text
central_get_scope_tree           -> dict: scope_id, scope_name, type, resource_count, device_count, personas:[{name, resources:[{name}]}], children:[...] (recursive)
central_get_config_assignments   -> {"config-assignment": [ {scope-id, device-function, profile-type, profile-instance, scope-name, scope-type} ]}
central_get_<type>(detailed=True)-> {"<kind>": [ {name, "@": <annotations, may be stringified>, ...} ]}  # object_type lives in "@"
```

`central_get_config_assignments` is the **name backbone**: `profile-instance` is
the real profile name (e.g. `WLAN-TWDC`), `profile-type` is the kind, and an
empty `profile-instance` is an unnamed orphan.

## Procedure

### Step 1 — Structure + name backbone (2 calls, always)

```python
# scope tree = hierarchy + per-scope resource/device counts + resource names
tree = unwrap(await call_tool("central_get_scope_tree", {"view": "committed"}))
# config-assignments = real profile names + where committed + UNNAMED orphans
A = rows(unwrap(await call_tool("central_get_config_assignments", {})),
         "config-assignment", "config-assignments")

unnamed_orphans = [a for a in A if not a.get("profile-instance")]
# assignments keyed by scope for the per-scope view. NOTE: the sandbox has no
# `collections` module — use plain dict + setdefault (not defaultdict/Counter).
by_scope = {}
for a in A:
    by_scope.setdefault(str(a.get("scope-id")), []).append(a)
```

This alone renders the hierarchy + per-scope profile names + the unnamed
orphans. It is cheap (2 calls) and is the minimum viable view.

### Step 2 — Classify shared / local / overridden / orphaned

Classification needs the object's `object_type`, which lives on the object, not
the assignment — so read the objects. **Reads are SEQUENTIAL** — the sandbox does
NOT allow `asyncio.gather` (or `async def` helpers); use plain `await` in a loop.
The sandbox also caps `call_tool` at **50 per `execute()` block**, so a full
classification spans multiple `execute()` blocks: do the shared-library reads in
one block, then the per-scope LOCAL reads ~40 at a time in following blocks.
Because this is sequential, **scope to the subtree the operator named** when the
hierarchy is large rather than classifying every scope — the whole-tenant scan is
~1 read per (scope × type) committed and can run into the low hundreds.

```python
# profile-type -> read tool. Almost all are central_get_<type-with-underscores>;
# the only exception is wlan-ssids (the tool is central_get_wlan_profiles).
_TOOL_OVERRIDE = {"wlan-ssids": "central_get_wlan_profiles"}
def config_tool(pt):
    return _TOOL_OVERRIDE.get(pt, "central_get_" + pt.replace("-", "_"))

ptypes = sorted({a["profile-type"] for a in A if a.get("profile-instance")})

# (block A) shared library names per type — SHARED objects at Global. Sequential.
shared = {}
for pt in ptypes:                              # ~20 reads → fits one execute() block
    m = unwrap(await call_tool(config_tool(pt), {"detailed": True}))
    shared[pt] = {o.get("name") for o in rows(m)
                  if isinstance(o, dict) and object_type(o) == "SHARED"}
```

```python
# (block B+) LOCAL names per (scope, type, device-function) — one read per distinct
# triple in the assignments. Sequential; ≤40 per execute() block (repeat in more
# blocks for the rest, or restrict `triples` to the operator's subtree).
triples = sorted({(a["scope-id"], a["profile-type"], a["device-function"])
                  for a in A if a.get("profile-instance")})
local_at = {}
for sid, pt, df in triples[:40]:               # then triples[40:80], … in later blocks
    m = unwrap(await call_tool(config_tool(pt),
                               {"view_type": "LOCAL", "scope_id": sid,
                                "device_function": df, "detailed": True}))
    local_at[(sid, pt, df)] = {o.get("name") for o in rows(m)
                               if isinstance(o, dict) and object_type(o) == "LOCAL"}
```

```python
# classify every named assignment
def classify(a):
    nm, pt = a.get("profile-instance"), a.get("profile-type")
    if not nm:
        return "orphaned-unnamed"
    is_local = nm in local_at.get((a["scope-id"], pt, a["device-function"]), set())
    if not is_local:
        return "shared"
    if nm in shared.get(pt, set()):
        return "overridden"
    if shared.get(pt):
        return "orphaned-local"
    return "local"
```

Notes:
- `system-info` and `aliases` are device-local types that do NOT appear in
  `config-assignments`. To include them, add them to the LOCAL scan at device
  scopes (`central_get_aliases` / `central_get_system_info` with
  `view_type="LOCAL"`); they classify `local` (no shared library) unless a
  shared same-name exists.
- If a whole subtree is uninteresting, don't scan it — classify only the scopes
  in view.

### Step 3 — Render (Generative UI)

Call `generate_prefab_ui` **directly as a top-level tool** — NOT from inside an
`execute()` block. Pass it **self-contained** `code`: inline the Step 1–2
results as Python literals at the top (do NOT pass a `data` argument — the
widget executes the code in the browser and won't have `data`'s globals, so any
name only defined via `data` hangs the widget on "waiting for content").

Confirm component names with `search_prefab_components` ONCE (broad query). The
component set for this view:

- `Accordion` / `AccordionItem` — the collapsible hierarchy; one item per scope,
  title = `<scope_name> · <N> profiles · <D> devices`, expandable.
- `Badge` / `Dot` — a chip per committed profile, **color by class**:
  shared = neutral/green, local = blue, **overridden = amber ⚠**,
  **orphaned = red ⚠**. Group chips by `profile-type` with a small `Heading`.
- `Metric` — top KPIs: total scopes, total profiles committed, # orphaned, # overridden.
- `Column` / `Row` / `Grid` / `Heading` / `Text` — layout.

```python
# --- Step 1–2 results, inlined as literals (substitute the REAL values) ---
hierarchy = [  # flattened, one row per scope, in tree order with a depth
    {"name": "Global", "type": "GLOBAL", "depth": 0, "profiles": 16, "devices": 0},
    {"name": "EST Timezone Sites", "type": "SITE_COLLECTION", "depth": 1, "profiles": 51, "devices": 0},
    # ...
]
per_scope = {  # scope_name -> profiles grouped by type, each with a class
    "EST Timezone Sites": {
        "policies": [{"name": "apple-tv", "cls": "shared"}, {"name": "night-night", "cls": "shared"}],
        "aliases":  [{"name": "AdamsLAB", "cls": "shared"}, {"name": "user-vlan", "cls": "overridden"}],
    },
}
summary = {"scopes": 137, "profiles": 240, "orphaned": 2, "overridden": 0}
CLR = {"shared": "green", "local": "blue", "overridden": "amber", "orphaned-local": "red", "orphaned-unnamed": "red"}

with Column(gap=4) as view:
    Heading("Central config placement")
    with Row(gap=4):
        Metric(label="Scopes", value=summary["scopes"])
        Metric(label="Profiles committed", value=summary["profiles"])
        Metric(label="Orphaned", value=summary["orphaned"], description="cleanup candidates")
        Metric(label="Overridden", value=summary["overridden"], description="local supersedes shared")
    with Accordion():
        for node in hierarchy:
            prof = per_scope.get(node["name"], {})
            title = f'{"  " * node["depth"]}{node["name"]} · {node["profiles"]} profiles' + (f' · {node["devices"]} devices' if node["devices"] else "")
            with AccordionItem(title=title):
                if not prof:
                    Text("No profiles committed directly at this scope.")
                for ptype, items in prof.items():
                    Heading(ptype.replace("-", " ").upper())
                    with Row(gap=2, wrap=True):
                        for it in items:
                            flag = " ⚠" if it["cls"].startswith("overridden") or it["cls"].startswith("orphaned") else ""
                            Badge(text=it["name"] + flag, color=CLR.get(it["cls"], "gray"))
app = PrefabApp(view=view)
```

(Use the exact component signatures from `search_prefab_components`; the above is
the shape, not a guaranteed API. If `Accordion` isn't available, fall back to
`ExpandableRow`, or nested `Card`s indented by `depth`.)

### Step 4 — Text walkthrough (ALWAYS emit, and the deliverable in non-apps clients)

Under the board (or instead of it, in a non-apps client), summarize in prose:

- The shape: how many scopes, how deep, where the bulk of config lives.
- **Orphans, called out explicitly:** each unnamed orphan (type @ scope) and
  each orphaned-local, with "safe cleanup candidate."
- **Overrides, called out explicitly:** each overridden profile (name, the scope
  where the local copy lives, the shared source it shadows) with the warning that
  it will NOT receive library edits.
- Never print raw numeric scope IDs — use scope names.

Example: *"137 scopes; 240 profiles committed, almost all shared from the Global
library. 2 orphaned assignments: a nameless `policy-groups` binding at Global
(CAMPUS_AP and MOBILITY_GW) — safe to delete. No local overrides detected."*

## Output rules

1. **Aggregate by default.** 4+ same-type siblings → one aggregated node
   ("4 Site Collections — Region-A · Region-B · …") with expand-on-demand.
2. **Real profile names, always** — `profile-instance`, never the generic type.
   The whole reason this skill exists is to answer "what profile is here", not
   "there's a policy here."
3. **Never expose raw numeric scope IDs** — use scope names; for unnamed
   intermediate scopes show type + child counts.
4. **Flag orphans and overrides visibly** — ⚠ + red/amber, and in the prose.
5. **No alerts.** This is a config-placement view.

## When NOT to use this skill

- **Single-site health / devices / clients** → `central-site-dashboard`.
- **Name → scope_id lookup** → `central-scope-walker`.
- **Compliance drift audit** → `central-scope-audit`.
- **Inspect a specific profile's actual values** → `central_get_<type>(name=...)`
  directly (that reads the body; this skill deliberately stays at metadata).
