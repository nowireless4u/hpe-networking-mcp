"""TRANSITIONAL cutover gate: canonical engine == legacy ``emit_calls`` output.

Asserts the new reader/writer engine emits the same Central calls as the legacy
JSON ``emit_calls`` engine for representative AOS 8 records across every migrated
kind — the gate that lets the old engine be retired with confidence. Comparison
is on (method, path, query, body); ``depends_on`` differs by representation
(step-numbers vs call-indices) and is excluded.

Policy is compared MODULO the two approved defect fixes: the new engine adds a
#420 policy-group-list registration the old engine never emitted (stripped here),
and fail-closes unmapped actions (not exercised — all parity records use mapped
actions). ``test_translations_aos8_config_kinds.py`` pins the fixed behavior.

DELETE this file together with the legacy engine (engine.py / loader.py / the
targets JSON) — it is the only remaining ``emit_calls`` importer in the tests.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations import orchestrator as o
from hpe_networking_mcp.translations.engine import emit_calls
from hpe_networking_mcp.translations.loader import load_translations

pytestmark = pytest.mark.unit

_T = load_translations()
_RT = {"central_scope_id": "S1"}


def _norm(path: str) -> str:
    return path.lstrip("/")


def _old(tid: str, rec: dict, rt: dict) -> list[tuple]:
    calls = emit_calls(translation=_T[tid], source_data=rec, source_platform_id="aos8", runtime_values=rt)
    return [(c.method, _norm(c.endpoint), c.query_params or {}, c.body) for c in calls]


def _new(kind: str, rec: dict, reader_ctx: dict | None, *, strip_policy_group: bool = False) -> list[tuple]:
    plan = o.plan("aos8", "central", kind, rec, reader_ctx=reader_ctx or {}, writer_ctx={"scope_id": "S1"})
    out = []
    for c in plan.calls:
        path = _norm(c["path"])
        if strip_policy_group and "/policy-groups/" in path:
            continue
        out.append((c["method"], path, c.get("query") or {}, c.get("body")))
    return out


@pytest.mark.parametrize(
    ("tid", "kind", "rec", "rt", "reader_ctx"),
    [
        ("central:vlan_id", o.VLAN_ID, {"id": 108}, _RT, None),
        (
            "central:vlan_id",
            o.VLAN_ID,
            {"id": 104, "option-82": True, "vlan_id__aaa": {"profile-name": "a"}, "vlan_id__descr": {"descr": "C"}},
            _RT,
            None,
        ),
        ("central:named_vlan", o.NAMED_VLAN, {"name": "user", "vlan-ids": "107"}, _RT, None),
        ("central:named_vlan", o.NAMED_VLAN, {"name": "iot", "vlan-ids": "108-110"}, _RT, None),
        ("central:named_vlan", o.NAMED_VLAN, {"name": "local", "vlan-ids": "104,160"}, _RT, None),
        (
            "central:net_group",
            o.NET_GROUP,
            {
                "dstname": "cppm",
                "netdst__entry": [
                    {"address": "10.0.0.5", "_objname": "netdst__host"},
                    {"address": "14.0.0.0", "netmask": "255.0.0.0", "_objname": "netdst__network"},
                    {"host_name": "x.example.com", "_objname": "netdst__name"},
                ],
                "invert": True,
            },
            _RT,
            None,
        ),
        ("central:role", o.ROLE, {"rname": "camera", "role__vlan": {"vlanstr": "internal"}}, _RT, None),
        (
            "central:role",
            o.ROLE,
            {
                "rname": "parent",
                "role__vlan": {"vlanstr": "104"},
                "role__cp": {"cp_profile_name": "cp"},
                "role__cp_acc": {"_present": True},
                "role__max_sess": {"max_sess": 65535},
                "role__reauth": {"seconds": True, "reauthperiod": 3600},
                "role__enforce_dhcp": {},
                "role_disable_ipclassify": {},
                "role__bwc": [{"dir_type": "downstream", "name": "c1"}],
                "role__bwc_app": [{"app_type": "app", "dir": "upstream", "appname": "youtube", "name": "a1"}],
                "role__bwc_web": [
                    {"web_opt": "web-cc-category", "dir": "up", "webcccatgname": "streaming/media", "name": "w1"}
                ],
                "role__bwc_ex": [{"app_type": "appcategory", "appname": "collaboration"}],
            },
            _RT,
            None,
        ),
        (
            "central:auth_server",
            o.AUTH_SERVER,
            {
                "rad_server_name": "R1",
                "rad_host": {"host": "10.1.1.1"},
                "rad_key": {"key": "s"},
                "rad_authport": {"authport": 1812},
            },
            _RT,
            None,
        ),
        (
            "central:auth_server",
            o.AUTH_SERVER,
            {"rad_server_name": "R1", "rad_host": {"host": "10.1.1.1"}, "rad_key": {"key": "s"}},
            {**_RT, "coa_servers": [{"rfc3576_server": "10.1.1.1"}]},
            {"coa_servers": [{"rfc3576_server": "10.1.1.1"}]},
        ),
        (
            "central:auth_server",
            o.AUTH_SERVER,
            {
                "tacacs_server_name": "T1",
                "tacacs_host": {"host": "10.0.0.9"},
                "tacacs_key": {"key": "tk"},
                "tacacs_tcpport": {"tcp-port": 49},
            },
            _RT,
            None,
        ),
        (
            "central:server_group",
            o.SERVER_GROUP,
            {"sg_name": "SG", "auth_server": [{"name": "a"}, {"name": "b"}]},
            _RT,
            None,
        ),
        (
            "central:dot1x_auth",
            o.DOT1X_AUTH,
            {
                "profile-name": "d1",
                "reauth_period": {"ra-period": 86400},
                "reauthentication": {},
                "server_cert": {"server-cert-name": "sc"},
            },
            _RT,
            None,
        ),
        (
            "central:mac_auth",
            o.MAC_AUTH,
            {
                "profile-name": "m1",
                "mac_reauth_period": {"ra-period": 3600},
                "mba_case": {"mba_case_t": "upper"},
                "mac_reauthentication": {},
            },
            _RT,
            None,
        ),
        (
            "central:captive_portal",
            o.CAPTIVE_PORTAL,
            {
                "profile-name": "g",
                "cp_default_role": {"default-role": "guest"},
                "cp_min_delay": {"minimum-delay": 5},
                "allow_guest": {},
                "cp_proto_http": {},
                "authentication_method": {"captive_auth_t": "MSCHAPv2"},
                "cp_white_list": [{"white-list": "a.com"}],
            },
            _RT,
            None,
        ),
        (
            "central:aaa_profile",
            o.AAA_PROFILE,
            {
                "profile-name": "corp",
                "rad_acct_sg": {"server_group_name": "SG"},
                "enforce_dhcp": {},
                "dot1x_auth_profile": {"profile-name": "d1"},
                "default_user_role": {"role": "logon"},
                "rfc3576_client": [{"rfc3576_server": "10.1.1.1"}],
            },
            _RT,
            None,
        ),
    ],
)
def test_parity_simple_kinds(tid, kind, rec, rt, reader_ctx):
    assert _new(kind, rec, reader_ctx) == _old(tid, rec, rt)


@pytest.mark.parametrize("strategy", ["ha_only", "intent_site", "intent_manual"])
def test_parity_gateway_cluster(strategy):
    rec = {
        "profile-name": "East",
        "cluster_controller": [{"ip": "10.0.0.1", "vrrp_ip": "10.0.0.9", "prio": 128, "mcast_vlan": 200}],
        "heartbeat_threshold": {"heartbeat-threshold": 5},
    }
    rt = {**_RT, "cluster_strategy": strategy}
    assert _new(o.GATEWAY_CLUSTER, rec, {"cluster_strategy": strategy}) == _old("central:gateway_cluster", rec, rt)


def test_parity_policy_modulo_policy_group():
    roles = [{"rname": "emp", "role__acl": [{"acl_type": "session", "pname": "p1"}]}]
    acl = {
        "accname": "p1",
        "acl_sess__v4policy": [
            {"src": "sany", "dst": "dany", "action": "permit"},
            {
                "src": "shost",
                "sipaddr": "10.0.0.5",
                "dst": "dnetwork",
                "dnetaddr": "192.168.0.0",
                "dnetmask": "255.255.255.0",
                "svc": "tcp",
                "service_app": "service",
                "proto": "tcp",
                "port1": 443,
                "action": "permit",
                "log": True,
            },
            {
                "src": "suser",
                "dst": "dalias",
                "dstalias": "cppm",
                "service_app": "service",
                "svc": "service-name",
                "service-name": "svc-https",
                "action": "deny",
            },
            {
                "src": "sany",
                "dst": "dany",
                "service_app": "app_opt",
                "app_web_type": "app_cat",
                "appname": "streaming",
                "appaction": "appdeny",
            },
        ],
    }
    rt = {**_RT, "role_records": roles}
    new = _new(o.POLICY, acl, {"role_records": roles}, strip_policy_group=True)
    assert new == _old("central:policy", acl, rt)
