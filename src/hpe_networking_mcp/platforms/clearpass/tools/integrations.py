"""ClearPass integration read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get


@tool(capability=Capability.READ)
async def clearpass_get_extensions(
    ctx: Context,
    extension_id: str | None = None,
    show_config: bool = False,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass extension instances (third-party integrations).

    If extension_id is provided, returns a single extension instance.
    Set show_config=True with extension_id to include configuration details.
    Otherwise returns a paginated list of all extension instances.

    Args:
        extension_id: Numeric ID for single-item lookup.
        show_config: If True and extension_id is set, returns config details.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if extension_id and show_config:
            return await client.request("get", f"/extension/instance/{path_seg(extension_id)}/config")
        if extension_id:
            return await client.request("get", f"/extension/instance/{path_seg(extension_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/extension/instance" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching extensions: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_syslog_targets(
    ctx: Context,
    syslog_target_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass syslog export targets.

    If syslog_target_id is provided, returns a single syslog target.
    Otherwise returns a paginated list of all syslog targets.

    Args:
        syslog_target_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+host_address" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if syslog_target_id:
            return await client.request("get", f"/syslog-target/{path_seg(syslog_target_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/syslog-target" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching syslog targets: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_syslog_export_filters(
    ctx: Context,
    syslog_export_filter_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass syslog export filter configurations.

    If syslog_export_filter_id is provided, returns a single export filter.
    Otherwise returns a paginated list of all syslog export filters.

    Args:
        syslog_export_filter_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if syslog_export_filter_id:
            return await client.request("get", f"/syslog-export-filter/{path_seg(syslog_export_filter_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/syslog-export-filter" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching syslog export filters: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_event_sources(
    ctx: Context,
    event_sources_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass event sources (external event ingestion sources).

    If event_sources_id is provided, returns a single event source.
    Otherwise returns a paginated list of all event sources.

    Args:
        event_sources_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if event_sources_id:
            return await client.request("get", f"/event-sources/{path_seg(event_sources_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/event-sources" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching event sources: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_context_servers(
    ctx: Context,
    context_server_action_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass context server actions (HTTP-based integrations).

    If context_server_action_id is provided, returns a single action.
    Otherwise returns a paginated list of all context server actions.

    Args:
        context_server_action_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+server_name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if context_server_action_id:
            return await client.request("get", f"/context-server-action/{path_seg(context_server_action_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/context-server-action" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching context server actions: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_endpoint_context_servers(
    ctx: Context,
    endpoint_context_server_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass endpoint context servers (MDM/EMM integrations).

    If endpoint_context_server_id is provided, returns a single server.
    Otherwise returns a paginated list of all endpoint context servers.

    Args:
        endpoint_context_server_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+server_name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        client = await get_clearpass_client()
        if endpoint_context_server_id:
            return await client.request("get", f"/endpoint-context-server/{path_seg(endpoint_context_server_id)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/endpoint-context-server" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching endpoint context servers: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_extension_log(
    ctx: Context,
    extension_id: str,
    tail: int | None = None,
) -> dict | str:
    """Get the runtime log from a ClearPass extension instance.

    Useful for debugging extension behavior without shelling into the
    ClearPass server. Returns recent log lines for the named extension.

    Args:
        extension_id: Extension instance ID (UUID-like).
        tail: Optional max number of recent log lines to return.

    See: https://developer.arubanetworks.com/cppm/reference (Integrations → /extension-instance/{id}/log)
    """
    try:
        client = await get_clearpass_client()
        path = f"/extension/instance/{path_seg(extension_id)}/log"
        if tail is not None:
            path += f"?tail={tail}"
        return await clearpass_get(client, path)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching extension log: {e}"}) from e
