---
name: central-qos-policy
title: Aruba Central switch QoS build — classes + marker policy + interface bind + queue/schedule/DSCP-map
description: |
  PRIMARY TRIGGER — invoke whenever the operator wants to CREATE or push
  switch QoS (Quality of Service) into Aruba Central: classifier/marker
  policies, DSCP marking, traffic classes, queue/schedule profiles, the
  system-wide DSCP→local-priority map, or to translate an AOS-CX / AOS-S
  (ProVision) QoS config into Central library objects.

  Match phrases include: "push QoS policies to Central", "create a QoS marker
  policy", "build my DSCP marking policy", "create traffic classes", "set up
  QoS classification on my switches", "translate this switch QoS config to
  Central", "mark voice traffic EF / video AF41", "class ip / policy qos in
  Central", "apply a QoS policy to a VLAN/interface", "qos queue-profile",
  "qos schedule-profile", "apply qos queue-profile … schedule-profile …",
  "qos dscp-map", "factory-default schedule-profile".

  ALSO TRIGGER on wrong-primitive symptoms — when the operator has built a
  CNX role-based policy and is trying to SVI-bind it: "sys_policy_pap_*",
  "sys_pap_*", "port-access role", "role-based policy", "role-based policy
  won't apply to VLAN", "apply role policy to SVI", "Cannot find in library
  'sys_policy_pap_…'", "Role-based Policies cannot be mapped to
  ScopeTypes.DEVICE", "the CNX UI won't let me apply the policy to a VLAN".

  ALSO TRIGGER on direct CLI-paste apply requests targeting an SVI policy
  bind — these are the exact wordings operators use when they paste config
  lines and say "just apply this": "apply policy sys_policy_pap_",
  "apply policy <NAME> routed-in", "apply policy <NAME> in on interface
  vlan", "interface vlan <N> apply policy", "push this to my switch:
  interface vlan … apply policy …", "MCP, do this: interface vlan … apply
  policy …".

  The operator chose the wrong primitive; the skill detects and pivots — see
  "Path picker" below.

  Switch QoS in Central decomposes into two halves that meet on the
  local-priority integer:
   • INGRESS / per-class — (1) traffic classes = `named-condition`,
     (2) marker/classifier policy = `policy` with `type: POLICY_QOS`,
     (3) optional VLAN/SVI binding (create the VLAN if missing).
   • EGRESS / system-wide — (4) queue-profile = `qos-queue` (local-priority
     → hardware queue), (5) schedule-profile = `qos-schedule` (per-queue
     WEIGHTED/STRICT/MIN_BANDWIDTH algo + weight/cap), (6) the atomic apply +
     DSCP-map = `qos-global` (one named library object holds both refs +
     `dscp-map[]`), assigned to a scope to activate on devices.

  This skill carries EXACT, live-verified payload shapes — several key fields
  are UNDOCUMENTED in the OpenAPI spec, so the schema alone is not enough
  (see the "exact shapes" sections below).

  Scope: ArubaOS-CX (`cx`) and ArubaOS-Switch / ProVision (`aos-s` / PVOS).
  Not for AP or gateway QoS (those use `dap` / firewall QoS — different model).
  Writes — gated by ENABLE_CENTRAL_WRITE_TOOLS and elicitation.
platforms: [central]
tags: [central, qos, dscp, switch, cx, aos-s, policy, config-model, write]
tools:
  - central_get_scope_tree
  - central_list_tools
  - central_get_tool_schema
  - central_invoke_tool
  - central_get_named_conditions
  - central_manage_named_conditions
  - central_get_policies
  - central_manage_policies
  - central_get_layer2_vlan
  - central_manage_layer2_vlan
  - central_get_vlan_interfaces
  - central_manage_vlan_interfaces
  - central_get_qos_queues
  - central_manage_qos_queues
  - central_get_qos_schedules
  - central_manage_qos_schedules
  - central_get_qos_global
  - central_manage_qos_global
  # Wrong-primitive detection + verification
  - central_get_role_with_policy
  - central_manage_roles
  - central_get_policy_groups
  - central_manage_policy_group_list
  - central_get_config_assignments
  - central_manage_config_assignment
  - central_get_effective_config
  - central_get_devices_config_health
  - central_show_commands
---

# Aruba Central switch QoS policy build

## Objective

Build a switch QoS classifier/marker configuration in Central from an
operator's intent or an existing AOS-CX / AOS-S CLI config, as structured
config-model objects — **not** a raw CLI template block.

A typical switch QoS config (CLI):

```
# Ingress / per-class (marking pipeline)
class ip QOS-m-voice-ef                       # traffic class: which packets
    5  match any any 10.16.46.254 count
    20 match udp 10.128.3.40/255.128.7.255 range 8000 48200 any count
class ip QOS-m-critical-af31
    10 match any any any dscp AF31 count       # match on a DSCP value
policy QOS-P-marker                            # marker policy: class -> action
    10 class ip QOS-m-voice-ef    action local-priority 5 action dscp EF
    30 class ip QOS-m-critical-af31 action local-priority 3 action dscp AF31
    90 class ip default            action local-priority 1 action dscp CS0
interface vlan 2
    apply policy QOS-P-marker routed-in        # bind to the VLAN interface

# Egress / system-wide (queueing + scheduling + DSCP-map)
qos queue-profile branch-1                         # local-priority -> hw queue
    map queue 0 local-priority 0
    ...
    map queue 7 local-priority 5               # voice (lp5) -> strict q7
qos schedule-profile QOS-P-mpls-scheduler      # per-queue algo + weights
    dwrr queue 0 weight 5
    ...
    strict queue 7 max-bandwidth 768 kbps      # cap voice queue
apply qos queue-profile branch-1 schedule-profile QOS-P-mpls-scheduler
qos dscp-map 40 local-priority 7 color green   # remap DSCP -> local-priority
qos dscp-map 47 local-priority 7 color green
```

### CLI → Central object mapping

| CLI construct | Central object | Tool |
|---|---|---|
| `class ip <name>` + `match`/`ignore` lines | traffic class (`named-condition`) | `central_manage_named_conditions` |
| `policy <name>` + `class … action …` | QoS marker policy (`policy`, `type: POLICY_QOS`) | `central_manage_policies` |
| `interface vlan <id>` (the VLAN itself) | layer2 VLAN | `central_manage_layer2_vlan` |
| `apply policy <name> routed-in` on the SVI | VLAN-interface policy bind | `central_manage_vlan_interfaces` |
| `qos queue-profile <name>` + `map queue Q local-priority LP` | queue-profile (`qos-queue`) | `central_manage_qos_queues` |
| `qos schedule-profile <name>` + `dwrr` / `wfq` / `strict` queue lines | schedule-profile (`qos-schedule`) | `central_manage_qos_schedules` |
| `apply qos queue-profile X schedule-profile Y` + `qos dscp-map …` | system-wide apply + DSCP-map (`qos-global` — one named library object) | `central_manage_qos_global` |

**This is a write workflow** — every create fires elicitation unless
`confirmed=true`, and requires `ENABLE_CENTRAL_WRITE_TOOLS`.

**Sections in this skill** map to the CLI pieces: A (classes) → B (marker policy)
→ C (SVI bind) cover the ingress / marking half (existing); D (queue-profile) →
E (schedule-profile) → F (apply + dscp-map via qos-global) cover the egress /
system-wide half. G is the update-an-applied-profile automated ritual. The two
halves are orthogonal — operators commonly push only one or the other.

## The five rules that prevent silent failure

1. **Some required fields are UNDOCUMENTED — carry the exact shapes below.**
   `central_get_tool_schema`'s `payload_schema` helps, but it CANNOT show
   everything: the policy's class-reference field (`condition-reference`) is
   absent from the spec entirely, and the address `type` discriminator's role
   isn't obvious. Use the verified shapes in this skill; consult `payload_schema`
   for the surrounding fields/enums.

2. **READ BACK AND ASSERT — never trust the `200`.** This API returns
   `status: success` while **silently dropping** any address/reference subtree
   it can't bind (e.g. a `subnet-address` without its `type` discriminator).
   After every create, GET the object and assert the match criteria / class
   references actually persisted. A create that "succeeded" but dropped all the
   IPs is the #1 failure mode here.

3. **The marker policy IS `central_manage_policies`** (`type: POLICY_QOS`) — its
   one-line description says "firewall policy" but `/policies` is unified. Don't
   conclude "no QoS tool exists" and fall back to a CLI template.

4. **POLICY_QOS has TWO associations; pick `ASSOCIATION_INTERFACE` for SVI bind.**
   The `policy` object's `association` field is `ASSOCIATION_INTERFACE` (traditional,
   SVI-bindable, renders device-side as `policy <name>`) or `ASSOCIATION_ROLE`
   (port-access role-based, renders as `port-access policy sys_policy_pap_<role>`,
   **only enforced on authenticated client sessions on access ports — never on
   SVI transit traffic**). If the operator handed you an existing role-based
   policy and wants SVI marking, see "Path picker — wrong primitive" below; do
   not try to bind it to an SVI.

5. **`SYNCHRONIZED` is not proof of correctness — verify with `show` commands.**
   When you bind a role-based policy by its CNX library name to an SVI at SITE
   scope, Central accepts with `HTTP 200`, lists it in the device-scope effective
   config, pushes a partial config to the device, **silently skips the role-based
   policy render**, and reports the device as `SYNCHRONIZED` with `activeIssues: []`.
   No error anywhere. After every device-touching push, call `central_show_commands`
   for `show port-access policy` / `show class ip` / the relevant `show running-config`
   subset and confirm the artifacts you expected actually rendered. `config-health`
   alone will lie to you on this path.

## Prerequisites

- `ENABLE_CENTRAL_WRITE_TOOLS` on (else build + show payloads only, don't write). The first `central_get_tool_schema` / create call surfaces any reachability problem — no separate health pre-flight needed.
- **Library scope** unless told otherwise: omit `scope_id` (build everything
  shared). For a scoped object pass `scope_id` + `device_function`.
- Switch OS is CX in the verified shapes below (`count`, `subnet-address`,
  `access-group-vlan-in` are CX). `device_types` tags in `payload_schema` are
  advisory/inconsistent — don't hard-gate on them.

## Path picker — POLICY_QOS comes in two flavors

Both go through `central_manage_policies`. The differentiator is one field — `association`. Same tool, two completely different deployment models.

| `association` | Device-side render | Where it enforces | SVI-bindable? | Use for |
|---|---|---|---|---|
| `ASSOCIATION_INTERFACE` | `policy <NAME>` (traditional classifier policy) + `class ip <NAME>` | Any port/SVI it's attached to via `policy.access-group-vlan-in` etc. | **Yes** | Marking transit traffic on a VLAN/interface. **This is what the rest of the skill assumes.** |
| `ASSOCIATION_ROLE` | `port-access policy sys_policy_pap_<ROLE-NAME>` + `class ip sys_pap_<ROLE-NAME>_ip_allow_N` (auto-prefixed, derived from the **role** name, not the policy name) | Only on authenticated client sessions hitting a port-access role — does NOT touch SVI transit traffic | **No** | Per-role enforcement under port-access auth. Out of scope for this skill — that's the AAA / NAC workflow. |

### Detecting the wrong primitive (live-verified error catalogue)

When an operator arrives having built `ASSOCIATION_ROLE` and wants SVI marking, you'll see one of these — quote the symptom from the operator's message and match against this table:

| Operator's symptom | What they tried | Central response (verified live on a 6100) |
|---|---|---|
| `"Cannot find in library 'sys_policy_pap_X' of type 'aruba-policy' referred in '<vlan-id>' of type 'aruba-interface-vlan'"` | Bound the device-rendered `sys_policy_pap_<ROLE>` to an SVI via `policy.access-group-vlan-in`. The device-side name never exists in Central's policy library by design — it's auto-generated at render time. | HTTP 400 — pure library-membership check, identical format for any unknown name. |
| `"Validation failure: Role-based Policies cannot be mapped to ScopeTypes.DEVICE."` (or `ScopeTypes.DEVICE_COLLECTION`) | Tried to scope-assign the `ASSOCIATION_ROLE` policy at a device or device-group scope. | HTTP 400 — explicit semantic guard. Role-based policies can only be assigned at SITE scope or higher. |
| `"Cannot find object 'X' of module 'aruba-policy'"` | Created the SVI bind directly at a DEVICE or DEVICE_COLLECTION scope referencing the policy by its CNX name, but the policy isn't *directly* assigned at that scope (effective-config inheritance doesn't count for transitive validation). | HTTP 500 (structured payload). |
| "the CNX UI won't let me apply the policy to a VLAN" / "Central UI accepts it but the QoS marking doesn't happen on the switch" | Created the SVI bind at SITE scope referencing the policy by its CNX library name. Central accepts with HTTP 200, lists everything in effective config, pushes the layer2 VLAN successfully, **silently skips the role-based policy at device-render time**, and reports `SYNCHRONIZED`. No error anywhere. | HTTP 200 — silent-skip-with-success-indication. The worst failure mode in the catalogue. |
| `"Validation failure: Policies {'X'} still part of Policy Group."` | Tried to delete the policy while it was still in the policy-group-list. | HTTP 400 — order-of-operations: remove from policy-group first. |

### Wrong-primitive runbook — diagnose and pivot

If the operator's symptom matches any row above, **stop. Don't try to make the role-based policy work for SVI marking — it can't, by design.** Run this block to confirm the diagnosis, then pivot:

```python
# Diagnose whether the policy the operator referenced is role-based.
policy_name = "QOS-P-marker"  # the name from the operator's CLI / Central UI

# Strip any device-rendered prefix the operator may have copied
candidate = policy_name
for prefix in ("sys_policy_pap_", "sys_pap_"):
    if candidate.startswith(prefix):
        candidate = candidate[len(prefix):]
        break

pol = await call_tool("central_invoke_tool", {
    "name": "central_get_policies", "params": {"name": candidate}})
data = pol.get("data", {})
if isinstance(data, dict) and "data" in data:
    data = data["data"]

diagnosis = {
    "raw_name_operator_gave":  policy_name,
    "normalized_lookup_name":  candidate,
    "found_in_library":        bool(data),
    "type":                    data.get("type") if isinstance(data, dict) else None,
    "association":             data.get("association") if isinstance(data, dict) else None,
}

if not diagnosis["found_in_library"]:
    diagnosis["verdict"] = (
        f"No policy named {candidate!r} exists in the library. If the operator "
        f"saw {policy_name!r} on the switch with a sys_policy_pap_ prefix, the "
        "non-prefixed name is what would be in the library."
    )
elif diagnosis["association"] == "ASSOCIATION_ROLE":
    diagnosis["verdict"] = (
        f"Policy {candidate!r} is ASSOCIATION_ROLE — port-access role-based. "
        "It CANNOT be SVI-bound. The CLI 'apply policy <name> routed-in' on an "
        "interface vlan expects ASSOCIATION_INTERFACE. The role-based policy "
        "renders as 'port-access policy sys_policy_pap_<role>' on the switch "
        "and only enforces on authenticated port-access sessions — never on "
        "SVI transit traffic."
    )
    diagnosis["remediation"] = (
        "1) DELETE the existing ASSOCIATION_ROLE policy (and the associated "
        "role + role-based policy-group-entry) — they were never going to work "
        "for transit marking.\n"
        "2) REBUILD as ASSOCIATION_INTERFACE using sections A (named-condition) "
        "+ B (POLICY_QOS with association: ASSOCIATION_INTERFACE) + C (SVI bind "
        "via central_manage_vlan_interfaces policy.access-group-vlan-in).\n"
        "3) SCOPE-ASSIGN the layer2-vlan + vlan-interfaces objects at the "
        "scope containing the target devices (the policy itself does NOT need "
        "explicit assignment when bound through the SVI — Central pulls it in "
        "transitively).\n"
        "4) AFTER push: run central_show_commands for 'show port-access policy' "
        "and 'show class ip' to confirm the artifacts rendered. SYNCHRONIZED "
        "alone is not enough."
    )
elif diagnosis["association"] == "ASSOCIATION_INTERFACE":
    diagnosis["verdict"] = (
        f"Policy {candidate!r} is already ASSOCIATION_INTERFACE — correct "
        "primitive for SVI bind. Proceed to section C; bind it via "
        "interface-vlan policy.access-group-vlan-in."
    )
else:
    diagnosis["verdict"] = (
        f"Policy {candidate!r} found but association is "
        f"{diagnosis['association']!r} — neither standard branch. Read the "
        "full policy via central_get_policies and confirm with the operator "
        "before any write."
    )

diagnosis
```

The `remediation` block above is the pivot to the existing sections A/B/C. **Do not attempt to keep the role-based artifacts** — even if you got the SVI bind to take at the API layer (it will at SITE scope), the device-side render will silently no-op and Central will lie about the sync state. Delete and rebuild.

### One more wrinkle — policy-group membership

If the operator's setup involves direct scope-assignment of a `policy` object (rare for traditional SVI-bound policies but required for role-based ones), the policy must first appear in the singleton `policy-group`'s `policy-group-list`. The CNX UI does this implicitly when the operator creates a role-based policy in the UI; via tool calls it's:

```python
await call_tool("central_manage_policy_group_list", {
    "name": "<policy-name>",
    "action_type": "update",   # NOT 'create' — the container exists; 'create' returns
                                # "Cannot create duplicate config, Module = Policy Group already exists"
    "payload": {"name": "<policy-name>", "position": 100},
    "confirmed": True,
})
```

And on cleanup: remove the policy-group-list entry BEFORE deleting the policy itself, or `central_manage_policies(action_type='delete')` returns
`"Validation failure: Policies {'<name>'} still part of Policy Group."`

## Exact shapes (live-verified)

### A. Traffic class — `central_manage_named_conditions`

`payload = {"rules-type": "NAMED_CONDITION_IP", "condition-rule": [ <rule>, … ]}`

Each `match` line → one `condition-rule`. **Every `source`/`destination` MUST
carry `type: "ADDRESS_SUBNET_MASK"`** or the address is silently dropped, and the
value is **dotted-quad / dotted-mask, NOT CIDR** (a host = `/255.255.255.255`).
Carry the source config's dotted masks through unchanged (don't convert to CIDR).

```jsonc
// match any any 203.0.113.0/255.255.255.0 count   (network destination)
{"position": 20, "count": true, "ip-header": {"protocol": "PROTOCOL_ANY"},
 "destination": {"type": "ADDRESS_SUBNET_MASK",
                 "subnet-address": {"network-subnet-address": "203.0.113.0/255.255.255.0"}}}

// match any any 10.16.46.254 count   (host -> /255.255.255.255)
{"position": 5, "count": true, "ip-header": {"protocol": "PROTOCOL_ANY"},
 "destination": {"type": "ADDRESS_SUBNET_MASK",
                 "subnet-address": {"network-subnet-address": "10.16.46.254/255.255.255.255"}}}

// match udp 10.128.3.40/255.128.7.255 range 8000 48200 any count   (source + src port range)
{"position": 20, "count": true, "ip-header": {"protocol": "IP_UDP"},
 "source": {"type": "ADDRESS_SUBNET_MASK",
            "subnet-address": {"network-subnet-address": "10.128.3.40/255.128.7.255"}},
 "transport-fields": {"source-port": {"operator": "COMPARISON_RANGE", "min": 8000, "max": 48200}}}

// match udp any 10.33.20.0/255.255.255.0 eq 5060   (dest + dest port)
{"position": 130, "count": true, "ip-header": {"protocol": "IP_UDP"},
 "destination": {"type": "ADDRESS_SUBNET_MASK",
                 "subnet-address": {"network-subnet-address": "10.33.20.0/255.255.255.0"}},
 "transport-fields": {"destination-port": {"operator": "COMPARISON_EQ", "min": 5060}}}

// match any any any dscp AF31 count   (match on a DSCP value, no address)
{"position": 10, "count": true, "ip-header": {"protocol": "PROTOCOL_ANY", "dscp": "AF31"}}

// ignore any any any fragment count
{"position": 360, "count": true, "ignore": true,
 "ip-header": {"protocol": "PROTOCOL_ANY", "fragment": true}}
```

Field notes:
- `protocol`: `PROTOCOL_ANY`, `IP_TCP`, `IP_UDP`, `IP_ICMP`, `IP_IGMP`, …
- ports: `operator` ∈ `COMPARISON_EQ` (use `min` only) / `COMPARISON_RANGE` (`min`+`max`);
  source port op → `source-port`, dest port op → `destination-port`. Convert named
  ports to numbers (`ssh`→22, `http`→80, `ldap`→389, `snmp-trap`→162, `syslog`→514,
  `microsoft-ds`→445).
- `comment` lines are labels — skip them (they don't classify traffic).
- `count` (CX) vs `log` (PVOS): use `count: true` on CX.

### B. Marker policy — `central_manage_policies`

```jsonc
{
  "type": "POLICY_QOS",
  "association": "ASSOCIATION_INTERFACE",
  "security-policy": {
    "type": "SECURITY_POLICY_TYPE_DEFAULT",
    "policy-rule": [
      // class ip QOS-m-voice-ef action local-priority 5 action dscp EF
      {"position": 10,
       "condition": {"type": "CONDITION_NAMED",
                     "named-condition": {"condition-reference": "QOS-m-voice-ef"}},
       "action": {"type": "ACTION_QOS",
                  "secondary-actions": {"local-queue-priority": 5, "dscp": "EF"}}},
      // class ip default action local-priority 1 action dscp CS0
      {"position": 90,
       "condition": {"type": "CONDITION_DEFAULT"},
       "action": {"type": "ACTION_QOS",
                  "secondary-actions": {"local-queue-priority": 1, "dscp": "DEFAULT"}}}
    ]
  }
}
```

Field notes:
- **`association`: MUST be `"ASSOCIATION_INTERFACE"`** for SVI bind. The alternative `"ASSOCIATION_ROLE"` produces a port-access role-based policy that renders as `port-access policy sys_policy_pap_<role>` on the device and cannot be SVI-bound (see the "Path picker" section above). If the operator's source config came from a CNX role-based policy, REBUILD with this field set to `ASSOCIATION_INTERFACE` — don't try to convert in place.
- **class reference**: `condition.named-condition.condition-reference` = the
  `named-condition` name. (This field is undocumented — do not look for it in
  `payload_schema`; do NOT use `condition.name`, which is rejected.)
- **default class** (`class ip default`): `condition.type: "CONDITION_DEFAULT"`,
  no `named-condition`.
- **action**: `type: "ACTION_QOS"`; `secondary-actions.local-queue-priority` is an
  **integer** (maps `local-priority N` directly); `secondary-actions.dscp` is the
  DSCP enum. **`CS0` → `"DEFAULT"`** (CS0 isn't a valid enum value; DSCP 0 is `DEFAULT`).

### C. Interface/VLAN bind (only if the config has `apply policy …`)

`apply policy <name> routed-in` on `interface vlan <id>`:
1. **Create the layer2 VLAN if missing** — `central_get_layer2_vlan(vlan="<id>")`; if absent,
   `central_manage_layer2_vlan(vlan="<id>", action_type="create", payload={"vlan": <id>})`.
2. **Apply the policy on the SVI** — `central_manage_vlan_interfaces(id="<id>",
   action_type="create", payload={"id": "<id>", "policy": {"access-group-vlan-in": "<policy>"}})`.
   `access-group-vlan-in` = the **routed-in** direction on a CX SVI (`access-group-in`
   is plain `in`/bridged; `service-policy-in` is PVOS).
3. **For a device-touching scope assignment**, both the layer2-vlan and the vlan-interfaces objects get scope-assigned (`central_manage_config_assignment` with `profile_type: 'layer2-vlan'` and `'vlan-interfaces'`, `device_function: 'ACCESS_SWITCH'`). Where the bound policy is `ASSOCIATION_INTERFACE`, Central pulls it through transitively. **Where the bound policy is `ASSOCIATION_ROLE`, Central will accept the create but silently no-op the bind on the device — see rule 5 and the Path picker.**
4. **Verify on the device** — call `central_show_commands(device_type='cx', commands='show running-config interface vlan <id>')` (and `show vlan <id>`, `show class ip`, `show policy` where allowed) and assert the bind appears. `central_get_devices_config_health` reporting `SYNCHRONIZED` is NOT sufficient — it stays `SYNCHRONIZED` even when the role-based-policy case silently drops the render.

Quick error→cause table for the bind step:

| Error | What it means | Fix |
|---|---|---|
| HTTP 400 `"Cannot find in library 'X' of type 'aruba-policy' referred in '<vlan-id>' of type 'aruba-interface-vlan'"` | The policy name isn't in Central's policy library at any scope visible to the validation. Typically: the operator copied a device-rendered `sys_policy_pap_<X>` name (auto-generated, never in the library). | Strip `sys_policy_pap_` / `sys_pap_` prefix and re-check via `central_get_policies(name=…)`. If still missing, the policy needs creating first. |
| HTTP 500 `"Cannot find object 'X' of module 'aruba-policy'"` | You're creating the SVI at a DEVICE or DEVICE_COLLECTION scope and the referenced policy isn't *directly assigned* at that scope (effective-config inheritance doesn't satisfy this validator). | Either create at SITE scope (where the policy is directly assigned) OR assign the policy at the same narrower scope first. |
| HTTP 200 + device shows VLAN but no policy render + `SYNCHRONIZED` | You pointed an `ASSOCIATION_ROLE` policy at the SVI. Pivot per the Path picker. | Don't try to convert; rebuild as `ASSOCIATION_INTERFACE`. |

If the config has no `apply policy …` line, skip this section entirely.

### D. Queue-profile — `central_manage_qos_queues`

Maps local-priority (the marker's output) → hardware queue. The CLI form
`map queue Q local-priority LP` becomes one entry per queue in a `priority`
array; each entry's `priorities` is a list (a queue can absorb multiple LPs).

```jsonc
// qos queue-profile branch-1
//   map queue 0 local-priority 0  ...  map queue 4 local-priority 4
//   map queue 5 local-priority 7  (q5 absorbs lp7 — scavenger)
//   map queue 6 local-priority 6
//   map queue 7 local-priority 5  (q7 absorbs lp5 — voice / EF)
{
  "priority": [
    {"queue": 0, "priorities": [0]},
    {"queue": 1, "priorities": [1]},
    {"queue": 2, "priorities": [2]},
    {"queue": 3, "priorities": [3]},
    {"queue": 4, "priorities": [4]},
    {"queue": 5, "priorities": [7]},
    {"queue": 6, "priorities": [6]},
    {"queue": 7, "priorities": [5]}
  ]
}
```

Validation rules (enforce client-side before write):
- **All eight local-priorities (0–7) must be mapped, no duplicates.** A queue
  may carry multiple LPs (`priorities: [3, 4]`), but the same LP must not
  appear in two queues. Walk the array and fail fast if either rule breaks.
- **Queue numbers** 0–7 (CX hardware).
- **Profile name**: 1–64 chars, `[a-zA-Z0-9._-]+`. Cannot be `DEFAULT` (that's
  the factory-default literal — see section F).

Distiller note: `payload_schema` annotates `priority` as Switch PVOS only, but
the inner item fields list both CX and PVOS and the API accepts the shape on CX
(round-trip verified). Ignore the top-level annotation; trust the shape.

### E. Schedule-profile — `central_manage_qos_schedules`

Per-queue scheduling algorithm + weight (or strict + optional rate cap). The
CLI forms `dwrr queue Q weight W` and `wfq queue Q weight W` both collapse
to `algorithm: "WEIGHTED"` at the API — the API enum has no DWRR/WFQ split.
(Factory-default schedule-profile is all queues `WEIGHTED` weight 1, which
on the device runs as WFQ.)

```jsonc
// qos schedule-profile QOS-P-mpls-scheduler
//   dwrr queue 0..6 weight ...    (WEIGHTED at the API)
//   strict queue 7 max-bandwidth 768 kbps
{
  "sched-entries": [
    {"queue": 0, "algorithm": "WEIGHTED", "weight": 5},
    {"queue": 1, "algorithm": "WEIGHTED", "weight": 9},
    {"queue": 2, "algorithm": "WEIGHTED", "weight": 41},
    {"queue": 3, "algorithm": "WEIGHTED", "weight": 21},
    {"queue": 4, "algorithm": "WEIGHTED", "weight": 20},
    {"queue": 5, "algorithm": "WEIGHTED", "weight": 1},
    {"queue": 6, "algorithm": "WEIGHTED", "weight": 3},
    {"queue": 7, "algorithm": "STRICT",   "max-bandwidth-kbps": 768}
  ]
}
```

Field notes:
- `algorithm` enum: `WEIGHTED` (DWRR or WFQ), `STRICT`, `MIN_BANDWIDTH`. Mandatory per entry.
- `weight`: integer 1–1023; for `WEIGHTED` and `MIN_BANDWIDTH`.
- `max-bandwidth-kbps` (integer kbps) XOR `max-bandwidth-percent` (integer 1–100). Never both on one entry.
- `burst`: integer kilobytes, valid only when one of the max-bandwidth fields is set.
- `minimum-bandwidth`: integer 1–100 (percent), for `MIN_BANDWIDTH` only.

Validation rules:
- **Must define every queue that appears in the paired queue-profile** (same queue numbers, same count — typically all 8 on CX).
- **All entries must use the same `algorithm`, except the highest-numbered queue may be `STRICT`.** Mixed WEIGHTED+STRICT on lower queues is rejected. `STRICT queue 7 + WEIGHTED queue 0..6` is the only legal mix.
- Profile name: same character/length rules as queue-profile; cannot be `DEFAULT`.

### F. System-wide apply + DSCP-map — `central_manage_qos_global`

One named library `qos-global` object holds **both** the queue/schedule refs
AND the DSCP-map. The CLI atomic line `apply qos queue-profile X schedule-profile Y`
plus the `qos dscp-map …` block all become **one write** in Central, then a
scope assignment to activate on devices.

```jsonc
// apply qos queue-profile branch-1 schedule-profile QOS-P-mpls-scheduler
// qos dscp-map 40 local-priority 7 color green
// qos dscp-map 41 local-priority 7 color green
// ... (46/EF intentionally skipped — preserves factory voice mapping)
// qos dscp-map 47 local-priority 7 color green
{
  "q-profile":     "branch-1",                      // custom profile name (oneOf branch 1)
  "sched-profile": "QOS-P-mpls-scheduler",          // custom profile name (oneOf branch 1)
  "dscp-map": [
    {"dscp": 40, "priority": 7, "color": "GREEN"},
    {"dscp": 41, "priority": 7, "color": "GREEN"},
    {"dscp": 42, "priority": 7, "color": "GREEN"},
    {"dscp": 43, "priority": 7, "color": "GREEN"},
    {"dscp": 44, "priority": 7, "color": "GREEN"},
    {"dscp": 45, "priority": 7, "color": "GREEN"},
    {"dscp": 47, "priority": 7, "color": "GREEN"}
  ]
}
```

**The five translation points that small models miss:**

1. **`WEIGHTED` covers BOTH `dwrr` and `wfq`.** The CLI distinction is lost at the API. Operators thinking "wfq" should send `algorithm: "WEIGHTED"` with `weight: 1` per queue (matches factory-default behavior).
2. **`factory-default` is the enum literal `"DEFAULT"`**, not the string `"factory-default"`. `q-profile` and `sched-profile` are each a `oneOf`: a custom profile name (1-64 chars, `[a-zA-Z0-9._-]+`) OR the literal `"DEFAULT"`. So `apply qos queue-profile branch-1 schedule-profile factory-default` becomes `{"q-profile": "branch-1", "sched-profile": "DEFAULT"}`.
3. **`qos-global` is a named library object, not a singleton.** The path is `/qos-global/{name}` with full CRUD. An operator-chosen name (e.g. `"Global-QoS-MPLS"`) holds the refs + dscp-map; **activation on devices happens via scope-assignment**, not by the create itself.
4. **DSCP-map lives inside qos-global** as a sub-array — not a separate object. The seven `qos dscp-map …` CLI lines + the `apply qos …` line collapse to one `central_manage_qos_global` payload.
5. **PATCH semantics — field-preserve + array-upsert-by-key.** On `action_type: "update"`:
   - Top-level fields you don't send are **preserved** (sending only `q-profile`+`sched-profile` leaves `dscp-map`, `cos-map`, `trust`, etc. intact).
   - Array fields (`dscp-map`, etc.) are **upserted by their `x-key`** (`dscp` for dscp-map). Entries you send are merged into the existing array by key; entries you don't send are kept. **You cannot remove an array entry by omission** — that requires deleting the whole qos-global and recreating, or a future per-row delete pattern.

Field notes:
- `dscp-map[].dscp` 0–63, `.priority` 0–7, `.color` `GREEN|YELLOW|RED`. Optional `.cos-override` (0–7, 802.1p remark) and `.name`.
- `cos-map` (peer field) handles L2 CoS in the same shape. `trust` enum: `DEFAULT`/`DOT1P`/`DSCP`/`IP_PRECEDENCE`/`NONE`/`DEVICE_ARUBA_AP`/`DEVICE_NONE`.
- After creating the qos-global, **assign it to the target scope** via the config-assignments tool so devices in that scope pick it up. Library-only creation doesn't activate anything.

### G. Updating an applied profile — automated ritual

The qos-global API rejects edits to a queue-profile or schedule-profile while
that profile is currently applied (`q-profile` or `sched-profile` on the active
qos-global). The recovery procedure is documented in the spec: flip qos-global
to `DEFAULT`/`DEFAULT`, edit the profile, restore the refs. Paste this block —
inputs at the top, the rest runs:

```python
# Update an applied queue- or schedule-profile safely.
# PATCH semantics: any qos-global field you don't send is preserved; dscp-map /
# cos-map / trust are kept intact across the flip.
profile_name    = "QOS-P-mpls-scheduler"          # the profile being edited
profile_kind    = "schedule"                      # "queue" or "schedule"
qos_global_name = "Global-QoS-MPLS"               # the active qos-global object
edit_payload    = {                               # the new profile shape
    "sched-entries": [
        # ... your updated sched-entries ...
    ],
}

def _unwrap(resp):
    d = resp.get("data", {})
    return d.get("data", d) if isinstance(d, dict) else d

status = {"steps": [], "ok": True, "plan": None}

# 1) Read the current qos-global to learn what's applied
current = await call_tool("central_invoke_tool", {
    "name": "central_get_qos_global", "params": {"name": qos_global_name}})
cur = _unwrap(current)
old_q = cur.get("q-profile")
old_s = cur.get("sched-profile")
status["steps"].append({"step": "read_current", "old_q": old_q, "old_s": old_s})

# 2) Decide whether the flip ritual is needed
ritual_needed = (
    (profile_kind == "queue"    and old_q == profile_name) or
    (profile_kind == "schedule" and old_s == profile_name)
)
status["ritual_needed"] = ritual_needed
status["plan"] = (
    f"flip {qos_global_name} -> DEFAULT/DEFAULT, edit {profile_kind} profile "
    f"{profile_name!r}, restore refs ({old_q!r}/{old_s!r}); "
    "dscp-map and other qos-global fields are preserved by PATCH semantics"
    if ritual_needed else
    f"profile {profile_name!r} is not currently applied to {qos_global_name!r} "
    "(old_q/old_s shown above) — editing in place; no flip needed"
)

# 3) Flip qos-global to DEFAULT/DEFAULT (only if ritual needed)
if ritual_needed:
    flip = await call_tool("central_manage_qos_global", {
        "name": qos_global_name, "action_type": "update",
        "payload": {"q-profile": "DEFAULT", "sched-profile": "DEFAULT"},
        "confirmed": True})
    flip_ok = flip.get("ok")
    status["steps"].append({"step": "flip_to_default", "ok": flip_ok, "status": flip.get("status")})
    if not flip_ok:
        status["ok"] = False
        status["failed_at"] = "flip_to_default"

    # Read-back assert the flip actually took
    if status["ok"]:
        rb = await call_tool("central_invoke_tool", {
            "name": "central_get_qos_global", "params": {"name": qos_global_name}})
        rb_data = _unwrap(rb)
        flip_seen_ok = (rb_data.get("q-profile") == "DEFAULT"
                        and rb_data.get("sched-profile") == "DEFAULT")
        status["steps"].append({"step": "verify_flip", "ok": flip_seen_ok,
                                "q": rb_data.get("q-profile"),
                                "s": rb_data.get("sched-profile")})
        if not flip_seen_ok:
            status["ok"] = False
            status["failed_at"] = "verify_flip"

# 4) Edit the profile
if status["ok"]:
    edit_tool  = "central_manage_qos_queues" if profile_kind == "queue" else "central_manage_qos_schedules"
    edit_param = "q_profile_name" if profile_kind == "queue" else "sched_profile_name"
    edit = await call_tool(edit_tool, {
        edit_param: profile_name, "action_type": "update",
        "payload": edit_payload, "confirmed": True})
    edit_ok = edit.get("ok")
    status["steps"].append({"step": "edit_profile", "ok": edit_ok, "status": edit.get("status")})
    if not edit_ok:
        status["ok"] = False
        status["failed_at"] = "edit_profile"

# 5) Restore refs — always runs if we flipped, even on failure (rollback)
if ritual_needed:
    restore = await call_tool("central_manage_qos_global", {
        "name": qos_global_name, "action_type": "update",
        "payload": {"q-profile": old_q, "sched-profile": old_s},
        "confirmed": True})
    status["steps"].append({"step": "restore_refs", "ok": restore.get("ok"),
                            "rollback": not status["ok"]})

# 6) Final read-back — surface the end-state
final = await call_tool("central_invoke_tool", {
    "name": "central_get_qos_global", "params": {"name": qos_global_name}})
final_data = _unwrap(final)
status["final_state"] = {
    "q-profile":     final_data.get("q-profile"),
    "sched-profile": final_data.get("sched-profile"),
}

status
```

What this block guarantees:
- **Skip-if-not-applied**: if the profile being edited isn't currently active on `qos_global_name`, no flip happens — the profile is edited in place.
- **Read-back assertion** after the flip catches silent server-side no-ops before we proceed to edit.
- **Always-restore** in the `if ritual_needed:` block — runs whether the edit succeeded or failed, so a failed edit doesn't leave the switch on factory-default.
- **PATCH preservation** — `dscp-map`, `cos-map`, `trust`, and any other qos-global fields you didn't touch are kept across the flip and restore (verified live).

The remaining exposure window: edit fails AND restore also fails. Surface
`status["failed_at"]` and `status["final_state"]` in the operator-facing reply.

## Steps

**Decide which halves apply** before starting. The marking half (1–5) and the
system half (6–9) are independent — if the operator's intent only covers one,
skip the other.

**Step 0 — Wrong-primitive check (run when ANY of the symptoms in "Detecting
the wrong primitive" match).** If the operator referenced a name starting with
`sys_policy_pap_` or `sys_pap_`, OR they hit any of the five error patterns,
OR their last AI session ended with "no Central API path exists for this," run
the **Wrong-primitive runbook** code block first. Pivot per its `remediation`
output. **Do not proceed to step 1 with the role-based artifacts still in
play** — the rebuild step in the remediation is required.

Ingress / marking half (sections A–C):

1. **Pull schemas** for `central_manage_named_conditions` + `central_manage_policies`
   (`central_get_tool_schema`) — confirms surrounding fields/enums. The exact
   shapes above are authoritative for the parts the schema omits.
2. **Build + validate ONE class**, then **read it back and assert** the
   `source`/`destination` persisted (not just `status: success`). If a rule
   came back without its address, the `type` discriminator or mask format is
   wrong — fix per section A; do not proceed until a class round-trips intact.
3. **Bulk-create the remaining classes** (loop in one `execute` block, preserve
   `position` order), then read each back and assert rule counts + match criteria.
4. **Build the `POLICY_QOS` marker policy** (section B), read it back, assert
   every rule's `condition-reference` + `local-queue-priority` + `dscp` persisted.
5. **Bind to the VLAN** (section C) if applicable, read back the SVI, assert
   `policy.access-group-vlan-in` == the policy name. **Then run the device-side
   verification:** `central_show_commands` for `show running-config interface
   vlan <id>`, `show class ip`, and `show policy` (where allowed). Assert the
   policy and class actually rendered on the box. Skipping this step lets the
   silent-skip-with-success-indication failure mode (rule 5) through undetected.
   `central_get_devices_config_health` alone is NOT sufficient — it stays
   `SYNCHRONIZED` even when the role-based-policy case silently drops the bind.

Egress / system-wide half (sections D–F):

6. **Build the queue-profile** (section D) — `central_manage_qos_queues`, read
   back, assert every queue 0–7 is present and every local-priority 0–7 appears
   exactly once across `priorities` arrays. If the operator wants to use the
   factory queue-profile, skip this step and reference `"DEFAULT"` in step 8.
7. **Build the schedule-profile** (section E) — `central_manage_qos_schedules`,
   read back, assert all queues from the queue-profile are present, the
   single-algorithm rule (only the highest-numbered queue may be `STRICT`) holds,
   and any `STRICT` queue with a cap carries either `max-bandwidth-kbps` or
   `max-bandwidth-percent` but not both. Skip this step too if using `"DEFAULT"`.
8. **Build the qos-global** (section F) — `central_manage_qos_global` with a
   meaningful name (e.g. `Global-QoS-<intent>`), payload carrying `q-profile`,
   `sched-profile`, and any `dscp-map[]` rows. Read back; assert refs are
   strings (not the enum-literal `"DEFAULT"` unless that was intended) and
   every dscp-map row persisted with `dscp`/`priority`/`color`. **The CLI
   atomic `apply` collapses into this one write** — there is no separate
   "apply" call.
9. **Assign the qos-global to the target scope** so devices pick it up — use
   the config-assignments tool. Library-only creation doesn't activate
   anything on hardware.

Updating an already-applied profile: use the section G ritual block instead of
calling the manage tool directly — the API rejects in-place edits to applied
queue- and schedule-profiles.

## Output

- Per-object push result table (class/policy/VLAN/SVI/queue-profile/schedule-profile/qos-global → created/failed + read-back-verified).
- The marker rule order (class → local-priority + DSCP) and the queue map (queue → local-priorities).
- Confirmation the policy is bound to the VLAN interface (or noted as skipped) and the qos-global is assigned to the target scope (or noted as library-only).

**Marking half: classes → POLICY_QOS policy → VLAN+SVI bind. System half:
queue-profile → schedule-profile → qos-global (apply + dscp-map) → scope
assignment. Use the exact shapes above (the spec omits key fields, collapses
DWRR/WFQ into WEIGHTED, and uses `"DEFAULT"` as the factory-profile literal).
Read back and assert every object — the API drops under-specified subtrees
silently while returning success.**
