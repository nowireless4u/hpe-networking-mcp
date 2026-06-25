"""Golden tests for the AOS 8 → Central canonical config translations.

One representative case per kind asserting the emitted Central call shape
(paths / profile-types / key body fields), plus the policy defect-fix behaviors
(#420 policy-group registration, fail-closed unmapped action, validuser
interface association). These are the lasting regression tests for the canonical
engine; the legacy-parity gate lives in ``test_translations_legacy_parity.py``.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations import orchestrator as o

pytestmark = pytest.mark.unit

_SCOPE = "S1"


def _plan(kind, record, reader_ctx=None, device_functions=None):
    wc = {"scope_id": _SCOPE}
    if device_functions:
        wc["device_functions"] = device_functions
    return o.plan("aos8", "central", kind, record, reader_ctx=reader_ctx or {}, writer_ctx=wc)


def _paths(plan):
    return [c["path"] for c in plan.calls]


def _assignment(plan):
    return next(c for c in plan.calls if c["path"].endswith("/config-assignments"))


def test_vlan_id_create_and_assign():
    plan = _plan(o.VLAN_ID, {"id": 108})
    assert plan.calls[0]["path"].endswith("/layer2-vlan/108")
    assert plan.calls[0]["body"] == {"vlan": "108"}
    entry = _assignment(plan)["body"]["config-assignment"]
    # VLANs assign to both gateway + AP.
    assert {e["device-function"] for e in entry} == {"MOBILITY_GW", "CAMPUS_AP"}
    assert all(e["profile-type"] == "layer2-vlan" and e["scope-id"] == _SCOPE for e in entry)


def test_vlan_id_optional_subfields():
    plan = _plan(o.VLAN_ID, {"id": 104, "option-82": True, "vlan_id__descr": {"descr": "Corp"}})
    body = plan.calls[0]["body"]
    assert body["option-82"] is True
    assert body["description"] == "Corp"


def test_named_vlan_six_step_chain():
    plan = _plan(o.NAMED_VLAN, {"name": "iot", "vlan-ids": "108-110"})
    paths = _paths(plan)
    # ranges expand to discrete layer2-vlan creates (108/109/110) + alias + named-vlan
    assert sum(1 for p in paths if "/layer2-vlan/" in p) == 3
    assert any(p.endswith("/aliases/iot") for p in paths)
    assert any(p.endswith("/named-vlan/iot") for p in paths)
    # last calls are the LOCAL alias overrides carrying the real range string
    local = [c for c in plan.calls if c["path"].endswith("/aliases/iot") and c["query"].get("object-type") == "LOCAL"]
    assert local and local[0]["body"]["default-value"]["vlan-value"]["vlan-id-ranges"] == ["108-110"]


def test_net_group_items_and_family():
    rec = {
        "dstname": "corp",
        "netdst__entry": [
            {"address": "10.0.0.5", "_objname": "netdst__host"},
            {"address": "192.168.0.0", "netmask": "255.255.255.0", "_objname": "netdst__network"},
            {"host_name": "cppm.example.com", "_objname": "netdst__name"},
        ],
        "invert": True,
    }
    plan = _plan(o.NET_GROUP, rec)
    body = plan.calls[0]["body"]
    assert body["netdestination-type"] == "IPV4_ONLY"
    assert body["invert"] is True
    types = [i["type"] for i in body["items"]]
    assert types == ["HOST", "NETWORK", "FQDN"]
    assert body["items"][1]["prefix"] == "192.168.0.0/24"


def test_role_groups_and_bw_contracts():
    rec = {
        "rname": "parent",
        "role__vlan": {"vlanstr": "internal"},
        "role__enforce_dhcp": {},
        "role__bwc": [{"dir_type": "downstream", "name": "c1"}],
    }
    plan = _plan(o.ROLE, rec)
    body = plan.calls[0]["body"]
    assert body["access-vlan-name"] == "internal"
    assert body["vlan-type"] == "VLAN_NAME"
    assert body["miscellaneous-parameters"]["enforce-dhcp"] is True
    assert body["aaa-bw-contract"]["bw-contract"] == [{"bwc-name": "c1", "direction": "DOWNSTREAM"}]
    # role assigns to gateway only
    assert {e["device-function"] for e in _assignment(plan)["body"]["config-assignment"]} == {"MOBILITY_GW"}


def test_auth_server_radius_with_coa():
    rec = {"rad_server_name": "RAD1", "rad_host": {"host": "10.1.1.1"}, "rad_key": {"key": "s"}}
    plan = _plan(o.AUTH_SERVER, rec, reader_ctx={"coa_servers": [{"rfc3576_server": "10.1.1.1"}]})
    body = plan.calls[0]["body"]
    assert plan.calls[0]["path"].endswith("/auth-servers/RAD1")
    assert body["type"] == "RADIUS"
    assert body["radius-server-mode"] == "AUTH_AND_COA"
    assert body["dynamic-authorization-enable"] is True
    assert body["shared-secret-config"]["plaintext-value"] == "s"


def test_server_group_ordered_members():
    rec = {"sg_name": "SG", "auth_server": [{"name": "a"}, {"name": "b"}]}
    plan = _plan(o.SERVER_GROUP, rec)
    body = plan.calls[0]["body"]
    assert body["type"] == "RADIUS"
    assert body["servers"] == [{"server-name": "a", "position": 1}, {"server-name": "b", "position": 2}]


def test_captive_portal_inverted_https_and_enum():
    rec = {
        "profile-name": "guest",
        "cp_proto_http": {},
        "authentication_method": {"captive_auth_t": "MSCHAPv2"},
        "cp_white_list": [{"white-list": "a.com"}],
    }
    plan = _plan(o.CAPTIVE_PORTAL, rec)
    body = plan.calls[0]["body"]
    assert body["use-https"] is False
    assert body["auth-protocol"] == "MSCHAPv2"
    assert body["allow-list"] == ["a.com"]


def test_aaa_profile_nested_blocks():
    rec = {
        "profile-name": "corp-aaa",
        "dot1x_auth_profile": {"profile-name": "d1"},
        "default_user_role": {"role": "logon"},
        "rfc3576_client": [{"rfc3576_server": "10.1.1.1"}],
    }
    plan = _plan(o.AAA_PROFILE, rec)
    body = plan.calls[0]["body"]
    assert body["authentication"]["dot1x-auth"] == "d1"
    assert body["authorization"]["pre-auth-role"] == "logon"
    assert body["rfc3576-server-list"] == ["10.1.1.1"]


def test_dot1x_and_mac_auth_paths():
    d = _plan(o.DOT1X_AUTH, {"profile-name": "d1", "reauthentication": {}})
    assert d.calls[0]["path"].endswith("/dot1xauth/d1")
    assert d.calls[0]["body"]["reauth-enable"] is True
    m = _plan(o.MAC_AUTH, {"profile-name": "m1", "mba_case": {"mba_case_t": "upper"}})
    assert m.calls[0]["path"].endswith("/macauth/m1")
    assert m.calls[0]["body"]["case-type"] == "upper"


def test_gateway_cluster_ha_only_vs_intent():
    rec = {"profile-name": "East", "cluster_controller": [{"ip": "10.0.0.1", "vrrp_ip": "10.0.0.9", "prio": 128}]}
    ha = _plan(o.GATEWAY_CLUSTER, rec, reader_ctx={"cluster_strategy": "ha_only"})
    assert len(ha.calls) == 1
    assert ha.calls[0]["path"].endswith("/gateway-clusters/East")
    assert ha.calls[0]["query"]["object-type"] == "LOCAL"
    assert ha.calls[0]["body"]["ipv4-gateways"][0] == {"ip": "10.0.0.1", "coa-vrrp-ip": "10.0.0.9", "priority": 128}
    intent = _plan(o.GATEWAY_CLUSTER, rec, reader_ctx={"cluster_strategy": "intent_manual"})
    assert len(intent.calls) == 2
    assert intent.calls[1]["path"].endswith("/gw-cluster-intent-config/East")
    assert intent.calls[1]["body"]["cluster-mode"] == "CM_MANUAL"


def test_gateway_cluster_requires_strategy():
    with pytest.raises(ValueError, match="cluster_strategy"):
        _plan(o.GATEWAY_CLUSTER, {"profile-name": "East"})


# --- policy + the approved defect fixes ---------------------------------------


def _policy(acl, roles):
    return _plan(o.POLICY, acl, reader_ctx={"role_records": roles})


def test_policy_420_policy_group_registration():
    plan = _policy({"accname": "p1", "acl_sess__v4policy": [{"src": "sany", "dst": "dany", "action": "permit"}]}, [])
    paths = _paths(plan)
    assert paths[0].endswith("/policies/p1")
    assert paths[1].endswith("/policy-groups/policy-group/policy-group-list/p1")
    assert plan.calls[1]["body"] == {"name": "p1", "position": 1}
    assert paths[2].endswith("/config-assignments")


def test_policy_any_any_expands_with_role_attribution():
    roles = [{"rname": "emp", "role__acl": [{"acl_type": "session", "pname": "p1"}]}]
    plan = _policy({"accname": "p1", "acl_sess__v4policy": [{"src": "sany", "dst": "dany", "action": "permit"}]}, roles)
    rules = plan.calls[0]["body"]["security-policy"]["policy-rule"]
    assert len(rules) == 2  # role->any AND any->role
    assert rules[0]["condition"]["source"] == {"type": "ADDRESS_ROLE", "role-list": ["emp"]}
    assert rules[1]["condition"]["destination"] == {"type": "ADDRESS_ROLE", "role-list": ["emp"]}


def test_policy_unmapped_action_fails_closed():
    plan = _policy({"accname": "p1", "acl_sess__v4policy": [{"src": "sany", "dst": "dany", "action": "bogus"}]}, [])
    rule = plan.calls[0]["body"]["security-policy"]["policy-rule"][0]
    assert rule["action"]["type"] == "ACTION_DENY"  # never silent ACTION_ALLOW
    assert plan.canonical.unmapped_actions == ["bogus"]
    assert any(u["kind"] == "policy_action" for u in plan.unresolved)


def test_policy_validuser_interface_association():
    plan = _policy(
        {"accname": "validuser", "acl_sess__v4policy": [{"src": "sany", "dst": "dany", "action": "permit"}]}, []
    )
    assert plan.calls[0]["body"]["association"] == "ASSOCIATION_INTERFACE"


def test_policy_port_range_vs_single():
    roles: list[dict] = []
    single = _policy(
        {
            "accname": "p1",
            "acl_sess__v4policy": [
                {
                    "src": "sany",
                    "dst": "dany",
                    "svc": "tcp",
                    "service_app": "service",
                    "proto": "tcp",
                    "port1": 443,
                    "action": "permit",
                }
            ],
        },
        roles,
    )
    tf = single.calls[0]["body"]["security-policy"]["policy-rule"][0]["condition"]["transport-fields"]
    assert tf["destination-port"] == {"operator": "COMPARISON_EQ", "min": 443}
    rng = _policy(
        {
            "accname": "p2",
            "acl_sess__v4policy": [
                {
                    "src": "sany",
                    "dst": "dany",
                    "svc": "tcp",
                    "service_app": "service",
                    "proto": "tcp",
                    "port1": 1000,
                    "port2": 2000,
                    "action": "permit",
                }
            ],
        },
        roles,
    )
    tf2 = rng.calls[0]["body"]["security-policy"]["policy-rule"][0]["condition"]["transport-fields"]
    assert tf2["destination-port"] == {"operator": "COMPARISON_RANGE", "min": 1000, "max": 2000}


def test_policy_alias_design_a():
    plan = _policy(
        {
            "accname": "p1",
            "acl_sess__v4policy": [{"src": "sany", "dst": "dalias", "dstalias": "cppm", "action": "permit"}],
        },
        [],
    )
    dst = plan.calls[0]["body"]["security-policy"]["policy-rule"][0]["condition"]["destination"]
    assert dst == {"type": "ADDRESS_ALIAS", "net-group": "cppm"}
