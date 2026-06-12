"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Marvis``
Operations in this file: 1
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
    name="mist_troubleshoot_org",
    description="GET /api/v1/orgs/{org_id}/troubleshoot\n\ntroubleshootOrg\n\nTroubleshoot sites, devices, clients, and wired clients for maximum of last 7 days from current time. See search APIs for device information:\n- [search Device](/#operations/searchOrgDevices)\n- [search Wireless Client](/#operations/searchOrgWirelessClients)\n- [search Wired Client](/#operations/searchOrgWiredClients)\n- [search Wan Client](/#operations/searchOrgWanClients)\n\n**NOTE**: requires Marvis subscription license",
    capability=Capability.READ,
)
async def mist_troubleshoot_org(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mac: Annotated[str | None, Field(description="**required** when troubleshooting device or a client")] = None,
    site_id: Annotated[str | None, Field(description="**required** when troubleshooting site")] = None,
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
    type: Annotated[
        Any | None,
        Field(
            description="When troubleshooting site, type of network to troubleshoot. enum: `wan`, `wired`, `wireless`"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/troubleshoot",
        path_params={"org_id": org_id},
        query_params={"mac": mac, "site_id": site_id, "start": start, "end": end, "type": type},
        body=None,
    )
