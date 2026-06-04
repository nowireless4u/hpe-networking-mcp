"""Template tool registry — module-level FastMCP holder + shared-registry shim.

Tool modules under ``platforms/_template/tools/`` decorate their functions with
``@tool(...)`` (imported from here) instead of directly with ``@mcp.tool(...)``.

The decorator is produced by the shared ``make_tool_decorator`` factory in
``_common.tool_registry`` — every platform's ``_registry.py`` is identical
except for the platform name. To stand up a new platform, copy this file and
change ``"_template"`` to your platform key.

The shim:

1. Records a ``ToolSpec`` in the shared registry (for dynamic-mode dispatch).
2. Delegates to ``mcp.tool(...)`` so the tool is registered with the server.
3. Merges the ``dynamic_managed`` + platform tags so the Visibility transform
   in ``server.py`` can hide the individual tools in dynamic mode.

Classify each tool with ``capability=`` (see ``docs/tool-annotation-rubric.md``);
that single classification derives the MCP annotations, the
``<platform>_write[_delete]`` enable tag, and the ``requires_confirmation``
gate tag. ``tags=`` is for functional/discovery tags only.
"""

from __future__ import annotations

from fastmcp import FastMCP

from hpe_networking_mcp.platforms._common.tool_registry import make_tool_decorator

# Set by ``platforms._template.register_tools()`` before tool modules are imported.
mcp: FastMCP = None  # type: ignore[assignment]

tool = make_tool_decorator("_template", lambda: mcp)
