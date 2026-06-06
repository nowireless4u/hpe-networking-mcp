"""Unit tests for the AOS 8 CLI → canonical-record parser.

Exercises ``parse_aos8_cli`` against small, synthetic AOS 8 CLI snippets and
asserts the parsed record shapes (netdestination / session-ACL / user-role),
the warning channel for clauses that aren't fully modelled, and the parser →
translation-engine integration path for a dual-nat session-ACL rule.

All snippets use GENERIC placeholder names only (corp-servers, BRANCH-1,
cp-portal, example.com, employee, guest, 10.0.0.0/24, fc00::/7) — never
real-customer data.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.aos8.cli_parser import parse_aos8_cli
from hpe_networking_mcp.translations.engine import emit_calls
from hpe_networking_mcp.translations.loader import load_translations

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# netdestination
# --------------------------------------------------------------------------- #


def test_netdestination_host_network_name() -> None:
    """host / network (dotted-quad mask) / name(FQDN) entries parse correctly."""
    res = parse_aos8_cli(
        "netdestination corp-servers\n  host 10.0.0.5\n  network 10.0.0.0 255.255.255.0\n  name example.com\n!\n"
    )
    assert len(res["netdst"]) == 1
    rec = res["netdst"][0]
    assert rec["dstname"] == "corp-servers"
    entries = rec["netdst__entry"]
    assert entries[0] == {"_objname": "netdst__host", "address": "10.0.0.5"}
    assert entries[1] == {
        "_objname": "netdst__network",
        "address": "10.0.0.0",
        "netmask": "255.255.255.0",
    }
    assert entries[2] == {"_objname": "netdst__name", "host_name": "example.com"}
    # Well-formed lines produce no warnings.
    assert res["_warnings"] == []


def test_netdestination6_ipv6_network() -> None:
    """netdestination6 with a single-token IPv6 CIDR keeps the prefix intact."""
    res = parse_aos8_cli("netdestination6 v6-net\n  network fc00::/7\n!\n")
    rec = res["netdst"][0]
    assert rec["dstname"] == "v6-net"
    # IPv6 / CIDR form keeps the prefix in one token (no separate netmask).
    assert rec["netdst6__entry"] == [{"_objname": "netdst6__network", "address": "fc00::/7"}]


def test_netdestination_invert_clause() -> None:
    """An ``invert`` clause sets the record-level invert flag."""
    res = parse_aos8_cli("netdestination corp-servers\n  invert\n  host 10.0.0.5\n!\n")
    rec = res["netdst"][0]
    assert rec["invert"] is True


def test_netdestination_range_warns() -> None:
    """A ``range`` line is captured as a typed entry AND warns (no engine map)."""
    res = parse_aos8_cli("netdestination corp-servers\n  range 10.0.0.10 10.0.0.20\n!\n")
    rec = res["netdst"][0]
    assert rec["netdst__entry"] == [{"_objname": "netdst__range", "start": "10.0.0.10", "end": "10.0.0.20"}]
    assert any("range 10.0.0.10 10.0.0.20" in w for w in res["_warnings"])


# --------------------------------------------------------------------------- #
# ip access-list session
# --------------------------------------------------------------------------- #


def _only_rule(cli: str) -> dict:
    """Parse a single-rule ACL snippet and return that v4 rule."""
    res = parse_aos8_cli(cli)
    assert len(res["acl_sess"]) == 1
    rules = res["acl_sess"][0]["acl_sess__v4policy"]
    assert len(rules) == 1
    return rules[0]


def test_acl_any_any_any_permit() -> None:
    """``any any any permit`` → src/dst any, service-any, permit."""
    rule = _only_rule("ip access-list session corp-acl\n  any any any permit\n!\n")
    assert rule["src"] == "sany"
    assert rule["dst"] == "dany"
    assert rule["svc"] == "service-any"
    assert rule["action"] == "permit"
    assert "_unparsed" not in rule


def test_acl_user_network_tcp_port_deny_log() -> None:
    """``user network ... tcp 443 deny log`` parses proto/port/action/log."""
    rule = _only_rule("ip access-list session corp-acl\n  user network 10.0.0.0 255.255.255.0 tcp 443 deny log\n!\n")
    assert rule["src"] == "suser"
    assert rule["dst"] == "dnetwork"
    assert rule["dnetaddr"] == "10.0.0.0"
    assert rule["dnetmask"] == "255.255.255.0"
    assert rule["svc"] == "tcp"
    assert rule["proto"] == "tcp"
    assert rule["port1"] == 443
    assert rule["action"] == "deny"
    assert rule["log"] is True


def test_acl_user_alias_named_service_permit() -> None:
    """``user alias corp-servers svc-https permit`` → dalias + named service."""
    rule = _only_rule("ip access-list session corp-acl\n  user alias corp-servers svc-https permit\n!\n")
    assert rule["src"] == "suser"
    assert rule["dst"] == "dalias"
    assert rule["dstalias"] == "corp-servers"
    assert rule["svc"] == "service-name"
    assert rule["service-name"] == "svc-https"
    assert rule["action"] == "permit"


def test_acl_any_any_named_service_src_nat() -> None:
    """``any any svc-icmp src-nat`` → both-any, named service, src-nat action."""
    rule = _only_rule("ip access-list session corp-acl\n  any any svc-icmp src-nat\n!\n")
    assert rule["src"] == "sany"
    assert rule["dst"] == "dany"
    assert rule["svc"] == "service-name"
    assert rule["service-name"] == "svc-icmp"
    assert rule["action"] == "src-nat"


def test_acl_user_any_dst_nat_port() -> None:
    """``user any svc-http dst-nat 8080`` captures the dst-nat port."""
    rule = _only_rule("ip access-list session corp-acl\n  user any svc-http dst-nat 8080\n!\n")
    assert rule["action"] == "dst-nat"
    assert rule["dnatport"] == 8080
    assert rule["service-name"] == "svc-http"


def test_acl_user_any_dual_nat_pool_port() -> None:
    """``user any svc-https dual-nat pool corp-pool 8081`` sets pool + port."""
    rule = _only_rule("ip access-list session corp-acl\n  user any svc-https dual-nat pool corp-pool 8081\n!\n")
    assert rule["action"] == "dual-nat"
    assert rule["dualnatpool"] == "corp-pool"
    assert rule["dualnatport"] == 8081


def test_acl_ipv6_rule_lands_in_v6policy() -> None:
    """An ``ipv6 ...`` rule is routed into the v6 policy array, not v4."""
    res = parse_aos8_cli("ip access-list session corp-acl\n  ipv6 user any icmpv6 deny\n!\n")
    acl = res["acl_sess"][0]
    assert acl["acl_sess__v4policy"] == []
    v6 = acl["acl_sess__v6policy"]
    assert len(v6) == 1
    rule = v6[0]
    assert rule["src"] == "suser"
    assert rule["dst"] == "dany"
    assert rule["action"] == "deny"
    # NOTE: the parser treats ``icmpv6`` as a named-service object (it only
    # special-cases the literal token ``icmp``), so it surfaces as a
    # service-name rather than an icmp service. See the test-suite docstring /
    # the agent report for the flagged behaviour.
    assert rule["svc"] == "service-name"
    assert rule["service-name"] == "icmpv6"


# --------------------------------------------------------------------------- #
# user-role
# --------------------------------------------------------------------------- #


def test_user_role_fields_and_acl_bindings() -> None:
    """user-role parses vlan / max-sessions / access-list session / captive-portal."""
    res = parse_aos8_cli(
        "user-role employee\n"
        "  vlan 100\n"
        "  max-sessions 10\n"
        "  access-list session corp-acl\n"
        "  access-list session guest-acl\n"
        "  captive-portal cp-portal\n"
        "!\n"
    )
    assert len(res["role"]) == 1
    rec = res["role"][0]
    assert rec["rname"] == "employee"
    assert rec["role__vlan"] == {"vlanstr": "100"}
    assert rec["role__max_sess"] == {"max_sess": 10}
    assert rec["role__cp"] == {"cp_profile_name": "cp-portal"}
    assert rec["role__acl"] == [
        {"acl_type": "session", "pname": "corp-acl"},
        {"acl_type": "session", "pname": "guest-acl"},
    ]
    assert res["_warnings"] == []


# --------------------------------------------------------------------------- #
# coverage / warnings
# --------------------------------------------------------------------------- #


def test_multi_stanza_counts_and_warning_capture() -> None:
    """A multi-object snippet parses to the right counts; unparseable lines warn."""
    res = parse_aos8_cli(
        "netdestination corp-servers\n"
        "  host 10.0.0.5\n"
        "  totally-bogus-clause xyz\n"  # unparseable line inside a known stanza
        "!\n"
        "netdestination6 v6-net\n"
        "  network fc00::/7\n"
        "!\n"
        "ip access-list session corp-acl\n"
        "  any any any permit\n"
        "  garbledsrc garbleddst something permit\n"  # unparseable rule
        "!\n"
        "user-role employee\n"
        "  vlan 100\n"
        "  access-list session corp-acl\n"
        "!\n"
    )
    # 2 netdst (corp-servers + v6-net), 1 acl, 1 role.
    assert len(res["netdst"]) == 2
    assert len(res["acl_sess"]) == 1
    assert len(res["role"]) == 1

    # Unparseable lines are surfaced in _warnings (never silently lost).
    assert any("totally-bogus-clause" in w for w in res["_warnings"])
    assert any("garbledsrc garbleddst" in w for w in res["_warnings"])

    # The unparseable ACL rule is captured under an _unparsed marker...
    v4 = res["acl_sess"][0]["acl_sess__v4policy"]
    unparsed = [r for r in v4 if "_unparsed" in r]
    assert len(unparsed) == 1
    assert unparsed[0]["_unparsed"] == "garbledsrc garbleddst something permit"

    # ...while the well-formed permit rule has NO _unparsed marker.
    well_formed = [r for r in v4 if "_unparsed" not in r]
    assert len(well_formed) == 1
    assert well_formed[0]["action"] == "permit"


def test_unrecognized_stanza_type_is_skipped() -> None:
    """A stanza whose header kind is out of scope is dropped (no crash)."""
    res = parse_aos8_cli("ip access-list eth some-eth-acl\n  permit any\n!\nuser-role employee\n  vlan 100\n!\n")
    # eth ACLs are out of scope — only the user-role survives.
    assert res["netdst"] == []
    assert res["acl_sess"] == []
    assert len(res["role"]) == 1
    assert res["role"][0]["rname"] == "employee"


# --------------------------------------------------------------------------- #
# integration: parser → central:policy translation engine
# --------------------------------------------------------------------------- #


def test_parsed_acl_feeds_central_policy_translation() -> None:
    """A parsed dual-nat ACL rule round-trips through the real central:policy engine."""
    cli = (
        "ip access-list session corp-acl\n"
        "  user any svc-https dual-nat pool corp-pool 8081\n"
        "!\n"
        "user-role employee\n"
        "  access-list session corp-acl\n"
        "!\n"
    )
    parsed = parse_aos8_cli(cli)
    acl_record = parsed["acl_sess"][0]
    role_records = parsed["role"]

    translation = load_translations()["central:policy"]
    calls = emit_calls(
        translation,
        acl_record,
        "aos8",
        runtime_values={"central_scope_id": "scope-abc", "role_records": role_records},
    )

    assert calls, "expected at least one target call from the policy translation"
    body = calls[0].body
    assert body is not None
    assert body["name"] == "corp-acl"

    policy_rules = body["security-policy"]["policy-rule"]
    assert len(policy_rules) == 1
    action = policy_rules[0]["action"]
    assert action["type"] == "ACTION_DUAL_NAT"
    # The parser-derived dualnatpool / dualnatport land in Central's dual-nat sub-shape.
    assert action["dual-nat"] == {"nat-pool": "corp-pool", "port": 8081}

    # The role that bound the ACL drives the policy-rule source role-list,
    # proving the parsed role record flowed through role_attribution.
    assert policy_rules[0]["condition"]["source"]["role-list"] == ["employee"]


# --------------------------------------------------------------------------- #
# Provenance (show configuration effective detail annotations)
# --------------------------------------------------------------------------- #

# Generic scope paths only — never a real customer hierarchy.
_ANNOTATED = """netdestination corp-servers              # inherited from [/md/HQ]
    host 10.0.0.10                       # inherited from [/md/HQ]
!
netdestination6 ipv6-reserved-range      # inherited from [/]
    network 2000::/3                     # inherited from [/]
!
ip access-list session corp-acl          # local [/md/HQ/floor-1]
    user any svc-http permit             # local [/md/HQ/floor-1]
!
user-role employee                       # local [/md/HQ/floor-1]
    access-list session corp-acl         # local [/md/HQ/floor-1]
!"""


def test_provenance_tags_source_scope() -> None:
    """Annotated input tags each record with its authoring scope."""
    out = parse_aos8_cli(_ANNOTATED)
    assert [(d["dstname"], d.get("_source_scope")) for d in out["netdst"]] == [("corp-servers", "/md/HQ")]
    assert out["acl_sess"][0]["_source_scope"] == "/md/HQ/floor-1"
    assert out["role"][0]["_source_scope"] == "/md/HQ/floor-1"
    assert out["_provenance"]["scopes_seen"] == ["/", "/md/HQ", "/md/HQ/floor-1"]


def test_provenance_drops_system_default_scope() -> None:
    """Objects authored at the system root (``/``) are dropped as defaults."""
    out = parse_aos8_cli(_ANNOTATED)
    names = [d["dstname"] for d in out["netdst"]]
    assert "ipv6-reserved-range" not in names  # authored at [/]
    assert out["_provenance"]["dropped_default_count"] == 1


def test_provenance_keep_all_override() -> None:
    """``drop_default_scopes=()`` keeps even system-default objects."""
    out = parse_aos8_cli(_ANNOTATED, drop_default_scopes=())
    names = {d["dstname"] for d in out["netdst"]}
    assert names == {"corp-servers", "ipv6-reserved-range"}


def test_provenance_dedupes_repeated_object_across_dumps() -> None:
    """The same (object, scope) repeated across concatenated dumps appears once."""
    out = parse_aos8_cli(_ANNOTATED + "\n" + _ANNOTATED)
    assert sum(1 for d in out["netdst"] if d["dstname"] == "corp-servers") == 1


def test_plain_config_unannotated_has_no_provenance() -> None:
    """Plain ``show running-config`` (no annotations) is unchanged — no scope keys."""
    plain = "netdestination corp-servers\n    host 10.0.0.10\n!"
    out = parse_aos8_cli(plain)
    assert "_provenance" not in out
    assert "_source_scope" not in out["netdst"][0]


# --------------------------------------------------------------------------- #
# Rule grammar — DPI app / WebCC / userrole / send-deny-response
# --------------------------------------------------------------------------- #

# These emit the field names the REST API uses and the policy translation reads
# (live-verified). Emitting the wrong field silently degrades the rule to
# RULE_ANY downstream — see issue #426.


def _first_rule(cfg: str) -> dict:
    return parse_aos8_cli(cfg)["acl_sess"][0]["acl_sess__v4policy"][0]


def test_web_cc_category_emits_api_field_names() -> None:
    rule = _first_rule("ip access-list session p\n    user any web-cc-category malware-sites deny\n!")
    assert rule["service_app"] == "app_opt"
    assert rule["app_web_type"] == "web_cat"
    assert rule["webcccatgname"] == "malware-sites"
    assert "appname" not in rule  # NOT the generic app field (that was the bug)


def test_web_cc_reputation_and_send_deny_response() -> None:
    rule = _first_rule("ip access-list session p\n    any any web-cc-reputation high-risk deny send-deny-response\n!")
    assert rule["app_web_type"] == "web_cc_rep"
    assert rule["web_rep2"] == "high-risk"
    assert rule["app-send-deny-response"] is True


def test_app_and_app_category_tokens() -> None:
    rules = parse_aos8_cli(
        "ip access-list session p\n    user any app youtube permit\n    user any app-category streaming-media permit\n!"
    )["acl_sess"][0]["acl_sess__v4policy"]
    assert (rules[0]["app_web_type"], rules[0]["appname"]) == ("app", "youtube")
    assert (rules[1]["app_web_type"], rules[1]["appname"]) == ("app_cat", "streaming-media")


def test_userrole_source_and_dest_bare_token() -> None:
    """The bare ``userrole <name>`` form (no hyphen) parses on both sides."""
    rule = _first_rule("ip access-list session p\n    userrole staff userrole guest any deny\n!")
    assert rule["src"] == "suserrole" and rule["surname"] == "staff"
    assert rule["dst"] == "duserrole" and rule["durname"] == "guest"


def test_grammar_forms_produce_no_warnings() -> None:
    cfg = (
        "ip access-list session p\n"
        "    user any web-cc-category malware-sites deny\n"
        "    userrole staff any app youtube deny\n!"
    )
    assert parse_aos8_cli(cfg)["_warnings"] == []
