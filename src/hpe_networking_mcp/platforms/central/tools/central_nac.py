"""Aruba Central ``central-nac`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``central-nac.json`` vendor
spec file. Wrappers
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

# ----- airpass-approval -----


@tool(annotations=READ_ONLY)
async def central_get_airpass_approval(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``airpass-approval`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        name: Specific ``airpass-approval`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "airpass-approval", name)


# ----- auth-profiles -----


@tool(annotations=READ_ONLY)
async def central_get_auth_profiles(
    ctx: Context,
    auth_profile_id: str | None = None,
) -> dict | list | str:
    """Get ``auth-profiles`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        auth_profile_id: Specific ``auth-profiles`` identifier (OpenAPI path param: ``auth-profile-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "auth-profiles", auth_profile_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_auth_profiles(
    ctx: Context,
    auth_profile_id: Annotated[
        str, Field(description="``auth-profiles`` identifier (OpenAPI path param: ``auth-profile-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``auth-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_auth_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``auth-profiles`` configuration in Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.
    """
    return await _manage_resource(
        ctx,
        "auth-profiles",
        "auth-profiles",
        auth_profile_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- authz-policies -----


@tool(annotations=READ_ONLY)
async def central_get_authz_policies(
    ctx: Context,
    policy_id: str | None = None,
) -> dict | list | str:
    """Get ``authz-policies`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        policy_id: Specific ``authz-policies`` identifier (OpenAPI path param: ``policy-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "authz-policies", policy_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_authz_policies(
    ctx: Context,
    policy_id: Annotated[str, Field(description="``authz-policies`` identifier (OpenAPI path param: ``policy-id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``authz-policies`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_authz_policies`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``authz-policies`` configuration in Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.
    """
    return await _manage_resource(
        ctx,
        "authz-policies",
        "authz-policies",
        policy_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- custom-messages -----


@tool(annotations=READ_ONLY)
async def central_get_custom_messages(
    ctx: Context,
    message_id: str | None = None,
) -> dict | list | str:
    """Get ``custom-messages`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        message_id: Specific ``custom-messages`` identifier (OpenAPI path param: ``message-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "custom-messages", message_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_custom_messages(
    ctx: Context,
    message_id: Annotated[
        str, Field(description="``custom-messages`` identifier (OpenAPI path param: ``message-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``custom-messages`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_custom_messages`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``custom-messages`` configuration in Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.
    """
    return await _manage_resource(
        ctx,
        "custom-messages",
        "custom-messages",
        message_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- default-custom-messages -----


@tool(annotations=READ_ONLY)
async def central_get_default_custom_messages(
    ctx: Context,
    message_id: str | None = None,
) -> dict | list | str:
    """Get ``default-custom-messages`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        message_id: Specific ``default-custom-messages`` identifier (OpenAPI path param: ``message-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "default-custom-messages", message_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_default_custom_messages(
    ctx: Context,
    message_id: Annotated[
        str, Field(description="``default-custom-messages`` identifier (OpenAPI path param: ``message-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``default-custom-messages`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_default_custom_messages`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``default-custom-messages`` configuration in Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.
    """
    return await _manage_resource(
        ctx,
        "default-custom-messages",
        "default-custom-messages",
        message_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- identity-stores -----


@tool(annotations=READ_ONLY)
async def central_get_identity_stores(
    ctx: Context,
    id: str | None = None,
) -> dict | list | str:
    """Get ``identity-stores`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        id: Specific ``identity-stores`` identifier (OpenAPI path param: ``id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "identity-stores", id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_identity_stores(
    ctx: Context,
    id: Annotated[str, Field(description="``identity-stores`` identifier (OpenAPI path param: ``id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``identity-stores`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_identity_stores`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``identity-stores`` configuration in Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.
    """
    return await _manage_resource(
        ctx,
        "identity-stores",
        "identity-stores",
        id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- message-providers -----


@tool(annotations=READ_ONLY)
async def central_get_message_providers(
    ctx: Context,
    provider_id: str | None = None,
) -> dict | list | str:
    """Get ``message-providers`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        provider_id: Specific ``message-providers`` identifier (OpenAPI path param: ``provider-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "message-providers", provider_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_message_providers(
    ctx: Context,
    provider_id: Annotated[
        str, Field(description="``message-providers`` identifier (OpenAPI path param: ``provider-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``message-providers`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_message_providers`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``message-providers`` configuration in Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.
    """
    return await _manage_resource(
        ctx,
        "message-providers",
        "message-providers",
        provider_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- overrides -----


@tool(annotations=READ_ONLY)
async def central_get_overrides(
    ctx: Context,
    override_id: str | None = None,
) -> dict | list | str:
    """Get ``overrides`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        override_id: Specific ``overrides`` identifier (OpenAPI path param: ``override-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "overrides", override_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_overrides(
    ctx: Context,
    override_id: Annotated[str, Field(description="``overrides`` identifier (OpenAPI path param: ``override-id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``overrides`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_overrides`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``overrides`` configuration in Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.
    """
    return await _manage_resource(
        ctx,
        "overrides",
        "overrides",
        override_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- portals -----


@tool(annotations=READ_ONLY)
async def central_get_portals(
    ctx: Context,
    portal_id: str | None = None,
) -> dict | list | str:
    """Get ``portals`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        portal_id: Specific ``portals`` identifier (OpenAPI path param: ``portal-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "portals", portal_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_portals(
    ctx: Context,
    portal_id: Annotated[str, Field(description="``portals`` identifier (OpenAPI path param: ``portal-id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``portals`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_portals`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``portals`` configuration in Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.
    """
    return await _manage_resource(
        ctx,
        "portals",
        "portals",
        portal_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- skins -----


@tool(annotations=READ_ONLY)
async def central_get_skins(
    ctx: Context,
    skin_id: str | None = None,
) -> dict | list | str:
    """Get ``skins`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        skin_id: Specific ``skins`` identifier (OpenAPI path param: ``skin-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "skins", skin_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_skins(
    ctx: Context,
    skin_id: Annotated[str, Field(description="``skins`` identifier (OpenAPI path param: ``skin-id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``skins`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_skins`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``skins`` configuration in Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.
    """
    return await _manage_resource(
        ctx,
        "skins",
        "skins",
        skin_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- static-tag -----


@tool(annotations=READ_ONLY)
async def central_get_static_tag(
    ctx: Context,
    tag_id: str | None = None,
) -> dict | list | str:
    """Get ``static-tag`` configurations from Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.

    Parameters:
        tag_id: Specific ``static-tag`` identifier (OpenAPI path param: ``tag-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "static-tag", tag_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_static_tag(
    ctx: Context,
    tag_id: Annotated[str, Field(description="``static-tag`` identifier (OpenAPI path param: ``tag-id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``static-tag`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_static_tag`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``static-tag`` configuration in Central.

    Air Pass enables seamless cellular roaming to enterprise networks. Air Pass approval defines site based approval requests for MNOs with the approval status. This is a read-only configuration.
    """
    return await _manage_resource(
        ctx,
        "static-tag",
        "static-tag",
        tag_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
