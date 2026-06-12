"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Constants Definitions``
Operations in this file: 16
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_list_ap_channels",
    description="GET /api/v1/const/ap_channels\n\nlistApChannels\n\nReturn supported AP radio channels for the requested country code, based on the regulatory domain used by Mist AP configuration.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/ap_esl_versions\n\nlistApLEslVersions\n\nReturn Electronic Shelf Label (ESL) firmware versions available per AP model.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/ap_led_status\n\nlistApLedDefinition\n\nReturn AP LED status definitions, including the values used to describe LED behavior and the corresponding `error_code` value.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/app_categories\n\nlistAppCategoryDefinitions\n\nReturn supported application categories used for application identification, traffic classification, and policy matching.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/app_subcategories\n\nlistAppSubCategoryDefinitions\n\nReturn supported application subcategories used for application identification, traffic classification, and policy matching.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/applications\n\nlistApplications\n\nReturn applications recognized by Juniper Mist devices for traffic classification and application analytics.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/countries\n\nlistCountryCodes\n\nReturn supported country codes for Mist configuration. Set `extend=true` to include additional country codes when available.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/fingerprint_types\n\nlistFingerprintTypes\n\nReturn supported client fingerprint attribute values (`family`, `model`, `mfg`, and `os_type`) that can be used in [Mist NAC Rules]($h/Orgs%20NAC%20Rules/_overview) `matching` conditions.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/gateway_applications\n\nlistGatewayApplications\n\nReturn applications recognized by Mist gateways for traffic classification.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/insight_metrics\n\nlistInsightMetrics\n\nReturn supported insight metric names and metadata used by insight and SLE APIs.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/license_types\n\nlistLicenseTypes\n\nReturn Mist license type definitions used by inventory and subscription APIs.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/marvisclient_versions\n\nlistMarvisClientVersions\n\nReturn available Marvis Client application versions for tracking or managing Marvis Client deployments.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/languages\n\nlistSiteLanguages\n\nReturn supported language codes for localized Mist configuration and user-facing portals.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/states\n\nlistStates\n\nReturn ISO state or province codes for the supplied country code.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/traffic_types\n\nlistTrafficTypes\n\nReturn traffic type definitions used to classify recognized network traffic.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/webhook_topics\n\nlistWebhookTopics\n\nReturn webhook topic definitions that can be subscribed to in webhook configuration.",
    capability=Capability.READ,
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
