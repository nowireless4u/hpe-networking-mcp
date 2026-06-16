"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``gmsHttpsUpload``
Operations in this file: 2
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
    name="edgeconnect_post_gms_https_certificate",
    description="POST /gms/httpsCertificate\n\nuploadHttpsCertificate\n\nUpload SSL Certificate and Private Key",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_https_certificate(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/httpsCertificate",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_https_certificate_validation",
    description="POST /gms/httpsCertificate/validation\n\nvalidateHttpsCertificate\n\nValidate SSL Certificate and Private Key",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_https_certificate_validation(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/httpsCertificate/validation",
        query_params=None,
        body=body,
    )
