"""Preprocessing for the ``central:policy`` translation.

AOS 8 ``acl_sess`` records have a structure that doesn't fit the standard
per-field ``key_mapping`` template:

* Two parallel arrays per ACL (``acl_sess__v4policy`` + ``acl_sess__v6policy``)
  that need to be merged into a single Central ``policy-rule[]`` array
  with each rule tagged by ``address-family``.
* The "any any" rule pattern is bidirectional in AOS 8 but Central can't
  express it for a role-bound policy — one AOS 8 rule expands to TWO
  Central rules (``role->any`` AND ``any->role``).
* Per-rule shape varies (source / destination address types, service
  modes, action variants) and the resulting rule object can have 5-10
  optional sub-fields each.
* The role-binding inversion: AOS 8 has ``role.role__acl[]`` referencing
  ACL names; Central has ``policy.policy-rule[].condition.source.role-list``
  referencing role names. Migration needs to compute which roles
  reference each ACL by reverse-indexing all role records.

This preprocessing module collapses all that into a single helper —
``preprocess_acl_for_policy`` — that the engine invokes (declared via
the translation JSON's ``preprocessing`` field). It produces an augmented
``source_data`` dict with a ``_central_rules`` field that the translation's
key_mappings then pass through verbatim into the policy body.

Consumer contract:

* Pre-fetch all AOS 8 role records once per migration run.
* Pass them via ``runtime_values["role_records"]: list[dict]``.
* Pass each ACL's record as ``source_data``.
* Engine auto-invokes ``preprocess_acl_for_policy`` before key_mappings.

The translation's ``key_mappings`` then become trivial:

* ``name`` ← ``accname`` via ``direct_str``
* ``policy_rules`` ← ``_central_rules`` via ``direct``

No 2-arg transform needed; no ``source_data``-wide access from a
transform; the body is structurally complete in the JSON. New translations
follow the same pattern when source shape needs preprocessing.
"""

from __future__ import annotations

import ipaddress
import re
from typing import Any

from hpe_networking_mcp.translations.policy_enum_tables import (
    AOS8_APP_CATEGORY_TO_CENTRAL,
    AOS8_APP_TO_CENTRAL,
    AOS8_WEB_CATEGORY_TO_CENTRAL,
    AOS8_WEB_REPUTATION_TO_CENTRAL,
)

# ---------------------------------------------------------------------------- #
# Public entry point — declared in central:policy_v1.json's preprocessing field
# ---------------------------------------------------------------------------- #


def preprocess_acl_for_policy(source_data: dict[str, Any], runtime_values: dict[str, Any]) -> dict[str, Any]:
    """Augment an AOS 8 acl_sess record with a Central-shaped ``_central_rules`` array.

    Args:
        source_data: One AOS 8 ``acl_sess`` record with ``accname`` +
            ``acl_sess__v4policy`` + ``acl_sess__v6policy`` fields.
        runtime_values: Caller-supplied runtime context. Must include
            ``role_records: list[dict]`` (every AOS 8 role record) for the
            role-attribution reverse-index lookup. May also include
            ``central_scope_id`` (used downstream by emit_calls, not here).

    Returns:
        New dict with all original fields plus ``_central_rules: list[dict]`` —
        the Central ``policy-rule[]`` array ready to land in the policy body.
        Source data is not mutated.

    Raises:
        ValueError: If ``runtime_values`` lacks ``role_records`` (the engine
            wraps this as ``EngineError`` with translation context).
    """
    role_records = runtime_values.get("role_records")
    if role_records is None:
        raise ValueError(
            "preprocess_acl_for_policy requires runtime_values['role_records'] "
            "(list of all AOS 8 role records). Pre-fetch once via "
            "aos8_get_effective_config(object_name='role') and pass to every "
            "emit_calls invocation."
        )
    accname = source_data.get("accname")
    role_attribution = _compute_role_attribution(accname, role_records) if accname else []

    central_rules: list[dict[str, Any]] = []
    position = 1
    for variant_field, address_family in (
        ("acl_sess__v4policy", "IPV4"),
        ("acl_sess__v6policy", "IPV6"),
    ):
        for aos8_rule in source_data.get(variant_field, []) or []:
            if not isinstance(aos8_rule, dict):
                continue
            # Skip system / inherited rules — consumer should pre-filter, but
            # we're defensive in case a stray inherited entry slips through.
            flags = aos8_rule.get("_flags") or {}
            if flags.get("inherited") or flags.get("system"):
                continue
            built = _build_central_rules(aos8_rule, address_family, position, role_attribution)
            if not built:
                continue
            central_rules.extend(built)
            position += len(built)

    association = "ASSOCIATION_INTERFACE" if str(accname) in _INTERFACE_ACL_NAMES else "ASSOCIATION_ROLE"

    return {**source_data, "_central_rules": central_rules, "_association": association}


# ---------------------------------------------------------------------------- #
# Role attribution lookup
# ---------------------------------------------------------------------------- #


def _compute_role_attribution(acl_name: str, role_records: list[dict]) -> list[str]:
    """Reverse-index role records to find which roles reference this ACL.

    AOS 8 binds ACLs to roles via ``role.role__acl[].pname`` (with
    ``acl_type == "session"``). For each role, scan its role__acl array
    and collect ``rname`` values where pname matches the ACL we're
    translating. System / default / readonly entries are skipped — those
    are AOS 8 built-ins that shouldn't propagate.
    """
    out: list[str] = []
    for role in role_records or []:
        if not isinstance(role, dict):
            continue
        # Skip top-level system roles (logon, guest, voice, etc.)
        role_flags = role.get("_flags") or {}
        if role_flags.get("default"):
            continue
        acl_list = role.get("role__acl") or []
        for acl_entry in acl_list:
            if not isinstance(acl_entry, dict):
                continue
            entry_flags = acl_entry.get("_flags") or {}
            if entry_flags.get("system") or entry_flags.get("default") or entry_flags.get("readonly"):
                continue
            if acl_entry.get("acl_type") == "session" and acl_entry.get("pname") == acl_name:
                rname = role.get("rname")
                if rname and rname not in out:
                    out.append(str(rname))
                break
    return out


# ---------------------------------------------------------------------------- #
# AOS 8 named-service -> Central net-service alias table (currently empty)
# ---------------------------------------------------------------------------- #
#
# Central ships ~73 net-services whose svc-* names mirror AOS 8 conventions
# closely (svc-http, svc-https, svc-dns, svc-icmp, etc.). The translation
# passes the AOS 8 svc-name verbatim into Central's services.net-service
# field — Central rejects unknown names with a clear error rather than
# silently mistranslating. Known structural mismatches (if any surface)
# are aliased here. Empty by default.

_AOS8_TO_CENTRAL_SVC_NAME_ALIASES: dict[str, str] = {}

# AOS 8 ACL names that are INTERFACE ACLs (applied to an interface, not bound to
# a user-role). These map to Central association = ASSOCIATION_INTERFACE rather
# than the default ASSOCIATION_ROLE. `validuser` is the canonical AOS 8 interface
# session ACL. Extensible — add other interface-ACL names here as they surface.
_INTERFACE_ACL_NAMES: frozenset[str] = frozenset({"validuser"})

# AOS 8 service-name forms that denote IPv6-ICMP (ra-guard etc.). These are NOT
# real Central net-service catalog entries — they route to a RULE_PROTOCOL rule
# with ip-header.protocol = IPV6_ICMP instead of RULE_NET_SERVICE.
_ICMPV6_SERVICE_NAMES: frozenset[str] = frozenset({"icmpv6", "icmp6"})


# ---------------------------------------------------------------------------- #
# AOS 8 action -> Central action.type
# ---------------------------------------------------------------------------- #

_AOS8_ACTION_TO_CENTRAL: dict[str, str] = {
    "permit": "ACTION_ALLOW",
    "deny_opt": "ACTION_DENY",
    "deny": "ACTION_DENY",
    "apppermit": "ACTION_ALLOW",
    "appdeny_opt": "ACTION_DENY",
    "appdeny": "ACTION_DENY",
    "src-nat": "ACTION_SOURCE_NAT",
    "dst-nat": "ACTION_DESTINATION_NAT",
    "dual-nat": "ACTION_DUAL_NAT",
    "redir_opt": "ACTION_REDIRECT",
    "redirect": "ACTION_REDIRECT",
    "route": "ACTION_ROUTE",
    "captive": "ACTION_CAPTIVE_PORTAL",
    "mirror": "ACTION_MIRROR",
}


# ---------------------------------------------------------------------------- #
# Per-rule orchestration
# ---------------------------------------------------------------------------- #


def _build_central_rules(
    aos8_rule: dict,
    address_family: str,
    starting_position: int,
    role_attribution: list[str],
) -> list[dict[str, Any]]:
    """Build the Central ``policy-rule[]`` entries for one AOS 8 v4/v6policy rule.

    Returns 0, 1, or 2 Central rule dicts:

    * 0 — source rule is malformed (caller skips).
    * 1 — typical case.
    * 2 — AOS 8 "any any" pattern (src=sany AND dst=dany) on a role-bound
      ACL, which is bidirectional. Central can't express any-any for a
      role-bound policy, so we expand to ``role->any`` AND ``any->role``.
    """
    net_service_block = _build_net_service_block(aos8_rule)
    services_block = net_service_block or _build_services_block(aos8_rule)
    proto_port_block = _build_protocol_port_block(aos8_rule)
    rule_type = _determine_rule_type(aos8_rule, services_block, proto_port_block)
    action = _build_action(aos8_rule)
    time_range = aos8_rule.get("trname")

    def _make_rule(pos: int, source: dict, destination: dict) -> dict[str, Any]:
        condition: dict[str, Any] = {
            "rule-type": rule_type,
            "address-family": address_family,
            "source": source,
            "destination": destination,
        }
        if services_block:
            condition.update(services_block)
        if proto_port_block:
            condition.update(proto_port_block)
        if time_range:
            condition["time-range-name"] = str(time_range)
        return {"position": pos, "condition": condition, "action": action}

    is_any_any = aos8_rule.get("src") == "sany" and aos8_rule.get("dst") == "dany"
    if is_any_any and role_attribution:
        role_addr = {"type": "ADDRESS_ROLE", "role-list": list(role_attribution)}
        any_addr = {"type": "ADDRESS_ANY"}
        return [
            _make_rule(starting_position, role_addr, any_addr),
            _make_rule(starting_position + 1, any_addr, role_addr),
        ]

    src = _build_address(aos8_rule, "src", address_family, role_attribution)
    dst = _build_address(aos8_rule, "dst", address_family, role_attribution)
    if src is None or dst is None:
        return []
    # Role injection: an AOS 8 session ACL applied to a role scopes a bare
    # `any` to that role's users. When neither side already resolves to a role
    # and exactly one side is `any`, convert that `any` side to the attributed
    # role so the rule is role-scoped (and Central can bind it). The any+any
    # pattern is handled above by the bidirectional expansion; both-sides-
    # specific is a network-based rule and is left as-is. See issue #419.
    if role_attribution and src.get("type") != "ADDRESS_ROLE" and dst.get("type") != "ADDRESS_ROLE":
        role_addr = {"type": "ADDRESS_ROLE", "role-list": list(role_attribution)}
        src_any = src.get("type") == "ADDRESS_ANY"
        dst_any = dst.get("type") == "ADDRESS_ANY"
        if src_any and not dst_any:
            src = role_addr
        elif dst_any and not src_any:
            dst = role_addr
    return [_make_rule(starting_position, src, dst)]


# ---------------------------------------------------------------------------- #
# Address builder (source / destination)
# ---------------------------------------------------------------------------- #


def _netmask_to_prefix(netmask: str) -> int | None:
    """Convert an IPv4 dotted netmask to a CIDR prefix length, or None on bad input."""
    try:
        return ipaddress.IPv4Network(f"0.0.0.0/{netmask}", strict=False).prefixlen
    except (ValueError, ipaddress.NetmaskValueError):
        return None


def _build_address(rule: dict, side: str, address_family: str, role_attribution: list[str]) -> dict[str, Any] | None:
    """Build a Central source/destination dict from one AOS 8 rule's fields."""
    discriminator = rule.get(side)
    if discriminator is None:
        return None
    is_ipv6 = address_family == "IPV6"

    if discriminator in ("sany", "dany"):
        return {"type": "ADDRESS_ANY"}

    if discriminator in ("slocalip", "dlocalip"):
        return {"type": "ADDRESS_LOCAL"}

    if discriminator in ("shost", "dhost"):
        ip_field = "sipaddr" if side == "src" else "dipaddr"
        ip = rule.get(ip_field)
        if ip is None:
            return None
        host_key = "host-ipv6-address" if is_ipv6 else "host-ipv4-address"
        return {"type": "ADDRESS_HOST", "host-address": {host_key: str(ip)}}

    if discriminator in ("snetwork", "dnetwork"):
        addr_field = "snetaddr" if side == "src" else "dnetaddr"
        mask_field = "snetmask" if side == "src" else "dnetmask"
        addr = rule.get(addr_field)
        mask = rule.get(mask_field)
        if addr is None or mask is None:
            return None
        if is_ipv6:
            v6_prefix: int = mask if isinstance(mask, int) else int(str(mask))
            return {
                "type": "ADDRESS_NETWORK",
                "network-address": {"network-ipv6-address": f"{addr}/{v6_prefix}"},
            }
        v4_prefix = _netmask_to_prefix(str(mask))
        if v4_prefix is None:
            return None
        return {
            "type": "ADDRESS_NETWORK",
            "network-address": {"network-ipv4-address": f"{addr}/{v4_prefix}"},
        }

    if discriminator in ("salias", "dalias"):
        alias_field = "srcalias" if side == "src" else "dstalias"
        alias = rule.get(alias_field)
        if alias is None:
            return None
        # A netdestination reference resolves in the `ac-netgroup` namespace —
        # we migrate netdestinations to Central net-groups (see central:net_group),
        # not to host-address aliases. Per roles-policy.json the top-level
        # `net-group` field is "Only applicable when type is ADDRESS_ALIAS";
        # host-address-alias belongs to ADDRESS_HOST.
        return {"type": "ADDRESS_ALIAS", "net-group": str(alias)}

    if discriminator in ("suserrole", "duserrole"):
        name_field = "surname" if side == "src" else "durname"
        role_name = rule.get(name_field)
        if role_name is None:
            return None
        return {"type": "ADDRESS_ROLE", "role": str(role_name)}

    if discriminator in ("suser", "duser"):
        if not role_attribution:
            return {"type": "ADDRESS_ANY"}
        return {"type": "ADDRESS_ROLE", "role-list": list(role_attribution)}

    if discriminator in ("suser_addr", "duser_addr"):
        return {"type": "ADDRESS_USER"}

    return None


# ---------------------------------------------------------------------------- #
# Service / protocol / port builders
# ---------------------------------------------------------------------------- #


def _build_net_service_block(rule: dict) -> dict[str, Any] | None:
    """Build Central ``services.net-service`` reference for AOS 8 named svc-* rules.

    Central ships a net-services catalog with svc-* names mirroring AOS 8's
    convention (svc-http, svc-https, svc-dns, svc-icmp, etc.). The
    translation passes the AOS 8 svc-name through; Central rejects unknown
    names with a clear error rather than silently mistranslating.
    """
    if rule.get("svc") != "service-name" or rule.get("service_app") != "service":
        return None
    name = rule.get("service-name") or rule.get("service_name")
    if not name:
        return None
    # ICMPv6 / ra-guard is NOT a real net-service catalog entry — route it to the
    # protocol-rule path (RULE_PROTOCOL + ip-header.protocol=IPV6_ICMP) instead.
    if str(name).lower() in _ICMPV6_SERVICE_NAMES:
        return None
    central_name = _AOS8_TO_CENTRAL_SVC_NAME_ALIASES.get(str(name), str(name))
    return {"services": {"net-service": central_name}}


def _build_services_block(rule: dict) -> dict[str, Any] | None:
    """Build Central ``condition.services`` block for app / web-cc rules."""
    if rule.get("service_app") != "app_opt":
        return None
    awt = rule.get("app_web_type")
    if awt == "app":
        appname = rule.get("appname")
        if not appname:
            return None
        central_val = AOS8_APP_TO_CENTRAL.get(str(appname), str(appname))
        return {"services": {"application": central_val}}
    if awt == "app_cat":
        cat = rule.get("appname")
        if not cat:
            return None
        central_val = AOS8_APP_CATEGORY_TO_CENTRAL.get(str(cat), str(cat).upper())
        return {"services": {"app-category": central_val}}
    if awt in ("web_cc_cat", "web_cat"):
        # AOS 8 REST emits ``web_cat`` for WebCC-category rules (live-verified on
        # 8.13 — see /md/Campus block-high-risk_web); the older ``web_cc_cat``
        # spelling never matched real API output, so category rules silently
        # fell through to the RULE_ANY default (a category-deny became a
        # deny-everything). Accept both.
        cat = rule.get("webcccatgname")
        if not cat:
            return None
        central_val = AOS8_WEB_CATEGORY_TO_CENTRAL.get(str(cat), str(cat).replace("/", "-").upper())
        return {"services": {"web-category": central_val}}
    if awt == "web_cc_rep":
        rep = rule.get("web_rep2") or rule.get("web_rep")
        if not rep:
            return None
        # web_rep2 may carry trailing digit (e.g. "high-risk2"); strip before lookup.
        rep_norm = re.sub(r"\d+$", "", str(rep)) or str(rep)
        central_val = AOS8_WEB_REPUTATION_TO_CENTRAL.get(rep_norm, rep_norm.replace("-", "_").upper())
        return {"services": {"web-reputation": central_val}}
    return None


def _build_protocol_port_block(rule: dict) -> dict[str, Any] | None:
    """Build Central ``ip-header`` + ``transport-fields`` for ICMP / proto+port rules."""
    svc_mode = rule.get("svc")
    service_app = rule.get("service_app")

    if service_app != "service":
        return None

    # ra-guard / IPv6-ICMP: AOS 8 surfaces this as a service-name (e.g. "icmpv6")
    # which is not a real net-service. Emit a protocol rule on IPV6_ICMP.
    if svc_mode == "service-name":
        name = rule.get("service-name") or rule.get("service_name")
        if name and str(name).lower() in _ICMPV6_SERVICE_NAMES:
            return {"ip-header": {"protocol": "IPV6_ICMP"}}
        return None

    if svc_mode == "icmp":
        ip_header: dict[str, Any] = {"protocol": "IP_ICMP"}
        icmp_type = rule.get("icmp_type")
        if icmp_type:
            ip_header["icmp"] = {"icmp-type": str(icmp_type)}
        return {"ip-header": ip_header}

    if svc_mode in ("tcp_udp", "tcp", "udp"):
        proto = rule.get("proto")
        # AOS 8 may return proto as a name ("tcp"/"udp") or a protocol number
        # (6/17). Map both — a numeric proto that fell through used to drop the
        # whole block, silently degrading the rule to RULE_ANY (issue #419).
        proto_enum = {"tcp": "IP_TCP", "udp": "IP_UDP", "6": "IP_TCP", "17": "IP_UDP"}.get(str(proto).lower())
        if proto_enum is None:
            return None
        out: dict[str, Any] = {"ip-header": {"protocol": proto_enum}}
        port1 = rule.get("port1")
        port2 = rule.get("port2")
        if port1 is not None:
            min_port = int(port1)
            # Central's PortConfig: `max` is only valid with COMPARISON_RANGE;
            # a single port must use COMPARISON_EQ + min only (live-confirmed
            # 400 otherwise — issue #419).
            if port2 is not None and int(port2) != min_port:
                out["transport-fields"] = {
                    "destination-port": {"operator": "COMPARISON_RANGE", "min": min_port, "max": int(port2)}
                }
            else:
                out["transport-fields"] = {"destination-port": {"operator": "COMPARISON_EQ", "min": min_port}}
        return out

    return None


def _determine_rule_type(rule: dict, services_block: dict | None, proto_port_block: dict | None) -> str:
    """Pick the appropriate Central ``condition.rule-type`` enum value."""
    if services_block is not None:
        services = services_block.get("services", {})
        if "net-service" in services:
            return "RULE_NET_SERVICE"
        if "application" in services:
            return "RULE_APPLICATION"
        if "app-category" in services:
            return "RULE_APP_CATEGORY"
        if "web-category" in services:
            return "RULE_WEB_CATEGORY"
        if "web-reputation" in services:
            return "RULE_WEB_REPUTATION"
    if proto_port_block is not None:
        protocol = proto_port_block.get("ip-header", {}).get("protocol")
        if protocol == "IP_TCP":
            return "RULE_TCP"
        if protocol == "IP_UDP":
            return "RULE_UDP"
        return "RULE_PROTOCOL"
    return "RULE_ANY"


# ---------------------------------------------------------------------------- #
# Action builder
# ---------------------------------------------------------------------------- #


def _build_action(rule: dict) -> dict[str, Any]:
    """Build Central ``action`` dict from one AOS 8 rule's action + sub-fields."""
    aos8_action = rule.get("action") or rule.get("appaction")
    central_type = _AOS8_ACTION_TO_CENTRAL.get(str(aos8_action), "ACTION_ALLOW")
    action: dict[str, Any] = {"type": central_type}

    if rule.get("log"):
        action.setdefault("secondary-actions", {})["log"] = True
    # `blacklist` is NOT an action type in AOS 8 — it's a per-rule option that
    # denylists the client. Central models it as a secondary-action flag layered
    # on top of the base action (keep permit/deny, add the denylist flag).
    if rule.get("blacklist"):
        action.setdefault("secondary-actions", {})["denylist"] = True
    if rule.get("app-send-deny-response"):
        action["send-deny-response"] = True

    if central_type == "ACTION_DESTINATION_NAT":
        # Central destination-nat sub-config uses `port` / `ip-address`
        # (roles-policy.json), not the AOS 8-flavored dest-port / dest-address.
        dst_nat: dict[str, Any] = {}
        if rule.get("dnatport") is not None:
            dst_nat["port"] = int(rule["dnatport"])
        if rule.get("dnataddr") is not None:
            dst_nat["ip-address"] = str(rule["dnataddr"])
        if dst_nat:
            action["destination-nat"] = dst_nat

    if central_type == "ACTION_DUAL_NAT":
        # Central dual-nat requires `nat-pool` (x-mandatory) + optional `port`.
        dual_nat: dict[str, Any] = {}
        if rule.get("dualnatpool") is not None:
            dual_nat["nat-pool"] = str(rule["dualnatpool"])
        if rule.get("dualnatport") is not None:
            dual_nat["port"] = int(rule["dualnatport"])
        if dual_nat:
            action["dual-nat"] = dual_nat

    if central_type == "ACTION_REDIRECT":
        # Central redirect sub-config is discriminated by `destination`:
        # REDIRECT_TUNNEL → tunnel (int id); REDIRECT_TUNNEL_GROUP → tunnel-group (name).
        re_dir = rule.get("re_dir")
        redirect: dict[str, Any] = {}
        if re_dir == "tunnel" and rule.get("tunid") is not None:
            redirect = {"destination": "REDIRECT_TUNNEL", "tunnel": int(rule["tunid"])}
        elif re_dir == "tunnel-group" and rule.get("tungrpname") is not None:
            redirect = {"destination": "REDIRECT_TUNNEL_GROUP", "tunnel-group": str(rule["tungrpname"])}
        if redirect:
            action["redirect"] = redirect

    return action
