"""ClearPass guest configuration read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if template_id:
            return await client.request("get", f"/template/pass/{path_seg(template_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/template/pass" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching pass templates: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if template_id:
            return await client.request("get", f"/template/print/{path_seg(template_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/template/print" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching print templates: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if page_id:
            return await client.request("get", f"/weblogin/{path_seg(page_id)}")
        if page_name:
            return await client.request("get", f"/weblogin/page-name/{path_seg(page_name)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/weblogin" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching web login pages: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_guest_auth_settings(
    ctx: Context,
) -> dict | str:
    """Get ClearPass guest authentication settings.

    Returns the global guest authentication configuration including
    allowed authentication methods and session policies.
    """
    try:
        client = await get_clearpass_client()
        return await client.request("get", "/guest/authentication")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching guest authentication settings: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_guest_manager_settings(
    ctx: Context,
) -> dict | str:
    """Get ClearPass Guest Manager settings.

    Returns the Guest Manager configuration including self-registration,
    sponsor approval, and account lifetime policies.
    """
    try:
        client = await get_clearpass_client()
        return await client.request("get", "/guestmanager")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching guest manager settings: {e}"}) from e
