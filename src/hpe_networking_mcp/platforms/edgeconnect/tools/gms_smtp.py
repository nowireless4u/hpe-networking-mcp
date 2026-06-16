"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``gmsSMTP``
Operations in this file: 7
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
    name="edgeconnect_get_gms_smtp",
    description="GET /gmsSMTP\n\nSMTP393\n\nGet SMTP email server configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_smtp(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsSMTP",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_smtp_unverified_emails",
    description="GET /gmsSMTP/unverifiedEmails\n\nlistUnverifiedEmails398\n\nList unverified email addresses",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_smtp_unverified_emails(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsSMTP/unverifiedEmails",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_smtp_verify_address",
    description="GET /gmsSMTP/verifyAddress\n\nverifyEmailAddress399\n\nVerify an email address using verification link",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_smtp_verify_address(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="Unique secure random string from the verification email link. This token identifies the pending email verification record."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsSMTP/verifyAddress",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_smtp",
    description="POST /gmsSMTP\n\nSMTPPost394\n\nConfigure SMTP email server settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_smtp(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsSMTP",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_smtp_del_unverified_emails",
    description="POST /gmsSMTP/delUnverifiedEmails\n\ndelUnverifiedEmails395\n\nDelete unverified email addresses",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_smtp_del_unverified_emails(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsSMTP/delUnverifiedEmails",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_smtp_send_verification_email",
    description="POST /gmsSMTP/sendVerificationEmail\n\nsendVerificationEmail396\n\nResend verification email to an unverified email address",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_smtp_send_verification_email(
    ctx: Context,
    address: Annotated[
        str,
        Field(description="Email address to send verification to. Must already exist in the unverified emails list."),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if address is not None:
        query_params["address"] = address
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsSMTP/sendVerificationEmail",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_smtp_test_email",
    description="POST /gmsSMTP/testEmail\n\nSMTPTestMail397\n\nSend test email to verify SMTP configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_smtp_test_email(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsSMTP/testEmail",
        query_params=None,
        body=body,
    )
