"""ClearPass local server configuration read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import mcp
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


@mcp.tool(annotations=READ_ONLY)
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
        from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

        client = await get_clearpass_session(ApiLocalServerConfiguration)
        if resource_name:
            return client.get_server_access_control_by_server_uuid_resource_name(
                server_uuid=server_uuid,
                resource_name=resource_name,
            )
        return client.get_server_access_control_by_server_uuid(server_uuid=server_uuid)
    except Exception as e:
        return f"Error fetching access controls: {e}"


@mcp.tool(annotations=READ_ONLY)
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
        from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

        client = await get_clearpass_session(ApiLocalServerConfiguration)
        if netbios_name:
            return client.get_ad_domain_by_server_uuid_netbios_name_netbios_name(
                server_uuid=server_uuid,
                netbios_name=netbios_name,
            )
        return client.get_ad_domain_by_server_uuid(server_uuid=server_uuid)
    except Exception as e:
        return f"Error fetching AD domains: {e}"


@mcp.tool(annotations=READ_ONLY)
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
        from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

        client = await get_clearpass_session(ApiLocalServerConfiguration)
        if uuid:
            return client.get_cluster_server_by_uuid(uuid=uuid)
        return {
            "cppm_version": client.get_cppm_version(),
            "server_version": client.get_server_version(),
        }
    except Exception as e:
        return f"Error fetching server version: {e}"


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_fips_status(
    ctx: Context,
) -> dict | str:
    """Get ClearPass FIPS (Federal Information Processing Standards) status.

    Returns whether FIPS mode is enabled or disabled on the ClearPass server.
    """
    try:
        from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

        client = await get_clearpass_session(ApiLocalServerConfiguration)
        return client.get_server_fips()
    except Exception as e:
        return f"Error fetching FIPS status: {e}"


@mcp.tool(annotations=READ_ONLY)
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
        from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

        client = await get_clearpass_session(ApiLocalServerConfiguration)
        if service_name:
            return client.get_server_service_by_server_uuid_service_name(
                server_uuid=server_uuid,
                service_name=service_name,
            )
        return client.get_server_service_by_server_uuid(server_uuid=server_uuid)
    except Exception as e:
        return f"Error fetching server services: {e}"


@mcp.tool(annotations=READ_ONLY)
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
        from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

        client = await get_clearpass_session(ApiLocalServerConfiguration)
        return client.get_server_snmp_by_server_uuid(server_uuid=server_uuid)
    except Exception as e:
        return f"Error fetching server SNMP config: {e}"
