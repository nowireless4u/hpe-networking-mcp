"""Aruba Central ``Uncategorized`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``Uncategorized`` OpenAPI tag-group. Wrappers
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

# ----- db-data-migration -----


@tool(annotations=READ_ONLY)
async def central_get_db_data_migration(
    ctx: Context,
    xpath: str | None = None,
) -> dict | list | str:
    """Get ``db-data-migration`` configurations from Central.

    Container to specify node operations.

    Parameters:
        xpath: Specific ``db-data-migration`` identifier (OpenAPI path param: ``xpath``). If omitted, returns all.
    """
    return await _get_resource(ctx, "node-operations", xpath)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_db_data_migration(
    ctx: Context,
    xpath: Annotated[str, Field(description="``db-data-migration`` identifier (OpenAPI path param: ``xpath``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``db-data-migration`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_db_data_migration`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``db-data-migration`` configuration in Central.

    Container to specify node operations.
    """
    return await _manage_resource(
        ctx,
        "node-operations",
        "db-data-migration",
        xpath,
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

    Distributed Services Module(DSM) configuration. DSM provide services such as stateful firewall and flow logging.

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

    Distributed Services Module(DSM) configuration. DSM provide services such as stateful firewall and flow logging.
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


# ----- feature-property -----


@tool(annotations=READ_ONLY)
async def central_get_feature_property(
    ctx: Context,
) -> dict | list | str:
    """Get the ``feature-property`` singleton configuration from Central.

    Features.
    """
    return await _get_resource(ctx, "features", None)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_feature_property(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``feature-property`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_feature_property`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``feature-property`` configuration in Central.

    Features.
    """
    return await _manage_resource(
        ctx,
        "features",
        "feature-property",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- firmware-management -----


@tool(annotations=READ_ONLY)
async def central_get_firmware_management(
    ctx: Context,
) -> dict | list | str:
    """Get the ``firmware-management`` singleton configuration from Central.

    Device firmware configuration parameters.
    """
    return await _get_resource(ctx, "device-firmware", None)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_firmware_management(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``firmware-management`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_firmware_management`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``firmware-management`` configuration in Central.

    Device firmware configuration parameters.
    """
    return await _manage_resource(
        ctx,
        "device-firmware",
        "firmware-management",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- interface-vxlan -----


@tool(annotations=READ_ONLY)
async def central_get_interface_vxlan(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``interface-vxlan`` configurations from Central.

    Configure VXLAN. Virtual eXtensible Local Access Network (VXLAN) provides a framework for Overlaying Virtualized Layer 2 Networks over Layer 3 networks. In CX it creates a VXLAN Interface.

    Parameters:
        name: Specific ``interface-vxlan`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vxlan", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_interface_vxlan(
    ctx: Context,
    name: Annotated[str, Field(description="``interface-vxlan`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``interface-vxlan`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_interface_vxlan`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``interface-vxlan`` configuration in Central.

    Configure VXLAN. Virtual eXtensible Local Access Network (VXLAN) provides a framework for Overlaying Virtualized Layer 2 Networks over Layer 3 networks. In CX it creates a VXLAN Interface.
    """
    return await _manage_resource(
        ctx,
        "vxlan",
        "interface-vxlan",
        name,
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

    Overlay WLAN Services Config.

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

    Overlay WLAN Services Config.
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


# ----- vsx-pair -----


@tool(annotations=READ_ONLY)
async def central_get_vsx_pair(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vsx-pair`` configurations from Central.

    VSX config for primary or secondary device.

    Parameters:
        name: Specific ``vsx-pair`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vsx-config", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vsx_pair(
    ctx: Context,
    name: Annotated[str, Field(description="``vsx-pair`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vsx-pair`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vsx_pair`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vsx-pair`` configuration in Central.

    VSX config for primary or secondary device.
    """
    return await _manage_resource(
        ctx,
        "vsx-config",
        "vsx-pair",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
