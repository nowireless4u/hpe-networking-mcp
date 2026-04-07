"""Aruba Central scope/configuration tree tools.

Provides 5 read-only tools for inspecting the Central scope hierarchy,
configuration resources, effective (inherited) config, devices within
scopes, and Mermaid diagram generation.
"""

from typing import Literal

from fastmcp import Context

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
from hpe_networking_mcp.platforms.central.tools import READ_ONLY


def register(mcp):
    """Register all Central scope tools on the given FastMCP instance."""

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_scope_tree(
        ctx: Context,
        view: Literal["committed", "effective"] = "committed",
    ) -> dict | list | str:
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
        conn = ctx.lifespan_context["central_conn"]
        try:
            tree = build_scope_tree(conn)
            return tree_to_dict(tree, effective=(view == "effective"))
        except Exception as e:
            return f"Error building scope tree: {e}"

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_scope_resources(
        ctx: Context,
        scope_id: str,
        persona: str | None = None,
        include_details: bool = False,
    ) -> dict | str:
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
        conn = ctx.lifespan_context["central_conn"]
        try:
            tree = build_scope_tree(conn)
        except Exception as e:
            return f"Error building scope tree: {e}"

        node = tree.get_node(scope_id)
        if node is None or node.data is None:
            return f"Scope '{scope_id}' not found in the tree. Use central_get_scope_tree to list valid scope IDs."

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

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_effective_config(
        ctx: Context,
        scope_id: str,
        persona: str | None = None,
        include_details: bool = False,
    ) -> dict | str:
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
        conn = ctx.lifespan_context["central_conn"]
        try:
            tree = build_scope_tree(conn)
        except Exception as e:
            return f"Error building scope tree: {e}"

        node = tree.get_node(scope_id)
        if node is None or node.data is None:
            return f"Scope '{scope_id}' not found in the tree. Use central_get_scope_tree to list valid scope IDs."

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

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_devices_in_scope(
        ctx: Context,
        scope_id: str,
        device_type: str | None = None,
    ) -> dict | str:
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
        conn = ctx.lifespan_context["central_conn"]
        try:
            tree = build_scope_tree(conn)
        except Exception as e:
            return f"Error building scope tree: {e}"

        node = tree.get_node(scope_id)
        if node is None:
            return f"Scope '{scope_id}' not found in the tree. Use central_get_scope_tree to list valid scope IDs."

        devices = get_devices_in_scope(tree, scope_id, device_type)
        return {
            "scope_id": scope_id,
            "device_count": len(devices),
            "devices": devices,
        }

    @mcp.tool(annotations=READ_ONLY)
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
        conn = ctx.lifespan_context["central_conn"]
        try:
            tree = build_scope_tree(conn)
            return tree_to_mermaid(tree, scope_id, include_resources, include_devices)
        except Exception as e:
            return f"Error generating scope diagram: {e}"
