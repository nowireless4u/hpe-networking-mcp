"""Aruba Central ``routing-overlays`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``routing-overlays.json`` vendor
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


# ----- aspath-lists -----


@tool(annotations=READ_ONLY)
async def central_get_aspath_lists(
    ctx: Context,
    aspath_list_name: str | None = None,
) -> dict | list | str:
    """Get ``aspath-lists`` configurations from Central.

    Container for all AIF configurations.

    Parameters:
        aspath_list_name: Specific ``aspath-lists`` identifier (OpenAPI path param: ``aspath-list-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "aspath-lists", aspath_list_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_aspath_lists(
    ctx: Context,
    aspath_list_name: Annotated[
        str, Field(description="``aspath-lists`` identifier (OpenAPI path param: ``aspath-list-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``aspath-lists`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_aspath_lists`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``aspath-lists`` configuration in Central.

    Container for all AIF configurations.
    """
    return await _manage_resource(
        ctx,
        "aspath-lists",
        "aspath-lists",
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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


# ----- community-lists -----


@tool(annotations=READ_ONLY)
async def central_get_community_lists(
    ctx: Context,
    community_list_name_community_type: str | None = None,
) -> dict | list | str:
    """Get ``community-lists`` configurations from Central.

    Container for all AIF configurations.

    Parameters:
        community_list_name_community_type: Specific ``community-lists`` identifier (OpenAPI path param: ``community-list-name-community-type``). If omitted, returns all.
    """
    return await _get_resource(ctx, "community-lists", community_list_name_community_type)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_community_lists(
    ctx: Context,
    community_list_name_community_type: Annotated[
        str,
        Field(
            description="``community-lists`` identifier (OpenAPI path param: ``community-list-name-community-type``)."
        ),
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``community-lists`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_community_lists`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``community-lists`` configuration in Central.

    Container for all AIF configurations.
    """
    return await _manage_resource(
        ctx,
        "community-lists",
        "community-lists",
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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


# ----- multicast-global -----


@tool(annotations=READ_ONLY)
async def central_get_multicast_global(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``multicast-global`` configurations from Central.

    Container for all AIF configurations.

    Parameters:
        name: Specific ``multicast-global`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "multicast-global", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_multicast_global(
    ctx: Context,
    name: Annotated[str, Field(description="``multicast-global`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``multicast-global`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_multicast_global`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``multicast-global`` configuration in Central.

    Container for all AIF configurations.
    """
    return await _manage_resource(
        ctx,
        "multicast-global",
        "multicast-global",
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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


# ----- nexthop-groups -----


@tool(annotations=READ_ONLY)
async def central_get_nexthop_groups(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``nexthop-groups`` configurations from Central.

    Container for all AIF configurations.

    Parameters:
        name: Specific ``nexthop-groups`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "nexthop-groups", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_nexthop_groups(
    ctx: Context,
    name: Annotated[str, Field(description="``nexthop-groups`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``nexthop-groups`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_nexthop_groups`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``nexthop-groups`` configuration in Central.

    Container for all AIF configurations.
    """
    return await _manage_resource(
        ctx,
        "nexthop-groups",
        "nexthop-groups",
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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


# ----- pim-router -----


@tool(annotations=READ_ONLY)
async def central_get_pim_router(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``pim-router`` configurations from Central.

    Container for all AIF configurations.

    Parameters:
        name: Specific ``pim-router`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "pim-router", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_pim_router(
    ctx: Context,
    name: Annotated[str, Field(description="``pim-router`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``pim-router`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_pim_router`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``pim-router`` configuration in Central.

    Container for all AIF configurations.
    """
    return await _manage_resource(
        ctx,
        "pim-router",
        "pim-router",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- prefix-lists -----


@tool(annotations=READ_ONLY)
async def central_get_prefix_lists(
    ctx: Context,
    prefix_list_name_address_family: str | None = None,
) -> dict | list | str:
    """Get ``prefix-lists`` configurations from Central.

    Container for all AIF configurations.

    Parameters:
        prefix_list_name_address_family: Specific ``prefix-lists`` identifier (OpenAPI path param: ``prefix-list-name-address-family``). If omitted, returns all.
    """
    return await _get_resource(ctx, "prefix-lists", prefix_list_name_address_family)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_prefix_lists(
    ctx: Context,
    prefix_list_name_address_family: Annotated[
        str, Field(description="``prefix-lists`` identifier (OpenAPI path param: ``prefix-list-name-address-family``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``prefix-lists`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_prefix_lists`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``prefix-lists`` configuration in Central.

    Container for all AIF configurations.
    """
    return await _manage_resource(
        ctx,
        "prefix-lists",
        "prefix-lists",
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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


# ----- route-maps -----


@tool(annotations=READ_ONLY)
async def central_get_route_maps(
    ctx: Context,
    route_map_name: str | None = None,
) -> dict | list | str:
    """Get ``route-maps`` configurations from Central.

    Container for all AIF configurations.

    Parameters:
        route_map_name: Specific ``route-maps`` identifier (OpenAPI path param: ``route-map-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "route-maps", route_map_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_route_maps(
    ctx: Context,
    route_map_name: Annotated[
        str, Field(description="``route-maps`` identifier (OpenAPI path param: ``route-map-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``route-maps`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_route_maps`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``route-maps`` configuration in Central.

    Container for all AIF configurations.
    """
    return await _manage_resource(
        ctx,
        "route-maps",
        "route-maps",
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

    Container for all AIF configurations.

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

    Container for all AIF configurations.
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


# ----- tracking-object -----


@tool(annotations=READ_ONLY)
async def central_get_tracking_object(
    ctx: Context,
    identifier: str | None = None,
) -> dict | list | str:
    """Get ``tracking-object`` configurations from Central.

    Container for all AIF configurations.

    Parameters:
        identifier: Specific ``tracking-object`` identifier (OpenAPI path param: ``identifier``). If omitted, returns all.
    """
    return await _get_resource(ctx, "tracking-object", identifier)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_tracking_object(
    ctx: Context,
    identifier: Annotated[
        str, Field(description="``tracking-object`` identifier (OpenAPI path param: ``identifier``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``tracking-object`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_tracking_object`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``tracking-object`` configuration in Central.

    Container for all AIF configurations.
    """
    return await _manage_resource(
        ctx,
        "tracking-object",
        "tracking-object",
        identifier,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vrfs -----


@tool(annotations=READ_ONLY)
async def central_get_vrfs(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vrfs`` configurations from Central.

    Container for all AIF configurations.

    Parameters:
        name: Specific ``vrfs`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vrfs", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vrfs(
    ctx: Context,
    name: Annotated[str, Field(description="``vrfs`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vrfs`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vrfs`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vrfs`` configuration in Central.

    Container for all AIF configurations.
    """
    return await _manage_resource(
        ctx,
        "vrfs",
        "vrfs",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
