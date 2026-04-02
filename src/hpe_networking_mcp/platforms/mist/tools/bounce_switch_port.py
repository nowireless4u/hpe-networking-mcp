"""Mist tool: bounce ports on a Juniper EX switch."""

from typing import Annotated
from uuid import UUID

import mistapi
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.mist._registry import mcp
from hpe_networking_mcp.platforms.mist.client import (
    get_apisession,
    handle_network_error,
    process_response,
)


def _check_mist_ports(
    apisession: mistapi.APISession,
    site_id: str,
    device_id: str,
    port_list: list[str],
) -> tuple[list[str], list[dict]]:
    """Check port status before bouncing. Returns (safe_ports, skipped)."""
    safe_ports: list[str] = []
    skipped: list[dict] = []

    try:
        stats = mistapi.api.v1.sites.stats.getSiteDeviceStats(
            apisession,
            site_id=site_id,
            device_id=device_id,
        )
        if_stat = {}
        if stats.data and isinstance(stats.data, dict):
            if_stat = stats.data.get("if_stat", {})
    except Exception:
        # If we can't get stats, skip all ports for safety
        for p in port_list:
            skipped.append({"port": p, "reason": "unable to verify port status"})
        return safe_ports, skipped

    for port_id in port_list:
        # Mist if_stat uses .0 suffix (e.g., ge-0/0/0.0)
        stat_key = f"{port_id}.0"
        info = if_stat.get(stat_key, if_stat.get(port_id))
        resolved_port = port_id

        # Auto-resolve ge- <-> mge- if port not found
        if info is None and port_id.startswith("ge-"):
            alt = port_id.replace("ge-", "mge-", 1)
            alt_key = f"{alt}.0"
            info = if_stat.get(alt_key, if_stat.get(alt))
            if info is not None:
                resolved_port = alt
                logger.info(
                    "Port %s not found, resolved to %s",
                    port_id,
                    alt,
                )
        elif info is None and port_id.startswith("mge-"):
            alt = port_id.replace("mge-", "ge-", 1)
            alt_key = f"{alt}.0"
            info = if_stat.get(alt_key, if_stat.get(alt))
            if info is not None:
                resolved_port = alt
                logger.info(
                    "Port %s not found, resolved to %s",
                    port_id,
                    alt,
                )

        if info is None:
            skipped.append(
                {
                    "port": port_id,
                    "reason": "port not found in device stats",
                }
            )
        elif resolved_port.startswith("xe-"):
            skipped.append({"port": resolved_port, "reason": "uplink port (xe-)"})
        elif not info.get("up", False):
            skipped.append(
                {
                    "port": resolved_port,
                    "reason": "port down — nothing connected",
                }
            )
        else:
            safe_ports.append(resolved_port)

    return safe_ports, skipped


@mcp.tool(
    name="mist_bounce_switch_port",
    description=(
        "Bounce ports on a Juniper EX switch. Safety checks are "
        "enforced automatically — ports that are down or are "
        "uplinks (xe-) will be skipped. Returns which ports "
        "were bounced and which were skipped with reasons."
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
            description=("Device ID of the EX switch. Use mist_search_device to find it."),
        ),
    ],
    ports: Annotated[
        str,
        Field(
            description=(
                "Comma-separated port names to bounce "
                "(e.g., 'ge-0/0/0,ge-0/0/1'). "
                "Juniper port format: ge-0/0/N (1G), "
                "mge-0/0/N (multi-gig). "
                "First number is stack member."
            ),
        ),
    ],
) -> dict | list | str:
    """Bounce ports on a Juniper EX switch with safety checks."""

    port_list = [p.strip() for p in ports.split(",")]

    logger.debug(
        "Tool bounce_switch_port called: site_id=%s, device_id=%s, ports=%s",
        site_id,
        device_id,
        port_list,
    )

    apisession, _response_format = await get_apisession()

    # Safety check: verify port status before bouncing
    safe_ports, skipped = _check_mist_ports(apisession, str(site_id), str(device_id), port_list)

    if not safe_ports:
        return {
            "bounced": [],
            "skipped": skipped,
            "message": "No ports qualified for bounce.",
        }

    try:
        response = mistapi.api.v1.sites.devices.bounceDevicePort(
            apisession,
            site_id=str(site_id),
            device_id=str(device_id),
            body={"ports": safe_ports},
        )
        await process_response(response)
        return {
            "bounced": safe_ports,
            "skipped": skipped,
            "result": "bounce completed",
        }

    except Exception as _exc:
        await handle_network_error(_exc)
        return f"Error bouncing ports: {_exc}"
