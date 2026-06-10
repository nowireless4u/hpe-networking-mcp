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
from fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command

# Per the upstream OpenAPI: search must be 3-128 chars when supplied.
_SEARCH_MIN_CHARS = 3
_SEARCH_MAX_CHARS = 128

# Resync is operational, not a config edit: it re-pushes the *intended*
# config (idempotent, non-destructive). Like the disconnect/reboot tools it
# runs immediately without elicitation and isn't gated behind
# ENABLE_CENTRAL_WRITE_TOOLS.
OPERATIONAL = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


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
        central_conn=get_central_conn(ctx),
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
        raise ToolError(
            {
                "status_code": 400,
                "message": f"search must be {_SEARCH_MIN_CHARS}-{_SEARCH_MAX_CHARS} chars, got {len(search)}",
            }
        )

    api_params: dict[str, Any] = {"limit": limit, "offset": offset}
    if sort is not None:
        api_params["sort"] = sort
    if filter is not None:
        api_params["filter"] = filter
    if search is not None:
        api_params["search"] = search

    response = retry_central_command(
        central_conn=get_central_conn(ctx),
        api_method="GET",
        api_path="network-config/v1alpha1/config-health/devices",
        api_params=api_params,
    )
    return response.get("msg", {})


@tool(annotations=OPERATIONAL)
async def central_resync_device_config(
    ctx: Context,
    serials: list[str],
) -> dict | str:
    """
    Triggers a full configuration sync (resync) for one or more devices.

    Forces Central to re-push the intended configuration to the named
    devices — the standard remediation when a device shows up as
    ``OUT_OF_SYNC`` or with ``CONFIG_PUSH_FAILURES``. Find candidates
    first with ``central_get_devices_config_health`` (fleet view) or
    ``central_get_device_config_issues`` (single serial).

    Idempotent and non-destructive: it re-applies the config Central
    already intends for the device, it does not change configuration.
    Runs immediately (no confirmation prompt).

    Devices that can't be acted on (stale/phantom inventory entries,
    unsupported device types) are silently skipped by Central — the
    response reports how many serials were actually triggered, which may
    be fewer than the number passed in.

    Parameters:
        - serials: List of device serial numbers to resync. Required and
          non-empty.

    Returns:
        Dict with Central's response, e.g.
        ``{"message": "Full configuration sync triggered for N devices."}``
        per the ``/network-config/v1alpha1/config-health/devices-resync``
        endpoint.
    """
    if not serials:
        raise ToolError(
            {
                "status_code": 400,
                "message": "serials must be a non-empty list of device serial numbers",
            }
        )

    response = retry_central_command(
        central_conn=get_central_conn(ctx),
        api_method="POST",
        api_path="network-config/v1alpha1/config-health/devices-resync",
        api_data={"serials": serials},
    )
    return response.get("msg", {})
