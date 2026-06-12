"""ClearPass local server configuration read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client


@tool(capability=Capability.READ)
async def clearpass_get_access_controls(
    ctx: Context,
    server_uuid: str,
    resource_name: str | None = None,
) -> dict | str:
    """Get ClearPass server access control rules.

    If resource_name is provided, returns a specific access control resource.
    Otherwise returns all access control rules for the server.

    Args:
        server_uuid: UUID of the ClearPass server node.
        resource_name: Specific resource name for single-item lookup.
    """
    try:
        client = await get_clearpass_client()
        if resource_name:
            return await client.request(
                "get", f"/server/access-control/{path_seg(server_uuid)}/{path_seg(resource_name)}"
            )
        return await client.request("get", f"/server/access-control/{path_seg(server_uuid)}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching access controls: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_ad_domains(
    ctx: Context,
    server_uuid: str,
    netbios_name: str | None = None,
) -> dict | str:
    """Get ClearPass Active Directory domain configurations.

    If netbios_name is provided, returns a specific AD domain.
    Otherwise returns all AD domains configured on the server.

    Args:
        server_uuid: UUID of the ClearPass server node.
        netbios_name: NetBIOS name for single-domain lookup.
    """
    try:
        client = await get_clearpass_client()
        if netbios_name:
            return await client.request(
                "get", f"/ad-domain/{path_seg(server_uuid)}/netbios-name/{path_seg(netbios_name)}"
            )
        return await client.request("get", f"/ad-domain/{path_seg(server_uuid)}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching AD domains: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_server_version(
    ctx: Context,
    uuid: str | None = None,
) -> dict | str:
    """Get ClearPass server version and cluster information.

    If uuid is provided, returns version info for a specific cluster member.
    Otherwise returns the CPPM version info and cluster server list.

    Args:
        uuid: Cluster member UUID for specific server lookup.
    """
    try:
        client = await get_clearpass_client()
        if uuid:
            return await client.request("get", f"/cluster/server/{path_seg(uuid)}")
        return {
            "cppm_version": await client.request("get", "/cppm-version"),
            "server_version": await client.request("get", "/server/version"),
        }
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching server version: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_fips_status(
    ctx: Context,
) -> dict | str:
    """Get ClearPass FIPS (Federal Information Processing Standards) status.

    Returns whether FIPS mode is enabled or disabled on the ClearPass server.
    """
    try:
        client = await get_clearpass_client()
        return await client.request("get", "/server/fips")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching FIPS status: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_server_services(
    ctx: Context,
    server_uuid: str,
    service_name: str | None = None,
) -> dict | str:
    """Get ClearPass server service status.

    If service_name is provided, returns status for a specific service.
    Otherwise returns all services running on the server.

    Args:
        server_uuid: UUID of the ClearPass server node.
        service_name: Service name for single-service lookup.
    """
    try:
        client = await get_clearpass_client()
        if service_name:
            return await client.request("get", f"/server/service/{path_seg(server_uuid)}/{path_seg(service_name)}")
        return await client.request("get", f"/server/service/{path_seg(server_uuid)}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching server services: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_server_snmp(
    ctx: Context,
    server_uuid: str,
) -> dict | str:
    """Get ClearPass server SNMP configuration.

    Returns the SNMP agent configuration for the specified server node,
    including community strings, trap settings, and engine ID.

    Args:
        server_uuid: UUID of the ClearPass server node.
    """
    try:
        client = await get_clearpass_client()
        return await client.request("get", f"/server/snmp/{path_seg(server_uuid)}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching server SNMP config: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_cluster_servers(
    ctx: Context,
) -> dict | str:
    """List all ClearPass servers in the cluster.

    Returns one record per cluster node with its UUID, name, IP address,
    role (publisher/subscriber), and cluster-membership state. Use this
    to find the ``server_uuid`` other server-scoped tools require
    (``clearpass_get_server_services``, ``clearpass_manage_service_params``,
    etc.).

    Common use case — answer "are all servers in the cluster configured
    consistently?":
    1. Call this tool to get the list of server UUIDs.
    2. Call ``clearpass_get_server_services`` for each.
    3. Compare param values across servers in code mode.

    See: https://developer.arubanetworks.com/cppm/reference (Local Server Configuration → /server)
    """
    try:
        client = await get_clearpass_client()
        return await client.request("get", "/cluster/server")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching cluster servers: {e}"}) from e
