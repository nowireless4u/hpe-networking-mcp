"""Aruba Central ``extensions`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``extensions.json`` vendor
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

# ----- psm -----


@tool(annotations=READ_ONLY)
async def central_get_psm(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``psm`` configurations from Central.

    PSM configuration.

    Parameters:
        name: Specific ``psm`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "psm", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_psm(
    ctx: Context,
    name: Annotated[str, Field(description="``psm`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``psm`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_psm`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``psm`` configuration in Central.

    PSM configuration.
    """
    return await _manage_resource(
        ctx,
        "psm",
        "psm",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- splunk-instances -----


@tool(annotations=READ_ONLY)
async def central_get_splunk_instances(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``splunk-instances`` configurations from Central.

    PSM configuration.

    Parameters:
        name: Specific ``splunk-instances`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "splunk-instances", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_splunk_instances(
    ctx: Context,
    name: Annotated[str, Field(description="``splunk-instances`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``splunk-instances`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_splunk_instances`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``splunk-instances`` configuration in Central.

    PSM configuration.
    """
    return await _manage_resource(
        ctx,
        "splunk-instances",
        "splunk-instances",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vsphere-instances -----


@tool(annotations=READ_ONLY)
async def central_get_vsphere_instances(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vsphere-instances`` configurations from Central.

    PSM configuration.

    Parameters:
        name: Specific ``vsphere-instances`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vsphere-instances", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vsphere_instances(
    ctx: Context,
    name: Annotated[str, Field(description="``vsphere-instances`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vsphere-instances`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vsphere_instances`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vsphere-instances`` configuration in Central.

    PSM configuration.
    """
    return await _manage_resource(
        ctx,
        "vsphere-instances",
        "vsphere-instances",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
