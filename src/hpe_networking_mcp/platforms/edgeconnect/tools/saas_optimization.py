"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``saasOptimization``
Operations in this file: 2
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
    name="edgeconnect_get_cloud_applications_config",
    description="GET /cloudApplications/config\n\ncloudAppsConfig160\n\nGet SaaS Optimization configuration for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_applications_config(
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
            description="Data retrieval source flag. When true (default), returns cached data from Orchestrator. When false, fetches fresh data directly from the appliance.",
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
        "/cloudApplications/config",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_applications_monitor",
    description="GET /cloudApplications/monitor\n\ncloudAppsMonitor161\n\nGet SaaS application subnet monitoring data including RTT and reachability status",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_applications_monitor(
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
            description="Data retrieval source flag. When true (default), returns cached data from Orchestrator. When false, fetches fresh data directly from the appliance.",
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
        "/cloudApplications/monitor",
        query_params=query_params or None,
    )
