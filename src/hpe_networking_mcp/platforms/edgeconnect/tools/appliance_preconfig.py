"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``appliancePreconfig``
Operations in this file: 11
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
    name="edgeconnect_delete_gms_appliance_preconfiguration",
    description="DELETE /gms/appliance/preconfiguration\n\ndeletePreconfiguration251\n\nDelete an appliance preconfiguration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_gms_appliance_preconfiguration(
    ctx: Context,
    preconfigId: Annotated[
        int,
        Field(
            description="Unique identifier of the preconfiguration to delete. Must reference an existing preconfiguration."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if preconfigId is not None:
        query_params["preconfigId"] = preconfigId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/gms/appliance/preconfiguration",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_appliance_preconfiguration",
    description="GET /gms/appliance/preconfiguration\n\ngetPreconfigurations246\n\nRetrieve appliance preconfigurations",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_appliance_preconfiguration(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter type to return a subset of data. Use 'names' to retrieve only preconfiguration names, or 'metadata' to retrieve metadata (excludes configData). Cannot be used together with preconfigId.",
        ),
    ] = None,
    preconfigId: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique identifier of a specific preconfiguration to retrieve. Returns a single preconfiguration object when specified. Cannot be used together with filter parameter.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if preconfigId is not None:
        query_params["preconfigId"] = preconfigId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/appliance/preconfiguration",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_appliance_preconfiguration_appliance",
    description="GET /gms/appliance/preconfiguration/appliance\n\ngetApplianceInfoRelevantForPreconfiguration\n\nGet appliance info for preconfiguration matching",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_appliance_preconfiguration_appliance(
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
        "GET",
        "/gms/appliance/preconfiguration/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_appliance_preconfiguration_apply",
    description="GET /gms/appliance/preconfiguration/apply\n\ngetPreconfigurationApplyStatus254\n\nGet preconfiguration apply status",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_appliance_preconfiguration_apply(
    ctx: Context,
    preconfigId: Annotated[
        int,
        Field(
            description="Unique identifier of the preconfiguration to check status for. Must reference an existing preconfiguration."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if preconfigId is not None:
        query_params["preconfigId"] = preconfigId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/appliance/preconfiguration/apply",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_appliance_preconfiguration_default",
    description="GET /gms/appliance/preconfiguration/default\n\ngetDefaultPreconfigurations248\n\nRetrieve the default preconfiguration template",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_appliance_preconfiguration_default(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/appliance/preconfiguration/default",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_gms_appliance_preconfiguration",
    description="POST /gms/appliance/preconfiguration\n\ncreatePreconfiguration246\n\nCreate a new appliance preconfiguration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_appliance_preconfiguration(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/appliance/preconfiguration",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_appliance_preconfiguration_apply",
    description="POST /gms/appliance/preconfiguration/apply\n\napplyManagedPreconfiguration256\n\nApply preconfiguration to a managed appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_appliance_preconfiguration_apply(
    ctx: Context,
    preconfigId: Annotated[
        int,
        Field(
            description="Unique identifier of the preconfiguration to apply. Must reference an existing preconfiguration created via POST /gms/appliance/preconfiguration."
        ),
    ],
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if preconfigId is not None:
        query_params["preconfigId"] = preconfigId
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/appliance/preconfiguration/apply",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_appliance_preconfiguration_apply_discovered",
    description="POST /gms/appliance/preconfiguration/apply/discovered\n\napplyDiscoveredPreconfiguration255\n\nApply preconfiguration to a discovered appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_appliance_preconfiguration_apply_discovered(
    ctx: Context,
    preconfigId: Annotated[
        int,
        Field(
            description="Unique identifier of the preconfiguration to apply. Must reference an existing preconfiguration created via POST /gms/appliance/preconfiguration."
        ),
    ],
    discoveredId: Annotated[
        int,
        Field(
            description="Unique identifier of the discovered appliance from the discovered appliances list. This ID is temporary and changes after the appliance is approved and managed."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if preconfigId is not None:
        query_params["preconfigId"] = preconfigId
    if discoveredId is not None:
        query_params["discoveredId"] = discoveredId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/appliance/preconfiguration/apply/discovered",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_appliance_preconfiguration_find_match",
    description="POST /gms/appliance/preconfiguration/findMatch\n\ngetMatchingPreconfiguration249\n\nFind matching preconfiguration by serial or tag",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_appliance_preconfiguration_find_match(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/appliance/preconfiguration/findMatch",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_appliance_preconfiguration_validate",
    description="POST /gms/appliance/preconfiguration/validate\n\nvalidatePreconfiguration250\n\nValidate a preconfiguration without saving",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_appliance_preconfiguration_validate(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/appliance/preconfiguration/validate",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_gms_appliance_preconfiguration",
    description="PUT /gms/appliance/preconfiguration\n\nupdatePreconfiguration247\n\nUpdate an existing appliance preconfiguration",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_appliance_preconfiguration(
    ctx: Context,
    preconfigId: Annotated[
        int,
        Field(
            description="Unique identifier of the preconfiguration to update. Must reference an existing preconfiguration."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if preconfigId is not None:
        query_params["preconfigId"] = preconfigId
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gms/appliance/preconfiguration",
        query_params=query_params or None,
        body=body,
    )
