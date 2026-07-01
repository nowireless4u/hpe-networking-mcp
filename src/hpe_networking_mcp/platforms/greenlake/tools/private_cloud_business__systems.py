"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/private-cloud-business.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``private-cloud-business``   Tag: ``systems``   Operations: 10
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
    name="greenlake_get_private_cloud_business_v1beta1_system_software_catalogs",
    description="GET /private-cloud-business/v1beta1/system-software-catalogs\n\nGetSystemSoftwareCatalogs\n\nGet all System Software Catalogs.",
    capability=Capability.READ,
)
async def greenlake_get_private_cloud_business_v1beta1_system_software_catalogs(
    ctx: Context,
    select: Annotated[
        str | None,
        Field(default=None, description="A list of properties in the items collection to include in the response."),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The expression to filter responses. The property names which are of type string should be passed in quotes('') and nested property names should be passed with \"/\" as the separator. Filtering is supported with following properties:  * eula  * createdAt  * customerId  * generation  * id  * name  * resourceUri  * type  * updatedAt  * hypervisor/name  * hypervisor/releaseDate  * hypervisor/releaseNotesUrl  * hypervisor/version  * releaseDate  * serverFirmware/name  * serverFirmware/releaseDate  * serverFirmware/releaseNotesUrl  * serverFirmware/version  * storageConnectionManager/name  * storageConnectionManager/releaseDate  * storageConnectionManager/releaseNotesUrl  * storageConnectionManager/version  * storageSoftware/name  * storageSoftware/releaseDate  * storageSoftware/releaseNotesUrl  * storageSoftware/version  * version",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Use limit in conjunction with offset for paging, e.g.: offset=30&&limit=10. Limit is the maximum number of items to include in the response.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if filter is not None:
        query_params["filter"] = filter
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/private-cloud-business/v1beta1/system-software-catalogs",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_private_cloud_business_v1beta1_system_software_catalogs_id",
    description="GET /private-cloud-business/v1beta1/system-software-catalogs/{id}\n\nGetSystemSoftwareCatalogById\n\nGet the System Software Catalog with specified id.",
    capability=Capability.READ,
)
async def greenlake_get_private_cloud_business_v1beta1_system_software_catalogs_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    select: Annotated[
        str | None,
        Field(default=None, description="A list of properties in the items collection to include in the response."),
    ] = None,
) -> Any:
    path = f"/private-cloud-business/v1beta1/system-software-catalogs/{path_seg(id)}"
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
    name="greenlake_get_private_cloud_business_v1beta1_systems",
    description="GET /private-cloud-business/v1beta1/systems\n\nListSystemInfo\n\nGet information about all systems subject to query parameters.",
    capability=Capability.READ,
)
async def greenlake_get_private_cloud_business_v1beta1_systems(
    ctx: Context,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Query parameter listing the properties of system information to fetch. Although Hypervisor Clusters collection (property hypervisorClusters) can be selected, selecting elements of the collection is not supported. Similarly, hypervisor clusters update status collection (property softwareInfo.hypervisorClusters) can be selected, but, selecting elements of the collection is not supported in the select query parameter. Although systemVms collection can be selected, selecting elements of the collection is not supported.",
        ),
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
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The expression to filter responses. This API doesn't support filtering based on hypervisorClusters collection property, softwareInfo.hypervisorClusters and systemVms collection property. Request with filter based on the above mentioned properties will be treated as a Bad Request with 400 Error.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A comma separated list of properties to sort by, followed by a direction indicator ("asc" or "desc"). If no direction indicator is specified the default order is ascending. This API doesn\'t support sorting based on hypervisorClusters collection property, softwareInfo.hypervisorClusters collection property and systemVms collection property. Request with sort based on the above mentioned properties will be treated as a Bad Request with 400 Error.',
        ),
    ] = None,
) -> Any:
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
        "/private-cloud-business/v1beta1/systems",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_private_cloud_business_v1beta1_systems_id",
    description="GET /private-cloud-business/v1beta1/systems/{id}\n\nGetSystemInfo\n\nGet information about the specified system subject to query parameters.",
    capability=Capability.READ,
)
async def greenlake_get_private_cloud_business_v1beta1_systems_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Identifier of the system, usually a UUID.")],
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Query parameter listing the properties of system information to fetch. Although Hypervisor Clusters collection (property hypervisorClusters) can be selected, selecting elements of the collection is not supported. Similarly, hypervisor clusters update status collection (property softwareInfo.hypervisorClusters) can be selected, but, selecting elements of the collection is not supported in the select query parameter.",
        ),
    ] = None,
) -> Any:
    path = f"/private-cloud-business/v1beta1/systems/{path_seg(id)}"
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
    name="greenlake_patch_private_cloud_business_v1beta1_systems_id",
    description="PATCH /private-cloud-business/v1beta1/systems/{id}\n\nPatchSystem\n\nModifies the system specified by systemId.",
    capability=Capability.WRITE,
)
async def greenlake_patch_private_cloud_business_v1beta1_systems_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Identifier of the system, usually a UUID.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/private-cloud-business/v1beta1/systems/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_private_cloud_business_v1beta1_systems_id_add_hypervisor_cluster",
    description="POST /private-cloud-business/v1beta1/systems/{id}/add-hypervisor-cluster\n\nAddHypervisorClusterToSystem\n\nInitiates addition of a hypervisor cluster to system with the given id.",
    capability=Capability.WRITE,
)
async def greenlake_post_private_cloud_business_v1beta1_systems_id_add_hypervisor_cluster(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Identifier of the system, usually a UUID.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/private-cloud-business/v1beta1/systems/{path_seg(id)}/add-hypervisor-cluster"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_private_cloud_business_v1beta1_systems_id_software_prechecks",
    description="POST /private-cloud-business/v1beta1/systems/{id}/software-prechecks\n\nInitiateSoftwarePrechecks\n\nInitiate software update prechecks on the given System.",
    capability=Capability.WRITE,
)
async def greenlake_post_private_cloud_business_v1beta1_systems_id_software_prechecks(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Identifier of the System, usually a UUID.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/private-cloud-business/v1beta1/systems/{path_seg(id)}/software-prechecks"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_private_cloud_business_v1beta1_systems_id_software_update",
    description="POST /private-cloud-business/v1beta1/systems/{id}/software-update\n\nInitiateSoftwareUpdate\n\nInitiate software update on the given System.",
    capability=Capability.WRITE,
)
async def greenlake_post_private_cloud_business_v1beta1_systems_id_software_update(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Identifier of the System, usually a UUID.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/private-cloud-business/v1beta1/systems/{path_seg(id)}/software-update"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_private_cloud_business_v1beta1_systems_id_software_update_resume",
    description="POST /private-cloud-business/v1beta1/systems/{id}/software-update-resume\n\nInitiateSoftwareUpdateResume\n\nResume the failed and paused software update on the selected System.",
    capability=Capability.WRITE,
)
async def greenlake_post_private_cloud_business_v1beta1_systems_id_software_update_resume(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Identifier of the System, usually a UUID.")],
) -> Any:
    path = f"/private-cloud-business/v1beta1/systems/{path_seg(id)}/software-update-resume"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_private_cloud_business_v1beta1_systems_id_software_version_refresh",
    description="POST /private-cloud-business/v1beta1/systems/{id}/software-version-refresh\n\nPerformSoftwareVersionRefresh\n\nRefresh the Software Catalog versions available for the system identified by id.",
    capability=Capability.WRITE,
)
async def greenlake_post_private_cloud_business_v1beta1_systems_id_software_version_refresh(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Identifier of the system, usually a UUID.")],
) -> Any:
    path = f"/private-cloud-business/v1beta1/systems/{path_seg(id)}/software-version-refresh"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )
