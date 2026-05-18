---
name: clearpass-policy-walker
title: ClearPass policy visualizer — render a service's decision flow as Mermaid
description: |
  TRIGGERS — call this when the operator wants to visualize or
  understand a ClearPass policy decision flow. Phrases include:
  "visualize the X policy", "show me how service Y decides", "walk the
  policy flow for Z", "what does the AirGroup service look like end-to-end",
  "why does this MAC get this role", "render the enforcement chain",
  "draw the policy", "diagram service N". Output is a Mermaid
  flowchart that an AI client renders inline, plus a per-service
  summary header and any unresolved-reference warnings. Backed by the
  `clearpass_compile_policy_flow` tool which fans out across services,
  role-mapping policies, enforcement policies + profiles, roles, auth
  methods, and auth sources to assemble the full picture.
  **Read-only.**
platforms: [clearpass]
tags: [clearpass, policy, visualization, audit]
tools: [health, clearpass_list_policy_services, clearpass_compile_policy_flow]
---

# ClearPass policy visualizer

## Objective

Render a single ClearPass policy service's decision flow as a Mermaid
flowchart, with first-applicable / evaluate-all / implicit-deny
semantics correctly modeled. The output is **one diagram per call** —
service match → authentication → role mapping → enforcement policy →
enforcement profile(s) — with deny / allow paths visually distinct.

Use this when an operator wants to *see* how a service decides, not
just dump the raw config. Particularly useful for:

- "Why does this MAC get this role?" — the diagram makes the rule
  chain explicit.
- Pre-change review — verify the policy structure before a change to
  a role-mapping or enforcement rule.
- Onboarding / handover — show a new operator how the policy actually
  decides.
- Documentation snapshots — paste the rendered Mermaid into a runbook.

**Read-only.** Does not mutate any ClearPass config.

## Prerequisites

- ClearPass reachable: `health(platform="clearpass")` first (skip if
  you already ran it earlier in the same session).
- The operator has named the target service, OR is asking generally
  ("show me a service" / "pick one to visualize") — in which case
  call the picker step first.

## Procedure

### Step 1 — Pick the target service

If the operator named a specific service ("visualize the AirGroup
service"), skip to Step 2 with `service_name` set.

Otherwise, call the picker:

```python
services = await call_tool("clearpass_list_policy_services", {"limit": 100})
# Surface a short summary (name, type, enabled) so the operator can choose.
```

The picker returns one entry per service with `id`, `name`, `type`,
`template`, `enabled`, `role_mapping_policy`, `enf_policy`,
`description`, `hit_count`, `monitor_mode`. Present a slim view —
operators usually pick by name.

### Step 2 — Compile the flow

```python
flow = await call_tool("clearpass_compile_policy_flow", {
    "service_name": "<exact ClearPass service name, e.g. [AirGroup Authorization Service]>",
    # or "service_id": 2,
    "include_details": False,   # set True for the per-rule inspector data
})
```

Returns:

```
{
    "service_id":   <internal slug>,
    "service_name": <ClearPass name>,
    "service_type": "RADIUS" | "TACACS" | "RADIUS_PROXY",
    "nodes": [{id, type, label, sub_label, trace_rule_id, rank_group}, ...],
    "edges": [{from_id, to_id, label, reason}, ...],
    "warnings": [<unresolved-reference message>, ...],
}
```

Node `type` is one of: `start`, `process`, `decision`, `action`, `end`.
Edge `label` is one of: `""` (unconditional), `YES`, `NO`, `FAIL`,
`PASS`, `CONTINUE`.

If the service wasn't found, the response carries
`{"status": "service_not_found", "available_services": [...]}` — show
the operator the available list and re-prompt.

### Step 3 — Render the FlowGraph as Mermaid

Use this exact template (don't improvise — the consistency across
sessions is the point of the skill):

```mermaid
flowchart TD
    %% --- nodes ---
    %% For each node in flow.nodes, emit ONE line:
    %%   start        →  <id>([service_name])
    %%   process      →  <id>[label]
    %%   decision     →  <id>{label}
    %%   action       →  <id>[/label/]
    %%   end (allow)  →  <id>(((label)))
    %%   end (deny)   →  <id>(((label))):::deny
    %%   end (skip)   →  <id>(((label))):::skip
    %% Multi-line labels: replace \n with <br/>

    %% --- edges ---
    %% For each edge in flow.edges:
    %%   ""        →  from --> to
    %%   YES       →  from -->|YES| to
    %%   NO        →  from -->|NO| to
    %%   FAIL      →  from -->|FAIL| to
    %%   PASS      →  from -->|PASS| to
    %%   CONTINUE  →  from -. CONTINUE .-> to

    %% --- classes ---
    classDef deny fill:#fee,stroke:#c33,stroke-width:2px;
    classDef skip fill:#eee,stroke:#999,stroke-width:1px;
```

End-node classification rules (for `:::deny` / `:::skip`):

- `:::deny` if the label starts with `Access: DENY` or `Auth Failed`.
- `:::skip` if the label starts with `Skip` (the service-no-match
  branch).
- No class (default styling) for `Access: ALLOW` and any non-end node.

### Step 4 — Output format

Emit, in this exact order:

1. **A one-line summary header**:

   `**Service:** <name> (<type>) — enabled=<true|false>, monitor_mode=<true|false>, role_mapping=<rm name or "—">, enforcement=<ep name or "—">`

2. **The rendered Mermaid block** (Step 3 template, filled in).

3. **Warnings section** (only if `warnings` is non-empty):

   ```
   ### Warnings

   - <each warning string on its own bullet>
   ```

4. **A short walkthrough** (3-6 sentences) describing the happy path
   from service-match → role assignment → enforcement decision in
   plain English. Reference rule indices (e.g. "rule 2 of the
   enforcement chain") so the operator can find them in the UI.

Do NOT include the raw JSON FlowGraph in the response — the diagram
is the point.

## Worked example

Operator: *"Visualize the AirGroup Authorization Service."*

```python
# Step 1 — skip picker (operator named the service)

# Step 2 — compile
flow = await call_tool("clearpass_compile_policy_flow", {
    "service_name": "[AirGroup Authorization Service]",
})

# Step 3 — render Mermaid per template, with nodes from flow["nodes"]
# and edges from flow["edges"]. Use service_name in the start-node
# shape: <start_id>([AirGroup Authorization Service])

# Step 4 — output:
#   header → mermaid block → warnings (if any) → walkthrough
```

## When NOT to use this skill

- The operator asks for the **raw config** of a service / role mapping
  / enforcement policy. Use the underlying `clearpass_get_services` /
  `clearpass_get_role_mappings` / `clearpass_get_enforcement_policies`
  tools directly — this skill produces a visualization, not raw JSON.
- The operator asks "what services exist" / "list services". Call
  `clearpass_list_policy_services` directly — the compile step is
  unnecessary overhead.
- The operator wants real-time policy decision testing (simulate a
  RADIUS request). ClearPass has a separate "Policy Simulation" UI
  feature; the OAuth REST API doesn't expose it. Tell the operator to
  use the ClearPass UI.

## Performance notes

`clearpass_compile_policy_flow` fans out across 7 endpoints
(`/config/service`, `/role-mapping`, `/enforcement-policy`,
`/enforcement-profile`, `/role`, `/auth-method`, `/auth-source`) on
every call. On a typical tenant this is well under a second total. On
a very large tenant (1000+ services) the fan-out becomes the dominant
cost; in that case prefer to call the picker first to choose a
specific service rather than calling compile speculatively.

## Output is deterministic

Same input → same FlowGraph → same rendered Mermaid. Node IDs are
slug + sha256[:6] hashes of the upstream object names, so they're
stable across re-renders. This makes the output safe to paste into
runbooks / docs and re-verify later.
