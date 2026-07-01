"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/data-services.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``data-services``   Tag: ``software_releases``   Operations: 3
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_data_services_v1beta1_software_releases",
    description="GET /data-services/v1beta1/software-releases\n\nSoftwareReleasesList\n\nList Software Releases",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_software_releases(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="An expression to filter list query results. Query result items that match the given filter are returned.  Expressions must be in the format `\\<property> <operator> \\<value>` or `\\<value> <operator> \\<property>`. The available operators are:  - `eq`: Test whether a property's value is equal to a literal. - `in`: Test whether a property's value appears in a list of literals.  Literals can be:  - GUIDs, such as `ae09cc99-57e1-4f82-9d80-e68698da641b`. - Strings, such as `'hello'`, `'world'`.  Expressions can also be joined using the `and` and `or` logical operators.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="The number of query results to return. Use limit in conjuction with offset for paging.",
        ),
    ] = None,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description="The offset to use for paging through the result set. Use offset in conjunction with limit for paging.",
        ),
    ] = None,
    select: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="Comma separated properties to return in the result. If omitted, all properties will be returned. This is applied to sub-properties of the objects in the items array. Selecting nested properties of an object is not supported.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="One or more properties and directions to sort query results by. A direction is optional and can be either `asc` or `desc` for ascending and descending order respectively. If the direction is omitted it defaults to `asc`.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
    if sort is not None:
        query_params["sort"] = sort
    return await greenlake_request(
        ctx,
        "GET",
        "/data-services/v1beta1/software-releases",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_data_services_v1beta1_software_releases_id",
    description="GET /data-services/v1beta1/software-releases/{id}\n\nSoftwareReleasesGet\n\nGet a Software Release",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_software_releases_id(
    ctx: Context,
    id: Annotated[str, Field(description="The ID of a Software Release.")],
    select: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="Comma separated properties to return in the result. If omitted, all properties will be returned. Selecting nested properties of an object is not supported.",
        ),
    ] = None,
) -> Any:
    path = f"/data-services/v1beta1/software-releases/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_data_services_v1beta1_software_releases_id_download",
    description="POST /data-services/v1beta1/software-releases/{id}/download\n\nSoftwareReleasesDownload\n\nDownload a Software Release file",
    capability=Capability.WRITE,
)
async def greenlake_post_data_services_v1beta1_software_releases_id_download(
    ctx: Context,
    id: Annotated[str, Field(description="The ID of a Software Release.")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/data-services/v1beta1/software-releases/{path_seg(id)}/download"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
