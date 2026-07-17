"""Aruba Central ``interfaces`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``interfaces.json`` vendor
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
    _OBJECT_TYPE_FIELD,
    _READ_DETAILED_FIELD,
    _READ_DEVICE_FUNCTION_FIELD,
    _READ_EFFECTIVE_FIELD,
    _READ_LIMIT_FIELD,
    _READ_OBJECT_TYPE_FIELD,
    _READ_OFFSET_FIELD,
    _READ_SCOPE_ID_FIELD,
    _READ_VIEW_TYPE_FIELD,
    _SCOPE_ID_FIELD,
    _get_resource,
    _manage_resource,
)

# ----- ap-port-profiles -----


@tool(capability=Capability.READ)
async def central_get_ap_port_profiles(
    ctx: Context,
    profile_name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``ap-port-profiles`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        profile_name: Specific ``ap-port-profiles`` identifier (OpenAPI path param: ``profile-name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "ap-port-profiles",
        profile_name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_ap_port_profiles(
    ctx: Context,
    profile_name: Annotated[
        str, Field(description="``ap-port-profiles`` identifier (OpenAPI path param: ``profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ap-port-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ap_port_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ap-port-profiles`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "ap-port-profiles",
        "ap-port-profiles",
        profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- ap-uplinks -----


@tool(capability=Capability.READ)
async def central_get_ap_uplinks(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``ap-uplinks`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``ap-uplinks`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "ap-uplinks",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_ap_uplinks(
    ctx: Context,
    name: Annotated[str, Field(description="``ap-uplinks`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ap-uplinks`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ap_uplinks`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ap-uplinks`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "ap-uplinks",
        "ap-uplinks",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- cdp -----


@tool(capability=Capability.READ)
async def central_get_cdp(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``cdp`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``cdp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "cdp",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_cdp(
    ctx: Context,
    name: Annotated[str, Field(description="``cdp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cdp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cdp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cdp`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "cdp",
        "cdp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- device-profile -----


@tool(capability=Capability.READ)
async def central_get_device_profile(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``device-profile`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``device-profile`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "device-profile",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_device_profile(
    ctx: Context,
    name: Annotated[str, Field(description="``device-profile`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``device-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_device_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``device-profile`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "device-profile",
        "device-profile",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- dhcp-client -----


@tool(capability=Capability.READ)
async def central_get_dhcp_client(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``dhcp-client`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``dhcp-client`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "dhcp-client",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_dhcp_client(
    ctx: Context,
    name: Annotated[str, Field(description="``dhcp-client`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dhcp-client`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dhcp_client`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dhcp-client`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "dhcp-client",
        "dhcp-client",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- ethernet-interfaces -----


@tool(capability=Capability.READ)
async def central_get_ethernet_interfaces(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``ethernet-interfaces`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``ethernet-interfaces`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "ethernet-interfaces",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_ethernet_interfaces(
    ctx: Context,
    name: Annotated[str, Field(description="``ethernet-interfaces`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ethernet-interfaces`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ethernet_interfaces`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ethernet-interfaces`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "ethernet-interfaces",
        "ethernet-interfaces",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- fault-monitor -----


@tool(capability=Capability.READ)
async def central_get_fault_monitor(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``fault-monitor`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``fault-monitor`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "fault-monitor",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_fault_monitor(
    ctx: Context,
    name: Annotated[str, Field(description="``fault-monitor`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``fault-monitor`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_fault_monitor`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``fault-monitor`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "fault-monitor",
        "fault-monitor",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- gw-port-profiles -----


@tool(capability=Capability.READ)
async def central_get_gw_port_profiles(
    ctx: Context,
    profile_name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``gw-port-profiles`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        profile_name: Specific ``gw-port-profiles`` identifier (OpenAPI path param: ``profile-name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "gw-port-profiles",
        profile_name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_gw_port_profiles(
    ctx: Context,
    profile_name: Annotated[
        str, Field(description="``gw-port-profiles`` identifier (OpenAPI path param: ``profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``gw-port-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_gw_port_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``gw-port-profiles`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "gw-port-profiles",
        "gw-port-profiles",
        profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- interface-profiles -----


@tool(capability=Capability.READ)
async def central_get_interface_profiles(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``interface-profiles`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``interface-profiles`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "interface-profiles",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_interface_profiles(
    ctx: Context,
    name: Annotated[str, Field(description="``interface-profiles`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``interface-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_interface_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``interface-profiles`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "interface-profiles",
        "interface-profiles",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- lacp -----


@tool(capability=Capability.READ)
async def central_get_lacp(
    ctx: Context,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get the ``lacp`` singleton configuration from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _get_resource(
        ctx,
        "lacp",
        None,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_lacp(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``lacp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_lacp`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``lacp`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "lacp",
        "lacp",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- lldp -----


@tool(capability=Capability.READ)
async def central_get_lldp(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``lldp`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``lldp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "lldp",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_lldp(
    ctx: Context,
    name: Annotated[str, Field(description="``lldp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``lldp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_lldp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``lldp`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "lldp",
        "lldp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- loopback-interfaces -----


@tool(capability=Capability.READ)
async def central_get_loopback_interfaces(
    ctx: Context,
    id: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``loopback-interfaces`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        id: Specific ``loopback-interfaces`` identifier (OpenAPI path param: ``id``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "loopback-interfaces",
        id,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_loopback_interfaces(
    ctx: Context,
    id: Annotated[str, Field(description="``loopback-interfaces`` identifier (OpenAPI path param: ``id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``loopback-interfaces`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_loopback_interfaces`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``loopback-interfaces`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "loopback-interfaces",
        "loopback-interfaces",
        id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- mgmt-interfaces -----


@tool(capability=Capability.READ)
async def central_get_mgmt_interfaces(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``mgmt-interfaces`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``mgmt-interfaces`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "mgmt-interfaces",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_mgmt_interfaces(
    ctx: Context,
    name: Annotated[str, Field(description="``mgmt-interfaces`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mgmt-interfaces`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mgmt_interfaces`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mgmt-interfaces`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "mgmt-interfaces",
        "mgmt-interfaces",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- mirror-endpoint -----


@tool(capability=Capability.READ)
async def central_get_mirror_endpoint(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``mirror-endpoint`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``mirror-endpoint`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "mirror-endpoint",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_mirror_endpoint(
    ctx: Context,
    name: Annotated[str, Field(description="``mirror-endpoint`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mirror-endpoint`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mirror_endpoint`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mirror-endpoint`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "mirror-endpoint",
        "mirror-endpoint",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- mirrors -----


@tool(capability=Capability.READ)
async def central_get_mirrors(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``mirrors`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``mirrors`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "mirrors",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_mirrors(
    ctx: Context,
    name: Annotated[str, Field(description="``mirrors`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mirrors`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mirrors`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mirrors`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "mirrors",
        "mirrors",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- portchannels -----


@tool(capability=Capability.READ)
async def central_get_portchannels(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``portchannels`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``portchannels`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "portchannels",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_portchannels(
    ctx: Context,
    name: Annotated[str, Field(description="``portchannels`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``portchannels`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_portchannels`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``portchannels`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "portchannels",
        "portchannels",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- sflow -----


@tool(capability=Capability.READ)
async def central_get_sflow(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``sflow`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``sflow`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "sflow",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_sflow(
    ctx: Context,
    name: Annotated[str, Field(description="``sflow`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``sflow`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_sflow`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``sflow`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "sflow",
        "sflow",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- static-macs -----


@tool(capability=Capability.READ)
async def central_get_static_macs(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``static-macs`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``static-macs`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "static-macs",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_static_macs(
    ctx: Context,
    name: Annotated[str, Field(description="``static-macs`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``static-macs`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_static_macs`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``static-macs`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "static-macs",
        "static-macs",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- sub-interfaces -----


@tool(capability=Capability.READ)
async def central_get_sub_interfaces(
    ctx: Context,
    parent_name_id: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``sub-interfaces`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        parent_name_id: Specific ``sub-interfaces`` identifier (OpenAPI path param: ``parent-name-id``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "sub-interfaces",
        parent_name_id,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_sub_interfaces(
    ctx: Context,
    parent_name_id: Annotated[
        str, Field(description="``sub-interfaces`` identifier (OpenAPI path param: ``parent-name-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``sub-interfaces`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_sub_interfaces`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``sub-interfaces`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "sub-interfaces",
        "sub-interfaces",
        parent_name_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- sw-port-profiles -----


@tool(capability=Capability.READ)
async def central_get_sw_port_profiles(
    ctx: Context,
    profile_name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``sw-port-profiles`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        profile_name: Specific ``sw-port-profiles`` identifier (OpenAPI path param: ``profile-name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "sw-port-profiles",
        profile_name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_sw_port_profiles(
    ctx: Context,
    profile_name: Annotated[
        str, Field(description="``sw-port-profiles`` identifier (OpenAPI path param: ``profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``sw-port-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_sw_port_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``sw-port-profiles`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "sw-port-profiles",
        "sw-port-profiles",
        profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- ufd -----


@tool(capability=Capability.READ)
async def central_get_ufd(
    ctx: Context,
    name: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``ufd`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        name: Specific ``ufd`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "ufd",
        name,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_ufd(
    ctx: Context,
    name: Annotated[str, Field(description="``ufd`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ufd`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ufd`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ufd`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "ufd",
        "ufd",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )


# ----- vlan-interfaces -----


@tool(capability=Capability.READ)
async def central_get_vlan_interfaces(
    ctx: Context,
    id: str | None = None,
    view_type: Annotated[str | None, _READ_VIEW_TYPE_FIELD] = None,
    object_type: Annotated[str | None, _READ_OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _READ_SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _READ_DEVICE_FUNCTION_FIELD] = None,
    effective: Annotated[bool | None, _READ_EFFECTIVE_FIELD] = None,
    detailed: Annotated[bool | None, _READ_DETAILED_FIELD] = None,
    limit: Annotated[int | None, _READ_LIMIT_FIELD] = None,
    offset: Annotated[int | None, _READ_OFFSET_FIELD] = None,
) -> dict | list | str:
    """Get ``vlan-interfaces`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        id: Specific ``vlan-interfaces`` identifier (OpenAPI path param: ``id``). If omitted, returns all.
    """
    return await _get_resource(
        ctx,
        "vlan-interfaces",
        id,
        view_type=view_type,
        object_type=object_type,
        scope_id=scope_id,
        device_function=device_function,
        effective=effective,
        detailed=detailed,
        limit=limit,
        offset=offset,
    )


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_vlan_interfaces(
    ctx: Context,
    id: Annotated[str, Field(description="``vlan-interfaces`` identifier (OpenAPI path param: ``id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vlan-interfaces`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vlan_interfaces`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    object_type: Annotated[str | None, _OBJECT_TYPE_FIELD] = None,
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vlan-interfaces`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "vlan-interfaces",
        "vlan-interfaces",
        id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
        object_type=object_type,
    )
