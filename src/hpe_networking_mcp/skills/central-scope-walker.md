---
name: central-scope-walker
title: Aruba Central scope-tree walker — find scope_id by name / path
description: |
  TRIGGERS — call this when you need to resolve an Aruba Central scope
  name, path, or partial match to a `scope_id` (or its parent path,
  type, or device count). Tiny utility skill: one paste-ready
  `execute` snippet that walks the `central_get_scope_tree` output.
  Useful when an operator says "site HQ" or "device group dallas-hq-floor-3"
  and you need the scope_id to feed downstream tools like
  `central_get_effective_config`, `central_manage_config_assignment`,
  or any of the `central_*` config-write tools. Designed for small
  local models that can't reliably author tree-recursion in the
  sandbox — the snippet is paste-and-go, no recursion authorship
  required. **Read-only.**
platforms: [central]
tags: [central, scope, utility, primitive]
tools: [central_get_scope_tree]
---

# Aruba Central scope-tree walker

## Objective

Resolve a human-friendly scope reference (e.g. `"HQ"`, `"USE/dallas-hq"`,
`"Global"`) to its Central `scope_id` plus parent path, type, and a
small set of useful metadata. One `execute` call, deterministic
output, no per-AI variation.

This skill is the answer to "I have a name; I need a `scope_id`." It
is intentionally small and stable. Other skills (`central-scope-audit`,
`change-pre-check`, `change-post-check`, `aos-migration`) reference it
as a primitive — they call it (or paste the snippet) when they need
to pin a name to an ID before running downstream operations.

**Read-only.** Does not mutate any config.

## Prerequisites

- Central reachable: `health(platform="central")` first (skip if you
  already ran it earlier in the same session).
- The operator has provided either:
  - an exact / partial scope name (`"HQ"`, `"dallas-hq"`), OR
  - a path (`"USE/dallas-hq"`, `"Global/USE/dallas-hq/floor-3"`), OR
  - the existing scope_id (in which case look it up to verify + get
    parent path / type / metadata).

## Procedure — one paste-ready `execute` snippet

Copy this snippet into `execute()` verbatim. It returns a single
deterministic dict. Do not author your own recursion — small models
have a poor track record at it (per Zach's 2026-05-07 OpenClaw test
report, which is why this skill exists). The snippet handles every
shape — exact match, case-insensitive partial, path-form, scope_id
lookup — so callers don't need branches.

```python
# Find a Central scope by name / path / id.
# Inputs: query (str). Output: list of matches with scope_id + parent path.
query = "HQ"  # change me

response = await call_tool("central_get_scope_tree", {"view": "committed"})
envelope = response.get("data", response)
root = envelope.get("result", envelope) if isinstance(envelope, dict) and "result" in envelope else envelope

def walk(node, path):
    here = path + [node.get("scope_name") or node.get("scope_id") or "?"]
    yield {
        "scope_id":     node.get("scope_id"),
        "scope_name":   node.get("scope_name"),
        "type":         node.get("type"),
        "path":         "/".join(here),
        "device_count": node.get("device_count"),
        "child_scope_count": node.get("child_scope_count"),
    }
    for child in node.get("children") or []:
        yield from walk(child, here)

all_nodes = list(walk(root, []))

# Match policy: exact (case-insensitive) name OR exact (case-insensitive) path
# OR exact scope_id OR case-insensitive substring on name/path. Listed in
# priority order so the first non-empty match wins.
q = query.strip()
ql = q.lower()

exact_id   = [n for n in all_nodes if n["scope_id"] == q]
exact_name = [n for n in all_nodes if (n.get("scope_name") or "").lower() == ql]
exact_path = [n for n in all_nodes if n["path"].lower() == ql]
substr     = [n for n in all_nodes if ql in (n.get("scope_name") or "").lower()
                                      or ql in n["path"].lower()]

if exact_id:
    matches, match_kind = exact_id, "scope_id"
elif exact_name:
    matches, match_kind = exact_name, "exact_name"
elif exact_path:
    matches, match_kind = exact_path, "exact_path"
elif substr:
    matches, match_kind = substr, "substring"
else:
    matches, match_kind = [], "none"

result = {
    "query":       query,
    "match_kind":  match_kind,
    "match_count": len(matches),
    "matches":     matches[:10],   # cap to keep small-model context bounded
    "total_scopes_walked": len(all_nodes),
}
result
```

That's it. The output is a small bounded dict; don't try to dump the
whole tree to the user — final-answer space breaks on large payloads
for small models.

## Match-kind semantics

| `match_kind` | What matched | Disambiguation rule |
|---|---|---|
| `scope_id` | The query was already a scope_id | Should be exactly 1 match. |
| `exact_name` | One or more scopes have this exact `scope_name` (case-insensitive) | Multiple matches happen when the same site name exists under different collections. Show parent paths to disambiguate; ask the operator which they meant. |
| `exact_path` | The query is a slash-separated path that matches exactly | Should be exactly 1 match (paths are unique). |
| `substring` | Loose case-insensitive substring of name OR path | The least specific match; if you got here, prefer to surface the candidates and ask the operator to pick. |
| `none` | No match | Tell the operator "no scope matches `<query>`"; suggest they run the full audit (`central-scope-audit`) or check spelling. |

## Decision matrix

| Condition | Action |
|---|---|
| `match_count == 0` | Surface "no scope matches"; offer alternatives (closest substring matches, full audit). Do NOT pick a default. |
| `match_count == 1` | Use `matches[0]["scope_id"]` for the downstream call. Show the parent path in any operator-facing output so they can confirm. |
| `match_count > 1` and `match_kind in (exact_name, substring)` | STOP and ask the operator which they meant — list `matches[:N]["path"]`. Do NOT silently pick the first one. |
| `match_count == 1` and `match_kind == "substring"` | Echo "matched on substring" in your reply so the operator can correct if it's the wrong scope. |

## When NOT to use this skill

- **You already have the scope_id.** No lookup needed.
- **You need every scope at once for a tree-walk** (e.g. running an audit
  across all sites). Use `central_get_scope_tree` directly and walk the
  tree yourself — this skill returns a bounded match list, not the
  whole catalog.
- **You need profile assignments at the scope** (e.g. "what's bound at
  HQ?"). Resolve the scope_id with this skill first, then call
  `central_get_scope_resources(scope_id=...)` or
  `central_get_effective_config(scope_id=..., view=...)`.

## Examples

> "what's the scope_id for site HQ?"
> "find dallas-hq under USE"
> "is there a scope called Global/USE/floor-3?"
> "I have scope_id 6f8e... — what's its parent path?"

## Output formatting

Return a one-line summary back to the operator:

> Matched **HQ** (scope_id `6f8e2d…`, type `SITE`) under path `Global/USE/HQ`. 12 devices.

If `match_count > 1`, list the candidates with parent paths and ask
which one they meant. If `match_count == 0`, say so plainly and suggest
running `central-scope-audit` to inventory the scope tree.
