"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``applianceBackup``
Operations in this file: 6
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_delete_appliance_backup",
    description="DELETE /appliance/backup\n\nbackupDelete44\n\nDelete a specific appliance backup record",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_appliance_backup(
    ctx: Context,
    backupFilePk: Annotated[
        int,
        Field(
            description="Unique database identifier of the backup record to delete. Obtain this ID from GET /appliance/backup response."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if backupFilePk is not None:
        query_params["backupFilePk"] = backupFilePk
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/appliance/backup",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_backup",
    description="GET /appliance/backup\n\nbackupGet45\n\nGet appliance backup history",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_backup(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    runningConfig: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include the running configuration data in response. Set to false to retrieve only backup metadata for faster queries.",
        ),
    ] = None,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by specific backup record ID. When provided, returns only the backup matching this ID.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if runningConfig is not None:
        query_params["runningConfig"] = runningConfig
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/backup",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_restore_status",
    description="GET /appliance/restore/status\n\napplianceBulkRestoreStatus\n\nGet appliance restore status (active and recent)",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_restore_status(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/restore/status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_appliance_backup",
    description="POST /appliance/backup\n\nbackupPost43\n\nBackup appliance configuration to Orchestrator database",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_backup(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/backup",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_appliance_restore",
    description="POST /appliance/restore\n\napplianceRestore72\n\nRestore appliance configuration from a backup",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_restore(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/restore",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_appliance_restore_bulk",
    description="POST /appliance/restore/bulk\n\napplianceRestoreBulk72\n\nBulk restore multiple appliances from backups",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_restore_bulk(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/restore/bulk",
        query_params=None,
        body=body,
    )
