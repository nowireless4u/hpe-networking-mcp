"""Axis Atmos Cloud platform module.

Axis is shipped as a hidden platform: it auto-disables when its single
``axis_api_token`` secret is missing and stays unreferenced in any
public-facing documentation until the user chooses to announce it. See
the scratch directory's ``AXIS_ATMOS_INTEGRATION_PLAN.md`` for the full
plan.

Phase 1 (this PR): scaffold + secret loader + health probe. ``TOOLS``
intentionally empty — the read/write surfaces land in subsequent waves.
"""

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

# Map of category (tools/<name>.py) -> tool names registered by that module.
# Empty in Phase 1; populated as read tools (Wave 3) and write tools (Phase 2)
# land. Mirrors every other platform's pattern.
TOOLS: dict[str, list[str]] = {}


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Load Axis tool modules and register them with FastMCP.

    Always imports every category so the platform registry is fully
    populated; runtime write-gating is handled by the ``Visibility``
    transform (static mode) and ``is_tool_enabled`` (dynamic mode, via
    the meta-tools).

    Returns the count of individual underlying tools that registered.
    """
    from hpe_networking_mcp.platforms._common.meta_tools import build_meta_tools
    from hpe_networking_mcp.platforms.axis import _registry

    _registry.mcp = mcp

    loaded: list[str] = []
    for category, tool_names in TOOLS.items():
        try:
            importlib.import_module(f"hpe_networking_mcp.platforms.axis.tools.{category}")
            loaded.extend(tool_names)
            logger.debug("Axis: loaded module {}", category)
        except Exception as e:
            logger.warning("Axis: failed to load module {} -- {}", category, e)

    if config.tool_mode == "dynamic":
        build_meta_tools("axis", mcp)
        logger.info(
            "Axis: {} underlying tools + 3 meta-tools registered (dynamic mode)",
            len(loaded),
        )
    else:
        logger.info("Axis: {} tools registered (static mode)", len(loaded))

    return len(loaded)
