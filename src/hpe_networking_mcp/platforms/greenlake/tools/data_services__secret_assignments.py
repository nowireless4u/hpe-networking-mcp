"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/data-services.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``data-services``   Tag: ``secret_assignments``   Operations: 2
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
    name="greenlake_get_data_services_v1beta1_secret_assignments",
    description="GET /data-services/v1beta1/secret-assignments\n\nReportAssignmentsV1\n\nReports filtered assignments",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_secret_assignments(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='An OData expression to filter responses by attribute. The OData logical operator "eq" is case-sensitive and supported for attributes "applianceId", "secretId", "goal", "service", or "status". The OData function "contains()" is not case-sensitive and supported for attribute "applianceId", "secretId", and "service". The OData logical operator "and" is supported for all attributes.',
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A response attribute to sort by, followed by a direction indicator ("asc" or "desc"). The attribute may be one of "applianceId", "secretId", "createdAt", "goal", "id", "label", "service", "status" or "updatedAt". Default: ascending.',
        ),
    ] = None,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description="The offset query parameter should be used in conjunction with limit for paging within a batched result set. The offset is the number of items from the beginning of the batched result set to the first item included in the response. Example: offset=30&limit=10",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="The limit query parameter should be used in conjunction with offset for paging within a batched result set. The limit is the maximum number of items to include in the response. Example: offset=30&limit=10",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/data-services/v1beta1/secret-assignments",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_data_services_v1beta1_secret_assignments_id",
    description="GET /data-services/v1beta1/secret-assignments/{id}\n\nReportAssignmentV1\n\nReports a specific assignment",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_secret_assignments_id(
    ctx: Context,
    id: Annotated[str, Field(description="UUID of the secret")],
) -> Any:
    path = f"/data-services/v1beta1/secret-assignments/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
