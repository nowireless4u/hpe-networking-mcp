"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Stats - Ports``
Operations in this file: 2
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
    name="mist_count_site_sw_or_gw_ports",
    description="GET /api/v1/sites/{site_id}/stats/ports/count\n\ncountSiteSwOrGwPorts\n\nCount switch and gateway port statistics for a site, optionally grouped by the `distinct` field and filtered by port, neighbor, PoE, STP, traffic, and time attributes. Use [Count Org Switch/Gateway Ports](/#operations/countOrgSwOrGwPorts) to count switch and gateway port statistics across the organization.",
    capability=Capability.READ,
)
async def mist_count_site_sw_or_gw_ports(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `full_duplex`, `mac`, `neighbor_mac`, `neighbor_port_desc`, `neighbor_system_name`, `poe_disabled`, `poe_mode`, `poe_on`, `port_id`, `port_mac`, `speed`, `up`"
        ),
    ] = None,
    full_duplex: Annotated[bool | None, Field(description="Indicates full or half duplex")] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    neighbor_mac: Annotated[str | None, Field(description="Chassis identifier of the chassis type listed")] = None,
    neighbor_port_desc: Annotated[
        str | None,
        Field(description='Description supplied by the system on the interface E.g. "GigabitEthernet2/0/39"'),
    ] = None,
    neighbor_system_name: Annotated[
        str | None,
        Field(
            description='Name supplied by the system on the interface E.g. neighbor system name E.g. "Kumar-Acc-SW.mist.local"'
        ),
    ] = None,
    poe_disabled: Annotated[bool | None, Field(description="Is the POE configured not be disabled.")] = None,
    poe_mode: Annotated[str | None, Field(description='POE mode depending on class E.g. "802.3at"')] = None,
    poe_on: Annotated[bool | None, Field(description="Is the device attached to POE")] = None,
    port_id: Annotated[str | None, Field(description="Filter results by port identifier")] = None,
    port_mac: Annotated[str | None, Field(description="Filter results by port MAC address")] = None,
    power_draw: Annotated[
        float | None,
        Field(
            description="Amount of power being used by the interface at the time the command is executed. Unit in watts."
        ),
    ] = None,
    tx_pkts: Annotated[int | None, Field(description="Filter results by transmitted packet count")] = None,
    rx_pkts: Annotated[int | None, Field(description="Filter results by received packet count")] = None,
    rx_bytes: Annotated[int | None, Field(description="Filter results by received byte count")] = None,
    tx_bps: Annotated[int | None, Field(description="Filter results by transmit rate")] = None,
    rx_bps: Annotated[int | None, Field(description="Filter results by receive rate")] = None,
    tx_mcast_pkts: Annotated[
        int | None, Field(description="Filter results by transmitted multicast packet count")
    ] = None,
    tx_bcast_pkts: Annotated[
        int | None, Field(description="Filter results by transmitted broadcast packet count")
    ] = None,
    rx_mcast_pkts: Annotated[int | None, Field(description="Filter results by received multicast packet count")] = None,
    rx_bcast_pkts: Annotated[int | None, Field(description="Filter results by received broadcast packet count")] = None,
    speed: Annotated[int | None, Field(description="Filter results by port speed")] = None,
    stp_state: Annotated[
        Any | None,
        Field(
            description='STP state used to filter port results when `up`==`true`. enum: `""`, `blocking`, `disabled`, `forwarding`, `learning`, `listening`'
        ),
    ] = None,
    stp_role: Annotated[
        Any | None,
        Field(
            description='STP role used to filter port results when `up`==`true`. enum: `""`, `alternate`, `backup`, `designated`, `disabled`, `root`, `root-prevented`'
        ),
    ] = None,
    auth_state: Annotated[
        Any | None,
        Field(
            description='Authentication state used to filter port results when `up`==`true` and the port has an authenticator role. enum: `""`, `authenticated`, `authenticating`, `held`, `init`'
        ),
    ] = None,
    up: Annotated[bool | None, Field(description="Indicates if interface is up")] = None,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/ports/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "full_duplex": full_duplex,
            "mac": mac,
            "neighbor_mac": neighbor_mac,
            "neighbor_port_desc": neighbor_port_desc,
            "neighbor_system_name": neighbor_system_name,
            "poe_disabled": poe_disabled,
            "poe_mode": poe_mode,
            "poe_on": poe_on,
            "port_id": port_id,
            "port_mac": port_mac,
            "power_draw": power_draw,
            "tx_pkts": tx_pkts,
            "rx_pkts": rx_pkts,
            "rx_bytes": rx_bytes,
            "tx_bps": tx_bps,
            "rx_bps": rx_bps,
            "tx_mcast_pkts": tx_mcast_pkts,
            "tx_bcast_pkts": tx_bcast_pkts,
            "rx_mcast_pkts": rx_mcast_pkts,
            "rx_bcast_pkts": rx_bcast_pkts,
            "speed": speed,
            "stp_state": stp_state,
            "stp_role": stp_role,
            "auth_state": auth_state,
            "up": up,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_sw_or_gw_ports",
    description="GET /api/v1/sites/{site_id}/stats/ports/search\n\nsearchSiteSwOrGwPorts\n\nSearch switch and gateway port statistics for a site.\nReturns ports that match the search criteria, including current or most recent port status and statistics within the hour.\n\nTraffic information (Tx/Rx) is reported as cumulative counters since the last device reboot. Use [Search Org Switch/Gateway Ports](/#operations/searchOrgSwOrGwPorts) to search switch and gateway port statistics across the organization.",
    capability=Capability.READ,
)
async def mist_search_site_sw_or_gw_ports(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_type: Annotated[Any | None, Field(description="Type of device. enum: `switch`, `gateway`, `all`")] = None,
    auth_state: Annotated[
        Any | None,
        Field(
            description='Authentication state used to filter port results when `up`==`true` and the port has an authenticator role. enum: `""`, `authenticated`, `authenticating`, `held`, `init`'
        ),
    ] = None,
    full_duplex: Annotated[bool | None, Field(description="Indicates full or half duplex")] = None,
    lte_imsi: Annotated[str | None, Field(description="LTE IMSI value, Check for null/empty")] = None,
    lte_iccid: Annotated[str | None, Field(description="LTE ICCID value, Check for null/empty")] = None,
    lte_imei: Annotated[str | None, Field(description="LTE IMEI value, Check for null/empty")] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    neighbor_mac: Annotated[str | None, Field(description="Chassis identifier of the chassis type listed")] = None,
    neighbor_port_desc: Annotated[
        str | None,
        Field(description='Description supplied by the system on the interface E.g. "GigabitEthernet2/0/39"'),
    ] = None,
    neighbor_system_name: Annotated[
        str | None,
        Field(
            description='Name supplied by the system on the interface E.g. neighbor system name E.g. "Kumar-Acc-SW.mist.local"'
        ),
    ] = None,
    poe_disabled: Annotated[bool | None, Field(description="Is the POE configured not be disabled.")] = None,
    poe_mode: Annotated[str | None, Field(description='POE mode depending on class E.g. "802.3at"')] = None,
    poe_on: Annotated[bool | None, Field(description="Is the device attached to POE")] = None,
    poe_priority: Annotated[
        Any | None, Field(description="PoE priority used to filter switch port results. enum: `low`, `high`")
    ] = None,
    port_id: Annotated[str | None, Field(description="Filter results by port identifier")] = None,
    port_mac: Annotated[str | None, Field(description="Filter results by port MAC address")] = None,
    speed: Annotated[int | None, Field(description="Filter results by port speed")] = None,
    stp_state: Annotated[
        Any | None,
        Field(
            description='STP state used to filter port results when `up`==`true`. enum: `""`, `blocking`, `disabled`, `forwarding`, `learning`, `listening`'
        ),
    ] = None,
    stp_role: Annotated[
        Any | None,
        Field(
            description='STP role used to filter port results when `up`==`true`. enum: `""`, `alternate`, `backup`, `designated`, `disabled`, `root`, `root-prevented`'
        ),
    ] = None,
    up: Annotated[bool | None, Field(description="Indicates if interface is up")] = None,
    xcvr_part_number: Annotated[str | None, Field(description="Optic Slot Partnumber, Check for null/empty")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/ports/search",
        path_params={"site_id": site_id},
        query_params={
            "device_type": device_type,
            "auth_state": auth_state,
            "full_duplex": full_duplex,
            "lte_imsi": lte_imsi,
            "lte_iccid": lte_iccid,
            "lte_imei": lte_imei,
            "mac": mac,
            "neighbor_mac": neighbor_mac,
            "neighbor_port_desc": neighbor_port_desc,
            "neighbor_system_name": neighbor_system_name,
            "poe_disabled": poe_disabled,
            "poe_mode": poe_mode,
            "poe_on": poe_on,
            "poe_priority": poe_priority,
            "port_id": port_id,
            "port_mac": port_mac,
            "speed": speed,
            "stp_state": stp_state,
            "stp_role": stp_role,
            "up": up,
            "xcvr_part_number": xcvr_part_number,
            "limit": limit,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
