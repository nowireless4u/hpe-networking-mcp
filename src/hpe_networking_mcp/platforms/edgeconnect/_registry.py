"""EdgeConnect tool registry — module-level FastMCP holder + shared-registry shim.

Generated tool modules under ``platforms/edgeconnect/tools/`` decorate their
functions with ``@tool(...)`` (imported from here). The decorator is produced by
the shared ``make_tool_decorator`` factory in ``_common.tool_registry`` — every
platform's ``_registry.py`` is identical except for the platform name.

Classify each tool with ``capability=`` (see ``docs/tool-annotation-rubric.md``);
that single classification derives the MCP annotations, the
``edgeconnect_write[_delete]`` enable tag, and the ``requires_confirmation``
gate tag. ``tags=`` is for functional/discovery tags only.
"""

from __future__ import annotations

from fastmcp import FastMCP

from hpe_networking_mcp.platforms._common.tool_registry import make_tool_decorator

# Set by ``platforms.edgeconnect.register_tools()`` before tool modules import.
mcp: FastMCP = None  # type: ignore[assignment]

tool = make_tool_decorator("edgeconnect", lambda: mcp)
