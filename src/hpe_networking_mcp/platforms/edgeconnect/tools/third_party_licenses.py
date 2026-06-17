"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``thirdPartyLicenses``
Operations in this file: 1
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_third_party_licenses",
    description="GET /thirdPartyLicenses\n\ngetThirdPartyLicenses\n\nRetrieve third-party license information",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_licenses(
    ctx: Context,
    action: Annotated[
        str | None,
        Field(
            default=None,
            description="Specifies the response behavior. Use 'download' to receive the response as a downloadable file attachment.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if action is not None:
        query_params["action"] = action
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyLicenses",
        query_params=query_params or None,
    )
