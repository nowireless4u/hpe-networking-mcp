"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs SLEs``
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
    name="mist_get_org_sites_sle",
    description="GET /api/v1/orgs/{org_id}/insights/sites-sle\n\ngetOrgSitesSle\n\nGet Org Sites SLE",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_sites_sle(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sle: Annotated[Any | None, Field(description="query parameter 'sle'")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/insights/sites-sle",
        path_params={"org_id": org_id},
        query_params={
            "sle": sle,
            "start": start,
            "end": end,
            "duration": duration,
            "interval": interval,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_sle",
    description="GET /api/v1/orgs/{org_id}/insights/{metric}\n\ngetOrgSle\n\nGet Org SLEs (all/worst sites, Mx Edges, ...)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_sle(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    metric: Annotated[
        str, Field(description="See [List Insight Metrics](/#operations/listInsightMetrics) for available metrics")
    ],
    sle: Annotated[
        str | None, Field(description="See [List Insight Metrics](/#operations/listInsightMetrics) for more details")
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/insights/{metric}",
        path_params={"org_id": org_id, "metric": metric},
        query_params={"sle": sle, "duration": duration, "interval": interval, "start": start, "end": end},
        body=None,
    )
