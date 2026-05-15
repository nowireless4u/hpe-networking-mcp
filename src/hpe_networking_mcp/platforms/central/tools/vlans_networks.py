"""Aruba Central ``VLANs & Networks`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``VLANs & Networks`` OpenAPI tag-group. Wrappers
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


# ----- gw-stp -----


@tool(annotations=READ_ONLY)
async def central_get_gw_stp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``gw-stp`` configurations from Central.

    Spanning Tree Protocol (STP) prevents network loops and ensures redundant path management in Layer 2 switched networks per IEEE 802.1D/802.1w standards. This module configures RSTP (Rapid Spanning Tree Protocol) and RPVST (Rapid Per-VLAN Spanning Tree) for Gateway devices. Configure global STP parameters including bridge priority, timers (hello-time, forward-delay, max-age), and per-VLAN RPVST instances. Use this API to retrieve the list of Spanning Tree profiles.

    Parameters:
        name: Specific ``gw-stp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "stp-gw", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_gw_stp(
    ctx: Context,
    name: Annotated[str, Field(description="``gw-stp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``gw-stp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_gw_stp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``gw-stp`` configuration in Central.

    Spanning Tree Protocol (STP) prevents network loops and ensures redundant path management in Layer 2 switched networks per IEEE 802.1D/802.1w standards. This module configures RSTP (Rapid Spanning Tree Protocol) and RPVST (Rapid Per-VLAN Spanning Tree) for Gateway devices. Configure global STP parameters including bridge priority, timers (hello-time, forward-delay, max-age), and per-VLAN RPVST instances. Use this API to retrieve the list of Spanning Tree profiles.
    """
    return await _manage_resource(
        ctx,
        "stp-gw",
        "gw-stp",
        name,
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

    Loop protect is a layer 2 mechanism that detects and prevents network loops, primarily in scenarios where the spanning tree protocol (STP) might be ineffective, such as edge ports connected to unmanaged devices or client-authenticated ports. Loop-protect configuration through this API is deprecated. Use API from aruba-switch-system:switch-system/profile/loop-protect instead.

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

    Loop protect is a layer 2 mechanism that detects and prevents network loops, primarily in scenarios where the spanning tree protocol (STP) might be ineffective, such as edge ports connected to unmanaged devices or client-authenticated ports. Loop-protect configuration through this API is deprecated. Use API from aruba-switch-system:switch-system/profile/loop-protect instead.
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

    MVRP(Multiple VLAN Registration Protocol) configuration.MVRP provides a mechanism to dynamically share VLAN configuration information across layer 2 switches on a network. MVRP eliminates the need to manually configure VLANs on each switch.

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

    MVRP(Multiple VLAN Registration Protocol) configuration.MVRP provides a mechanism to dynamically share VLAN configuration information across layer 2 switches on a network. MVRP eliminates the need to manually configure VLANs on each switch.
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


# ----- smartlink -----


@tool(annotations=READ_ONLY)
async def central_get_smartlink(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``smartlink`` configurations from Central.

    Smartlink configuration.Smartlink provides simple and fast-converging link redundancy in network topologies with dual uplink between different layers of the network. It requires an active (primary) and backup (secondary) link. The active link carries the traffic. If the active link fails, a switchover is triggered and the traffic is directed to the backup link.

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

    Smartlink configuration.Smartlink provides simple and fast-converging link redundancy in network topologies with dual uplink between different layers of the network. It requires an active (primary) and backup (secondary) link. The active link carries the traffic. If the active link fails, a switchover is triggered and the traffic is directed to the backup link.
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

    Static neighbor configuration.

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

    Static neighbor configuration.
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

    STP(Spanning tree protocol) configuration. STP is a network protocol that prevents layer 2 loops and broadcast storms in Ethernet networks.It does this by selectively blocking some ports and allowing others to forward traffic.

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

    STP(Spanning tree protocol) configuration. STP is a network protocol that prevents layer 2 loops and broadcast storms in Ethernet networks.It does this by selectively blocking some ports and allowing others to forward traffic.
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


# ----- vlan -----


@tool(annotations=READ_ONLY)
async def central_get_vlan(
    ctx: Context,
    vlan: str | None = None,
) -> dict | list | str:
    """Get ``vlan`` configurations from Central.

    Configure and manage L2 VLAN profiles. Each VLAN profile maps to each layer2 VLAN ID. Using this profile features related to layer 2 VLAN can be configured like wired AAA profile for VLANs. VLANs are primarily used to provide network segmentation at layer 2. VLANs enable the grouping of users by logical function instead of physical location. VLANs are generally assigned on an organizational basis rather than on a physical basis. For example, a network administrator could assign all workstations and servers used by a particular workgroup to the same VLAN, regardless of their physical locations. Hosts in the same VLAN can directly communicate with one another. A router or a Layer 3 switch is required for hosts in different VLANs to communicate with one another. VLANs help reduce bandwidth waste, improve LAN security, and enable network administrators to address issues such as scalability and network management.

    Parameters:
        vlan: Specific ``vlan`` identifier (OpenAPI path param: ``vlan``). If omitted, returns all.
    """
    return await _get_resource(ctx, "layer2-vlan", vlan)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vlan(
    ctx: Context,
    vlan: Annotated[str, Field(description="``vlan`` identifier (OpenAPI path param: ``vlan``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vlan`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vlan`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vlan`` configuration in Central.

    Configure and manage L2 VLAN profiles. Each VLAN profile maps to each layer2 VLAN ID. Using this profile features related to layer 2 VLAN can be configured like wired AAA profile for VLANs. VLANs are primarily used to provide network segmentation at layer 2. VLANs enable the grouping of users by logical function instead of physical location. VLANs are generally assigned on an organizational basis rather than on a physical basis. For example, a network administrator could assign all workstations and servers used by a particular workgroup to the same VLAN, regardless of their physical locations. Hosts in the same VLAN can directly communicate with one another. A router or a Layer 3 switch is required for hosts in different VLANs to communicate with one another. VLANs help reduce bandwidth waste, improve LAN security, and enable network administrators to address issues such as scalability and network management.
    """
    return await _manage_resource(
        ctx,
        "layer2-vlan",
        "vlan",
        vlan,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vlan-range -----


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vlan_range(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``vlan-range`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vlan_range`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``vlan-range`` configuration in Central.

    aruba-vlan-range API generated from aruba-vlan-range.yang.
    """
    return await _manage_resource(
        ctx,
        "layer2-vlan-range",
        "vlan-range",
        None,
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

    Virtual Router Redundancy Protocol (VRRP) Configurations. VRRP specifies an election protocol to provide the virtual router function described below. All protocol messaging is performed using IP multicast datagrams, thus the protocol can operate over a variety of multiaccess LAN technologies supporting IP multicast. The virtual router MAC address is used as the source in all periodic VRRP messages sent by the Active router to enable bridge learning in an extended LAN. A virtual router is defined by its virtual router identifier (VRID) and a set of IP addresses. A VRRP router may associate a virtual router with its real addresses on an interface, and may also be configured with additional virtual router mappings and priority for virtual routers it is willing to standby. A Standby router will not attempt to preempt the Active unless it has higher priority. This eliminates service disruption unless a more preferred path becomes available. It is also possible to administratively prohibit all preemption attempts. The only exception is that a VRRP router will always become Active of any virtual router associated with addresses it owns. If the Active becomes unavailable then the highest priority Standby will transition to Active after a short delay, providing a controlled transition of the virtual router responsibility with minimal service interruption. AOS-CX : VRRP can be configured on physical ports, VLAN interfaces and LAG interfaces. All such configurations work in the mentioned interfaces context. VRRP mandates the associated interface to be routing interface.

    Parameters:
        name: Specific ``vrrp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vrrp-global", name)


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

    Virtual Router Redundancy Protocol (VRRP) Configurations. VRRP specifies an election protocol to provide the virtual router function described below. All protocol messaging is performed using IP multicast datagrams, thus the protocol can operate over a variety of multiaccess LAN technologies supporting IP multicast. The virtual router MAC address is used as the source in all periodic VRRP messages sent by the Active router to enable bridge learning in an extended LAN. A virtual router is defined by its virtual router identifier (VRID) and a set of IP addresses. A VRRP router may associate a virtual router with its real addresses on an interface, and may also be configured with additional virtual router mappings and priority for virtual routers it is willing to standby. A Standby router will not attempt to preempt the Active unless it has higher priority. This eliminates service disruption unless a more preferred path becomes available. It is also possible to administratively prohibit all preemption attempts. The only exception is that a VRRP router will always become Active of any virtual router associated with addresses it owns. If the Active becomes unavailable then the highest priority Standby will transition to Active after a short delay, providing a controlled transition of the virtual router responsibility with minimal service interruption. AOS-CX : VRRP can be configured on physical ports, VLAN interfaces and LAG interfaces. All such configurations work in the mentioned interfaces context. VRRP mandates the associated interface to be routing interface.
    """
    return await _manage_resource(
        ctx,
        "vrrp-global",
        "vrrp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vrrp-interface -----


@tool(annotations=READ_ONLY)
async def central_get_vrrp_interface(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vrrp-interface`` configurations from Central.

    Virtual Router Redundancy Protocol (VRRP) Interface Configurations. Upon configuration, this profile is to be referenced from either a VLAN profile or a port profile. VRRP specifies an election protocol to provide the virtual router function described below. All protocol messaging is performed using IP multicast datagrams, thus the protocol can operate over a variety of multiaccess LAN technologies supporting IP multicast. The virtual router MAC address is used as the source in all periodic VRRP messages sent by the Active router to enable bridge learning in an extended LAN. A virtual router is defined by its virtual router identifier (VRID) and a set of IP addresses. A VRRP router may associate a virtual router with its real addresses on an interface, and may also be configured with additional virtual router mappings and priority for virtual routers it is willing to standby. A Standby router will not attempt to preempt the Active unless it has higher priority. This eliminates service disruption unless a more preferred path becomes available. It is also possible to administratively prohibit all preemption attempts. The only exception is that a VRRP router will always become Active of any virtual router associated with addresses it owns. If the Active becomes unavailable then the highest priority Standby will transition to Active after a short delay, providing a controlled transition of the virtual router responsibility with minimal service interruption. AOS-CX : VRRP can be configured on physical ports, VLAN interfaces and LAG interfaces. All such configurations work in the mentioned interfaces context. VRRP mandates the associated interface to be routing interface.

    Parameters:
        name: Specific ``vrrp-interface`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vrrp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vrrp_interface(
    ctx: Context,
    name: Annotated[str, Field(description="``vrrp-interface`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vrrp-interface`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vrrp_interface`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vrrp-interface`` configuration in Central.

    Virtual Router Redundancy Protocol (VRRP) Interface Configurations. Upon configuration, this profile is to be referenced from either a VLAN profile or a port profile. VRRP specifies an election protocol to provide the virtual router function described below. All protocol messaging is performed using IP multicast datagrams, thus the protocol can operate over a variety of multiaccess LAN technologies supporting IP multicast. The virtual router MAC address is used as the source in all periodic VRRP messages sent by the Active router to enable bridge learning in an extended LAN. A virtual router is defined by its virtual router identifier (VRID) and a set of IP addresses. A VRRP router may associate a virtual router with its real addresses on an interface, and may also be configured with additional virtual router mappings and priority for virtual routers it is willing to standby. A Standby router will not attempt to preempt the Active unless it has higher priority. This eliminates service disruption unless a more preferred path becomes available. It is also possible to administratively prohibit all preemption attempts. The only exception is that a VRRP router will always become Active of any virtual router associated with addresses it owns. If the Active becomes unavailable then the highest priority Standby will transition to Active after a short delay, providing a controlled transition of the virtual router responsibility with minimal service interruption. AOS-CX : VRRP can be configured on physical ports, VLAN interfaces and LAG interfaces. All such configurations work in the mentioned interfaces context. VRRP mandates the associated interface to be routing interface.
    """
    return await _manage_resource(
        ctx,
        "vrrp",
        "vrrp-interface",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
