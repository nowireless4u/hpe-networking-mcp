"""Aruba Central ``miscellaneous`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``miscellaneous.json`` vendor
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

# ----- device-firmware -----


@tool(annotations=READ_ONLY)
async def central_get_device_firmware(
    ctx: Context,
) -> dict | list | str:
    """Get the ``device-firmware`` singleton configuration from Central.

    Device firmware configuration parameters.
    """
    return await _get_resource(ctx, "device-firmware", None)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_device_firmware(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``device-firmware`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_device_firmware`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``device-firmware`` configuration in Central.

    Device firmware configuration parameters.
    """
    return await _manage_resource(
        ctx,
        "device-firmware",
        "device-firmware",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dsm -----


@tool(annotations=READ_ONLY)
async def central_get_dsm(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dsm`` configurations from Central.

    Device firmware configuration parameters.

    Parameters:
        name: Specific ``dsm`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dsm", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dsm(
    ctx: Context,
    name: Annotated[str, Field(description="``dsm`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dsm`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dsm`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dsm`` configuration in Central.

    Device firmware configuration parameters.
    """
    return await _manage_resource(
        ctx,
        "dsm",
        "dsm",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- features -----


@tool(annotations=READ_ONLY)
async def central_get_features(
    ctx: Context,
) -> dict | list | str:
    """Get the ``features`` singleton configuration from Central.

    Device firmware configuration parameters.
    """
    return await _get_resource(ctx, "features", None)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_features(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``features`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_features`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``features`` configuration in Central.

    Device firmware configuration parameters.
    """
    return await _manage_resource(
        ctx,
        "features",
        "features",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- node-operations -----


@tool(annotations=READ_ONLY)
async def central_get_node_operations(
    ctx: Context,
    xpath: str | None = None,
) -> dict | list | str:
    """Get ``node-operations`` configurations from Central.

    Device firmware configuration parameters.

    Parameters:
        xpath: Specific ``node-operations`` identifier (OpenAPI path param: ``xpath``). If omitted, returns all.
    """
    return await _get_resource(ctx, "node-operations", xpath)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_node_operations(
    ctx: Context,
    xpath: Annotated[str, Field(description="``node-operations`` identifier (OpenAPI path param: ``xpath``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``node-operations`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_node_operations`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``node-operations`` configuration in Central.

    Device firmware configuration parameters.
    """
    return await _manage_resource(
        ctx,
        "node-operations",
        "node-operations",
        xpath,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- overlay-wlan -----


@tool(annotations=READ_ONLY)
async def central_get_overlay_wlan(
    ctx: Context,
    profile: str | None = None,
) -> dict | list | str:
    """Get ``overlay-wlan`` configurations from Central.

    Device firmware configuration parameters.

    Parameters:
        profile: Specific ``overlay-wlan`` identifier (OpenAPI path param: ``profile``). If omitted, returns all.
    """
    return await _get_resource(ctx, "overlay-wlan", profile)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_overlay_wlan(
    ctx: Context,
    profile: Annotated[str, Field(description="``overlay-wlan`` identifier (OpenAPI path param: ``profile``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``overlay-wlan`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_overlay_wlan`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``overlay-wlan`` configuration in Central.

    Device firmware configuration parameters.
    """
    return await _manage_resource(
        ctx,
        "overlay-wlan",
        "overlay-wlan",
        profile,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vsx-config -----


@tool(annotations=READ_ONLY)
async def central_get_vsx_config(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vsx-config`` configurations from Central.

    Device firmware configuration parameters.

    Parameters:
        name: Specific ``vsx-config`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vsx-config", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vsx_config(
    ctx: Context,
    name: Annotated[str, Field(description="``vsx-config`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vsx-config`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vsx_config`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vsx-config`` configuration in Central.

    Device firmware configuration parameters.
    """
    return await _manage_resource(
        ctx,
        "vsx-config",
        "vsx-config",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vxlan -----


@tool(annotations=READ_ONLY)
async def central_get_vxlan(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vxlan`` configurations from Central.

    Device firmware configuration parameters.

    Parameters:
        name: Specific ``vxlan`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vxlan", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vxlan(
    ctx: Context,
    name: Annotated[str, Field(description="``vxlan`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vxlan`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vxlan`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vxlan`` configuration in Central.

    Device firmware configuration parameters.
    """
    return await _manage_resource(
        ctx,
        "vxlan",
        "vxlan",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
