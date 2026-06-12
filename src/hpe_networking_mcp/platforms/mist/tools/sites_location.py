"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Location``
Operations in this file: 8
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
    name="mist_clear_site_ml_overwrite_for_device",
    description="DELETE /api/v1/sites/{site_id}/location/ml/device/{device_id}\n\nclearSiteMlOverwriteForDevice\n\nClear ML Overwrite for Device",
    capability=Capability.WRITE_DELETE,
)
async def mist_clear_site_ml_overwrite_for_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/location/ml/device/{device_id}",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_clear_site_ml_overwrite_for_map",
    description="DELETE /api/v1/sites/{site_id}/location/ml/map/{map_id}\n\nclearSiteMlOverwriteForMap\n\nClear ML Overwrite for Map",
    capability=Capability.WRITE_DELETE,
)
async def mist_clear_site_ml_overwrite_for_map(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/location/ml/map/{map_id}",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_beam_coverage_overview",
    description="GET /api/v1/sites/{site_id}/location/coverage\n\ngetSiteBeamCoverageOverview\n\nGet Beam Coverage Overview",
    capability=Capability.READ,
)
async def mist_get_site_beam_coverage_overview(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str | None, Field(description="Filter results by map identifier")] = None,
    type: Annotated[
        Any | None, Field(description="Filter results by type. enum: `asset`, `client`, `sdkclient`")
    ] = None,
    client_type: Annotated[str | None, Field(description="Filter results by client type")] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    resolution: Annotated[
        Any | None, Field(description="Location calculation resolution used by the query. enum: `default`, `fine`")
    ] = None,
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
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/location/coverage",
        path_params={"site_id": site_id},
        query_params={
            "map_id": map_id,
            "type": type,
            "client_type": client_type,
            "duration": duration,
            "resolution": resolution,
            "start": start,
            "end": end,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_default_plf_for_models",
    description="GET /api/v1/sites/{site_id}/location/ml/defaults\n\ngetSiteDefaultPlfForModels\n\nGet Default PLF for Models",
    capability=Capability.READ,
)
async def mist_get_site_default_plf_for_models(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/location/ml/defaults",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_machine_learning_current_stat",
    description="GET /api/v1/sites/{site_id}/location/ml/current\n\ngetSiteMachineLearningCurrentStat\n\nGet Machine Learning Current Stat\nFor each VBLE AP, it has ML model parameters (e.g. Path-loss-estimate, Intercept) as well as completion indicators (Level and PercentageComplete). For the completeness, ML takes N sample to finish its first level and use N*0.25 samples to complete each successive level. When a device is moved, the completeness will be reset as it has to re-learn.",
    capability=Capability.READ,
)
async def mist_get_site_machine_learning_current_stat(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str | None, Field(description="Filter results by map identifier")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/location/ml/current",
        path_params={"site_id": site_id},
        query_params={"map_id": map_id},
        body=None,
    )


@_mcp_tool(
    name="mist_overwrite_site_ml_for_device",
    description="PUT /api/v1/sites/{site_id}/location/ml/device/{device_id}\n\noverwriteSiteMlForDevice\n\nOverwrite ML For Device",
    capability=Capability.WRITE,
)
async def mist_overwrite_site_ml_for_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/location/ml/device/{device_id}",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_overwrite_site_ml_for_map",
    description="PUT /api/v1/sites/{site_id}/location/ml/map/{map_id}\n\noverwriteSiteMlForMap\n\nOverwrite ML For Map",
    capability=Capability.WRITE,
)
async def mist_overwrite_site_ml_for_map(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/location/ml/map/{map_id}",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_reset_site_ml_stats_by_map",
    description="POST /api/v1/sites/{site_id}/location/ml/reset/map/{map_id}\n\nresetSiteMlStatsByMap\n\nReset ML Stats by Map",
    capability=Capability.WRITE,
)
async def mist_reset_site_ml_stats_by_map(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/location/ml/reset/map/{map_id}",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=None,
    )
