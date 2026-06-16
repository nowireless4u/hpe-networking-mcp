"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``ipObjects``
Operations in this file: 13
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
    name="edgeconnect_delete_ip_objects_address_group",
    description="DELETE /ipObjects/addressGroup\n\naclAddressGroupsDelete429\n\nDelete an ACL address group",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_ip_objects_address_group(
    ctx: Context,
    name: Annotated[
        str,
        Field(
            description="The unique name of the ACL address group to delete. Must be an existing address group name."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if name is not None:
        query_params["name"] = name
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/ipObjects/addressGroup",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_ip_objects_service_group",
    description="DELETE /ipObjects/serviceGroup\n\nserviceGroupsDelete436\n\nDelete an ACL service group",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_ip_objects_service_group(
    ctx: Context,
    name: Annotated[
        str,
        Field(
            description="The unique name of the ACL service group to delete. Must be an existing service group name."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if name is not None:
        query_params["name"] = name
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/ipObjects/serviceGroup",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ip_objects_address_group",
    description="GET /ipObjects/addressGroup\n\naclAddressGroupsGet430\n\nRetrieve ACL address groups",
    capability=Capability.READ,
)
async def edgeconnect_get_ip_objects_address_group(
    ctx: Context,
    name: Annotated[
        str | None,
        Field(
            default=None,
            description="The unique name of the address group to retrieve. If omitted, returns all address groups.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if name is not None:
        query_params["name"] = name
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ipObjects/addressGroup",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ip_objects_memory_consumed",
    description="GET /ipObjects/memoryConsumed\n\naclIpObjectsMemoryConsumed\n\nGet estimated memory consumption for IP object groups",
    capability=Capability.READ,
)
async def edgeconnect_get_ip_objects_memory_consumed(
    ctx: Context,
    type: Annotated[
        str, Field(description="Specifies which IP object type to calculate memory for. Case-insensitive.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if type is not None:
        query_params["type"] = type
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ipObjects/memoryConsumed",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ip_objects_service_group",
    description="GET /ipObjects/serviceGroup\n\nserviceGroupsGet437\n\nRetrieve ACL service groups",
    capability=Capability.READ,
)
async def edgeconnect_get_ip_objects_service_group(
    ctx: Context,
    name: Annotated[
        str | None,
        Field(
            default=None,
            description="Unique name of the service group to retrieve. If omitted, returns all service groups.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if name is not None:
        query_params["name"] = name
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ipObjects/serviceGroup",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_ip_objects_address_group",
    description="POST /ipObjects/addressGroup\n\naddressGroupsPost425\n\nCreate or update an ACL address group",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ip_objects_address_group(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/ipObjects/addressGroup",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_ip_objects_address_group_bulk_upload",
    description="POST /ipObjects/addressGroup/bulkUpload\n\naclAddressGroupBulkUpload427\n\nBulk import address groups from CSV file",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ip_objects_address_group_bulk_upload(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/ipObjects/addressGroup/bulkUpload",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_ip_objects_address_group_merge",
    description="POST /ipObjects/addressGroup/merge\n\naclAddressGroupMerge428\n\nConsolidate all address groups immediately",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ip_objects_address_group_merge(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/ipObjects/addressGroup/merge",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_ip_objects_service_group",
    description="POST /ipObjects/serviceGroup\n\nserviceGroupsPost432\n\nCreate or update an ACL service group",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ip_objects_service_group(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/ipObjects/serviceGroup",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_ip_objects_service_group_bulk_upload",
    description="POST /ipObjects/serviceGroup/bulkUpload\n\naclServiceGroupBulkUpload434\n\nBulk import service groups from CSV file",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ip_objects_service_group_bulk_upload(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/ipObjects/serviceGroup/bulkUpload",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_ip_objects_service_group_merge",
    description="POST /ipObjects/serviceGroup/merge\n\naclServiceGroupMerge435\n\nConsolidate all service groups immediately",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ip_objects_service_group_merge(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/ipObjects/serviceGroup/merge",
        query_params=None,
    )


@tool(
    name="edgeconnect_put_ip_objects_address_group",
    description="PUT /ipObjects/addressGroup\n\naddressGroupsPut426\n\nReplace an existing ACL address group",
    capability=Capability.WRITE,
)
async def edgeconnect_put_ip_objects_address_group(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/ipObjects/addressGroup",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_ip_objects_service_group",
    description="PUT /ipObjects/serviceGroup\n\nserviceGroupsPut433\n\nReplace an existing ACL service group",
    capability=Capability.WRITE,
)
async def edgeconnect_put_ip_objects_service_group(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/ipObjects/serviceGroup",
        query_params=None,
        body=body,
    )
