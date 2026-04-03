"""Core logic for building and querying the Aruba Central scope/configuration tree.

Adapted from CnxScopeTools cnx_scope.py and device_classifier.py. This is a pure
logic module with no MCP dependencies -- it builds a treelib Tree from Central API
data and provides query/traversal helpers.
"""

from __future__ import annotations

import re
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

MERMAID_COLORS: dict[str, str] = {
    "GLOBAL": "#808080",
    "COLLECTION": "#4CAF50",
    "SITE": "#FF9800",
    "AP": "#2196F3",
    "SWITCH": "#9C27B0",
    "GATEWAY": "#F44336",
    "OTHER": "#607D8B",
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

    result: dict[str, Any] = {
        "scope_id": device.get("scope_id"),
        "scope_name": scope_name,
        "type": device_type,
        "personas": _extract_personas(node.data.get("resources")),
        "children": [],
    }
    if device_type == "DEVICE":
        result["device_info"] = _get_device_info(device)
        result["persona"] = device.get("persona")

    for child in tree.children(node_id):
        child_dict = _node_to_dict(tree, child.tag)
        if child_dict is not None:
            result["children"].append(child_dict)
    return result


def _node_to_dict_effective(tree: Tree, node_id: str) -> dict | None:
    """Recursively convert a tree node to a dict with effective (inherited) resources."""
    node = tree.get_node(node_id)
    if node is None or node.data is None:
        return None
    device = node.data.get("device")
    if device is None:
        return None

    scope_name = _get_scope_name(device)
    device_type = device.get("type", "")

    result: dict[str, Any] = {
        "scope_id": device.get("scope_id"),
        "scope_name": scope_name,
        "type": device_type,
        "personas": _extract_personas(node.data.get("resources")),
        "effective_resources": _collect_effective_for_node(tree, node_id, device),
        "children": [],
    }
    if device_type == "DEVICE":
        result["device_info"] = _get_device_info(device)
        result["persona"] = device.get("persona")

    for child in tree.children(node_id):
        child_dict = _node_to_dict_effective(tree, child.tag)
        if child_dict is not None:
            result["children"].append(child_dict)
    return result


def _extract_personas(resources_tree: Tree | None) -> list[dict]:
    """Extract persona/resource list from a node's resources subtree."""
    if resources_tree is None or resources_tree.root is None:
        return []
    personas: list[dict] = []
    for persona_node in sorted(resources_tree.children(resources_tree.root), key=lambda n: n.tag):
        resource_nodes = resources_tree.children(persona_node.tag)
        resources = [{"name": rn.tag, "has_details": rn.data is not None} for rn in resource_nodes]
        if resources:
            personas.append({"name": persona_node.tag, "resources": resources})
    return personas


def _collect_effective_for_node(tree: Tree, node_id: str, device: dict) -> list[dict]:
    """Collect effective (committed + inherited) resources for a single node."""
    persona = device.get("persona")
    path_ids = list(tree.rsearch(node_id))

    effective: dict[str, list[dict]] = {}
    for ancestor_id in path_ids:
        ancestor_node = tree.get_node(ancestor_id)
        if ancestor_node is None or ancestor_node.data is None:
            continue
        res_tree: Tree | None = ancestor_node.data.get("resources")
        if res_tree is None or res_tree.root is None:
            continue
        ancestor_device = ancestor_node.data.get("device", {})
        origin_name = _get_scope_name(ancestor_device)

        # Collect for the specific persona (devices) or all personas (scopes)
        target_personas = [persona] if persona else [pn.tag for pn in res_tree.children(res_tree.root)]
        for p in target_personas:
            if p is None:
                continue
            p_node = res_tree.get_node(p)
            if p_node is None:
                continue
            for rn in res_tree.children(p):
                if rn.tag not in effective:
                    effective[rn.tag] = []
                effective[rn.tag].append(
                    {
                        "name": rn.tag,
                        "origin_scope_id": ancestor_device.get("scope_id"),
                        "origin_scope_name": origin_name,
                        "persona": p,
                        "has_details": rn.data is not None,
                    }
                )
    return [{"name": k, "instances": v} for k, v in sorted(effective.items())]


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------


def get_effective_resources_for_node(
    tree: Tree,
    scope_id: str,
    persona: str | None = None,
) -> list[dict]:
    """Collect effective (inherited + committed) resources for a given scope node.

    Walks from the node up to the root, collecting resources at each level.

    Args:
        tree: The scope tree.
        scope_id: Target scope node ID.
        persona: Optional persona filter.

    Returns:
        List of resource groups with origin tracking.
    """
    node = tree.get_node(scope_id)
    if node is None or node.data is None:
        return []
    device = node.data.get("device", {})

    # If no explicit persona, use the device's own persona or collect all
    effective_persona = persona or device.get("persona")
    path_ids = list(tree.rsearch(scope_id))

    effective: dict[str, list[dict]] = {}
    for ancestor_id in path_ids:
        ancestor_node = tree.get_node(ancestor_id)
        if ancestor_node is None or ancestor_node.data is None:
            continue
        res_tree: Tree | None = ancestor_node.data.get("resources")
        if res_tree is None or res_tree.root is None:
            continue
        ancestor_device = ancestor_node.data.get("device", {})
        origin_name = _get_scope_name(ancestor_device)

        target_personas = (
            [effective_persona] if effective_persona else [pn.tag for pn in res_tree.children(res_tree.root)]
        )
        for p in target_personas:
            if p is None:
                continue
            p_node = res_tree.get_node(p)
            if p_node is None:
                continue
            for rn in res_tree.children(p):
                if rn.tag not in effective:
                    effective[rn.tag] = []
                effective[rn.tag].append(
                    {
                        "name": rn.tag,
                        "origin_scope_id": ancestor_device.get("scope_id"),
                        "origin_scope_name": origin_name,
                        "persona": p,
                        "has_details": rn.data is not None,
                    }
                )
    return [{"name": k, "instances": v} for k, v in sorted(effective.items())]


def get_devices_in_scope(
    tree: Tree,
    scope_id: str,
    device_type: str | None = None,
) -> list[dict]:
    """Find all DEVICE nodes under a given scope.

    Args:
        tree: The scope tree.
        scope_id: Scope node ID to search under.
        device_type: Optional filter -- "AP", "SWITCH", "GATEWAY", or "OTHER".

    Returns:
        List of device dicts with metadata.
    """
    node = tree.get_node(scope_id)
    if node is None:
        return []
    results: list[dict] = []
    _collect_devices(tree, scope_id, device_type, results)
    return results


def _collect_devices(tree: Tree, node_id: str, device_type: str | None, results: list[dict]) -> None:
    """Recursively collect DEVICE nodes under a scope."""
    node = tree.get_node(node_id)
    if node is None or node.data is None:
        return
    device = node.data.get("device", {})
    if device.get("type") == "DEVICE":
        meta = device.get("meta") or {}
        category = classify_device(meta.get("device_type"))
        if device_type is None or category == device_type.upper():
            results.append(
                {
                    "scope_id": device.get("scope_id"),
                    "scope_name": _get_scope_name(device),
                    "category": category,
                    "persona": device.get("persona"),
                    **_get_device_info(device),
                }
            )
    for child in tree.children(node_id):
        _collect_devices(tree, child.tag, device_type, results)


# ---------------------------------------------------------------------------
# Mermaid diagram generation
# ---------------------------------------------------------------------------

_SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9_]")


def _safe_id(text: str) -> str:
    """Convert arbitrary text to a safe Mermaid node ID."""
    return _SAFE_ID_RE.sub("_", text)


def tree_to_mermaid(
    tree: Tree,
    scope_id: str | None = None,
    include_resources: bool = False,
    include_devices: bool = True,
) -> str:
    """Build a Mermaid flowchart with compact circle nodes and a legend.

    Hierarchy flow: Global → Site Collections → Sites → Devices.
    Device groups shown as separate islands with dashed links
    to their member devices (they add config independently).

    Args:
        tree: The scope tree.
        scope_id: If provided, only render the subtree rooted here.
        include_resources: Whether to show resource nodes.
        include_devices: Whether to show device leaf nodes.

    Returns:
        Mermaid flowchart string.
    """
    if tree.root is None:
        return 'flowchart TD\n    EMPTY["No scope data"]'

    root = scope_id if scope_id else tree.root
    if tree.get_node(root) is None:
        return f"flowchart TD\n    EMPTY[\"Scope '{root}' not found\"]"

    lines: list[str] = ["flowchart TD"]
    class_assignments: dict[str, str] = {}  # m_id -> class name
    device_group_links: list[tuple[str, str]] = []  # (group_id, device_id)
    _counter = {"n": 0}

    def next_id(prefix: str) -> str:
        _counter["n"] += 1
        return f"{prefix}{_counter['n']}"

    def _get_node_class(
        node_type: str,
        device: dict,
        tree: Tree,
        node_id: str,
    ) -> tuple[str, str]:
        """Return (short_label, css_class) for a node."""
        scope_name = _get_scope_name(device)
        if node_type == "DEVICE":
            meta = device.get("meta") or {}
            cat = classify_device(meta.get("device_type"))
            model = meta.get("device_model", "")
            serial = meta.get("serial_number", "")
            short = serial if serial else scope_name
            if model and model != "N/A":
                short = f"{model}"
            return short, cat.lower()
        if node_type == "GLOBAL":
            return scope_name, "global_scope"
        # COLLECTION — check if it's a site
        if _has_device_descendant(tree, node_id):
            children_types = []
            for c in tree.children(node_id):
                cn = tree.get_node(c.tag)
                if cn is not None and cn.data is not None:
                    dt = cn.data.get("device", {}).get("type", "")
                    children_types.append(dt)
            if any(t == "DEVICE" for t in children_types):
                return scope_name, "site"
        return scope_name, "collection"

    def render_node(
        node_id: str,
        parent_mermaid_id: str | None,
    ) -> None:
        node = tree.get_node(node_id)
        if node is None or node.data is None:
            return
        device = node.data.get("device", {})
        node_type = device.get("type", "")

        is_device = node_type == "DEVICE"
        if is_device and not include_devices:
            return

        label, css_class = _get_node_class(node_type, device, tree, node_id)

        m_id = next_id("N")

        # Circle syntax for compact nodes
        lines.append(f"    {m_id}(({label}))")
        if parent_mermaid_id:
            lines.append(f"    {parent_mermaid_id} --> {m_id}")
        class_assignments[m_id] = css_class

        # Resources as small dashed links
        if include_resources and not is_device:
            res_tree: Tree | None = (node.data or {}).get("resources")
            if res_tree is not None and res_tree.root is not None:
                for pn in res_tree.children(res_tree.root):
                    for rn in res_tree.children(pn.tag):
                        r_id = next_id("R")
                        short_res = rn.tag.split("/")[-1]
                        lines.append(f"    {r_id}[/{short_res}/]")
                        lines.append(f"    {m_id} -.-> {r_id}")
                        class_assignments[r_id] = "resource"

        # Recurse children
        for child in tree.children(node_id):
            render_node(child.tag, m_id)

    render_node(root, None)

    # Class definitions
    lines.append("")
    lines.append("    classDef global_scope fill:#808080,color:#fff,stroke-width:0")
    lines.append("    classDef collection fill:#4CAF50,color:#fff,stroke-width:0")
    lines.append("    classDef site fill:#FF9800,color:#fff,stroke-width:0")
    lines.append("    classDef ap fill:#2196F3,color:#fff,stroke-width:0")
    lines.append("    classDef switch fill:#9C27B0,color:#fff,stroke-width:0")
    lines.append("    classDef gateway fill:#F44336,color:#fff,stroke-width:0")
    lines.append("    classDef other fill:#607D8B,color:#fff,stroke-width:0")
    lines.append("    classDef devgroup fill:#607D8B,color:#fff,stroke-dasharray:5")
    lines.append("    classDef resource fill:#E0E0E0,color:#333,stroke-width:0")

    # Apply classes
    for m_id, cls in class_assignments.items():
        lines.append(f"    class {m_id} {cls}")

    # Device group dashed links
    for gid, did in device_group_links:
        lines.append(f"    {gid} -.-> {did}")

    # Legend
    lines.append("")
    lines.append("    subgraph Legend")
    lines.append("        direction LR")
    lines.append("        L1((Global)):::global_scope")
    lines.append("        L2((Collection)):::collection")
    lines.append("        L3((Site)):::site")
    lines.append("        L4((AP)):::ap")
    lines.append("        L5((Switch)):::switch")
    lines.append("        L6((Gateway)):::gateway")
    lines.append("    end")

    return "\n".join(lines)


def _has_device_descendant(tree: Tree, node_id: str) -> bool:
    """Check if any descendant of a node is a DEVICE."""
    for child in tree.children(node_id):
        child_node = tree.get_node(child.tag)
        if child_node is None or child_node.data is None:
            continue
        device = child_node.data.get("device", {})
        if device.get("type") == "DEVICE":
            return True
        if _has_device_descendant(tree, child.tag):
            return True
    return False
