"""Engine tests — emit_calls produces the right ordered target API calls.

Coverage: take the shipped Central named-VLAN translation, feed it a
realistic AOS 8 vlan_name_id source dict + Central-shaped runtime_values,
and assert the engine produces exactly the 6-step sequence we hand-validated
against the live tenant.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.engine import EngineError, emit_calls
from hpe_networking_mcp.translations.loader import load_translations

pytestmark = pytest.mark.unit


@pytest.fixture
def translations() -> dict:
    return load_translations()


@pytest.fixture
def named_vlan(translations: dict):
    return translations["central:named_vlan"]


@pytest.fixture
def vlan_id(translations: dict):
    return translations["central:vlan_id"]


@pytest.fixture
def role(translations: dict):
    return translations["central:role"]


def _runtime(scope_id: str = "SCOPE", device_functions: list[str] | None = None) -> dict:
    """Helper: build Central-shaped runtime_values for the named-VLAN translation."""
    rv: dict = {"central_scope_id": scope_id}
    if device_functions is not None:
        rv["device_functions"] = device_functions
    return rv


# --------------------------------------------------------------------------- #
# Core: end-to-end emit
# --------------------------------------------------------------------------- #


def test_named_vlan_with_single_vlan_id_emits_expected_calls(named_vlan) -> None:
    """Source: vlan_name_id record {name: 'user', vlan-ids: '107'}.

    Expected fan-out:
    * step 1 (per_vlan_id_in_binding × 1 ID) = 1
    * step 2 (once) = 1
    * step 3 (once) = 1
    * step 4 (per_vlan_id × 1 ID, body_template multi-DF) = 1
    * step 5 (once, body_template multi-DF) = 1
    * step 6 (per_device_function × 2 DFs) = 2
    Total = 7
    """
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan, source, "aos8", runtime_values=_runtime())
    assert len(calls) == 7
    assert [c.step for c in calls] == [1, 2, 3, 4, 5, 6, 6]


def test_step1_layer2_vlan_create(named_vlan) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan, source, "aos8", runtime_values=_runtime())
    step1 = [c for c in calls if c.step == 1][0]
    assert step1.method == "POST"
    assert step1.endpoint == "/network-config/v1alpha1/layer2-vlan/107"
    assert step1.body == {"vlan": "107"}


def test_step2_alias_create_with_placeholder(named_vlan) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan, source, "aos8", runtime_values=_runtime())
    step2 = [c for c in calls if c.step == 2][0]
    assert step2.endpoint == "/network-config/v1alpha1/aliases/user"
    assert step2.body == {
        "name": "user",
        "type": "ALIAS_VLAN",
        "default-value": {"vlan-value": {"vlan-id-ranges": ["1"]}},
    }


def test_step3_named_vlan_references_alias(named_vlan) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan, source, "aos8", runtime_values=_runtime())
    step3 = [c for c in calls if c.step == 3][0]
    assert step3.endpoint == "/network-config/v1alpha1/named-vlan/user"
    assert step3.body == {"name": "user", "vlan": {"vlan-alias": "user"}}


def test_step4_assign_layer2_vlan_packs_both_device_functions(named_vlan) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan, source, "aos8", runtime_values=_runtime("SCOPE-A"))
    step4 = [c for c in calls if c.step == 4][0]
    assert step4.endpoint == "/network-config/v1alpha1/config-assignments"
    items = (step4.body or {})["config-assignment"]
    assert len(items) == 2
    assert {item["device-function"] for item in items} == {"MOBILITY_GW", "CAMPUS_AP"}
    assert all(item["scope-id"] == "SCOPE-A" for item in items)
    assert all(item["profile-type"] == "layer2-vlan" for item in items)
    assert all(item["profile-instance"] == "107" for item in items)


def test_step5_assign_named_vlan_packs_both_device_functions(named_vlan) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan, source, "aos8", runtime_values=_runtime("SCOPE-B"))
    step5 = [c for c in calls if c.step == 5][0]
    items = (step5.body or {})["config-assignment"]
    assert len(items) == 2
    assert all(item["profile-type"] == "named-vlan" for item in items)
    assert all(item["profile-instance"] == "user" for item in items)
    assert all(item["scope-id"] == "SCOPE-B" for item in items)


def test_step6_local_alias_override_per_device_function(named_vlan) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan, source, "aos8", runtime_values=_runtime("SCOPE-C"))
    step6 = [c for c in calls if c.step == 6]
    assert len(step6) == 2
    dfs_seen = set()
    for c in step6:
        assert c.endpoint == "/network-config/v1alpha1/aliases/user"
        assert c.query_params["object-type"] == "LOCAL"
        assert c.query_params["scope-id"] == "SCOPE-C"
        dfs_seen.add(c.query_params["device-function"])
        assert c.body == {
            "name": "user",
            "type": "ALIAS_VLAN",
            "default-value": {"vlan-value": {"vlan-id-ranges": ["107"]}},
        }
    assert dfs_seen == {"MOBILITY_GW", "CAMPUS_AP"}


# --------------------------------------------------------------------------- #
# Iteration patterns
# --------------------------------------------------------------------------- #


def test_csv_vlan_ids_expand_to_multiple_layer2_calls(named_vlan) -> None:
    source = {"name": "local", "vlan-ids": "104,160"}
    calls = emit_calls(named_vlan, source, "aos8", runtime_values=_runtime())
    step1_calls = [c for c in calls if c.step == 1]
    assert len(step1_calls) == 2
    assert {c.endpoint for c in step1_calls} == {
        "/network-config/v1alpha1/layer2-vlan/104",
        "/network-config/v1alpha1/layer2-vlan/160",
    }


def test_range_vlan_ids_expand_for_layer2_but_preserve_for_alias_override(named_vlan) -> None:
    """Asymmetric transform: layer2-vlan iterates 108,109,110; alias override gets ['108-110']."""
    source = {"name": "iot", "vlan-ids": "108-110"}
    calls = emit_calls(named_vlan, source, "aos8", runtime_values=_runtime())

    step1_calls = [c for c in calls if c.step == 1]
    assert len(step1_calls) == 3
    assert {c.endpoint for c in step1_calls} == {
        "/network-config/v1alpha1/layer2-vlan/108",
        "/network-config/v1alpha1/layer2-vlan/109",
        "/network-config/v1alpha1/layer2-vlan/110",
    }

    step4_calls = [c for c in calls if c.step == 4]
    assert len(step4_calls) == 3
    for c in step4_calls:
        items = (c.body or {})["config-assignment"]
        assert len(items) == 2
        assert {item["device-function"] for item in items} == {"MOBILITY_GW", "CAMPUS_AP"}

    step6_calls = [c for c in calls if c.step == 6]
    assert len(step6_calls) == 2
    for c in step6_calls:
        assert (c.body or {})["default-value"]["vlan-value"]["vlan-id-ranges"] == ["108-110"]


def test_runtime_device_functions_override_target_meta(named_vlan) -> None:
    """Caller can restrict device functions via runtime_values."""
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(
        named_vlan,
        source,
        "aos8",
        runtime_values=_runtime("SCOPE", device_functions=["MOBILITY_GW"]),
    )
    # Step 6 (per-device-function) goes from 2 calls to 1
    assert len([c for c in calls if c.step == 6]) == 1
    # Steps 4 and 5 (multi-DF arrays) go from 2-element to 1-element
    step4 = [c for c in calls if c.step == 4][0]
    assert len((step4.body or {})["config-assignment"]) == 1


def test_alias_name_override_takes_precedence(named_vlan) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(
        named_vlan,
        source,
        "aos8",
        runtime_values=_runtime(),
        overrides={"alias_name": "USR-ALIAS-CUSTOM"},
    )
    step2 = [c for c in calls if c.step == 2][0]
    assert step2.endpoint == "/network-config/v1alpha1/aliases/USR-ALIAS-CUSTOM"
    step3 = [c for c in calls if c.step == 3][0]
    assert step3.body == {"name": "user", "vlan": {"vlan-alias": "USR-ALIAS-CUSTOM"}}


# --------------------------------------------------------------------------- #
# Error paths
# --------------------------------------------------------------------------- #


def test_unknown_source_platform_raises(named_vlan) -> None:
    with pytest.raises(EngineError, match="does not declare source 'cisco_ios'"):
        emit_calls(named_vlan, {}, "cisco_ios", runtime_values=_runtime())


def test_missing_required_runtime_value_raises(named_vlan) -> None:
    """Translation declares central_scope_id required; engine validates."""
    with pytest.raises(EngineError, match="central_scope_id"):
        emit_calls(named_vlan, {"name": "user", "vlan-ids": "107"}, "aos8", runtime_values={})


def test_missing_source_field_raises_when_used(named_vlan) -> None:
    """If source data lacks a key the emit needs, surface a clear error."""
    source = {"name": "user"}  # vlan-ids missing
    with pytest.raises(EngineError, match="vlan_ids"):
        emit_calls(named_vlan, source, "aos8", runtime_values=_runtime())


# --------------------------------------------------------------------------- #
# central:vlan_id — bare and rich AOS 8 vlan_id records
# --------------------------------------------------------------------------- #


def test_vlan_id_bare_record_emits_two_calls(vlan_id) -> None:
    """Bare vlan_id source {id: 108}: step 1 body has only 'vlan'; step 2 multi-DF."""
    source = {"id": 108}
    calls = emit_calls(vlan_id, source, "aos8", runtime_values=_runtime("SCOPE-A"))
    assert len(calls) == 2
    assert [c.step for c in calls] == [1, 2]

    step1 = calls[0]
    assert step1.method == "POST"
    assert step1.endpoint == "/network-config/v1alpha1/layer2-vlan/108"
    # Optional fields absent → keys dropped from body
    assert step1.body == {"vlan": "108"}


def test_vlan_id_bare_record_step2_assigns_to_all_device_functions(vlan_id) -> None:
    source = {"id": 108}
    calls = emit_calls(vlan_id, source, "aos8", runtime_values=_runtime("SCOPE-A"))
    step2 = calls[1]
    assert step2.endpoint == "/network-config/v1alpha1/config-assignments"
    items = (step2.body or {})["config-assignment"]
    assert len(items) == 2
    assert {item["device-function"] for item in items} == {"MOBILITY_GW", "CAMPUS_AP"}
    assert all(item["profile-type"] == "layer2-vlan" for item in items)
    assert all(item["profile-instance"] == "108" for item in items)
    assert all(item["scope-id"] == "SCOPE-A" for item in items)


def test_vlan_id_rich_record_includes_all_subproperties(vlan_id) -> None:
    """Rich record with description / option-82 / wired-aaa-profile fills the body."""
    source = {
        "id": 104,
        "option-82": True,
        "vlan_id__aaa": {"profile-name": "corp-aaa"},
        "vlan_id__descr": {"descr": "Corp VLAN"},
    }
    calls = emit_calls(vlan_id, source, "aos8", runtime_values=_runtime())
    step1 = calls[0]
    assert step1.body == {
        "vlan": "104",
        "description": "Corp VLAN",
        "option-82": True,
        "wired-aaa-profile": "corp-aaa",
    }


def test_vlan_id_partial_rich_record_only_description(vlan_id) -> None:
    """Only description present: option-82 + wired-aaa-profile keys drop out."""
    source = {"id": 200, "vlan_id__descr": {"descr": "Mgmt"}}
    calls = emit_calls(vlan_id, source, "aos8", runtime_values=_runtime())
    step1 = calls[0]
    assert step1.body == {"vlan": "200", "description": "Mgmt"}


def test_vlan_id_partial_rich_record_only_option82(vlan_id) -> None:
    """Only option-82 present: description + wired-aaa-profile keys drop out."""
    source = {"id": 200, "option-82": True}
    calls = emit_calls(vlan_id, source, "aos8", runtime_values=_runtime())
    step1 = calls[0]
    assert step1.body == {"vlan": "200", "option-82": True}


def test_vlan_id_option82_false_is_preserved(vlan_id) -> None:
    """option-82=false should appear in the body — only None drops keys, not falsy."""
    source = {"id": 200, "option-82": False}
    calls = emit_calls(vlan_id, source, "aos8", runtime_values=_runtime())
    step1 = calls[0]
    assert step1.body == {"vlan": "200", "option-82": False}


def test_vlan_id_runtime_device_functions_override(vlan_id) -> None:
    """Caller can restrict device functions via runtime_values for the multi-DF step."""
    source = {"id": 108}
    calls = emit_calls(
        vlan_id,
        source,
        "aos8",
        runtime_values=_runtime(device_functions=["MOBILITY_GW"]),
    )
    step2 = calls[1]
    items = (step2.body or {})["config-assignment"]
    assert len(items) == 1
    assert items[0]["device-function"] == "MOBILITY_GW"


def test_vlan_id_missing_required_id_raises(vlan_id) -> None:
    """Without 'id' the engine can't build the path — surface clear error."""
    with pytest.raises(EngineError, match="vlan_id"):
        emit_calls(vlan_id, {}, "aos8", runtime_values=_runtime())


# --------------------------------------------------------------------------- #
# central:role — Gateway-targeted, sourced from live AOS 8 captures
# --------------------------------------------------------------------------- #


def _role_runtime(scope_id: str = "SCOPE") -> dict:
    """Helper: role translation defaults to MOBILITY_GW only (no AP)."""
    return {"central_scope_id": scope_id}


def test_role_minimum_record_emits_two_calls(role) -> None:
    """Source with just rname: step 1 body has only 'name'; nested groups drop entirely."""
    source = {"rname": "minimal-role"}
    calls = emit_calls(role, source, "aos8", runtime_values=_role_runtime("SCOPE-A"))
    assert len(calls) == 2
    assert [c.step for c in calls] == [1, 2]
    step1 = calls[0]
    assert step1.method == "POST"
    assert step1.endpoint == "/network-config/v1alpha1/roles/minimal-role"
    assert step1.body == {"name": "minimal-role"}


def test_role_with_named_vlan_emits_root_access_vlan_name(role) -> None:
    """Per Central role schema, GW VLAN binding is at the ROOT (not vlan-parameters)."""
    source = {"rname": "camera_role_ubt", "role__vlan": {"vlanstr": "internal"}}
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {
        "name": "camera_role_ubt",
        "access-vlan-name": "internal",
        "vlan-type": "VLAN_NAME",
    }


def test_role_with_numeric_vlan_emits_root_access_vlan_id(role) -> None:
    source = {"rname": "data-role", "role__vlan": {"vlanstr": "104"}}
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {"name": "data-role", "access-vlan-id": 104, "vlan-type": "VLAN_ID"}


def test_role_pattern_b_flags_render_as_true(role) -> None:
    """Empty-dict source flags (live shape on configured 'parent' role) -> body bool true.

    Source: role__enforce_dhcp/role__robust_age_out/role__reg_role/role__dpi_disable/
    role__disable_webcc surface as {} when configured. Single-underscore variants
    (role_disable_ipclassify / role_enable_youtubeedu) too. role__openflow is
    deliberately omitted to confirm it doesn't appear in the body.
    """
    source = {
        "rname": "parent",
        "role__enforce_dhcp": {},
        "role__robust_age_out": {},
        "role__reg_role": {},
        "role__dpi_disable": {},
        "role__disable_webcc": {},
        "role_disable_ipclassify": {},
        "role_enable_youtubeedu": {},
    }
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {
        "name": "parent",
        "miscellaneous-parameters": {
            "enforce-dhcp": True,
            "robust-age-out": True,
            "registration-role": True,
        },
        "classification-parameters": {
            "ip-classification": True,
            "dpi-classification": True,
            "dpi-youtube-education": True,
            "web-cc": True,
        },
    }
    assert "openflow-enable" not in body["miscellaneous-parameters"]


def test_role_pattern_a_flags_render_as_true(role) -> None:
    """Pattern-A flags ({_present: true} live shape on system defaults) also -> True."""
    source = {
        "rname": "logon-role",
        "role__cp_acc": {"_present": True, "_flags": {"default": True}},
        "role__openflow": {"_present": True, "_flags": {"default": True}},
    }
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {
        "name": "logon-role",
        "session-parameters": {"check-for-accounting": True},
        "miscellaneous-parameters": {"openflow-enable": True},
    }


def test_role_reauth_minutes_routes_to_minutes_field(role) -> None:
    source = {"rname": "r1", "role__reauth": {"reauthperiod": 30}}
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {"name": "r1", "session-parameters": {"reauthentication-interval": 30}}


def test_role_reauth_seconds_routes_to_seconds_field(role) -> None:
    """Live shape from configured 'parent' role: {seconds: true, reauthperiod: 3600}."""
    source = {"rname": "parent", "role__reauth": {"seconds": True, "reauthperiod": 3600}}
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {
        "name": "parent",
        "session-parameters": {"reauthentication-interval-seconds": 3600},
    }


def test_role_captive_portal_lands_in_session_parameters(role) -> None:
    source = {"rname": "onguard-role", "role__cp": {"cp_profile_name": "onguard-captive-portal"}}
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {
        "name": "onguard-role",
        "session-parameters": {"captive-portal": "onguard-captive-portal"},
    }


def test_role_max_sessions_lands_in_session_parameters(role) -> None:
    source = {"rname": "r", "role__max_sess": {"max_sess": 1024}}
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {"name": "r", "session-parameters": {"max-sessions": 1024}}


def test_role_full_rich_record_renders_all_three_groups(role) -> None:
    """Reproduce the live 'parent' role at /md/Campus/West (full Tier 1 + reauth-seconds)."""
    source = {
        "rname": "parent",
        "role__vlan": {"vlanstr": "104"},
        "role__cp_acc": {"_present": True},
        "role__openflow": {"_present": True},
        "role__reauth": {"seconds": True, "reauthperiod": 3600},
        "role__max_sess": {"max_sess": 65535},
        "role__enforce_dhcp": {},
        "role__robust_age_out": {},
        "role__reg_role": {},
        "role__dpi_disable": {},
        "role__disable_webcc": {},
        "role_disable_ipclassify": {},
        "role_enable_youtubeedu": {},
    }
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {
        "name": "parent",
        "access-vlan-id": 104,
        "vlan-type": "VLAN_ID",
        "session-parameters": {
            "check-for-accounting": True,
            "max-sessions": 65535,
            "reauthentication-interval-seconds": 3600,
        },
        "miscellaneous-parameters": {
            "enforce-dhcp": True,
            "robust-age-out": True,
            "registration-role": True,
            "openflow-enable": True,
        },
        "classification-parameters": {
            "ip-classification": True,
            "dpi-classification": True,
            "dpi-youtube-education": True,
            "web-cc": True,
        },
    }


def test_role_does_not_emit_policies_field(role) -> None:
    """Critical inversion: AOS 8 role.role__acl is NOT mapped to body 'policies'.

    Central back-fills role.policies[] from policy-side references; sending
    policies[] would either be rejected or silently overwritten.
    """
    source = {
        "rname": "guest-postauth-role",
        "role__acl": [
            {"acl_type": "session", "pname": "ra-guard"},
            {"acl_type": "session", "pname": "guest-postauth"},
        ],
    }
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {"name": "guest-postauth-role"}
    assert "policies" not in body


def test_role_step2_assigns_only_to_mobility_gw_by_default(role) -> None:
    """target_meta declares MOBILITY_GW only — no CAMPUS_AP."""
    source = {"rname": "demo"}
    step2 = emit_calls(role, source, "aos8", runtime_values=_role_runtime("SCOPE-A"))[1]
    items = (step2.body or {})["config-assignment"]
    assert len(items) == 1
    assert items[0]["device-function"] == "MOBILITY_GW"
    assert items[0]["profile-type"] == "role"
    assert items[0]["profile-instance"] == "demo"


def test_role_missing_required_rname_raises(role) -> None:
    with pytest.raises(EngineError, match="name"):
        emit_calls(role, {}, "aos8", runtime_values=_role_runtime())


def test_role_empty_nested_groups_drop_when_no_subfields_set(role) -> None:
    """Confirm session-parameters / miscellaneous-parameters / classification-parameters
    drop entirely when the source has no fields targeting them.
    """
    body = emit_calls(role, {"rname": "bare"}, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert "session-parameters" not in body
    assert "miscellaneous-parameters" not in body
    assert "classification-parameters" not in body


# --------------------------------------------------------------------------- #
# central:role — bandwidth-contract sub-shapes
# --------------------------------------------------------------------------- #


def test_role_bwc_basic_lands_in_aaa_bw_contract(role) -> None:
    """Source from 'blacklisted' role: role__bwc=[{dir_type, name}]."""
    source = {
        "rname": "blacklisted",
        "role__bwc": [
            {"dir_type": "downstream", "name": "blacklisteddownstreamper-roleui"},
            {"dir_type": "upstream", "name": "blacklistedupstreamper-roleui"},
        ],
    }
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {
        "name": "blacklisted",
        "aaa-bw-contract": {
            "bw-contract": [
                {"bwc-name": "blacklisteddownstreamper-roleui", "direction": "DOWNSTREAM"},
                {"bwc-name": "blacklistedupstreamper-roleui", "direction": "UPSTREAM"},
            ]
        },
    }


def test_role_bwc_app_array_fans_out_to_app_and_appcategory_groups(role) -> None:
    """Live shape: role__bwc_app mixes app + appcategory; the engine fans out
    via paired filter transforms to two distinct Central body fields.
    """
    source = {
        "rname": "parent",
        "role__bwc_app": [
            {"app_type": "app", "dir": "downstream", "appname": "youtube", "name": "parentyoutubedownstream"},
            {"app_type": "app", "dir": "upstream", "appname": "youtube", "name": "parentyoutubeupstream"},
            {
                "app_type": "appcategory",
                "dir": "downstream",
                "appname": "streaming",
                "name": "parentstreamingdownstream",
            },
            {
                "app_type": "appcategory",
                "dir": "upstream",
                "appname": "streaming",
                "name": "parentstreamingupstream",
            },
        ],
    }
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {
        "name": "parent",
        "app-aaa-contract": {
            "app": [
                {"appname": "youtube", "bwc-name": "parentyoutubedownstream", "direction": "DOWNSTREAM"},
                {"appname": "youtube", "bwc-name": "parentyoutubeupstream", "direction": "UPSTREAM"},
            ]
        },
        "app-category-aaa-contract": {
            "app-category": [
                {"category-name": "STREAMING", "bwc-name": "parentstreamingdownstream", "direction": "DOWNSTREAM"},
                {"category-name": "STREAMING", "bwc-name": "parentstreamingupstream", "direction": "UPSTREAM"},
            ]
        },
    }


def test_role_bwc_web_array_fans_out_to_category_and_reputation_groups(role) -> None:
    """Live shape: role__bwc_web mixes web-cc-category + web-cc-reputation."""
    source = {
        "rname": "parent",
        "role__bwc_web": [
            {
                "webcccatgname": "streaming/media",
                "web_opt": "web-cc-category",
                "dir": "downstream",
                "name": "parent-streaming-down",
            },
            {
                "webcccatgname": "streaming/media",
                "web_opt": "web-cc-category",
                "dir": "upstream",
                "name": "parent-streaming-up",
            },
            {
                "web_rep": "trustworthy",
                "web_opt": "web-cc-reputation",
                "dir": "downstream",
                "name": "parent-trustworthy-down",
            },
            {
                "web_rep": "trustworthy",
                "web_opt": "web-cc-reputation",
                "dir": "upstream",
                "name": "parent-trustworthy-up",
            },
        ],
    }
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {
        "name": "parent",
        "web-category-aaa-contract": {
            "web-category": [
                {
                    "webcategory-name": "STREAMING-MEDIA",
                    "bwc-name": "parent-streaming-down",
                    "direction": "DOWNSTREAM",
                },
                {
                    "webcategory-name": "STREAMING-MEDIA",
                    "bwc-name": "parent-streaming-up",
                    "direction": "UPSTREAM",
                },
            ]
        },
        "web-reputation-aaa-contract": {
            "web-reputation": [
                {"webrepname": "TRUSTWORTHY", "bwc-name": "parent-trustworthy-down", "direction": "DOWNSTREAM"},
                {"webrepname": "TRUSTWORTHY", "bwc-name": "parent-trustworthy-up", "direction": "UPSTREAM"},
            ]
        },
    }


def test_role_no_bwc_configured_drops_all_bw_contract_keys(role) -> None:
    """Confirm a role without any bw-contract source doesn't produce empty
    aaa-bw-contract / app-aaa-contract / etc. groups.
    """
    body = emit_calls(role, {"rname": "no-bwc"}, "aos8", runtime_values=_role_runtime())[0].body or {}
    for key in (
        "aaa-bw-contract",
        "app-aaa-contract",
        "app-category-aaa-contract",
        "web-category-aaa-contract",
        "web-reputation-aaa-contract",
    ):
        assert key not in body
