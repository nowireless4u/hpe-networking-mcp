"""Aruba Central Services tools — asset tags, AP ranging scans, device
locations, location analytics, FCO (Factory Cell Order), and WiFi
client locations.

Wraps the ``network-services/v1`` endpoint family beyond the already-
covered firmware-details and audits/wids surfaces. Each capability is a
distinct subsystem; they're collected here because they share the
``network-services/v1`` namespace.
"""

from typing import Annotated, Literal

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


def _get(conn, path: str, params: dict | None = None) -> dict | str:
    response = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=path,
        api_params=params or {},
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# ---------------------------------------------------------------------------
# Factory Cell Order (FCO)
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_fco_resp_info(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Device serial number.")],
) -> dict | str:
    """Get FCO (Factory Cell Order) response info for one device.

    Returns provisioning / RMA-related metadata tied to the device's
    factory order record. Useful when troubleshooting onboarding /
    pre-shared-key / claim-code workflows.
    """
    conn = ctx.lifespan_context["central_conn"]
    return _get(conn, f"network-services/v1/fco-resp-info/{serial_number}")


@tool(annotations=READ_ONLY)
async def central_get_fco_resp_info_all(
    ctx: Context,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List FCO response info across all devices in the tenant.

    Paginated; use for bulk audits of factory-order state.
    """
    conn = ctx.lifespan_context["central_conn"]
    return _get(conn, "network-services/v1/fco-resp-info-all", {"limit": limit, "offset": offset})


# ---------------------------------------------------------------------------
# Asset tags
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_asset_tags(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List BLE asset tags detected by the tenant's APs.

    Asset tags are physical BLE beacons (e.g. ArubaAssetTag, Blyott)
    attached to assets you want to track — laptops, medical equipment,
    inventory, etc. APs detect the BLE broadcasts and report the tags
    along with their last-known location. Each record carries the tag's
    BLE ``macAddress``, ``deviceClassifications`` (vendor / type),
    ``firstSeen`` / lastSeen timestamps, and the ``metadata`` block —
    user-attached descriptive fields (name, owner, asset category, etc.)
    populated via ``central_manage_asset_tag_metadata``.

    Use ``central_start_ap_ranging_scan`` to calibrate AP-to-AP
    distances on a floor for accurate location, and the device-location
    / wifi-clients-locations endpoints alongside this for the full
    location-services picture.
    """
    conn = ctx.lifespan_context["central_conn"]
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return _get(conn, "network-services/v1/asset-tags", params)


@tool(annotations=READ_ONLY)
async def central_get_asset_tag(
    ctx: Context,
    asset_tag_id: Annotated[
        str,
        Field(description="Asset-tag identifier (assigned by Central on first detection)."),
    ],
) -> dict | str:
    """Get one BLE asset tag's full record.

    Returns classifications, BLE MAC, first/last seen, attached metadata,
    and the last-known location for the tracked tag.
    """
    conn = ctx.lifespan_context["central_conn"]
    return _get(conn, f"network-services/v1/asset-tags/{asset_tag_id}")


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_asset_tag_metadata(
    ctx: Context,
    asset_tag_id: Annotated[str, Field(description="Asset-tag identifier.")],
    action_type: Annotated[
        Literal["create", "update", "delete"],
        Field(
            description=(
                "``'create'`` (POST), ``'update'`` (PUT — replaces wholesale), "
                "or ``'delete'`` (clears all metadata fields)."
            ),
        ),
    ],
    payload: Annotated[
        dict | None,
        Field(
            description=(
                "Descriptive fields to attach to the BLE asset tag — typically "
                "``{name, description, ownership info, asset category, ...}``. "
                "These are inventory-style attributes; they don't change what's "
                "detected, they let you label what each detected tag *is*. "
                "Ignored for delete."
            ),
        ),
    ] = None,
) -> dict | str:
    """Create / update / delete the descriptive metadata attached to a BLE asset tag.

    The metadata is the inventory record for a tracked asset — name,
    owner, asset class, etc. It doesn't affect detection; APs detect the
    BLE broadcast regardless. PUT (``update``) replaces the metadata
    wholesale. Requires ``ENABLE_CENTRAL_WRITE_TOOLS=true``.
    """
    conn = ctx.lifespan_context["central_conn"]
    method_map = {"create": "POST", "update": "PUT", "delete": "DELETE"}
    if action_type not in method_map:
        return f"Error: unknown action_type '{action_type}'."
    method = method_map[action_type]
    if action_type != "delete" and not payload:
        return f"Error: ``payload`` is required for {action_type}."
    response = retry_central_command(
        central_conn=conn,
        api_method=method,
        api_path=f"network-services/v1/asset-tags/{asset_tag_id}/metadata",
        api_data=payload or {},
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {
            "status": "success",
            "action": action_type,
            "asset_tag_id": asset_tag_id,
            "data": response.get("msg", {}),
        }
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# ---------------------------------------------------------------------------
# AP ranging scans (Beacon/BLE-based distance calibration for floor plans)
# ---------------------------------------------------------------------------


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_start_ap_ranging_scan(
    ctx: Context,
    payload: Annotated[
        dict,
        Field(
            description=(
                "Scan request body — typically includes ``site_id``, "
                "``floor_id``, scan-mode, and AP serial(s) participating. "
                "Consult Central docs for the exact shape."
            ),
        ),
    ],
) -> dict | str:
    """Kick off an AP ranging scan.

    Ranging scans calibrate inter-AP distances for accurate location
    services on a floor plan. Requires
    ``ENABLE_CENTRAL_WRITE_TOOLS=true``. The scan runs server-side;
    poll via ``central_get_ap_ranging_scan`` with the returned scan ID.
    """
    conn = ctx.lifespan_context["central_conn"]
    response = retry_central_command(
        central_conn=conn,
        api_method="POST",
        api_path="network-services/v1/ap-ranging-scans",
        api_data=payload,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(annotations=READ_ONLY)
async def central_get_ap_ranging_scans(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    floor_id: Annotated[str, Field(description="Floor identifier (under ``site_id``).")],
) -> dict | str:
    """List AP ranging scans for a floor."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(
        conn,
        f"network-services/v1/sitemaps/{site_id}/floors/{floor_id}/ap-ranging-scans",
    )


@tool(annotations=READ_ONLY)
async def central_get_ap_ranging_scan(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    floor_id: Annotated[str, Field(description="Floor identifier.")],
    scan_id: Annotated[str, Field(description="Scan identifier.")],
) -> dict | str:
    """Get one AP ranging scan's results / status."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(
        conn,
        f"network-services/v1/sitemaps/{site_id}/floors/{floor_id}/ap-ranging-scans/{scan_id}",
    )


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_delete_ap_ranging_scan(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    floor_id: Annotated[str, Field(description="Floor identifier.")],
    scan_id: Annotated[str, Field(description="Scan identifier to delete.")],
) -> dict | str:
    """Delete an AP ranging scan record. Requires ``ENABLE_CENTRAL_WRITE_TOOLS=true``."""
    conn = ctx.lifespan_context["central_conn"]
    response = retry_central_command(
        central_conn=conn,
        api_method="DELETE",
        api_path=f"network-services/v1/sitemaps/{site_id}/floors/{floor_id}/ap-ranging-scans/{scan_id}",
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "scan_id": scan_id}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# ---------------------------------------------------------------------------
# Device locations (placement on floor plans)
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_site_device_locations(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List device locations placed at a site (across all floors)."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(
        conn,
        f"network-services/v1/sites/{site_id}/device-locations",
        {"limit": limit, "offset": offset},
    )


@tool(annotations=READ_ONLY)
async def central_get_site_device_location(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    location_id: Annotated[str, Field(description="Device-location identifier.")],
) -> dict | str:
    """Get one device-location record."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(conn, f"network-services/v1/sites/{site_id}/device-locations/{location_id}")


@tool(annotations=READ_ONLY)
async def central_get_device_location(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    serial_number: Annotated[str, Field(description="Device serial number.")],
) -> dict | str:
    """Get the placement (floor + coordinates) for a specific device at a site."""
    conn = ctx.lifespan_context["central_conn"]
    return _get(
        conn,
        f"network-services/v1/sites/{site_id}/devices/{serial_number}/location",
    )


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_device_location(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    serial_number: Annotated[str, Field(description="Device serial number.")],
    action_type: Annotated[
        Literal["set", "delete"],
        Field(description="``'set'`` (POST — place / move the device) or ``'delete'`` (unplace)."),
    ],
    payload: Annotated[
        dict | None,
        Field(
            description=(
                "Placement payload — typically ``floor_id``, ``x``, ``y``, "
                "rotation. Required for ``set``; ignored for ``delete``."
            ),
        ),
    ] = None,
) -> dict | str:
    """Place / move / unplace a device on a site's floor plan."""
    conn = ctx.lifespan_context["central_conn"]
    if action_type == "set":
        if not payload:
            return "Error: ``payload`` is required for set."
        response = retry_central_command(
            central_conn=conn,
            api_method="POST",
            api_path=f"network-services/v1/sites/{site_id}/devices/{serial_number}/location",
            api_data=payload,
        )
    elif action_type == "delete":
        response = retry_central_command(
            central_conn=conn,
            api_method="DELETE",
            api_path=f"network-services/v1/sites/{site_id}/devices/{serial_number}/location",
        )
    else:
        return f"Error: unknown action_type '{action_type}'."
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {
            "status": "success",
            "action": action_type,
            "serial_number": serial_number,
            "data": response.get("msg", {}),
        }
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# ---------------------------------------------------------------------------
# WiFi client locations + Location analytics
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_wifi_clients_locations(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """Get real-time locations of WiFi clients across the tenant.

    PII: returns client MAC + computed coordinates. MACs ride existing
    normalization rules. Use a ``filter`` to scope by site / floor /
    client MAC.
    """
    conn = ctx.lifespan_context["central_conn"]
    params: dict = {"limit": limit, "offset": offset}
    if filter:
        params["filter"] = filter
    return _get(conn, "network-services/v1/wifi-clients-locations", params)


@tool(annotations=READ_ONLY)
async def central_get_location_analytics_trends(
    ctx: Context,
    start: Annotated[str | None, Field(description="ISO-8601 start timestamp.")] = None,
    end: Annotated[str | None, Field(description="ISO-8601 end timestamp.")] = None,
    filter: str | None = None,
) -> dict | str:
    """Get location-analytics trend data over a time window.

    Surfaces visitor dwell-time, footfall, and repeat-visitor analytics
    derived from WiFi client locations.
    """
    conn = ctx.lifespan_context["central_conn"]
    params: dict = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    if filter:
        params["filter"] = filter
    return _get(conn, "network-services/v1/location-analytics/trends", params)


@tool(annotations=READ_ONLY)
async def central_get_location_analytics_site_insights(
    ctx: Context,
    filter: str | None = None,
) -> dict | str:
    """Get per-site location-analytics insights (summary KPIs)."""
    conn = ctx.lifespan_context["central_conn"]
    params: dict = {}
    if filter:
        params["filter"] = filter
    return _get(conn, "network-services/v1/location-analytics/sites/insights", params)
