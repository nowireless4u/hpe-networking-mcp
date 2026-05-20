"""ClearPass policy element read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get


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
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return clearpass_get(client, "/config/service" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching services: {e}"}) from e


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
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return clearpass_get(client, "/posture-policy" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching posture policies: {e}"}) from e


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
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return clearpass_get(client, "/network-device-group" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching device groups: {e}"}) from e


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
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return clearpass_get(client, "/proxy-target" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching proxy targets: {e}"}) from e


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
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return clearpass_get(client, "/radius-dictionary" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching RADIUS dictionaries: {e}"}) from e


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
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return clearpass_get(client, "/tacacs-service-dictionary" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching TACACS+ dictionaries: {e}"}) from e


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
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return clearpass_get(client, "/application-dictionary" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching application dictionaries: {e}"}) from e


@tool(annotations=READ_ONLY)
async def clearpass_get_radius_dynamic_authorization_template(
    ctx: Context,
    template_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass RADIUS dynamic-authorization (CoA) templates.

    These are pre-defined CoA payload templates that enforcement profiles
    reference to issue ``Disconnect-Request`` and ``CoA-Request`` packets
    to network devices — e.g. role-change, VLAN-change, bandwidth limits.

    If template_id or name is provided, returns a single template.
    Otherwise returns a paginated list of all CoA templates.

    Args:
        template_id: Numeric ID for single-item lookup.
        name: Template name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order. Default server-side: "+id".
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25, max 1000).
        calculate_count: When true, include total count in response.

    See: https://developer.arubanetworks.com/cppm/reference (Policy Elements → /radius-dynamic-authorization-template)
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if template_id:
            return clearpass_get(client, f"/radius-dynamic-authorization-template/{template_id}")
        if name:
            return clearpass_get(client, f"/radius-dynamic-authorization-template/name/{name}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return clearpass_get(client, "/radius-dynamic-authorization-template" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(
            {"status_code": 502, "message": f"Error fetching RADIUS dynamic authorization templates: {e}"}
        ) from e
