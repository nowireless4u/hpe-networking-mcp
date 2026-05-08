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
        "exclude-app-contract",
        "exclude-app-cat-contract",
    ):
        assert key not in body


def test_role_bwc_exclude_array_fans_out_to_app_and_appcategory_groups(role) -> None:
    """Live shape: role__bwc_ex=[{app_type, appname}] mixes app + appcategory.

    Source from 'parent' role at /md/Campus/West:
      [{"app_type": "app", "appname": "netflix"},
       {"app_type": "appcategory", "appname": "collaboration"}]
    """
    source = {
        "rname": "parent",
        "role__bwc_ex": [
            {"app_type": "app", "appname": "netflix"},
            {"app_type": "appcategory", "appname": "collaboration"},
        ],
    }
    body = emit_calls(role, source, "aos8", runtime_values=_role_runtime())[0].body or {}
    assert body == {
        "name": "parent",
        "exclude-app-contract": {"exclude-app": [{"exclude-app-name": "netflix"}]},
        "exclude-app-cat-contract": {"exclude-app-category": [{"exclude-app-category-name": "COLLABORATION"}]},
    }


# --------------------------------------------------------------------------- #
# Engine 2-arg transform support
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# Engine preprocessing dispatch
# --------------------------------------------------------------------------- #


def test_engine_invokes_preprocessing_before_key_mappings() -> None:
    """Translation declares preprocessing → engine resolves the dotted path,
    invokes the function with (source_data, runtime_values), and uses the
    returned augmented source for key_mappings.
    """
    import sys
    import types

    # Register a synthetic preprocessing function
    mod = types.ModuleType("__test_preproc_mod")

    def _preproc(source_data: dict, runtime_values: dict) -> dict:
        return {**source_data, "_augmented": f"hello-{runtime_values.get('multiplier', 1)}"}

    mod.preproc = _preproc  # type: ignore[attr-defined]
    sys.modules["__test_preproc_mod"] = mod

    try:
        from hpe_networking_mcp.translations.loader import Translation

        spec = {
            "version": 1,
            "target_platform": "central",
            "target_id": "preproc",
            "preprocessing": "__test_preproc_mod.preproc",
            "target_emits": [
                {
                    "step": 1,
                    "name": "test",
                    "purpose": "test",
                    "endpoint": "/test/{out}",
                    "method": "POST",
                    "iteration": "once",
                }
            ],
            "target_meta": {},
            "target_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
            "sources": {
                "aos8": {
                    "kind": "rest",
                    "mapping_kind": "simple",
                    "objects": [{"object": "x"}],
                    "key_mappings": {
                        "out": {"from": "_augmented", "to": "test", "transform": "direct"},
                    },
                }
            },
        }
        t = Translation.model_validate(spec)
        calls = emit_calls(t, {"input": "raw"}, "aos8", runtime_values={"multiplier": 42})
        # Preprocessing wrote {_augmented: "hello-42"}; key_mappings picked it up
        assert calls[0].endpoint == "/test/hello-42"
    finally:
        del sys.modules["__test_preproc_mod"]


def test_engine_preprocessing_is_optional() -> None:
    """Translations without preprocessing declared work as before — no engine change.

    All existing translations (named_vlan, vlan_id, role) don't declare
    preprocessing and should keep working. This is a smoke test.
    """
    translations = load_translations()
    # vlan_id has no preprocessing
    vid = translations["central:vlan_id"]
    assert vid.preprocessing is None
    # And it still emits cleanly
    calls = emit_calls(vid, {"id": 100}, "aos8", runtime_values={"central_scope_id": "S"})
    assert len(calls) == 2
    assert calls[0].body == {"vlan": "100"}


def test_engine_preprocessing_bad_path_raises_clear_error() -> None:
    """Malformed dotted path → EngineError with translation context."""
    from hpe_networking_mcp.translations.loader import Translation

    spec = {
        "version": 1,
        "target_platform": "central",
        "target_id": "bad_preproc",
        "preprocessing": "nonexistent",  # no dot — invalid path
        "target_emits": [
            {
                "step": 1,
                "name": "x",
                "purpose": "x",
                "endpoint": "/x",
                "method": "POST",
                "iteration": "once",
            }
        ],
        "target_meta": {},
        "target_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
        "sources": {"aos8": {"kind": "rest", "objects": [{"object": "x"}]}},
    }
    t = Translation.model_validate(spec)
    with pytest.raises(EngineError, match="dotted import path"):
        emit_calls(t, {}, "aos8")


def test_engine_preprocessing_missing_module_raises() -> None:
    """Preprocessing path points at a module that doesn't exist → EngineError."""
    from hpe_networking_mcp.translations.loader import Translation

    spec = {
        "version": 1,
        "target_platform": "central",
        "target_id": "missing_module",
        "preprocessing": "definitely.not.a.real.module.preproc",
        "target_emits": [
            {
                "step": 1,
                "name": "x",
                "purpose": "x",
                "endpoint": "/x",
                "method": "POST",
                "iteration": "once",
            }
        ],
        "target_meta": {},
        "target_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
        "sources": {"aos8": {"kind": "rest", "objects": [{"object": "x"}]}},
    }
    t = Translation.model_validate(spec)
    with pytest.raises(EngineError, match="couldn't import module"):
        emit_calls(t, {}, "aos8")


def test_engine_preprocessing_non_dict_return_raises() -> None:
    """Preprocessing function must return a dict; anything else is a clear error."""
    import sys
    import types

    mod = types.ModuleType("__test_bad_preproc")

    def _bad_preproc(source_data: dict, runtime_values: dict) -> list:
        return []  # type: ignore[return-value]

    mod.bad = _bad_preproc  # type: ignore[attr-defined]
    sys.modules["__test_bad_preproc"] = mod

    try:
        from hpe_networking_mcp.translations.loader import Translation

        spec = {
            "version": 1,
            "target_platform": "central",
            "target_id": "bad_return",
            "preprocessing": "__test_bad_preproc.bad",
            "target_emits": [
                {
                    "step": 1,
                    "name": "x",
                    "purpose": "x",
                    "endpoint": "/x",
                    "method": "POST",
                    "iteration": "once",
                }
            ],
            "target_meta": {},
            "target_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
            "sources": {"aos8": {"kind": "rest", "objects": [{"object": "x"}]}},
        }
        t = Translation.model_validate(spec)
        with pytest.raises(EngineError, match="returned list.*expected dict"):
            emit_calls(t, {}, "aos8")
    finally:
        del sys.modules["__test_bad_preproc"]


def test_engine_dispatches_2arg_transforms_with_ctx() -> None:
    """A registered transform with a 2-arg signature receives the engine's ctx
    (source_data + runtime_values) as its second positional argument.
    """
    from hpe_networking_mcp.translations.transforms import _REGISTRY  # noqa: PLC2701

    captured: dict = {}

    def _spy_transform(value, ctx):
        captured["value"] = value
        captured["ctx"] = ctx
        return f"saw:{value}"

    _REGISTRY["__test_2arg_spy"] = _spy_transform
    try:
        # Minimal translation that uses the spy
        from hpe_networking_mcp.translations.loader import Translation

        spec = {
            "version": 1,
            "target_platform": "central",
            "target_id": "spy",
            "target_emits": [
                {
                    "step": 1,
                    "name": "spy_emit",
                    "purpose": "test",
                    "endpoint": "/spy/{out}",
                    "method": "POST",
                    "iteration": "once",
                }
            ],
            "target_meta": {},
            "target_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
            "required_runtime_values": ["my_runtime_key"],
            "sources": {
                "aos8": {
                    "kind": "rest",
                    "mapping_kind": "simple",
                    "objects": [{"object": "x"}],
                    "key_mappings": {
                        "out": {"from": "input_field", "to": "spy", "transform": "__test_2arg_spy"},
                    },
                }
            },
        }
        t = Translation.model_validate(spec)
        emit_calls(
            t,
            {"input_field": "hello", "extra": "data"},
            "aos8",
            runtime_values={"my_runtime_key": "rt-value"},
        )
        assert captured["value"] == "hello"
        assert captured["ctx"]["source_data"] == {"input_field": "hello", "extra": "data"}
        assert captured["ctx"]["runtime_values"] == {"my_runtime_key": "rt-value"}
    finally:
        del _REGISTRY["__test_2arg_spy"]


def test_engine_still_dispatches_1arg_transforms_unchanged() -> None:
    """1-arg transforms (the existing convention) MUST NOT receive ctx.

    Adding 2-arg support shouldn't break the simpler signature; existing
    transforms continue to work as before.
    """
    from hpe_networking_mcp.translations.transforms import _REGISTRY  # noqa: PLC2701

    received_args: list = []

    def _legacy_transform(value):
        received_args.append(value)
        return value.upper()

    _REGISTRY["__test_1arg_legacy"] = _legacy_transform
    try:
        from hpe_networking_mcp.translations.loader import Translation

        spec = {
            "version": 1,
            "target_platform": "central",
            "target_id": "legacy",
            "target_emits": [
                {
                    "step": 1,
                    "name": "legacy_emit",
                    "purpose": "test",
                    "endpoint": "/legacy/{out}",
                    "method": "POST",
                    "iteration": "once",
                }
            ],
            "target_meta": {},
            "target_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
            "sources": {
                "aos8": {
                    "kind": "rest",
                    "mapping_kind": "simple",
                    "objects": [{"object": "x"}],
                    "key_mappings": {
                        "out": {"from": "field", "to": "spy", "transform": "__test_1arg_legacy"},
                    },
                }
            },
        }
        t = Translation.model_validate(spec)
        calls = emit_calls(t, {"field": "hello"}, "aos8")
        assert calls[0].endpoint == "/legacy/HELLO"
        assert received_args == ["hello"]
    finally:
        del _REGISTRY["__test_1arg_legacy"]


# --------------------------------------------------------------------------- #
# central:policy — AOS 8 acl_sess -> Central /policies translation
# --------------------------------------------------------------------------- #


@pytest.fixture
def policy(translations: dict):
    return translations["central:policy"]


def _policy_runtime(
    source: dict | None = None,
    scope_id: str = "SCOPE",
    role_attribution: list[str] | None = None,
) -> dict:
    """Build runtime_values for the central:policy translation.

    Constructs ``role_records`` containing one role per name in
    ``role_attribution`` (defaulting to ``['parent']``) where each role's
    ``role__acl[]`` references the ACL via ``source['accname']``. The
    preprocessing function will then compute role_attribution by reverse-
    indexing — so this helper exercises the full preprocessing path.

    If ``source`` is None the role_records list is empty (test the
    fallback where preprocessing finds no role attribution).
    """
    if role_attribution is None:
        role_attribution = ["parent"]
    accname = (source or {}).get("accname")
    role_records: list[dict] = []
    if accname:
        role_records = [
            {"rname": r, "role__acl": [{"acl_type": "session", "pname": accname}]} for r in role_attribution
        ]
    return {"central_scope_id": scope_id, "role_records": role_records}


def test_policy_minimum_acl_emits_two_calls(policy) -> None:
    """ACL with one any-any-any permit rule + role_attribution=['parent'] →
    POST /policies/parent + config-assignments.

    Note: AOS 8 'any any' on a role-bound ACL is BIDIRECTIONAL — Central
    represents this as TWO unidirectional rules (role->any AND any->role)
    so return traffic is matched. One AOS 8 rule expands to 2 Central rules.
    """
    source = {
        "accname": "parent",
        "acl_sess__v4policy": [
            {
                "sany": True,
                "src": "sany",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            }
        ],
        "acl_sess__v6policy": [],
    }
    calls = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source, "SCOPE-A"))
    assert len(calls) == 2
    assert [c.step for c in calls] == [1, 2]

    step1 = calls[0]
    assert step1.method == "POST"
    assert step1.endpoint == "/network-config/v1alpha1/policies/parent"
    assert step1.body == {
        "name": "parent",
        "type": "POLICY_TYPE_SECURITY",
        "association": "ASSOCIATION_ROLE",
        "security-policy": {
            "type": "SECURITY_POLICY_TYPE_DEFAULT",
            "policy-rule": [
                {
                    "position": 1,
                    "condition": {
                        "rule-type": "RULE_ANY",
                        "address-family": "IPV4",
                        "source": {"type": "ADDRESS_ROLE", "role-list": ["parent"]},
                        "destination": {"type": "ADDRESS_ANY"},
                    },
                    "action": {"type": "ACTION_ALLOW"},
                },
                {
                    "position": 2,
                    "condition": {
                        "rule-type": "RULE_ANY",
                        "address-family": "IPV4",
                        "source": {"type": "ADDRESS_ANY"},
                        "destination": {"type": "ADDRESS_ROLE", "role-list": ["parent"]},
                    },
                    "action": {"type": "ACTION_ALLOW"},
                },
            ],
        },
    }


def test_policy_suser_dst_uses_role_attribution(policy) -> None:
    """suser source + role_attribution=['parent','guest'] → ADDRESS_ROLE with role-list."""
    source = {
        "accname": "user-rule",
        "acl_sess__v4policy": [
            {
                "suser": True,
                "src": "suser",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            }
        ],
    }
    rt = _policy_runtime(source, role_attribution=["parent", "guest"])
    body = emit_calls(policy, source, "aos8", runtime_values=rt)[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["condition"]["source"] == {"type": "ADDRESS_ROLE", "role-list": ["parent", "guest"]}
    assert rule["condition"]["destination"] == {"type": "ADDRESS_ANY"}


def test_policy_dst_host_with_ip(policy) -> None:
    """dst=dhost + dipaddr=10.1.1.1 → ADDRESS_HOST with host-ipv4-address."""
    source = {
        "accname": "host-rule",
        "acl_sess__v4policy": [
            {
                "suser": True,
                "src": "suser",
                "dipaddr": "10.1.1.1",
                "dst": "dhost",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            }
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["condition"]["destination"] == {
        "type": "ADDRESS_HOST",
        "host-address": {"host-ipv4-address": "10.1.1.1"},
    }


def test_policy_dst_userrole_with_durname(policy) -> None:
    """dst=duserrole + durname='parent' → ADDRESS_ROLE with explicit role (not role-list)."""
    source = {
        "accname": "userrole-rule",
        "acl_sess__v4policy": [
            {
                "suser": True,
                "src": "suser",
                "durname": "parent",
                "dst": "duserrole",
                "appname": "youtube",
                "app_web_type": "app",
                "service_app": "app_opt",
                "appdeny": True,
                "appaction": "appdeny_opt",
            }
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["condition"]["destination"] == {"type": "ADDRESS_ROLE", "role": "parent"}
    assert rule["condition"]["services"] == {"application": "youtube"}
    assert rule["condition"]["rule-type"] == "RULE_APPLICATION"
    assert rule["action"]["type"] == "ACTION_DENY"


def test_policy_dst_localip(policy) -> None:
    source = {
        "accname": "local-rule",
        "acl_sess__v4policy": [
            {
                "suser": True,
                "src": "suser",
                "dlocalip": True,
                "dst": "dlocalip",
                "appname": "netflix",
                "app_web_type": "app",
                "service_app": "app_opt",
                "appdeny": True,
                "appaction": "appdeny_opt",
            }
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["condition"]["destination"] == {"type": "ADDRESS_LOCAL"}


def test_policy_named_service_svc_http_uses_central_net_service(policy) -> None:
    """svc-http (named service) → RULE_NET_SERVICE + services.net-service: 'svc-http'.

    Central ships a net-services catalog with svc-* names mirroring AOS 8's
    convention (svc-http, svc-https, svc-dns, svc-icmp, etc.). The translation
    references those by name rather than mapping to raw protocol+port —
    cleaner, uses Central's authoritative catalog, and lets unknown svc-*
    names produce a clean Central error instead of silent mistranslation.
    """
    source = {
        "accname": "http-rule",
        "acl_sess__v4policy": [
            {
                "suser": True,
                "src": "suser",
                "dany": True,
                "dst": "dany",
                "service-name": "svc-http",
                "svc": "service-name",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            }
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["condition"]["rule-type"] == "RULE_NET_SERVICE"
    assert rule["condition"]["services"] == {"net-service": "svc-http"}
    # No raw protocol/port for named-service rules — Central looks up the
    # net-service catalog entry instead
    assert "ip-header" not in rule["condition"]
    assert "transport-fields" not in rule["condition"]


def test_policy_icmp_echo_rule(policy) -> None:
    """svc=icmp + icmp_type=echo → RULE_PROTOCOL + ip-header.protocol=IP_ICMP + icmp.icmp-type=echo."""
    source = {
        "accname": "icmp-rule",
        "acl_sess__v4policy": [
            {
                "sany": True,
                "src": "sany",
                "dany": True,
                "dst": "dany",
                "echo": True,
                "icmp_type": "echo",
                "svc": "icmp",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            }
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["condition"]["rule-type"] == "RULE_PROTOCOL"
    assert rule["condition"]["ip-header"] == {"protocol": "IP_ICMP", "icmp": {"icmp-type": "echo"}}


def test_policy_dst_nat_action(policy) -> None:
    """action=dst-nat with dnatport=8080 → ACTION_DESTINATION_NAT + destination-nat.dest-port=8080."""
    source = {
        "accname": "dst-nat-rule",
        "acl_sess__v4policy": [
            {
                "suser": True,
                "src": "suser",
                "dany": True,
                "dst": "dany",
                "service-name": "svc-http",
                "svc": "service-name",
                "service_app": "service",
                "dnatport": 8080,
                "action": "dst-nat",
            }
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["action"] == {
        "type": "ACTION_DESTINATION_NAT",
        "destination-nat": {"dest-port": 8080},
    }


def test_policy_redirect_tunnel_group(policy) -> None:
    """action=redir_opt + re_dir=tunnel-group + tungrpname → ACTION_REDIRECT + redirect.tunnel-group."""
    source = {
        "accname": "redir-rule",
        "acl_sess__v4policy": [
            {
                "suser": True,
                "src": "suser",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "tungrpname": "test",
                "re_dir": "tunnel-group",
                "action": "redir_opt",
            }
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["action"] == {
        "type": "ACTION_REDIRECT",
        "redirect": {"tunnel-group": "test"},
    }


def test_policy_time_range_reference_lands_in_condition(policy) -> None:
    source = {
        "accname": "tr-rule",
        "acl_sess__v4policy": [
            {
                "sany": True,
                "src": "sany",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
                "trname": "business-hours",
            }
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["condition"]["time-range-name"] == "business-hours"


def test_policy_v6policy_tagged_address_family_ipv6(policy) -> None:
    """Rules from acl_sess__v6policy get address-family: IPV6.

    Each AOS 8 'any any' rule expands to 2 Central rules (bidirectional);
    one v4 any-any + one v6 any-any → 4 Central rules total. Positions are
    sequential across the merged v4+v6 array.
    """
    source = {
        "accname": "dual-stack",
        "acl_sess__v4policy": [
            {
                "sany": True,
                "src": "sany",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            },
        ],
        "acl_sess__v6policy": [
            {
                "sany": True,
                "src": "sany",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            },
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rules = body["security-policy"]["policy-rule"]
    # 1 v4 any-any (expands to 2) + 1 v6 any-any (expands to 2) = 4 rules
    assert len(rules) == 4
    # v4 first (rules 1-2), then v6 (rules 3-4)
    assert rules[0]["condition"]["address-family"] == "IPV4"
    assert rules[1]["condition"]["address-family"] == "IPV4"
    assert rules[2]["condition"]["address-family"] == "IPV6"
    assert rules[3]["condition"]["address-family"] == "IPV6"
    # Positions sequential across v4+v6
    assert [r["position"] for r in rules] == [1, 2, 3, 4]
    # Rules 1+3 are role->any (the "outbound" half of any-any)
    assert rules[0]["condition"]["source"]["type"] == "ADDRESS_ROLE"
    assert rules[0]["condition"]["destination"] == {"type": "ADDRESS_ANY"}
    # Rules 2+4 are any->role (the "inbound" half)
    assert rules[1]["condition"]["source"] == {"type": "ADDRESS_ANY"}
    assert rules[1]["condition"]["destination"]["type"] == "ADDRESS_ROLE"


def test_policy_inherited_rules_skipped(policy) -> None:
    """Defensive: rules with _flags.inherited=True are skipped by the transform."""
    source = {
        "accname": "with-inherited",
        "acl_sess__v4policy": [
            {
                "sany": True,
                "src": "sany",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
                "_flags": {"inherited": True},
            },  # should be skipped
            {
                "suser": True,
                "src": "suser",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            },  # should land
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rules = body["security-policy"]["policy-rule"]
    assert len(rules) == 1
    assert rules[0]["condition"]["source"] == {"type": "ADDRESS_ROLE", "role-list": ["parent"]}


def test_policy_step2_assigns_to_mobility_gw(policy) -> None:
    source = {
        "accname": "demo",
        "acl_sess__v4policy": [
            {
                "sany": True,
                "src": "sany",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            },
        ],
    }
    step2 = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source, "SCOPE-X"))[1]
    items = (step2.body or {})["config-assignment"]
    assert len(items) == 1
    assert items[0] == {
        "scope-id": "SCOPE-X",
        "device-function": "MOBILITY_GW",
        "profile-type": "policy",
        "profile-instance": "demo",
    }


def test_policy_missing_role_records_raises(policy) -> None:
    """role_records is required — engine should raise on missing.

    Per the standardized template, the consumer pre-fetches all role records
    once per migration run and passes via runtime_values. The preprocessing
    function reverse-indexes to compute role_attribution per ACL.
    """
    with pytest.raises(EngineError, match="role_records"):
        emit_calls(
            policy, {"accname": "test"}, "aos8", runtime_values={"central_scope_id": "SCOPE"}
        )  # missing role_records


def test_policy_empty_acl_emits_empty_policy_rule_list(policy) -> None:
    """ACL with empty rule arrays: preprocessing returns _central_rules=[];
    body lands as policy-rule: []. Per the LLD ('empty ACL not migrated'),
    consumer should typically filter empty ACLs from migration before
    calling emit_calls — this test exercises the defensive path.
    """
    source = {"accname": "empty", "acl_sess__v4policy": [], "acl_sess__v6policy": []}
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    assert body["security-policy"] == {"type": "SECURITY_POLICY_TYPE_DEFAULT", "policy-rule": []}


# --------------------------------------------------------------------------- #
# central:policy — "any any" rewrite rule (operator-confirmed)
# --------------------------------------------------------------------------- #


def test_policy_any_any_rule_replaces_source_with_role_attribution(policy) -> None:
    """AOS 8 'any any' rule on a role-bound ACL → Central 'role any' rewrite.

    Central can't represent any-any for a role-bound policy. The translation
    replaces the source (only) with role_attribution to produce 'role → any'
    (the Central-canonical equivalent).
    """
    source = {
        "accname": "any-any",
        "acl_sess__v4policy": [
            {
                "sany": True,
                "src": "sany",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            }
        ],
    }
    rt = _policy_runtime(source, role_attribution=["faculty", "staff"])
    body = emit_calls(policy, source, "aos8", runtime_values=rt)[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["condition"]["source"] == {"type": "ADDRESS_ROLE", "role-list": ["faculty", "staff"]}
    assert rule["condition"]["destination"] == {"type": "ADDRESS_ANY"}


def test_policy_any_specific_keeps_source_as_address_any(policy) -> None:
    """sany source + DESTINATION-specific (host/network/role) → keep source ADDRESS_ANY.

    Per Reading A: only the literal 'any-any' pattern gets rewritten. Rules
    where AOS 8 says 'any → specific-something' translate to Central
    'any → specific-something' since Central does support that pattern.
    """
    source = {
        "accname": "any-host",
        "acl_sess__v4policy": [
            {
                "sany": True,
                "src": "sany",
                "dipaddr": "10.1.1.1",
                "dst": "dhost",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            }
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["condition"]["source"] == {"type": "ADDRESS_ANY"}
    assert rule["condition"]["destination"] == {
        "type": "ADDRESS_HOST",
        "host-address": {"host-ipv4-address": "10.1.1.1"},
    }


def test_policy_any_to_network_keeps_source_as_address_any(policy) -> None:
    """sany source + dst=dnetwork (specific destination network) → source stays ADDRESS_ANY.

    Same Reading A logic: Central allows 'any → network' so no rewrite
    needed. Companion to test_policy_any_specific_keeps_source_as_address_any
    which exercises 'any → host'.
    """
    source = {
        "accname": "any-network",
        "acl_sess__v4policy": [
            {
                "sany": True,
                "src": "sany",
                "snetaddr": None,
                "dnetaddr": "10.0.0.0",
                "dnetmask": "255.0.0.0",
                "dst": "dnetwork",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "deny": True,
                "action": "deny_opt",
            }
        ],
    }
    body = emit_calls(policy, source, "aos8", runtime_values=_policy_runtime(source))[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["condition"]["source"] == {"type": "ADDRESS_ANY"}
    assert rule["condition"]["destination"] == {
        "type": "ADDRESS_NETWORK",
        "network-address": {"network-ipv4-address": "10.0.0.0/8"},
    }
    assert rule["action"] == {"type": "ACTION_DENY"}


def test_policy_any_any_with_empty_role_attribution_falls_back_to_address_any(policy) -> None:
    """Defensive: when role_attribution is empty AND src=sany+dst=dany, the
    'any-any' rewrite has no role to attribute to. Fall back to ADDRESS_ANY
    rather than producing an invalid empty role-list.

    Per the LLD, ACLs with no role attribution shouldn't reach the translation
    at all (consumer should filter), but the transform is defensive.
    """
    source = {
        "accname": "orphan-acl",
        "acl_sess__v4policy": [
            {
                "sany": True,
                "src": "sany",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "permit": True,
                "action": "permit",
            }
        ],
    }
    # role_records is empty — preprocessing finds no role attribution for this ACL
    rt = {"central_scope_id": "SCOPE", "role_records": []}
    body = emit_calls(policy, source, "aos8", runtime_values=rt)[0].body or {}
    rule = body["security-policy"]["policy-rule"][0]
    assert rule["condition"]["source"] == {"type": "ADDRESS_ANY"}
    assert rule["condition"]["destination"] == {"type": "ADDRESS_ANY"}
