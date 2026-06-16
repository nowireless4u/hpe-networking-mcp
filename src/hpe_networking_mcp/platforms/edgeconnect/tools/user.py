"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``user``
Operations in this file: 9
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
    name="edgeconnect_delete_users",
    description="DELETE /users\n\ndeleteUser\n\nDelete a user account",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_users(
    ctx: Context,
    userId: Annotated[
        str,
        Field(
            description="The unique primary key identifier (userPk) of the user to delete. Must be provided along with userName."
        ),
    ],
    userName: Annotated[
        str,
        Field(
            description="The username of the user to delete. Used for logging and deleting related records. Must match the userId."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if userId is not None:
        query_params["userId"] = userId
    if userName is not None:
        query_params["userName"] = userName
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/users",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_users",
    description="GET /users\n\ngetUsers\n\nRetrieve user accounts",
    capability=Capability.READ,
)
async def edgeconnect_get_users(
    ctx: Context,
    userId: Annotated[
        str | None,
        Field(
            default=None,
            description="Username to filter by. If omitted, returns all users. If provided, returns a single-element array with the matching user.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if userId is not None:
        query_params["userId"] = userId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/users",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_users_new_tfa_key",
    description="GET /users/newTfaKey\n\ngenerateNewUserKey\n\nGenerate new TOTP two-factor authentication key",
    capability=Capability.READ,
)
async def edgeconnect_get_users_new_tfa_key(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/users/newTfaKey",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_users_notify_password_expiry",
    description="GET /users/notifyPasswordExpiry\n\ngetNotifyPasswordExpiry\n\nGet password expiry notification status",
    capability=Capability.READ,
)
async def edgeconnect_get_users_notify_password_expiry(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/users/notifyPasswordExpiry",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_users_validate_commonwords",
    description="GET /users/validateCommonwords\n\nvalidateCommonWords\n\nValidate password against common words list",
    capability=Capability.READ,
)
async def edgeconnect_get_users_validate_commonwords(
    ctx: Context,
    userPassword: Annotated[
        str,
        Field(
            description="The password string to validate against the common words list. Comparison is case-insensitive (converted to lowercase before checking)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if userPassword is not None:
        query_params["userPassword"] = userPassword
    return await edgeconnect_request(
        ctx,
        "GET",
        "/users/validateCommonwords",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_users",
    description="POST /users\n\naddModifyUser\n\nCreate or update a user account",
    capability=Capability.WRITE,
)
async def edgeconnect_post_users(
    ctx: Context,
    newUser: Annotated[
        bool, Field(description="Set to true to create a new user, false to update existing user. Required parameter.")
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if newUser is not None:
        query_params["newUser"] = newUser
    return await edgeconnect_request(
        ctx,
        "POST",
        "/users",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_users_forgot_password",
    description="POST /users/forgotPassword\n\nforgotPassword\n\nInitiate password reset",
    capability=Capability.WRITE,
)
async def edgeconnect_post_users_forgot_password(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/users/forgotPassword",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_users_password",
    description="POST /users/password\n\nsetAdminPassword\n\nChange user password",
    capability=Capability.WRITE,
)
async def edgeconnect_post_users_password(
    ctx: Context,
    username: Annotated[
        str,
        Field(
            description="The username of the account whose password is being changed. Must match an existing user in the system."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if username is not None:
        query_params["username"] = username
    return await edgeconnect_request(
        ctx,
        "POST",
        "/users/password",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_users_reset_password",
    description="POST /users/resetPassword\n\nresetPassword\n\nReset user password",
    capability=Capability.WRITE,
)
async def edgeconnect_post_users_reset_password(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/users/resetPassword",
        query_params=None,
        body=body,
    )
