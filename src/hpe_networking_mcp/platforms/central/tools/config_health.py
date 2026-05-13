"""Central config-health diagnostics for the New Central Configuration API.

Wraps the ``/network-config/v1alpha1/config-health/*`` endpoints. Used
when troubleshooting "device not achieving config sync" —
``central_get_device_config_issues`` returns per-device active issue
detail (one serial in, list of issues + recommended actions out);
``central_get_devices_config_health`` returns the fleet-wide summary
with sort/filter/search for spotting which devices need attention.
"""

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command

# Per the upstream OpenAPI: search must be 3-128 chars when supplied.
_SEARCH_MIN_CHARS = 3
_SEARCH_MAX_CHARS = 128


@tool(annotations=READ_ONLY)
async def central_get_device_config_issues(
    ctx: Context,
    serial: str,
) -> dict | str:
    """
    Returns active configuration issues for a single device.

    Use when a specific device isn't achieving config sync: pass its
    serial number and get the list of configuration issues blocking
    sync, plus any recommended actions Central has surfaced.

    To diagnose across multiple devices, call
    ``central_get_devices_config_health`` first to spot which devices
    have issues, then drill in here per-serial.

    Parameters:
        - serial: Device serial number. Required.

    Returns:
        Dict with the device's active configuration issues per the
        Central ``/network-config/v1alpha1/config-health/active-issue``
        response shape.
    """
    response = retry_central_command(
        central_conn=ctx.lifespan_context["central_conn"],
        api_method="GET",
        api_path="network-config/v1alpha1/config-health/active-issue",
        api_params={"serial": serial},
    )
    return response.get("msg", {})


@tool(annotations=READ_ONLY)
async def central_get_devices_config_health(
    ctx: Context,
    limit: int = 100,
    offset: int = 0,
    sort: str | None = None,
    filter: str | None = None,
    search: str | None = None,
) -> dict | str:
    """
    Returns a summary of configuration health across devices in the fleet.

    Use to spot which devices have config-sync issues or non-zero
    activeIssues counts before drilling in with
    ``central_get_device_config_issues``.

    Parameters:
        - limit: Page size (1-100, default 100).
        - offset: Page offset (default 0).
        - sort: Optional sort by one of: ``name``, ``serial``, ``type``,
          ``siteName``, ``configStatus``, ``deviceFunction``,
          ``lastConfigTimestamp``, ``model``, ``deviceGroupName``,
          ``topPriorityIssue``, ``recommendedAction``, ``role``,
          ``deployment``, ``activeIssues``. Append ``asc`` or ``desc``
          (e.g. ``"activeIssues desc"`` for worst-offenders-first).
        - filter: OData 4.0 filter on ``name``, ``deviceFunction``,
          ``configStatus``, ``type``, ``model``, ``serial``,
          ``deviceGroupName``, or ``activeIssues``. Example:
          ``"configStatus eq 'OUT_OF_SYNC'"``.
        - search: Free-text search across ``name``, ``serial``,
          ``siteName``, ``topPriorityIssue``, and ``recommendedAction``.
          Must be 3-128 characters when supplied.

    Returns:
        Dict with the devices config-health summary per the Central
        ``/network-config/v1alpha1/config-health/devices`` response shape.
    """
    if search is not None and not (_SEARCH_MIN_CHARS <= len(search) <= _SEARCH_MAX_CHARS):
        return f"Error: search must be {_SEARCH_MIN_CHARS}-{_SEARCH_MAX_CHARS} chars when supplied, got {len(search)}"

    api_params: dict[str, Any] = {"limit": limit, "offset": offset}
    if sort is not None:
        api_params["sort"] = sort
    if filter is not None:
        api_params["filter"] = filter
    if search is not None:
        api_params["search"] = search

    response = retry_central_command(
        central_conn=ctx.lifespan_context["central_conn"],
        api_method="GET",
        api_path="network-config/v1alpha1/config-health/devices",
        api_params=api_params,
    )
    return response.get("msg", {})
