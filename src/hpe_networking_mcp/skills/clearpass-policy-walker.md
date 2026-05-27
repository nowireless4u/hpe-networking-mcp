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
platforms: [clearpass, central]
tags: [clearpass, central, policy, visualization, audit]
tools: [clearpass_list_policy_services, clearpass_compile_policy_flow, central_get_role_with_policy]
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

### Step 3 — Embed the pre-rendered Mermaid sections from the response

**Use the ``mermaid`` field on the response directly. Do NOT
re-assemble the diagram from ``nodes`` / ``edges``.** The engine
pre-renders ready-to-paste Mermaid server-side specifically to
eliminate AI-side assembly errors — previously the AI would inline two
node declarations on the same source line, which throws Mermaid's
``Parse error … got NODE_STRING`` (issues #356, #358). Pre-rendering
sidesteps that whole failure mode.

The response carries:

```python
result["mermaid"] = {
    "sections": [
        {"title": "Block A — Service intake (start → match → auth)", "code": "flowchart LR\n..."},
        {"title": "Block B — Role mapping", "code": "flowchart LR\n..."},
        {"title": "Block C — Enforcement (decision → access)", "code": "flowchart LR\n..."},
    ],
    "simulated": False,  # or True when a simulation was requested
}
```

For each entry in ``result["mermaid"]["sections"]``, emit a section
header (the ``title``) and a fenced Mermaid block containing the
``code`` verbatim:

````markdown
## Block A — Service intake (start → match → auth)

```mermaid
flowchart LR
    ...
```

## Block B — Role mapping

```mermaid
flowchart LR
    ...
```

## Block C — Enforcement (decision → access)

```mermaid
flowchart LR
    ...
```
````

Constraints when copying the code:

- Paste each ``code`` verbatim — preserve every newline. Do NOT
  collapse whitespace, re-flow, or "tidy up" the syntax. The engine
  emits one node per line, one edge per line, with labels safely
  quoted; touching it re-introduces the parser bug.
- Do not edit node labels or add classDefs of your own — the engine
  already includes ``classDef deny`` / ``classDef skip`` (and the sim
  classes when ``simulated`` is true).
- Sections with no nodes (e.g. RADIUS_PROXY skips role mapping
  entirely) are omitted from the list — just iterate what's there.

If your client supports it, render each section as its own code fence
so the user can zoom them independently. If your client renders all
fences sequentially that's fine too — they'll appear stacked.

After the three blocks, add a one-sentence connection note: *"All
role-mapping outcomes (Block B) converge to the enforcement chain in
Block C."*

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

### Step 4b-2 — Honor the rule-combine algorithms (NEVER hardcode "stop on match")

The response carries two top-level fields you MUST use when labelling
rule rows in any UI (custom widget or otherwise):

- ``role_mapping_combine`` — one of ``"first-applicable"`` /
  ``"evaluate-all"`` / ``None``.
- ``enforcement_combine`` — same domain.

The mermaid section titles already include the combine algorithm —
when emitting your own rule list (e.g. expandable cards per rule),
label them accordingly:

- ``evaluate-all`` → "**continue on match**" (rules continue, device
  can accumulate multiple roles or actions).
- ``first-applicable`` → "**stop on match**" (first matching rule wins).
- ``None`` → don't apply a combine label (service has no policy of
  that kind).

Hardcoding "stop on match" on an evaluate-all role-mapping policy is a
bug (issue #360). A common ClearPass shape is **evaluate-all role
mapping + first-applicable enforcement** — read the response fields,
don't assume.

### Step 4d — Drilling into Aruba role definitions (cross-platform)

When the operator wants to see what an Aruba role actually does
(beyond the name), call ``central_get_role_with_policy(name=<role>)``.
You'll know which roles to look up because enforcement profiles push
them via the ``Aruba-User-Role`` attribute — visible in
``details.profile_attributes[<profile name>].attributes[]``. Common
examples:

- Profile ``WLAN-NIGHT-NIGHT`` has ``Aruba-User-Role = "night-night"``
- Profile ``WLAN-NEST-DEVICE`` has ``Aruba-User-Role = "nest-device"``

Call shape:

```python
detail = await call_tool("central_get_role_with_policy", {"name": "night-night"})
# Returns: {name, role: {...}|None, policy: {...}|None, not_found: [...], errors: [...]}
```

Surface in your reply as an additional inspector block (mirror the
role-mapping / enforcement section style). The ``policy.security-
policy.policy-rule[]`` array has the firewall rules — each rule's
``condition`` (rule-type, services with app-category / application,
source/destination) and ``action`` (``ACTION_ALLOW`` /
``ACTION_DENY``) are what determines what traffic the role can do.

Many roles are **skeletal** (just ``{name, description}``) — that's
fine. Many roles **have no separate security policy** —
``not_found: ["policy"]`` is informational, not an error. Say so:
"*The night-night role is referenced as a source in the 'AP default'
policy but has no policy named after itself.*"

Prefetch is cheap (~2 GETs per role), but call only for roles the
operator actually asks about — don't blast Central for every profile
referenced in a 15-rule enforcement chain.

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

## Step 5 — What-if simulation (REQUIRED prompt after rendering)

After Step 4 finishes (header + diagram + warnings + walkthrough),
**you MUST offer the operator the simulation workflow.** Add a
section to your reply:

> **Want to see what fires for a specific device?**
> I can simulate the policy against a device's attributes — tell me
> the role(s) and any other attributes (visitor name, endpoint
> status, time, etc.) and I'll re-render with the matching path
> highlighted. Example: *"Role=Kid, GuestUser:visitor=Bobby,
> time=20:00"*.

When the operator responds with attributes, you re-call
``clearpass_compile_policy_flow`` with ``simulated_attributes`` set
and re-render with the matched path highlighted. The attribute keys
use ``"<namespace>:<attribute>"`` form — the keys you saw in the
rendered decision conditions. Values are strings or lists of strings.

### Step 5a — Required UNCERTAINTY-FIRST output contract

The simulator returns a ``simulation`` block with a ``status`` field
that is the single most important value in the response. **You MUST
honor it:**

| ``simulation.status`` | What you say to the operator |
|---|---|
| ``"resolved"`` | Confidently name the matching enforcement rule and access decision: *"Matches **E11** → applies WLAN-NIGHT-NIGHT + VLAN-USER + MPSK + timeout 7am + SDWAN role updates → **Access: ALLOW**"* |
| ``"uncertain"`` | DO NOT name an outcome. Say: *"Cannot determine the outcome without these additional attribute(s): `GuestUser:visitor`, `Endpoint:Status`. Provide them and I'll re-simulate."* List ALL items in ``simulation.unknown_attributes``. |
| ``"no_match"`` | *"No enforcement rule matched the simulated context — falls through to implicit deny."* |

This contract is load-bearing. A prior version of this skill
appeared to support simulation but produced confidently wrong
outcomes (the post-auth bucketing bug in v3.1.3.0 mis-classified
every MPSK rule as DENY, and the simulator dutifully reported that as
the answer). The current engine returns ``None`` for any predicate it
can't evaluate, propagates ``None`` through And/Or/Not, and surfaces
``unknown_attributes`` explicitly so the AI never has to guess.
**Never override ``status: "uncertain"`` with a confident guess.**

### Step 5b — Highlighting the matched path in the re-rendered diagram

The engine handles all simulation styling server-side. When you re-call
``clearpass_compile_policy_flow`` with ``simulated_attributes``, the
response's ``mermaid.sections`` already has:

- The green ``:::sim_match`` class applied to decision nodes whose rule
  fires under the simulated context.
- The dimmed ``:::sim_skip`` class applied to decision nodes whose
  condition is contradicted.
- The classDefs (``sim_match`` / ``sim_skip`` / ``sim_unknown``)
  injected into every block.

You don't need to add any styling yourself — just embed the
``code`` verbatim per Step 3 and the highlighting appears.

Above the diagrams (between the summary header and Block A), add a
one-line outcome banner naming the matched enforcement rule (by index
/ role list — NEVER by numeric ID) and the resulting access decision.
Below Block C, list any ``simulation.unknown_attributes``.

### Step 5c — Attribute prompting hints

When the operator asks "what attributes can I provide?" or you need
to suggest a starting point, name the attributes that appear in the
rendered conditions for THIS service. Don't list arbitrary ClearPass
attribute paths — only the ones that actually affect this policy's
decisions. Pull them from the decision-node conditions.

Common ones for typical policies:

- ``Tips:Role`` — pass as a list when evaluate-all role mapping can
  assign multiple roles (e.g. ``["Kid", "Night Night"]``).
- ``GuestUser:visitor`` — visitor name (string).
- ``GuestUser:Role ID`` — guest device role ID (string).
- ``Endpoint:Status`` — ``"Known"`` / ``"Unknown"`` / etc.
- ``Authorization:[Guest Device Repository]:Device Role ID`` —
  per-device numeric role from the guest device repo.
- ``Connection:NAD-IP-Address`` — string.
- ``Connection:Client-Mac-Address`` — string.

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
