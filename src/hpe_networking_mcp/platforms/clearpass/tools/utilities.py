"""ClearPass utility tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if type == "mpsk":
            return await client.request("get", "/random-mpsk")
        return await client.request("get", "/random-password")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error generating random password: {e}"}) from e
