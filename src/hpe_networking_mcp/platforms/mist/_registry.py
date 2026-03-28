"""Mist tool registry -- holds the FastMCP instance that tools register against.

The ``mcp`` attribute is set by :func:`platforms.mist.register_tools` *before*
any tool module is imported, so that ``@mcp.tool()`` decorators work correctly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

# Set by platforms.mist.register_tools() before tool modules are imported
mcp: FastMCP = None  # type: ignore[assignment]
