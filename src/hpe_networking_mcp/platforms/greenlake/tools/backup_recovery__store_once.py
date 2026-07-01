"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/backup-recovery.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``backup-recovery``   Tag: ``store_once``   Operations: 6
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
    name="greenlake_delete_backup_recovery_v1beta1_storeonces_id",
    description="DELETE /backup-recovery/v1beta1/storeonces/{id}\n\nStoreOnceDelete\n\nDelete the StoreOnce.",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_backup_recovery_v1beta1_storeonces_id(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    force: Annotated[
        bool | None,
        Field(default=None, description="Forceful delete option in case connectivity with StoreOnce is lost."),
    ] = None,
) -> Any:
    path = f"/backup-recovery/v1beta1/storeonces/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_storeonces",
    description="GET /backup-recovery/v1beta1/storeonces\n\nStoreOncesList\n\nGet the list of available StoreOnces.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_storeonces(
    ctx: Context,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        "/backup-recovery/v1beta1/storeonces",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_storeonces_id",
    description="GET /backup-recovery/v1beta1/storeonces/{id}\n\nStoreOnceGetById\n\nGet details of a StoreOnce.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_storeonces_id(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
) -> Any:
    path = f"/backup-recovery/v1beta1/storeonces/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_backup_recovery_v1beta1_storeonces_id",
    description="PATCH /backup-recovery/v1beta1/storeonces/{id}\n\nStoreOnceUpdate\n\nUpdate the StoreOnce.",
    capability=Capability.WRITE,
)
async def greenlake_patch_backup_recovery_v1beta1_storeonces_id(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/storeonces/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_storeonces",
    description="POST /backup-recovery/v1beta1/storeonces\n\nStoreOnceCreate\n\nCreate a StoreOnce.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_storeonces(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/backup-recovery/v1beta1/storeonces",
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_storeonces_id_refresh",
    description="POST /backup-recovery/v1beta1/storeonces/{id}/refresh\n\nStoreOnceReferesh\n\nRefresh the StoreOnce.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_storeonces_id_refresh(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
) -> Any:
    path = f"/backup-recovery/v1beta1/storeonces/{path_seg(id)}/refresh"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )
