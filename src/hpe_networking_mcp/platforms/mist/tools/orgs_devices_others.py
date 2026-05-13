"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Devices - Others``
Operations in this file: 8
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_count_org_other_device_events",
    description="GET /api/v1/orgs/{org_id}/otherdevices/events/count\n\ncountOrgOtherDeviceEvents\n\nCount by Distinct Attributes of Org OtherDevices Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_other_device_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    type: Annotated[
        str | None,
        Field(description="See [List Device Events Definitions](/#operations/listOtherDeviceEventsDefinitions)"),
    ] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
    description="DELETE /api/v1/orgs/{org_id}/otherdevices/{device_mac}\n\ndeleteOrgOtherDevice\n\nDelete OtherDevice",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    description="GET /api/v1/orgs/{org_id}/otherdevices/{device_mac}\n\ngetOrgOtherDevice\n\nGet Org other device (3rd party device)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/otherdevices\n\nlistOrgOtherDevices\n\nGet List of Org other devices (3rd party devices)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_other_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    vendor: Annotated[str | None, Field(description="query parameter 'vendor'")] = None,
    mac: Annotated[str | None, Field(description="query parameter 'mac'")] = None,
    serial: Annotated[str | None, Field(description="query parameter 'serial'")] = None,
    model: Annotated[str | None, Field(description="query parameter 'model'")] = None,
    name: Annotated[str | None, Field(description="query parameter 'name'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
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
    description="POST /api/v1/orgs/{org_id}/otherdevices/{device_mac}/reboot\n\nrebootOrgOtherDevice\n\nReboot OtherDevice",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/otherdevices/events/search\n\nsearchOrgOtherDeviceEvents\n\nSearch Org OtherDevices Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_other_device_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[str | None, Field(description="Site id")] = None,
    mac: Annotated[str | None, Field(description="MAC")] = None,
    device_mac: Annotated[str | None, Field(description="MAC of attached device")] = None,
    model: Annotated[str | None, Field(description="Device model")] = None,
    vendor: Annotated[str | None, Field(description="Vendor name")] = None,
    type: Annotated[
        str | None,
        Field(description="See [List Device Events Definitions](/#operations/listOtherDeviceEventsDefinitions)"),
    ] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
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
    description="PUT /api/v1/orgs/{org_id}/otherdevices/{device_mac}\n\nupdateOrgOtherDevice\n\nIf the Site / Device cannot be identified, a manual association can be made",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="PUT /api/v1/orgs/{org_id}/otherdevices\n\nupdateOrgOtherDevices\n\nAssign or unassign OtherDevices to and from a site.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
