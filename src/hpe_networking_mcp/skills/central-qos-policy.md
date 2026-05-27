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

  Switch QoS in Central decomposes into objects built IN ORDER: (1) traffic
  classes = `named-condition`, (2) the marker/classifier policy = `policy`
  with `type: POLICY_QOS`, (3) optional interface/VLAN binding (create the
  VLAN if missing). This skill carries EXACT, live-verified payload shapes —
  several key fields are UNDOCUMENTED in the OpenAPI spec, so the schema alone
  is not enough (see the "exact shapes" sections below).

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
  - central_get_named_condition
  - central_manage_named_condition
  - central_get_policies
  - central_manage_policy
  - central_get_vlan
  - central_manage_vlan
  - central_get_interface_vlan
  - central_manage_interface_vlan
---

# Aruba Central switch QoS policy build

## Objective

Build a switch QoS classifier/marker configuration in Central from an
operator's intent or an existing AOS-CX / AOS-S CLI config, as structured
config-model objects — **not** a raw CLI template block.

A typical switch QoS config (CLI):

```
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
```

### CLI → Central object mapping

| CLI construct | Central object | Tool |
|---|---|---|
| `class ip <name>` + `match`/`ignore` lines | traffic class (`named-condition`) | `central_manage_named_condition` |
| `policy <name>` + `class … action …` | QoS marker policy (`policy`, `type: POLICY_QOS`) | `central_manage_policy` |
| `interface vlan <id>` (the VLAN itself) | layer2 VLAN | `central_manage_vlan` |
| `apply policy <name> routed-in` on the SVI | VLAN-interface policy bind | `central_manage_interface_vlan` |

**This is a write workflow** — every create fires elicitation unless
`confirmed=true`, and requires `ENABLE_CENTRAL_WRITE_TOOLS`.

## The three rules that prevent silent failure

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

3. **The marker policy IS `central_manage_policy`** (`type: POLICY_QOS`) — its
   one-line description says "firewall policy" but `/policies` is unified. Don't
   conclude "no QoS tool exists" and fall back to a CLI template.

## Prerequisites

- `ENABLE_CENTRAL_WRITE_TOOLS` on (else build + show payloads only, don't write). The first `central_get_tool_schema` / create call surfaces any reachability problem — no separate health pre-flight needed.
- **Library scope** unless told otherwise: omit `scope_id` (build everything
  shared). For a scoped object pass `scope_id` + `device_function`.
- Switch OS is CX in the verified shapes below (`count`, `subnet-address`,
  `access-group-vlan-in` are CX). `device_types` tags in `payload_schema` are
  advisory/inconsistent — don't hard-gate on them.

## Exact shapes (live-verified)

### A. Traffic class — `central_manage_named_condition`

`payload = {"rules-type": "NAMED_CONDITION_IP", "condition-rule": [ <rule>, … ]}`

Each `match` line → one `condition-rule`. **Every `source`/`destination` MUST
carry `type: "ADDRESS_SUBNET_MASK"`** or the address is silently dropped, and the
value is **dotted-quad / dotted-mask, NOT CIDR** (a host = `/255.255.255.255`).
Carry the source config's dotted masks through unchanged (don't convert to CIDR).

```jsonc
// match any any 165.130.0.0/255.255.0.0 count   (network destination)
{"position": 20, "count": true, "ip-header": {"protocol": "PROTOCOL_ANY"},
 "destination": {"type": "ADDRESS_SUBNET_MASK",
                 "subnet-address": {"network-subnet-address": "165.130.0.0/255.255.0.0"}}}

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

### B. Marker policy — `central_manage_policy`

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
1. **Create the layer2 VLAN if missing** — `central_get_vlan(vlan="<id>")`; if absent,
   `central_manage_vlan(vlan="<id>", action_type="create", payload={"vlan": <id>})`.
2. **Apply the policy on the SVI** — `central_manage_interface_vlan(id="<id>",
   action_type="create", payload={"id": "<id>", "policy": {"access-group-vlan-in": "<policy>"}})`.
   `access-group-vlan-in` = the **routed-in** direction on a CX SVI (`access-group-in`
   is plain `in`/bridged; `service-policy-in` is PVOS).

If the config has no `apply policy …` line, skip this section entirely.

## Steps

1. **Pull schemas** for `central_manage_named_condition` + `central_manage_policy`
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
   `policy.access-group-vlan-in` == the policy name.

## Output

- Per-object push result table (class/policy/VLAN/SVI → created/failed + read-back-verified).
- The marker rule order (class → local-priority + DSCP).
- Confirmation the policy is bound to the VLAN interface (or noted as skipped).

**Build classes → POLICY_QOS policy → VLAN+SVI bind. Use the exact shapes above
(the spec omits key fields). Read back and assert every object — the API drops
under-specified subtrees silently while returning success.**
