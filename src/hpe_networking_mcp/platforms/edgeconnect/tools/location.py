"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``location``
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
    name="edgeconnect_get_location_address_to_location",
    description="GET /location/addressToLocation\n\naddressLookup450\n\nConvert address to geographic coordinates (geocoding)",
    capability=Capability.READ,
)
async def edgeconnect_get_location_address_to_location(
    ctx: Context,
    address: Annotated[
        str,
        Field(
            description="Physical address string to geocode (street, city, postal code, country). The address is URL-encoded before being sent to the geocoding service."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if address is not None:
        query_params["address"] = address
    return await edgeconnect_request(
        ctx,
        "GET",
        "/location/addressToLocation",
        query_params=query_params or None,
    )
