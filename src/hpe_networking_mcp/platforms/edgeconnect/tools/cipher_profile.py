"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``cipherProfile``
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
    name="edgeconnect_delete_security_cipher_profile",
    description="DELETE /security/cipherProfile\n\ndeleteCipherProfile\n\nDelete a cipher profile",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_security_cipher_profile(
    ctx: Context,
    profileId: Annotated[
        int,
        Field(
            description="Unique identifier of the cipher profile to delete. Must reference an existing, editable, and inactive profile."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if profileId is not None:
        query_params["profileId"] = profileId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/security/cipherProfile",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_security_cipher_profile",
    description="GET /security/cipherProfile\n\ngetCipherProfiles\n\nRetrieve all cipher profiles",
    capability=Capability.READ,
)
async def edgeconnect_get_security_cipher_profile(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/security/cipherProfile",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_security_cipher_profile_active_profile",
    description="GET /security/cipherProfile/activeProfile\n\nshowActiveCipherProfile\n\nRetrieve the active cipher profile",
    capability=Capability.READ,
)
async def edgeconnect_get_security_cipher_profile_active_profile(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/security/cipherProfile/activeProfile",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_security_cipher_profile_default_cipher_parameters",
    description="GET /security/cipherProfile/defaultCipherParameters\n\ngetDefaultCipherParameters\n\nRetrieve default supported cipher parameters",
    capability=Capability.READ,
)
async def edgeconnect_get_security_cipher_profile_default_cipher_parameters(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/security/cipherProfile/defaultCipherParameters",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_security_cipher_profile_activate",
    description="POST /security/cipherProfile/activate\n\nactivateCipherProfile\n\nActivate a cipher profile",
    capability=Capability.WRITE,
)
async def edgeconnect_post_security_cipher_profile_activate(
    ctx: Context,
    profileId: Annotated[
        int,
        Field(
            description="The unique identifier of the cipher profile to activate. Must reference an existing profile ID from the list of available cipher profiles."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if profileId is not None:
        query_params["profileId"] = profileId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/security/cipherProfile/activate",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_security_cipher_profile_clone",
    description="POST /security/cipherProfile/clone\n\ncloneCipherProfile\n\nClone an existing cipher profile",
    capability=Capability.WRITE,
)
async def edgeconnect_post_security_cipher_profile_clone(
    ctx: Context,
    profileId: Annotated[
        int,
        Field(description="Unique identifier of the cipher profile to clone. Must reference an existing profile ID."),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if profileId is not None:
        query_params["profileId"] = profileId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/security/cipherProfile/clone",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_security_cipher_profile_validate",
    description="POST /security/cipherProfile/validate\n\nvalidateCipherProfile\n\nValidate cipher profile against appliance certificate settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_security_cipher_profile_validate(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/security/cipherProfile/validate",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_security_cipher_profile_validate_gms",
    description="POST /security/cipherProfile/validate/gms\n\nvalidateCipherProfileForGMS\n\nValidate cipher profile against GMS certificate",
    capability=Capability.WRITE,
)
async def edgeconnect_post_security_cipher_profile_validate_gms(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/security/cipherProfile/validate/gms",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_security_cipher_profile",
    description="PUT /security/cipherProfile\n\nupdateCipherProfile\n\nUpdate an existing cipher profile",
    capability=Capability.WRITE,
)
async def edgeconnect_put_security_cipher_profile(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/security/cipherProfile",
        query_params=None,
        body=body,
    )
