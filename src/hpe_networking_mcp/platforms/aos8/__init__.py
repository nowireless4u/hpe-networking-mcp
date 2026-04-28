"""Aruba OS 8 / Mobility Conductor platform module."""

from __future__ import annotations

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

TOOLS: dict[str, list[str]] = {}  # populated in Phase 3

__all__ = ["TOOLS", "register_tools"]


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Wire up the AOS8 platform.

    Phase 2: stub — sets the _registry.mcp holder so future tool-module imports
    work, but registers zero tools (tools/ is empty). Phase 3 will populate
    TOOLS and call build_meta_tools.

    Args:
        mcp: The FastMCP server instance to register tools with.
        config: Server configuration containing AOS8 secrets and tool mode.

    Returns:
        The number of underlying tools registered (0 in Phase 2).
    """
    from hpe_networking_mcp.platforms.aos8 import _registry

    _registry.mcp = mcp

    mode = config.tool_mode
    if mode == "dynamic":
        logger.info(
            "AOS8: 0 underlying tools registered (dynamic mode — meta-tools deferred until Phase 3)"
        )
    elif mode == "code":
        logger.info("AOS8: 0 underlying tools registered (code mode)")
    else:
        logger.info("AOS8: 0 tools registered (static mode)")
    return 0
