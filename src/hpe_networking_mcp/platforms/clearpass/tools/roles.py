"""ClearPass role and role mapping read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client
from hpe_networking_mcp.platforms.clearpass.utils import clearpass_get


@tool(capability=Capability.READ)
async def clearpass_get_roles(
    ctx: Context,
    role_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass roles used in enforcement and authorization policies.

    If role_id or name is provided, returns a single role.
    Otherwise returns a paginated list of all roles.

    Args:
        role_id: Numeric ID for single-item lookup.
        name: Role name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if role_id:
            return await client.request("get", f"/role/{role_id}")
        if name:
            return await client.request("get", f"/role/name/{name}")
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
            f"calculate_count={'true' if calculate_count else 'false'}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return await clearpass_get(client, "/role" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching roles: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_role_mappings(
    ctx: Context,
    role_mapping_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass role mapping policies.

    Role mappings define how attributes from authentication sources are
    mapped to ClearPass roles for authorization decisions.

    If role_mapping_id or name is provided, returns a single mapping.
    Otherwise returns a paginated list of all role mappings.

    Args:
        role_mapping_id: Numeric ID for single-item lookup.
        name: Role mapping name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if role_mapping_id:
            return await client.request("get", f"/role-mapping/{role_mapping_id}")
        if name:
            return await client.request("get", f"/role-mapping/name/{name}")
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
            f"calculate_count={'true' if calculate_count else 'false'}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return await clearpass_get(client, "/role-mapping" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching role mappings: {e}"}) from e
