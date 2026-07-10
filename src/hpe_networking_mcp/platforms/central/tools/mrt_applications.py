"""Aruba Central application-visibility monitoring tools.

Wraps the ``network-monitoring/v1`` usage-analytics endpoints that roll
traffic up by category: top application categories, top website
categories, and per-application security-risk scoring. All three share
the same time-window + scoping query surface (a required ``start-at`` /
``end-at`` window plus optional site / client / device / SSID / role
filters) and return the standard ``{count, items, offset, total}``
collection shape.
"""

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command

# Shared parameter docs — every field scopes the same usage rollup.
_START = Annotated[str, Field(description="ISO-8601 start of the reporting window (required).")]
_END = Annotated[str, Field(description="ISO-8601 end of the reporting window (required).")]
_SITE = Annotated[str | None, Field(description="Scope to one site by site ID.")]
_CLIENT = Annotated[str | None, Field(description="Scope to one client by client ID (MAC).")]
_SERIAL = Annotated[str | None, Field(description="Scope to one device by serial number.")]
_SSID = Annotated[str | None, Field(description="Scope to one SSID.")]
_ROLE = Annotated[str | None, Field(description="Scope to one user role.")]
_OFFSET = Annotated[int | None, Field(description="Pagination offset.")]
_LIMIT = Annotated[int | None, Field(description="Max rows to return.")]
_TOP = Annotated[int | None, Field(description="Return only the top-N categories by usage.")]


async def _get(conn, path: str, params: dict) -> dict | str:
    """GET *path* with *params*; return the payload or a structured error dict."""
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=path,
        api_params=params,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


def _usage_params(
    *,
    start_at: str,
    end_at: str,
    site_id: str | None,
    client_id: str | None,
    serial_number: str | None,
    ssid: str | None,
    user_role: str | None,
    offset: int | None,
    limit: int | None,
    top: int | None = None,
) -> dict:
    """Build the kebab-case query dict Central's usage endpoints expect."""
    params: dict = {"start-at": start_at, "end-at": end_at}
    optional = {
        "site-id": site_id,
        "client-id": client_id,
        "serial-number": serial_number,
        "ssid": ssid,
        "user-role": user_role,
        "offset": offset,
        "limit": limit,
        "top": top,
    }
    params.update({k: v for k, v in optional.items() if v is not None})
    return params


@tool(capability=Capability.READ)
async def central_get_application_categories(
    ctx: Context,
    start_at: _START,
    end_at: _END,
    site_id: _SITE = None,
    client_id: _CLIENT = None,
    serial_number: _SERIAL = None,
    ssid: _SSID = None,
    user_role: _ROLE = None,
    offset: _OFFSET = None,
    limit: _LIMIT = None,
    top: _TOP = None,
) -> dict | str:
    """Get top application categories by usage over a time window.

    Rolls per-application traffic up into categories (e.g. streaming,
    collaboration, social) and ranks them by volume across the requested
    scope. Returns the ``{count, items, offset, total}`` collection shape.
    """
    conn = get_central_conn(ctx)
    params = _usage_params(
        start_at=start_at,
        end_at=end_at,
        site_id=site_id,
        client_id=client_id,
        serial_number=serial_number,
        ssid=ssid,
        user_role=user_role,
        offset=offset,
        limit=limit,
        top=top,
    )
    return await _get(conn, "network-monitoring/v1/application-categories", params)


@tool(capability=Capability.READ)
async def central_get_website_categories(
    ctx: Context,
    start_at: _START,
    end_at: _END,
    site_id: _SITE = None,
    client_id: _CLIENT = None,
    serial_number: _SERIAL = None,
    ssid: _SSID = None,
    user_role: _ROLE = None,
    offset: _OFFSET = None,
    limit: _LIMIT = None,
    top: _TOP = None,
) -> dict | str:
    """Get top website categories by usage over a time window.

    The web-filtering counterpart of ``central_get_application_categories``
    — ranks browsed website categories (e.g. business, media, gaming) by
    traffic across the requested scope. Returns the ``{count, items,
    offset, total}`` collection shape.
    """
    conn = get_central_conn(ctx)
    params = _usage_params(
        start_at=start_at,
        end_at=end_at,
        site_id=site_id,
        client_id=client_id,
        serial_number=serial_number,
        ssid=ssid,
        user_role=user_role,
        offset=offset,
        limit=limit,
        top=top,
    )
    return await _get(conn, "network-monitoring/v1/website-categories", params)


@tool(capability=Capability.READ)
async def central_get_security_risks(
    ctx: Context,
    start_at: _START,
    end_at: _END,
    site_id: _SITE = None,
    client_id: _CLIENT = None,
    serial_number: _SERIAL = None,
    ssid: _SSID = None,
    user_role: _ROLE = None,
    offset: _OFFSET = None,
    limit: _LIMIT = None,
) -> dict | str:
    """Get per-application security-risk information over a time window.

    Surfaces the risk scoring Central assigns to observed applications
    (risky/anonymizer/malware-associated traffic) across the requested
    scope, for security posture review. Returns the ``{count, items,
    offset, total}`` collection shape. (No ``top`` parameter on this
    endpoint — use ``limit`` / ``offset`` to page.)
    """
    conn = get_central_conn(ctx)
    params = _usage_params(
        start_at=start_at,
        end_at=end_at,
        site_id=site_id,
        client_id=client_id,
        serial_number=serial_number,
        ssid=ssid,
        user_role=user_role,
        offset=offset,
        limit=limit,
    )
    return await _get(conn, "network-monitoring/v1/security-risks", params)
