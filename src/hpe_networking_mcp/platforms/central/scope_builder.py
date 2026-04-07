"""Core logic for building and querying the Aruba Central scope/configuration tree.

Adapted from CnxScopeTools cnx_scope.py and device_classifier.py. This is a pure
logic module with no MCP dependencies -- it builds a treelib Tree from Central API
data and provides query/traversal helpers.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Literal

from loguru import logger
from treelib import Tree

from hpe_networking_mcp.platforms.central.utils import retry_central_command

# ---------------------------------------------------------------------------
# Device classification
# ---------------------------------------------------------------------------

AP_PATTERNS: list[str] = ["ap", "iap", "access point", "rap"]
SWITCH_PATTERNS: list[str] = ["switch", "cx", "aos-cx", "2930", "2540", "6300", "6400", "8400"]
GATEWAY_PATTERNS: list[str] = ["gateway", "gw", "controller", "mc", "vgw", "sd-wan", "edgeconnect"]

# Known resource name prefixes for categorization
RESOURCE_CATEGORY_PREFIXES: dict[str, str] = {
    "vlan": "vlan",
    "policy": "policy",
    "role": "policy",
    "user-role": "policy",
    "profile": "profile",
    "system": "system",
    "dns": "dns",
    "interface": "interface",
    "ssid": "ssid",
    "wlan": "ssid",
    "cert": "certificate",
    "certificate": "certificate",
    "acl": "acl",
    "ntp": "ntp",
    "snmp": "snmp",
    "aaa": "aaa",
    "radius": "aaa",
    "vpn": "vpn",
    "tunnel": "vpn",
    "routing": "routing",
    "route": "routing",
    "dhcp": "dhcp",
    "firewall": "firewall",
    "management": "management",
    "device-identity": "identity",
    "mpsk": "ssid",
}


def classify_device(device_type: str | None) -> Literal["AP", "SWITCH", "GATEWAY", "OTHER"]:
    """Classify a device type string into a category.

    Args:
        device_type: Raw device type string from API (e.g. "Aruba AP-515").

    Returns:
        One of "AP", "SWITCH", "GATEWAY", or "OTHER".
    """
    if not device_type:
        return "OTHER"
    normalized = device_type.lower().strip()
    for p in AP_PATTERNS:
        if p in normalized:
            return "AP"
    for p in SWITCH_PATTERNS:
        if p in normalized:
            return "SWITCH"
    for p in GATEWAY_PATTERNS:
        if p in normalized:
            return "GATEWAY"
    return "OTHER"


# ---------------------------------------------------------------------------
# Tree construction helpers (ported from cnx_scope.py)
# ---------------------------------------------------------------------------


def _get_scope_name(device: dict) -> str:
    """Return the human-readable scope name for a device/scope node."""
    meta = device.get("meta") or {}
    return meta.get("scope_name", device.get("scope_id", "<UNKNOWN>"))


def _get_device_info(device: dict) -> dict[str, Any]:
    """Extract device metadata into a flat dict."""
    meta = device.get("meta") or {}
    return {
        "device_type": meta.get("device_type", "N/A"),
        "device_model": meta.get("device_model", "N/A"),
        "part_number": meta.get("part_number"),
        "mac_address": meta.get("mac_address"),
        "serial_number": meta.get("serial_number", "N/A"),
    }


def _insert_tree(devices_by_scopeid: dict, device_tree: Tree, scope_ids: list[str]) -> None:
    """Insert a device path (root-to-leaf) into the tree."""
    parent_scope_id = None
    for scope_id in scope_ids:
        node = device_tree.get_node(scope_id)
        if node is None:
            if scope_id not in devices_by_scopeid:
                continue
            resources_tree = Tree()
            resources_tree.create_node("resources", "resources")
            device_tree.create_node(
                scope_id,
                scope_id,
                parent=parent_scope_id,
                data={"device": devices_by_scopeid[scope_id], "resources": resources_tree},
            )
        parent_scope_id = scope_id


def _build_tree(device_data: dict, maps_data: dict) -> Tree:
    """Build the complete scope tree from the two Central API responses.

    Args:
        device_data: Response from cnxdevice/v1/debug/get_scope_data (contains "devices").
        maps_data: Response from network-config/v1alpha1/scope-maps (contains "scope-map").

    Returns:
        A treelib Tree with scope hierarchy and attached resources.
    """
    devices = device_data.get("devices", [])
    devices_by_scopeid: dict[str, dict] = {}
    for device in devices:
        scope_id = device.get("scope_id")
        if scope_id and scope_id not in devices_by_scopeid:
            devices_by_scopeid[scope_id] = device

    device_tree = Tree()
    for device in devices:
        hier_path = device.get("hier_path")
        if hier_path is None:
            continue
        _insert_tree(devices_by_scopeid, device_tree, list(reversed(hier_path)))

    # Attach resources from scope-maps
    for resource in maps_data.get("scope-map", []):
        scope_id = resource.get("scope-name")
        persona = resource.get("persona")
        if not scope_id or not persona:
            continue
        node = device_tree.get_node(scope_id)
        if node is None or node.data is None:
            continue
        resources_tree: Tree = node.data.get("resources")
        if resources_tree is None:
            continue
        persona_node = resources_tree.get_node(persona)
        if persona_node is None:
            resources_tree.create_node(persona, persona, parent="resources")
        resources_tree.create_node(
            resource.get("resource", "unknown"),
            parent=persona,
            data=resource.get("_details"),
        )

    logger.info("Scope tree built: {} nodes from {} devices", len(device_tree.all_nodes()), len(devices))
    return device_tree


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_scope_tree(conn: Any) -> Tree:
    """Fetch scope data and scope maps from Central, return a treelib Tree.

    Makes two API calls:
      1. GET cnxdevice/v1/debug/get_scope_data
      2. GET network-config/v1alpha1/scope-maps

    Args:
        conn: pycentral connection object.

    Returns:
        A treelib Tree representing the scope hierarchy.
    """
    device_resp = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="cnxdevice/v1/debug/get_scope_data",
    )
    maps_resp = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="network-config/v1alpha1/scope-maps",
    )
    device_data = device_resp.get("msg", {})
    maps_data = maps_resp.get("msg", {})
    return _build_tree(device_data, maps_data)


# ---------------------------------------------------------------------------
# Dict conversion
# ---------------------------------------------------------------------------


def tree_to_dict(tree: Tree, effective: bool = False) -> dict | list:
    """Convert a scope tree to a JSON-serializable structure.

    Args:
        tree: The treelib scope tree.
        effective: If True, include inherited resources at each node.

    Returns:
        A hierarchical dict (committed) or list (effective) representation.
    """
    if tree.root is None:
        return {}
    if effective:
        return _node_to_dict_effective(tree, tree.root) or {}
    return _node_to_dict(tree, tree.root) or {}


def _node_to_dict(tree: Tree, node_id: str) -> dict | None:
    """Recursively convert a committed tree node to a dict."""
    node = tree.get_node(node_id)
    if node is None or node.data is None:
        return None
    device = node.data.get("device")
    if device is None:
        return None

    scope_name = _get_scope_name(device)
    device_type = device.get("type", "")
    personas = _extract_personas(node.data.get("resources"))

    children: list[dict] = []
    child_scope_count = 0
    device_count = 0
    for child in tree.children(node_id):
        child_dict = _node_to_dict(tree, child.tag)
        if child_dict is not None:
            children.append(child_dict)
            if child_dict.get("type") == "DEVICE":
                device_count += 1
            else:
                child_scope_count += 1

    result: dict[str, Any] = {
        "scope_id": device.get("scope_id"),
        "scope_name": scope_name,
        "type": device_type,
        "persona_count": len(personas),
        "resource_count": sum(p["count"] for p in personas),
        "child_scope_count": child_scope_count,
        "device_count": device_count,
        "personas": personas,
        "children": children,
    }
    if device_type == "DEVICE":
        result["device_info"] = _get_device_info(device)
        result["persona"] = device.get("persona")

    return result


def _node_to_dict_effective(tree: Tree, node_id: str) -> dict | None:
    """Recursively convert a tree node to a dict with effective (inherited) resources."""
    # Import here to avoid circular imports
    from hpe_networking_mcp.platforms.central.scope_queries import (
        _collect_effective_for_node,
    )

    node = tree.get_node(node_id)
    if node is None or node.data is None:
        return None
    device = node.data.get("device")
    if device is None:
        return None

    scope_name = _get_scope_name(device)
    device_type = device.get("type", "")
    personas = _extract_personas(node.data.get("resources"))

    children: list[dict] = []
    child_scope_count = 0
    device_count = 0
    for child in tree.children(node_id):
        child_dict = _node_to_dict_effective(tree, child.tag)
        if child_dict is not None:
            children.append(child_dict)
            if child_dict.get("type") == "DEVICE":
                device_count += 1
            else:
                child_scope_count += 1

    result: dict[str, Any] = {
        "scope_id": device.get("scope_id"),
        "scope_name": scope_name,
        "type": device_type,
        "persona_count": len(personas),
        "resource_count": sum(p["count"] for p in personas),
        "child_scope_count": child_scope_count,
        "device_count": device_count,
        "personas": personas,
        "effective_resources": _collect_effective_for_node(tree, node_id, device),
        "children": children,
    }
    if device_type == "DEVICE":
        result["device_info"] = _get_device_info(device)
        result["persona"] = device.get("persona")

    return result


def _extract_personas(resources_tree: Tree | None) -> list[dict]:
    """Extract persona/resource list from a node's resources subtree.

    Returns enriched persona dicts with count and category breakdown.
    """
    if resources_tree is None or resources_tree.root is None:
        return []
    personas: list[dict] = []
    for persona_node in sorted(resources_tree.children(resources_tree.root), key=lambda n: n.tag):
        resource_nodes = resources_tree.children(persona_node.tag)
        resources = [{"name": rn.tag, "has_details": rn.data is not None} for rn in resource_nodes]
        if resources:
            categories = _categorize_resources(resources)
            personas.append(
                {
                    "name": persona_node.tag,
                    "count": len(resources),
                    "categories": categories,
                    "resources": resources,
                }
            )
    return personas


def _categorize_resources(resources: list[dict]) -> dict[str, int]:
    """Group resources by category based on name prefixes.

    Args:
        resources: List of resource dicts with "name" keys.

    Returns:
        Dict mapping category names to counts.
    """
    counts: Counter[str] = Counter()
    for r in resources:
        name = r.get("name", "").lower()
        category = "other"
        for prefix, cat in RESOURCE_CATEGORY_PREFIXES.items():
            if name.startswith(prefix) or f"/{prefix}" in name:
                category = cat
                break
        counts[category] += 1
    return dict(sorted(counts.items(), key=lambda x: (-x[1], x[0])))
