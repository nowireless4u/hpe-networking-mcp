"""Aruba Central ``Routing & Overlays`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``Routing & Overlays`` OpenAPI tag-group. Wrappers
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

# ----- advanced-intelligent-forwarding -----


@tool(annotations=READ_ONLY)
async def central_get_advanced_intelligent_forwarding(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``advanced-intelligent-forwarding`` configurations from Central.

    Container for all AIF configurations.

    Parameters:
        name: Specific ``advanced-intelligent-forwarding`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "advanced-intelligent-forwarding", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_advanced_intelligent_forwarding(
    ctx: Context,
    name: Annotated[
        str, Field(description="``advanced-intelligent-forwarding`` identifier (OpenAPI path param: ``name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``advanced-intelligent-forwarding`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_advanced_intelligent_forwarding`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``advanced-intelligent-forwarding`` configuration in Central.

    Container for all AIF configurations.
    """
    return await _manage_resource(
        ctx,
        "advanced-intelligent-forwarding",
        "advanced-intelligent-forwarding",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- aspath-list -----


@tool(annotations=READ_ONLY)
async def central_get_aspath_list(
    ctx: Context,
    aspath_list_name: str | None = None,
) -> dict | list | str:
    """Get ``aspath-list`` configurations from Central.

    AS Path Lists configuration. The AS Path is the sequence of Autonomous System numbers traversed by a BGP route announcement. This container manages AS Path Lists for filtering and controlling BGP routes based on path characteristics using permit/deny actions and regular expression patterns.

    Parameters:
        aspath_list_name: Specific ``aspath-list`` identifier (OpenAPI path param: ``aspath-list-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "aspath-lists", aspath_list_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_aspath_list(
    ctx: Context,
    aspath_list_name: Annotated[
        str, Field(description="``aspath-list`` identifier (OpenAPI path param: ``aspath-list-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``aspath-list`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_aspath_list`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``aspath-list`` configuration in Central.

    AS Path Lists configuration. The AS Path is the sequence of Autonomous System numbers traversed by a BGP route announcement. This container manages AS Path Lists for filtering and controlling BGP routes based on path characteristics using permit/deny actions and regular expression patterns.
    """
    return await _manage_resource(
        ctx,
        "aspath-lists",
        "aspath-list",
        aspath_list_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- bfd -----


@tool(annotations=READ_ONLY)
async def central_get_bfd(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``bfd`` configurations from Central.

    BFD global configuration. Bidirectional Forwarding Detection (BFD) is a protocol intended to detect faults in the bidirectional path between two forwarding engines, including interfaces, data link(s), and to the extent possible the forwarding engines themselves, with potentially very low latency. It operates independently of media, data protocols, and routing protocols.

    Parameters:
        name: Specific ``bfd`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "bfd", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_bfd(
    ctx: Context,
    name: Annotated[str, Field(description="``bfd`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``bfd`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_bfd`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``bfd`` configuration in Central.

    BFD global configuration. Bidirectional Forwarding Detection (BFD) is a protocol intended to detect faults in the bidirectional path between two forwarding engines, including interfaces, data link(s), and to the extent possible the forwarding engines themselves, with potentially very low latency. It operates independently of media, data protocols, and routing protocols.
    """
    return await _manage_resource(
        ctx,
        "bfd",
        "bfd",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- bgp -----


@tool(annotations=READ_ONLY)
async def central_get_bgp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``bgp`` configurations from Central.

    Border Gateway Protocol (BGP) is the standard exterior gateway protocol (RFC 4271) for exchanging routing information between autonomous systems on the Internet and enterprise networks. BGP supports IPv4/IPv6 unicast, EVPN (Ethernet VPN), and multicast address families with advanced features including route reflection, confederation, graceful restart, and multi-path load balancing. Configure BGP global parameters, neighbor relationships, route redistribution, and address family-specific policies. Requires route map, prefix list, keychain, and community list configurations for routing policy enforcement. Use this API to retrieve BGP configuration.

    Parameters:
        name: Specific ``bgp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "bgp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_bgp(
    ctx: Context,
    name: Annotated[str, Field(description="``bgp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``bgp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_bgp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``bgp`` configuration in Central.

    Border Gateway Protocol (BGP) is the standard exterior gateway protocol (RFC 4271) for exchanging routing information between autonomous systems on the Internet and enterprise networks. BGP supports IPv4/IPv6 unicast, EVPN (Ethernet VPN), and multicast address families with advanced features including route reflection, confederation, graceful restart, and multi-path load balancing. Configure BGP global parameters, neighbor relationships, route redistribution, and address family-specific policies. Requires route map, prefix list, keychain, and community list configurations for routing policy enforcement. Use this API to retrieve BGP configuration.
    """
    return await _manage_resource(
        ctx,
        "bgp",
        "bgp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- community-list -----


@tool(annotations=READ_ONLY)
async def central_get_community_list(
    ctx: Context,
    community_list_name_community_type: str | None = None,
) -> dict | list | str:
    """Get ``community-list`` configurations from Central.

    BGP Community Lists configuration. A BGP Community is a 32-bit value used to classify and group routes for policy application. This container manages three types of Community Lists: Standard (specific community values), Expanded (regular expression patterns), and Extended (route targets and extended community formats). Each list contains ordered entries with permit or deny actions for route classification and policy enforcement.

    Parameters:
        community_list_name_community_type: Specific ``community-list`` identifier (OpenAPI path param: ``community-list-name-community-type``). If omitted, returns all.
    """
    return await _get_resource(ctx, "community-lists", community_list_name_community_type)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_community_list(
    ctx: Context,
    community_list_name_community_type: Annotated[
        str,
        Field(
            description="``community-list`` identifier (OpenAPI path param: ``community-list-name-community-type``)."
        ),
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``community-list`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_community_list`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``community-list`` configuration in Central.

    BGP Community Lists configuration. A BGP Community is a 32-bit value used to classify and group routes for policy application. This container manages three types of Community Lists: Standard (specific community values), Expanded (regular expression patterns), and Extended (route targets and extended community formats). Each list contains ordered entries with permit or deny actions for route classification and policy enforcement.
    """
    return await _manage_resource(
        ctx,
        "community-lists",
        "community-list",
        community_list_name_community_type,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- evpn -----


@tool(annotations=READ_ONLY)
async def central_get_evpn(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``evpn`` configurations from Central.

    Ethernet Virtual Private Network (EVPN) container. EVPN provides Layer 2 and Layer 3 VPN services using BGP control plane and VXLAN/MPLS data plane encapsulation for seamless multi-site connectivity.

    Parameters:
        name: Specific ``evpn`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "evpn", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_evpn(
    ctx: Context,
    name: Annotated[str, Field(description="``evpn`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``evpn`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_evpn`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``evpn`` configuration in Central.

    Ethernet Virtual Private Network (EVPN) container. EVPN provides Layer 2 and Layer 3 VPN services using BGP control plane and VXLAN/MPLS data plane encapsulation for seamless multi-site connectivity.
    """
    return await _manage_resource(
        ctx,
        "evpn",
        "evpn",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ip-routing -----


@tool(annotations=READ_ONLY)
async def central_get_ip_routing(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ip-routing`` configurations from Central.

    IP routing configuration.

    Parameters:
        name: Specific ``ip-routing`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ip-routing", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ip_routing(
    ctx: Context,
    name: Annotated[str, Field(description="``ip-routing`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ip-routing`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ip_routing`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ip-routing`` configuration in Central.

    IP routing configuration.
    """
    return await _manage_resource(
        ctx,
        "ip-routing",
        "ip-routing",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- l3-route -----


@tool(annotations=READ_ONLY)
async def central_get_l3_route(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``l3-route`` configurations from Central.

    L3 route.

    Parameters:
        name: Specific ``l3-route`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "l3-route", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_l3_route(
    ctx: Context,
    name: Annotated[str, Field(description="``l3-route`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``l3-route`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_l3_route`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``l3-route`` configuration in Central.

    L3 route.
    """
    return await _manage_resource(
        ctx,
        "l3-route",
        "l3-route",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mpls -----


@tool(annotations=READ_ONLY)
async def central_get_mpls(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mpls`` configurations from Central.

    MPLS global configuration.

    Parameters:
        name: Specific ``mpls`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mpls", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_mpls(
    ctx: Context,
    name: Annotated[str, Field(description="``mpls`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mpls`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mpls`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mpls`` configuration in Central.

    MPLS global configuration.
    """
    return await _manage_resource(
        ctx,
        "mpls",
        "mpls",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- msdp -----


@tool(annotations=READ_ONLY)
async def central_get_msdp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``msdp`` configurations from Central.

    Multicast Source Discovery Protocol Router configurations. When MSDP is configured in a network, Rendezvous Points(RP) running MSDP exchange source information with MSDP enabled RPs in other domains. An RP can join the interdomain source tree for sources that are sending to groups for which it has multicast receivers.

    Parameters:
        name: Specific ``msdp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "msdp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_msdp(
    ctx: Context,
    name: Annotated[str, Field(description="``msdp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``msdp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_msdp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``msdp`` configuration in Central.

    Multicast Source Discovery Protocol Router configurations. When MSDP is configured in a network, Rendezvous Points(RP) running MSDP exchange source information with MSDP enabled RPs in other domains. An RP can join the interdomain source tree for sources that are sending to groups for which it has multicast receivers.
    """
    return await _manage_resource(
        ctx,
        "msdp",
        "msdp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- multicast -----


@tool(annotations=READ_ONLY)
async def central_get_multicast(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``multicast`` configurations from Central.

    Multicast Global Configurations.

    Parameters:
        name: Specific ``multicast`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "multicast-global", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_multicast(
    ctx: Context,
    name: Annotated[str, Field(description="``multicast`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``multicast`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_multicast`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``multicast`` configuration in Central.

    Multicast Global Configurations.
    """
    return await _manage_resource(
        ctx,
        "multicast-global",
        "multicast",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- multicast-static-route -----


@tool(annotations=READ_ONLY)
async def central_get_multicast_static_route(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``multicast-static-route`` configurations from Central.

    Multicast Static Route configuration. Multicast static routes are used to configure a static multicast flow and program it directly into the IP multicast forwarding table instead of learning multicast routes using dynamic multicast protocols.

    Parameters:
        name: Specific ``multicast-static-route`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "multicast-static-route", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_multicast_static_route(
    ctx: Context,
    name: Annotated[str, Field(description="``multicast-static-route`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``multicast-static-route`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_multicast_static_route`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``multicast-static-route`` configuration in Central.

    Multicast Static Route configuration. Multicast static routes are used to configure a static multicast flow and program it directly into the IP multicast forwarding table instead of learning multicast routes using dynamic multicast protocols.
    """
    return await _manage_resource(
        ctx,
        "multicast-static-route",
        "multicast-static-route",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- nexthop-group -----


@tool(annotations=READ_ONLY)
async def central_get_nexthop_group(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``nexthop-group`` configurations from Central.

    Nexthop groups.

    Parameters:
        name: Specific ``nexthop-group`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "nexthop-groups", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_nexthop_group(
    ctx: Context,
    name: Annotated[str, Field(description="``nexthop-group`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``nexthop-group`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_nexthop_group`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``nexthop-group`` configuration in Central.

    Nexthop groups.
    """
    return await _manage_resource(
        ctx,
        "nexthop-groups",
        "nexthop-group",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ospfv2 -----


@tool(annotations=READ_ONLY)
async def central_get_ospfv2(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ospfv2`` configurations from Central.

    OSPFv2 (Open Shortest Path First version 2) is a routing protocol which is described in RFC2328 entitled OSPF Version 2. It is a Link State-based IGP(Interior Gateway Protocol) routing protocol. It is widely used in medium to large-sized enterprise networks. The characteristics of OSPFv2 are: - Provides a loop free topology using SPF algorithm. - Allows hierarchical routing using area 0 (backbone area) as the top of the hierarchy. - Supports load balancing with equal cost routes for same destination. - OSPFv2 is a classless protocol and allows for a hierarchical design with VLSM(Variable length subnet masking) and route summarization. - Provides authentication of routing messages. - Scales enterprise size network easily with area concept. - Provides fast convergence with triggered, incremental updates via Link State Advertisements (LSAs).

    Parameters:
        name: Specific ``ospfv2`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ospfv2", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ospfv2(
    ctx: Context,
    name: Annotated[str, Field(description="``ospfv2`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ospfv2`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ospfv2`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ospfv2`` configuration in Central.

    OSPFv2 (Open Shortest Path First version 2) is a routing protocol which is described in RFC2328 entitled OSPF Version 2. It is a Link State-based IGP(Interior Gateway Protocol) routing protocol. It is widely used in medium to large-sized enterprise networks. The characteristics of OSPFv2 are: - Provides a loop free topology using SPF algorithm. - Allows hierarchical routing using area 0 (backbone area) as the top of the hierarchy. - Supports load balancing with equal cost routes for same destination. - OSPFv2 is a classless protocol and allows for a hierarchical design with VLSM(Variable length subnet masking) and route summarization. - Provides authentication of routing messages. - Scales enterprise size network easily with area concept. - Provides fast convergence with triggered, incremental updates via Link State Advertisements (LSAs).
    """
    return await _manage_resource(
        ctx,
        "ospfv2",
        "ospfv2",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ospfv3 -----


@tool(annotations=READ_ONLY)
async def central_get_ospfv3(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ospfv3`` configurations from Central.

    OSPFv3 (Open Shortest Path First version 3) is a routing protocol which is described in RFC5340 entitled OSPF for IPv6. It is a Link State-based IGP (Interior Gateway Protocol) routing protocol. It is widely used with medium to large-sized enterprise networks. The characteristics of OSPFv3 are: - Provides a loop free topology using SPF algorithm. - Allows hierarchical routing using area 0 (backbone area) as the top of the hierarchy. - Supports load balancing with equal cost routes for same destination. - OSPFv3 is a classless protocol and allows for a hierarchical design with VLSM (Variable Length Subnet Masking) and route summarization. - Scales enterprise size network easily with area concept. - Provides fast convergence with triggered, incremental updates via Link State Advertisements (LSAs).

    Parameters:
        name: Specific ``ospfv3`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ospfv3", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ospfv3(
    ctx: Context,
    name: Annotated[str, Field(description="``ospfv3`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ospfv3`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ospfv3`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ospfv3`` configuration in Central.

    OSPFv3 (Open Shortest Path First version 3) is a routing protocol which is described in RFC5340 entitled OSPF for IPv6. It is a Link State-based IGP (Interior Gateway Protocol) routing protocol. It is widely used with medium to large-sized enterprise networks. The characteristics of OSPFv3 are: - Provides a loop free topology using SPF algorithm. - Allows hierarchical routing using area 0 (backbone area) as the top of the hierarchy. - Supports load balancing with equal cost routes for same destination. - OSPFv3 is a classless protocol and allows for a hierarchical design with VLSM (Variable Length Subnet Masking) and route summarization. - Scales enterprise size network easily with area concept. - Provides fast convergence with triggered, incremental updates via Link State Advertisements (LSAs).
    """
    return await _manage_resource(
        ctx,
        "ospfv3",
        "ospfv3",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- pim -----


@tool(annotations=READ_ONLY)
async def central_get_pim(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``pim`` configurations from Central.

    Configure Protocol Independent Multicast. In a network, IP multicast traffic transmitted for multimedia applications is blocked at routed interface boundaries unless a multicast routing protocol is running. Protocol Independent Multicast (PIM) is a family of routing protocols. It forms multicast trees to forward traffic from multicast sources to the clients requesting for traffic.

    Parameters:
        name: Specific ``pim`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "pim-router", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_pim(
    ctx: Context,
    name: Annotated[str, Field(description="``pim`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``pim`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_pim`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``pim`` configuration in Central.

    Configure Protocol Independent Multicast. In a network, IP multicast traffic transmitted for multimedia applications is blocked at routed interface boundaries unless a multicast routing protocol is running. Protocol Independent Multicast (PIM) is a family of routing protocols. It forms multicast trees to forward traffic from multicast sources to the clients requesting for traffic.
    """
    return await _manage_resource(
        ctx,
        "pim-router",
        "pim",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- prefix-list -----


@tool(annotations=READ_ONLY)
async def central_get_prefix_list(
    ctx: Context,
    prefix_list_name_address_family: str | None = None,
) -> dict | list | str:
    """Get ``prefix-list`` configurations from Central.

    Prefix Lists are standard routing filters (RFC 4632) used to permit or deny network routes based on IP address prefixes in CIDR notation. Configure IPv4 and IPv6 prefix lists for granular route control in BGP and OSPF routing policies. Each list contains sequential entries with permit/deny actions and optional prefix length matching constraints for flexible route filtering across multi-site networks. Device Limits: Gateway restricts prefix list names to 1-50 characters. Use this API to retrieve the list of prefix list configurations.

    Parameters:
        prefix_list_name_address_family: Specific ``prefix-list`` identifier (OpenAPI path param: ``prefix-list-name-address-family``). If omitted, returns all.
    """
    return await _get_resource(ctx, "prefix-lists", prefix_list_name_address_family)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_prefix_list(
    ctx: Context,
    prefix_list_name_address_family: Annotated[
        str, Field(description="``prefix-list`` identifier (OpenAPI path param: ``prefix-list-name-address-family``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``prefix-list`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_prefix_list`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``prefix-list`` configuration in Central.

    Prefix Lists are standard routing filters (RFC 4632) used to permit or deny network routes based on IP address prefixes in CIDR notation. Configure IPv4 and IPv6 prefix lists for granular route control in BGP and OSPF routing policies. Each list contains sequential entries with permit/deny actions and optional prefix length matching constraints for flexible route filtering across multi-site networks. Device Limits: Gateway restricts prefix list names to 1-50 characters. Use this API to retrieve the list of prefix list configurations.
    """
    return await _manage_resource(
        ctx,
        "prefix-lists",
        "prefix-list",
        prefix_list_name_address_family,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- rip -----


@tool(annotations=READ_ONLY)
async def central_get_rip(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``rip`` configurations from Central.

    Routing Information Protocol (RIP) is a distance-vector interior gateway protocol (IGP) using hop count as the routing metric with a maximum of 15 hops (RFC 2453). RIP supports RIPv1 and RIPv2 for IPv4 networks with features including route redistribution, authentication, route filtering, and configurable timers. Configure RIP router instances with administrative distance, maximum paths, timers (update, timeout, garbage-collection), route redistribution from other protocols, and interface-specific parameters. Use this API to retrieve the list of RIP profiles.

    Parameters:
        name: Specific ``rip`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "rip", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_rip(
    ctx: Context,
    name: Annotated[str, Field(description="``rip`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``rip`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_rip`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``rip`` configuration in Central.

    Routing Information Protocol (RIP) is a distance-vector interior gateway protocol (IGP) using hop count as the routing metric with a maximum of 15 hops (RFC 2453). RIP supports RIPv1 and RIPv2 for IPv4 networks with features including route redistribution, authentication, route filtering, and configurable timers. Configure RIP router instances with administrative distance, maximum paths, timers (update, timeout, garbage-collection), route redistribution from other protocols, and interface-specific parameters. Use this API to retrieve the list of RIP profiles.
    """
    return await _manage_resource(
        ctx,
        "rip",
        "rip",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- routemap -----


@tool(annotations=READ_ONLY)
async def central_get_routemap(
    ctx: Context,
    route_map_name: str | None = None,
) -> dict | list | str:
    """Get ``routemap`` configurations from Central.

    Route Maps provide advanced routing policy control by manipulating route attributes during redistribution between routing protocols (BGP, OSPF, RIP, static routes). Route maps use match conditions (IP prefix lists, community lists, AS path lists) and set actions (metric modification, next-hop changes, AS path prepending) to filter and transform routing information. Configure route map sequences with permit/deny actions to implement complex routing policies for traffic engineering and route aggregation. Requires prefix-list, community-list, and AS path-list configurations for match conditions. Device Limits: Gateway restricts route map names to 1-50 characters. Use this API to retrieve the list of route map configurations.

    Parameters:
        route_map_name: Specific ``routemap`` identifier (OpenAPI path param: ``route-map-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "route-maps", route_map_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_routemap(
    ctx: Context,
    route_map_name: Annotated[
        str, Field(description="``routemap`` identifier (OpenAPI path param: ``route-map-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``routemap`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_routemap`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``routemap`` configuration in Central.

    Route Maps provide advanced routing policy control by manipulating route attributes during redistribution between routing protocols (BGP, OSPF, RIP, static routes). Route maps use match conditions (IP prefix lists, community lists, AS path lists) and set actions (metric modification, next-hop changes, AS path prepending) to filter and transform routing information. Configure route map sequences with permit/deny actions to implement complex routing policies for traffic engineering and route aggregation. Requires prefix-list, community-list, and AS path-list configurations for match conditions. Device Limits: Gateway restricts route map names to 1-50 characters. Use this API to retrieve the list of route map configurations.
    """
    return await _manage_resource(
        ctx,
        "route-maps",
        "routemap",
        route_map_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- static-route -----


@tool(annotations=READ_ONLY)
async def central_get_static_route(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``static-route`` configurations from Central.

    Static routing is a type of network routing technique. Static routing is not a routing protocol; instead, it is the manual configuration and selection of a network route, usually managed by the network administrator. It is employed in scenarios where the network routing parameters are not expected to change often.

    Parameters:
        name: Specific ``static-route`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "static-route", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_static_route(
    ctx: Context,
    name: Annotated[str, Field(description="``static-route`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``static-route`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_static_route`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``static-route`` configuration in Central.

    Static routing is a type of network routing technique. Static routing is not a routing protocol; instead, it is the manual configuration and selection of a network route, usually managed by the network administrator. It is employed in scenarios where the network routing parameters are not expected to change often.
    """
    return await _manage_resource(
        ctx,
        "static-route",
        "static-route",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- track-object -----


@tool(annotations=READ_ONLY)
async def central_get_track_object(
    ctx: Context,
    identifier: str | None = None,
) -> dict | list | str:
    """Get ``track-object`` configurations from Central.

    Tracking object configurations.

    Parameters:
        identifier: Specific ``track-object`` identifier (OpenAPI path param: ``identifier``). If omitted, returns all.
    """
    return await _get_resource(ctx, "tracking-object", identifier)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_track_object(
    ctx: Context,
    identifier: Annotated[str, Field(description="``track-object`` identifier (OpenAPI path param: ``identifier``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``track-object`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_track_object`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``track-object`` configuration in Central.

    Tracking object configurations.
    """
    return await _manage_resource(
        ctx,
        "tracking-object",
        "track-object",
        identifier,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vrf -----


@tool(annotations=READ_ONLY)
async def central_get_vrf(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vrf`` configurations from Central.

    Virtual Routing Forwarding (VRF) container. A VRF is a logical partition of a network device's routing infrastructure that enables multiple independent routing tables on a single device. This container manages VRF instances, each with isolated routing domains, independent routing policies, route targets, and address families (IPv4, IPv6). VRFs support multi-tenancy, network segregation, and route leaking capabilities (IVRL - Inter-VRF Route Leaking) for complex network architectures.

    Parameters:
        name: Specific ``vrf`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vrfs", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vrf(
    ctx: Context,
    name: Annotated[str, Field(description="``vrf`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vrf`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vrf`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vrf`` configuration in Central.

    Virtual Routing Forwarding (VRF) container. A VRF is a logical partition of a network device's routing infrastructure that enables multiple independent routing tables on a single device. This container manages VRF instances, each with isolated routing domains, independent routing policies, route targets, and address families (IPv4, IPv6). VRFs support multi-tenancy, network segregation, and route leaking capabilities (IVRL - Inter-VRF Route Leaking) for complex network architectures.
    """
    return await _manage_resource(
        ctx,
        "vrfs",
        "vrf",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
