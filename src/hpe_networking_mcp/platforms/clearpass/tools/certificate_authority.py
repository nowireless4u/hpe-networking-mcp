"""ClearPass internal Certificate Authority (CA) read tools.

Covers ClearPass's internal CA — the certificate store
(``/api/certificate``) and onboard device records
(``/api/onboard/device``) that hold CA-issued identities for managed
devices.

Note: ``/api/onboard/device`` is distinct from ``/api/device``
(identity device records, wrapped by ``clearpass_get_devices``).
The onboard endpoint is CA-scope only.

See: https://developer.arubanetworks.com/cppm/reference (Certificate Authority)
"""

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
    """Build ClearPass REST API query string for list endpoints."""
    params = [
        f"filter={filter}" if filter else "",
        f"sort={sort}" if sort else "",
        f"offset={offset}",
        f"limit={limit}",
        f"calculate_count={'true' if calculate_count else 'false'}",
    ]
    return "?" + "&".join(p for p in params if p)


@tool(annotations=READ_ONLY)
async def clearpass_get_certificates(
    ctx: Context,
    certificate_id: str | None = None,
    chain: bool = False,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get certificates issued by ClearPass's internal CA.

    If ``certificate_id`` is provided, returns a single cert record.
    With ``chain=True``, returns the full certificate chain for that ID
    (issuer chain back to the root). Otherwise returns a paginated list
    of all CA-issued certificates.

    Args:
        certificate_id: Numeric ID for single-item lookup.
        chain: When true alongside ``certificate_id``, returns the cert chain.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order. Default server-side: "+id".
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25, max 1000).
        calculate_count: When true, include total count in response.

    See: https://developer.arubanetworks.com/cppm/reference
    (Certificate Authority → /certificate, /certificate/{id}, /certificate/{id}/chain)
    """
    try:
        from pyclearpass.api_certificateauthority import ApiCertificateAuthority

        client = await get_clearpass_session(ApiCertificateAuthority)
        if certificate_id and chain:
            return client._send_request(f"/certificate/{certificate_id}/chain", "get")
        if certificate_id:
            return client._send_request(f"/certificate/{certificate_id}", "get")
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/certificate" + query, "get")
    except Exception as e:
        return f"Error fetching CA certificates: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_onboard_devices(
    ctx: Context,
    onboard_device_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass onboard device records (CA-issued device certificates).

    Onboard records track devices that received a CA-issued cert through
    the onboarding workflow. Each record holds the cert metadata, owner
    (user), serial number, MAC, and onboarding timestamp.

    Note: this is distinct from ``clearpass_get_devices`` — that tool
    returns RADIUS device-database records (``/api/device``), while
    this tool covers onboarded-device cert records (``/api/onboard/device``).

    If ``onboard_device_id`` is provided, returns a single record.
    Otherwise returns a paginated list of all onboard devices.

    Args:
        onboard_device_id: Numeric ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order. Default server-side: "+id".
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25, max 1000).
        calculate_count: When true, include total count in response.

    See: https://developer.arubanetworks.com/cppm/reference (Certificate Authority → /onboard/device)
    """
    try:
        from pyclearpass.api_certificateauthority import ApiCertificateAuthority

        client = await get_clearpass_session(ApiCertificateAuthority)
        if onboard_device_id:
            return client._send_request(f"/onboard/device/{onboard_device_id}", "get")
        query = _build_query_string(filter, sort, offset, limit, calculate_count)
        return client._send_request("/onboard/device" + query, "get")
    except Exception as e:
        return f"Error fetching onboard devices: {e}"
