"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs NAC IDP``
Operations in this file: 1
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_validate_org_idp_credential",
    description='POST /api/v1/orgs/{org_id}/mist_nac/test_idp\n\nvalidateOrgIdpCredential\n\nIDP Credential Validation. The output will be available through websocket. As there can be multiple commands issued against the same device at the same time and the output all goes through the same websocket stream, `session` is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n``` json\n{\n    "subscribe": "orgs/{org_id}/mist_nac/test_idp"\n}\n\n ```\n\n### Response (no idp can be found)\n\n``` json\n{\n    "event": "data",\n    "channel": "/orgs/{org_id}/mist_nac/test_idp",\n    "status": \n   ...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_validate_org_idp_credential(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/mist_nac/test_idp"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mist_nac/test_idp",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
