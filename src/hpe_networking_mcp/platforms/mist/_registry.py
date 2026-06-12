"""Mist tool registry — module-level FastMCP holder + shared-registry shim.

Generated tool modules under ``platforms/mist/tools/`` decorate their
functions with ``@tool(...)`` (imported from here as ``_mcp_tool``). The shim
is built by the shared ``make_tool_decorator`` factory — see
``platforms/_template/_registry.py`` for the canonical reference and
``docs/tool-annotation-rubric.md`` for how ``capability=`` classifies a tool.
"""

from __future__ import annotations

from fastmcp import FastMCP

from hpe_networking_mcp.platforms._common.tool_registry import make_tool_decorator

# Set by ``platforms.mist.register_tools()`` before tool modules are imported.
mcp: FastMCP = None  # type: ignore[assignment]

tool = make_tool_decorator("mist", lambda: mcp)
