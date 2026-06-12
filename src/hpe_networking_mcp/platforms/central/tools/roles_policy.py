"""Aruba Central ``roles-policy`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``roles-policy.json`` vendor
spec file. Wrappers
delegate to ``_get_resource`` / ``_manage_resource`` /
``_operation_request`` in ``security_policy.py`` — the same shared
helpers used by the hand-curated Roles & Policy tools.
"""

# ruff: noqa: E501

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools.security_policy import (
    _CONFIRMED_FIELD,
    _DEVICE_FUNCTION_FIELD,
    _SCOPE_ID_FIELD,
    _get_resource,
    _manage_resource,
)

# ----- object-groups -----


@tool(capability=Capability.READ)
async def central_get_object_groups(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``object-groups`` configurations from Central.

    Configure Object Groups.

    Parameters:
        name: Specific ``object-groups`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "object-groups", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_object_groups(
    ctx: Context,
    name: Annotated[str, Field(description="``object-groups`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``object-groups`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_object_groups`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``object-groups`` configuration in Central.

    Configure Object Groups.
    """
    return await _manage_resource(
        ctx,
        "object-groups",
        "object-groups",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- policies -----


@tool(capability=Capability.READ)
async def central_get_policies(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``policies`` configurations from Central.

    Configure Object Groups.

    Parameters:
        name: Specific ``policies`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "policies", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_policies(
    ctx: Context,
    name: Annotated[str, Field(description="``policies`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``policies`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_policies`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``policies`` configuration in Central.

    Configure Object Groups.
    """
    return await _manage_resource(
        ctx,
        "policies",
        "policies",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- policy-group-list -----


@tool(capability=Capability.READ)
async def central_get_policy_group_list(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``policy-group-list`` configurations from Central.

    Configure Object Groups.

    Parameters:
        name: Specific ``policy-group-list`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "policy-groups/policy-group/policy-group-list", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_policy_group_list(
    ctx: Context,
    name: Annotated[str, Field(description="``policy-group-list`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``policy-group-list`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_policy_group_list`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``policy-group-list`` configuration in Central.

    Configure Object Groups.
    """
    return await _manage_resource(
        ctx,
        "policy-groups/policy-group/policy-group-list",
        "policy-group-list",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- policy-groups -----


@tool(capability=Capability.READ)
async def central_get_policy_groups(
    ctx: Context,
) -> dict | list | str:
    """Get the ``policy-groups`` singleton configuration from Central.

    Configure Object Groups.
    """
    return await _get_resource(ctx, "policy-groups", None)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_policy_groups(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``policy-groups`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_policy_groups`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``policy-groups`` configuration in Central.

    Configure Object Groups.
    """
    return await _manage_resource(
        ctx,
        "policy-groups",
        "policy-groups",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- role-acls -----


@tool(capability=Capability.READ)
async def central_get_role_acls(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``role-acls`` configurations from Central.

    Configure Object Groups.

    Parameters:
        name: Specific ``role-acls`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "role-acls", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_role_acls(
    ctx: Context,
    name: Annotated[str, Field(description="``role-acls`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``role-acls`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_role_acls`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``role-acls`` configuration in Central.

    Configure Object Groups.
    """
    return await _manage_resource(
        ctx,
        "role-acls",
        "role-acls",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- role-gpids -----


@tool(capability=Capability.READ)
async def central_get_role_gpids(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``role-gpids`` configurations from Central.

    Configure Object Groups.

    Parameters:
        name: Specific ``role-gpids`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "role-gpids", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_role_gpids(
    ctx: Context,
    name: Annotated[str, Field(description="``role-gpids`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``role-gpids`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_role_gpids`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``role-gpids`` configuration in Central.

    Configure Object Groups.
    """
    return await _manage_resource(
        ctx,
        "role-gpids",
        "role-gpids",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- roles -----


@tool(capability=Capability.READ)
async def central_get_roles(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``roles`` configurations from Central.

    Configure Object Groups.

    Parameters:
        name: Specific ``roles`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "roles", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_roles(
    ctx: Context,
    name: Annotated[str, Field(description="``roles`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``roles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_roles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``roles`` configuration in Central.

    Configure Object Groups.
    """
    return await _manage_resource(
        ctx,
        "roles",
        "roles",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
