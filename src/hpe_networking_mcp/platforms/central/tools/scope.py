"""Aruba Central scope/configuration tree tools.

Provides 6 read-only tools for inspecting the Central scope hierarchy,
configuration resources, committed config at a scope, effective
(inherited) config, devices within scopes, and Mermaid diagram
generation.

Error contract (v3.2.0.1+): every public tool raises
``fastmcp.exceptions.ToolError`` with a structured payload
(``{"status_code": <HTTP-style int>, "message": "..."}``) on failure.
This replaces the older "return error string" pattern from v2.2.0.1
— the change is safe in code mode because
``SandboxErrorCatchMiddleware`` catches the raise and re-raises with
readable text. See CLAUDE.md "Tool error contract" section for the
project-wide pattern + status-code domain.
"""

from typing import Literal

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.scope_builder import (
    build_scope_tree,
    tree_to_dict,
)
from hpe_networking_mcp.platforms.central.scope_queries import (
    build_inheritance_path,
    get_devices_in_scope,
    get_effective_resources_for_node,
    tree_to_mermaid,
)
from hpe_networking_mcp.platforms.central.utils import get_central_conn


@tool(capability=Capability.READ)
async def central_get_scope_tree(
    ctx: Context,
    view: Literal["committed", "effective"] = "committed",
) -> dict | list:
    """
    Get the full Aruba Central scope/configuration hierarchy as a tree.

    The "committed" view shows the tree with resources as they are directly
    assigned at each scope level. The "effective" view adds inherited
    resources from parent scopes at every node.

    Parameters:
        view: Tree view mode -- "committed" (default) or "effective".

    Returns:
        Hierarchical dict with scope_id, scope_name, type, personas
        (resources), and children at each level. Device leaf nodes
        include device_info and persona fields.
    """
    conn = get_central_conn(ctx)
    try:
        tree = await build_scope_tree(conn)
        return tree_to_dict(tree, effective=(view == "effective"))
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error building scope tree: {e}"}) from e


@tool(capability=Capability.READ)
async def central_get_scope_resources(
    ctx: Context,
    scope_id: str,
    persona: str | None = None,
    include_details: bool = False,
) -> dict:
    """
    Get the configuration resources directly assigned to a specific scope node.

    Returns the personas and their resources committed at the given scope.
    This does NOT include inherited resources from parent scopes -- use
    central_get_effective_config for that.

    Parameters:
        scope_id: The scope ID to look up (e.g. a UUID from the scope tree).
        persona: Optional persona filter (e.g. "access_point", "switch").
        include_details: If True, include full resource configuration data.

    Returns:
        Dict with scope_id, scope_name, type, and a personas list. Each
        persona has a name and list of resources with name and has_details.
    """
    conn = get_central_conn(ctx)
    try:
        tree = await build_scope_tree(conn)
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error building scope tree: {e}"}) from e

    node = tree.get_node(scope_id)
    if node is None or node.data is None:
        raise ToolError(
            {
                "status_code": 404,
                "message": (
                    f"Scope {scope_id!r} not found in the tree. Use central_get_scope_tree to list valid scope IDs."
                ),
            }
        )

    device = node.data.get("device", {})
    resources_tree = node.data.get("resources")

    personas: list[dict] = []
    if resources_tree is not None and resources_tree.root is not None:
        for persona_node in sorted(resources_tree.children(resources_tree.root), key=lambda n: n.tag):
            if persona and persona_node.tag != persona:
                continue
            resource_nodes = resources_tree.children(persona_node.tag)
            resources = []
            for rn in resource_nodes:
                entry: dict = {"name": rn.tag, "has_details": rn.data is not None}
                if include_details and rn.data is not None:
                    entry["details"] = rn.data
                resources.append(entry)
            if resources:
                personas.append({"name": persona_node.tag, "resources": resources})

    meta = device.get("meta") or {}
    return {
        "scope_id": device.get("scope_id"),
        "scope_name": meta.get("scope_name", scope_id),
        "type": device.get("type", ""),
        "personas": personas,
    }


@tool(capability=Capability.READ)
async def central_get_committed_config(
    ctx: Context,
    scope_id: str,
    persona: str | None = None,
    include_details: bool = True,
) -> dict:
    """
    Get the configuration committed directly at a scope node (no inheritance).

    The "committed" view shows what was assigned AT this scope — it does
    NOT roll up parent-scope inheritance. Use
    :func:`central_get_effective_config` for the inherited rollup
    (committed + everything inherited from ancestors).

    Returns the same per-resource shape ``effective_resources`` uses so
    the two views are directly diff-able side by side: when an operator
    asks "what did the parent contribute vs what was added here?", call
    both and compare ``committed_resources`` to ``effective_resources``.

    Parameters:
        scope_id: The scope ID to query.
        persona: Optional persona filter (e.g. ``"CAMPUS_AP"``,
            ``"ACCESS_SWITCH"``, ``"BRANCH_GW"``). Omit for all
            personas committed at this scope.
        include_details: When True (default) include each resource's
            full configuration data. Set False for a name-only summary
            useful when the operator only wants the inventory.

    Returns:
        Dict with ``scope_id``, ``scope_name``, ``type``, ``scope_path``
        (Global → ... → this scope, useful when comparing to
        ``effective_resources``' ``inheritance_path``), and
        ``committed_resources`` — a flat list of
        ``{persona, name, has_details, details?}`` entries. Empty list
        when nothing is committed at this scope (a normal case for
        intermediate site-collection nodes that exist purely as
        organizational containers).
    """
    conn = get_central_conn(ctx)
    try:
        tree = await build_scope_tree(conn)
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error building scope tree: {e}"}) from e

    node = tree.get_node(scope_id)
    if node is None or node.data is None:
        raise ToolError(
            {
                "status_code": 404,
                "message": (
                    f"Scope {scope_id!r} not found in the tree. Use central_get_scope_tree to list valid scope IDs."
                ),
            }
        )

    device = node.data.get("device", {})
    resources_tree = node.data.get("resources")
    meta = device.get("meta") or {}

    committed: list[dict] = []
    if resources_tree is not None and resources_tree.root is not None:
        for persona_node in sorted(resources_tree.children(resources_tree.root), key=lambda n: n.tag):
            if persona and persona_node.tag != persona:
                continue
            for rn in resources_tree.children(persona_node.tag):
                entry: dict = {
                    "persona": persona_node.tag,
                    "name": rn.tag,
                    "has_details": rn.data is not None,
                }
                if include_details and rn.data is not None:
                    entry["details"] = rn.data
                committed.append(entry)

    return {
        "scope_id": device.get("scope_id"),
        "scope_name": meta.get("scope_name", scope_id),
        "type": device.get("type", ""),
        "scope_path": build_inheritance_path(tree, scope_id),
        "committed_resources": committed,
    }


@tool(capability=Capability.READ)
async def central_get_effective_config(
    ctx: Context,
    scope_id: str,
    persona: str | None = None,
    include_details: bool = False,
) -> dict:
    """
    Get the effective (inherited + committed) configuration for a scope node.

    Walks from the given scope up to the global root, collecting all
    resources at each ancestor. Resources are grouped by name with
    origin tracking so you can see where each config element comes from.

    Parameters:
        scope_id: The scope ID to query.
        persona: Optional persona filter (e.g. "access_point", "switch").
        include_details: If True, include full resource configuration data.

    Returns:
        Dict with scope_id, scope_name, inheritance_path (ordered from
        Global root to this scope), and effective_resources list. Each
        resource group has a name and list of instances showing
        origin_scope_id, origin_scope_name, persona, and has_details.
    """
    conn = get_central_conn(ctx)
    try:
        tree = await build_scope_tree(conn)
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error building scope tree: {e}"}) from e

    node = tree.get_node(scope_id)
    if node is None or node.data is None:
        raise ToolError(
            {
                "status_code": 404,
                "message": (
                    f"Scope {scope_id!r} not found in the tree. Use central_get_scope_tree to list valid scope IDs."
                ),
            }
        )

    device = node.data.get("device", {})
    meta = device.get("meta") or {}
    effective = get_effective_resources_for_node(tree, scope_id, persona, include_details)
    path = build_inheritance_path(tree, scope_id)

    return {
        "scope_id": device.get("scope_id"),
        "scope_name": meta.get("scope_name", scope_id),
        "type": device.get("type", ""),
        "inheritance_path": path,
        "effective_resources": effective,
    }


@tool(capability=Capability.READ)
async def central_get_devices_in_scope(
    ctx: Context,
    scope_id: str,
    device_type: str | None = None,
) -> dict:
    """
    List all devices under a given scope (including nested sub-scopes).

    Recursively collects all DEVICE nodes beneath the specified scope.
    Each device includes classification (AP, SWITCH, GATEWAY, OTHER),
    serial number, model, MAC address, and persona.

    Parameters:
        scope_id: The scope ID to search under.
        device_type: Optional filter -- "AP", "SWITCH", "GATEWAY", or "OTHER".

    Returns:
        Dict with scope_id and a devices list. Each device has scope_id,
        scope_name, category, persona, device_type, device_model,
        serial_number, mac_address, and part_number.
    """
    conn = get_central_conn(ctx)
    try:
        tree = await build_scope_tree(conn)
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error building scope tree: {e}"}) from e

    node = tree.get_node(scope_id)
    if node is None:
        raise ToolError(
            {
                "status_code": 404,
                "message": (
                    f"Scope {scope_id!r} not found in the tree. Use central_get_scope_tree to list valid scope IDs."
                ),
            }
        )

    devices = get_devices_in_scope(tree, scope_id, device_type)
    return {
        "scope_id": scope_id,
        "device_count": len(devices),
        "devices": devices,
    }


@tool(capability=Capability.READ)
async def central_get_scope_diagram(
    ctx: Context,
    scope_id: str | None = None,
    include_resources: bool = False,
    include_devices: bool = True,
) -> str:
    """
    Generate a Mermaid flowchart diagram of the scope hierarchy.

    Produces a Mermaid-formatted string that can be rendered in any
    Mermaid-compatible viewer. Nodes are color-coded by type:
    Global (grey), Collection (green), Site (orange), AP (blue),
    Switch (purple), Gateway (red), Other (blue-grey).

    Parameters:
        scope_id: Optional scope ID to render a subtree. If omitted, renders the full tree.
        include_resources: If True, show configuration resource nodes (dashed edges).
        include_devices: If True (default), show device leaf nodes.

    Returns:
        Mermaid flowchart string ready for rendering.
    """
    conn = get_central_conn(ctx)
    try:
        tree = await build_scope_tree(conn)
        return tree_to_mermaid(tree, scope_id, include_resources, include_devices)
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error generating scope diagram: {e}"}) from e
