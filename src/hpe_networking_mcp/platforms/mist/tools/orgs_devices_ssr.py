"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Devices - SSR``
Operations in this file: 3
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
    name="mist_export_org_ssr_id_tokens",
    description="POST /api/v1/orgs/{org_id}/ssr/export_idtokens\n\nexportOrgSsrIdTokens\n\nExport IDTokens from Mist to import into Conductor to securely allow SSR devices during onboarding",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_export_org_ssr_id_tokens(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/ssr/export_idtokens",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_get_org128_t_registration_commands",
    description="GET /api/v1/orgs/{org_id}/128routers/register_cmd\n\ngetOrg128TRegistrationCommands\n\n128T devices can be managed/adopted by Mist.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org128_t_registration_commands(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ttl: Annotated[
        int | None, Field(description="Token validity duration in seconds. Defaults to 1 year (31536000 seconds)")
    ] = None,
    asset_ids: Annotated[
        Any | None,
        Field(
            description="When specified restricts registration to listed assets only. Prefer HTTP body over headers for this parameter, especially with long lists to avoid header size limits."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/128routers/register_cmd",
        path_params={"org_id": org_id},
        query_params={"ttl": ttl, "asset_ids": asset_ids},
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_ssr_registration_commands",
    description="GET /api/v1/orgs/{org_id}/ssr/register_cmd\n\ngetOrgSsrRegistrationCommands\n\nSSR devices can be managed/adopted by Mist.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_ssr_registration_commands(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ttl: Annotated[
        int | None, Field(description="Token validity duration in seconds. Defaults to 1 year (31536000 seconds)")
    ] = None,
    asset_ids: Annotated[
        Any | None,
        Field(
            description="When specified restricts registration to listed assets only. Prefer HTTP body over headers for this parameter, especially with long lists to avoid header size limits."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ssr/register_cmd",
        path_params={"org_id": org_id},
        query_params={"ttl": ttl, "asset_ids": asset_ids},
        body=None,
    )
