"""ClearPass policy element read tools."""

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
async def clearpass_get_services(
    ctx: Context,
    config_service_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass policy services (authentication/authorization service rules).

    If config_service_id or name is provided, returns a single service.
    Otherwise returns a paginated list of all configured services.

    Args:
        config_service_id: Numeric ID for single-item lookup.
        name: Service name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if config_service_id:
            return client.get_config_service_by_config_service_id(config_service_id=config_service_id)
        if name:
            return client.get_config_service_name_by_name(name=name)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/config/service" + query, "get")
    except Exception as e:
        return f"Error fetching services: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_posture_policies(
    ctx: Context,
    posture_policy_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass posture (health check) policies.

    If posture_policy_id or name is provided, returns a single posture policy.
    Otherwise returns a paginated list of all posture policies.

    Args:
        posture_policy_id: Numeric ID for single-item lookup.
        name: Policy name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if posture_policy_id:
            return client.get_posture_policy_by_posture_policy_id(posture_policy_id=posture_policy_id)
        if name:
            return client.get_posture_policy_name_by_name(name=name)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/posture-policy" + query, "get")
    except Exception as e:
        return f"Error fetching posture policies: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_device_groups(
    ctx: Context,
    network_device_group_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass network device groups.

    If network_device_group_id or name is provided, returns a single group.
    Otherwise returns a paginated list of all device groups.

    Args:
        network_device_group_id: Numeric ID for single-item lookup.
        name: Group name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if network_device_group_id:
            return client.get_network_device_group_by_network_device_group_id(
                network_device_group_id=network_device_group_id,
            )
        if name:
            return client.get_network_device_group_name_by_name(name=name)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/network-device-group" + query, "get")
    except Exception as e:
        return f"Error fetching device groups: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_proxy_targets(
    ctx: Context,
    proxy_target_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass RADIUS proxy targets.

    If proxy_target_id or name is provided, returns a single proxy target.
    Otherwise returns a paginated list of all proxy targets.

    Args:
        proxy_target_id: Numeric ID for single-item lookup.
        name: Proxy target name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if proxy_target_id:
            return client.get_proxy_target_by_proxy_target_id(proxy_target_id=proxy_target_id)
        if name:
            return client.get_proxy_target_name_by_name(name=name)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/proxy-target" + query, "get")
    except Exception as e:
        return f"Error fetching proxy targets: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_radius_dictionaries(
    ctx: Context,
    radius_dictionary_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass RADIUS dictionary definitions.

    If radius_dictionary_id or name is provided, returns a single dictionary.
    Otherwise returns a paginated list of all RADIUS dictionaries.

    Args:
        radius_dictionary_id: Numeric ID for single-item lookup.
        name: Dictionary name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if radius_dictionary_id:
            return client.get_radius_dictionary_by_radius_dictionary_id(
                radius_dictionary_id=radius_dictionary_id,
            )
        if name:
            return client.get_radius_dictionary_name_by_name(name=name)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/radius-dictionary" + query, "get")
    except Exception as e:
        return f"Error fetching RADIUS dictionaries: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_tacacs_dictionaries(
    ctx: Context,
    tacacs_service_dictionary_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass TACACS+ service dictionary definitions.

    If tacacs_service_dictionary_id or name is provided, returns a single dictionary.
    Otherwise returns a paginated list of all TACACS+ dictionaries.

    Args:
        tacacs_service_dictionary_id: Numeric ID for single-item lookup.
        name: Dictionary name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if tacacs_service_dictionary_id:
            return client.get_tacacs_service_dictionary_by_tacacs_service_dictionary_id(
                tacacs_service_dictionary_id=tacacs_service_dictionary_id,
            )
        if name:
            return client.get_tacacs_service_dictionary_name_by_name(name=name)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/tacacs-service-dictionary" + query, "get")
    except Exception as e:
        return f"Error fetching TACACS+ dictionaries: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_application_dictionaries(
    ctx: Context,
    application_dictionary_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass application dictionary definitions.

    If application_dictionary_id or name is provided, returns a single dictionary.
    Otherwise returns a paginated list of all application dictionaries.

    Args:
        application_dictionary_id: Numeric ID for single-item lookup.
        name: Dictionary name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if application_dictionary_id:
            return client.get_application_dictionary_by_application_dictionary_id(
                application_dictionary_id=application_dictionary_id,
            )
        if name:
            return client.get_application_dictionary_name_by_name(name=name)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/application-dictionary" + query, "get")
    except Exception as e:
        return f"Error fetching application dictionaries: {e}"
