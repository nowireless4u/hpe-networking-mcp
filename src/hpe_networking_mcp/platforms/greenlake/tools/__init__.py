"""GreenLake tools package.

Imports all tool modules so their ``@mcp.tool()`` decorators fire, then
exposes a single ``register_all`` entry-point used by the platform init.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_all(mcp: FastMCP) -> int:
    """Import every tool module (triggering ``@mcp.tool()`` registration).

    Returns the total number of tools registered.
    """
    # Importing the modules is sufficient -- each module decorates its
    # functions with ``@mcp.tool()`` at import time.
    from hpe_networking_mcp.platforms.greenlake.tools import (  # noqa: F401
        audit_logs,
        devices,
        subscriptions,
        users,
        workspaces,
    )

    # 2 tools per service * 5 services = 10
    return 10
