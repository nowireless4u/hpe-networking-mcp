"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``appliance``
Operations in this file: 32
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
    name="edgeconnect_delete_appliance",
    description="DELETE /appliance\n\nApplianceDel80\n\nQueue an appliance for deletion from the network.",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_appliance(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_appliance_delete_for_discovery",
    description="DELETE /appliance/deleteForDiscovery\n\nDeleteForRediscovery49\n\nQueue appliance for deletion from Orchestrator for rediscovery",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_appliance_delete_for_discovery(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/appliance/deleteForDiscovery",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_appliance_discovered_delete",
    description="DELETE /appliance/discovered/delete\n\ndeleteDiscoveredByPortalObjectId\n\nDelete a discovered appliance or queue a managed appliance for deletion",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_appliance_discovered_delete(
    ctx: Context,
    portalObjectId: Annotated[
        str,
        Field(
            description="The unique portal object identifier for the appliance. This ID is assigned by the cloud portal and uniquely identifies the appliance across the system."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if portalObjectId is not None:
        query_params["portalObjectId"] = portalObjectId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/appliance/discovered/delete",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_appliance_pppoe",
    description="DELETE /appliance/pppoe\n\ndeletePPPoEList\n\nDelete a PPPoE virtual interface configuration from an appliance",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_appliance_pppoe(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    pppoeName: Annotated[
        str,
        Field(
            description="Name of the PPPoE virtual interface to delete. Must be a valid, non-empty PPPoE configuration name."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if pppoeName is not None:
        query_params["pppoeName"] = pppoeName
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/appliance/pppoe",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_appliance_rest",
    description="DELETE /appliance/rest\n\napplianceDELETEAPI69\n\nDelete appliance resource via passthrough API",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_appliance_rest(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    url: Annotated[
        str,
        Field(
            description="Appliance API path relative to '/rest/json/'. For example, use 'shaper' to call '/rest/json/shaper'."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if url is not None:
        query_params["url"] = url
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/appliance/rest",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_get_appliance",
    description="GET /appliance\n\nApplianceGetOne81\n\nRetrieve appliance information by nePk or list all accessible appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_approved",
    description="GET /appliance/approved\n\ngetAllApprovedAppliances\n\nRetrieve all approved appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_approved(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/approved",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_appliance_custom_tag_meta",
    description="GET /appliance/customTagMeta\n\ngetCustomTagMeta\n\nGet custom tag metadata for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_custom_tag_meta(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    If_None_Match: Annotated[
        str | None,
        Field(
            default=None,
            description="ETag value from a previous response. If the data has not changed, a 304 Not Modified response is returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    header_params: dict[str, Any] = {}
    if If_None_Match is not None:
        header_params["If-None-Match"] = If_None_Match
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/customTagMeta",
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_denied",
    description="GET /appliance/denied\n\ngetAllDeniedAppliances\n\nRetrieve all denied appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_denied(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/denied",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_appliance_discovered",
    description="GET /appliance/discovered\n\ngetAllDiscoveredAppliances\n\nGet all discovered appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_discovered(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/discovered",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_appliance_dns_cache_config",
    description="GET /appliance/dnsCache/config\n\ngetDnsCacheConfig\n\nGet DNS Cache Configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_dns_cache_config(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="Data source selector. When true, retrieves from Orchestrator's database cache. When false, fetches directly from the appliance (slower but real-time).",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/dnsCache/config",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_ha_peer_meta",
    description="GET /appliance/haPeerMeta\n\ngetHaPeerMeta\n\nRetrieve HA peer metadata for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_ha_peer_meta(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    If_None_Match: Annotated[
        str | None,
        Field(
            default=None,
            description="ETag value from a previous response for conditional request. If the data has not changed, the server returns HTTP 304 Not Modified.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    header_params: dict[str, Any] = {}
    if If_None_Match is not None:
        header_params["If-None-Match"] = If_None_Match
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/haPeerMeta",
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_interface_meta",
    description="GET /appliance/interfaceMeta\n\ngetInterfaceMeta\n\nGet interface labels for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_interface_meta(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    If_None_Match: Annotated[
        str | None, Field(default=None, description="ETag value from previous response. Returns 304 if data unchanged.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    header_params: dict[str, Any] = {}
    if If_None_Match is not None:
        header_params["If-None-Match"] = If_None_Match
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/interfaceMeta",
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_pppoe_list",
    description="GET /appliance/pppoeList\n\ngetPPPoEList\n\nGet PPPoE configuration list from appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_pppoe_list(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="Data source selector. When 'true' (default), retrieves from Orchestrator cache. When 'false', fetches live data from the appliance and updates the cache.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/pppoeList",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_queued_for_deletion",
    description="GET /appliance/queuedForDeletion\n\nCheckAppliancesQueuedForDeletion67\n\nGet appliances queued for deletion",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_queued_for_deletion(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/queuedForDeletion",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_appliance_rest",
    description="GET /appliance/rest\n\napplianceGetAPI70\n\nRetrieve appliance data via passthrough API",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_rest(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    url: Annotated[
        str,
        Field(
            description="Appliance API path relative to '/rest/json/'. Use 'shaper' to call '/rest/json/shaper'. May include query parameters after '?'."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if url is not None:
        query_params["url"] = url
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/rest",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_scalars",
    description="GET /appliance/scalars\n\ngetScalars\n\nGet scalar data of an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_scalars(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="Controls data source. When 'true' (default), retrieves from Orchestrator cache for faster response. When 'false', fetches directly from the appliance and updates the cache.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/scalars",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_shell_shell_access_setting",
    description="GET /appliance/shell/shellAccessSetting\n\ngetShellAccessSetting\n\nGet shell access setting of appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_shell_shell_access_setting(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="When 'true', returns data from Orchestrator's cache. When 'false', fetches data directly from the appliance. Defaults to 'true' if not specified.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/shell/shellAccessSetting",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_stats_config",
    description="GET /appliance/statsConfig\n\nstatsConfigGet75\n\nGet appliance statistics configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_stats_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/statsConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_appliance_stats_config_default",
    description="GET /appliance/statsConfig/default\n\nstatsConfigDefaultGet77\n\nGet default appliance statistics configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_stats_config_default(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/statsConfig/default",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_appliance_zone_list_meta",
    description="GET /appliance/zoneListMeta\n\ngetZoneListMeta79\n\nGet cached zone list metadata for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_zone_list_meta(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
    If_None_Match: Annotated[
        str | None,
        Field(
            default=None,
            description="ETag value from previous response for cache validation. Returns 304 if data unchanged.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    header_params: dict[str, Any] = {}
    if If_None_Match is not None:
        header_params["If-None-Match"] = If_None_Match
    return await edgeconnect_request(
        ctx,
        "GET",
        "/appliance/zoneListMeta",
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="edgeconnect_post_appliance",
    description="POST /appliance\n\nApplianceChg82\n\nUpdate an appliance's IP, credentials, network role, site, and web protocol",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_appliance_change_group",
    description="POST /appliance/changeGroup\n\nApplianceChgGr46\n\nMove appliances to a different group",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_change_group(
    ctx: Context,
    groupPk: Annotated[
        str,
        Field(
            description="Target group primary key where appliances will be moved. Format: '<id>.Network' (e.g., '5.Network')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if groupPk is not None:
        query_params["groupPk"] = groupPk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/changeGroup",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_appliance_change_password",
    description="POST /appliance/changePassword\n\nchangeAppliancePassword47\n\nChange a user's password on an appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_change_password(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    username: Annotated[
        str,
        Field(
            description="The username on the appliance whose password will be changed. Must match an existing user on the appliance."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if username is not None:
        query_params["username"] = username
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/changePassword",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_appliance_denied_delete",
    description="POST /appliance/denied/delete\n\ndeleteDeniedAppliances51\n\nDelete denied appliances permanently",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_denied_delete(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/denied/delete",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_appliance_discovered_add",
    description="POST /appliance/discovered/add\n\naddDiscoveredApplianceToOrchestrator\n\nAdd a discovered appliance to Orchestrator without portal approval",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_discovered_add(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Primary key (ID) of the discovered appliance to add. Obtain this value from /appliance/discovered endpoint."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/discovered/add",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_appliance_discovered_approve",
    description="POST /appliance/discovered/approve\n\napproveDiscoveredAppliances54\n\nApprove and add a discovered appliance to Orchestrator.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_discovered_approve(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Primary key ID of the discovered appliance to approve. Use /appliance/discovered API to retrieve available IDs."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/discovered/approve",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_appliance_discovered_deny",
    description="POST /appliance/discovered/deny\n\ndenyDiscoveredAppliances55\n\nDeny a discovered appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_discovered_deny(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Primary key (database ID) of the discovered appliance to deny. This ID is returned from the GET /appliance/discovered endpoint."
        ),
    ],
    body: Annotated[str | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/discovered/deny",
        query_params=query_params or None,
        body=body,
        body_mode="text",
    )


@tool(
    name="edgeconnect_post_appliance_rediscover_appliance",
    description="POST /appliance/rediscoverAppliance\n\nrediscoverAppliance68\n\nRediscover a denied appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_rediscover_appliance(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the discovered appliance to rediscover. Must reference an existing appliance in the denied state."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/rediscoverAppliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_appliance_rest",
    description="POST /appliance/rest\n\nappliancePostAPI71\n\nModify appliance settings via passthrough API",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_rest(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    url: Annotated[
        str,
        Field(
            description="Appliance API path relative to '/rest/json/'. Leading '/' is optional and will be stripped. May include query parameters after '?'."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if url is not None:
        query_params["url"] = url
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/rest",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_appliance_stats_config",
    description="POST /appliance/statsConfig\n\nstatsConfigPost76\n\nUpdate appliance statistics configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_stats_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/statsConfig",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_appliance_discovered_update",
    description="PUT /appliance/discovered/update\n\ntriggerUpdateDiscoveredAppliances\n\nTrigger discovered appliances update job",
    capability=Capability.WRITE,
)
async def edgeconnect_put_appliance_discovered_update(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/appliance/discovered/update",
        query_params=None,
    )
