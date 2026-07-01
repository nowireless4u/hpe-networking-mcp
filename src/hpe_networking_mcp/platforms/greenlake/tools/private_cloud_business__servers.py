"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/private-cloud-business.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``private-cloud-business``   Tag: ``servers``   Operations: 2
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_private_cloud_business_v1beta1_systems_id_servers",
    description="GET /private-cloud-business/v1beta1/systems/{id}/servers\n\nGetSystemServersInfo\n\nGet information about the specified system's servers.",
    capability=Capability.READ,
)
async def greenlake_get_private_cloud_business_v1beta1_systems_id_servers(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Identifier of the system, usually a UUID.")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query parameter listing the properties of Server information to fetch."),
    ] = None,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description="Use offset in conjunction with limit for paging, e.g.: offset=30&&limit=10. Offset is the number of items from the beginning of the result set to the first item included in the response.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Use limit in conjunction with offset for paging, e.g.: offset=30&&limit=10. Limit is the maximum number of items to include in the response.",
        ),
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="The expression to filter responses.")] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A comma separated list of properties to sort by, followed by a direction indicator ("asc" or "desc"). If no direction indicator is specified the default order is ascending.',
        ),
    ] = None,
) -> Any:
    path = f"/private-cloud-business/v1beta1/systems/{path_seg(id)}/servers"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_private_cloud_business_v1beta1_systems_system_id_servers_server_id",
    description="GET /private-cloud-business/v1beta1/systems/{systemId}/servers/{serverId}\n\nGetSystemServerInfo\n\nGet information about a system's specific server.",
    capability=Capability.READ,
)
async def greenlake_get_private_cloud_business_v1beta1_systems_system_id_servers_server_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="Unique Identifier of the system, usually a UUID.")],
    serverId: Annotated[str, Field(description="Unique Identifier of the Server, usually a UUID.")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query parameter listing the properties of Server information to fetch."),
    ] = None,
) -> Any:
    path = f"/private-cloud-business/v1beta1/systems/{path_seg(systemId)}/servers/{path_seg(serverId)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )
