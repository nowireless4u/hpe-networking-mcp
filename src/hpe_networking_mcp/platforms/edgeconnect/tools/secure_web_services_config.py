"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``secureWebServicesConfig``
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
    name="edgeconnect_get_secure_web_services_config",
    description="GET /secureWebServicesConfig\n\ngetSecureWebServicesConfig\n\nGet Secure Web Services configuration for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_secure_web_services_config(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="Flag to retrieve cached configuration data. When set to 'true', returns cached data instead of fetching from the appliance directly.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/secureWebServicesConfig",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_secure_web_services_config_url_look_up",
    description="GET /secureWebServicesConfig/urlLookUp\n\ngetUrlLookUp\n\nLookup URL/IP classification and reputation from BrightCloud",
    capability=Capability.READ,
)
async def edgeconnect_get_secure_web_services_config_url_look_up(
    ctx: Context,
    urlLookUp: Annotated[
        str,
        Field(
            description="URL or IP address to lookup for classification and reputation. Must be a valid URL (e.g., https://example.com) or IP address."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if urlLookUp is not None:
        query_params["urlLookUp"] = urlLookUp
    return await edgeconnect_request(
        ctx,
        "GET",
        "/secureWebServicesConfig/urlLookUp",
        query_params=query_params or None,
    )
