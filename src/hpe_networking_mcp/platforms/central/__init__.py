"""Aruba Central platform module."""

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Load and register all Central tool modules. Returns count of registered tools + prompts."""
    from hpe_networking_mcp.platforms.central import _registry

    _registry.mcp = mcp

    from hpe_networking_mcp.platforms.central.tools import (
        sites,
        devices,
        clients,
        alerts,
        events,
        prompts,
    )

    sites.register(mcp)
    devices.register(mcp)
    clients.register(mcp)
    alerts.register(mcp)
    events.register(mcp)
    prompts.register(mcp)

    logger.info("Central: registered tools and prompts")
    return 10  # number of tools + prompts registered
