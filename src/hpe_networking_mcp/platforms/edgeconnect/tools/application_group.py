"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``applicationGroup``
Operations in this file: 5
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
    name="edgeconnect_get_application",
    description="GET /application\n\napplicationGet85\n\nGet all built-in and user-defined applications",
    capability=Capability.READ,
)
async def edgeconnect_get_application(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/application",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_application_builtin",
    description="GET /application/builtin\n\ngetBuiltInApplications\n\nList all built-in application signatures",
    capability=Capability.READ,
)
async def edgeconnect_get_application_builtin(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/application/builtin",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_application_groups",
    description="GET /applicationGroups\n\ngetUserAppGroups\n\nGet application groups from appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_application_groups(
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
            description="Data source selector. When 'true' (default), retrieves from Orchestrator cache. When 'false', fetches real-time data directly from appliance.",
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
        "/applicationGroups",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_application_user_defined",
    description="GET /application/userDefined\n\ngetUserDefinedApplications\n\nList all user-defined custom applications",
    capability=Capability.READ,
)
async def edgeconnect_get_application_user_defined(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/application/userDefined",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_application_user_defined_config",
    description="GET /application/userDefinedConfig\n\ngetUserDefinedConfig\n\nGet user-defined application rules from appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_application_user_defined_config(
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
            description="Data source selector. When true (default), retrieves from Orchestrator cache for faster response. When false, fetches real-time data directly from the appliance.",
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
        "/application/userDefinedConfig",
        query_params=query_params or None,
    )
