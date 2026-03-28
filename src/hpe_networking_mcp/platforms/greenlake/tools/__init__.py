"""GreenLake tools package.

Imports tool modules so their ``@mcp.tool()`` decorators fire, then
exposes a single ``register_all`` entry-point used by the platform init.

Supports two modes controlled by the ``mode`` parameter:
- ``static``  (default) -- register the 10 dedicated per-endpoint tools
- ``dynamic`` -- register the 3 meta-tools (list, schema, invoke)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from fastmcp import FastMCP


def _register_static(mcp: FastMCP) -> int:
    """Import the 5 static tool modules (2 tools each = 10 total)."""
    from hpe_networking_mcp.platforms.greenlake.tools import (  # noqa: F401
        audit_logs,
        devices,
        subscriptions,
        users,
        workspaces,
    )

    return 10


def _register_dynamic(mcp: FastMCP) -> int:
    """Import the dynamic meta-tools module (3 tools)."""
    from hpe_networking_mcp.platforms.greenlake.tools import dynamic  # noqa: F401

    return 3


def register_all(mcp: FastMCP, mode: str = "static") -> int:
    """Import tool modules (triggering ``@mcp.tool()`` registration).

    Args:
        mcp: The FastMCP server instance (already set on ``_registry``).
        mode: ``"static"`` for 10 dedicated tools, ``"dynamic"`` for 3 meta-tools.

    Returns:
        The total number of tools registered.
    """
    mode = mode.lower().strip()

    if mode == "dynamic":
        logger.info("GreenLake: registering dynamic meta-tools (3 tools)")
        return _register_dynamic(mcp)
    elif mode == "static":
        logger.info("GreenLake: registering static tools (10 tools)")
        return _register_static(mcp)
    else:
        logger.warning(
            "GreenLake: unknown MCP_TOOL_MODE '{}', falling back to static", mode
        )
        return _register_static(mcp)
