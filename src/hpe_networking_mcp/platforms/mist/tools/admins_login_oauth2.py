"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Admins Login - OAuth2``
Operations in this file: 3
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_get_oauth2_authorization_url_for_login",
    description="GET /api/v1/login/oauth/{provider}\n\ngetOauth2AuthorizationUrlForLogin\n\nReturn the provider authorization URL used to start an OAuth2 login or account-linking flow. When `forward` is provided, the provider redirects back to that callback URL after authorization.",
    capability=Capability.READ,
)
async def mist_get_oauth2_authorization_url_for_login(
    ctx: Context,
    provider: Annotated[str, Field(description="path parameter 'provider'")],
    forward: Annotated[str | None, Field(description="Callback URL used after completing the OAuth login flow")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/login/oauth/{provider}",
        path_params={"provider": provider},
        query_params={"forward": forward},
        body=None,
    )


@_mcp_tool(
    name="mist_login_oauth2",
    description="POST /api/v1/login/oauth/{provider}\n\nloginOauth2\n\nComplete an OAuth2 login by exchanging the provider authorization code for a Mist administrator session.",
    capability=Capability.WRITE,
)
async def mist_login_oauth2(
    ctx: Context,
    provider: Annotated[str, Field(description="path parameter 'provider'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/login/oauth/{provider}",
        path_params={"provider": provider},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_unlink_oauth2_provider",
    description="DELETE /api/v1/login/oauth/{provider}\n\nunlinkOauth2Provider\n\nUnlink the specified OAuth2 provider from the authenticated administrator account so it can no longer be used for that account's OAuth login.",
    capability=Capability.WRITE_DELETE,
)
async def mist_unlink_oauth2_provider(
    ctx: Context,
    provider: Annotated[str, Field(description="path parameter 'provider'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/login/oauth/{provider}",
        path_params={"provider": provider},
        query_params=None,
        body=None,
    )
