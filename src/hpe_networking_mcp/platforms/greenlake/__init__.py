"""HPE GreenLake platform module.

Consolidates the five original per-service MCP servers (audit-logs, devices,
subscriptions, users, workspaces) into a single platform module.
"""

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig


def register_tools(mcp_instance: FastMCP, config: ServerConfig) -> int:
    """Load and register all GreenLake tool modules. Returns count of registered tools."""
    from hpe_networking_mcp.platforms.greenlake import _registry

    _registry.mcp = mcp_instance

    # Determine tool mode from config
    mode = config.greenlake_tool_mode

    # Register tools using the selected mode
    from hpe_networking_mcp.platforms.greenlake.tools import register_all

    count = register_all(mcp_instance, mode=mode)
    logger.info("GreenLake: registered {} tools (mode={})", count, mode)
    return count
