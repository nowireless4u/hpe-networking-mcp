from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.central import monitoring_api
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.utils import (
    as_collection,
    fetch_site_data_parallel,
    get_central_conn,
    groups_to_map,
    normalize_site_name_filter,
    retry_central_command,
)

# Write annotations. Central's elicitation middleware enables the
# ``central_write_delete`` tag when ENABLE_CENTRAL_WRITE_TOOLS=true, so ALL
# central write tools carry that tag regardless of destructiveness.
_CONFIRMED_FIELD = Field(
    default=False,
    description=(
        "Fallback confirmation flag — honored only when the client cannot "
        "show a confirmation prompt (the universal gate prompts otherwise)."
    ),
)


async def _scope_write(
    ctx: Context,
    *,
    method: str,
    path: str,
    body: dict,
    action_message: str,
    confirmed: bool,
) -> dict | str:
    """Shared write helper for scope mutation tools.

    Issues the request and returns the response body, raising ``ToolError``
    on non-2xx. Confirmation is handled by the universal gate at the
    invoke-tool dispatch chokepoint (``confirmed`` is the fallback flag
    passed through by the tools).
    """
    conn = get_central_conn(ctx)
    response = await retry_central_command(central_conn=conn, api_method=method, api_path=path, api_data=body)
    code = response.get("code", 0)
    if not 200 <= code < 300:
        msg = response.get("msg", "unknown error")
        raise ToolError({"status_code": code or 502, "message": f"{action_message} failed: {msg}"})
    return response.get("msg", {})


@tool(capability=Capability.READ)
async def central_get_sites(
    ctx: Context,
    filter: str | None = None,
    sort: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """
    Returns site configuration data from Aruba Central (address, timezone, etc.).

    Use this tool when you need site details like address, city, state, country,
    zipcode, timezone, or scopeName. For site health metrics and device/client
    counts, use central_get_site_health instead.

    Parameters:
        filter: OData 4.0 filter string. Supports filtering on scopeName,
            address, city, state, country, zipcode, collectionName.
            Example: "scopeName eq 'Moms House'" or "state eq 'Indiana'"
        sort: Sort by field. One of scopeName, address, state, country, city,
            deviceCount, collectionName, zipcode, timezone, longitude, latitude.
        limit: Number of sites to return (1-100, default 100).
        offset: Offset for pagination (default 0).

    Returns:
        Dict with sites list and pagination info.
    """
    conn = get_central_conn(ctx)
    api_params: dict = {"limit": limit, "offset": offset}
    if filter:
        api_params["filter"] = filter
    if sort:
        api_params["sort"] = sort

    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="network-config/v1/sites",
        api_params=api_params,
    )
    return response.get("msg", {})


@tool(capability=Capability.READ)
async def central_get_site_health(
    ctx: Context,
    site_name: str | list[str] | None = None,
) -> dict:
    """
    Returns health metrics and device/client counts for sites.

    For site configuration data (address, timezone, etc.), use central_get_sites.

    Prefer calling with a site_name filter targeting only the sites you care about.
    Do NOT call without a filter unless the user explicitly requests data for all
    sites — returning all sites is expensive and consumes significant context.

    Recommended workflow: Call central_get_site_name_id_mapping first to get a
    lightweight overview of all sites (names, IDs, health scores). Use health scores
    and alert counts to decide which sites warrant further investigation, then call
    this tool with those specific site names.

    Parameters:
        site_name: One site name or a list of site names to filter by (exact match).
            Accepts either a single string (e.g. "HQ") or a list of strings
            (e.g. ["HQ", "BRANCH-1"]). If omitted, all sites are returned (use sparingly).
    """
    wanted = normalize_site_name_filter(site_name)
    sites_data = await fetch_site_data_parallel(get_central_conn(ctx))
    if wanted:
        return as_collection([sites_data[name] for name in wanted if name in sites_data])
    return as_collection(list(sites_data.values()))


@tool(capability=Capability.READ)
async def central_get_site_name_id_mapping(ctx: Context) -> dict:
    """
    Returns a lightweight mapping of all site names to their IDs and health
    scores. The list is sorted by health score (lowest to highest — worst to best)
    to help quickly identify sites that may need attention. Sites with
    unknown/None health values are placed last.

    Use this before calling central_get_site_health or any endpoint that requires a
    site_id. It is especially useful when the user provides a partial or ambiguous
    site name — verify the correct name here, then pass it to the appropriate tool.
    The health score also helps identify sites with issues before drilling down
    further.

    Returns ``{"items": [...]}`` where each item is a site, sorted worst-health
    first, with:
    - site_name: The site's display name.
    - site_id: Unique identifier used in other API calls.
    - health: Overall health score (0-100, weighted average:
      Good=100, Fair=50, Poor=0).
    - total_devices: Total number of devices at the site.
    - total_clients: Total number of clients at the site.
    - total_alerts: Total number of alerts at the site.
    """
    sites = await monitoring_api.get_all_sites(central_conn=get_central_conn(ctx))
    rows = []
    for site in sites:
        health_obj = groups_to_map(site.get("health", {}))
        summary = None
        if all(k in health_obj for k in ["Poor", "Fair", "Good"]):
            summary = round((health_obj["Poor"] * 0) + (health_obj["Fair"] * 0.5) + (health_obj["Good"] * 1))
        rows.append(
            {
                "site_name": site["siteName"],
                "site_id": site.get("id"),
                "health": summary,
                "total_devices": site.get("devices", {}).get("count", 0),
                "total_clients": site.get("clients", {}).get("count", 0),
                "total_alerts": site.get("alerts", {}).get("total", 0),
            }
        )
    rows.sort(key=lambda r: r["health"] if r["health"] is not None else float("inf"))
    return as_collection(rows)


@tool(capability=Capability.READ)
async def central_get_global_scope(ctx: Context) -> dict | str:
    """Get the Global scope id for the tenant.

    Returns the root/global ``scopeId`` — the top of the Central scope hierarchy.
    Use it as the ``scope_id`` (with ``scope_type='org'``) when rooting
    ``central_get_hierarchy`` at the tenant root.
    """
    conn = get_central_conn(ctx)
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="network-config/v1/global",
        api_params={},
    )
    code = response.get("code", 0)
    if not 200 <= code < 300:
        msg = response.get("msg", "unknown error")
        raise ToolError({"status_code": code or 502, "message": f"Failed to fetch global scope id: {msg}"})
    return response.get("msg", {})


@tool(capability=Capability.READ)
async def central_get_hierarchy(
    ctx: Context,
    scope_id: Annotated[
        str,
        Field(
            description=(
                "scopeId of the resource to root the hierarchy at (site, "
                "site-collection, device-group, or org). Get the tenant-root id "
                "from central_get_global_scope."
            ),
        ),
    ],
    scope_type: Annotated[
        str,
        Field(
            description=(
                "Scope type of scope_id — one of 'org', 'site-collection', 'site', 'device-group', or 'device'."
            ),
        ),
    ],
) -> dict | str:
    """Get the scope hierarchy rooted at a given scope.

    Returns the tree of child scopes (site-collections, sites, device-groups,
    devices) beneath the resource identified by ``scope_id`` + ``scope_type``.
    """
    conn = get_central_conn(ctx)
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="network-config/v1/hierarchy",
        api_params={"id": scope_id, "type": scope_type},
    )
    code = response.get("code", 0)
    if not 200 <= code < 300:
        msg = response.get("msg", "unknown error")
        detail = f"Failed to fetch scope hierarchy for {scope_type} {scope_id!r}: {msg}"
        raise ToolError({"status_code": code or 502, "message": detail})
    return response.get("msg", {})


# ---------------------------------------------------------------------------
# Scope membership writes (device-group / site device assignment)
# ---------------------------------------------------------------------------

_DEVICES_FIELD = Field(description="List of device serial numbers to act on.")


@tool(capability=Capability.WRITE, tags={"central_write_delete"})
async def central_add_devices_to_device_group(
    ctx: Context,
    dest_scope_id: Annotated[
        str, Field(description="scopeId of the destination device-group. Get it from central_get_hierarchy.")
    ],
    devices: Annotated[list[str], _DEVICES_FIELD],
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Add devices to a device-group (POST network-config/v1/device-groups-add-devices)."""
    return await _scope_write(
        ctx,
        method="POST",
        path="network-config/v1/device-groups-add-devices",
        body={"desScopeId": dest_scope_id, "devices": devices},
        action_message=f"Add {len(devices)} device(s) to device-group {dest_scope_id}",
        confirmed=confirmed,
    )


@tool(capability=Capability.WRITE, tags={"central_write_delete"})
async def central_remove_devices_from_device_group(
    ctx: Context,
    devices: Annotated[list[str], _DEVICES_FIELD],
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Remove devices from their device-group (POST network-config/v1/device-groups-remove-devices)."""
    return await _scope_write(
        ctx,
        method="POST",
        path="network-config/v1/device-groups-remove-devices",
        body={"devices": devices},
        action_message=f"Remove {len(devices)} device(s) from their device-group",
        confirmed=confirmed,
    )


@tool(capability=Capability.WRITE, tags={"central_write_delete"})
async def central_create_device_group_with_devices(
    ctx: Context,
    scope_name: Annotated[str, Field(description="Name for the new device-group.")],
    devices: Annotated[list[str], _DEVICES_FIELD],
    description: Annotated[str | None, Field(description="Optional description for the device-group.")] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create a device-group and add its devices in one call.

    POST network-config/v1/device-groups-create-and-add-devices.
    """
    body: dict = {"scopeName": scope_name, "devices": devices}
    if description is not None:
        body["description"] = description
    return await _scope_write(
        ctx,
        method="POST",
        path="network-config/v1/device-groups-create-and-add-devices",
        body=body,
        action_message=f"Create device-group {scope_name!r} with {len(devices)} device(s)",
        confirmed=confirmed,
    )


@tool(capability=Capability.WRITE, tags={"central_write_delete"})
async def central_add_devices_to_site(
    ctx: Context,
    dest_scope_id: Annotated[
        str, Field(description="scopeId of the destination site. Get it from central_get_hierarchy.")
    ],
    devices: Annotated[list[str], _DEVICES_FIELD],
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Add devices to a site (POST network-config/v1/site-add-devices)."""
    return await _scope_write(
        ctx,
        method="POST",
        path="network-config/v1/site-add-devices",
        body={"desScopeId": dest_scope_id, "devices": devices},
        action_message=f"Add {len(devices)} device(s) to site {dest_scope_id}",
        confirmed=confirmed,
    )


# ---------------------------------------------------------------------------
# Scope bulk deletes (destructive)
# ---------------------------------------------------------------------------

_BULK_ITEMS_FIELD = Field(
    description=(
        "List of objects identifying the scopes to delete (each typically "
        "carries the scope `id`). Inspect existing scopes via "
        "central_get_sites / central_get_hierarchy first."
    )
)


@tool(capability=Capability.WRITE_DELETE)
async def central_bulk_delete_device_groups(
    ctx: Context,
    items: Annotated[list[dict], _BULK_ITEMS_FIELD],
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Bulk-delete device-groups (DELETE network-config/v1/device-groups/bulk). Destructive."""
    return await _scope_write(
        ctx,
        method="DELETE",
        path="network-config/v1/device-groups/bulk",
        body={"items": items},
        action_message=f"Bulk-delete {len(items)} device-group(s)",
        confirmed=confirmed,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_bulk_delete_sites(
    ctx: Context,
    items: Annotated[list[dict], _BULK_ITEMS_FIELD],
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Bulk-delete sites (DELETE network-config/v1/sites/bulk). Destructive."""
    return await _scope_write(
        ctx,
        method="DELETE",
        path="network-config/v1/sites/bulk",
        body={"items": items},
        action_message=f"Bulk-delete {len(items)} site(s)",
        confirmed=confirmed,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_bulk_delete_site_collections(
    ctx: Context,
    items: Annotated[list[dict], _BULK_ITEMS_FIELD],
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Bulk-delete site-collections (DELETE network-config/v1/site-collections/bulk). Destructive."""
    return await _scope_write(
        ctx,
        method="DELETE",
        path="network-config/v1/site-collections/bulk",
        body={"items": items},
        action_message=f"Bulk-delete {len(items)} site-collection(s)",
        confirmed=confirmed,
    )
