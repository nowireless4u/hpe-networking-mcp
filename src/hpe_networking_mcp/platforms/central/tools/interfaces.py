"""Aruba Central ``Interfaces`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``Interfaces`` OpenAPI tag-group. Wrappers
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

# ----- ap-port-profile -----


@tool(annotations=READ_ONLY)
async def central_get_ap_port_profile(
    ctx: Context,
    profile_name: str | None = None,
) -> dict | list | str:
    """Get ``ap-port-profile`` configurations from Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.

    Parameters:
        profile_name: Specific ``ap-port-profile`` identifier (OpenAPI path param: ``profile-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ap-port-profiles", profile_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ap_port_profile(
    ctx: Context,
    profile_name: Annotated[
        str, Field(description="``ap-port-profile`` identifier (OpenAPI path param: ``profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ap-port-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ap_port_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ap-port-profile`` configuration in Central.

    Port profiles, config parameters on the port such as VLAN settings, authentication methods, link speed, PoE settings, and more.
    """
    return await _manage_resource(
        ctx,
        "ap-port-profiles",
        "ap-port-profile",
        profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ap-uplink -----


@tool(annotations=READ_ONLY)
async def central_get_ap_uplink(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ap-uplink`` configurations from Central.

    AP uplink profile, configure the uplink parameters, such like ethernet uplink, cellular uplink, preemption parameters, management VLAN, etc.

    Parameters:
        name: Specific ``ap-uplink`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ap-uplinks", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ap_uplink(
    ctx: Context,
    name: Annotated[str, Field(description="``ap-uplink`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ap-uplink`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ap_uplink`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ap-uplink`` configuration in Central.

    AP uplink profile, configure the uplink parameters, such like ethernet uplink, cellular uplink, preemption parameters, management VLAN, etc.
    """
    return await _manage_resource(
        ctx,
        "ap-uplinks",
        "ap-uplink",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cdp -----


@tool(annotations=READ_ONLY)
async def central_get_cdp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``cdp`` configurations from Central.

    Cisco Discovery Protocol (CDP) configuration.CDP is used for collecting directly connected neighbor device information like hardware,software,device name details etc.

    Parameters:
        name: Specific ``cdp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "cdp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cdp`` configuration in Central.

    Cisco Discovery Protocol (CDP) configuration.CDP is used for collecting directly connected neighbor device information like hardware,software,device name details etc.
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
    )


# ----- device-profile -----


@tool(annotations=READ_ONLY)
async def central_get_device_profile(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``device-profile`` configurations from Central.

    Device-Profile allows automatic discovery and configuration of other devices such as APs, IP phones, Security cameras, Printers etc.. on the network. The discovery is done via LLDP, CDP or MAC match.

    Parameters:
        name: Specific ``device-profile`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "device-profile", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``device-profile`` configuration in Central.

    Device-Profile allows automatic discovery and configuration of other devices such as APs, IP phones, Security cameras, Printers etc.. on the network. The discovery is done via LLDP, CDP or MAC match.
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
    )


# ----- dhcp-client -----


@tool(annotations=READ_ONLY)
async def central_get_dhcp_client(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dhcp-client`` configurations from Central.

    Dynamic Host Configuration Protocol Client Options Configuration. The main purpose of this feature is to enable DHCP client on the preferred VLAN. The DHCP client feature allows VLAN to act as a host requesting configuration parameters such as IP address, DNS IPs, ZTP information etc.

    Parameters:
        name: Specific ``dhcp-client`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dhcp-client", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dhcp-client`` configuration in Central.

    Dynamic Host Configuration Protocol Client Options Configuration. The main purpose of this feature is to enable DHCP client on the preferred VLAN. The DHCP client feature allows VLAN to act as a host requesting configuration parameters such as IP address, DNS IPs, ZTP information etc.
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
    )


# ----- fault-monitor -----


@tool(annotations=READ_ONLY)
async def central_get_fault_monitor(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``fault-monitor`` configurations from Central.

    Fault monitor top level configuration.

    Parameters:
        name: Specific ``fault-monitor`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "fault-monitor", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``fault-monitor`` configuration in Central.

    Fault monitor top level configuration.
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
    )


# ----- gw-port-profile -----


@tool(annotations=READ_ONLY)
async def central_get_gw_port_profile(
    ctx: Context,
    profile_name: str | None = None,
) -> dict | list | str:
    """Get ``gw-port-profile`` configurations from Central.

    To configure and manage port profiles. A port-profile can be used to configure ethernet interface. Same profile can be applied to multiple interfaces and avoids repeating same configuration for interfaces. Gigabit ethernet config, LLDP, spanning-tree, switch-port configuration, etc can be applied using the port-profile.

    Parameters:
        profile_name: Specific ``gw-port-profile`` identifier (OpenAPI path param: ``profile-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "gw-port-profiles", profile_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_gw_port_profile(
    ctx: Context,
    profile_name: Annotated[
        str, Field(description="``gw-port-profile`` identifier (OpenAPI path param: ``profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``gw-port-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_gw_port_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``gw-port-profile`` configuration in Central.

    To configure and manage port profiles. A port-profile can be used to configure ethernet interface. Same profile can be applied to multiple interfaces and avoids repeating same configuration for interfaces. Gigabit ethernet config, LLDP, spanning-tree, switch-port configuration, etc can be applied using the port-profile.
    """
    return await _manage_resource(
        ctx,
        "gw-port-profiles",
        "gw-port-profile",
        profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- interface-ethernet -----


@tool(annotations=READ_ONLY)
async def central_get_interface_ethernet(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``interface-ethernet`` configurations from Central.

    Ethernet interfaces provide physical connectivity for network devices including switches, gateways, access points, and bridges. This module supports configuration of interface properties, port profiles, link aggregation, Power over Ethernet (PoE), security features (AAA, port-security, LLDP), Layer 3 routing capabilities, and advanced features like PIM multicast, flow telemetry, and port monitoring. Supported scopes: Device. This configuration relies on Port Profile configurations (sw-profile for switches, gw-profile for gateways, ap-profile for access points, br-profile for bridges) for template-based settings. Interface names follow device-specific patterns (e.g., gateway model GW_7005 supports 0/0/[0-3], GW_7205 supports 0/0/[0-5]). Use this API to retrieve the list of Ethernet Interface configurations.

    Parameters:
        name: Specific ``interface-ethernet`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ethernet-interfaces", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_interface_ethernet(
    ctx: Context,
    name: Annotated[str, Field(description="``interface-ethernet`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``interface-ethernet`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_interface_ethernet`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``interface-ethernet`` configuration in Central.

    Ethernet interfaces provide physical connectivity for network devices including switches, gateways, access points, and bridges. This module supports configuration of interface properties, port profiles, link aggregation, Power over Ethernet (PoE), security features (AAA, port-security, LLDP), Layer 3 routing capabilities, and advanced features like PIM multicast, flow telemetry, and port monitoring. Supported scopes: Device. This configuration relies on Port Profile configurations (sw-profile for switches, gw-profile for gateways, ap-profile for access points, br-profile for bridges) for template-based settings. Interface names follow device-specific patterns (e.g., gateway model GW_7005 supports 0/0/[0-3], GW_7205 supports 0/0/[0-5]). Use this API to retrieve the list of Ethernet Interface configurations.
    """
    return await _manage_resource(
        ctx,
        "ethernet-interfaces",
        "interface-ethernet",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- interface-loopback -----


@tool(annotations=READ_ONLY)
async def central_get_interface_loopback(
    ctx: Context,
    id: str | None = None,
) -> dict | list | str:
    """Get ``interface-loopback`` configurations from Central.

    Placeholder for loopback interface(s) configuration. A loopback interface is a virtual interface that is always up and support IPv4/IPv6 address configurations.

    Parameters:
        id: Specific ``interface-loopback`` identifier (OpenAPI path param: ``id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "loopback-interfaces", id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_interface_loopback(
    ctx: Context,
    id: Annotated[str, Field(description="``interface-loopback`` identifier (OpenAPI path param: ``id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``interface-loopback`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_interface_loopback`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``interface-loopback`` configuration in Central.

    Placeholder for loopback interface(s) configuration. A loopback interface is a virtual interface that is always up and support IPv4/IPv6 address configurations.
    """
    return await _manage_resource(
        ctx,
        "loopback-interfaces",
        "interface-loopback",
        id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- interface-management -----


@tool(annotations=READ_ONLY)
async def central_get_interface_management(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``interface-management`` configurations from Central.

    Configuration for the Management Interface. The device is configured or monitored through the Management interface on mgmt VRF. All management traffic such as device ssh, snmp, tftp and so on, goes through the Management interface.

    Parameters:
        name: Specific ``interface-management`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mgmt-interfaces", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_interface_management(
    ctx: Context,
    name: Annotated[str, Field(description="``interface-management`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``interface-management`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_interface_management`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``interface-management`` configuration in Central.

    Configuration for the Management Interface. The device is configured or monitored through the Management interface on mgmt VRF. All management traffic such as device ssh, snmp, tftp and so on, goes through the Management interface.
    """
    return await _manage_resource(
        ctx,
        "mgmt-interfaces",
        "interface-management",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- interface-portchannel -----


@tool(annotations=READ_ONLY)
async def central_get_interface_portchannel(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``interface-portchannel`` configurations from Central.

    Port Channel (Link Aggregation Group/LAG) interfaces combine multiple physical Ethernet links into a single logical interface for increased bandwidth, load balancing, and redundancy per IEEE 802.3ad. Port channels support static aggregation and dynamic LACP negotiation with features including VLAN trunking, routing protocols, access control, and QoS policies. Configure port channel member interfaces, LACP parameters, VLAN assignments, IP addressing, and link protection settings. Supported scopes: Device. Device Limits: Gateway supports port channels 0-7 (8 total). Use this API to retrieve the list of port channel interfaces.

    Parameters:
        name: Specific ``interface-portchannel`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "portchannels", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_interface_portchannel(
    ctx: Context,
    name: Annotated[str, Field(description="``interface-portchannel`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``interface-portchannel`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_interface_portchannel`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``interface-portchannel`` configuration in Central.

    Port Channel (Link Aggregation Group/LAG) interfaces combine multiple physical Ethernet links into a single logical interface for increased bandwidth, load balancing, and redundancy per IEEE 802.3ad. Port channels support static aggregation and dynamic LACP negotiation with features including VLAN trunking, routing protocols, access control, and QoS policies. Configure port channel member interfaces, LACP parameters, VLAN assignments, IP addressing, and link protection settings. Supported scopes: Device. Device Limits: Gateway supports port channels 0-7 (8 total). Use this API to retrieve the list of port channel interfaces.
    """
    return await _manage_resource(
        ctx,
        "portchannels",
        "interface-portchannel",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- interface-profile -----


@tool(annotations=READ_ONLY)
async def central_get_interface_profile(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``interface-profile`` configurations from Central.

    List of Interface Profile configuration. Interface Profile is bundle of interface configuration for devices with specific sku/model. Defined for set of uplink/downlink ports for given models. Interface Profile can be defined for stacks/chassis for fixed/automatic set of members/LineCards. Interface Profile can be defined for custom stack/chassis size. One Interface Profile can have port-profile config for uplink + downlink + custom ports for given model/device type. In case of stacks, Interface Profile will not be applied VSF link ports, if they are part of automatic/custom Interface Profile model+ports.

    Parameters:
        name: Specific ``interface-profile`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "interface-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_interface_profile(
    ctx: Context,
    name: Annotated[str, Field(description="``interface-profile`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``interface-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_interface_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``interface-profile`` configuration in Central.

    List of Interface Profile configuration. Interface Profile is bundle of interface configuration for devices with specific sku/model. Defined for set of uplink/downlink ports for given models. Interface Profile can be defined for stacks/chassis for fixed/automatic set of members/LineCards. Interface Profile can be defined for custom stack/chassis size. One Interface Profile can have port-profile config for uplink + downlink + custom ports for given model/device type. In case of stacks, Interface Profile will not be applied VSF link ports, if they are part of automatic/custom Interface Profile model+ports.
    """
    return await _manage_resource(
        ctx,
        "interface-profiles",
        "interface-profile",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- interface-subinterface -----


@tool(annotations=READ_ONLY)
async def central_get_interface_subinterface(
    ctx: Context,
    parent_name_id: str | None = None,
) -> dict | list | str:
    """Get ``interface-subinterface`` configurations from Central.

    Sub Interfaces.

    Parameters:
        parent_name_id: Specific ``interface-subinterface`` identifier (OpenAPI path param: ``parent-name-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "sub-interfaces", parent_name_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_interface_subinterface(
    ctx: Context,
    parent_name_id: Annotated[
        str, Field(description="``interface-subinterface`` identifier (OpenAPI path param: ``parent-name-id``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``interface-subinterface`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_interface_subinterface`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``interface-subinterface`` configuration in Central.

    Sub Interfaces.
    """
    return await _manage_resource(
        ctx,
        "sub-interfaces",
        "interface-subinterface",
        parent_name_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- interface-vlan -----


@tool(annotations=READ_ONLY)
async def central_get_interface_vlan(
    ctx: Context,
    id: str | None = None,
) -> dict | list | str:
    """Get ``interface-vlan`` configurations from Central.

    Layer 3 VLAN (Switched Virtual Interface/SVI) configurations provide IP routing functionality for VLANs, enabling inter-VLAN routing and gateway services. VLAN interfaces support IPv4/IPv6 addressing, DHCP relay, routing protocol participation (OSPF, BGP, RIP), VRRP for high availability, and access control policies. Configure VLAN interface IP addresses, DHCP servers/relay agents, multicast protocols, routing parameters, and security policies. Device Limits: Gateway supports max 3 IPv6 addresses, 16 IPv4 helper addresses, and 3 IPv6 helper addresses per VLAN interface. Use this API to retrieve the list of VLAN interfaces.

    Parameters:
        id: Specific ``interface-vlan`` identifier (OpenAPI path param: ``id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vlan-interfaces", id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_interface_vlan(
    ctx: Context,
    id: Annotated[str, Field(description="``interface-vlan`` identifier (OpenAPI path param: ``id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``interface-vlan`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_interface_vlan`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``interface-vlan`` configuration in Central.

    Layer 3 VLAN (Switched Virtual Interface/SVI) configurations provide IP routing functionality for VLANs, enabling inter-VLAN routing and gateway services. VLAN interfaces support IPv4/IPv6 addressing, DHCP relay, routing protocol participation (OSPF, BGP, RIP), VRRP for high availability, and access control policies. Configure VLAN interface IP addresses, DHCP servers/relay agents, multicast protocols, routing parameters, and security policies. Device Limits: Gateway supports max 3 IPv6 addresses, 16 IPv4 helper addresses, and 3 IPv6 helper addresses per VLAN interface. Use this API to retrieve the list of VLAN interfaces.
    """
    return await _manage_resource(
        ctx,
        "vlan-interfaces",
        "interface-vlan",
        id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- lacp -----


@tool(annotations=READ_ONLY)
async def central_get_lacp(
    ctx: Context,
) -> dict | list | str:
    """Get the ``lacp`` singleton configuration from Central.

    Link Aggregation Control Protocol (LACP) dynamically negotiates and manages link aggregation groups (LAGs/Port Channels) per IEEE 802.3ad/802.1AX standards. LACP provides automatic failover, load distribution across member links, and detection of misconfigured aggregation. Configure system-level LACP priority, hashing algorithms, and interface-specific parameters including active/passive modes, heartbeat rates (fast/slow), and minimum active link thresholds. Use this API to retrieve LACP system configuration.
    """
    return await _get_resource(ctx, "lacp", None)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``lacp`` configuration in Central.

    Link Aggregation Control Protocol (LACP) dynamically negotiates and manages link aggregation groups (LAGs/Port Channels) per IEEE 802.3ad/802.1AX standards. LACP provides automatic failover, load distribution across member links, and detection of misconfigured aggregation. Configure system-level LACP priority, hashing algorithms, and interface-specific parameters including active/passive modes, heartbeat rates (fast/slow), and minimum active link thresholds. Use this API to retrieve LACP system configuration.
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
    )


# ----- lldp -----


@tool(annotations=READ_ONLY)
async def central_get_lldp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``lldp`` configurations from Central.

    The Link Layer Discovery Protocol (LLDP) is an industry-standard, vendor-neutral method to allow networked devices to advertise capabilities, discover and identify other LLDP enabled devices and gather information in a LAN. LLDP is supported on physical interfaces and Out-Of-Band Management (OOBM) interfaces and it is not supported on logical interfaces.

    Parameters:
        name: Specific ``lldp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "lldp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``lldp`` configuration in Central.

    The Link Layer Discovery Protocol (LLDP) is an industry-standard, vendor-neutral method to allow networked devices to advertise capabilities, discover and identify other LLDP enabled devices and gather information in a LAN. LLDP is supported on physical interfaces and Out-Of-Band Management (OOBM) interfaces and it is not supported on logical interfaces.
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
    )


# ----- mirror -----


@tool(annotations=READ_ONLY)
async def central_get_mirror(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mirror`` configurations from Central.

    Mirror Configuration. Mirroring is the ability of a switch to transmit a copy of a packet out another system interface. This allows network administrators to replicate all traffic arriving and/or leaving selected system interfaces for collection/analysis purposes.

    Parameters:
        name: Specific ``mirror`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mirrors", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_mirror(
    ctx: Context,
    name: Annotated[str, Field(description="``mirror`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mirror`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mirror`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mirror`` configuration in Central.

    Mirror Configuration. Mirroring is the ability of a switch to transmit a copy of a packet out another system interface. This allows network administrators to replicate all traffic arriving and/or leaving selected system interfaces for collection/analysis purposes.
    """
    return await _manage_resource(
        ctx,
        "mirrors",
        "mirror",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mirror-endpoint -----


@tool(annotations=READ_ONLY)
async def central_get_mirror_endpoint(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mirror-endpoint`` configurations from Central.

    Mirror-Endpoints terminate a remote mirror tunnel. They serve to control packet decapsulation and forwarding to the mirror destinations. Creating a Mirror-Endpoint is independent of the corresponding mirror session, which means there is no ordering requirement for the creation of a mirror session and a Mirror Endpoint.

    Parameters:
        name: Specific ``mirror-endpoint`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mirror-endpoint", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mirror-endpoint`` configuration in Central.

    Mirror-Endpoints terminate a remote mirror tunnel. They serve to control packet decapsulation and forwarding to the mirror destinations. Creating a Mirror-Endpoint is independent of the corresponding mirror session, which means there is no ordering requirement for the creation of a mirror session and a Mirror Endpoint.
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
    )


# ----- sflow -----


@tool(annotations=READ_ONLY)
async def central_get_sflow(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``sflow`` configurations from Central.

    Sampled Flow (sFlow) configuration.sFlow is an industry-standard sampling technology used to sample application-level packet flows and gather interface statistics from network devices.

    Parameters:
        name: Specific ``sflow`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "sflow", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``sflow`` configuration in Central.

    Sampled Flow (sFlow) configuration.sFlow is an industry-standard sampling technology used to sample application-level packet flows and gather interface statistics from network devices.
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
    )


# ----- static-mac -----


@tool(annotations=READ_ONLY)
async def central_get_static_mac(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``static-mac`` configurations from Central.

    Static MAC configuration.

    Parameters:
        name: Specific ``static-mac`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "static-macs", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_static_mac(
    ctx: Context,
    name: Annotated[str, Field(description="``static-mac`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``static-mac`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_static_mac`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``static-mac`` configuration in Central.

    Static MAC configuration.
    """
    return await _manage_resource(
        ctx,
        "static-macs",
        "static-mac",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- sw-port-profile -----


@tool(annotations=READ_ONLY)
async def central_get_sw_port_profile(
    ctx: Context,
    profile_name: str | None = None,
) -> dict | list | str:
    """Get ``sw-port-profile`` configurations from Central.

    Configure and manage port profiles. A port profile is a template for configuring ethernet interface configurations. It is a mechanism intended to ease the process of configuring multiple interfaces with same set of configurations. Instead of manually configuring each interface one-by-one, the port profile collects the common configuration settings and allows them to be applied on the interface or a collection of interfaces.

    Parameters:
        profile_name: Specific ``sw-port-profile`` identifier (OpenAPI path param: ``profile-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "sw-port-profiles", profile_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_sw_port_profile(
    ctx: Context,
    profile_name: Annotated[
        str, Field(description="``sw-port-profile`` identifier (OpenAPI path param: ``profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``sw-port-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_sw_port_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``sw-port-profile`` configuration in Central.

    Configure and manage port profiles. A port profile is a template for configuring ethernet interface configurations. It is a mechanism intended to ease the process of configuring multiple interfaces with same set of configurations. Instead of manually configuring each interface one-by-one, the port profile collects the common configuration settings and allows them to be applied on the interface or a collection of interfaces.
    """
    return await _manage_resource(
        ctx,
        "sw-port-profiles",
        "sw-port-profile",
        profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ufd -----


@tool(annotations=READ_ONLY)
async def central_get_ufd(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ufd`` configurations from Central.

    Uplink Failure Detection(UFD) Configurations.UFD monitors (tracks the forwarding state of) the interfaces/LAGs(Link Aggregation) configured as links-to-monitor (LtM) and when all LtM links go down,UFD disables the interfaces/LAGs configured as links-to-disable (LtD). If any of the LtM links come back up, then all the LtD links are brought back up.

    Parameters:
        name: Specific ``ufd`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ufd", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ufd`` configuration in Central.

    Uplink Failure Detection(UFD) Configurations.UFD monitors (tracks the forwarding state of) the interfaces/LAGs(Link Aggregation) configured as links-to-monitor (LtM) and when all LtM links go down,UFD disables the interfaces/LAGs configured as links-to-disable (LtD). If any of the LtM links come back up, then all the LtD links are brought back up.
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
    )
