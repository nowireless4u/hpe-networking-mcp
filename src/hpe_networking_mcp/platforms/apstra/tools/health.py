"""Apstra health and guideline tools."""

from __future__ import annotations

import time
from typing import Any

from fastmcp import Context
from fastmcp.server.dependencies import get_context

from hpe_networking_mcp.platforms.apstra import guidelines
from hpe_networking_mcp.platforms.apstra._registry import mcp
from hpe_networking_mcp.platforms.apstra.client import ApstraAuthError, ApstraClient
from hpe_networking_mcp.platforms.apstra.tools import READ_ONLY


@mcp.tool(annotations=READ_ONLY)
async def apstra_health(ctx: Context) -> dict[str, Any]:
    """Server health check for Apstra.

    Returns status plus a live login probe so operators can tell whether the
    credentials currently stored in Docker secrets are still valid. Returns a
    ``degraded`` status instead of raising when login fails so this tool
    always yields a result to the client.
    """
    lifespan_ctx = get_context().lifespan_context
    client: ApstraClient | None = lifespan_ctx.get("apstra_client")
    config = lifespan_ctx.get("apstra_config")

    info: dict[str, Any] = {
        "status": "healthy",
        "service": "apstra-mcp",
        "timestamp": time.time(),
    }

    if client is None or config is None:
        info["status"] = "degraded"
        info["apstra_connection"] = "unavailable (client not initialized)"
        return info

    info["server"] = client.server

    try:
        await client.health_check()
        info["apstra_connection"] = "OK"
    except ApstraAuthError as e:
        info["status"] = "degraded"
        info["apstra_connection"] = f"FAILED: {e}"
    except Exception as e:
        info["status"] = "degraded"
        info["apstra_connection"] = f"ERROR: {e}"

    return info


@mcp.tool(annotations=READ_ONLY)
async def apstra_formatting_guidelines(ctx: Context) -> str:
    """Return the full formatting guidelines for Apstra network-infrastructure output."""
    return guidelines.get_formatting_guidelines()
