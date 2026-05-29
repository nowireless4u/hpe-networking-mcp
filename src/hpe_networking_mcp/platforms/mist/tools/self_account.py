"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Self Account``
Operations in this file: 7
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
    name="mist_delete_self",
    description="DELETE /api/v1/self\n\ndeleteSelf\n\nTo delete ones account and every associated with it. The effects:\n\nthe account would be deleted\nany orphaned Org (that only has this account as admin) will be deleted\nalong with all data with Org (sites, wlans, devices) will be gone.",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_self(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/self",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_self",
    description="GET /api/v1/self\n\ngetSelf\n\nGet ‘whoami’ and privileges (which org and which sites I have access to)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_self(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/self",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_self_api_usage",
    description="GET /api/v1/self/usage\n\ngetSelfApiUsage\n\nGet the status of the API usage for the current user or API Token",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_self_api_usage(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/self/usage",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_self_login_failures",
    description="GET /api/v1/self/login_failures\n\ngetSelfLoginFailures\n\nGet a list of failed login attempts across all Orgs for the current admin",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_self_login_failures(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/self/login_failures",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_self",
    description="PUT /api/v1/self\n\nupdateSelf\n\nUpdate Account Information",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_self(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/self",
        path_params=None,
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_self_email",
    description="POST /api/v1/self/update\n\nupdateSelfEmail\n\nChange Email\nWe require the user to verify that they actually own the email address they intend to change it to.\n\nAfter the API call, the user will receive an email to the new email address with a link like https://manage.mist.com/verify/update?expire=:exp_time&email=:admin_email&token=:token\n\nUpon clicking the link, the user is provided with a login page to authenticate using existing credentials. After successful login, the email address of the user gets updated\n\n**Note**: The request parameter email can be used by UI to validate that the current...",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_self_email(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/self/update",
        path_params=None,
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_verify_self_email",
    description="GET /api/v1/self/update/verify/{token}\n\nverifySelfEmail\n\nVerify Email change",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_verify_self_email(
    ctx: Context,
    token: Annotated[str, Field(description="path parameter 'token'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/self/update/verify/{token}",
        path_params={"token": token},
        query_params=None,
        body=None,
    )
