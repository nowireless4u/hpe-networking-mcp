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
