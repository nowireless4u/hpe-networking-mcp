"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``fileCreation``
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
    name="edgeconnect_post_file_creation_fine_uploader",
    description="POST /fileCreation/fineUploader\n\nfileCreation236\n\nUpload files to Orchestrator",
    capability=Capability.WRITE,
)
async def edgeconnect_post_file_creation_fine_uploader(
    ctx: Context,
    type: Annotated[
        str,
        Field(
            description="Upload destination type determining where the file is stored. Each type has specific file size limits and allowed extensions."
        ),
    ],
    qqfile: Annotated[
        str,
        Field(
            description="Name of the file being uploaded. Must match pattern: alphanumeric, underscore, hyphen, dot followed by allowed extensions (.csv, .jpg, .jpeg, .gif, .png, .gip, .zip, .log, .gz, .img)."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if type is not None:
        query_params["type"] = type
    if qqfile is not None:
        query_params["qqfile"] = qqfile
    return await edgeconnect_request(
        ctx,
        "POST",
        "/fileCreation/fineUploader",
        query_params=query_params or None,
        body=body,
        body_mode="multipart",
    )
