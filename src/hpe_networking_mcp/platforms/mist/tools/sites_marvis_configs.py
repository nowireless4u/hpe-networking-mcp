"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Marvis Configs``
Operations in this file: 4
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
    name="mist_count_site_marvis_config_actions",
    description="GET /api/v1/sites/{site_id}/marvis_configs/count\n\ncountSiteMarvisConfigActions\n\nCount Marvis Config Actions for a site by a distinct field.",
    capability=Capability.READ,
)
async def mist_count_site_marvis_config_actions(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[
        str,
        Field(
            description="Field to count by. enum: `mac`, `type`, `src`, `admin_id`, `op`, `port_id`, `reason`, `vlan_ids`"
        ),
    ] = "mac",
    mac: Annotated[str | None, Field(description="Filter by device MAC address")] = None,
    type: Annotated[str | None, Field(description="Filter by config type (e.g. wired)")] = None,
    src: Annotated[str | None, Field(description="Filter by source of the config action (e.g. marvis)")] = None,
    admin_id: Annotated[str | None, Field(description="Filter by admin ID")] = None,
    op: Annotated[
        str | None,
        Field(description="Filter by operation type (e.g. disable_port, enable_port, update_mtu, add_vlans_to_port)"),
    ] = None,
    port_id: Annotated[str | None, Field(description="Filter by port identifier (e.g. ge-0/0/13)")] = None,
    vlan_ids: Annotated[int | None, Field(description="Filter by VLAN ID")] = None,
    reason: Annotated[
        str | None, Field(description="Filter by reason for the config action (e.g. rogue_dhcp_server_detected)")
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
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
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/marvis_configs/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "mac": mac,
            "type": type,
            "src": src,
            "admin_id": admin_id,
            "op": op,
            "port_id": port_id,
            "vlan_ids": vlan_ids,
            "reason": reason,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_delete_site_marvis_config_action",
    description="DELETE /api/v1/sites/{site_id}/marvis_configs/{id}\n\ndeleteSiteMarvisConfigAction\n\nDelete a Marvis Config Action.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_site_marvis_config_action(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    id: Annotated[str, Field(description="UUID of the Marvis Config Action")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/marvis_configs/{id}",
        path_params={"site_id": site_id, "id": id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_marvis_config_actions",
    description="GET /api/v1/sites/{site_id}/marvis_configs/search\n\nsearchSiteMarvisConfigActions\n\nSearch Marvis Config Actions for a site.",
    capability=Capability.READ,
)
async def mist_search_site_marvis_config_actions(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mac: Annotated[str | None, Field(description="Filter by device MAC address")] = None,
    type: Annotated[str | None, Field(description="Filter by config type (e.g. wired)")] = None,
    src: Annotated[str | None, Field(description="Filter by source of the config action (e.g. marvis)")] = None,
    admin_id: Annotated[str | None, Field(description="Filter by admin ID")] = None,
    op: Annotated[
        str | None,
        Field(description="Filter by operation type (e.g. disable_port, enable_port, update_mtu, add_vlans_to_port)"),
    ] = None,
    port_id: Annotated[str | None, Field(description="Filter by port identifier (e.g. ge-0/0/13)")] = None,
    vlan_ids: Annotated[int | None, Field(description="Filter by VLAN ID")] = None,
    reason: Annotated[
        str | None, Field(description="Filter by reason for the config action (e.g. rogue_dhcp_server_detected)")
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
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
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/marvis_configs/search",
        path_params={"site_id": site_id},
        query_params={
            "mac": mac,
            "type": type,
            "src": src,
            "admin_id": admin_id,
            "op": op,
            "port_id": port_id,
            "vlan_ids": vlan_ids,
            "reason": reason,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_submit_site_marvis_config_feedback",
    description="POST /api/v1/sites/{site_id}/marvis_configs/{id}/feedback\n\nsubmitSiteMarvisConfigFeedback\n\nSubmit feedback on a Marvis-injected config action (e.g. mark as invalid).",
    capability=Capability.WRITE,
)
async def mist_submit_site_marvis_config_feedback(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    id: Annotated[str, Field(description="UUID of the Marvis Config Action")],
    body: Annotated[dict[str, Any], Field(description="Request Body")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/marvis_configs/{id}/feedback",
        path_params={"site_id": site_id, "id": id},
        query_params=None,
        body=body,
    )
