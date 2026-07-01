"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/backup-recovery.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``backup-recovery``   Tag: ``datastores``   Operations: 1
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
    name="greenlake_post_backup_recovery_v1beta1_datastores_id_restore",
    description="POST /backup-recovery/v1beta1/datastores/{id}/restore\n\nDatastoreRestoreFromCopy\n\nRestore a datastore from snapshot or a backup.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_datastores_id_restore(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/datastores/{path_seg(id)}/restore"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
