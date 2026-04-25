"""ClearPass certificate read tools."""

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
        calculate_count: When true, response includes total item count.

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
async def clearpass_get_trust_list(
    ctx: Context,
    cert_trust_list_id: str | None = None,
    details_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass certificate trust list entries.

    If cert_trust_list_id is provided, returns a single trust list entry.
    If details_id is provided, returns detailed certificate information.
    Otherwise returns a paginated list of all trust list entries.

    Args:
        cert_trust_list_id: Numeric ID for single-item lookup.
        details_id: Numeric ID for detailed certificate info.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_platformcertificates import ApiPlatformCertificates

        client = await get_clearpass_session(ApiPlatformCertificates)
        if details_id:
            return client.get_cert_trust_list_details_by_cert_trust_list_details_id(
                cert_trust_list_details_id=details_id,
            )
        if cert_trust_list_id:
            return client.get_cert_trust_list_by_cert_trust_list_id(
                cert_trust_list_id=cert_trust_list_id,
            )
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/cert-trust-list" + query, "get")
    except Exception as e:
        return f"Error fetching trust list: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_client_certificates(
    ctx: Context,
    client_cert_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass client certificates.

    If client_cert_id is provided, returns a single client certificate.
    Otherwise returns a paginated list of all client certificates.

    Args:
        client_cert_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+subject" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_platformcertificates import ApiPlatformCertificates

        client = await get_clearpass_session(ApiPlatformCertificates)
        if client_cert_id:
            return client.get_client_cert_by_client_cert_id(client_cert_id=client_cert_id)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/client-cert" + query, "get")
    except Exception as e:
        return f"Error fetching client certificates: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_server_certificates(
    ctx: Context,
    service_id: str | None = None,
    server_uuid: str | None = None,
    service_name: str | None = None,
) -> dict | str:
    """Get ClearPass server certificates.

    If service_id is provided, returns a server certificate by service ID.
    If server_uuid and service_name are provided, returns a server certificate by name.
    Otherwise returns a list of all server certificates.

    Args:
        service_id: Service ID for single-item lookup.
        server_uuid: Server UUID (required with service_name for lookup by name).
        service_name: Service name (required with server_uuid for lookup by name).
    """
    try:
        from pyclearpass.api_platformcertificates import ApiPlatformCertificates

        client = await get_clearpass_session(ApiPlatformCertificates)
        if service_id:
            return client.get_server_cert_by_service_id(service_id=service_id)
        if server_uuid and service_name:
            return client.get_server_cert_name_by_server_uuid_service_name(
                server_uuid=server_uuid,
                service_name=service_name,
            )
        return client._send_request("/server-cert", "get")
    except Exception as e:
        return f"Error fetching server certificates: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_service_certificates(
    ctx: Context,
    service_cert_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass service certificates.

    If service_cert_id is provided, returns a single service certificate.
    Otherwise returns a paginated list of all service certificates.

    Args:
        service_cert_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+subject" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_platformcertificates import ApiPlatformCertificates

        client = await get_clearpass_session(ApiPlatformCertificates)
        if service_cert_id:
            return client.get_service_cert_by_service_cert_id(service_cert_id=service_cert_id)
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/service-cert" + query, "get")
    except Exception as e:
        return f"Error fetching service certificates: {e}"
