"""Aruba Central ``Network Services`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``Network Services`` OpenAPI tag-group. Wrappers
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

# ----- dhcp-pool -----


@tool(annotations=READ_ONLY)
async def central_get_dhcp_pool(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dhcp-pool`` configurations from Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

    Parameters:
        name: Specific ``dhcp-pool`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dhcp-pool", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dhcp_pool(
    ctx: Context,
    name: Annotated[str, Field(description="``dhcp-pool`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dhcp-pool`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dhcp_pool`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dhcp-pool`` configuration in Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
    """
    return await _manage_resource(
        ctx,
        "dhcp-pool",
        "dhcp-pool",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dhcp-relay -----


@tool(annotations=READ_ONLY)
async def central_get_dhcp_relay(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dhcp-relay`` configurations from Central.

    DHCP Relay forwards DHCP requests from clients on one network segment to DHCP servers located on different network segments, enabling centralized IP address management across multiple subnets. DHCP Relay supports DHCPv4 (RFC 2131) and DHCPv6 (RFC 3315) with configurable helper addresses, Option 82 insertion for client identification, hop count control, and smart relay functionality. Configure IPv4 and IPv6 relay parameters including server addresses, source interfaces, and DHCP option handling policies. Use this API to retrieve the list of DHCP relay profiles.

    Parameters:
        name: Specific ``dhcp-relay`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dhcp-relay", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dhcp_relay(
    ctx: Context,
    name: Annotated[str, Field(description="``dhcp-relay`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dhcp-relay`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dhcp_relay`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dhcp-relay`` configuration in Central.

    DHCP Relay forwards DHCP requests from clients on one network segment to DHCP servers located on different network segments, enabling centralized IP address management across multiple subnets. DHCP Relay supports DHCPv4 (RFC 2131) and DHCPv6 (RFC 3315) with configurable helper addresses, Option 82 insertion for client identification, hop count control, and smart relay functionality. Configure IPv4 and IPv6 relay parameters including server addresses, source interfaces, and DHCP option handling policies. Use this API to retrieve the list of DHCP relay profiles.
    """
    return await _manage_resource(
        ctx,
        "dhcp-relay",
        "dhcp-relay",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dhcp-server -----


@tool(annotations=READ_ONLY)
async def central_get_dhcp_server(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dhcp-server`` configurations from Central.

    Dynamic Host Configuration Protocol server Configurations. DHCPv4 and DHCPv6 server can automatically allocate IPv4/IPv6 addresses and deliver configuration settings to client hosts. This also can be configured to provide various network information like IP addresses of DNS server address, boot-file name, vendor specific options etc.

    Parameters:
        name: Specific ``dhcp-server`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dhcp-server", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dhcp_server(
    ctx: Context,
    name: Annotated[str, Field(description="``dhcp-server`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dhcp-server`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dhcp_server`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dhcp-server`` configuration in Central.

    Dynamic Host Configuration Protocol server Configurations. DHCPv4 and DHCPv6 server can automatically allocate IPv4/IPv6 addresses and deliver configuration settings to client hosts. This also can be configured to provide various network information like IP addresses of DNS server address, boot-file name, vendor specific options etc.
    """
    return await _manage_resource(
        ctx,
        "dhcp-server",
        "dhcp-server",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dhcp-snooping -----


@tool(annotations=READ_ONLY)
async def central_get_dhcp_snooping(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dhcp-snooping`` configurations from Central.

    Configuration of DHCP-Snooping. DHCP-Snooping is a security feature to help avoid the "Denial of Service"/"man in the middle" attacks that result from unauthorized users adding a DHCP server to the network that then provides invalid configuration data to other DHCP clients on the network.

    Parameters:
        name: Specific ``dhcp-snooping`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dhcp-snooping", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dhcp_snooping(
    ctx: Context,
    name: Annotated[str, Field(description="``dhcp-snooping`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dhcp-snooping`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dhcp_snooping`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dhcp-snooping`` configuration in Central.

    Configuration of DHCP-Snooping. DHCP-Snooping is a security feature to help avoid the "Denial of Service"/"man in the middle" attacks that result from unauthorized users adding a DHCP server to the network that then provides invalid configuration data to other DHCP clients on the network.
    """
    return await _manage_resource(
        ctx,
        "dhcp-snooping",
        "dhcp-snooping",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dhcp-snooping-interface -----


@tool(annotations=READ_ONLY)
async def central_get_dhcp_snooping_interface(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dhcp-snooping-interface`` configurations from Central.

    DHCP-Snooping interface parameters.

    Parameters:
        name: Specific ``dhcp-snooping-interface`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dhcp-snooping-interface", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dhcp_snooping_interface(
    ctx: Context,
    name: Annotated[str, Field(description="``dhcp-snooping-interface`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dhcp-snooping-interface`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dhcp_snooping_interface`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dhcp-snooping-interface`` configuration in Central.

    DHCP-Snooping interface parameters.
    """
    return await _manage_resource(
        ctx,
        "dhcp-snooping-interface",
        "dhcp-snooping-interface",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dynamic-arp-inspection-interface -----


@tool(annotations=READ_ONLY)
async def central_get_dynamic_arp_inspection_interface(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dynamic-arp-inspection-interface`` configurations from Central.

    Dynamic ARP Inspection interface level configuration.

    Parameters:
        name: Specific ``dynamic-arp-inspection-interface`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dynamic-arp-inspection-interface", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dynamic_arp_inspection_interface(
    ctx: Context,
    name: Annotated[
        str, Field(description="``dynamic-arp-inspection-interface`` identifier (OpenAPI path param: ``name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dynamic-arp-inspection-interface`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dynamic_arp_inspection_interface`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dynamic-arp-inspection-interface`` configuration in Central.

    Dynamic ARP Inspection interface level configuration.
    """
    return await _manage_resource(
        ctx,
        "dynamic-arp-inspection-interface",
        "dynamic-arp-inspection-interface",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- external-storage -----


@tool(annotations=READ_ONLY)
async def central_get_external_storage(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``external-storage`` configurations from Central.

    External storage volumes accessible from the switch. The feature manages external storage volumes and make them available to system applications and protocols. The storage is used to store and retrieve data files when capacity use pattern is such that external storage is the best choice. The feature supports network attached storage as well as local external storage.

    Parameters:
        name: Specific ``external-storage`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "external-storage", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_external_storage(
    ctx: Context,
    name: Annotated[str, Field(description="``external-storage`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``external-storage`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_external_storage`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``external-storage`` configuration in Central.

    External storage volumes accessible from the switch. The feature manages external storage volumes and make them available to system applications and protocols. The storage is used to store and retrieve data files when capacity use pattern is such that external storage is the best choice. The feature supports network attached storage as well as local external storage.
    """
    return await _manage_resource(
        ctx,
        "external-storage",
        "external-storage",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ip-binding -----


@tool(annotations=READ_ONLY)
async def central_get_ip_binding(
    ctx: Context,
    ip_version_vlan_client_address: str | None = None,
) -> dict | list | str:
    """Get ``ip-binding`` configurations from Central.

    Source IP binding configuration. Add a static IPv4 or Ipv6 to MAC binding in the IP Binding database.

    Parameters:
        ip_version_vlan_client_address: Specific ``ip-binding`` identifier (OpenAPI path param: ``ip-version-vlan-client-address``). If omitted, returns all.
    """
    return await _get_resource(ctx, "source-ip-bindings", ip_version_vlan_client_address)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ip_binding(
    ctx: Context,
    ip_version_vlan_client_address: Annotated[
        str, Field(description="``ip-binding`` identifier (OpenAPI path param: ``ip-version-vlan-client-address``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ip-binding`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ip_binding`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ip-binding`` configuration in Central.

    Source IP binding configuration. Add a static IPv4 or Ipv6 to MAC binding in the IP Binding database.
    """
    return await _manage_resource(
        ctx,
        "source-ip-bindings",
        "ip-binding",
        ip_version_vlan_client_address,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ip-lockdown -----


@tool(annotations=READ_ONLY)
async def central_get_ip_lockdown(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ip-lockdown`` configurations from Central.

    IP source lockdown. IP source lockdown feature is used to prevent IP source address spoofing on a per-port basis. When dynamic IP source lockdown is enabled, IP traffic received on a port are forwarded only if IP address, VLAN, MAC address and Port matches the IP binding entry. The IP binding can either be statically configured or learnt by the DHCP Snooping feature.

    Parameters:
        name: Specific ``ip-lockdown`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ip-source-lockdown", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ip_lockdown(
    ctx: Context,
    name: Annotated[str, Field(description="``ip-lockdown`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ip-lockdown`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ip_lockdown`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ip-lockdown`` configuration in Central.

    IP source lockdown. IP source lockdown feature is used to prevent IP source address spoofing on a per-port basis. When dynamic IP source lockdown is enabled, IP traffic received on a port are forwarded only if IP address, VLAN, MAC address and Port matches the IP binding entry. The IP binding can either be statically configured or learnt by the DHCP Snooping feature.
    """
    return await _manage_resource(
        ctx,
        "ip-source-lockdown",
        "ip-lockdown",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ip-lockdown-interface -----


@tool(annotations=READ_ONLY)
async def central_get_ip_lockdown_interface(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ip-lockdown-interface`` configurations from Central.

    IP source lockdown interface configuration.

    Parameters:
        name: Specific ``ip-lockdown-interface`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ip-source-lockdown-interface", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ip_lockdown_interface(
    ctx: Context,
    name: Annotated[str, Field(description="``ip-lockdown-interface`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ip-lockdown-interface`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ip_lockdown_interface`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ip-lockdown-interface`` configuration in Central.

    IP source lockdown interface configuration.
    """
    return await _manage_resource(
        ctx,
        "ip-source-lockdown-interface",
        "ip-lockdown-interface",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ipsla -----


@tool(annotations=READ_ONLY)
async def central_get_ipsla(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ipsla`` configurations from Central.

    Internet Protocol Service Level Agreement (IPSLA) configuration. IPSLA as a feature enables measuring network performance between two nodes in a network for different service level agreement parameters such as round trip time (RTT), one way delay, jitter, reachability, packet loss, voice quality scores etc.

    Parameters:
        name: Specific ``ipsla`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ipsla", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ipsla(
    ctx: Context,
    name: Annotated[str, Field(description="``ipsla`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ipsla`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ipsla`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ipsla`` configuration in Central.

    Internet Protocol Service Level Agreement (IPSLA) configuration. IPSLA as a feature enables measuring network performance between two nodes in a network for different service level agreement parameters such as round trip time (RTT), one way delay, jitter, reachability, packet loss, voice quality scores etc.
    """
    return await _manage_resource(
        ctx,
        "ipsla",
        "ipsla",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mgmd -----


@tool(annotations=READ_ONLY)
async def central_get_mgmd(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mgmd`` configurations from Central.

    Multicast Group Membership Discovery (MGMD) manages multicast group membership using IGMP (Internet Group Management Protocol) for IPv4 and MLD (Multicast Listener Discovery) for IPv6 networks. MGMD enables efficient multicast traffic delivery by controlling group membership, reducing unnecessary flooding, and conserving network bandwidth. Configure IGMP snooping, MLD snooping, querier functionality, fast-leave processing, static groups, proxy domains, and query intervals for multicast optimization. Use this API to retrieve the list of MGMD profiles.

    Parameters:
        name: Specific ``mgmd`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mgmd-global", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_mgmd(
    ctx: Context,
    name: Annotated[str, Field(description="``mgmd`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mgmd`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mgmd`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mgmd`` configuration in Central.

    Multicast Group Membership Discovery (MGMD) manages multicast group membership using IGMP (Internet Group Management Protocol) for IPv4 and MLD (Multicast Listener Discovery) for IPv6 networks. MGMD enables efficient multicast traffic delivery by controlling group membership, reducing unnecessary flooding, and conserving network bandwidth. Configure IGMP snooping, MLD snooping, querier functionality, fast-leave processing, static groups, proxy domains, and query intervals for multicast optimization. Use this API to retrieve the list of MGMD profiles.
    """
    return await _manage_resource(
        ctx,
        "mgmd-global",
        "mgmd",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- multicast-dns -----


@tool(annotations=READ_ONLY)
async def central_get_multicast_dns(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``multicast-dns`` configurations from Central.

    Multicast DNS configuration. Multicast DNS (mDNS) gateway helps users to discover various services such as printers and Apple TV, across VLANs.

    Parameters:
        name: Specific ``multicast-dns`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "multicast-dns", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_multicast_dns(
    ctx: Context,
    name: Annotated[str, Field(description="``multicast-dns`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``multicast-dns`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_multicast_dns`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``multicast-dns`` configuration in Central.

    Multicast DNS configuration. Multicast DNS (mDNS) gateway helps users to discover various services such as printers and Apple TV, across VLANs.
    """
    return await _manage_resource(
        ctx,
        "multicast-dns",
        "multicast-dns",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- nae-lite -----


@tool(annotations=READ_ONLY)
async def central_get_nae_lite(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``nae-lite`` configurations from Central.

    NAE Lite parameters.

    Parameters:
        name: Specific ``nae-lite`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "nae-lite", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_nae_lite(
    ctx: Context,
    name: Annotated[str, Field(description="``nae-lite`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``nae-lite`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_nae_lite`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``nae-lite`` configuration in Central.

    NAE Lite parameters.
    """
    return await _manage_resource(
        ctx,
        "nae-lite",
        "nae-lite",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- nd-snooping -----


@tool(annotations=READ_ONLY)
async def central_get_nd_snooping(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``nd-snooping`` configurations from Central.

    Configuration of ND-Snooping. Enabling the ND-Snooping feature on your switches prevents ND attacks. ND-Snooping does not just snoop but also detect attacks by default. ND-Snooping drops invalid ND packets and, together with DIPLDv6, blocks data traffic from invalid hosts.

    Parameters:
        name: Specific ``nd-snooping`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "nd-snooping", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_nd_snooping(
    ctx: Context,
    name: Annotated[str, Field(description="``nd-snooping`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``nd-snooping`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_nd_snooping`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``nd-snooping`` configuration in Central.

    Configuration of ND-Snooping. Enabling the ND-Snooping feature on your switches prevents ND attacks. ND-Snooping does not just snoop but also detect attacks by default. ND-Snooping drops invalid ND packets and, together with DIPLDv6, blocks data traffic from invalid hosts.
    """
    return await _manage_resource(
        ctx,
        "nd-snooping",
        "nd-snooping",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- nd-snooping-interface -----


@tool(annotations=READ_ONLY)
async def central_get_nd_snooping_interface(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``nd-snooping-interface`` configurations from Central.

    Configuration of ND-Snooping on interface.

    Parameters:
        name: Specific ``nd-snooping-interface`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "nd-snooping-interface", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_nd_snooping_interface(
    ctx: Context,
    name: Annotated[str, Field(description="``nd-snooping-interface`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``nd-snooping-interface`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_nd_snooping_interface`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``nd-snooping-interface`` configuration in Central.

    Configuration of ND-Snooping on interface.
    """
    return await _manage_resource(
        ctx,
        "nd-snooping-interface",
        "nd-snooping-interface",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ptp -----


@tool(annotations=READ_ONLY)
async def central_get_ptp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ptp`` configurations from Central.

    Precision Time Protocol (PTP) is defined in the IEEE 1588 standard. Standard for a Precision Clock Synchronization Protocol for Networked Measurement and Control Systems.

    Parameters:
        name: Specific ``ptp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ptp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ptp(
    ctx: Context,
    name: Annotated[str, Field(description="``ptp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ptp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ptp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ptp`` configuration in Central.

    Precision Time Protocol (PTP) is defined in the IEEE 1588 standard. Standard for a Precision Clock Synchronization Protocol for Networked Measurement and Control Systems.
    """
    return await _manage_resource(
        ctx,
        "ptp",
        "ptp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- qos-global -----


@tool(annotations=READ_ONLY)
async def central_get_qos_global(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``qos-global`` configurations from Central.

    Global QoS configuration.

    Parameters:
        name: Specific ``qos-global`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "qos-global", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_qos_global(
    ctx: Context,
    name: Annotated[str, Field(description="``qos-global`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``qos-global`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_qos_global`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``qos-global`` configuration in Central.

    Global QoS configuration.
    """
    return await _manage_resource(
        ctx,
        "qos-global",
        "qos-global",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- qos-queue -----


@tool(annotations=READ_ONLY)
async def central_get_qos_queue(
    ctx: Context,
    q_profile_name: str | None = None,
) -> dict | list | str:
    """Get ``qos-queue`` configurations from Central.

    QoS queue parameters.

    Parameters:
        q_profile_name: Specific ``qos-queue`` identifier (OpenAPI path param: ``q-profile-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "qos-queues", q_profile_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_qos_queue(
    ctx: Context,
    q_profile_name: Annotated[
        str, Field(description="``qos-queue`` identifier (OpenAPI path param: ``q-profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``qos-queue`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_qos_queue`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``qos-queue`` configuration in Central.

    QoS queue parameters.
    """
    return await _manage_resource(
        ctx,
        "qos-queues",
        "qos-queue",
        q_profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- qos-schedule -----


@tool(annotations=READ_ONLY)
async def central_get_qos_schedule(
    ctx: Context,
    sched_profile_name: str | None = None,
) -> dict | list | str:
    """Get ``qos-schedule`` configurations from Central.

    QoS schedule parameters.

    Parameters:
        sched_profile_name: Specific ``qos-schedule`` identifier (OpenAPI path param: ``sched-profile-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "qos-schedules", sched_profile_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_qos_schedule(
    ctx: Context,
    sched_profile_name: Annotated[
        str, Field(description="``qos-schedule`` identifier (OpenAPI path param: ``sched-profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``qos-schedule`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_qos_schedule`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``qos-schedule`` configuration in Central.

    QoS schedule parameters.
    """
    return await _manage_resource(
        ctx,
        "qos-schedules",
        "qos-schedule",
        sched_profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- qos-threshold-profile -----


@tool(annotations=READ_ONLY)
async def central_get_qos_threshold_profile(
    ctx: Context,
    thresh_profile_name: str | None = None,
) -> dict | list | str:
    """Get ``qos-threshold-profile`` configurations from Central.

    QoS threshold profile parameters.

    Parameters:
        thresh_profile_name: Specific ``qos-threshold-profile`` identifier (OpenAPI path param: ``thresh-profile-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "qos-thresholds", thresh_profile_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_qos_threshold_profile(
    ctx: Context,
    thresh_profile_name: Annotated[
        str, Field(description="``qos-threshold-profile`` identifier (OpenAPI path param: ``thresh-profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``qos-threshold-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_qos_threshold_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``qos-threshold-profile`` configuration in Central.

    QoS threshold profile parameters.
    """
    return await _manage_resource(
        ctx,
        "qos-thresholds",
        "qos-threshold-profile",
        thresh_profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- udp-broadcast-forwarder -----


@tool(annotations=READ_ONLY)
async def central_get_udp_broadcast_forwarder(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``udp-broadcast-forwarder`` configurations from Central.

    Configure UDP Broadcast Forwarder globally. The routers by default do not forward broadcast packets. However, there are situations where it is desirable to forward certain broadcast packets. The UDP (User Datagram Protocol) broadcast forwarder takes the client's UDP broadcast packets and forwards to the configured server(s) in a different subnet. UDP broadcast forwarding is supported only for IPv4 addresses.

    Parameters:
        name: Specific ``udp-broadcast-forwarder`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "udp-broadcast-forwarders", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_udp_broadcast_forwarder(
    ctx: Context,
    name: Annotated[str, Field(description="``udp-broadcast-forwarder`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``udp-broadcast-forwarder`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_udp_broadcast_forwarder`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``udp-broadcast-forwarder`` configuration in Central.

    Configure UDP Broadcast Forwarder globally. The routers by default do not forward broadcast packets. However, there are situations where it is desirable to forward certain broadcast packets. The UDP (User Datagram Protocol) broadcast forwarder takes the client's UDP broadcast packets and forwards to the configured server(s) in a different subnet. UDP broadcast forwarding is supported only for IPv4 addresses.
    """
    return await _manage_resource(
        ctx,
        "udp-broadcast-forwarders",
        "udp-broadcast-forwarder",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
