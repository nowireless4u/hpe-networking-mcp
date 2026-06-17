"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``sslCACertificate``
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
    name="edgeconnect_get_ssl_cacertificate",
    description="GET /sslCACertificate\n\nsslCACerts610\n\nGet all CA SSL certificates from an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_ssl_cacertificate(
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
            description="Controls data source: 'true' retrieves from GMS cache, 'false' fetches directly from appliance. Defaults to 'true' if not provided.",
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
        "/sslCACertificate",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_ssl_cacertificate_get_text",
    description="POST /sslCACertificate/getText\n\nsslCACertGetTextPost608\n\nGet CA certificate full text representation",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ssl_cacertificate_get_text(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/sslCACertificate/getText",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_ssl_cacertificate_validation",
    description="POST /sslCACertificate/validation\n\nsslCACertValidation609\n\nValidate SSL CA certificate",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ssl_cacertificate_validation(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/sslCACertificate/validation",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_ssl_certificate_get_info",
    description="POST /sslCertificate/getInfo\n\nsslCertGetInfoPost611\n\nParse SSL certificate and extract information",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ssl_certificate_get_info(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/sslCertificate/getInfo",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_ssl_certificate_get_text",
    description="POST /sslCertificate/getText\n\nsslCertGetTextPost612\n\nGet SSL certificate full text representation",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ssl_certificate_get_text(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/sslCertificate/getText",
        query_params=None,
        body=body,
    )
