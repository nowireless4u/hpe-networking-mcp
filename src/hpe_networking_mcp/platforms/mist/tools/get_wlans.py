"""Mist tool: list WLANs/SSIDs at organization or site level."""

from typing import Annotated
from uuid import UUID

import mistapi
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.mist._registry import mcp
from hpe_networking_mcp.platforms.mist.client import (
    format_response,
    get_apisession,
    handle_network_error,
    process_response,
)


@mcp.tool(
    name="mist_get_wlans",
    description=(
        "List WLANs/SSIDs configured in the organization or a specific site. "
        "Returns WLAN name, SSID, security settings, VLAN, and status."
    ),
    tags={"configuration"},
    annotations={
        "title": "Get WLANs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_wlans(
    org_id: Annotated[UUID, Field(description="Organization ID")],
    site_id: Annotated[
        UUID | None,
        Field(
            description=("Site ID. If provided, returns WLANs for this site only."),
        ),
    ] = None,
) -> dict | list | str:
    """List WLANs configured in an organization or site."""

    logger.debug("Tool get_wlans called")
    logger.debug(
        "Input Parameters: org_id: %s, site_id: %s",
        org_id,
        site_id,
    )

    apisession, response_format = await get_apisession()

    try:
        if site_id:
            response = mistapi.api.v1.sites.wlans.listSiteWlans(apisession, site_id=str(site_id))
        else:
            response = mistapi.api.v1.orgs.wlans.listOrgWlans(apisession, org_id=str(org_id))
        await process_response(response)

    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
