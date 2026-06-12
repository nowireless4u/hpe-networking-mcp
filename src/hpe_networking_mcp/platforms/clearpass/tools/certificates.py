"""ClearPass certificate read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if details_id:
            return await client.request("get", f"/cert-trust-list-details/{details_id}")
        if cert_trust_list_id:
            return await client.request("get", f"/cert-trust-list/{cert_trust_list_id}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/cert-trust-list" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching trust list: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if client_cert_id:
            return await client.request("get", f"/client-cert/{client_cert_id}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/client-cert" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching client certificates: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if service_id:
            return await client.request("get", f"/server-cert/{service_id}")
        if server_uuid and service_name:
            return await client.request("get", f"/server-cert/name/{server_uuid}/{service_name}")
        return await clearpass_get(client, "/server-cert")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching server certificates: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if service_cert_id:
            return await client.request("get", f"/service-cert/{service_cert_id}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/service-cert" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching service certificates: {e}"}) from e


@tool(capability=Capability.READ)
async def clearpass_get_revocation_list(
    ctx: Context,
    revocation_list_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass certificate revocation lists (CRLs).

    CRLs enumerate revoked client/server certificates ClearPass should
    reject when validating peer certs (e.g. EAP-TLS sessions).

    If revocation_list_id is provided, returns a single CRL.
    Otherwise returns a paginated list of all CRLs.

    Args:
        revocation_list_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order. Default server-side: "+id".
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25, max 1000).
        calculate_count: When true, include total count in response.

    See: https://developer.arubanetworks.com/cppm/reference (Platform Certificates → /revocation-list)
    """
    try:
        client = await get_clearpass_client()
        if revocation_list_id:
            return await clearpass_get(client, f"/revocation-list/{revocation_list_id}")
        query = build_query_string(filter, sort, offset, limit, calculate_count)
        return await clearpass_get(client, "/revocation-list" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching revocation lists: {e}"}) from e
