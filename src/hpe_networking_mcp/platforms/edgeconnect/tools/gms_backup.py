"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``gmsBackup``
Operations in this file: 4
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
    name="edgeconnect_get_gms_backup",
    description="GET /gms/backup\n\ngetGmsBackupConfiguration\n\nGet orchestrator backup configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_backup(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/backup",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_backup_export_template",
    description="GET /gms/backup/exportTemplate\n\nexportGmsTemplate\n\nExport orchestrator blueprint template as SQL file",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_backup_export_template(
    ctx: Context,
    mode: Annotated[
        str,
        Field(
            description="Export mode type. 'template' exports a clean blueprint for new orchestrators (no appliances/3rd party services allowed). 'migration' exports for orchestrator migration (overlay disabled, no IPSec key rotation)."
        ),
    ],
    download: Annotated[
        str | None,
        Field(
            default=None,
            description="Triggers file download with Content-Disposition header. Any non-null value enables download attachment mode.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if mode is not None:
        query_params["mode"] = mode
    if download is not None:
        query_params["download"] = download
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/backup/exportTemplate",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_backup_config",
    description="POST /gms/backup/config\n\nsetGmsBackupConfig\n\nCreate or update orchestrator backup configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_backup_config(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/backup/config",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_backup_test_connection",
    description="POST /gms/backup/testConnection\n\ntestBackupConnection\n\nTest remote backup server connection",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_backup_test_connection(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/backup/testConnection",
        query_params=None,
        body=body,
    )
