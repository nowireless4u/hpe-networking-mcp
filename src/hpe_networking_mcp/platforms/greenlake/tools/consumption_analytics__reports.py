"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/consumption-analytics.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``consumption-analytics``   Tag: ``reports``   Operations: 7
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_consumption_analytics_v2_reports",
    description="GET /consumption-analytics/v2/reports\n\nreports-v2-list\n\nList report definitions",
    capability=Capability.READ,
)
async def greenlake_get_consumption_analytics_v2_reports(
    ctx: Context,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of items to return.")] = None,
    offset: Annotated[
        int | None,
        Field(default=None, description="The number of items to skip before starting to collect the result set."),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        "/consumption-analytics/v2/reports",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_consumption_analytics_v2_reports_id",
    description="GET /consumption-analytics/v2/reports/{id}\n\nreports-v2-get-by-id\n\nRetrieve a report definition",
    capability=Capability.READ,
)
async def greenlake_get_consumption_analytics_v2_reports_id(
    ctx: Context,
    id: Annotated[str, Field(description="The ID of the report definition.")],
) -> Any:
    path = f"/consumption-analytics/v2/reports/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_consumption_analytics_v2_reports_usage_fields",
    description="GET /consumption-analytics/v2/reports/usage-fields\n\nreports-v2-usage-fields\n\nList usage fields",
    capability=Capability.READ,
)
async def greenlake_get_consumption_analytics_v2_reports_usage_fields(
    ctx: Context,
) -> Any:
    return await greenlake_request(
        ctx,
        "GET",
        "/consumption-analytics/v2/reports/usage-fields",
    )


@tool(
    name="greenlake_post_consumption_analytics_v2_reports_execute",
    description="POST /consumption-analytics/v2/reports/execute\n\nreports-v2-gen-by-def\n\nGenerate report from definition",
    capability=Capability.WRITE,
)
async def greenlake_post_consumption_analytics_v2_reports_execute(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/consumption-analytics/v2/reports/execute",
        body=body,
    )


@tool(
    name="greenlake_post_consumption_analytics_v2_reports_execute_csv",
    description="POST /consumption-analytics/v2/reports/execute/csv\n\nreports-v2-gen-by-def-csv\n\nGenerate report from definition as CSV",
    capability=Capability.WRITE,
)
async def greenlake_post_consumption_analytics_v2_reports_execute_csv(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/consumption-analytics/v2/reports/execute/csv",
        body=body,
    )


@tool(
    name="greenlake_post_consumption_analytics_v2_reports_id_execute",
    description="POST /consumption-analytics/v2/reports/{id}/execute\n\nreports-v2-gen-by-id\n\nGenerate report for saved definition",
    capability=Capability.WRITE,
)
async def greenlake_post_consumption_analytics_v2_reports_id_execute(
    ctx: Context,
    id: Annotated[str, Field(description="The ID of the report to export.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/consumption-analytics/v2/reports/{path_seg(id)}/execute"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_consumption_analytics_v2_reports_id_execute_csv",
    description="POST /consumption-analytics/v2/reports/{id}/execute/csv\n\nreports-v2-gen-by-id-csv\n\nGenerate saved report as CSV",
    capability=Capability.WRITE,
)
async def greenlake_post_consumption_analytics_v2_reports_id_execute_csv(
    ctx: Context,
    id: Annotated[str, Field(description="The ID of the saved report to export.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/consumption-analytics/v2/reports/{path_seg(id)}/execute/csv"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
