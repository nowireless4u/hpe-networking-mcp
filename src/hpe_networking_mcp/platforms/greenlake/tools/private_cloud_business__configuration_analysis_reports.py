"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/private-cloud-business.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``private-cloud-business``   Tag: ``configuration_analysis_reports``   Operations: 3
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_private_cloud_business_v1beta1_configuration_analysis_reports",
    description="GET /private-cloud-business/v1beta1/configuration-analysis-reports\n\nListLatestConfigAnalysisReport\n\nReturns a list of config analysis rules execution results.",
    capability=Capability.READ,
)
async def greenlake_get_private_cloud_business_v1beta1_configuration_analysis_reports(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(default=None, description="Filter criteria - e.g. systemId eq c0930136-5317-5647-8d92-87ca3984c5f9"),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="The resource property to sort by followed by the response order. Response order can be either “asc” (ascending) or “desc” (descending)",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    return await greenlake_request(
        ctx,
        "GET",
        "/private-cloud-business/v1beta1/configuration-analysis-reports",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_private_cloud_business_v1beta1_configuration_analysis_reports_report_id",
    description="GET /private-cloud-business/v1beta1/configuration-analysis-reports/{reportId}\n\nListConfigAnalysisReportById\n\nReturns a config analysis rules execution results for the provided reportId.",
    capability=Capability.READ,
)
async def greenlake_get_private_cloud_business_v1beta1_configuration_analysis_reports_report_id(
    ctx: Context,
    reportId: Annotated[str, Field(description="Unique identifier of a Config Analysis Report.")],
) -> Any:
    path = f"/private-cloud-business/v1beta1/configuration-analysis-reports/{path_seg(reportId)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_private_cloud_business_v1beta1_configuration_analysis_reports",
    description="POST /private-cloud-business/v1beta1/configuration-analysis-reports\n\nExecuteConfigAnalysisRules\n\nInitiates config analysis rules execution.",
    capability=Capability.WRITE,
)
async def greenlake_post_private_cloud_business_v1beta1_configuration_analysis_reports(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/private-cloud-business/v1beta1/configuration-analysis-reports",
        body=body,
    )
