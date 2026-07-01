"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/data-services.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``data-services``   Tag: ``secrets``   Operations: 5
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
    name="greenlake_delete_data_services_v1beta1_secrets_id",
    description="DELETE /data-services/v1beta1/secrets/{id}\n\nRemoveSecretV1\n\nRemoves a secret",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_data_services_v1beta1_secrets_id(
    ctx: Context,
    id: Annotated[str, Field(description="UUID of the secret")],
    safe: Annotated[bool | None, Field(default=None, description="Enable delete-lock safety checking")] = None,
    x_envoy_external_address: Annotated[
        str | None, Field(default=None, description="header parameter 'x-envoy-external-address'")
    ] = None,
    x_forwarded_for: Annotated[
        str | None, Field(default=None, description="header parameter 'x-forwarded-for'")
    ] = None,
) -> Any:
    path = f"/data-services/v1beta1/secrets/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if safe is not None:
        query_params["safe"] = safe
    header_params: dict[str, str] = {}
    if x_envoy_external_address is not None:
        header_params["x-envoy-external-address"] = str(x_envoy_external_address)
    if x_forwarded_for is not None:
        header_params["x-forwarded-for"] = str(x_forwarded_for)
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_data_services_v1beta1_secrets",
    description="GET /data-services/v1beta1/secrets\n\nReportSecretsV1\n\nReports filtered secrets",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_secrets(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='An OData expression to filter responses by attribute. The OData logical operator "eq" is case-sensitive and supported for attributes "classifier", "label", "name", "service", "status" and "subclassifier". The OData function "contains()" is not case-sensitive and supported for attributes "label", "name" and "service". The OData logical operator "and" is supported for all attributes.',
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A response attribute to sort by, followed by a direction indicator ("asc" or "desc"). The attribute may be one of "assignmentsCount", "classifier", "createdAt", "createdBy", "id", "label", "lastUpdatedBy", "name", "service", "status", "subclassifier" or "updatedAt". Default: ascending.',
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
        "/data-services/v1beta1/secrets",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_data_services_v1beta1_secrets_id",
    description="GET /data-services/v1beta1/secrets/{id}\n\nReportSecretV1\n\nReports a specific secret",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_secrets_id(
    ctx: Context,
    id: Annotated[str, Field(description="UUID of the secret")],
) -> Any:
    path = f"/data-services/v1beta1/secrets/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_data_services_v1beta1_secrets_id",
    description="PATCH /data-services/v1beta1/secrets/{id}\n\nChangeSecretV1\n\nChanges a secret",
    capability=Capability.WRITE,
)
async def greenlake_patch_data_services_v1beta1_secrets_id(
    ctx: Context,
    id: Annotated[str, Field(description="UUID of the secret")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    x_envoy_external_address: Annotated[
        str | None, Field(default=None, description="header parameter 'x-envoy-external-address'")
    ] = None,
    x_forwarded_for: Annotated[
        str | None, Field(default=None, description="header parameter 'x-forwarded-for'")
    ] = None,
) -> Any:
    path = f"/data-services/v1beta1/secrets/{path_seg(id)}"
    header_params: dict[str, str] = {}
    if x_envoy_external_address is not None:
        header_params["x-envoy-external-address"] = str(x_envoy_external_address)
    if x_forwarded_for is not None:
        header_params["x-forwarded-for"] = str(x_forwarded_for)
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_data_services_v1beta1_secrets",
    description="POST /data-services/v1beta1/secrets\n\nAddSecretV1\n\nAdds a secret",
    capability=Capability.WRITE,
)
async def greenlake_post_data_services_v1beta1_secrets(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    x_envoy_external_address: Annotated[
        str | None, Field(default=None, description="header parameter 'x-envoy-external-address'")
    ] = None,
    x_forwarded_for: Annotated[
        str | None, Field(default=None, description="header parameter 'x-forwarded-for'")
    ] = None,
) -> Any:
    header_params: dict[str, str] = {}
    if x_envoy_external_address is not None:
        header_params["x-envoy-external-address"] = str(x_envoy_external_address)
    if x_forwarded_for is not None:
        header_params["x-forwarded-for"] = str(x_forwarded_for)
    return await greenlake_request(
        ctx,
        "POST",
        "/data-services/v1beta1/secrets",
        header_params=header_params or None,
        body=body,
    )
