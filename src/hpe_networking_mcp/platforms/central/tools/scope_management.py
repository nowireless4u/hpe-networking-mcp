"""Aruba Central ``scope-management`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``scope-management.json`` vendor
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

# ----- device-collection-add-devices -----


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_device_collection_add_devices(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``device-collection-add-devices`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_device_collection_add_devices`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``device-collection-add-devices`` configuration in Central.

    This API will return a list of device-groups, based on the query parameters. Each device-group in the returned list includes details like - deviceCount, id, type, description, scopeId, scopeName.
    """
    return await _manage_resource(
        ctx,
        "device-collection-add-devices",
        "device-collection-add-devices",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- device-collection-create-and-add-devices -----


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_device_collection_create_and_add_devices(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``device-collection-create-and-add-devices`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_device_collection_create_and_add_devices`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``device-collection-create-and-add-devices`` configuration in Central.

    This API will return a list of device-groups, based on the query parameters. Each device-group in the returned list includes details like - deviceCount, id, type, description, scopeId, scopeName.
    """
    return await _manage_resource(
        ctx,
        "device-collection-create-and-add-devices",
        "device-collection-create-and-add-devices",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- device-collection-remove-devices -----


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_device_collection_remove_devices(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``device-collection-remove-devices`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_device_collection_remove_devices`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``device-collection-remove-devices`` configuration in Central.

    This API will return a list of device-groups, based on the query parameters. Each device-group in the returned list includes details like - deviceCount, id, type, description, scopeId, scopeName.
    """
    return await _manage_resource(
        ctx,
        "device-collection-remove-devices",
        "device-collection-remove-devices",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- device-collections -----


@tool(annotations=READ_ONLY)
async def central_get_device_collections(
    ctx: Context,
) -> dict | list | str:
    """Get the ``device-collections`` singleton configuration from Central.

    This API will return a list of device-groups, based on the query parameters. Each device-group in the returned list includes details like - deviceCount, id, type, description, scopeId, scopeName.
    """
    return await _get_resource(ctx, "device-collections", None)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_device_collections(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``device-collections`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_device_collections`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``device-collections`` configuration in Central.

    This API will return a list of device-groups, based on the query parameters. Each device-group in the returned list includes details like - deviceCount, id, type, description, scopeId, scopeName.
    """
    return await _manage_resource(
        ctx,
        "device-collections",
        "device-collections",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
