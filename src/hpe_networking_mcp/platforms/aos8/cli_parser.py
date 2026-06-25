"""AOS 8 CLI → canonical config-record parser (a source-record producer).

This is the CLI counterpart to ``aos8_get_effective_config`` (which produces
records from the REST API). It parses pasted/uploaded AOS 8 running-config CLI
into the **same record dicts the translation engine already consumes** —
``netdst`` (netdestination), ``acl_sess`` (session ACL), and ``role``
(user-role) — so the existing ``translations`` engine maps them unchanged.

It is deliberately pure and deterministic (text in, records out, no I/O), and
tolerant: a line/clause it can't fully model is captured under an ``_unparsed``
marker rather than dropped, so coverage gaps are visible to the caller and the
engine's ``unmapped_fields`` handling.

Record shapes match the engine's input contract (see each target spec's
``sources.aos8.objects[].live_shape_example``):

* netdestination → ``{"dstname": str, "netdst__entry": [{"_objname": ...}]}``
* session ACL    → ``{"accname": str, "acl_sess__v4policy": [...], "acl_sess__v6policy": [...]}``
* user-role      → ``{"rname": str, "role__acl": [{"acl_type": "session", "pname": ...}], ...}``
"""

from __future__ import annotations

import re
from typing import Any

# ``show configuration effective detail <scope>`` annotates every line with its
# provenance: ``# inherited from [<path>]`` (authored at an ancestor scope) or
# ``# local [<path>]`` (authored at the queried scope). The bracketed path is
# the object's authoring scope in BOTH cases — which is exactly what the Central
# scope mapping (aos-migration Stage 7/8) needs, and what lets us dedupe the
# same inherited object across multiple per-leaf dumps. Anchored to end-of-line
# so a stray ``#`` mid-config never false-matches.
# MULTILINE so end-of-line ``$`` matches per line — both when stripping a single
# line and when scanning the whole document in ``_has_provenance``.
_PROVENANCE_RE = re.compile(r"\s+#\s+(inherited from|local)\s+\[([^\]]*)\]\s*$", re.MULTILINE)


def _strip_provenance(line: str) -> tuple[str, str | None, bool]:
    """Split an effective-detail line into ``(clean_line, source_scope, is_local)``.

    Returns ``(line, None, False)`` for plain config (no provenance comment), so
    the parser handles ``show running-config`` and ``show configuration
    effective detail`` through the same path.
    """
    m = _PROVENANCE_RE.search(line)
    if not m:
        return line, None, False
    return line[: m.start()], m.group(2), m.group(1) == "local"


def _has_provenance(text: str) -> bool:
    """True when the text carries ``show configuration effective detail`` annotations."""
    return _PROVENANCE_RE.search(text) is not None


# AOS 8 session-ACL action keywords → value the engine's _build_action expects
# (keys of translations.readers.aos8.policy._AOS8_ACTION_TO_CENTRAL).
_ACTIONS = {
    "permit": "permit",
    "deny": "deny",
    "src-nat": "src-nat",
    "dst-nat": "dst-nat",
    "dual-nat": "dual-nat",
    "redirect": "redirect",
    "route": "route",
    # Recognised so the rule structure is captured; the engine treats these as
    # unmapped actions (see policy_v1.json unmapped_fields) — parsing them here
    # keeps the rule from being dropped as ``_unparsed``.
    "captive": "captive",
    "mirror": "mirror",
    "blacklist": "blacklist",
}

# Trailing rule options we recognise (everything else is captured raw).
_OPTION_KEYWORDS = {"log", "position", "time-range", "queue", "tos", "dot1p-priority", "blacklist", "disable-scanning"}


def parse_aos8_cli(
    text: str,
    *,
    drop_default_scopes: tuple[str, ...] = ("/", "/mm"),
) -> dict[str, Any]:
    """Parse AOS 8 CLI text into canonical config records grouped by object.

    Handles both ``show running-config`` (plain) and ``show configuration
    effective detail <scope>`` (provenance-annotated) input through one path.
    For annotated input, each record is tagged with ``_source_scope`` (its
    authoring scope — feeds the Central scope mapping), records authored at a
    system/Mobility-Manager scope are dropped as defaults, and an object that
    repeats across concatenated per-leaf dumps (same name + scope) is deduped.

    Args:
        text: AOS 8 running-config CLI (``netdestination`` / ``ip access-list
            session`` / ``user-role`` stanzas, ``!``-delimited), optionally
            carrying ``# inherited from [..]`` / ``# local [..]`` annotations.
        drop_default_scopes: authoring scopes treated as non-migratable defaults
            and skipped (annotated input only). Defaults to the system root
            ``/`` (factory built-ins) and ``/mm`` (Mobility Manager). Pass an
            empty tuple to keep everything.

    Returns:
        ``{"netdst": [...], "acl_sess": [...], "role": [...], "_warnings": [...]}``
        — record lists ready to feed the translation engine, plus warnings for
        clauses that weren't fully modelled. Annotated input additionally
        carries ``"_provenance": {"scopes_seen": [...], "dropped_default_count": int}``.
    """
    buckets: dict[str, list[dict[str, Any]]] = {"netdst": [], "acl_sess": [], "role": []}
    warnings: list[str] = []
    annotated = _has_provenance(text)
    seen: set[tuple[str, str, str]] = set()
    scopes_seen: set[str] = set()
    dropped_defaults = 0

    for header, body, scope in _stanzas(text):
        tokens = header.split()
        kind = tokens[0] if tokens else ""
        bucket: str | None = None
        name: str | None = None
        record: dict[str, Any] | None = None
        if kind == "netdestination" and len(tokens) >= 2:
            name, bucket = tokens[1], "netdst"
            record = _parse_netdestination(name, body, warnings)
        elif kind == "netdestination6" and len(tokens) >= 2:
            name, bucket = tokens[1], "netdst"
            record = _parse_netdestination(name, body, warnings, ipv6=True)
        elif kind == "ip" and tokens[:3] == ["ip", "access-list", "session"] and len(tokens) >= 4:
            name, bucket = tokens[3], "acl_sess"
            record = _parse_acl_session(name, body, warnings)
        elif kind == "user-role" and len(tokens) >= 2:
            name, bucket = tokens[1], "role"
            record = _parse_user_role(name, body, warnings)
        else:
            # other stanza types (ip access-list eth, etc.) are out of scope here
            continue

        if scope is not None:
            scopes_seen.add(scope)
            if scope in drop_default_scopes:
                dropped_defaults += 1
                continue
            key = (bucket, name, scope)
            if key in seen:  # same object repeated across concatenated dumps
                continue
            seen.add(key)
            record["_source_scope"] = scope

        buckets[bucket].append(record)

    result: dict[str, Any] = {
        "netdst": buckets["netdst"],
        "acl_sess": buckets["acl_sess"],
        "role": buckets["role"],
        "_warnings": warnings,
    }
    if annotated:
        result["_provenance"] = {
            "scopes_seen": sorted(scopes_seen),
            "dropped_default_count": dropped_defaults,
        }
    return result


# --------------------------------------------------------------------------- #
# Stanza splitting
# --------------------------------------------------------------------------- #


def _stanzas(text: str) -> list[tuple[str, list[str], str | None]]:
    """Split CLI into ``(header, body-lines, source_scope)`` stanzas delimited by ``!``.

    A stanza header is a non-indented line; its body is the following indented
    lines up to the next ``!`` or non-indented line. ``source_scope`` is the
    authoring scope from the header's ``# inherited from``/``# local`` annotation
    (``None`` for plain, unannotated config). Provenance comments are stripped
    from every line before parsing, so the downstream ``_parse_*`` helpers never
    see them.
    """
    out: list[tuple[str, list[str], str | None]] = []
    header: str | None = None
    body: list[str] = []
    scope: str | None = None
    for raw in text.splitlines():
        clean, line_scope, _is_local = _strip_provenance(raw.rstrip())
        line = clean.rstrip()
        if not line.strip():
            continue
        if line.strip() == "!":
            if header is not None:
                out.append((header, body, scope))
            header, body, scope = None, [], None
            continue
        if line[0].isspace():  # indented → body line
            if header is not None:
                body.append(line.strip())
        else:  # non-indented → new header
            if header is not None:
                out.append((header, body, scope))
            header, body, scope = line.strip(), [], line_scope
    if header is not None:
        out.append((header, body, scope))
    return out


# --------------------------------------------------------------------------- #
# netdestination
# --------------------------------------------------------------------------- #


def _parse_netdestination(name: str, body: list[str], warnings: list[str], *, ipv6: bool = False) -> dict[str, Any]:
    pfx = "netdst6" if ipv6 else "netdst"
    entries: list[dict[str, Any]] = []
    record: dict[str, Any] = {"dstname": name}
    for line in body:
        t = line.split()
        if not t:
            continue
        kw = t[0]
        if kw == "host" and len(t) >= 2:
            entries.append({"_objname": f"{pfx}__host", "address": t[1]})
        elif kw == "network" and len(t) >= 3:
            entries.append({"_objname": f"{pfx}__network", "address": t[1], "netmask": t[2]})
        elif kw == "network" and len(t) == 2:
            # IPv6 / CIDR form: ``network <prefix>/<len>`` (single token).
            entries.append({"_objname": f"{pfx}__network", "address": t[1]})
        elif kw == "invert":
            record["invert"] = True
        elif kw == "name" and len(t) >= 2:
            entries.append({"_objname": f"{pfx}__name", "host_name": t[1]})
        elif kw == "range" and len(t) >= 3:
            # The net_group preprocessing maps host/network/name only — range
            # has no Central items[] mapping yet. Emit a typed entry so the gap
            # is visible rather than silently dropped.
            entries.append({"_objname": f"{pfx}__range", "start": t[1], "end": t[2]})
            warnings.append(
                f"netdestination {name!r}: 'range {t[1]} {t[2]}' has no engine "
                "mapping (net_group handles host/network/name)"
            )
        elif kw == "description":
            record["description"] = line.split(" ", 1)[1] if " " in line else ""
        else:
            warnings.append(f"netdestination {name!r}: unparsed line {line!r}")
    record[f"{pfx}__entry"] = entries
    return record


# --------------------------------------------------------------------------- #
# user-role
# --------------------------------------------------------------------------- #


def _parse_user_role(name: str, body: list[str], warnings: list[str]) -> dict[str, Any]:
    record: dict[str, Any] = {"rname": name}
    acls: list[dict[str, Any]] = []
    for line in body:
        t = line.split()
        if not t:
            continue
        if t[:2] == ["access-list", "session"] and len(t) >= 3:
            acls.append({"acl_type": "session", "pname": t[2]})
        elif t[0] == "vlan" and len(t) >= 2:
            record["role__vlan"] = {"vlanstr": t[1]}
        elif t[0] == "max-sessions" and len(t) >= 2:
            record["role__max_sess"] = {"max_sess": int(t[1])} if t[1].isdigit() else {"max_sess": t[1]}
        elif t[0] == "captive-portal" and len(t) >= 2 and t[0] != "no":
            record["role__cp"] = {"cp_profile_name": t[1]}
        elif t[0] == "reauthentication-interval" and len(t) >= 2:
            record["role__reauth"] = {"reauthperiod": int(t[1])} if t[1].isdigit() else {"reauthperiod": t[1]}
        elif t[0] in ("bw-contract", "no", "dialer", "pool", "vpn-ip-pool", "via"):
            # known-but-unmodelled role attributes — note, don't fail
            warnings.append(f"user-role {name!r}: unmodelled clause {line!r}")
        else:
            warnings.append(f"user-role {name!r}: unparsed line {line!r}")
    if acls:
        record["role__acl"] = acls
    return record


# --------------------------------------------------------------------------- #
# ip access-list session
# --------------------------------------------------------------------------- #


def _parse_acl_session(name: str, body: list[str], warnings: list[str]) -> dict[str, Any]:
    v4: list[dict[str, Any]] = []
    v6: list[dict[str, Any]] = []
    for line in body:
        t = line.split()
        if not t:
            continue
        is_v6 = t[0] == "ipv6"
        if is_v6:
            t = t[1:]
        rule = _parse_acl_rule(t, name, line, warnings)
        if rule is None:
            continue
        (v6 if is_v6 else v4).append(rule)
    return {"accname": name, "acl_sess__v4policy": v4, "acl_sess__v6policy": v6}


def _consume_address(t: list[str], i: int, side: str) -> tuple[dict[str, Any], int] | None:
    """Consume a source/dest address spec starting at token index ``i``.

    ``side`` is ``"s"`` (source) or ``"d"`` (destination). Returns the fields to
    merge into the rule plus the next token index, or ``None`` if unrecognised.
    """
    disc = "src" if side == "s" else "dst"
    kw = t[i]
    if kw == "any":
        return {disc: f"{side}any"}, i + 1
    if kw == "user":
        return {disc: f"{side}user"}, i + 1
    if kw == "localip":
        return {disc: f"{side}localip"}, i + 1
    if kw == "host" and i + 1 < len(t):
        return {disc: f"{side}host", ("sipaddr" if side == "s" else "dipaddr"): t[i + 1]}, i + 2
    if kw == "network" and i + 1 < len(t):
        addr_f = "snetaddr" if side == "s" else "dnetaddr"
        mask_f = "snetmask" if side == "s" else "dnetmask"
        nxt = t[i + 1]
        if "/" in nxt:
            # IPv6 / CIDR single-token prefix: ``network fc00::/7``. Split into
            # bare address + prefix length so the engine builds ``addr/len``.
            addr, _, plen = nxt.partition("/")
            return {disc: f"{side}network", addr_f: addr, mask_f: plen}, i + 2
        if i + 2 < len(t):
            return {disc: f"{side}network", addr_f: nxt, mask_f: t[i + 2]}, i + 3
        return None
    if kw == "alias" and i + 1 < len(t):
        return {disc: f"{side}alias", ("srcalias" if side == "s" else "dstalias"): t[i + 1]}, i + 2
    if kw in ("user-role", "userrole") and i + 1 < len(t):
        # AOS 8 CLI emits the bare ``userrole <name>`` form (no hyphen) in
        # effective config; accept both spellings.
        return {disc: f"{side}userrole", ("surname" if side == "s" else "durname"): t[i + 1]}, i + 2
    return None


def _parse_acl_rule(t: list[str], acl: str, line: str, warnings: list[str]) -> dict[str, Any] | None:
    """Parse one session-ACL rule's tokens (after any leading ``ipv6``)."""
    rule: dict[str, Any] = {"service_app": "service"}
    i = 0
    src = _consume_address(t, i, "s")
    if src is None:
        warnings.append(f"acl {acl!r}: unparsed source in {line!r}")
        return {"_unparsed": line}
    rule.update(src[0])
    i = src[1]
    dst = _consume_address(t, i, "d")
    if dst is None:
        warnings.append(f"acl {acl!r}: unparsed destination in {line!r}")
        return {"_unparsed": line}
    rule.update(dst[0])
    i = dst[1]

    # Split the remainder into service-tokens / action / options at the first
    # recognised action keyword.
    rest = t[i:]
    action_idx = next((k for k, tok in enumerate(rest) if tok in _ACTIONS), None)
    if action_idx is None:
        warnings.append(f"acl {acl!r}: no action keyword in {line!r}")
        return {"_unparsed": line}
    svc_tokens = rest[:action_idx]
    action = rest[action_idx]
    opts = rest[action_idx + 1 :]

    _apply_service(rule, svc_tokens, acl, line, warnings)
    rule["action"] = _ACTIONS[action]
    _apply_action_args(rule, action, opts)
    if "log" in opts:
        rule["log"] = True
    if "send-deny-response" in opts:
        # Maps to the engine's ``action.send-deny-response`` (API field
        # ``app-send-deny-response``); common on WebCC deny rules.
        rule["app-send-deny-response"] = True
    return rule


def _apply_service(rule: dict[str, Any], svc: list[str], acl: str, line: str, warnings: list[str]) -> None:
    if not svc or svc == ["any"]:
        rule["svc"] = "service-any"
        return
    head = svc[0]
    if head in ("tcp", "udp", "tcp-udp"):
        rule["svc"] = "tcp_udp" if head == "tcp-udp" else head
        rule["proto"] = head
        ports = [x for x in svc[1:] if x.isdigit()]
        if ports:
            rule["port1"] = int(ports[0])
            if len(ports) > 1:
                rule["port2"] = int(ports[1])
        return
    if head == "icmp":
        rule["svc"] = "icmp"
        return
    if head.isdigit():  # raw protocol number
        rule["svc"] = "proto"
        rule["proto"] = head
        return
    # DPI app / WebCC rules. The CLI tokens and the value FIELD differ per type —
    # these field names are the ones the REST API emits and the policy
    # translation reads (live-verified on 8.13): app/app-category use ``appname``,
    # web-cc-category uses ``webcccatgname``, web-cc-reputation uses ``web_rep2``.
    # Emitting the wrong field (e.g. ``appname`` for a category) silently degrades
    # the rule to RULE_ANY downstream — see issue #426.
    if head in ("app", "app-category", "appcategory", "web-cc-category", "web-cc-reputation") and len(svc) >= 2:
        rule["service_app"] = "app_opt"
        value = svc[1]
        if head == "app":
            rule["app_web_type"] = "app"
            rule["appname"] = value
        elif head in ("app-category", "appcategory"):
            rule["app_web_type"] = "app_cat"
            rule["appname"] = value
        elif head == "web-cc-category":
            rule["app_web_type"] = "web_cat"
            rule["webcccatgname"] = value
        else:  # web-cc-reputation
            rule["app_web_type"] = "web_cc_rep"
            rule["web_rep2"] = value
        return
    # named service object (svc-*, or a user service name)
    rule["svc"] = "service-name"
    rule["service-name"] = head
    if len(svc) > 1:
        warnings.append(f"acl {acl!r}: extra service tokens {svc[1:]} in {line!r}")


def _apply_action_args(rule: dict[str, Any], action: str, opts: list[str]) -> None:
    if action == "dst-nat":
        nums = [o for o in opts if o.isdigit()]
        if nums:
            rule["dnatport"] = int(nums[0])
        # Optional explicit NAT target IP: ``dst-nat <ip> <port>`` (OSU configs
        # use the port-only form; capture the IP form too for completeness).
        ips = [o for o in opts if not o.isdigit() and ("." in o or ":" in o)]
        if ips:
            rule["dnataddr"] = ips[0]
    elif action == "dual-nat":
        # Form: ``dual-nat pool <pool-name> <port>``.
        if "pool" in opts:
            j = opts.index("pool")
            if j + 1 < len(opts):
                rule["dualnatpool"] = opts[j + 1]
        nums = [o for o in opts if o.isdigit()]
        if nums:
            rule["dualnatport"] = int(nums[0])
    elif action == "redirect":
        if "tunnel-group" in opts:
            j = opts.index("tunnel-group")
            rule["re_dir"] = "tunnel-group"
            if j + 1 < len(opts):
                rule["tungrpname"] = opts[j + 1]
        elif "tunnel" in opts:
            j = opts.index("tunnel")
            rule["re_dir"] = "tunnel"
            if j + 1 < len(opts) and opts[j + 1].isdigit():
                rule["tunid"] = int(opts[j + 1])
