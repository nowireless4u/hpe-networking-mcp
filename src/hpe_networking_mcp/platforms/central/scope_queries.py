"""Query helpers and Mermaid diagram generation for the Central scope tree.

Provides functions for querying effective (inherited) resources, collecting
devices within scopes, and rendering Mermaid flowchart diagrams.
"""

from __future__ import annotations

import re
from typing import Any

from treelib import Tree

from hpe_networking_mcp.platforms.central.scope_builder import (
    _get_device_info,
    _get_scope_name,
    classify_device,
)

# ---------------------------------------------------------------------------
# Effective resource collection
# ---------------------------------------------------------------------------


def get_effective_resources_for_node(
    tree: Tree,
    scope_id: str,
    persona: str | None = None,
    include_details: bool = False,
) -> list[dict]:
    """Collect effective (inherited + committed) resources for a given scope node.

    Walks from the node up to the root, collecting resources at each level.

    Args:
        tree: The scope tree.
        scope_id: Target scope node ID.
        persona: Optional persona filter.
        include_details: If True, include full resource configuration data.

    Returns:
        List of resource groups with origin tracking.
    """
    node = tree.get_node(scope_id)
    if node is None or node.data is None:
        return []
    device = node.data.get("device", {})

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
                entry: dict[str, Any] = {
                    "name": rn.tag,
                    "origin_scope_id": ancestor_device.get("scope_id"),
                    "origin_scope_name": origin_name,
                    "persona": p,
                    "has_details": rn.data is not None,
                }
                if include_details and rn.data is not None:
                    entry["details"] = rn.data
                effective[rn.tag].append(entry)
    return [{"name": k, "instances": v} for k, v in sorted(effective.items())]


def _collect_effective_for_node(tree: Tree, node_id: str, device: dict) -> list[dict]:
    """Collect effective (committed + inherited) resources for a single node.

    Internal helper used by tree_to_dict effective view. Delegates to
    get_effective_resources_for_node with the device's own persona.

    Args:
        tree: The scope tree.
        node_id: The node ID.
        device: The device data dict for this node.

    Returns:
        List of resource groups with origin tracking.
    """
    persona = device.get("persona")
    return get_effective_resources_for_node(tree, node_id, persona=persona)


def build_inheritance_path(tree: Tree, scope_id: str) -> list[dict]:
    """Build an ordered inheritance path from Global root down to the given scope.

    Args:
        tree: The scope tree.
        scope_id: Target scope node ID.

    Returns:
        List of dicts from root to target, each with scope_name, scope_type,
        and resource_count at that level.
    """
    path_ids = list(reversed(list(tree.rsearch(scope_id))))
    path: list[dict] = []
    for nid in path_ids:
        node = tree.get_node(nid)
        if node is None or node.data is None:
            continue
        device = node.data.get("device", {})
        res_tree: Tree | None = node.data.get("resources")
        resource_count = 0
        if res_tree is not None and res_tree.root is not None:
            for pn in res_tree.children(res_tree.root):
                resource_count += len(res_tree.children(pn.tag))
        path.append(
            {
                "scope_id": device.get("scope_id"),
                "scope_name": _get_scope_name(device),
                "scope_type": device.get("type", ""),
                "resource_count": resource_count,
            }
        )
    return path


# ---------------------------------------------------------------------------
# Device collection
# ---------------------------------------------------------------------------


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


def _get_node_class(
    node_type: str,
    device: dict,
) -> tuple[str, str]:
    """Return (short_label, css_class) for a Mermaid node.

    Args:
        node_type: The scope node type (GLOBAL, SITE, DEVICE, etc.).
        device: The device data dict for this node.

    Returns:
        Tuple of (display_label, css_class_name).
    """
    scope_name = _get_scope_name(device)
    if node_type == "DEVICE":
        meta = device.get("meta") or {}
        cat = classify_device(meta.get("device_type"))
        short = scope_name if scope_name and scope_name != "<UNKNOWN>" else (meta.get("device_model") or "Device")
        return short, cat.lower()
    if node_type == "GLOBAL":
        return scope_name, "global_scope"
    if node_type == "DEVICE_COLLECTION":
        return scope_name, "devgroup"
    if node_type == "SITE":
        return scope_name, "site"
    if node_type == "SITE_COLLECTION":
        return scope_name, "collection"
    return scope_name, "collection"


def _build_device_id_map(tree: Tree, root: str) -> dict[str, str]:
    """Pre-scan all DEVICE nodes and assign Mermaid IDs for device group linking.

    Args:
        tree: The scope tree.
        root: Root node ID to scan from.

    Returns:
        Dict mapping scope_id -> scope_name for all DEVICE nodes.
    """
    device_map: dict[str, str] = {}
    for node in tree.all_nodes():
        if node.data is None:
            continue
        device = node.data.get("device", {})
        if device.get("type") == "DEVICE":
            device_map[node.tag] = _get_scope_name(device)
    return device_map


def tree_to_mermaid(
    tree: Tree,
    scope_id: str | None = None,
    include_resources: bool = False,
    include_devices: bool = True,
) -> str:
    """Build a Mermaid flowchart with compact circle nodes and a legend.

    Hierarchy flow: Global -> Site Collections -> Sites -> Devices.
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
    class_assignments: dict[str, str] = {}
    _counter = {"n": 0}

    def next_id(prefix: str) -> str:
        _counter["n"] += 1
        return f"{prefix}{_counter['n']}"

    device_scope_to_mid: dict[str, str] = {}
    dev_groups: list[tuple[str, str]] = []

    def render_node(node_id: str, parent_mermaid_id: str | None) -> None:
        node = tree.get_node(node_id)
        if node is None or node.data is None:
            return
        device = node.data.get("device", {})
        node_type = device.get("type", "")

        is_device = node_type == "DEVICE"
        if is_device and not include_devices:
            return

        if node_type == "DEVICE_COLLECTION":
            label, css_class = _get_node_class(node_type, device)
            m_id = next_id("DG")
            lines.append(f"    {m_id}(({label}))")
            class_assignments[m_id] = css_class
            dev_groups.append((node_id, m_id))
            return

        label, css_class = _get_node_class(node_type, device)
        m_id = next_id("N")

        lines.append(f"    {m_id}(({label}))")
        if parent_mermaid_id:
            lines.append(f"    {parent_mermaid_id} --> {m_id}")
        class_assignments[m_id] = css_class

        if is_device:
            device_scope_to_mid[node_id] = m_id

        if include_resources and not is_device:
            _render_resource_nodes(node, m_id, lines, class_assignments, next_id)

        for child in tree.children(node_id):
            render_node(child.tag, m_id)

    render_node(root, None)

    _link_device_groups(tree, dev_groups, device_scope_to_mid, lines)
    _append_mermaid_styles(lines, class_assignments)

    return "\n".join(lines)


def _render_resource_nodes(
    node: Any,
    parent_mid: str,
    lines: list[str],
    class_assignments: dict[str, str],
    next_id_fn: Any,
) -> None:
    """Render resource nodes as small dashed links from a scope node."""
    res_tree: Tree | None = (node.data or {}).get("resources")
    if res_tree is None or res_tree.root is None:
        return
    for pn in res_tree.children(res_tree.root):
        for rn in res_tree.children(pn.tag):
            r_id = next_id_fn("R")
            short_res = rn.tag.split("/")[-1]
            lines.append(f"    {r_id}[/{short_res}/]")
            lines.append(f"    {parent_mid} -.-> {r_id}")
            class_assignments[r_id] = "resource"


def _link_device_groups(
    tree: Tree,
    dev_groups: list[tuple[str, str]],
    device_scope_to_mid: dict[str, str],
    lines: list[str],
) -> None:
    """Link device group nodes to their member devices via dashed lines."""
    for dg_nid, dg_mid in dev_groups:
        for child in tree.children(dg_nid):
            cn = tree.get_node(child.tag)
            if cn is None or cn.data is None:
                continue
            child_device = cn.data.get("device", {})
            if child_device.get("type") == "DEVICE":
                dev_mid = device_scope_to_mid.get(child.tag)
                if dev_mid:
                    lines.append(f"    {dg_mid} -.-> {dev_mid}")


def _append_mermaid_styles(lines: list[str], class_assignments: dict[str, str]) -> None:
    """Append Mermaid class definitions, class assignments, and legend."""
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

    for m_id, cls in class_assignments.items():
        lines.append(f"    class {m_id} {cls}")

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
