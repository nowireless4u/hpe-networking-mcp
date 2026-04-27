"""Axis Atmos Cloud platform module.

Wraps the Axis Atmos Admin API at
``https://admin-api.axissecurity.com/api/v1.0`` for SASE / cloud-edge
management — connectors, tunnels, locations, identity, applications,
web-category and SSL-exclusion policy. Auto-disables when the
``axis_api_token`` secret is missing or empty.

Reads carry no write tag; writes carry ``axis_write_delete`` so the
visibility transform + elicitation middleware gate them on
``ENABLE_AXIS_WRITE_TOOLS=true``. Every ``axis_manage_*`` write stages —
the caller invokes ``axis_commit_changes`` to apply pending edits,
matching the workflow Axis enforces for changes made through the admin
UI.
"""

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

# Map of category (tools/<name>.py) -> tool names registered by that module.
TOOLS: dict[str, list[str]] = {
    # ── Read-only categories ──────────────────────────────────────
    "application_groups": ["axis_get_application_groups", "axis_manage_application_group"],
    "applications": ["axis_get_applications", "axis_manage_application"],
    "connector_zones": ["axis_get_connector_zones", "axis_manage_connector_zone"],
    "connectors": [
        "axis_get_connectors",
        "axis_manage_connector",
        "axis_regenerate_connector",
    ],
    "groups": ["axis_get_groups", "axis_manage_group"],
    "locations": [
        "axis_get_locations",
        "axis_get_sub_locations",
        "axis_manage_location",
        "axis_manage_sub_location",
    ],
    "ssl_exclusions": ["axis_get_ssl_exclusions", "axis_manage_ssl_exclusion"],
    "status": ["axis_get_status"],
    "tunnels": ["axis_get_tunnels", "axis_manage_tunnel"],
    "users": ["axis_get_users", "axis_manage_user"],
    "web_categories": ["axis_get_web_categories", "axis_manage_web_category"],
    # ── Commit (Axis writes stage; this applies them) ─────────────
    "commit": ["axis_commit_changes"],
}

# Tools whose endpoints exist in the Axis swagger but currently return 403
# even when the token has read/write access — Axis appears to gate these
# server-side without a corresponding scope toggle in the admin portal
# (likely an unreleased / hidden API). Implementations stay on disk so
# re-enabling is a one-line move from this dict back into ``TOOLS`` when
# Axis flips them on.
_DISABLED_TOOLS: dict[str, list[str]] = {
    "custom_ip_categories": ["axis_get_custom_ip_categories", "axis_manage_custom_ip_category"],
    "ip_feed_categories": ["axis_get_ip_feed_categories", "axis_manage_ip_feed_category"],
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
