"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Stats - Ports``
Operations in this file: 2
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
    name="mist_count_org_sw_or_gw_ports",
    description="GET /api/v1/orgs/{org_id}/stats/ports/count\n\ncountOrgSwOrGwPorts\n\nCount by Distinct Attributes of Switch/Gateway Ports at the Org level",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_sw_or_gw_ports(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    full_duplex: Annotated[bool | None, Field(description="Indicates full or half duplex")] = None,
    mac: Annotated[str | None, Field(description="Device identifier")] = None,
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
    port_id: Annotated[str | None, Field(description="Interface name")] = None,
    port_mac: Annotated[str | None, Field(description="Interface mac address")] = None,
    power_draw: Annotated[
        float | None,
        Field(
            description="Amount of power being used by the interface at the time the command is executed. Unit in watts."
        ),
    ] = None,
    tx_pkts: Annotated[int | None, Field(description="Output packets")] = None,
    rx_pkts: Annotated[int | None, Field(description="Input packets")] = None,
    rx_bytes: Annotated[int | None, Field(description="Input bytes")] = None,
    tx_bps: Annotated[int | None, Field(description="Output rate")] = None,
    rx_bps: Annotated[int | None, Field(description="Input rate")] = None,
    tx_mcast_pkts: Annotated[int | None, Field(description="Multicast output packets")] = None,
    tx_bcast_pkts: Annotated[int | None, Field(description="Broadcast output packets")] = None,
    rx_mcast_pkts: Annotated[int | None, Field(description="Multicast input packets")] = None,
    rx_bcast_pkts: Annotated[int | None, Field(description="Broadcast input packets")] = None,
    speed: Annotated[int | None, Field(description="Port speed")] = None,
    stp_state: Annotated[Any | None, Field(description="If `up`==`true`")] = None,
    stp_role: Annotated[Any | None, Field(description="If `up`==`true`")] = None,
    auth_state: Annotated[Any | None, Field(description="If `up`==`true` && has Authenticator role")] = None,
    up: Annotated[bool | None, Field(description="Indicates if interface is up")] = None,
    site_id: Annotated[str | None, Field(description="Site ID")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/stats/ports/count",
        path_params={"org_id": org_id},
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
            "site_id": site_id,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_sw_or_gw_ports",
    description="GET /api/v1/orgs/{org_id}/stats/ports/search\n\nsearchOrgSwOrGwPorts\n\nSearch Switch / Gateway Ports Stats.\nReturns a list of switch/gateway ports stats that match the search criteria.\n\nThe response provide current/last port status and statistics within the hour.\nTraffic information (Tx/Rx) are cumulative counters since the last device reboot.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_sw_or_gw_ports(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_type: Annotated[Any | None, Field(description="Type of device. enum: `switch`, `gateway`, `all`")] = None,
    auth_state: Annotated[Any | None, Field(description="If `up`==`true` && has Authenticator role")] = None,
    full_duplex: Annotated[bool | None, Field(description="Indicates full or half duplex")] = None,
    lte_imsi: Annotated[str | None, Field(description="LTE IMSI value, Check for null/empty")] = None,
    lte_iccid: Annotated[str | None, Field(description="LTE ICCID value, Check for null/empty")] = None,
    lte_imei: Annotated[str | None, Field(description="LTE IMEI value, Check for null/empty")] = None,
    mac: Annotated[str | None, Field(description="Device identifier")] = None,
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
    poe_priority: Annotated[Any | None, Field(description="PoE priority.")] = None,
    port_id: Annotated[str | None, Field(description="Interface name")] = None,
    port_mac: Annotated[str | None, Field(description="Interface mac address")] = None,
    speed: Annotated[int | None, Field(description="Port speed")] = None,
    stp_state: Annotated[Any | None, Field(description="If `up`==`true`")] = None,
    stp_role: Annotated[Any | None, Field(description="If `up`==`true`")] = None,
    up: Annotated[bool | None, Field(description="Indicates if interface is up")] = None,
    xcvr_part_number: Annotated[str | None, Field(description="Optic Slot Partnumber, Check for null/empty")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
        "/api/v1/orgs/{org_id}/stats/ports/search",
        path_params={"org_id": org_id},
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
