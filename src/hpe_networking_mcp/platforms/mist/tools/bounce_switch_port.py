"""Mist tool: bounce ports on a Juniper EX switch."""

from typing import Annotated
from uuid import UUID

from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.mist._registry import mcp
from hpe_networking_mcp.platforms.mist.client import (
    get_apisession,
    handle_network_error,
    process_response,
)


@mcp.tool(
    name="mist_bounce_switch_port",
    description=(
        "Bounce ports on a Juniper EX switch. "
        "BEFORE calling this tool, you MUST: "
        "1) Use mist_get_stats or mist_get_switch_details to verify "
        "it is an edge/access switch and check that the target port "
        "has a client or AP connected with active PoE draw. "
        "2) Skip ports with no PoE consumption or no connected devices. "
        "3) NEVER bounce uplink (xe-), stack, or aggregation ports."
    ),
    tags={"devices"},
    annotations={
        "title": "Bounce switch port",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bounce_switch_port(
    site_id: Annotated[UUID, Field(description="Site ID")],
    device_id: Annotated[
        UUID,
        Field(
            description="Device ID of the EX switch. Use mist_search_device to find it.",
        ),
    ],
    ports: Annotated[
        str,
        Field(
            description=(
                "Comma-separated port names to bounce (e.g., 'ge-0/0/0,ge-0/0/1'). "
                "Only bounce edge/access ports — never bounce uplink (xe-), stack, or trunk ports. "
                "Juniper port format: ge-0/0/0 (1G), mge-0/0/0 (multi-gig). "
                "First number is stack member."
            ),
        ),
    ],
) -> dict | list | str:
    """Bounce ports on a Juniper EX switch to reset link state."""

    port_list = [p.strip() for p in ports.split(",")]

    logger.debug("Tool bounce_switch_port called")
    logger.debug(
        "Input Parameters: site_id: %s, device_id: %s, ports: %s",
        site_id,
        device_id,
        port_list,
    )

    apisession, _response_format = await get_apisession()

    try:
        import mistapi.api.v1.sites.devices

        response = mistapi.api.v1.sites.devices.bounceDevicePort(
            apisession,
            site_id=str(site_id),
            device_id=str(device_id),
            body={"ports": port_list},
        )
        await process_response(response)
        return {"success": True, "ports_bounced": port_list}

    except Exception as _exc:
        await handle_network_error(_exc)
        return f"Error bouncing ports: {_exc}"
