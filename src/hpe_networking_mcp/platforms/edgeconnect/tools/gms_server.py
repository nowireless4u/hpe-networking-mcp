"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``gmsServer``
Operations in this file: 10
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_gms_operating_system",
    description="GET /gmsOperatingSystem\n\nOsInfo364\n\nGet Orchestrator Operating System Type",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_operating_system(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsOperatingSystem",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_operating_system_disk_space_full",
    description="GET /gmsOperatingSystem/diskSpaceFull\n\nDiskSpaceInfoGet365\n\nGet Disk Space Full Notification Status",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_operating_system_disk_space_full(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsOperatingSystem/diskSpaceFull",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_operating_system_root_password_changed",
    description="GET /gmsOperatingSystem/root/passwordChanged\n\nRootPasswordInfoGet367\n\nGet Root Password Changed Status",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_operating_system_root_password_changed(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsOperatingSystem/root/passwordChanged",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_versions",
    description="GET /gms/versions\n\nversionInfo357\n\nGet Orchestrator Version Information",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_versions(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/versions",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gmsserver_brief_info",
    description="GET /gmsserver/briefInfo\n\ngmsBriefInfo400\n\nGet Orchestrator Server Brief Information",
    capability=Capability.READ,
)
async def edgeconnect_get_gmsserver_brief_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsserver/briefInfo",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gmsserver_hello",
    description="GET /gmsserver/hello\n\nhello401\n\nGet Server Instance UUID",
    capability=Capability.READ,
)
async def edgeconnect_get_gmsserver_hello(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsserver/hello",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gmsserver_info",
    description="GET /gmsserver/info\n\ngmsServerInfo402\n\nGet Orchestrator Server Detailed Information",
    capability=Capability.READ,
)
async def edgeconnect_get_gmsserver_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsserver/info",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gmsserver_ping",
    description="GET /gmsserver/ping\n\ngmsPingInfo403\n\nPing Orchestrator Server Health Check",
    capability=Capability.READ,
)
async def edgeconnect_get_gmsserver_ping(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsserver/ping",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_gms_operating_system_root_password_changed",
    description="POST /gmsOperatingSystem/root/passwordChanged\n\nRootPasswordInfoPost368\n\nUpdate Root Password Changed Status",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_operating_system_root_password_changed(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsOperatingSystem/root/passwordChanged",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_gms_operating_system_disk_space_full",
    description="PUT /gmsOperatingSystem/diskSpaceFull\n\nDiskSpaceInfoPut366\n\nDismiss Disk Space Warning Notification",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_operating_system_disk_space_full(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gmsOperatingSystem/diskSpaceFull",
        query_params=None,
        body=body,
    )
