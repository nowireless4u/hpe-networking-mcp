"""Juniper Mist platform module.

Spec-driven since v3.1.0.0 (issue #304). The 35 hand-curated tools that
shipped through v3.0.1.15 have been replaced by ~1000 tools generated
from the vendored Mist OpenAPI spec at ``vendor/mist_openapi.json``.
Each generated tool follows our ``mist_<snake_case_operationId>``
naming convention and calls into ``_client.mist_request`` for transport.

Regenerate the tool surface from the current vendored spec via:

    uv run python scripts/regenerate_mist_tools.py

The vendored spec auto-syncs daily via
``.github/workflows/sync-mist-openapi.yml``. Tool regeneration is a
deliberate release-time step so the maintainer reviews the tool diff
before tagging.
"""

from __future__ import annotations

import importlib
import pkgutil

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Load every generated Mist tool module and register them with FastMCP.

    Walks ``platforms.mist.tools`` and imports each ``<tag>.py`` submodule;
    the ``@_mcp_tool(...)`` decorators in each module record the tool with
    FastMCP via the shared ``_registry.tool`` shim.

    Returns the count of underlying tools that registered (does not
    include the 3 meta-tools).
    """
    from hpe_networking_mcp.platforms._common.meta_tools import build_meta_tools
    from hpe_networking_mcp.platforms.mist import _registry
    from hpe_networking_mcp.platforms.mist import tools as tools_pkg

    _registry.mcp = mcp

    loaded: list[str] = []
    for _finder, modname, _ispkg in pkgutil.iter_modules(tools_pkg.__path__):
        if modname.startswith("_"):
            continue
        full_path = f"{tools_pkg.__name__}.{modname}"
        try:
            importlib.import_module(full_path)
            loaded.append(modname)
        except Exception as exc:
            logger.warning("Mist: failed to load tool module {} -- {}", modname, exc)

    # Meta-tools are always registered (issue #302). In code mode they're
    # reachable via ``await call_tool("mist_list_tools", ...)`` from inside
    # ``execute()`` even though they're hidden from the top-level catalog.
    build_meta_tools("mist", mcp)
    logger.info(
        "Mist: registered {} generated tool module(s) + 3 meta-tools ({} mode)",
        len(loaded),
        config.tool_mode,
    )

    return len(loaded)
