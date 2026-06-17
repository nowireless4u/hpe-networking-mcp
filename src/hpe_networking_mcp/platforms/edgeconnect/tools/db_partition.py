"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``dbPartition``
Operations in this file: 2
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
    name="edgeconnect_delete_db_partition",
    description="DELETE /dbPartition\n\ndeleteDbPartition\n\nDelete a database statistics table partition",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_db_partition(
    ctx: Context,
    table: Annotated[
        str,
        Field(
            description="Name of the statistics database table containing the partition. Must be a valid table name with alphanumeric characters and underscores only."
        ),
    ],
    partition: Annotated[
        str,
        Field(
            description="Name of the partition to delete. Must be a valid partition name (alphanumeric and underscores). Cannot be 'defaultPartition' as it is required for table integrity."
        ),
    ],
    statsCollector: Annotated[
        int | None,
        Field(
            default=None,
            description="ID of the external stats collector associated with the partition. Use when deleting partitions from remote/external stats collector databases. If omitted, deletes from local database.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if table is not None:
        query_params["table"] = table
    if partition is not None:
        query_params["partition"] = partition
    if statsCollector is not None:
        query_params["statsCollector"] = statsCollector
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/dbPartition",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_db_partition_info",
    description="GET /dbPartition/info\n\ngetPartitionsInfo\n\nGet database partition details",
    capability=Capability.READ,
)
async def edgeconnect_get_db_partition_info(
    ctx: Context,
    table: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter results by specific database table name. When omitted, returns partitions from all tables.",
        ),
    ] = None,
    partition: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter results by specific partition name. When omitted, returns all partitions (except empty partition names).",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if table is not None:
        query_params["table"] = table
    if partition is not None:
        query_params["partition"] = partition
    return await edgeconnect_request(
        ctx,
        "GET",
        "/dbPartition/info",
        query_params=query_params or None,
    )
