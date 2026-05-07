"""Engine tests — emit_calls produces the right ordered Central calls.

End-to-end coverage: take the shipped named_vlan_v1.json mapping, feed it
a realistic AOS 8 vlan_name_id source dict, and assert the engine produces
exactly the 6-step sequence we hand-validated against the live tenant.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.migrations.engine import EngineError, emit_calls
from hpe_networking_mcp.migrations.loader import load_mappings

pytestmark = pytest.mark.unit


@pytest.fixture
def mappings() -> dict:
    return load_mappings()


@pytest.fixture
def named_vlan_mapping(mappings: dict):
    return mappings["named_vlan"]


# --------------------------------------------------------------------------- #
# Core: end-to-end emit on a single-ID binding
# --------------------------------------------------------------------------- #


def test_named_vlan_with_single_vlan_id_emits_six_calls(named_vlan_mapping) -> None:
    """Source: vlan_name_id record {name: 'user', vlan-ids: '107'}.

    Expected: 1 layer2-vlan create + 1 alias create + 1 named-vlan create
    + 1 layer2-vlan assign (with 2-DF array) + 1 named-vlan assign
    (with 2-DF array) + 2 LOCAL alias overrides (one per DF) = 7 calls.

    Wait: 1+1+1+1+1+2 = 7. The 6-step *flow* fans out to 7 calls because
    step 6 is per-device-function. Confirm the call count.
    """
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(
        mapping=named_vlan_mapping,
        source_data=source,
        source_platform_id="aos8",
        central_scope_id="18413656377",
    )

    # 6 steps × iteration fan-out
    # step 1: per_vlan_id_in_binding × 1 ID = 1
    # step 2: once = 1
    # step 3: once = 1
    # step 4: per_vlan_id × 1 ID, body_template multi-DF = 1
    # step 5: once, body_template multi-DF = 1
    # step 6: per_device_function × 2 DFs = 2
    # Total = 7
    assert len(calls) == 7

    # Steps emitted in order
    steps = [c.step for c in calls]
    assert steps == [1, 2, 3, 4, 5, 6, 6]


def test_step1_layer2_vlan_create(named_vlan_mapping) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan_mapping, source, "aos8", "SCOPE")
    step1 = [c for c in calls if c.step == 1][0]
    assert step1.method == "POST"
    assert step1.endpoint == "/network-config/v1alpha1/layer2-vlan/107"
    assert step1.body == {"vlan": "107"}
    assert step1.query_params == {}


def test_step2_alias_create_with_placeholder(named_vlan_mapping) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan_mapping, source, "aos8", "SCOPE")
    step2 = [c for c in calls if c.step == 2][0]
    assert step2.method == "POST"
    assert step2.endpoint == "/network-config/v1alpha1/aliases/user"
    assert step2.body == {
        "name": "user",
        "type": "ALIAS_VLAN",
        "default-value": {"vlan-value": {"vlan-id-ranges": ["1"]}},
    }


def test_step3_named_vlan_create_references_alias(named_vlan_mapping) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan_mapping, source, "aos8", "SCOPE")
    step3 = [c for c in calls if c.step == 3][0]
    assert step3.method == "POST"
    assert step3.endpoint == "/network-config/v1alpha1/named-vlan/user"
    assert step3.body == {"name": "user", "vlan": {"vlan-alias": "user"}}


def test_step4_assign_layer2_vlan_packs_both_device_functions(named_vlan_mapping) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan_mapping, source, "aos8", "SCOPE-A")
    step4 = [c for c in calls if c.step == 4][0]
    assert step4.method == "POST"
    assert step4.endpoint == "/network-config/v1alpha1/config-assignments"
    body = step4.body or {}
    assert "config-assignment" in body
    items = body["config-assignment"]
    assert len(items) == 2
    assert {item["device-function"] for item in items} == {"MOBILITY_GW", "CAMPUS_AP"}
    assert all(item["scope-id"] == "SCOPE-A" for item in items)
    assert all(item["profile-type"] == "layer2-vlan" for item in items)
    assert all(item["profile-instance"] == "107" for item in items)


def test_step5_assign_named_vlan_packs_both_device_functions(named_vlan_mapping) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan_mapping, source, "aos8", "SCOPE-B")
    step5 = [c for c in calls if c.step == 5][0]
    body = step5.body or {}
    items = body["config-assignment"]
    assert len(items) == 2
    assert all(item["profile-type"] == "named-vlan" for item in items)
    assert all(item["profile-instance"] == "user" for item in items)
    assert all(item["scope-id"] == "SCOPE-B" for item in items)


def test_step6_local_alias_override_per_device_function(named_vlan_mapping) -> None:
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(named_vlan_mapping, source, "aos8", "SCOPE-C")
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


def test_csv_vlan_ids_expand_to_multiple_layer2_calls(named_vlan_mapping) -> None:
    source = {"name": "local", "vlan-ids": "104,160"}
    calls = emit_calls(named_vlan_mapping, source, "aos8", "SCOPE")
    step1_calls = [c for c in calls if c.step == 1]
    assert len(step1_calls) == 2
    assert {c.endpoint for c in step1_calls} == {
        "/network-config/v1alpha1/layer2-vlan/104",
        "/network-config/v1alpha1/layer2-vlan/160",
    }


def test_range_vlan_ids_expand_for_layer2_but_preserve_for_alias_override(named_vlan_mapping) -> None:
    """Asymmetric transform: layer2-vlan iterates 108,109,110; alias override gets ['108-110']."""
    source = {"name": "iot", "vlan-ids": "108-110"}
    calls = emit_calls(named_vlan_mapping, source, "aos8", "SCOPE")

    # Step 1: 3 separate layer2-vlan creations
    step1_calls = [c for c in calls if c.step == 1]
    assert len(step1_calls) == 3
    assert {c.endpoint for c in step1_calls} == {
        "/network-config/v1alpha1/layer2-vlan/108",
        "/network-config/v1alpha1/layer2-vlan/109",
        "/network-config/v1alpha1/layer2-vlan/110",
    }

    # Step 4: 3 separate POSTs to /config-assignments, each packing MOBILITY_GW + CAMPUS_AP
    step4_calls = [c for c in calls if c.step == 4]
    assert len(step4_calls) == 3
    for c in step4_calls:
        items = (c.body or {})["config-assignment"]
        assert len(items) == 2  # multi-DF array
        assert {item["device-function"] for item in items} == {"MOBILITY_GW", "CAMPUS_AP"}

    # Step 6: alias overrides preserve range syntax
    step6_calls = [c for c in calls if c.step == 6]
    assert len(step6_calls) == 2  # one per DF
    for c in step6_calls:
        assert (c.body or {})["default-value"]["vlan-value"]["vlan-id-ranges"] == ["108-110"]


def test_device_function_override_changes_call_count(named_vlan_mapping) -> None:
    """Caller can restrict which device functions emit; e.g. tunnel-only migration → MOBILITY_GW only."""
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(
        named_vlan_mapping,
        source,
        "aos8",
        "SCOPE",
        device_functions=["MOBILITY_GW"],
    )
    # Step 6 (per-device-function) goes from 2 calls to 1
    assert len([c for c in calls if c.step == 6]) == 1
    # Steps 4 and 5 (multi-DF arrays) go from 2-element arrays to 1-element
    step4 = [c for c in calls if c.step == 4][0]
    assert len((step4.body or {})["config-assignment"]) == 1


def test_alias_name_override_takes_precedence(named_vlan_mapping) -> None:
    """Operators can override the lowercase-of-named-vlan default."""
    source = {"name": "user", "vlan-ids": "107"}
    calls = emit_calls(
        named_vlan_mapping,
        source,
        "aos8",
        "SCOPE",
        overrides={"alias_name": "USR-ALIAS-CUSTOM"},
    )
    step2 = [c for c in calls if c.step == 2][0]
    assert step2.endpoint == "/network-config/v1alpha1/aliases/USR-ALIAS-CUSTOM"
    step3 = [c for c in calls if c.step == 3][0]
    assert step3.body == {"name": "user", "vlan": {"vlan-alias": "USR-ALIAS-CUSTOM"}}


# --------------------------------------------------------------------------- #
# Error paths
# --------------------------------------------------------------------------- #


def test_unknown_source_platform_raises(named_vlan_mapping) -> None:
    with pytest.raises(EngineError, match="does not declare source 'cisco_ios'"):
        emit_calls(
            mapping=named_vlan_mapping,
            source_data={},
            source_platform_id="cisco_ios",
            central_scope_id="X",
        )


def test_missing_required_source_field_raises_when_used(named_vlan_mapping) -> None:
    """If source data lacks a key the emit needs, surface a clear error."""
    # vlan-ids missing entirely
    source = {"name": "user"}
    with pytest.raises(EngineError, match="vlan_ids"):
        emit_calls(named_vlan_mapping, source, "aos8", "SCOPE")
