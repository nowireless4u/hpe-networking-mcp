"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``StatsDebug``
Operations in this file: 15
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
    name="edgeconnect_get_stats_collector_data_status",
    description="GET /statsCollector/dataStatus\n\ngetDataStatus\n\nGet Data Status from All Stats Collectors",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_collector_data_status(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/statsCollector/dataStatus",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_build_in_user_details",
    description="GET /stats/infrastructure/buildInUserDetails\n\ngetBuildInUserDetails\n\nCheck Built-in Admin User Existence",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_build_in_user_details(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/buildInUserDetails",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_d_benv_variables",
    description="GET /stats/infrastructure/dBEnvVariables\n\ngetDBEnvVariables\n\nGet Database Environment Variables",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_d_benv_variables(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/dBEnvVariables",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_host_name",
    description="GET /stats/infrastructure/hostName\n\ngetHostName\n\nGet Orchestrator Hostname",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_host_name(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/hostName",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_hourly_flow_stats_retention",
    description="GET /stats/infrastructure/hourlyFlowStatsRetention\n\ngetHourlyFlowStatsRetention\n\nGet Hourly Flow Stats Retention Configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_hourly_flow_stats_retention(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/hourlyFlowStatsRetention",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_http_port",
    description="GET /stats/infrastructure/httpPort\n\ngetHttpPort\n\nGet HTTP Port",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_http_port(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/httpPort",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_ip_address",
    description="GET /stats/infrastructure/ipAddress\n\ngetIpAddress\n\nGet Orchestrator IP Address",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_ip_address(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/ipAddress",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_is_certificate_present",
    description="GET /stats/infrastructure/isCertificatePresent\n\nisCertificatePresent\n\nCheck Stats Collector Signing Certificate Presence",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_is_certificate_present(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/isCertificatePresent",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_is_in_container",
    description="GET /stats/infrastructure/isInContainer\n\nisInContainer\n\nCheck Container Deployment Mode",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_is_in_container(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/isInContainer",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_orchestrator_model",
    description="GET /stats/infrastructure/orchestratorModel\n\ngetOrchestratorModel\n\nGet Orchestrator Model Configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_orchestrator_model(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/orchestratorModel",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_os_flavor_version",
    description="GET /stats/infrastructure/osFlavorVersion\n\ngetOsFlavorVersionInfo\n\nGet OS Flavor and Version",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_os_flavor_version(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/osFlavorVersion",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_platform_info",
    description="GET /stats/infrastructure/platformInfo\n\ngetPlatformInfo\n\nGet Orchestrator Platform Information",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_platform_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/platformInfo",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_smtp_configuration",
    description="GET /stats/infrastructure/smtpConfiguration\n\ngetSmtpConfiguration\n\nGet SMTP Configuration Resource Keys",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_smtp_configuration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/smtpConfiguration",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_infrastructure_validate_configure_logger",
    description="GET /stats/infrastructure/validateConfigureLogger\n\nvalidateConfigureLogger\n\nValidate Logger Configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_infrastructure_validate_configure_logger(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/infrastructure/validateConfigureLogger",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_orchestration_task_stats_appliance",
    description="GET /stats/orchestrationTask/stats/appliance\n\ngetOrchTaskStatsForAppliance\n\nGet Orchestration Task Statistics for a Specific Appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_orchestration_task_stats_appliance(
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
        "/stats/orchestrationTask/stats/appliance",
        query_params=query_params or None,
    )
