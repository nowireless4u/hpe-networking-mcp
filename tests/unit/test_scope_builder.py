"""Unit tests for scope_builder and scope_queries modules."""

import pytest
from treelib import Tree

from hpe_networking_mcp.platforms.central.scope_builder import (
    _categorize_resources,
    _extract_personas,
    classify_device,
    tree_to_dict,
)
from hpe_networking_mcp.platforms.central.scope_queries import (
    build_inheritance_path,
    get_devices_in_scope,
    get_effective_resources_for_node,
)

# ---------------------------------------------------------------------------
# Helpers — build mock scope trees for testing
# ---------------------------------------------------------------------------


def _make_device(scope_id: str, scope_name: str, node_type: str, **extra) -> dict:
    """Create a device dict matching the API structure."""
    device = {
        "scope_id": scope_id,
        "type": node_type,
        "meta": {"scope_name": scope_name, **extra},
    }
    if "persona" in extra:
        device["persona"] = extra["persona"]
    return device


def _make_resources(*resources: tuple[str, str]) -> Tree:
    """Create a resources subtree from (persona, resource_name) pairs."""
    rtree = Tree()
    rtree.create_node("resources", "resources")
    personas_added: set[str] = set()
    for persona, resource_name in resources:
        if persona not in personas_added:
            rtree.create_node(persona, persona, parent="resources")
            personas_added.add(persona)
        rtree.create_node(resource_name, parent=persona, data={"config": "value"})
    return rtree


def _build_simple_tree() -> Tree:
    """Build a 3-level scope tree: Global -> Site -> Device."""
    tree = Tree()

    global_res = _make_resources(
        ("ACCESS_SWITCH", "policy/global-policy"),
        ("ACCESS_SWITCH", "dns/PDC DNS"),
        ("CAMPUS_AP", "policy/global-policy"),
    )
    tree.create_node(
        "global-id",
        "global-id",
        data={
            "device": _make_device("global-id", "GLOBAL", "GLOBAL"),
            "resources": global_res,
        },
    )

    site_res = _make_resources(
        ("ACCESS_SWITCH", "vlan/VLAN-100"),
        ("ACCESS_SWITCH", "vlan/VLAN-200"),
        ("ACCESS_SWITCH", "profile/switch-profile"),
        ("CAMPUS_AP", "ssid/MySSID"),
    )
    tree.create_node(
        "site-id",
        "site-id",
        parent="global-id",
        data={
            "device": _make_device("site-id", "HQ Site", "SITE"),
            "resources": site_res,
        },
    )

    dev_res = _make_resources()
    tree.create_node(
        "dev-id",
        "dev-id",
        parent="site-id",
        data={
            "device": _make_device(
                "dev-id",
                "switch-01",
                "DEVICE",
                device_type="Aruba CX 6200",
                device_model="6200",
                serial_number="CN1234",
                mac_address="AA:BB:CC:DD:EE:FF",
                persona="ACCESS_SWITCH",
            ),
            "resources": dev_res,
        },
    )

    return tree


# ---------------------------------------------------------------------------
# classify_device
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestClassifyDevice:
    def test_ap_patterns(self):
        assert classify_device("Aruba AP-515") == "AP"
        assert classify_device("iap-315") == "AP"

    def test_switch_patterns(self):
        assert classify_device("Aruba CX 6300") == "SWITCH"
        assert classify_device("AOS-CX Switch") == "SWITCH"

    def test_gateway_patterns(self):
        assert classify_device("Aruba Gateway 7010") == "GATEWAY"
        assert classify_device("SD-WAN Edge") == "GATEWAY"

    def test_other(self):
        assert classify_device("Unknown Thing") == "OTHER"
        assert classify_device(None) == "OTHER"
        assert classify_device("") == "OTHER"


# ---------------------------------------------------------------------------
# _categorize_resources
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCategorizeResources:
    def test_groups_by_prefix(self):
        resources = [
            {"name": "vlan/VLAN-100"},
            {"name": "vlan/VLAN-200"},
            {"name": "policy/my-policy"},
            {"name": "dns/PDC DNS"},
        ]
        result = _categorize_resources(resources)
        assert result["vlan"] == 2
        assert result["policy"] == 1
        assert result["dns"] == 1

    def test_unknown_prefix_categorized_as_other(self):
        resources = [{"name": "custom-resource-xyz"}]
        result = _categorize_resources(resources)
        assert result["other"] == 1

    def test_empty_list(self):
        assert _categorize_resources([]) == {}

    def test_slash_prefix_detection(self):
        resources = [{"name": "some/certificate/thing"}]
        result = _categorize_resources(resources)
        assert result.get("certificate") == 1


# ---------------------------------------------------------------------------
# _extract_personas
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExtractPersonas:
    def test_includes_count_and_categories(self):
        rtree = _make_resources(
            ("ACCESS_SWITCH", "vlan/VLAN-100"),
            ("ACCESS_SWITCH", "policy/my-policy"),
            ("CAMPUS_AP", "ssid/MySSID"),
        )
        personas = _extract_personas(rtree)
        assert len(personas) == 2

        switch_persona = next(p for p in personas if p["name"] == "ACCESS_SWITCH")
        assert switch_persona["count"] == 2
        assert "vlan" in switch_persona["categories"]
        assert "policy" in switch_persona["categories"]

        ap_persona = next(p for p in personas if p["name"] == "CAMPUS_AP")
        assert ap_persona["count"] == 1

    def test_none_tree_returns_empty(self):
        assert _extract_personas(None) == []

    def test_empty_tree_returns_empty(self):
        rtree = Tree()
        assert _extract_personas(rtree) == []


# ---------------------------------------------------------------------------
# tree_to_dict — committed view with counts
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTreeToDict:
    def test_root_has_counts(self):
        tree = _build_simple_tree()
        result = tree_to_dict(tree)

        assert result["scope_name"] == "GLOBAL"
        assert result["persona_count"] == 2
        assert result["resource_count"] == 3
        assert result["child_scope_count"] == 1
        assert result["device_count"] == 0

    def test_site_has_counts(self):
        tree = _build_simple_tree()
        result = tree_to_dict(tree)
        site = result["children"][0]

        assert site["scope_name"] == "HQ Site"
        assert site["persona_count"] == 2
        assert site["resource_count"] == 4
        assert site["device_count"] == 1

    def test_device_has_device_info(self):
        tree = _build_simple_tree()
        result = tree_to_dict(tree)
        device = result["children"][0]["children"][0]

        assert device["type"] == "DEVICE"
        assert device["device_info"]["device_model"] == "6200"
        assert device["persona"] == "ACCESS_SWITCH"

    def test_empty_tree(self):
        tree = Tree()
        assert tree_to_dict(tree) == {}


# ---------------------------------------------------------------------------
# get_effective_resources_for_node
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEffectiveResources:
    def test_inherits_from_ancestors(self):
        tree = _build_simple_tree()
        effective = get_effective_resources_for_node(tree, "dev-id")

        resource_names = [r["name"] for r in effective]
        assert "policy/global-policy" in resource_names
        assert "vlan/VLAN-100" in resource_names

    def test_include_details_returns_data(self):
        tree = _build_simple_tree()
        effective = get_effective_resources_for_node(tree, "site-id", include_details=True)

        has_details = False
        for resource_group in effective:
            for instance in resource_group["instances"]:
                if "details" in instance:
                    has_details = True
                    assert instance["details"] == {"config": "value"}
        assert has_details, "Expected at least one resource with details"

    def test_include_details_false_omits_data(self):
        tree = _build_simple_tree()
        effective = get_effective_resources_for_node(tree, "site-id", include_details=False)

        for resource_group in effective:
            for instance in resource_group["instances"]:
                assert "details" not in instance

    def test_persona_filter(self):
        tree = _build_simple_tree()
        effective = get_effective_resources_for_node(tree, "site-id", persona="CAMPUS_AP")

        for resource_group in effective:
            for instance in resource_group["instances"]:
                assert instance["persona"] == "CAMPUS_AP"

    def test_nonexistent_scope_returns_empty(self):
        tree = _build_simple_tree()
        assert get_effective_resources_for_node(tree, "nonexistent") == []


# ---------------------------------------------------------------------------
# build_inheritance_path
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBuildInheritancePath:
    def test_path_order_root_to_leaf(self):
        tree = _build_simple_tree()
        path = build_inheritance_path(tree, "dev-id")

        assert len(path) == 3
        assert path[0]["scope_name"] == "GLOBAL"
        assert path[0]["scope_type"] == "GLOBAL"
        assert path[1]["scope_name"] == "HQ Site"
        assert path[1]["scope_type"] == "SITE"
        assert path[2]["scope_name"] == "switch-01"
        assert path[2]["scope_type"] == "DEVICE"

    def test_path_includes_resource_counts(self):
        tree = _build_simple_tree()
        path = build_inheritance_path(tree, "site-id")

        global_entry = path[0]
        assert global_entry["resource_count"] == 3

        site_entry = path[1]
        assert site_entry["resource_count"] == 4

    def test_root_path_is_single_entry(self):
        tree = _build_simple_tree()
        path = build_inheritance_path(tree, "global-id")
        assert len(path) == 1
        assert path[0]["scope_name"] == "GLOBAL"


# ---------------------------------------------------------------------------
# get_devices_in_scope
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetDevicesInScope:
    def test_finds_devices_under_scope(self):
        tree = _build_simple_tree()
        devices = get_devices_in_scope(tree, "global-id")
        assert len(devices) == 1
        assert devices[0]["scope_name"] == "switch-01"
        assert devices[0]["category"] == "SWITCH"

    def test_device_type_filter(self):
        tree = _build_simple_tree()
        assert len(get_devices_in_scope(tree, "global-id", "SWITCH")) == 1
        assert len(get_devices_in_scope(tree, "global-id", "AP")) == 0

    def test_nonexistent_scope_returns_empty(self):
        tree = _build_simple_tree()
        assert get_devices_in_scope(tree, "nope") == []
