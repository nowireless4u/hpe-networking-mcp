"""Aruba Central ``Config Management`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``Config Management`` OpenAPI tag-group. Wrappers
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

# ----- config-checkpoint -----


@tool(annotations=READ_ONLY)
async def central_get_config_checkpoint(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``config-checkpoint`` configurations from Central.

    Contains configuration elements for configuration checkpoints.

    Parameters:
        name: Specific ``config-checkpoint`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "config-checkpoint", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_config_checkpoint(
    ctx: Context,
    name: Annotated[str, Field(description="``config-checkpoint`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``config-checkpoint`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_config_checkpoint`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``config-checkpoint`` configuration in Central.

    Contains configuration elements for configuration checkpoints.
    """
    return await _manage_resource(
        ctx,
        "config-checkpoint",
        "config-checkpoint",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- persona-assignment -----


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_persona_assignment(
    ctx: Context,
    target_device_function: Annotated[
        str, Field(description="``persona-assignment`` identifier (OpenAPI path param: ``device-function``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``persona-assignment`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_persona_assignment`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``persona-assignment`` configuration in Central.

    Device list to device function mapping.
    """
    return await _manage_resource(
        ctx,
        "persona-assignment",
        "persona-assignment",
        target_device_function,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- persona-mapping -----


@tool(annotations=READ_ONLY)
async def central_get_persona_mapping(
    ctx: Context,
    device_type: str | None = None,
) -> dict | list | str:
    """Get ``persona-mapping`` configurations from Central.

    Device type to device function mapping.

    Parameters:
        device_type: Specific ``persona-mapping`` identifier (OpenAPI path param: ``device-type``). If omitted, returns all.
    """
    return await _get_resource(ctx, "device-persona-mapping", device_type)
