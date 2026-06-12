"""ClearPass policy element read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if config_service_id:
            return await client.request("get", f"/config/service/{path_seg(config_service_id)}")
        if name:
            return await client.request("get", f"/config/service/name/{path_seg(name)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/config/service" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching services: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if posture_policy_id:
            return await client.request("get", f"/posture-policy/{path_seg(posture_policy_id)}")
        if name:
            return await client.request("get", f"/posture-policy/name/{path_seg(name)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/posture-policy" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching posture policies: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if network_device_group_id:
            return await client.request("get", f"/network-device-group/{path_seg(network_device_group_id)}")
        if name:
            return await client.request("get", f"/network-device-group/name/{path_seg(name)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/network-device-group" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching device groups: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if proxy_target_id:
            return await client.request("get", f"/proxy-target/{path_seg(proxy_target_id)}")
        if name:
            return await client.request("get", f"/proxy-target/name/{path_seg(name)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/proxy-target" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching proxy targets: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if radius_dictionary_id:
            return await client.request("get", f"/radius-dictionary/{path_seg(radius_dictionary_id)}")
        if name:
            return await client.request("get", f"/radius-dictionary/name/{path_seg(name)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/radius-dictionary" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching RADIUS dictionaries: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if tacacs_service_dictionary_id:
            return await client.request("get", f"/tacacs-service-dictionary/{path_seg(tacacs_service_dictionary_id)}")
        if name:
            return await client.request("get", f"/tacacs-service-dictionary/name/{path_seg(name)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/tacacs-service-dictionary" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching TACACS+ dictionaries: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if application_dictionary_id:
            return await client.request("get", f"/application-dictionary/{path_seg(application_dictionary_id)}")
        if name:
            return await client.request("get", f"/application-dictionary/name/{path_seg(name)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/application-dictionary" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching application dictionaries: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if template_id:
            return await clearpass_get(client, f"/radius-dynamic-authorization-template/{path_seg(template_id)}")
        if name:
            return await clearpass_get(client, f"/radius-dynamic-authorization-template/name/{path_seg(name)}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/radius-dynamic-authorization-template" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(
            {"status_code": 502, "message": f"Error fetching RADIUS dynamic authorization templates: {e}"}
        ) from e
