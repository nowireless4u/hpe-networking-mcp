"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Utilities WAN``
Operations in this file: 14
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
    name="mist_clear_site_device_session",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/clear_session\n\nclearSiteDeviceSession\n\nClear session",
    capability=Capability.WRITE,
)
async def mist_clear_site_device_session(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/clear_session"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/clear_session",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_clear_site_ssr_arp_cache",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/clear_arp\n\nclearSiteSsrArpCache\n\nClear ARP cache for SSR, SRX and Switch\n\nClear the entire ARP cache or a subset if arguments are provided.\n\n*Note*: port_id is optional if neither vlan nor ip is specified",
    capability=Capability.WRITE,
)
async def mist_clear_site_ssr_arp_cache(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/clear_arp"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/clear_arp",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_clear_site_ssr_bgp_routes",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/clear_bgp\n\nclearSiteBgpRoutes\n\nClear routes associated with one or all BGP neighbors",
    capability=Capability.WRITE,
)
async def mist_clear_site_ssr_bgp_routes(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/clear_bgp"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/clear_bgp",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_release_site_ssr_dhcp_lease",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/release_dhcp\n\nreleaseSiteSsrDhcpLease\n\nReleases an active DHCP lease.\n\n\nThe output will be available through websocket.\n\nAs there can be multiple commands issued against the same Device at the same\ntime and the output all goes through the same websocket stream, session is\nintroduced for demux.\n\n\n\n#### Subscribe to Device Command outputs\n\n\n`WS /api-ws/v1/stream`\n\n\n```json\n\n{ "subscribe": "/sites/{site_id}/devices/{device_id}/cmd" }\n\n```\n\n\n\n#### Example output from ws stream\n\n\n```json\n{\n    "event": "data",\n    "channel": "/sites/d6fb4f96-3ba4-...',
    capability=Capability.WRITE,
)
async def mist_release_site_ssr_dhcp_lease(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/release_dhcp"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/release_dhcp",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_run_site_srx_top_command",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/run_top\n\nrunSiteSrxTopCommand\n\nRun top command on switches and SRX. The output will be available through websocket. \n\nAs there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n  "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```',
    capability=Capability.WRITE,
)
async def mist_run_site_srx_top_command(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/run_top",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_service_ping_from_ssr",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/service_ping\n\nservicePingFromSsr\n\nPing from SSR\n\nService Ping can be performed from the Device. The output will be available through websocket. As there can be multiple command issued against the same device at the same time and the output all goes through the same websocket stream, session is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n##### Example output from ws stream\n```json\n{\n    "event": "data",\n    "channel": "/sites...',
    capability=Capability.WRITE,
)
async def mist_service_ping_from_ssr(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/service_ping",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_gateway_ospf_database",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_ospf_database\n\nshowSiteGatewayOspfDatabase\n\nGet OSPF Database from SSR and SRX. The output will be available through websocket. \n\nAs there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n  "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n\n#### Example output from ws stream\n```\n===== ==================== ========== ======= ======== ==...',
    capability=Capability.WRITE,
)
async def mist_show_site_gateway_ospf_database(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_ospf_database",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_gateway_ospf_interfaces",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_ospf_interfaces\n\nshowSiteGatewayOspfInterfaces\n\nGet OSPF interfaces from SSR and SRX. The output will be available through websocket. \n\nAs there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n  "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n\n#### Example output from ws stream\n```\n===== ================== =================== ======...',
    capability=Capability.WRITE,
)
async def mist_show_site_gateway_ospf_interfaces(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_ospf_interfaces",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_gateway_ospf_neighbors",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_ospf_neighbors\n\nshowSiteGatewayOspfNeighbors\n\nGet OSPF Neighbors from SSR and SRX. The output will be available through websocket. \n\nAs there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n  "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n\n#### Example output from ws stream\n```\n===== ==================== ========== ======= ========...',
    capability=Capability.WRITE,
)
async def mist_show_site_gateway_ospf_neighbors(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_ospf_neighbors",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_gateway_ospf_summary",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_ospf_summary\n\nshowSiteGatewayOspfSummary\n\nGet OSPF summary from SSR and SRX. The output will be available through websocket. \n\nAs there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n  "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n\n#### Example output from ws stream\n```\n===== =========== ========== ============= =================...',
    capability=Capability.WRITE,
)
async def mist_show_site_gateway_ospf_summary(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_ospf_summary",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_ssr_and_srx_routes",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_route\n\nshowSiteSsrAndSrxRoutes\n\nGet routes from SSR, SRX and Switch. \n\nThe output will be available through websocket. As there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n##### Example output from ws stream\n```\nadmin@labsystem1.fiedler# show bgp neighbors\nBGP neighbor is 192.1...',
    capability=Capability.WRITE,
)
async def mist_show_site_ssr_and_srx_routes(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="All attributes are optional")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_route",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_ssr_and_srx_sessions",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_session\n\nshowSiteSsrAndSrxSessions\n\nGet active sessions passing through the Device.\n\n\nThe output will be available through websocket. As there can be multiple command\nissued against the same device at the same time and the output all goes through\nthe same websocket stream, session is introduced for demux.\n\n\n\n#### Subscribe to Device Command outputs\n\n`WS /api-ws/v1/stream`\n\n\n```json \n{ "subscribe": "/sites/{site_id}/devices/{device_id}/cmd" }\n```\n\n\n#### Example output from ws stream\n\n```json \n{\n      "channel": "/sites/d6fb4f96-xxxx-xxxx-...',
    capability=Capability.WRITE,
)
async def mist_show_site_ssr_and_srx_sessions(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/show_session"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_session",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_show_site_ssr_service_path",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/show_service_path\n\nshowSiteSsrServicePath\n\nGet service path information of the Device.\n\n\nThe output will be available through websocket. As there can be multiple command\nissued against the same device at the same time and the output all goes through\nthe same websocket stream, session is introduced for demux.\n\n\n\n#### Subscribe to Device Command outputs\n\n`WS /api-ws/v1/stream`\n\n\n```json\n{ "subscribe": "/sites/{site_id}/devices/{device_id}/cmd" }\n```\n\n#### Example output from ws stream\n\n```json\n{\n      "channel": "/sites/d6fb4f96-xxxx-xxxx-xxxx-...',
    capability=Capability.WRITE,
)
async def mist_show_site_ssr_service_path(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/show_service_path",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/show_service_path",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_test_site_ssr_dns_resolution",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/resolve_dns\n\ntestSiteSsrDnsResolution\n\nDNS resolutions are performed on the Device.\n\nThe output will be available through websocket. As there can be multiple commands issued against the same SSR at the same time and the output all goes through the same websocket stream, `session` is used for demux.\n \n #### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n##### Example output from ws stream\n```\n Router      | Hostname               | Resolved | Last Resolved...',
    capability=Capability.WRITE,
)
async def mist_test_site_ssr_dns_resolution(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/resolve_dns",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )
