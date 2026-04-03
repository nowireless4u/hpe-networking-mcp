"""Aruba Central platform module."""

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Load and register all Central tool modules. Returns count of registered tools + prompts."""
    from hpe_networking_mcp.platforms.central import _registry

    _registry.mcp = mcp

    from hpe_networking_mcp.platforms.central.tools import (
        actions,
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
        switch_poe,
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
    switch_poe.register(mcp)
    applications.register(mcp)
    troubleshooting.register(mcp)
    actions.register(mcp)
    prompts.register(mcp)

    logger.info("Central: registered tools and prompts")
    return 38  # 37 tools + 10 prompts registered
