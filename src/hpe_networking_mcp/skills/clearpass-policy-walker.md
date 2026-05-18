---
name: clearpass-policy-walker
title: ClearPass policy visualizer — render a service's decision flow as Mermaid
description: |
  TRIGGERS — call this whenever the operator wants to visualize,
  render, diagram, draw, walk, or otherwise understand a ClearPass
  service or its policy decision flow.

  Match phrases include, with NAMED-SERVICE patterns the most common:

  - "visualize the <name> service", "visualize the <name> auth service",
    "visualize the <name> authentication service", "visualize the
    <name> policy service", "visualize the <name> ClearPass service",
    "visualize the <name> policy"
  - "show me how <name> decides", "show me the <name> service",
    "show me the <name> policy flow"
  - "draw the <name> service", "draw the <name> policy"
  - "render the <name> enforcement chain", "render the <name> policy"
  - "diagram <name>", "diagram the <name> service",
    "flowchart the <name> service"
  - "walk the policy flow for <name>", "walk the <name> service",
    "what does the <name> service look like end-to-end"
  - "why does this MAC get this role", "why is this device getting
    <role>"
  - Anything that pairs the verbs visualize / render / diagram / draw
    / flowchart / show-me / walk with a ClearPass service name —
    including service names you don't immediately recognize. ClearPass
    service names often contain casual phrases (e.g. "No Wireless For
    You", "Guest Onboarding", "AirGroup Authorization") — treat the
    whole name as opaque and feed it to `clearpass_compile_policy_flow`
    via `service_name=`.

  CRITICAL — when an operator names a specific ClearPass service, DO
  NOT guess what it does. Call `clearpass_compile_policy_flow` (or
  `clearpass_list_policy_services` first if you need to confirm the
  exact name) to get the real, current configuration. Hallucinating a
  guess at what a service named "No Wireless For You" might do is a
  bug. The tools are cheap; use them.

  Output is a Mermaid flowchart rendered inline plus a per-service
  summary header and any unresolved-reference warnings. Backed by
  `clearpass_compile_policy_flow` which fans out across services,
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

## Operator-output rules (read first)

These constrain every response you produce inside this skill:

1. **NEVER expose numeric ClearPass service IDs to the user.** IDs
   like `3010`, `3044`, `id 1`, `service_id=2` are internal API
   identifiers — operators don't know them and don't want to see
   them. Refer to services by their full name in quotes. If you
   internally pass `service_id` to the tool, fine — just don't echo
   it in your reply.
2. **Don't expose engine-internal slug IDs either** — values like
   `service_id` in the returned FlowGraph (e.g. `no_wireless_for_you_..._a1b2c3`)
   are for stable diff/test purposes, not for operators.
3. Refer to services by their full ClearPass name. If a name has
   surrounding brackets (`[Policy Manager Admin Network Login Service]`),
   include them.

## Prerequisites

- ClearPass reachable: `health(platform="clearpass")` first (skip if
  you already ran it earlier in the same session).
- The operator has named the target service (use it directly — the
  compile tool does fuzzy matching), OR is asking generally
  ("show me a service" / "pick one to visualize") — in which case
  call the picker step first.

## Procedure

### Step 1 — Compile the flow (fuzzy match handles operator phrasing)

If the operator named a specific service ("visualize the AirGroup
service" / "No Wireless For You" / "the office onboarding policy"),
go straight to the compile call — the tool resolves the name fuzzily:

```python
flow = await call_tool("clearpass_compile_policy_flow", {
    "service_name": "<whatever the operator said>",
    "include_details": False,   # set True for the per-rule inspector data
})
```

Match order inside the tool: exact → case-insensitive exact →
case-insensitive substring. A casual phrase like `"ClearPass No
Wireless For You"` will resolve to the real `"No Wireless For You
Auth Service"` automatically.

### Step 2 — Handle the three response shapes

**Success** — proceed to Step 3 to render. Shape:

```
{
    "service_id":   <internal slug — DO NOT show user>,
    "service_name": <exact ClearPass name — safe to show>,
    "service_type": "RADIUS" | "TACACS" | "RADIUS_PROXY",
    "nodes": [{id, type, label, sub_label, trace_rule_id, rank_group}, ...],
    "edges": [{from_id, to_id, label, reason}, ...],
    "warnings": [<unresolved-reference message>, ...],
}
```

**Ambiguous** — the substring matched multiple services. Shape:

```
{
    "status": "ambiguous",
    "query":  <what you sent>,
    "candidates": ["<name 1>", "<name 2>", ...]
}
```

Present the candidate names (no IDs, no other metadata) and ask the
operator which one they meant. Example reply:

> Multiple services match — which did you mean?
> - "No Wireless For You Auth Service"
> - "No Wireless For You Auth Service - Mist"

Re-call the compile with the chosen name. Do not show numeric IDs in
the disambiguation prompt.

**Not found** — substring matched zero services. Shape:

```
{
    "status": "service_not_found",
    "query": <what you sent>,
    "available_services": [<name>, ...],
    "available_count": <int>
}
```

Reply with the closest plausible matches by name and ask the operator
to confirm. If the count is small (≤ 25 — the full list is returned)
you can list them all; otherwise call `clearpass_list_policy_services`
for the full inventory and present it.

### Step 1-alt — Picker (only when operator hasn't named a service)

When the operator says something like *"show me a service to
visualize"* without naming one:

```python
services = await call_tool("clearpass_list_policy_services", {"limit": 100})
# Present names + type + enabled. DO NOT include the numeric id in your reply.
```

### Step 3 — Render the FlowGraph as Mermaid

**Critical readability rules (read first):**

1. **Use `flowchart LR` (left-right)**, not `TD`. Role-mapping and
   enforcement chains often have 12+ rules each — `TD` produces a
   tall narrow column that the client shrinks to fit width, making
   every label tiny and unreadable. `LR` lays the chain out
   horizontally with reasonable node spacing.
2. **Use `short_label` for every node, NOT `label`.** Each FlowNode
   carries both: `label` is verbose (3 lines per predicate, full
   namespace) suitable for inspector tooltips; `short_label` is a
   compact single-line summary suitable for the diagram. With many
   rules, `label` produces dense unreadable diamonds.
3. **For large policies (≥ 8 decision nodes total), split the
   rendering into 2–3 separate Mermaid blocks** instead of one giant
   diagram. See "Step 3b — Sectioned rendering" below.

Mermaid template (single-block version, fine for small policies):

```mermaid
flowchart LR
    %%{init: {'flowchart': {'nodeSpacing': 30, 'rankSpacing': 50, 'curve': 'basis'}}}%%

    %% --- nodes (use short_label, NOT label) ---
    %% For each node in flow.nodes, emit ONE line:
    %%   start        →  <id>([short_label])
    %%   process      →  <id>[short_label]
    %%   decision     →  <id>{short_label}
    %%   action       →  <id>[/short_label/]
    %%   end (allow)  →  <id>(((short_label)))
    %%   end (deny)   →  <id>(((short_label))):::deny
    %%   end (skip)   →  <id>(((short_label))):::skip

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

- `:::deny` if the `short_label` starts with `Access: DENY` or contains
  `Auth Failed`.
- `:::skip` if the `short_label` starts with `Skip` (the
  service-no-match branch).
- No class (default styling) for `Access: ALLOW` and any non-end node.

### Step 3b — Sectioned rendering (REQUIRED for ≥ 8 decision nodes)

When the policy is large, ONE Mermaid block becomes unreadable even
with `LR` + `short_label`. Split into:

**Block A — Service intake** (start + service-match + auth + auth-fail):

```
nodes with id matching <sid>__start, <sid>__match, <sid>__no_match,
<sid>__auth, <sid>__auth_fail
plus edges between them
```

**Block B — Role mapping** (the `rm_chain` rank_group):

```
nodes with id matching <sid>__rm_rule_*, <sid>__rm_action_*, <sid>__rm_default,
<sid>__no_role
plus edges between them
end this block with a "→ enforcement" placeholder edge to a stub node
```

**Block C — Enforcement** (the `enf_chain` rank_group):

```
nodes with id matching <sid>__enf_rule_*, <sid>__enf_action_*, <sid>__enf_end_*,
<sid>__enf_default_action, <sid>__enf_default_end, <sid>__enf_implicit_deny,
<sid>__enf_no_policy
plus edges between them
start this block with a stub node receiving from "← from role mapping"
```

Each block gets its own `flowchart LR` + init directive. Operators can
zoom each section independently. Below the three blocks, add a
one-sentence connection note: *"All role-mapping outcomes converge to
the enforcement chain in Block C."*

When in doubt about sizing: if the policy has more than 8 total
decision nodes across role-mapping + enforcement, split.

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

### Step 4b — When roles in enforcement rules don't appear in the role-mapping section

ClearPass enforcement rules can match on roles that the role-mapping
policy never sets — those roles come from **authorization-source
attributes** (e.g. ``Authorization:[Guest Device Repository]:Role ID``
maps a guest-device repository field directly to ``Tips:Role``). The
visualizer renders the enforcement rule conditions accurately
(including non-role attributes like ``GuestUser:visitor``,
``Endpoint:Status``, ``Authorization:[Guest Device Repository]:Device
Role ID``) but the role-mapping section only shows what the role-
mapping policy explicitly sets.

If you see a role referenced in an enforcement rule that has no
matching ``Set Role`` action in the role-mapping section, **call it
out in the walkthrough**:

> Note: the role "Visitor 'Inspire 3D'" referenced in enforcement
> rule 0 isn't set by the role-mapping policy — it comes from the
> ``[Guest Device Repository]`` authorization source as a per-device
> attribute. Same applies to "Endpoint=Oculus" in rule 5 (endpoint
> attribute, not a role).

### Step 4c — When rules apply multiple profiles (MAC auth + MPSK shape)

A common ClearPass pattern is one rule that applies **many profiles
together**: one RADIUS Accept (the access decision), one VLAN
assignment, one MPSK passphrase profile, and several
Post_Authentication updates (endpoint database writes, SDWAN role
pushes, downloadable-role assignments). The flow renders this as:

- Decision node: the rule's WHEN conditions
- Action node: ALL profile names, comma-separated (might be 5-10
  names)
- End node: ``Access: ALLOW`` — the RADIUS-layer decision

The end node is intentionally the RADIUS-layer ALLOW/DENY. The
post-auth + endpoint-update profiles are visible in the action node
(operator can see what side-effects run) but they don't change the
access decision — they happen regardless of whether access is
granted. If the operator asks *"why does this rule say ALLOW when
it's an MPSK enforcement?"*, explain: the RADIUS server sends
Access-Accept and the action node lists the per-device profiles
(MPSK passphrase, VLAN, downloadable role, endpoint updates) that
ride with it.

## Worked example — fuzzy match in action

Operator: *"Visualize the ClearPass No Wireless For You Auth Service."*

```python
# Step 1 — compile (with the operator's exact phrasing — fuzzy match
# will resolve it to the real service name)
flow = await call_tool("clearpass_compile_policy_flow", {
    "service_name": "ClearPass No Wireless For You Auth Service",
})

# Tool internally:
#   - exact match: no
#   - case-insensitive exact: no
#   - case-insensitive substring "no wireless for you":
#       → matches both "No Wireless For You Auth Service" AND
#         "No Wireless For You Auth Service - Mist"
#   - returns status="ambiguous" with both names as candidates
```

Reply to the operator (NO IDs):

> Multiple services match — which did you mean?
> - "No Wireless For You Auth Service"
> - "No Wireless For You Auth Service - Mist"

Operator picks one → re-call with the exact name → success → Step 3
(render) + Step 4 (output).

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
