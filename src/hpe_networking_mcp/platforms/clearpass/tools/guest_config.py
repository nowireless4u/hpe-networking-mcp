"""ClearPass guest configuration read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


def _build_query_string(
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> str:
    """Build ClearPass REST API query string for list endpoints."""
    params = [
        f"filter={filter}" if filter else "",
        f"sort={sort}" if sort else "",
        f"offset={offset}",
        f"limit={limit}",
        f"calculate_count={'true' if calculate_count else 'false'}",
    ]
    return "?" + "&".join(p for p in params if p)


@tool(annotations=READ_ONLY)
async def clearpass_get_pass_templates(
    ctx: Context,
    template_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass guest pass templates (receipt/credential templates).

    If template_id is provided, returns a single template.
    Otherwise returns a paginated list of all pass templates.

    Args:
        template_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_guestconfiguration import ApiGuestConfiguration

        client = await get_clearpass_session(ApiGuestConfiguration)
        if template_id:
            return client.get_template_pass_by_id(id=template_id)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/template/pass" + query, "get")
    except Exception as e:
        return f"Error fetching pass templates: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_print_templates(
    ctx: Context,
    template_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass guest print templates (printable credential layouts).

    If template_id is provided, returns a single template.
    Otherwise returns a paginated list of all print templates.

    Args:
        template_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_guestconfiguration import ApiGuestConfiguration

        client = await get_clearpass_session(ApiGuestConfiguration)
        if template_id:
            return client.get_template_print_by_id(id=template_id)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/template/print" + query, "get")
    except Exception as e:
        return f"Error fetching print templates: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_weblogin_pages(
    ctx: Context,
    page_id: str | None = None,
    page_name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass web login (captive portal) page configurations.

    If page_id or page_name is provided, returns a single page config.
    Otherwise returns a paginated list of all web login pages.

    Args:
        page_id: Numeric ID for single-item lookup.
        page_name: Page name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_guestconfiguration import ApiGuestConfiguration

        client = await get_clearpass_session(ApiGuestConfiguration)
        if page_id:
            return client.get_weblogin_by_id(id=page_id)
        if page_name:
            return client.get_weblogin_page_name_by_page_name(page_name=page_name)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/weblogin" + query, "get")
    except Exception as e:
        return f"Error fetching web login pages: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_guest_auth_settings(
    ctx: Context,
) -> dict | str:
    """Get ClearPass guest authentication settings.

    Returns the global guest authentication configuration including
    allowed authentication methods and session policies.
    """
    try:
        from pyclearpass.api_guestconfiguration import ApiGuestConfiguration

        client = await get_clearpass_session(ApiGuestConfiguration)
        return client.get_guest_authentication()
    except Exception as e:
        return f"Error fetching guest authentication settings: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_guest_manager_settings(
    ctx: Context,
) -> dict | str:
    """Get ClearPass Guest Manager settings.

    Returns the Guest Manager configuration including self-registration,
    sponsor approval, and account lifetime policies.
    """
    try:
        from pyclearpass.api_guestconfiguration import ApiGuestConfiguration

        client = await get_clearpass_session(ApiGuestConfiguration)
        return client.get_guestmanager()
    except Exception as e:
        return f"Error fetching guest manager settings: {e}"
