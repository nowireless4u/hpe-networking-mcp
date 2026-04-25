"""ClearPass integration read tools."""

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
    """Build ClearPass REST API query string for list endpoints.

    Args:
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset.
        limit: Max results per page.

    Returns:
        Query string starting with '?' for appending to a path.
    """
    params = [
        f"filter={filter}" if filter else "",
        f"sort={sort}" if sort else "",
        f"offset={offset}",
        f"limit={limit}",
        f"calculate_count={'true' if calculate_count else 'false'}",
    ]
    return "?" + "&".join(p for p in params if p)


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_integrations import ApiIntegrations

        client = await get_clearpass_session(ApiIntegrations)
        if extension_id and show_config:
            return client.get_extension_instance_by_id_config(id=extension_id)
        if extension_id:
            return client.get_extension_instance_by_id(id=extension_id)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/extension/instance" + query, "get")
    except Exception as e:
        return f"Error fetching extensions: {e}"


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_integrations import ApiIntegrations

        client = await get_clearpass_session(ApiIntegrations)
        if syslog_target_id:
            return client.get_syslog_target_by_syslog_target_id(syslog_target_id=syslog_target_id)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/syslog-target" + query, "get")
    except Exception as e:
        return f"Error fetching syslog targets: {e}"


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_integrations import ApiIntegrations

        client = await get_clearpass_session(ApiIntegrations)
        if syslog_export_filter_id:
            return client.get_syslog_export_filter_by_syslog_export_filter_id(
                syslog_export_filter_id=syslog_export_filter_id,
            )
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/syslog-export-filter" + query, "get")
    except Exception as e:
        return f"Error fetching syslog export filters: {e}"


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_integrations import ApiIntegrations

        client = await get_clearpass_session(ApiIntegrations)
        if event_sources_id:
            return client.get_event_sources_by_event_sources_id(event_sources_id=event_sources_id)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/event-sources" + query, "get")
    except Exception as e:
        return f"Error fetching event sources: {e}"


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_integrations import ApiIntegrations

        client = await get_clearpass_session(ApiIntegrations)
        if context_server_action_id:
            return client.get_context_server_action_by_context_server_action_id(
                context_server_action_id=context_server_action_id,
            )
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/context-server-action" + query, "get")
    except Exception as e:
        return f"Error fetching context server actions: {e}"


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_integrations import ApiIntegrations

        client = await get_clearpass_session(ApiIntegrations)
        if endpoint_context_server_id:
            return client.get_endpoint_context_server_by_endpoint_context_server_id(
                endpoint_context_server_id=endpoint_context_server_id,
            )
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/endpoint-context-server" + query, "get")
    except Exception as e:
        return f"Error fetching endpoint context servers: {e}"


@tool(annotations=READ_ONLY)
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
        from pyclearpass.api_integrations import ApiIntegrations

        client = await get_clearpass_session(ApiIntegrations)
        path = f"/extension-instance/{extension_id}/log"
        if tail is not None:
            path += f"?tail={tail}"
        return client._send_request(path, "get")
    except Exception as e:
        return f"Error fetching extension log: {e}"
