"""ClearPass utility tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def clearpass_generate_random_password(
    ctx: Context,
    type: str = "password",
) -> dict | str:
    """Generate a random password or MPSK using ClearPass.

    Uses ClearPass server-side random generation for cryptographically
    secure passwords or Multi Pre-Shared Keys (MPSKs).

    Args:
        type: Type of random string to generate. Either "password" or "mpsk".
    """
    try:
        from pyclearpass.api_toolsandutilities import ApiToolsAndUtilities

        client = await get_clearpass_session(ApiToolsAndUtilities)
        if type == "mpsk":
            return client.get_random_mpsk()
        return client.get_random_password()
    except Exception as e:
        return f"Error generating random password: {e}"
