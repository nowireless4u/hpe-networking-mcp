"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``login``
Operations in this file: 14
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
    name="edgeconnect_get_authentication_advance_properties",
    description="GET /authentication/advanceProperties\n\nauthentication123\n\nRetrieve Orchestrator advanced configuration properties",
    capability=Capability.READ,
)
async def edgeconnect_get_authentication_advance_properties(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/authentication/advanceProperties",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_authentication_jwt",
    description="GET /authentication/jwt\n\njwtAuthentication123\n\nAuthenticate and login via JWT (JSON Web Token) SSO",
    capability=Capability.READ,
)
async def edgeconnect_get_authentication_jwt(
    ctx: Context,
    id_token: Annotated[
        str,
        Field(
            description="A signed JWT token containing user identity claims. Must include issuer (iss), audience (aud), expiration (exp), and user identifier claims matching the configured JWT settings."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id_token is not None:
        query_params["id_token"] = id_token
    return await edgeconnect_request(
        ctx,
        "GET",
        "/authentication/jwt",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_authentication_login_status",
    description="GET /authentication/loginStatus\n\nauthentication122\n\nGet the current authentication status of the HTTP session",
    capability=Capability.READ,
)
async def edgeconnect_get_authentication_login_status(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/authentication/loginStatus",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_authentication_logout",
    description="GET /authentication/logout\n\nauthentication127\n\nLogout and terminate the current HTTP session",
    capability=Capability.OPERATIONAL,
)
async def edgeconnect_get_authentication_logout(
    ctx: Context,
    comments: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional comment to log with the logout action. Use 'session-timeout' for auto-logout due to session expiration.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if comments is not None:
        query_params["comments"] = comments
    return await edgeconnect_request(
        ctx,
        "GET",
        "/authentication/logout",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_authentication_oauth_redirect",
    description="GET /authentication/oauth/redirect\n\noauthRedirect128\n\nOAuth callback endpoint for SSO authentication",
    capability=Capability.READ,
)
async def edgeconnect_get_authentication_oauth_redirect(
    ctx: Context,
    state: Annotated[
        str,
        Field(
            description="OAuth state token obtained from /authentication/oauth/stateToken endpoint. Used to validate the OAuth callback and identify the OAuth provider configuration."
        ),
    ],
    code: Annotated[
        str,
        Field(
            description="Authorization code returned by the OAuth provider after user authentication. Exchanged for access and refresh tokens."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if state is not None:
        query_params["state"] = state
    if code is not None:
        query_params["code"] = code
    return await edgeconnect_request(
        ctx,
        "GET",
        "/authentication/oauth/redirect",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_authentication_oauth_state_token",
    description="GET /authentication/oauth/stateToken\n\noauthStateToken129\n\nGenerate OAuth state token for SSO authorization flow",
    capability=Capability.READ,
)
async def edgeconnect_get_authentication_oauth_state_token(
    ctx: Context,
    oauthType: Annotated[
        int,
        Field(
            description="The numeric ID of the configured OAuth provider. Obtain from the OAuth configuration settings in Orchestrator."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if oauthType is not None:
        query_params["oauthType"] = oauthType
    return await edgeconnect_request(
        ctx,
        "GET",
        "/authentication/oauth/stateToken",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_authentication_orchestrator_randomizer",
    description="GET /authentication/orchestratorRandomizer\n\nauthentication121\n\nRetrieve the orchestrator randomizer key for client-side password encryption.",
    capability=Capability.READ,
)
async def edgeconnect_get_authentication_orchestrator_randomizer(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/authentication/orchestratorRandomizer",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_authentication_saml2_logout",
    description="GET /authentication/saml2/logout\n\nsamlLogout132\n\nProcess SAML 2.0 Single Logout (SLO) request from Identity Provider",
    capability=Capability.READ,
)
async def edgeconnect_get_authentication_saml2_logout(
    ctx: Context,
    SAMLRequest: Annotated[
        str,
        Field(
            description="Base64-encoded and DEFLATE-compressed SAML 2.0 LogoutRequest XML from the Identity Provider. Contains issuer, name ID, and session index for Single Logout (SLO)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if SAMLRequest is not None:
        query_params["SAMLRequest"] = SAMLRequest
    return await edgeconnect_request(
        ctx,
        "GET",
        "/authentication/saml2/logout",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_authentication_login",
    description="POST /authentication/login\n\nauthenticationLogin1\n\nAuthenticate user and create REST API HTTP session",
    capability=Capability.WRITE,
)
async def edgeconnect_post_authentication_login(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/authentication/login",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_authentication_login_token",
    description="POST /authentication/loginToken\n\nauthentication126\n\nRequest two-factor authentication code via email",
    capability=Capability.WRITE,
)
async def edgeconnect_post_authentication_login_token(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/authentication/loginToken",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_authentication_password_validation",
    description="POST /authentication/password/validation\n\nauthentication130\n\nValidate user credentials without creating a session",
    capability=Capability.WRITE,
)
async def edgeconnect_post_authentication_password_validation(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/authentication/password/validation",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_authentication_saml2_consume",
    description="POST /authentication/saml2/consume\n\nsamlAuthentication131\n\nSAML 2.0 SSO callback endpoint for authentication",
    capability=Capability.WRITE,
)
async def edgeconnect_post_authentication_saml2_consume(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/authentication/saml2/consume",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_authentication_user_auth_type",
    description="POST /authentication/userAuthType\n\nuserAuthType133\n\nCheck the two-factor authentication methods required for user login",
    capability=Capability.WRITE,
)
async def edgeconnect_post_authentication_user_auth_type(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/authentication/userAuthType",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_authentication_user_auth_type_token",
    description="POST /authentication/userAuthTypeToken\n\nuserAuthTypeToken134\n\nCheck user 2FA configuration using a reset password token",
    capability=Capability.WRITE,
)
async def edgeconnect_post_authentication_user_auth_type_token(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/authentication/userAuthTypeToken",
        query_params=None,
        body=body,
    )
