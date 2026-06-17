"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``sslSubstituteCert``
Operations in this file: 2
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
    name="edgeconnect_get_ssl_substitute_certificate",
    description="GET /sslSubstituteCertificate\n\nsslSubstituteCertGet614\n\nGet SSL Substitute Certificate Configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_ssl_substitute_certificate(
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
            description="Data source selector. When 'true' or omitted, returns cached data from Orchestrator database. When 'false', fetches fresh data directly from the appliance (slower but up-to-date).",
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
        "/sslSubstituteCertificate",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_ssl_substitute_certificate_validation",
    description="POST /sslSubstituteCertificate/validation\n\nsslSubstituteCertValidation613\n\nValidate SSL Substitute Certificate",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ssl_substitute_certificate_validation(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/sslSubstituteCertificate/validation",
        query_params=None,
        body=body,
    )
