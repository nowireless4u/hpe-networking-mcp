"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``gmsRemoteAuth``
Operations in this file: 20
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
    name="edgeconnect_delete_gms_remote_auth_jwt",
    description="DELETE /gmsRemoteAuth/JWT\n\ngmsRemoteAuthDeleteJwtConfig\n\nDelete JWT authentication configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_gms_remote_auth_jwt(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the JWT configuration to delete. Must reference an existing configuration in the gmsConfig table."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/gmsRemoteAuth/JWT",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_gms_remote_auth_oauth",
    description="DELETE /gmsRemoteAuth/OAuth\n\ngmsRemoteAuthDeleteOneOauth377\n\nDelete an OAuth server configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_gms_remote_auth_oauth(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the OAuth server configuration to delete. Must reference an existing OAuth server."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/gmsRemoteAuth/OAuth",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_gms_remote_auth_radius",
    description="DELETE /gmsRemoteAuth/RADIUS\n\ngmsRemoteAuthDeleteRadius380\n\nDelete RADIUS server configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_gms_remote_auth_radius(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/gmsRemoteAuth/RADIUS",
        query_params=None,
    )


@tool(
    name="edgeconnect_delete_gms_remote_auth_saml",
    description="DELETE /gmsRemoteAuth/SAML\n\ngmsRemoteAuthDeleteSamlConfig385\n\nDelete a SAML server configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_gms_remote_auth_saml(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the SAML server configuration to delete. Must reference an existing SAML server."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/gmsRemoteAuth/SAML",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_gms_remote_auth_tacacs",
    description="DELETE /gmsRemoteAuth/TACACS+\n\ngmsRemoteAuthDeleteTacacs388\n\nDelete TACACS+ server configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_gms_remote_auth_tacacs(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/gmsRemoteAuth/TACACS+",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_remote_auth",
    description="GET /gmsRemoteAuth\n\ngmsRemoteAuthGetFull369\n\nGet all remote authentication server configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_remote_auth(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsRemoteAuth",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_remote_auth_jwt",
    description="GET /gmsRemoteAuth/JWT\n\ngmsRemoteAuthGetAllJWT370\n\nRetrieve JWT authentication configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_remote_auth_jwt(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique identifier for a specific JWT configuration in the gmsConfig table. If omitted, returns all JWT configurations.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsRemoteAuth/JWT",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_remote_auth_oauth",
    description="GET /gmsRemoteAuth/OAuth\n\ngmsRemoteAuthGetAllOauth375\n\nRetrieve OAuth server configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_remote_auth_oauth(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="OAuth server ID to retrieve a specific configuration. If omitted, returns all OAuth server configurations.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsRemoteAuth/OAuth",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_remote_auth_radius",
    description="GET /gmsRemoteAuth/RADIUS\n\ngmsRemoteAuthGetRadius381\n\nRetrieve RADIUS authentication server configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_remote_auth_radius(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsRemoteAuth/RADIUS",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_remote_auth_saml",
    description="GET /gmsRemoteAuth/SAML\n\ngmsRemoteAuthGetAllSamlConfig383\n\nRetrieve SAML server configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_remote_auth_saml(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="SAML server identifier. If omitted, all SAML configurations are returned. If provided, only the matching configuration is returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsRemoteAuth/SAML",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_remote_auth_tacacs",
    description="GET /gmsRemoteAuth/TACACS+\n\ngmsRemoteAuthGetTacacs389\n\nRetrieve TACACS+ remote authentication server configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_remote_auth_tacacs(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsRemoteAuth/TACACS+",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_remote_auth_type",
    description="GET /gmsRemoteAuth/type\n\ngmsRemoteAuthGetLight391\n\nGet available remote authentication types",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_remote_auth_type(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsRemoteAuth/type",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_gms_remote_auth_jwt",
    description="POST /gmsRemoteAuth/JWT\n\ngmsRemoteAuthPostJwt371\n\nCreate JWT authentication configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_remote_auth_jwt(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsRemoteAuth/JWT",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_remote_auth_oauth",
    description="POST /gmsRemoteAuth/OAuth\n\ngmsRemoteAuthPostOauth376\n\nCreate a new OAuth server configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_remote_auth_oauth(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsRemoteAuth/OAuth",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_remote_auth_radius",
    description="POST /gmsRemoteAuth/RADIUS\n\ngmsRemoteAuthPostRadius382\n\nCreate or update RADIUS authentication server configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_remote_auth_radius(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsRemoteAuth/RADIUS",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_remote_auth_saml",
    description="POST /gmsRemoteAuth/SAML\n\ngmsRemoteAuthPostSaml384\n\nCreate a new SAML server configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_remote_auth_saml(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsRemoteAuth/SAML",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_remote_auth_tacacs",
    description="POST /gmsRemoteAuth/TACACS+\n\ngmsRemoteAuthPostTacacs390\n\nCreate or update TACACS+ remote authentication server configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_remote_auth_tacacs(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsRemoteAuth/TACACS+",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_gms_remote_auth_jwt",
    description="PUT /gmsRemoteAuth/JWT\n\ngmsRemoteAuthUpdateOneJwt374\n\nUpdate JWT authentication configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_remote_auth_jwt(
    ctx: Context,
    id: Annotated[
        int, Field(description="Unique identifier of the JWT configuration to update in the gmsConfig table.")
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gmsRemoteAuth/JWT",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_gms_remote_auth_oauth",
    description="PUT /gmsRemoteAuth/OAuth\n\ngmsRemoteAuthUpdateOneOauth379\n\nUpdate an existing OAuth server configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_remote_auth_oauth(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the OAuth server configuration to update. Must reference an existing OAuth server."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gmsRemoteAuth/OAuth",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_gms_remote_auth_saml",
    description="PUT /gmsRemoteAuth/SAML\n\ngmsRemoteAuthUpdateSamlConfig387\n\nUpdate SAML server configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_remote_auth_saml(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the SAML server configuration to update. Must reference an existing SAML server."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gmsRemoteAuth/SAML",
        query_params=query_params or None,
        body=body,
    )
