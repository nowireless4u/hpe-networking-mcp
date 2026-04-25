"""HPE GreenLake platform module.

Consolidates the five original per-service MCP servers (audit-logs, devices,
subscriptions, users, workspaces) into a single platform module, aligned with
the shared dynamic-mode infrastructure used by Apstra, Mist, Central, and
ClearPass.
"""

from __future__ import annotations

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig
from hpe_networking_mcp.platforms.greenlake.tools import TOOLS


def register_tools(mcp_instance: FastMCP, config: ServerConfig) -> int:
    """Load all GreenLake tool modules and register them with FastMCP.

    Always imports every category so ``REGISTRIES["greenlake"]`` is fully
    populated; runtime gating (if GreenLake ever grows write tools) would go
    through the shared Visibility transform in static mode or
    ``is_tool_enabled`` in dynamic mode.

    Returns the count of individual underlying tools that registered.
    """
    from hpe_networking_mcp.platforms._common.meta_tools import build_meta_tools
    from hpe_networking_mcp.platforms.greenlake import _registry

    _registry.mcp = mcp_instance

    loaded: list[str] = []
    for category, tool_names in TOOLS.items():
        try:
            importlib.import_module(f"hpe_networking_mcp.platforms.greenlake.tools.{category}")
            loaded.extend(tool_names)
            logger.debug("GreenLake: loaded module {}", category)
        except Exception as e:
            logger.warning("GreenLake: failed to load module {} -- {}", category, e)

    if config.tool_mode == "dynamic":
        build_meta_tools("greenlake", mcp_instance)
        logger.info(
            "GreenLake: {} underlying tools + 3 meta-tools registered (dynamic mode)",
            len(loaded),
        )
    elif config.tool_mode == "code":
        logger.info("GreenLake: {} underlying tools registered (code mode)", len(loaded))
    else:
        logger.info("GreenLake: {} tools registered (static mode)", len(loaded))

    return len(loaded)
