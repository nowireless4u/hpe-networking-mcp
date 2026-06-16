"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``statsCollection``
Operations in this file: 8
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
    name="edgeconnect_get_stats_collector_backup_config",
    description="GET /statsCollector/backup/config\n\ngetScBackupConfiguration711\n\nRetrieve stats collector backup configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_collector_backup_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/statsCollector/backup/config",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_collector_backup_use_gms_config",
    description="GET /statsCollector/backup/useGmsConfig\n\ngetUseGmsConfig714\n\nCheck if stats collector backup uses Orchestrator backup configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_collector_backup_use_gms_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/statsCollector/backup/useGmsConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_collector_status",
    description="GET /statsCollector/status\n\ngetHealthStatusOfAllStatsCollectors726\n\nGet health status of all stats collectors",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_collector_status(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/statsCollector/status",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_collector_unsupported_appliances",
    description="GET /statsCollector/unsupportedAppliances\n\ngetUnsupportedAppliances727\n\nGet appliances incompatible with new stats collection",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_collector_unsupported_appliances(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/statsCollector/unsupportedAppliances",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_stats_collector_associations_by_nepks",
    description="POST /statsCollector/associationsByNepks\n\nstatsCollectorAssociationsByNepks710\n\nGet stats collector assignments for appliance IDs",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_collector_associations_by_nepks(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/statsCollector/associationsByNepks",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_collector_backup_config",
    description="POST /statsCollector/backup/config\n\nsetScBackupConfig712\n\nAdd or update stats collector backup configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_collector_backup_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/statsCollector/backup/config",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_collector_backup_test_connection",
    description="POST /statsCollector/backup/testConnection\n\nscBackupTestConnection713\n\nTest stats collector backup server connection",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_collector_backup_test_connection(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/statsCollector/backup/testConnection",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_collector_backup_use_gms_config",
    description="POST /statsCollector/backup/useGmsConfig\n\nsetUseGmsConfig715\n\nSet whether stats collector backup uses Orchestrator backup configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_collector_backup_use_gms_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/statsCollector/backup/useGmsConfig",
        query_params=None,
        body=body,
    )
