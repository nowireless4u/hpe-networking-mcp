"""Aruba Central platform module."""

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Load and register all Central tool modules. Returns count of registered tools + prompts."""
    from hpe_networking_mcp.platforms.central import _registry

    _registry.mcp = mcp

    from hpe_networking_mcp.platforms.central.tools import (
        alerts,
        applications,
        audit_logs,
        clients,
        devices,
        events,
        monitoring,
        prompts,
        sites,
        stats,
        troubleshooting,
        wlans,
    )

    sites.register(mcp)
    devices.register(mcp)
    clients.register(mcp)
    alerts.register(mcp)
    events.register(mcp)
    monitoring.register(mcp)
    wlans.register(mcp)
    audit_logs.register(mcp)
    stats.register(mcp)
    applications.register(mcp)
    troubleshooting.register(mcp)
    prompts.register(mcp)

    logger.info("Central: registered tools and prompts")
    return 27  # 26 tools + 11 prompts registered
