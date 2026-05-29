"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Constants Definitions``
Operations in this file: 16
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_list_ap_channels",
    description="GET /api/v1/const/ap_channels\n\nlistApChannels\n\nGet List of List of Available channels per country code",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_ap_channels(
    ctx: Context,
    country_code: Annotated[str | None, Field(description="Country code, in two-character")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/ap_channels",
        path_params=None,
        query_params={"country_code": country_code},
        body=None,
    )


@_mcp_tool(
    name="mist_list_ap_l_esl_versions",
    description="GET /api/v1/const/ap_esl_versions\n\nlistApLEslVersions\n\nGet Available AP ESL Versions",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_ap_l_esl_versions(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/ap_esl_versions",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_ap_led_definition",
    description="GET /api/v1/const/ap_led_status\n\nlistApLedDefinition\n\nGet List of AP LED definition",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_ap_led_definition(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/ap_led_status",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_app_category_definitions",
    description="GET /api/v1/const/app_categories\n\nlistAppCategoryDefinitions\n\nGet List of definitions of all the supported Application Categories. The example field contains an example payload as you would receive in the alarm webhook output.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_app_category_definitions(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/app_categories",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_app_sub_category_definitions",
    description="GET /api/v1/const/app_subcategories\n\nlistAppSubCategoryDefinitions\n\nGet List of definitions of all the supported Application sub-categories. The example field contains an example payload as you would receive in the alarm webhook output.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_app_sub_category_definitions(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/app_subcategories",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_applications",
    description="GET /api/v1/const/applications\n\nlistApplications\n\nGet List of a list of applications that Juniper-Mist Devices recognize",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_applications(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/applications",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_country_codes",
    description="GET /api/v1/const/countries\n\nlistCountryCodes\n\nGet List of available Country Codes",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_country_codes(
    ctx: Context,
    extend: Annotated[bool, Field(description="Will include more country codes if true")] = False,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/countries",
        path_params=None,
        query_params={"extend": extend},
        body=None,
    )


@_mcp_tool(
    name="mist_list_fingerprint_types",
    description="GET /api/v1/const/fingerprint_types\n\nlistFingerprintTypes\n\nGet List of supported fingerprint attribute values\n* family\n* model\n* mfg\n* os_type\n\nThis information can be used in the [Mist NAC Rules]($h/Orgs%20NAC%20Rules/_overview) `matching` attribute.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_fingerprint_types(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/fingerprint_types",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_gateway_applications",
    description="GET /api/v1/const/gateway_applications\n\nlistGatewayApplications\n\nGet the full list of applications that we recognize",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_gateway_applications(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/gateway_applications",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_insight_metrics",
    description="GET /api/v1/const/insight_metrics\n\nlistInsightMetrics\n\nList Insight Metrics",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_insight_metrics(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/insight_metrics",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_license_types",
    description="GET /api/v1/const/license_types\n\nlistLicenseTypes\n\nGet License Types",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_license_types(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/license_types",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_marvis_client_versions",
    description="GET /api/v1/const/marvisclient_versions\n\nlistMarvisClientVersions\n\nGet List of the available Marvis Client Versions.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_marvis_client_versions(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/marvisclient_versions",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_languages",
    description="GET /api/v1/const/languages\n\nlistSiteLanguages\n\nGet List of Languages",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_languages(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/languages",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_states",
    description="GET /api/v1/const/states\n\nlistStates\n\nGet List of ISO States based on country code",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_states(
    ctx: Context,
    country_code: Annotated[str, Field(description="Country code, in [two-character](/#operations/listCountryCodes)")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/states",
        path_params=None,
        query_params={"country_code": country_code},
        body=None,
    )


@_mcp_tool(
    name="mist_list_traffic_types",
    description="GET /api/v1/const/traffic_types\n\nlistTrafficTypes\n\nGet List of identified traffic",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_traffic_types(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/traffic_types",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_webhook_topics",
    description="GET /api/v1/const/webhook_topics\n\nlistWebhookTopics\n\nGet List of the available Webhook Topics.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_webhook_topics(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/webhook_topics",
        path_params=None,
        query_params=None,
        body=None,
    )
