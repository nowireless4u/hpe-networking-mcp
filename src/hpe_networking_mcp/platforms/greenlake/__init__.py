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

    # Register static tools for all 5 services
    from hpe_networking_mcp.platforms.greenlake.tools import register_all

    count = register_all(mcp_instance)
    logger.info("GreenLake: registered {} tools", count)
    return count
