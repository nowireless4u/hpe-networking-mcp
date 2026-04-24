"""Mist tool: get detailed information for a specific AP."""

from typing import Annotated
from uuid import UUID

import mistapi
from fastmcp import Context
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.mist._registry import tool
from hpe_networking_mcp.platforms.mist.client import (
    format_response,
    get_apisession,
    handle_network_error,
    process_response,
)


@tool(
    name="mist_get_ap_details",
    description=(
        "Get detailed information for a specific AP including model, firmware, radio configuration, IP, and status."
    ),
    tags={"devices"},
    annotations={
        "title": "Get AP details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_ap_details(
    ctx: Context,
    site_id: Annotated[UUID, Field(description="Site ID")],
    device_id: Annotated[
        UUID,
        Field(
            description=("AP device ID (use mist_search_device to find it)"),
        ),
    ],
) -> dict | list | str:
    """Get detailed information for a specific AP."""

    logger.debug("Tool get_ap_details called")
    logger.debug(
        "Input Parameters: site_id: %s, device_id: %s",
        site_id,
        device_id,
    )

    apisession, response_format = await get_apisession(ctx)

    try:
        response = mistapi.api.v1.sites.devices.getSiteDevice(
            apisession,
            site_id=str(site_id),
            device_id=str(device_id),
        )
        await process_response(response)

    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
