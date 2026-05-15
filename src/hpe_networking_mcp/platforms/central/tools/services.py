"""Aruba Central ``Services`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``Services`` OpenAPI tag-group. Wrappers
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

# ----- airgroup-policy -----


@tool(annotations=READ_ONLY)
async def central_get_airgroup_policy(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``airgroup-policy`` configurations from Central.

    An Airgroup policy must have a service definition, whereas VLAN and roles are optional. In case of roles, both 'allowed-roles' and 'disallowed-roles' cannot be configured at the same time. One of them must be empty. A maximum of 20 roles can be configured. In case of VLANs, both 'allowed-vlans' and 'disallowed-vlans' cannot be configured at the same time. One of them must be empty. A maximum of 20 VLANs or VLAN ranges can be configured. This feature is applicable for AP.

    Parameters:
        name: Specific ``airgroup-policy`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "airgroup-policies", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_airgroup_policy(
    ctx: Context,
    name: Annotated[str, Field(description="``airgroup-policy`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``airgroup-policy`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_airgroup_policy`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``airgroup-policy`` configuration in Central.

    An Airgroup policy must have a service definition, whereas VLAN and roles are optional. In case of roles, both 'allowed-roles' and 'disallowed-roles' cannot be configured at the same time. One of them must be empty. A maximum of 20 roles can be configured. In case of VLANs, both 'allowed-vlans' and 'disallowed-vlans' cannot be configured at the same time. One of them must be empty. A maximum of 20 VLANs or VLAN ranges can be configured. This feature is applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "airgroup-policies",
        "airgroup-policy",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- airgroup-servers -----


@tool(annotations=READ_ONLY)
async def central_get_airgroup_servers(
    ctx: Context,
    mac_address: str | None = None,
) -> dict | list | str:
    """Get ``airgroup-servers`` configurations from Central.

    Hosts that can act as Airgroup servers. The server can be restricted to specific role(s) and AP(s). In case of roles, both 'allowed-roles' and 'disallowed-roles' cannot be configured at the same time. One of them must be empty. Maximum 20 roles can be configured. In case of APs, a maximum of 50 APs can be configured.

    Parameters:
        mac_address: Specific ``airgroup-servers`` identifier (OpenAPI path param: ``mac-address``). If omitted, returns all.
    """
    return await _get_resource(ctx, "airgroup-servers", mac_address)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_airgroup_servers(
    ctx: Context,
    mac_address: Annotated[
        str, Field(description="``airgroup-servers`` identifier (OpenAPI path param: ``mac-address``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``airgroup-servers`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_airgroup_servers`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``airgroup-servers`` configuration in Central.

    Hosts that can act as Airgroup servers. The server can be restricted to specific role(s) and AP(s). In case of roles, both 'allowed-roles' and 'disallowed-roles' cannot be configured at the same time. One of them must be empty. Maximum 20 roles can be configured. In case of APs, a maximum of 50 APs can be configured.
    """
    return await _manage_resource(
        ctx,
        "airgroup-servers",
        "airgroup-servers",
        mac_address,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- airgroup-service-definition -----


@tool(annotations=READ_ONLY)
async def central_get_airgroup_service_definition(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``airgroup-service-definition`` configurations from Central.

    A Airgroup service definition is a group of service ID(s), which requires at least one custom service ID. A service ID can be of type mDNS or SSDP. A maximum of 100 service IDs are allowed across all the services. A maximum of 16 services are allowed and in each service 32 service IDs are allowed. There are pre-defined services with default service IDs. These are read-only and can be enabled or disabled. This feature is applicable for AP.

    Parameters:
        name: Specific ``airgroup-service-definition`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "airgroup-service-definitions", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_airgroup_service_definition(
    ctx: Context,
    name: Annotated[
        str, Field(description="``airgroup-service-definition`` identifier (OpenAPI path param: ``name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``airgroup-service-definition`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_airgroup_service_definition`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``airgroup-service-definition`` configuration in Central.

    A Airgroup service definition is a group of service ID(s), which requires at least one custom service ID. A service ID can be of type mDNS or SSDP. A maximum of 100 service IDs are allowed across all the services. A maximum of 16 services are allowed and in each service 32 service IDs are allowed. There are pre-defined services with default service IDs. These are read-only and can be enabled or disabled. This feature is applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "airgroup-service-definitions",
        "airgroup-service-definition",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- airgroup-system -----


@tool(annotations=READ_ONLY)
async def central_get_airgroup_system(
    ctx: Context,
) -> dict | list | str:
    """Get the ``airgroup-system`` singleton configuration from Central.

    AirGroup is a unique service that uses zero-configuration networking and allows devices to communicate over complex access-network topologies. AirGroup supports Bonjour and DLNA services on supported devices. This feature is applicable for AP.
    """
    return await _get_resource(ctx, "airgroup-system", None)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_airgroup_system(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``airgroup-system`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_airgroup_system`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``airgroup-system`` configuration in Central.

    AirGroup is a unique service that uses zero-configuration networking and allows devices to communicate over complex access-network topologies. AirGroup supports Bonjour and DLNA services on supported devices. This feature is applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "airgroup-system",
        "airgroup-system",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- location -----


@tool(annotations=READ_ONLY)
async def central_get_location(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``location`` configurations from Central.

    Location configuration. It supports three methods for locating: 1, Received Signal Strength Indication (RSSI): Calculate the pathloss of signal to locate a device. 2, Analytics and Location Engine (ALE): The ALE is designed to gather client information from the network, process it, and share it through a standard API. The client information gathered by ALE can be used for business purposes by analyzing a client’s Internet behavior such as shopping preferences. ALE includes a location engine that calculates the associated and unassociated device location every 30 seconds by default. 3, Real Time Location System (RTLS): AP supports the real-time tracking of devices when integrated with the Airwave server or a third-party RTLS server such as Aeroscout RTLS server. With the help of the RTLS, the devices can be monitored in real time or through history. This feature is only applicable for AP.

    Parameters:
        name: Specific ``location`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "location", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_location(
    ctx: Context,
    name: Annotated[str, Field(description="``location`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``location`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_location`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``location`` configuration in Central.

    Location configuration. It supports three methods for locating: 1, Received Signal Strength Indication (RSSI): Calculate the pathloss of signal to locate a device. 2, Analytics and Location Engine (ALE): The ALE is designed to gather client information from the network, process it, and share it through a standard API. The client information gathered by ALE can be used for business purposes by analyzing a client’s Internet behavior such as shopping preferences. ALE includes a location engine that calculates the associated and unassociated device location every 30 seconds by default. 3, Real Time Location System (RTLS): AP supports the real-time tracking of devices when integrated with the Airwave server or a third-party RTLS server such as Aeroscout RTLS server. With the help of the RTLS, the devices can be monitored in real time or through history. This feature is only applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "location",
        "location",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
