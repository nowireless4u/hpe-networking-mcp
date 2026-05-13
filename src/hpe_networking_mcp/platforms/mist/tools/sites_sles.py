"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Sites SLEs``
Operations in this file: 19
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
    name="mist_get_site_sle_classifier_details",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/classifier/{classifier}/summary\n\ngetSiteSleClassifierDetails\n\nGet SLE classifier details\n\n\nThis API Endpoint is deprecated and replaced by [Get Site SLE Classifier Summary Trend](/#operations/getSiteSleClassifierSummaryTrend)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_sle_classifier_details(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[
        str,
        Field(
            description="* site_id if `scope`==`site`\n* device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway`\n* mac if `scope`==`client`"
        ),
    ],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    classifier: Annotated[str, Field(description="path parameter 'classifier'")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/classifier/{classifier}/summary",
        path_params={
            "site_id": site_id,
            "scope": scope,
            "scope_id": scope_id,
            "metric": metric,
            "classifier": classifier,
        },
        query_params={"start": start, "end": end, "duration": duration},
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_sle_classifier_summary_trend",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/classifier/{classifier}/summary-trend\n\ngetSiteSleClassifierSummaryTrend\n\nGet SLE classifier Summary Trend",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_sle_classifier_summary_trend(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[
        str,
        Field(
            description="* site_id if `scope`==`site`\n* device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway`\n* mac if `scope`==`client`"
        ),
    ],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    classifier: Annotated[str, Field(description="path parameter 'classifier'")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/classifier/{classifier}/summary-trend",
        path_params={
            "site_id": site_id,
            "scope": scope,
            "scope_id": scope_id,
            "metric": metric,
            "classifier": classifier,
        },
        query_params={"start": start, "end": end, "duration": duration},
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_sle_histogram",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/histogram\n\ngetSiteSleHistogram\n\nGet the histogram for the SLE metric",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_sle_histogram(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[
        str,
        Field(
            description="* site_id if `scope`==`site`\n* device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway`\n* mac if `scope`==`client`"
        ),
    ],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/histogram",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration},
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_sle_impact_summary",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impact-summary\n\ngetSiteSleImpactSummary\n\nGet impact summary counts optionally filtered by classifier and failure type\n \n* Wireless SLE Fields: `wlan`, `device_type`, `device_os` ,`band`, `ap`, `server`, `mxedge`\n* Wired SLE Fields: `switch`, `client`, `vlan`, `interface`, `chassis`\n* WAN SLE Fields: `gateway`, `client`, `interface`, `chassis`, `peer_path`, `gateway_zones`",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_sle_impact_summary(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[
        str,
        Field(
            description="* site_id if `scope`==`site`\n* device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway`\n* mac if `scope`==`client`"
        ),
    ],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    fields: Annotated[Any | None, Field(description="query parameter 'fields'")] = None,
    classifier: Annotated[str | None, Field(description="query parameter 'classifier'")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impact-summary",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration, "fields": fields, "classifier": classifier},
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_sle_summary",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/summary\n\ngetSiteSleSummary\n\nGet the summary for the SLE metric\n\n\nThis API Endpoint is deprecated and replaced by [Get Site SLE Summary Trend](/#operations/getSiteSleSummaryTrend)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_sle_summary(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[
        str,
        Field(
            description="* site_id if `scope`==`site`\n* device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway`\n* mac if `scope`==`client`"
        ),
    ],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/summary",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration},
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_sle_summary_trend",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/summary-trend\n\ngetSiteSleSummaryTrend\n\nGet the summary for the SLE metric trend",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_sle_summary_trend(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[
        str,
        Field(
            description="* site_id if `scope`==`site`\n* device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway`\n* mac if `scope`==`client`"
        ),
    ],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/summary-trend",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration},
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_sle_threshold",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/threshold\n\ngetSiteSleThreshold\n\nGet the SLE threshold",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_sle_threshold(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[
        str,
        Field(
            description="* site_id if `scope`==`site`\n* device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway`\n* mac if `scope`==`client`"
        ),
    ],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/threshold",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_sle_impacted_applications",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-applications\n\nlistSiteSleImpactedApplications\n\nFor WAN SLEs. List the impacted interfaces optionally filtered by classifier and failure type",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_sle_impacted_applications(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[str, Field(description="path parameter 'scope_id'")],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    classifier: Annotated[str | None, Field(description="query parameter 'classifier'")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-applications",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration, "classifier": classifier},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_sle_impacted_aps",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-aps\n\nlistSiteSleImpactedAps\n\nFor Wireless SLEs. List the impacted APs optionally filtered by classifier and failure type",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_sle_impacted_aps(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[str, Field(description="path parameter 'scope_id'")],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    classifier: Annotated[str | None, Field(description="query parameter 'classifier'")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-aps",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration, "classifier": classifier},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_sle_impacted_chassis",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-chassis\n\nlistSiteSleImpactedChassis\n\nFor Wired and WAN SLEs. List the impacted interfaces optionally filtered by classifier and failure type",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_sle_impacted_chassis(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[str, Field(description="path parameter 'scope_id'")],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    classifier: Annotated[str | None, Field(description="query parameter 'classifier'")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-chassis",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration, "classifier": classifier},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_sle_impacted_gateways",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-gateways\n\nlistSiteSleImpactedGateways\n\nFor WAN SLEs. List the impacted interfaces optionally filtered by classifier and failure type",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_sle_impacted_gateways(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[str, Field(description="path parameter 'scope_id'")],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    classifier: Annotated[str | None, Field(description="query parameter 'classifier'")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-gateways",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration, "classifier": classifier},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_sle_impacted_interfaces",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-interfaces\n\nlistSiteSleImpactedInterfaces\n\nFor Wired and WAN SLEs. List the impacted interfaces optionally filtered by classifier and failure type",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_sle_impacted_interfaces(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[str, Field(description="path parameter 'scope_id'")],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    classifier: Annotated[str | None, Field(description="query parameter 'classifier'")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-interfaces",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration, "classifier": classifier},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_sle_impacted_switches",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-switches\n\nlistSiteSleImpactedSwitches\n\nFor Wired SLEs. List the impacted switches optionally filtered by classifier and failure type",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_sle_impacted_switches(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[str, Field(description="path parameter 'scope_id'")],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    classifier: Annotated[str | None, Field(description="query parameter 'classifier'")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-switches",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration, "classifier": classifier},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_sle_impacted_wired_clients",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-clients\n\nlistSiteSleImpactedWiredClients\n\nFor Wired SLEs. List the impacted interfaces optionally filtered by classifier and failure type",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_sle_impacted_wired_clients(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[str, Field(description="path parameter 'scope_id'")],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    classifier: Annotated[str | None, Field(description="query parameter 'classifier'")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-clients",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration, "classifier": classifier},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_sle_impacted_wireless_clients",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-users\n\nlistSiteSleImpactedWirelessClients\n\nFor Wireless SLEs. List the impacted wireless users optionally filtered by classifier and failure type",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_sle_impacted_wireless_clients(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[str, Field(description="path parameter 'scope_id'")],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    classifier: Annotated[str | None, Field(description="query parameter 'classifier'")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/impacted-users",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params={"start": start, "end": end, "duration": duration, "classifier": classifier},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_sle_metric_classifiers",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/classifiers\n\nlistSiteSleMetricClassifiers\n\nList classifiers for a specific metric",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_sle_metric_classifiers(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[
        str,
        Field(
            description="* site_id if `scope`==`site`\n* device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway`\n* mac if `scope`==`client`"
        ),
    ],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/classifiers",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_sles_metrics",
    description="GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metrics\n\nlistSiteSlesMetrics\n\nList the metrics for the given scope",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_sles_metrics(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[
        str,
        Field(
            description="* site_id if `scope`==`site`\n* device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway`\n* mac if `scope`==`client`"
        ),
    ],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metrics",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_replace_site_sle_threshold",
    description="POST /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/threshold\n\nreplaceSiteSleThreshold\n\nReplace the SLE threshold",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_replace_site_sle_threshold(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[
        str,
        Field(
            description="* site_id if `scope`==`site`\n* device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway`\n* mac if `scope`==`client`"
        ),
    ],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/threshold",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/threshold",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_site_sle_threshold",
    description="PUT /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/threshold\n\nupdateSiteSleThreshold\n\nUpdate the SLE threshold",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_sle_threshold(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    scope: Annotated[Any, Field(description="path parameter 'scope'")],
    scope_id: Annotated[
        str,
        Field(
            description="* site_id if `scope`==`site`\n* device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway`\n* mac if `scope`==`client`"
        ),
    ],
    metric: Annotated[str, Field(description="Values from `listSiteSlesMetrics`")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for PUT /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/threshold",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metric/{metric}/threshold",
        path_params={"site_id": site_id, "scope": scope, "scope_id": scope_id, "metric": metric},
        query_params=None,
        body=body,
    )
