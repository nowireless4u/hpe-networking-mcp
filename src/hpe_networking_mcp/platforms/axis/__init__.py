"""Axis Atmos Cloud platform module.

Axis is shipped as a hidden platform: it auto-disables when its single
``axis_api_token`` secret is missing and stays unreferenced in any
public-facing documentation until the user chooses to announce it. See
the scratch directory's ``AXIS_ATMOS_INTEGRATION_PLAN.md`` for the full
plan.

Phase 1: scaffold + secret loader + health probe + 15 read tools.
Phase 2 (later) will add the manage/commit/regenerate write surface.
"""

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

# Map of category (tools/<name>.py) -> tool names registered by that module.
# Read-only tool files only in Phase 1. Phase 2 will add manage_* categories.
TOOLS: dict[str, list[str]] = {
    "application_groups": ["axis_get_application_groups"],
    "applications": ["axis_get_applications"],
    "connector_zones": ["axis_get_connector_zones"],
    "connectors": ["axis_get_connectors"],
    "groups": ["axis_get_groups"],
    "locations": ["axis_get_locations", "axis_get_sub_locations"],
    "ssl_exclusions": ["axis_get_ssl_exclusions"],
    "status": ["axis_get_status"],
    "tunnels": ["axis_get_tunnels"],
    "users": ["axis_get_users"],
    "web_categories": ["axis_get_web_categories"],
}

# Tools whose endpoints exist in the Axis swagger but currently return 403
# even when the token has read access — Axis appears to gate these
# server-side without a corresponding scope toggle in the admin portal
# (likely an unreleased / hidden API). Implementations stay on disk so
# re-enabling is a one-line move from this dict back into ``TOOLS`` when
# Axis flips them on.
_DISABLED_TOOLS: dict[str, list[str]] = {
    "custom_ip_categories": ["axis_get_custom_ip_categories"],
    "ip_feed_categories": ["axis_get_ip_feed_categories"],
}


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
    elif config.tool_mode == "code":
        logger.info("Axis: {} underlying tools registered (code mode)", len(loaded))
    else:
        logger.info("Axis: {} tools registered (static mode)", len(loaded))

    return len(loaded)
