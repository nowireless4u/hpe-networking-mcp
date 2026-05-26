---
name: central-qos-policy
title: Aruba Central switch QoS policy build — traffic classes + marker policy + interface bind
description: |
  PRIMARY TRIGGER — invoke whenever the operator wants to CREATE or push
  switch QoS (Quality of Service) into Aruba Central: classifier/marker
  policies, DSCP marking, traffic classes, priority queueing, or to translate
  an AOS-CX / AOS-S (ProVision) QoS config into Central library objects.

  Match phrases include: "push QoS policies to Central", "create a QoS marker
  policy", "build my DSCP marking policy", "create traffic classes", "set up
  QoS classification on my switches", "translate this switch QoS config to
  Central", "mark voice traffic EF / video AF41", "class ip / policy qos in
  Central", "apply a QoS policy to a VLAN/interface".

  Switch QoS in Central decomposes into THREE objects that must be built in
  order: (1) traffic classes = `named-condition`, (2) the marker/classifier
  policy = `policy` with `type: POLICY_QOS`, (3) the interface/VLAN binding.
  This skill is schema-first: it reads the distilled `payload_schema` from
  `central_get_tool_schema` so field names and enums are never guessed.

  Scope: ArubaOS-CX (`cx`) and ArubaOS-Switch / ProVision (`aos-s` / PVOS).
  Not for AP or gateway QoS (those use `dap` / firewall QoS — different model).
  Writes — gated by ENABLE_CENTRAL_WRITE_TOOLS and elicitation.
platforms: [central]
tags: [central, qos, dscp, switch, cx, aos-s, policy, config-model, write]
tools:
  - health
  - central_get_scope_tree
  - central_list_tools
  - central_get_tool_schema
  - central_invoke_tool
  - central_get_named_condition
  - central_manage_named_condition
  - central_get_policies
  - central_manage_policy
---

# Aruba Central switch QoS policy build

## Objective

Build a switch QoS classifier/marker configuration in Central from an
operator's intent or an existing AOS-CX / AOS-S CLI config, as structured
config-model objects — **not** a raw CLI template block, and **without
guessing the payload schema**.

A typical switch QoS config (CLI) looks like:

```
class ip QOS-m-voice-ef          # traffic class: which packets
    10 match udp any 10.33.20.0/24 range 8000 48200 count
    20 match any any 10.16.46.254 count
policy QOS-P-marker              # marker policy: class -> action
    10 class ip QOS-m-voice-ef action local-priority 5 action dscp EF
    20 class ip QOS-m-video-af41 action local-priority 4 action dscp AF41
    90 class ip default action local-priority 1 action dscp CS0
interface vlan 2
    apply policy QOS-P-marker routed-in   # bind to interface/VLAN
```

### CLI → Central object mapping

| CLI construct | Central object | Tool |
|---|---|---|
| `class ip <name>` + `match`/`ignore`/`comment` lines | traffic class (`named-condition`) | `central_manage_named_condition` |
| `policy <name>` + `class … action dscp/local-priority` | QoS marker policy (`policy`, `type: POLICY_QOS`) | `central_manage_policy` |
| `apply policy <name> <direction>` on an interface/VLAN | interface/VLAN binding | interface config tools (separate step) |

**This is a write workflow** — every create fires elicitation unless
`confirmed=true`, and requires `ENABLE_CENTRAL_WRITE_TOOLS`.

## Two rules that prevent the common failures

1. **Read the schema; never guess.** Both `central_manage_named_condition`
   and `central_manage_policy` take an opaque `payload: dict`. Call
   `central_get_tool_schema(name=…)` first — its `payload_schema` block carries
   the real field names + enums. Guessing produced ~15 rejected 400s on a real
   run: the entry list is `condition-rule` (not `condition-entry-list`) and
   `rules-type` is `NAMED_CONDITION_IP` (not `ipv4`/`ip`/`acl`).

2. **The marker policy IS `central_manage_policy`.** Its description says
   "firewall policy" but `/policies` is unified — `type` includes **`POLICY_QOS`**.
   Do not conclude "no QoS policy tool exists" and fall back to a CLI template.
   A marker policy is a `POLICY_QOS` policy whose rules carry `packet-marking.dscp`
   (your `action dscp`) and `local-queue-priority` (your `action local-priority`).

## Prerequisites

- `health(platform="central")` reachable.
- `ENABLE_CENTRAL_WRITE_TOOLS` on (else build + show payloads only, don't push).
- **Know the switch OS.** The `named-condition` field set splits by OS:
  `Switch CX` uses per-rule `count`; `Switch PVOS` uses `log`. CLI tells —
  `apply policy … routed-in` + `count` + `action local-priority` reads as CX.
  Treat the schema's `device_types` (`x-supportedDeviceType`) tags as advisory:
  they're inconsistent in the source specs, so use them to pick the field
  family, not as a hard gate.

## Steps

### 1. Pull the schemas (both objects), once

```
central_get_tool_schema(name="central_manage_named_condition")
central_get_tool_schema(name="central_manage_policy")
```

From `payload_schema.fields` confirm, for the traffic class:
`rules-type` (enum, mandatory), `condition-rule[]` → `{position, ip-header{protocol,dscp},
source, destination, transport-fields{source-port,destination-port}, count|log, ignore}`.
For the policy: `type` (→ `POLICY_QOS`), the rule array, `condition.type:
CONDITION_NAMED` (references a class), and the action's `packet-marking.dscp`
+ `local-queue-priority`. Note `enum_count` on any enum means it was truncated
for size (e.g. the DPI `application` catalog).

### 2. Resolve scope

Library/shared QoS objects omit `scope_id`. For a scoped object, pass
`scope_id` + `device_function` (resolve the id via the `central-scope-walker`
skill). Build the classes and the policy at the **same** scope.

### 3. Build + validate ONE traffic class first

Build the smallest class from the schema and push just that one, so any
remaining error is field-precise:

```python
result = await call_tool("central_invoke_tool", {
    "name": "central_manage_named_condition",
    "params": {
        "name": "QOS-m-voice-ef",
        "action_type": "create",
        "payload": {
            "rules-type": "NAMED_CONDITION_IP",
            "condition-rule": [
                {"position": 10, "count": True,
                 "ip-header": {"protocol": "IP_UDP"},
                 "source": {"source": {"prefix": "10.33.20.0/24"}},
                 "transport-fields": {"source-port": {"range": {"min": 8000, "max": 48200}}}},
                {"position": 20, "count": True,
                 "ip-header": {"protocol": "PROTOCOL_ANY"},
                 "destination": {"destination": {"address": "10.16.46.254"}}},
            ],
        },
        "confirmed": True,
    },
})
return result
```

If it errors, re-read `payload_schema` for the named field and fix —
do **not** revert to guessing. (Exact `source`/`destination` and `*-port`
sub-shapes come from the schema; the snippet above is illustrative.)

### 4. Bulk-create the remaining traffic classes

Once the shape is confirmed, loop the rest in one `execute` block, preserving
each class's match lines in `position` order, and collect per-class status.

### 5. Build the marker policy referencing the classes

One `central_manage_policy` with `type: POLICY_QOS` and one rule per class, in
the operator's evaluation order, each rule:
- `condition.type: CONDITION_NAMED` pointing at the class name,
- action setting `packet-marking.dscp` (DSCP enum: `EF`, `AF41`, `AF31`,
  `AF21`, `CS0`/`DEFAULT`, …) and `local-queue-priority` (the `local-priority`
  queue 0–7),
- a final default rule for unmatched traffic.

### 6. Bind to the interface/VLAN (separate step)

`apply policy … <direction>` maps to the interface/VLAN config tools — surface
this as the remaining step (resolve the right interface tool via
`central_list_tools(filter="interface")` and its `payload_schema`).

### 7. Verify

Read each class back (`central_get_named_condition`) and the policy
(`central_get_policies`); confirm they round-trip. Surface any structured
`ToolError` status verbatim (400 = fix payload; 5xx = upstream/escalate).

## Output

- The validated traffic-class payload shape (so the operator sees what was built).
- Per-object push result table (class/policy → created / updated / failed + message).
- The marker policy rule order (class → DSCP + local-priority).
- Remaining interface/VLAN binding step.

**Classes first, then the `POLICY_QOS` policy that references them, then the
interface bind. Read the schema, validate one, then bulk-push. Never guess.**
