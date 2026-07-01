"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/storage-fleet.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``storage-fleet``   Tag: ``certificates``   Operations: 13
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
    name="greenlake_delete_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificates_certificate_id",
    description="DELETE /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates/{certificateId}\n\ndeleteStorageClusterCustomCertificate\n\ndelete storage cluster custom certificate identified by {certificateId}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificates_certificate_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    certificateId: Annotated[str, Field(description="ID unique to certificate created in objectstore")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/custom-certificates/{path_seg(certificateId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_delete_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_certificates_certificate_id",
    description="DELETE /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates/{certificateId}\n\ndeleteStorageClusterTrustCertificate\n\ndelete storage cluster trust certificate identified by {certificateId}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_certificates_certificate_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    certificateId: Annotated[str, Field(description="ID unique to certificate created in objectstore")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/trust-certificates/{path_seg(certificateId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificate_policies",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificate-policies\n\nDeviceType7GetCustomCertificatePolicies\n\nGet all custom certificate policies of a HPE Alletra Storage MP X10000 system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificate_policies(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="Lucene query to filter Certificate by Key.")] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Data query to sort Certificate resource by Key.")
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/custom-certificate-policies"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificate_policies_certificate_policy_id",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificate-policies/{certificatePolicyId}\n\nDeviceType7GetCustomCertificatePoliciesById\n\nGet Certificate policies of a HPE Alletra Storage MP X10000 system identified by certificatePolicyID",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificate_policies_certificate_policy_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    certificatePolicyId: Annotated[str, Field(description="ID unique to certificate policy created in objectstore")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/custom-certificate-policies/{path_seg(certificatePolicyId)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificates",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates\n\nDeviceType7GetCustomCertificates\n\nGet all custom certificates of a HPE Alletra Storage MP X10000 system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificates(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="Lucene query to filter Certificate by Key.")] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Data query to sort Certificate resource by Key.")
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/custom-certificates"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificates_certificate_id",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates/{certificateId}\n\nDeviceType7GetCustomCertificateById\n\nGet Custom Certificate of a HPE Alletra Storage MP X10000 system identified by certificateID",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificates_certificate_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    certificateId: Annotated[str, Field(description="ID unique to certificate created in objectstore")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/custom-certificates/{path_seg(certificateId)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_certificates",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates\n\nDeviceType7GetTrustCertificates\n\nGet all custom certificates of a HPE Alletra Storage MP X10000 system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_certificates(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="Lucene query to filter Certificate by Key.")] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Data query to sort Certificate resource by Key.")
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/trust-certificates"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_certificates_certificate_id",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates/{certificateId}\n\nDeviceType7GetTrustCertificateById\n\nGet Trust Certificate of a HPE Alletra Storage MP X10000 system identified by certificateID",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_certificates_certificate_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    certificateId: Annotated[str, Field(description="ID unique to certificate created in objectstore")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/trust-certificates/{path_seg(certificateId)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_stores",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-stores\n\nDeviceType7GetTrustStores\n\nGet all Trust Store of a HPE Alletra Storage MP X10000 system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_stores(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="Lucene query to filter Trust Store by Key.")] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Data query to sort Trust Store resource by Key.")
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/trust-stores"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_stores_trust_store_id",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-stores/{TrustStoreId}\n\nDeviceType7GetTrustStoreById\n\nGet Trust Store of a HPE Alletra Storage MP X10000 system identified by ID",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_stores_trust_store_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    TrustStoreId: Annotated[str, Field(description="ID unique to trustStore created in objectstore")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = (
        f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/trust-stores/{path_seg(TrustStoreId)}"
    )
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
    name="greenlake_post_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificates",
    description="POST /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates\n\ncreateStorageClusterCustomCertificate\n\nCreate a custom certificate for storage cluster",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificates(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/custom-certificates"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_certificates",
    description="POST /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates\n\ncreateStorageClusterTrustCertificate\n\nCreate a trust certificate for storage cluster",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_trust_certificates(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/trust-certificates"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificates_certificate_id",
    description="PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates/{certificateId}\n\nDeviceType7ImportCustomCertificate\n\nImport certificates for HPE Alletra Storage MP X10000 system identified by certificateId",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_custom_certificates_certificate_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    certificateId: Annotated[str, Field(description="ID unique to certificate created in objectstore")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/custom-certificates/{path_seg(certificateId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
