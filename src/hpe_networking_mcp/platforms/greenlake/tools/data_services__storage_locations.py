"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/data-services.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``data-services``   Tag: ``storage_locations``   Operations: 1
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_data_services_v1beta1_storage_locations",
    description="GET /data-services/v1beta1/storage-locations\n\nListLocations\n\nList storage locations",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_storage_locations(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The expression to use for filtering responses.  The filter expression for this endpoint accepts the following operators on the following properties:  - `in` operator on the `capabilities` property;  For example:  - `'backup-and-recovery' in capabilities`;  Grouping of expressions to change the evaluation precedence is NOT supported.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        "/data-services/v1beta1/storage-locations",
        query_params=query_params or None,
    )
