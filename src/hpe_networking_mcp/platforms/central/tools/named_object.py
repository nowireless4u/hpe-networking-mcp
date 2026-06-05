"""Aruba Central ``named-object`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``named-object.json`` vendor
spec file. Wrappers
delegate to ``_get_resource`` / ``_manage_resource`` /
``_operation_request`` in ``security_policy.py`` — the same shared
helpers used by the hand-curated Roles & Policy tools.
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

# ----- aliases -----


@tool(annotations=READ_ONLY)
async def central_get_aliases(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``aliases`` configurations from Central.

    Top level container for Aliases.

    Parameters:
        name: Specific ``aliases`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "aliases", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_aliases(
    ctx: Context,
    name: Annotated[str, Field(description="``aliases`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``aliases`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_aliases`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``aliases`` configuration in Central.

    Top level container for Aliases.
    """
    return await _manage_resource(
        ctx,
        "aliases",
        "aliases",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- named-conditions -----


@tool(annotations=READ_ONLY)
async def central_get_named_conditions(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``named-conditions`` configurations from Central.

    Top level container for Aliases.

    Parameters:
        name: Specific ``named-conditions`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "named-conditions", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_named_conditions(
    ctx: Context,
    name: Annotated[str, Field(description="``named-conditions`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``named-conditions`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_named_conditions`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``named-conditions`` configuration in Central.

    Top level container for Aliases.
    """
    return await _manage_resource(
        ctx,
        "named-conditions",
        "named-conditions",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- net-services -----


@tool(annotations=READ_ONLY)
async def central_get_net_services(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``net-services`` configurations from Central.

    Top level container for Aliases.

    Parameters:
        name: Specific ``net-services`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "net-services", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_net_services(
    ctx: Context,
    name: Annotated[str, Field(description="``net-services`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``net-services`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_net_services`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``net-services`` configuration in Central.

    Top level container for Aliases.
    """
    return await _manage_resource(
        ctx,
        "net-services",
        "net-services",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
