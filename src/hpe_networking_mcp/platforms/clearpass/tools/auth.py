"""ClearPass authentication source and method read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def clearpass_get_auth_sources(
    ctx: Context,
    auth_source_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
) -> dict | str:
    """Get ClearPass authentication sources (AD, LDAP, SQL, local DB, etc.).

    If auth_source_id or name is provided, returns a single auth source.
    Otherwise returns a paginated list of all authentication sources.

    Args:
        auth_source_id: Numeric ID for single-item lookup.
        name: Auth source name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if auth_source_id:
            return client.get_auth_source_by_auth_source_id(auth_source_id=auth_source_id)
        if name:
            return client.get_auth_source_name_by_name(name=name)
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return client._send_request("/auth-source" + query, "get")
    except Exception as e:
        return f"Error fetching auth sources: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_auth_source_status(
    ctx: Context,
    auth_source_id: str,
) -> dict | str:
    """Get the configuration details of a ClearPass authentication source.

    Returns the full auth source record including type, server addresses,
    connection settings, and attribute mappings for status review.

    Args:
        auth_source_id: Numeric ID of the authentication source.
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        return client.get_auth_source_by_auth_source_id(auth_source_id=auth_source_id)
    except Exception as e:
        return f"Error fetching auth source status: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_test_auth_source(
    ctx: Context,
    auth_source_id: str,
) -> dict | str:
    """Retrieve an authentication source record for connectivity review.

    Returns the auth source configuration. Actual connectivity testing
    (e.g. LDAP bind test, AD domain join check) requires ClearPass
    server-side capabilities not available via the REST API.

    Args:
        auth_source_id: Numeric ID of the authentication source to test.
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        result = client.get_auth_source_by_auth_source_id(auth_source_id=auth_source_id)
        return {
            "auth_source": result,
            "note": "Actual connectivity testing (LDAP bind, AD join check) "
            "requires ClearPass server-side capabilities.",
        }
    except Exception as e:
        return f"Error fetching auth source for testing: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_auth_methods(
    ctx: Context,
    auth_method_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
) -> dict | str:
    """Get ClearPass authentication methods (EAP, MAC Auth, RADIUS proxy, etc.).

    If auth_method_id or name is provided, returns a single method.
    Otherwise returns a paginated list of all authentication methods.

    Args:
        auth_method_id: Numeric ID for single-item lookup.
        name: Auth method name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if auth_method_id:
            return client.get_auth_method_by_auth_method_id(auth_method_id=auth_method_id)
        if name:
            return client.get_auth_method_name_by_name(name=name)
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return client._send_request("/auth-method" + query, "get")
    except Exception as e:
        return f"Error fetching auth methods: {e}"
