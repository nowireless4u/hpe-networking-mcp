"""ClearPass role and role mapping read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def clearpass_get_roles(
    ctx: Context,
    role_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
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
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if role_id:
            return client.get_role_by_role_id(role_id=role_id)
        if name:
            return client.get_role_name_by_name(name=name)
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return client._send_request("/role" + query, "get")
    except Exception as e:
        return f"Error fetching roles: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_role_mappings(
    ctx: Context,
    role_mapping_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
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
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if role_mapping_id:
            return client.get_role_mapping_by_role_mapping_id(role_mapping_id=role_mapping_id)
        if name:
            return client.get_role_mapping_name_by_name(name=name)
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return client._send_request("/role-mapping" + query, "get")
    except Exception as e:
        return f"Error fetching role mappings: {e}"
