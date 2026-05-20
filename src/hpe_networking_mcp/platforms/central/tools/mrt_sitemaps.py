"""Aruba Central Sitemaps tools — floor plans, buildings, walls, zones,
device placement, wall types, and sitemap imports.

Wraps the ``network-monitoring/v1/sitemaps/*`` + ``/wall-types`` +
``/catalogue-aps`` endpoint family. Sitemap operations underpin
location-services accuracy and the floor-plan view in Central's UI.
"""

from typing import Annotated, Literal

from fastmcp import Context
from fastmcp.exceptions import ToolError
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


def _call(conn, method: str, path: str, params: dict | None = None, data: dict | None = None) -> dict:
    response = retry_central_command(
        central_conn=conn,
        api_method=method,
        api_path=path,
        api_params=params or {},
        api_data=data or {},
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# ---------------------------------------------------------------------------
# Sitemap summary + catalogue
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_sitemap_summary(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
) -> dict:
    """Get high-level sitemap summary for a site (counts, floors, devices placed)."""
    conn = ctx.lifespan_context["central_conn"]
    return _call(conn, "GET", f"network-monitoring/v1/sitemaps-summary/{site_id}")


@tool(annotations=READ_ONLY)
async def central_get_catalogue_aps(
    ctx: Context,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """List catalogue APs — the AP models available for placement on floor plans."""
    conn = ctx.lifespan_context["central_conn"]
    return _call(
        conn,
        "GET",
        "network-monitoring/v1/catalogue-aps",
        params={"limit": limit, "offset": offset},
    )


# ---------------------------------------------------------------------------
# Network-device placement (deployed / assigned / planned)
# ---------------------------------------------------------------------------


_DeviceStatus = Literal["deployed", "assigned", "planned"]


@tool(annotations=READ_ONLY)
async def central_get_sitemap_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    status: Annotated[
        _DeviceStatus,
        Field(description="``'deployed'``, ``'assigned'``, or ``'planned'``."),
    ],
) -> dict:
    """List network devices on a site map by lifecycle status.

    ``planned`` = placeholders on the floor plan that haven't been
    associated with a real device. ``assigned`` = real device with
    serial associated to a placement. ``deployed`` = associated AND
    seen online at the placement.
    """
    conn = ctx.lifespan_context["central_conn"]
    return _call(conn, "GET", f"network-monitoring/v1/sitemaps/{site_id}/network-devices-{status}")


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_sitemap_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    action: Annotated[
        Literal["deploy", "undeploy", "assign", "plan", "unplan"],
        Field(description="Lifecycle transition to apply."),
    ],
    payload: Annotated[
        dict,
        Field(
            description="Action body — typically a list of device placements with serial / floor / x / y / rotation."
        ),
    ],
) -> dict:
    """Apply a device-placement lifecycle transition on a site map.

    | action | endpoint |
    |---|---|
    | deploy | POST /sitemaps/:site/network-devices-deployed |
    | undeploy | POST /sitemaps/:site/network-devices-undeploy |
    | assign | POST /sitemaps/:site/network-devices-assigned |
    | plan | POST /sitemaps/:site/network-devices-planned |
    | unplan | DELETE /sitemaps/:site/network-devices-planned |

    Requires ``ENABLE_CENTRAL_WRITE_TOOLS=true``.
    """
    conn = ctx.lifespan_context["central_conn"]
    action_map = {
        "deploy": ("POST", "network-devices-deployed"),
        "undeploy": ("POST", "network-devices-undeploy"),
        "assign": ("POST", "network-devices-assigned"),
        "plan": ("POST", "network-devices-planned"),
        "unplan": ("DELETE", "network-devices-planned"),
    }
    if action not in action_map:
        raise ToolError({"status_code": 400, "message": f"unknown action '{action}'."})
    method, segment = action_map[action]
    response = retry_central_command(
        central_conn=conn,
        api_method=method,
        api_path=f"network-monitoring/v1/sitemaps/{site_id}/{segment}",
        api_data=payload,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "action": action, "site_id": site_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# ---------------------------------------------------------------------------
# Floors
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_floor(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    floor_id: Annotated[str, Field(description="Floor identifier.")],
) -> dict:
    """Get one floor's configuration (dimensions, scale, building, image ref)."""
    conn = ctx.lifespan_context["central_conn"]
    return _call(conn, "GET", f"network-monitoring/v1/sitemaps/{site_id}/floors/{floor_id}")


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_floor(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    action_type: Annotated[
        Literal["create", "update", "delete"],
        Field(description="``'create'`` (POST), ``'update'`` (PUT), or ``'delete'``."),
    ],
    floor_id: Annotated[
        str | None,
        Field(description="Floor identifier. Required for update/delete; ignored for create."),
    ] = None,
    payload: Annotated[
        dict | None,
        Field(description="Floor configuration body. Required for create/update; ignored for delete."),
    ] = None,
) -> dict:
    """Create / update / delete a floor under a site."""
    conn = ctx.lifespan_context["central_conn"]
    if action_type == "create":
        if not payload:
            raise ToolError({"status_code": 400, "message": "``payload`` is required for create."})
        response = retry_central_command(
            central_conn=conn,
            api_method="POST",
            api_path=f"network-monitoring/v1/sitemaps/{site_id}/floors",
            api_data=payload,
        )
    elif action_type == "update":
        if not floor_id or not payload:
            raise ToolError({"status_code": 400, "message": "``floor_id`` and ``payload`` are required for update."})
        response = retry_central_command(
            central_conn=conn,
            api_method="PUT",
            api_path=f"network-monitoring/v1/sitemaps/{site_id}/floors/{floor_id}",
            api_data=payload,
        )
    elif action_type == "delete":
        if not floor_id:
            raise ToolError({"status_code": 400, "message": "``floor_id`` is required for delete."})
        response = retry_central_command(
            central_conn=conn,
            api_method="DELETE",
            api_path=f"network-monitoring/v1/sitemaps/{site_id}/floors/{floor_id}",
        )
    else:
        raise ToolError({"status_code": 400, "message": f"unknown action_type '{action_type}'."})
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "action": action_type, "floor_id": floor_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_set_floor_scale(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    floor_id: Annotated[str, Field(description="Floor identifier.")],
    payload: Annotated[
        dict,
        Field(description="Scale calibration body — typically two anchor points + real-world distance."),
    ],
) -> dict:
    """Set the physical scale calibration for a floor (drives location accuracy)."""
    conn = ctx.lifespan_context["central_conn"]
    response = retry_central_command(
        central_conn=conn,
        api_method="POST",
        api_path=f"network-monitoring/v1/sitemaps/{site_id}/floors/{floor_id}/scale",
        api_data=payload,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "floor_id": floor_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(annotations=READ_ONLY)
async def central_get_floor_image(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    floor_id: Annotated[str, Field(description="Floor identifier.")],
) -> dict:
    """Get the floor-plan image reference / metadata."""
    conn = ctx.lifespan_context["central_conn"]
    return _call(conn, "GET", f"network-monitoring/v1/sitemaps/{site_id}/floors/{floor_id}/image")


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_set_floor_image(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    floor_id: Annotated[str, Field(description="Floor identifier.")],
    payload: Annotated[
        dict,
        Field(description="Image-upload payload — typically a base64 blob or upload URL reference per Central's docs."),
    ],
) -> dict:
    """Upload / replace the floor-plan image for a floor."""
    conn = ctx.lifespan_context["central_conn"]
    response = retry_central_command(
        central_conn=conn,
        api_method="PUT",
        api_path=f"network-monitoring/v1/sitemaps/{site_id}/floors/{floor_id}/image",
        api_data=payload,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "floor_id": floor_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# ---------------------------------------------------------------------------
# Buildings
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_buildings(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
) -> dict:
    """List buildings at a site."""
    conn = ctx.lifespan_context["central_conn"]
    return _call(conn, "GET", f"network-monitoring/v1/sitemaps/{site_id}/buildings")


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_building(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    building_id: Annotated[str, Field(description="Building identifier.")],
    action_type: Annotated[
        Literal["update", "delete"],
        Field(description="``'update'`` (PUT) or ``'delete'``."),
    ],
    payload: Annotated[
        dict | None,
        Field(description="Building body. Required for update; ignored for delete."),
    ] = None,
) -> dict:
    """Update or delete a building. (Create endpoint not exposed by Central MRT.)"""
    conn = ctx.lifespan_context["central_conn"]
    if action_type == "update":
        if not payload:
            raise ToolError({"status_code": 400, "message": "``payload`` is required for update."})
        response = retry_central_command(
            central_conn=conn,
            api_method="PUT",
            api_path=f"network-monitoring/v1/sitemaps/{site_id}/buildings/{building_id}",
            api_data=payload,
        )
    elif action_type == "delete":
        response = retry_central_command(
            central_conn=conn,
            api_method="DELETE",
            api_path=f"network-monitoring/v1/sitemaps/{site_id}/buildings/{building_id}",
        )
    else:
        raise ToolError({"status_code": 400, "message": f"unknown action_type '{action_type}'."})
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "action": action_type, "building_id": building_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# ---------------------------------------------------------------------------
# Sitemap import
# ---------------------------------------------------------------------------


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_import_sitemap(
    ctx: Context,
    site_id: Annotated[str, Field(description="Target site identifier.")],
    payload: Annotated[
        dict,
        Field(
            description="Import-request body — typically references the floor-plan file(s) being imported and metadata."
        ),
    ],
) -> dict:
    """Kick off a sitemap import (bulk floor-plan upload). Poll status via ``central_get_sitemap_import_status``."""
    conn = ctx.lifespan_context["central_conn"]
    response = retry_central_command(
        central_conn=conn,
        api_method="POST",
        api_path=f"network-monitoring/v1/sitemaps/{site_id}/import",
        api_data=payload,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "site_id": site_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(annotations=READ_ONLY)
async def central_get_sitemap_import_status(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    import_id: Annotated[str, Field(description="Import job identifier (from ``central_import_sitemap``).")],
) -> dict:
    """Get the status / result of a sitemap import job."""
    conn = ctx.lifespan_context["central_conn"]
    return _call(conn, "GET", f"network-monitoring/v1/sitemaps/{site_id}/import/{import_id}")


# ---------------------------------------------------------------------------
# Wall types (tenant-global)
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_wall_types(ctx: Context) -> dict:
    """List the wall types configured at the tenant level (used in floor walls)."""
    conn = ctx.lifespan_context["central_conn"]
    return _call(conn, "GET", "network-monitoring/v1/wall-types")


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_wall_types(
    ctx: Context,
    action_type: Annotated[
        Literal["create", "update", "delete"],
        Field(description="``'create'`` (POST), ``'update'`` (PUT), or ``'delete'``."),
    ],
    payload: Annotated[
        dict | None,
        Field(description="Wall-types body — typically a list of {name, attenuation, color, ...}. Ignored for delete."),
    ] = None,
) -> dict:
    """Create / update / delete tenant-global wall types."""
    conn = ctx.lifespan_context["central_conn"]
    method_map = {"create": "POST", "update": "PUT", "delete": "DELETE"}
    if action_type not in method_map:
        raise ToolError({"status_code": 400, "message": f"unknown action_type '{action_type}'."})
    if action_type != "delete" and not payload:
        raise ToolError({"status_code": 400, "message": f"``payload`` is required for {action_type}."})
    response = retry_central_command(
        central_conn=conn,
        api_method=method_map[action_type],
        api_path="network-monitoring/v1/wall-types",
        api_data=payload or {},
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "action": action_type, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# ---------------------------------------------------------------------------
# Floor walls + zones
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_floor_walls(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    floor_id: Annotated[str, Field(description="Floor identifier.")],
) -> dict:
    """List walls placed on a floor (used by location services for signal attenuation modeling)."""
    conn = ctx.lifespan_context["central_conn"]
    return _call(conn, "GET", f"network-monitoring/v1/sitemaps/{site_id}/floors/{floor_id}/walls")


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_floor_walls(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    floor_id: Annotated[str, Field(description="Floor identifier.")],
    action_type: Annotated[
        Literal["create", "update", "delete"],
        Field(description="``'create'`` (POST), ``'update'`` (PUT), or ``'delete'``."),
    ],
    payload: Annotated[
        dict | None,
        Field(description="Wall-set body. Ignored for delete (which clears all walls on the floor)."),
    ] = None,
) -> dict:
    """Manage walls on a floor (create / update / delete the wall set)."""
    conn = ctx.lifespan_context["central_conn"]
    method_map = {"create": "POST", "update": "PUT", "delete": "DELETE"}
    if action_type not in method_map:
        raise ToolError({"status_code": 400, "message": f"unknown action_type '{action_type}'."})
    if action_type != "delete" and not payload:
        raise ToolError({"status_code": 400, "message": f"``payload`` is required for {action_type}."})
    response = retry_central_command(
        central_conn=conn,
        api_method=method_map[action_type],
        api_path=f"network-monitoring/v1/sitemaps/{site_id}/floors/{floor_id}/walls",
        api_data=payload or {},
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "action": action_type, "floor_id": floor_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(annotations=READ_ONLY)
async def central_get_floor_zones(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    floor_id: Annotated[str, Field(description="Floor identifier.")],
) -> dict:
    """List zones placed on a floor (named polygons used for location analytics)."""
    conn = ctx.lifespan_context["central_conn"]
    return _call(conn, "GET", f"network-monitoring/v1/sitemaps/{site_id}/floors/{floor_id}/zones")


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_floor_zones(
    ctx: Context,
    site_id: Annotated[str, Field(description="Site identifier.")],
    floor_id: Annotated[str, Field(description="Floor identifier.")],
    action_type: Annotated[
        Literal["create", "update", "delete"],
        Field(description="``'create'`` (POST), ``'update'`` (PUT), or ``'delete'``."),
    ],
    payload: Annotated[
        dict | None,
        Field(description="Zone-set body. Ignored for delete."),
    ] = None,
) -> dict:
    """Manage zones on a floor (create / update / delete the zone set)."""
    conn = ctx.lifespan_context["central_conn"]
    method_map = {"create": "POST", "update": "PUT", "delete": "DELETE"}
    if action_type not in method_map:
        raise ToolError({"status_code": 400, "message": f"unknown action_type '{action_type}'."})
    if action_type != "delete" and not payload:
        raise ToolError({"status_code": 400, "message": f"``payload`` is required for {action_type}."})
    response = retry_central_command(
        central_conn=conn,
        api_method=method_map[action_type],
        api_path=f"network-monitoring/v1/sitemaps/{site_id}/floors/{floor_id}/zones",
        api_data=payload or {},
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "action": action_type, "floor_id": floor_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}
