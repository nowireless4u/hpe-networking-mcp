"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs JSI``
Operations in this file: 10
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
    name="mist_adopt_org_jsi_device",
    description="GET /api/v1/orgs/{org_id}/jsi/devices/outbound_ssh_cmd\n\nadoptOrgJsiDevice\n\nAdopt JSI devices",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_adopt_org_jsi_device(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/jsi/devices/outbound_ssh_cmd",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_count_org_jsi_assets_and_contracts",
    description="GET /api/v1/orgs/{org_id}/jsi/inventory/count\n\ncountOrgJsiAssetsAndContracts\n\nCount devices purchased from the accounts associated with the Org",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_jsi_assets_and_contracts(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="Distinct attributes to count")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/jsi/inventory/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_count_org_jsi_pbn",
    description="GET /api/v1/orgs/{org_id}/jsi/pbn/count\n\ncountOrgJsiPbn\n\nGet count of PBN advisories grouped by specified field",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_jsi_pbn(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any, Field(description="Field to group by enum: `versions`, `models`, `customer_risk`, `bug_type`")
    ],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/jsi/pbn/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "limit": limit, "start": start, "end": end},
        body=None,
    )


@_mcp_tool(
    name="mist_count_org_jsi_sirt",
    description="GET /api/v1/orgs/{org_id}/jsi/sirt/count\n\ncountOrgJsiSirt\n\nGet count of SIRT advisories grouped by specified field",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_jsi_sirt(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any, Field(description="Field to group by. enum: `jsa_updated_date`, `models`, `severity`, `versions`")
    ],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/jsi/sirt/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "limit": limit, "start": start, "end": end},
        body=None,
    )


@_mcp_tool(
    name="mist_create_org_jsi_device_shell_session",
    description="POST /api/v1/orgs/{org_id}/jsi/devices/{device_mac}/shell\n\ncreateOrgJsiDeviceShellSession\n\nCreate Shell Session",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_jsi_device_shell_session(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/jsi/devices/{device_mac}/shell",
        path_params={"org_id": org_id, "device_mac": device_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_jsi_devices",
    description="GET /api/v1/orgs/{org_id}/jsi/devices\n\nlistOrgJsiDevices\n\nGet List of Org devices that connected to JSI",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_jsi_devices(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
    model: Annotated[str | None, Field(description="Device model")] = None,
    serial: Annotated[str | None, Field(description="Device serial")] = None,
    mac: Annotated[str | None, Field(description="Device MAC Address")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/jsi/devices",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page, "model": model, "serial": serial, "mac": mac},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_jsi_past_purchases",
    description="GET /api/v1/orgs/{org_id}/jsi/inventory\n\nlistOrgJsiPastPurchases\n\nThis gets all devices purchased from the accounts associated with the Org \n  * Fetch Install base devices for all linked accounts and associated account of the linked accounts. \n  * The primary and the associated account ids will be queries from SFDC by passing the linked account \n  * Returns only the device centric details of the Install base device. No customer specific information will be returned.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_jsi_past_purchases(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
    model: Annotated[str | None, Field(description="query parameter 'model'")] = None,
    serial: Annotated[str | None, Field(description="query parameter 'serial'")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/jsi/inventory",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page, "model": model, "serial": serial},
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_jsi_assets_and_contracts",
    description="GET /api/v1/orgs/{org_id}/jsi/inventory/search\n\nsearchOrgJsiAssetsAndContracts\n\nThis gets all devices purchased from the accounts associated with the Org \n  * Fetch Install base devices for all linked accounts and associated account of the linked accounts. \n  * The primary and the associated account ids will be queries from SFDC by passing the linked account \n  * Returns only the device centric details of the Install base device. No customer specific information will be returned.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_jsi_assets_and_contracts(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    claimed: Annotated[
        bool | None, Field(description="Device claim status, `true` for claimed devices, `false` for all devices")
    ] = None,
    model: Annotated[str | None, Field(description="Device model")] = None,
    serial: Annotated[str | None, Field(description="Device serial")] = None,
    sku: Annotated[str | None, Field(description="SKU name of the device")] = None,
    status: Annotated[Any | None, Field(description="Device status")] = None,
    warranty_type: Annotated[Any | None, Field(description="Device warranty type")] = None,
    eol_after: Annotated[str | None, Field(description="Filter devices with End Of Life date after this date")] = None,
    eol_before: Annotated[
        str | None, Field(description="Filter devices with End Of Life date before this date")
    ] = None,
    eos_after: Annotated[
        str | None, Field(description="Filter devices with End Of Support date after this date")
    ] = None,
    eos_before: Annotated[
        str | None, Field(description="Filter devices with End Of Support date before this date")
    ] = None,
    version_eos_after: Annotated[
        str | None, Field(description="Filter devices with OS Version End Of Support date after this date")
    ] = None,
    version_eos_before: Annotated[
        str | None, Field(description="Filter devices with OS Version End Of Support date before this date")
    ] = None,
    has_support: Annotated[
        bool | None, Field(description="Indicates if the device is covered under active support contract")
    ] = None,
    sirt_id: Annotated[
        str | None, Field(description="To get the onboarded devices that are affected by the SIRT ID")
    ] = None,
    pbn_id: Annotated[
        str | None, Field(description="To get the onboarded devices that are affected by the PBN ID")
    ] = None,
    text: Annotated[str | None, Field(description="Wildcards for `serial`, `model`, `account_id`")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
        "/api/v1/orgs/{org_id}/jsi/inventory/search",
        path_params={"org_id": org_id},
        query_params={
            "claimed": claimed,
            "model": model,
            "serial": serial,
            "sku": sku,
            "status": status,
            "warranty_type": warranty_type,
            "eol_after": eol_after,
            "eol_before": eol_before,
            "eos_after": eos_after,
            "eos_before": eos_before,
            "version_eos_after": version_eos_after,
            "version_eos_before": version_eos_before,
            "has_support": has_support,
            "sirt_id": sirt_id,
            "pbn_id": pbn_id,
            "text": text,
            "limit": limit,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_jsi_pbn",
    description="GET /api/v1/orgs/{org_id}/jsi/pbn/search\n\nsearchOrgJsiPbn\n\nText search for PBN (Problem Bug Notification) advisories. Search can be done on versions, models, customer_risk, id, and bug_type fields.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_jsi_pbn(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    versions: Annotated[str | None, Field(description="OS versions to search for")] = None,
    models: Annotated[str | None, Field(description="Device models to search for")] = None,
    customer_risk: Annotated[str | None, Field(description="Customer risk level to filter by")] = None,
    id: Annotated[str | None, Field(description="PBN ID to search for")] = None,
    bug_type: Annotated[str | None, Field(description="Bug type to filter by")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/jsi/pbn/search",
        path_params={"org_id": org_id},
        query_params={
            "versions": versions,
            "models": models,
            "customer_risk": customer_risk,
            "id": id,
            "bug_type": bug_type,
            "limit": limit,
            "page": page,
            "search_after": search_after,
            "start": start,
            "end": end,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_jsi_sirt",
    description="GET /api/v1/orgs/{org_id}/jsi/sirt/search\n\nsearchOrgJsiSirt\n\nSearch and get all the SIRT for the onboarded devices. Search can be done on severity, id, updated_after, updated_before, published_after, published_before, models, versions, and text fields.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_jsi_sirt(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    severity: Annotated[str | None, Field(description="Severity of the SIRT (Critical, High, Medium, Low)")] = None,
    id: Annotated[str | None, Field(description="JSA number")] = None,
    updated_after: Annotated[str | None, Field(description="JSA Updated date to be filtered after this date")] = None,
    updated_before: Annotated[str | None, Field(description="JSA Updated date to be filtered before this date")] = None,
    published_after: Annotated[
        str | None, Field(description="JSA Published date to be filtered after this date")
    ] = None,
    published_before: Annotated[
        str | None, Field(description="JSA Published date to be filtered before this date")
    ] = None,
    models: Annotated[str | None, Field(description="Models affected by the SIRT")] = None,
    versions: Annotated[str | None, Field(description="Software version affected by the SIRT")] = None,
    text: Annotated[
        str | None, Field(description="Wildcards search on os_version_affected, affected_models, severity, jsa_id")
    ] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/jsi/sirt/search",
        path_params={"org_id": org_id},
        query_params={
            "severity": severity,
            "id": id,
            "updated_after": updated_after,
            "updated_before": updated_before,
            "published_after": published_after,
            "published_before": published_before,
            "models": models,
            "versions": versions,
            "text": text,
            "limit": limit,
            "page": page,
            "sort": sort,
            "search_after": search_after,
            "start": start,
            "end": end,
        },
        body=None,
    )
