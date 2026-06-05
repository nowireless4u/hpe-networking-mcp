"""Aruba Central ``vlans-networks`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``vlans-networks.json`` vendor
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

# ----- erps -----


@tool(annotations=READ_ONLY)
async def central_get_erps(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``erps`` configurations from Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.

    Parameters:
        name: Specific ``erps`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "erps", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_erps(
    ctx: Context,
    name: Annotated[str, Field(description="``erps`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``erps`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_erps`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``erps`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "erps",
        "erps",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- layer2-vlan -----


@tool(annotations=READ_ONLY)
async def central_get_layer2_vlan(
    ctx: Context,
    vlan: str | None = None,
) -> dict | list | str:
    """Get ``layer2-vlan`` configurations from Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.

    Parameters:
        vlan: Specific ``layer2-vlan`` identifier (OpenAPI path param: ``vlan``). If omitted, returns all.
    """
    return await _get_resource(ctx, "layer2-vlan", vlan)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_layer2_vlan(
    ctx: Context,
    vlan: Annotated[str, Field(description="``layer2-vlan`` identifier (OpenAPI path param: ``vlan``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``layer2-vlan`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_layer2_vlan`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``layer2-vlan`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "layer2-vlan",
        "layer2-vlan",
        vlan,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- layer2-vlan-range -----


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_layer2_vlan_range(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``layer2-vlan-range`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_layer2_vlan_range`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``layer2-vlan-range`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "layer2-vlan-range",
        "layer2-vlan-range",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- loop-protect -----


@tool(annotations=READ_ONLY)
async def central_get_loop_protect(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``loop-protect`` configurations from Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.

    Parameters:
        name: Specific ``loop-protect`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "loop-protect", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_loop_protect(
    ctx: Context,
    name: Annotated[str, Field(description="``loop-protect`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``loop-protect`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_loop_protect`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``loop-protect`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "loop-protect",
        "loop-protect",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mvrp -----


@tool(annotations=READ_ONLY)
async def central_get_mvrp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mvrp`` configurations from Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.

    Parameters:
        name: Specific ``mvrp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mvrp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_mvrp(
    ctx: Context,
    name: Annotated[str, Field(description="``mvrp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mvrp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mvrp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mvrp`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "mvrp",
        "mvrp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- named-vlan -----


@tool(annotations=READ_ONLY)
async def central_get_named_vlan(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``named-vlan`` configurations from Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.

    Parameters:
        name: Specific ``named-vlan`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "named-vlan", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_named_vlan(
    ctx: Context,
    name: Annotated[str, Field(description="``named-vlan`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``named-vlan`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_named_vlan`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``named-vlan`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "named-vlan",
        "named-vlan",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- smartlink -----


@tool(annotations=READ_ONLY)
async def central_get_smartlink(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``smartlink`` configurations from Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.

    Parameters:
        name: Specific ``smartlink`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "smartlink", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_smartlink(
    ctx: Context,
    name: Annotated[str, Field(description="``smartlink`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``smartlink`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_smartlink`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``smartlink`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "smartlink",
        "smartlink",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- static-neighbor -----


@tool(annotations=READ_ONLY)
async def central_get_static_neighbor(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``static-neighbor`` configurations from Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.

    Parameters:
        name: Specific ``static-neighbor`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "static-neighbor", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_static_neighbor(
    ctx: Context,
    name: Annotated[str, Field(description="``static-neighbor`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``static-neighbor`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_static_neighbor`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``static-neighbor`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "static-neighbor",
        "static-neighbor",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- stp -----


@tool(annotations=READ_ONLY)
async def central_get_stp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``stp`` configurations from Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.

    Parameters:
        name: Specific ``stp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "stp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_stp(
    ctx: Context,
    name: Annotated[str, Field(description="``stp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``stp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_stp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``stp`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "stp",
        "stp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- stp-gw -----


@tool(annotations=READ_ONLY)
async def central_get_stp_gw(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``stp-gw`` configurations from Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.

    Parameters:
        name: Specific ``stp-gw`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "stp-gw", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_stp_gw(
    ctx: Context,
    name: Annotated[str, Field(description="``stp-gw`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``stp-gw`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_stp_gw`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``stp-gw`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "stp-gw",
        "stp-gw",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vrrp -----


@tool(annotations=READ_ONLY)
async def central_get_vrrp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vrrp`` configurations from Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.

    Parameters:
        name: Specific ``vrrp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vrrp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vrrp(
    ctx: Context,
    name: Annotated[str, Field(description="``vrrp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vrrp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vrrp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vrrp`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "vrrp",
        "vrrp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vrrp-global -----


@tool(annotations=READ_ONLY)
async def central_get_vrrp_global(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vrrp-global`` configurations from Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.

    Parameters:
        name: Specific ``vrrp-global`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vrrp-global", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vrrp_global(
    ctx: Context,
    name: Annotated[str, Field(description="``vrrp-global`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vrrp-global`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vrrp_global`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vrrp-global`` configuration in Central.

    Ethernet Ring Protection Switching (ERPS) is a protocol defined by the International Telecommunication Union - Telecommunication Standardization Sector (ITU-T) to eliminate loops at Layer 2.
    """
    return await _manage_resource(
        ctx,
        "vrrp-global",
        "vrrp-global",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
