"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Devices - Others``
Operations in this file: 8
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_count_org_other_device_events",
    description="GET /api/v1/orgs/{org_id}/otherdevices/events/count\n\ncountOrgOtherDeviceEvents\n\nCount third-party device events across the organization, optionally grouped by `distinct` and filtered by event type and time range.",
    capability=Capability.READ,
)
async def mist_count_org_other_device_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(description="Field used to group this count response. enum: `mac`, `site_id`, `type`, `vendor`"),
    ] = None,
    type: Annotated[
        str | None,
        Field(description="See [List Device Events Definitions](/#operations/listOtherDeviceEventsDefinitions)"),
    ] = None,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/otherdevices/events/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "type": type,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_delete_org_other_device",
    description="DELETE /api/v1/orgs/{org_id}/otherdevices/{device_mac}\n\ndeleteOrgOtherDevice\n\nDelete a third-party device record from the organization by device MAC address.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_other_device(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/otherdevices/{device_mac}",
        path_params={"org_id": org_id, "device_mac": device_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_other_device",
    description="GET /api/v1/orgs/{org_id}/otherdevices/{device_mac}\n\ngetOrgOtherDevice\n\nRetrieve details for a third-party device record, including vendor, model, serial, attached Mist device MAC address, site assignment, and state.",
    capability=Capability.READ,
)
async def mist_get_org_other_device(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/otherdevices/{device_mac}",
        path_params={"org_id": org_id, "device_mac": device_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_other_devices",
    description="GET /api/v1/orgs/{org_id}/otherdevices\n\nlistOrgOtherDevices\n\nList third-party devices across the organization, such as devices discovered or tracked outside the managed Mist device inventory.",
    capability=Capability.READ,
)
async def mist_list_org_other_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    vendor: Annotated[str | None, Field(description="Filter results by vendor")] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    serial: Annotated[str | None, Field(description="Filter results by device serial number")] = None,
    model: Annotated[str | None, Field(description="Filter results by device model")] = None,
    name: Annotated[str | None, Field(description="Filter results by name")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/otherdevices",
        path_params={"org_id": org_id},
        query_params={
            "vendor": vendor,
            "mac": mac,
            "serial": serial,
            "model": model,
            "name": name,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_reboot_org_other_device",
    description="POST /api/v1/orgs/{org_id}/otherdevices/{device_mac}/reboot\n\nrebootOrgOtherDevice\n\nRequest a reboot for a third-party device by device MAC address.",
    capability=Capability.WRITE,
)
async def mist_reboot_org_other_device(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/otherdevices/{device_mac}/reboot",
        path_params={"org_id": org_id, "device_mac": device_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_other_device_events",
    description="GET /api/v1/orgs/{org_id}/otherdevices/events/search\n\nsearchOrgOtherDeviceEvents\n\nSearch third-party device events across the organization with filters for site, MAC address, attached device MAC address, model, vendor, event type, and time range.",
    capability=Capability.READ,
)
async def mist_search_org_other_device_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    device_mac: Annotated[str | None, Field(description="MAC of attached device")] = None,
    model: Annotated[str | None, Field(description="Filter results by device model")] = None,
    vendor: Annotated[str | None, Field(description="Filter results by vendor")] = None,
    type: Annotated[
        str | None,
        Field(description="See [List Device Events Definitions](/#operations/listOtherDeviceEventsDefinitions)"),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/otherdevices/events/search",
        path_params={"org_id": org_id},
        query_params={
            "site_id": site_id,
            "mac": mac,
            "device_mac": device_mac,
            "model": model,
            "vendor": vendor,
            "type": type,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_other_device",
    description="PUT /api/v1/orgs/{org_id}/otherdevices/{device_mac}\n\nupdateOrgOtherDevice\n\nManually update the site or attached Mist device association for a third-party device when automatic identification is unavailable.",
    capability=Capability.WRITE,
)
async def mist_update_org_other_device(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/otherdevices/{device_mac}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/otherdevices/{device_mac}",
        path_params={"org_id": org_id, "device_mac": device_mac},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_org_other_devices",
    description="PUT /api/v1/orgs/{org_id}/otherdevices\n\nupdateOrgOtherDevices\n\nBulk assign or unassign third-party devices to or from a site by MAC address.",
    capability=Capability.WRITE,
)
async def mist_update_org_other_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/otherdevices"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/otherdevices",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
