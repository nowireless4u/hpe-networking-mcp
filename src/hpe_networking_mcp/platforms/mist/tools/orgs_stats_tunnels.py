"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Stats - Tunnels``
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
    name="mist_count_org_tunnels_stats",
    description="GET /api/v1/orgs/{org_id}/stats/tunnels/count\n\ncountOrgTunnelsStats\n\nCount by Distinct Attributes of Mist Tunnels Stats",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_tunnels_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="- If `type`==`wxtunnel`: wxtunnel_id / ap / remote_ip / remote_port / state / mxedge_id / mxcluster_id / site_id / peer_mxedge_id; default is wxtunnel_id \n- If `type`==`wan`: mac / site_id / node / peer_ip / peer_host/ ip / tunnel_name /..."
        ),
    ] = None,
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/stats/tunnels/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "type": type, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_tunnels_stats",
    description="GET /api/v1/orgs/{org_id}/stats/tunnels/search\n\nsearchOrgTunnelsStats\n\nBy default the endpoint returns only `wxtunnel` type stats, to get `wan` type stats\nyou need to specify `type=wan` in the query parameters.\n\n\nTunnel types:\n- `wxtunnel` (default) - A WxLan Tunnel (WxTunnel) are used to create a secure connection between Juniper Mist Access Points and third-party VPN concentrators using protocols such as L2TPv3 or dmvpn.\n- `wan` - A WAN Tunnel is a secure connection between two Gateways, typically used for site-to-site or mesh connectivity. It can be configured with various protocols and ...",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_tunnels_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxcluster_id: Annotated[str | None, Field(description="If `type`==`wxtunnel`")] = None,
    site_id: Annotated[str | None, Field(description="query parameter 'site_id'")] = None,
    wxtunnel_id: Annotated[str | None, Field(description="If `type`==`wxtunnel`")] = None,
    ap: Annotated[str | None, Field(description="If `type`==`wxtunnel`")] = None,
    mac: Annotated[str | None, Field(description="If `type`==`wan`")] = None,
    node: Annotated[str | None, Field(description="If `type`==`wan`")] = None,
    peer_ip: Annotated[str | None, Field(description="If `type`==`wan`")] = None,
    peer_host: Annotated[str | None, Field(description="If `type`==`wan`")] = None,
    ip: Annotated[str | None, Field(description="If `type`==`wan`")] = None,
    tunnel_name: Annotated[str | None, Field(description="If `type`==`wan`")] = None,
    protocol: Annotated[str | None, Field(description="If `type`==`wan`")] = None,
    auth_algo: Annotated[str | None, Field(description="If `type`==`wan`")] = None,
    encrypt_algo: Annotated[str | None, Field(description="If `type`==`wan`")] = None,
    ike_version: Annotated[str | None, Field(description="If `type`==`wan`")] = None,
    up: Annotated[str | None, Field(description="If `type`==`wan`")] = None,
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "5m",
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
        "/api/v1/orgs/{org_id}/stats/tunnels/search",
        path_params={"org_id": org_id},
        query_params={
            "mxcluster_id": mxcluster_id,
            "site_id": site_id,
            "wxtunnel_id": wxtunnel_id,
            "ap": ap,
            "mac": mac,
            "node": node,
            "peer_ip": peer_ip,
            "peer_host": peer_host,
            "ip": ip,
            "tunnel_name": tunnel_name,
            "protocol": protocol,
            "auth_algo": auth_algo,
            "encrypt_algo": encrypt_algo,
            "ike_version": ike_version,
            "up": up,
            "type": type,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
