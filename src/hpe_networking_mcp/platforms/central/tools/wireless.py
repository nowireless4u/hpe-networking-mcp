"""Aruba Central ``wireless`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``wireless.json`` vendor
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

# ----- alg -----


@tool(capability=Capability.READ)
async def central_get_alg(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``alg`` configurations from Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.

    Parameters:
        name: Specific ``alg`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "alg", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_alg(
    ctx: Context,
    name: Annotated[str, Field(description="``alg`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``alg`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_alg`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``alg`` configuration in Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.
    """
    return await _manage_resource(
        ctx,
        "alg",
        "alg",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ids -----


@tool(capability=Capability.READ)
async def central_get_ids(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ids`` configurations from Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.

    Parameters:
        name: Specific ``ids`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ids", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_ids(
    ctx: Context,
    name: Annotated[str, Field(description="``ids`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ids`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ids`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ids`` configuration in Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.
    """
    return await _manage_resource(
        ctx,
        "ids",
        "ids",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mesh -----


@tool(capability=Capability.READ)
async def central_get_mesh(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mesh`` configurations from Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.

    Parameters:
        name: Specific ``mesh`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mesh", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_mesh(
    ctx: Context,
    name: Annotated[str, Field(description="``mesh`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mesh`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mesh`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mesh`` configuration in Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.
    """
    return await _manage_resource(
        ctx,
        "mesh",
        "mesh",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mpsk-local -----


@tool(capability=Capability.READ)
async def central_get_mpsk_local(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mpsk-local`` configurations from Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.

    Parameters:
        name: Specific ``mpsk-local`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mpsk-local", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_mpsk_local(
    ctx: Context,
    name: Annotated[str, Field(description="``mpsk-local`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mpsk-local`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mpsk_local`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mpsk-local`` configuration in Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.
    """
    return await _manage_resource(
        ctx,
        "mpsk-local",
        "mpsk-local",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- passpoint -----


@tool(capability=Capability.READ)
async def central_get_passpoint(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``passpoint`` configurations from Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.

    Parameters:
        name: Specific ``passpoint`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "passpoint", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_passpoint(
    ctx: Context,
    name: Annotated[str, Field(description="``passpoint`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``passpoint`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_passpoint`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``passpoint`` configuration in Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.
    """
    return await _manage_resource(
        ctx,
        "passpoint",
        "passpoint",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- radio -----


@tool(capability=Capability.READ)
async def central_get_radio(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``radio`` configurations from Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.

    Parameters:
        name: Specific ``radio`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "radios", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_radio(
    ctx: Context,
    name: Annotated[str, Field(description="``radio`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``radio`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_radio`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``radio`` configuration in Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.
    """
    return await _manage_resource(
        ctx,
        "radios",
        "radio",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
