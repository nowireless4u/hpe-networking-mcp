"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/sustainability.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``sustainability``   Tag: ``ingests``   Operations: 3
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
    name="greenlake_get_sustainability_insight_ctr_v1beta1_ingests",
    description="GET /sustainability-insight-ctr/v1beta1/ingests\n\ngetIngests\n\nGet all metadata of uploaded 3rd party device measurements.",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_ingests(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from.")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of ingested records to return.")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/sustainability-insight-ctr/v1beta1/ingests",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_sustainability_insight_ctr_v1beta1_ingests_id",
    description="GET /sustainability-insight-ctr/v1beta1/ingests/{id}\n\ngetIngest\n\nGet metadata for a 3rd party device measurement.",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_ingests_id(
    ctx: Context,
    id: Annotated[str, Field(description="UUID of the record")],
) -> Any:
    path = f"/sustainability-insight-ctr/v1beta1/ingests/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_sustainability_insight_ctr_v1beta1_ingests",
    description="POST /sustainability-insight-ctr/v1beta1/ingests\n\naddIngest\n\nUpload a document with 3rd party device measurement data.",
    capability=Capability.WRITE,
)
async def greenlake_post_sustainability_insight_ctr_v1beta1_ingests(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/sustainability-insight-ctr/v1beta1/ingests",
        body=body,
    )
