"""Aruba Central ``Central NAC`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``Central NAC`` OpenAPI tag-group. Wrappers
delegate to ``_get_resource`` / ``_manage_resource`` in
``security_policy.py`` — the same shared helpers used by the
hand-curated Roles & Policy tools.
"""

# ruff: noqa: E501

from typing import Annotated

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.tools.security_policy import (
    _CONFIRMED_FIELD,
    _DEVICE_FUNCTION_FIELD,
    _SCOPE_ID_FIELD,
    _get_resource,
    _manage_resource,
)

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)

# ----- cda-airpass-approval -----


@tool(annotations=READ_ONLY)
async def central_get_cda_airpass_approval(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``cda-airpass-approval`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        name: Specific ``cda-airpass-approval`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "airpass-approval", name)


# ----- cda-auth-profile -----


@tool(annotations=READ_ONLY)
async def central_get_cda_auth_profile(
    ctx: Context,
    auth_profile_id: str | None = None,
) -> dict | list | str:
    """Get ``cda-auth-profile`` configurations from Central.

    Authentication profiles to be used for Central NAC. Authentication profile defines the authentication method, authentication sources, and additional attributes used to authenticate users on the associated networks. Authentication profiles must be configured with default query parameters.

    Parameters:
        auth_profile_id: Specific ``cda-auth-profile`` identifier (OpenAPI path param: ``auth-profile-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "auth-profiles", auth_profile_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cda_auth_profile(
    ctx: Context,
    auth_profile_id: Annotated[
        str, Field(description="``cda-auth-profile`` identifier (OpenAPI path param: ``auth-profile-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cda-auth-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cda_auth_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cda-auth-profile`` configuration in Central.

    Authentication profiles to be used for Central NAC. Authentication profile defines the authentication method, authentication sources, and additional attributes used to authenticate users on the associated networks. Authentication profiles must be configured with default query parameters.
    """
    return await _manage_resource(
        ctx,
        "auth-profiles",
        "cda-auth-profile",
        auth_profile_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cda-authz-policy -----


@tool(annotations=READ_ONLY)
async def central_get_cda_authz_policy(
    ctx: Context,
    policy_id: str | None = None,
) -> dict | list | str:
    """Get ``cda-authz-policy`` configurations from Central.

    Authorization policies to be used for Central NAC. Authorization policy defines authorization sources and rules that determine the enforcement profile that is assigned to user or device upon authorization. Authorization policies must be configured with default query parameters.

    Parameters:
        policy_id: Specific ``cda-authz-policy`` identifier (OpenAPI path param: ``policy-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "authz-policies", policy_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cda_authz_policy(
    ctx: Context,
    policy_id: Annotated[
        str, Field(description="``cda-authz-policy`` identifier (OpenAPI path param: ``policy-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cda-authz-policy`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cda_authz_policy`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cda-authz-policy`` configuration in Central.

    Authorization policies to be used for Central NAC. Authorization policy defines authorization sources and rules that determine the enforcement profile that is assigned to user or device upon authorization. Authorization policies must be configured with default query parameters.
    """
    return await _manage_resource(
        ctx,
        "authz-policies",
        "cda-authz-policy",
        policy_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cda-identity-store -----


@tool(annotations=READ_ONLY)
async def central_get_cda_identity_store(
    ctx: Context,
    id: str | None = None,
) -> dict | list | str:
    """Get ``cda-identity-store`` configurations from Central.

    Identity stores to be used for Central NAC. These stores can be configured for Identity providers like Azure, Microsoft, Okta and local user or MAC based stores. They can be referenced in authentication profiles and authorization policies and used for authentication and authorization. Identity stores must be configured with default query parameters.

    Parameters:
        id: Specific ``cda-identity-store`` identifier (OpenAPI path param: ``id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "identity-stores", id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cda_identity_store(
    ctx: Context,
    id: Annotated[str, Field(description="``cda-identity-store`` identifier (OpenAPI path param: ``id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cda-identity-store`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cda_identity_store`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cda-identity-store`` configuration in Central.

    Identity stores to be used for Central NAC. These stores can be configured for Identity providers like Azure, Microsoft, Okta and local user or MAC based stores. They can be referenced in authentication profiles and authorization policies and used for authentication and authorization. Identity stores must be configured with default query parameters.
    """
    return await _manage_resource(
        ctx,
        "identity-stores",
        "cda-identity-store",
        id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cda-message-provider -----


@tool(annotations=READ_ONLY)
async def central_get_cda_message_provider(
    ctx: Context,
    provider_id: str | None = None,
) -> dict | list | str:
    """Get ``cda-message-provider`` configurations from Central.

    A list of messaging service providers (e.g Twilio for SMS) to use with Central NAC. At most, one SMS messaging service provider is allowed.

    Parameters:
        provider_id: Specific ``cda-message-provider`` identifier (OpenAPI path param: ``provider-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "message-providers", provider_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cda_message_provider(
    ctx: Context,
    provider_id: Annotated[
        str, Field(description="``cda-message-provider`` identifier (OpenAPI path param: ``provider-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cda-message-provider`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cda_message_provider`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cda-message-provider`` configuration in Central.

    A list of messaging service providers (e.g Twilio for SMS) to use with Central NAC. At most, one SMS messaging service provider is allowed.
    """
    return await _manage_resource(
        ctx,
        "message-providers",
        "cda-message-provider",
        provider_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cda-portal-custom-message -----


@tool(annotations=READ_ONLY)
async def central_get_cda_portal_custom_message(
    ctx: Context,
    message_id: str | None = None,
) -> dict | list | str:
    """Get ``cda-portal-custom-message`` configurations from Central.

    A list of custom messages that can be used with Central NAC portal profiles and visitor management facilities to provide customized email and SMS messages for Central NAC visitors.

    Parameters:
        message_id: Specific ``cda-portal-custom-message`` identifier (OpenAPI path param: ``message-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "custom-messages", message_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cda_portal_custom_message(
    ctx: Context,
    message_id: Annotated[
        str, Field(description="``cda-portal-custom-message`` identifier (OpenAPI path param: ``message-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cda-portal-custom-message`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cda_portal_custom_message`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cda-portal-custom-message`` configuration in Central.

    A list of custom messages that can be used with Central NAC portal profiles and visitor management facilities to provide customized email and SMS messages for Central NAC visitors.
    """
    return await _manage_resource(
        ctx,
        "custom-messages",
        "cda-portal-custom-message",
        message_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cda-portal-default-custom-message -----


@tool(annotations=READ_ONLY)
async def central_get_cda_portal_default_custom_message(
    ctx: Context,
    message_id: str | None = None,
) -> dict | list | str:
    """Get ``cda-portal-default-custom-message`` configurations from Central.

    Default custom message assignments. Only one custom message of each type and purpose combination can be assigned as a default. For example, there can only be one EMAIL PASSWORD_NOTICE, and one SMS PASSWORD_NOTICE, assigned default message.

    Parameters:
        message_id: Specific ``cda-portal-default-custom-message`` identifier (OpenAPI path param: ``message-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "default-custom-messages", message_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cda_portal_default_custom_message(
    ctx: Context,
    message_id: Annotated[
        str, Field(description="``cda-portal-default-custom-message`` identifier (OpenAPI path param: ``message-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cda-portal-default-custom-message`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cda_portal_default_custom_message`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cda-portal-default-custom-message`` configuration in Central.

    Default custom message assignments. Only one custom message of each type and purpose combination can be assigned as a default. For example, there can only be one EMAIL PASSWORD_NOTICE, and one SMS PASSWORD_NOTICE, assigned default message.
    """
    return await _manage_resource(
        ctx,
        "default-custom-messages",
        "cda-portal-default-custom-message",
        message_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cda-portal-overrides-profile -----


@tool(annotations=READ_ONLY)
async def central_get_cda_portal_overrides_profile(
    ctx: Context,
    override_id: str | None = None,
) -> dict | list | str:
    """Get ``cda-portal-overrides-profile`` configurations from Central.

    A list of portal overrides that contain multilingual text overrides to be applied to Central NAC portals (e.g. MPSK provisioning, or captive portals).

    Parameters:
        override_id: Specific ``cda-portal-overrides-profile`` identifier (OpenAPI path param: ``override-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "overrides", override_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cda_portal_overrides_profile(
    ctx: Context,
    override_id: Annotated[
        str, Field(description="``cda-portal-overrides-profile`` identifier (OpenAPI path param: ``override-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cda-portal-overrides-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cda_portal_overrides_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cda-portal-overrides-profile`` configuration in Central.

    A list of portal overrides that contain multilingual text overrides to be applied to Central NAC portals (e.g. MPSK provisioning, or captive portals).
    """
    return await _manage_resource(
        ctx,
        "overrides",
        "cda-portal-overrides-profile",
        override_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cda-portal-profile -----


@tool(annotations=READ_ONLY)
async def central_get_cda_portal_profile(
    ctx: Context,
    portal_id: str | None = None,
) -> dict | list | str:
    """Get ``cda-portal-profile`` configurations from Central.

    A list of portal profiles that contain customizations to be applied to Central NAC portals (e.g. MPSK provisioning, or captive portals).

    Parameters:
        portal_id: Specific ``cda-portal-profile`` identifier (OpenAPI path param: ``portal-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "portals", portal_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cda_portal_profile(
    ctx: Context,
    portal_id: Annotated[
        str, Field(description="``cda-portal-profile`` identifier (OpenAPI path param: ``portal-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cda-portal-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cda_portal_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cda-portal-profile`` configuration in Central.

    A list of portal profiles that contain customizations to be applied to Central NAC portals (e.g. MPSK provisioning, or captive portals).
    """
    return await _manage_resource(
        ctx,
        "portals",
        "cda-portal-profile",
        portal_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cda-portal-skin-profile -----


@tool(annotations=READ_ONLY)
async def central_get_cda_portal_skin_profile(
    ctx: Context,
    skin_id: str | None = None,
) -> dict | list | str:
    """Get ``cda-portal-skin-profile`` configurations from Central.

    A list of portal skins that contain page-level layout and presentation customizations to be applied to Central NAC portals (e.g. MPSK provisioning, or captive portals).

    Parameters:
        skin_id: Specific ``cda-portal-skin-profile`` identifier (OpenAPI path param: ``skin-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "skins", skin_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cda_portal_skin_profile(
    ctx: Context,
    skin_id: Annotated[
        str, Field(description="``cda-portal-skin-profile`` identifier (OpenAPI path param: ``skin-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cda-portal-skin-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cda_portal_skin_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cda-portal-skin-profile`` configuration in Central.

    A list of portal skins that contain page-level layout and presentation customizations to be applied to Central NAC portals (e.g. MPSK provisioning, or captive portals).
    """
    return await _manage_resource(
        ctx,
        "skins",
        "cda-portal-skin-profile",
        skin_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cda-static-tag -----


@tool(annotations=READ_ONLY)
async def central_get_cda_static_tag(
    ctx: Context,
    tag_id: str | None = None,
) -> dict | list | str:
    """Get ``cda-static-tag`` configurations from Central.

    Static Tags can be used to build policies that apply to specific devices.

    Parameters:
        tag_id: Specific ``cda-static-tag`` identifier (OpenAPI path param: ``tag-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "static-tag", tag_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cda_static_tag(
    ctx: Context,
    tag_id: Annotated[str, Field(description="``cda-static-tag`` identifier (OpenAPI path param: ``tag-id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cda-static-tag`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cda_static_tag`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cda-static-tag`` configuration in Central.

    Static Tags can be used to build policies that apply to specific devices.
    """
    return await _manage_resource(
        ctx,
        "static-tag",
        "cda-static-tag",
        tag_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
