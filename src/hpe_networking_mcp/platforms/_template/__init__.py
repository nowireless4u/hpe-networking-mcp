"""Template platform module — canonical scaffold for new platforms.

This module is intentionally not wired into ``server.py:create_server``,
so it never registers any tool at runtime. ``register_tools`` exists so
copies of this module work out of the box once the new platform is wired
into the server.

See ``README.md`` in this directory for the step-by-step copy procedure.
"""

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

# Map of category (sub-module name under ``tools/``) -> list of tool names
# registered by that module. Mirrors every other platform's pattern. The
# names here are illustrative only — replace with real tools when copying
# this template.
TOOLS: dict[str, list[str]] = {
    "example_read": [
        "template_get_example",
    ],
    "example_write": [
        "template_manage_example",
    ],
}


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Load template tool modules and register them with FastMCP.

    Always imports every category so the platform registry is fully
    populated; runtime write-gating is handled by the ``Visibility``
    transform (static mode) and ``is_tool_enabled`` (dynamic mode, via
    the meta-tools).

    Returns the count of individual underlying tools that registered.
    """
    from hpe_networking_mcp.platforms._common.meta_tools import build_meta_tools
    from hpe_networking_mcp.platforms._template import _registry

    _registry.mcp = mcp

    loaded: list[str] = []
    for category, tool_names in TOOLS.items():
        try:
            importlib.import_module(f"hpe_networking_mcp.platforms._template.tools.{category}")
            loaded.extend(tool_names)
            logger.debug("Template: loaded module {}", category)
        except Exception as e:
            logger.warning("Template: failed to load module {} -- {}", category, e)

    if config.tool_mode == "dynamic":
        build_meta_tools("_template", mcp)
        logger.info(
            "Template: {} underlying tools + 3 meta-tools registered (dynamic mode)",
            len(loaded),
        )
    else:
        logger.info("Template: {} tools registered (static mode)", len(loaded))

    return len(loaded)
