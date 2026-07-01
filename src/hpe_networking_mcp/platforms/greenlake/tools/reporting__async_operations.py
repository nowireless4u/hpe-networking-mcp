"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/reporting.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``reporting``   Tag: ``async_operations``   Operations: 1
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_reporting_v1_async_operations_id",
    description="GET /reporting/v1/async-operations/{id}\n\nAsynchronous operation details",
    capability=Capability.READ,
)
async def greenlake_get_reporting_v1_async_operations_id(
    ctx: Context,
    id: Annotated[str, Field(description="The unique identifier returned by an asynchronous API call.")],
) -> Any:
    path = f"/reporting/v1/async-operations/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
