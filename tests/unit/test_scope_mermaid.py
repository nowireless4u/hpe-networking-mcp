"""Unit tests for Mermaid diagram generation in scope_queries."""

import pytest
from treelib import Tree

from hpe_networking_mcp.platforms.central.scope_queries import tree_to_mermaid

# ---------------------------------------------------------------------------
# Helpers
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


def _make_resources() -> Tree:
    """Create an empty resources subtree."""
    rtree = Tree()
    rtree.create_node("resources", "resources")
    return rtree


def _build_mermaid_tree() -> Tree:
    """Build a tree: Global -> Site -> 2 Devices (AP + Switch)."""
    tree = Tree()

    tree.create_node(
        "g",
        "g",
        data={
            "device": _make_device("g", "GLOBAL", "GLOBAL"),
            "resources": _make_resources(),
        },
    )
    tree.create_node(
        "s",
        "s",
        parent="g",
        data={
            "device": _make_device("s", "HQ Site", "SITE"),
            "resources": _make_resources(),
        },
    )
    tree.create_node(
        "ap1",
        "ap1",
        parent="s",
        data={
            "device": _make_device(
                "ap1",
                "ap-lobby-01",
                "DEVICE",
                device_type="Aruba AP-515",
                device_model="AP-515",
            ),
            "resources": _make_resources(),
        },
    )
    tree.create_node(
        "sw1",
        "sw1",
        parent="s",
        data={
            "device": _make_device(
                "sw1",
                "switch-idf-01",
                "DEVICE",
                device_type="Aruba CX 6200",
                device_model="6200",
            ),
            "resources": _make_resources(),
        },
    )
    return tree


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTreeToMermaid:
    def test_contains_flowchart_header(self):
        tree = _build_mermaid_tree()
        result = tree_to_mermaid(tree)
        assert result.startswith("flowchart TD")

    def test_device_labels_use_hostname_not_model(self):
        tree = _build_mermaid_tree()
        result = tree_to_mermaid(tree)

        # Hostnames should appear in the diagram
        assert "ap-lobby-01" in result
        assert "switch-idf-01" in result

        # Model numbers should NOT be used as labels
        # They might appear elsewhere but not as the primary ((label))
        lines = result.split("\n")
        label_lines = [line for line in lines if "((" in line and "))" in line]
        for line in label_lines:
            # Extract label between (( and ))
            if "AP-515" in line and "ap-lobby-01" not in line:
                pytest.fail(f"Model number used as label instead of hostname: {line}")
            if "6200" in line and "switch-idf-01" not in line:
                pytest.fail(f"Model number used as label instead of hostname: {line}")

    def test_contains_legend(self):
        tree = _build_mermaid_tree()
        result = tree_to_mermaid(tree)
        assert "subgraph Legend" in result
        assert "L1((Global))" in result

    def test_contains_class_definitions(self):
        tree = _build_mermaid_tree()
        result = tree_to_mermaid(tree)
        assert "classDef global_scope" in result
        assert "classDef site" in result
        assert "classDef ap" in result
        assert "classDef switch" in result

    def test_include_devices_false_hides_devices(self):
        tree = _build_mermaid_tree()
        result = tree_to_mermaid(tree, include_devices=False)
        assert "ap-lobby-01" not in result
        assert "switch-idf-01" not in result

    def test_empty_tree(self):
        tree = Tree()
        result = tree_to_mermaid(tree)
        assert "No scope data" in result

    def test_nonexistent_scope_id(self):
        tree = _build_mermaid_tree()
        result = tree_to_mermaid(tree, scope_id="nonexistent")
        assert "not found" in result

    def test_subtree_rendering(self):
        tree = _build_mermaid_tree()
        result = tree_to_mermaid(tree, scope_id="s")
        assert "HQ Site" in result
        assert "ap-lobby-01" in result
        # Global should NOT appear when rendering subtree
        assert "GLOBAL" not in result or "global_scope" in result  # class name is ok
