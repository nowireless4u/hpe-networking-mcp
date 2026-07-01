"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/service-catalog__service-provision-nbapi-v1beta1-service-provision-v1beta1.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``service-catalog``   Tag: ``service_provisions``   Operations: 7
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
    name="greenlake_delete_service_catalog_v1beta1_service_provisions_id",
    description="DELETE /service-catalog/v1beta1/service-provisions/{id}\n\ndeleteServiceProvision\n\nUnprovision and delete Service Provision entry",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_service_catalog_v1beta1_service_provisions_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service provision ID")],
    If_Match: Annotated[int, Field(description="Generation version match")],
    force: Annotated[
        bool | None,
        Field(default=None, description="Specifies the force-delete action (irrespective of provision status)"),
    ] = None,
) -> Any:
    path = f"/service-catalog/v1beta1/service-provisions/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    header_params: dict[str, str] = {}
    if If_Match is not None:
        header_params["If-Match"] = str(If_Match)
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1beta1_service_provisions",
    description="GET /service-catalog/v1beta1/service-provisions\n\ngetServiceProvisions\n\nGet Service Provisions",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1beta1_service_provisions(
    ctx: Context,
    Hpe_workspace_id: Annotated[
        str | None, Field(default=None, description="Is required for (only) App API if view all is false")
    ] = None,
    next: Annotated[
        str | None, Field(default=None, description="Specifies the start-id for the next page of service offers.")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of entries per page")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Supports Odata format. <br> **Supported Fields:** id, ServiceOfferId, workspaceId, serviceManagerProvisionId, serviceManagerId, serviceManagerInstanceId, status, organizationId, slug. <br> **Supported operand:** _eq_ <br> **Supported operations:** _and_",
        ),
    ] = None,
    unredacted: Annotated[
        bool | None,
        Field(default=None, description="Get entire entry along with sensitive fields corresponding to user workspace"),
    ] = None,
    all: Annotated[bool | None, Field(default=None, description="Get unredacted entries for all workspaces")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if next is not None:
        query_params["next"] = next
    if limit is not None:
        query_params["limit"] = limit
    if filter is not None:
        query_params["filter"] = filter
    if unredacted is not None:
        query_params["unredacted"] = unredacted
    if all is not None:
        query_params["all"] = all
    header_params: dict[str, str] = {}
    if Hpe_workspace_id is not None:
        header_params["Hpe-workspace-id"] = str(Hpe_workspace_id)
    return await greenlake_request(
        ctx,
        "GET",
        "/service-catalog/v1beta1/service-provisions",
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1beta1_service_provisions_id",
    description="GET /service-catalog/v1beta1/service-provisions/{id}\n\ngetServiceProvision\n\nGet Service Provision",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1beta1_service_provisions_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service provision ID")],
    unredacted: Annotated[
        bool | None,
        Field(default=None, description="Get entire entry along with sensitive fields corresponding to user workspace"),
    ] = None,
) -> Any:
    path = f"/service-catalog/v1beta1/service-provisions/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if unredacted is not None:
        query_params["unredacted"] = unredacted
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_service_catalog_v1beta1_service_provisions",
    description="POST /service-catalog/v1beta1/service-provisions\n\npostServiceProvision\n\nCreate Service Provision",
    capability=Capability.WRITE,
)
async def greenlake_post_service_catalog_v1beta1_service_provisions(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/service-catalog/v1beta1/service-provisions",
        body=body,
    )


@tool(
    name="greenlake_post_service_catalog_v1beta1_service_provisions_id_retry",
    description="POST /service-catalog/v1beta1/service-provisions/{id}/retry\n\nretryServiceProvision\n\nRetrigger Service provisioning in case it failed previously",
    capability=Capability.WRITE,
)
async def greenlake_post_service_catalog_v1beta1_service_provisions_id_retry(
    ctx: Context,
    id: Annotated[str, Field(description="Service provision ID")],
) -> Any:
    path = f"/service-catalog/v1beta1/service-provisions/{path_seg(id)}/retry"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_service_catalog_v1beta1_service_provisions_id_retry_unprovision",
    description="POST /service-catalog/v1beta1/service-provisions/{id}/retry-unprovision\n\nretryServiceUnprovision\n\nRetrigger Service Unprovisioning in case it failed previously",
    capability=Capability.WRITE,
)
async def greenlake_post_service_catalog_v1beta1_service_provisions_id_retry_unprovision(
    ctx: Context,
    id: Annotated[str, Field(description="Service provision ID")],
) -> Any:
    path = f"/service-catalog/v1beta1/service-provisions/{path_seg(id)}/retry-unprovision"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_service_catalog_v1beta1_service_provisions_id_retry_workspace_transfer",
    description="POST /service-catalog/v1beta1/service-provisions/{id}/retry-workspace-transfer\n\nretryWorkspaceTransfer\n\nRetry Workspace Transfer",
    capability=Capability.WRITE,
)
async def greenlake_post_service_catalog_v1beta1_service_provisions_id_retry_workspace_transfer(
    ctx: Context,
    id: Annotated[str, Field(description="Service provision ID")],
) -> Any:
    path = f"/service-catalog/v1beta1/service-provisions/{path_seg(id)}/retry-workspace-transfer"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )
