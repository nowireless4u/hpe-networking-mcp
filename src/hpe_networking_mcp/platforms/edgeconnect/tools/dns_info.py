"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``dnsInfo``
Operations in this file: 1
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
    name="edgeconnect_get_stats_dns_info",
    description="GET /stats/dnsInfo\n\ngetDnsByIp\n\nGet DNS domain name by IP address",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_dns_info(
    ctx: Context,
    ip: Annotated[
        str,
        Field(
            description="IP address to resolve to a DNS domain name. Must be a valid IPv4 or IPv6 address format. Cannot be null or empty."
        ),
    ],
    startTime: Annotated[
        int,
        Field(
            description="Start of the time range in Unix epoch seconds (signed 64-bit integer). Defines the lower boundary for DNS record lookup."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range in Unix epoch seconds (signed 64-bit integer). Must be greater than startTime for valid results."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if ip is not None:
        query_params["ip"] = ip
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    return await edgeconnect_request(
        ctx,
        "GET",
        "/stats/dnsInfo",
        query_params=query_params or None,
    )
