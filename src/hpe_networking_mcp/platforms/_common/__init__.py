"""Shared infrastructure for the dynamic tool-mode refactor (v2.0, #157).

Modules:
    tool_registry  — ``ToolSpec``, ``REGISTRIES``, ``record_tool``,
                     ``is_tool_enabled``, ``clear_registry``.
    meta_tools     — ``build_meta_tools(platform, mcp, registry)`` factory
                     that returns ``<platform>_list_tools`` /
                     ``<platform>_get_tool_schema`` /
                     ``<platform>_invoke_tool``.

The goal: keep the single-PR blast radius small for the per-platform
migration PRs (Phases 1-3, 5). The registry and meta-tool factory are
added here once; each platform then swaps its ``@mcp.tool(...)`` decorators
for the thin ``tool()`` shim in its ``_registry.py`` and gains three
meta-tools for free.
"""
