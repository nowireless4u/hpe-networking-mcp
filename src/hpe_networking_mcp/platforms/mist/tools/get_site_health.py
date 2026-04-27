"""Mist tool: get organization-wide site health overview."""

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
    name="mist_get_site_health",
    description=(
        "Organization-wide health AGGREGATE — total device counts, "
        "client counts, SLE summaries, and `num_sites` rolled up "
        "across every site in the org. NOT a per-site breakdown. "
        "If you want a per-site list (one record per site with that "
        "site's health), use `mist_get_org_or_site_info("
        "info_type='site')` instead. Calls "
        "`/api/v1/orgs/{org_id}/stats` under the hood."
    ),
    tags={"info"},
    annotations={
        "title": "Get site health",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_site_health(
    ctx: Context,
    org_id: Annotated[UUID, Field(description="Organization ID")],
) -> dict | list | str:
    """Get health overview across all sites in the organization."""

    logger.debug("Tool get_site_health called")
    logger.debug("Input Parameters: org_id: %s", org_id)

    apisession, response_format = await get_apisession(ctx)

    try:
        response = mistapi.api.v1.orgs.stats.getOrgStats(apisession, org_id=str(org_id))
        await process_response(response)

    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
