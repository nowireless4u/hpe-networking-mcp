"""Aruba Central ``network-services`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``network-services.json`` vendor
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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


# ----- ip-source-lockdown -----


@tool(annotations=READ_ONLY)
async def central_get_ip_source_lockdown(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ip-source-lockdown`` configurations from Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

    Parameters:
        name: Specific ``ip-source-lockdown`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ip-source-lockdown", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ip_source_lockdown(
    ctx: Context,
    name: Annotated[str, Field(description="``ip-source-lockdown`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ip-source-lockdown`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ip_source_lockdown`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ip-source-lockdown`` configuration in Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
    """
    return await _manage_resource(
        ctx,
        "ip-source-lockdown",
        "ip-source-lockdown",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ip-source-lockdown-interface -----


@tool(annotations=READ_ONLY)
async def central_get_ip_source_lockdown_interface(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ip-source-lockdown-interface`` configurations from Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

    Parameters:
        name: Specific ``ip-source-lockdown-interface`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ip-source-lockdown-interface", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ip_source_lockdown_interface(
    ctx: Context,
    name: Annotated[
        str, Field(description="``ip-source-lockdown-interface`` identifier (OpenAPI path param: ``name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ip-source-lockdown-interface`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ip_source_lockdown_interface`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ip-source-lockdown-interface`` configuration in Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
    """
    return await _manage_resource(
        ctx,
        "ip-source-lockdown-interface",
        "ip-source-lockdown-interface",
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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


# ----- mgmd-global -----


@tool(annotations=READ_ONLY)
async def central_get_mgmd_global(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mgmd-global`` configurations from Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

    Parameters:
        name: Specific ``mgmd-global`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mgmd-global", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_mgmd_global(
    ctx: Context,
    name: Annotated[str, Field(description="``mgmd-global`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mgmd-global`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mgmd_global`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mgmd-global`` configuration in Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
    """
    return await _manage_resource(
        ctx,
        "mgmd-global",
        "mgmd-global",
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

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

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
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


# ----- qos-queues -----


@tool(annotations=READ_ONLY)
async def central_get_qos_queues(
    ctx: Context,
    q_profile_name: str | None = None,
) -> dict | list | str:
    """Get ``qos-queues`` configurations from Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

    Parameters:
        q_profile_name: Specific ``qos-queues`` identifier (OpenAPI path param: ``q-profile-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "qos-queues", q_profile_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_qos_queues(
    ctx: Context,
    q_profile_name: Annotated[
        str, Field(description="``qos-queues`` identifier (OpenAPI path param: ``q-profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``qos-queues`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_qos_queues`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``qos-queues`` configuration in Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
    """
    return await _manage_resource(
        ctx,
        "qos-queues",
        "qos-queues",
        q_profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- qos-schedules -----


@tool(annotations=READ_ONLY)
async def central_get_qos_schedules(
    ctx: Context,
    sched_profile_name: str | None = None,
) -> dict | list | str:
    """Get ``qos-schedules`` configurations from Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

    Parameters:
        sched_profile_name: Specific ``qos-schedules`` identifier (OpenAPI path param: ``sched-profile-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "qos-schedules", sched_profile_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_qos_schedules(
    ctx: Context,
    sched_profile_name: Annotated[
        str, Field(description="``qos-schedules`` identifier (OpenAPI path param: ``sched-profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``qos-schedules`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_qos_schedules`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``qos-schedules`` configuration in Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
    """
    return await _manage_resource(
        ctx,
        "qos-schedules",
        "qos-schedules",
        sched_profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- qos-thresholds -----


@tool(annotations=READ_ONLY)
async def central_get_qos_thresholds(
    ctx: Context,
    thresh_profile_name: str | None = None,
) -> dict | list | str:
    """Get ``qos-thresholds`` configurations from Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

    Parameters:
        thresh_profile_name: Specific ``qos-thresholds`` identifier (OpenAPI path param: ``thresh-profile-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "qos-thresholds", thresh_profile_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_qos_thresholds(
    ctx: Context,
    thresh_profile_name: Annotated[
        str, Field(description="``qos-thresholds`` identifier (OpenAPI path param: ``thresh-profile-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``qos-thresholds`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_qos_thresholds`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``qos-thresholds`` configuration in Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
    """
    return await _manage_resource(
        ctx,
        "qos-thresholds",
        "qos-thresholds",
        thresh_profile_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- source-ip-bindings -----


@tool(annotations=READ_ONLY)
async def central_get_source_ip_bindings(
    ctx: Context,
    ip_version_vlan_client_address: str | None = None,
) -> dict | list | str:
    """Get ``source-ip-bindings`` configurations from Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

    Parameters:
        ip_version_vlan_client_address: Specific ``source-ip-bindings`` identifier (OpenAPI path param: ``ip-version-vlan-client-address``). If omitted, returns all.
    """
    return await _get_resource(ctx, "source-ip-bindings", ip_version_vlan_client_address)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_source_ip_bindings(
    ctx: Context,
    ip_version_vlan_client_address: Annotated[
        str,
        Field(
            description="``source-ip-bindings`` identifier (OpenAPI path param: ``ip-version-vlan-client-address``)."
        ),
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``source-ip-bindings`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_source_ip_bindings`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``source-ip-bindings`` configuration in Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
    """
    return await _manage_resource(
        ctx,
        "source-ip-bindings",
        "source-ip-bindings",
        ip_version_vlan_client_address,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- udp-broadcast-forwarders -----


@tool(annotations=READ_ONLY)
async def central_get_udp_broadcast_forwarders(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``udp-broadcast-forwarders`` configurations from Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.

    Parameters:
        name: Specific ``udp-broadcast-forwarders`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "udp-broadcast-forwarders", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_udp_broadcast_forwarders(
    ctx: Context,
    name: Annotated[str, Field(description="``udp-broadcast-forwarders`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``udp-broadcast-forwarders`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_udp_broadcast_forwarders`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``udp-broadcast-forwarders`` configuration in Central.

    Dynamic Host Configuration Protocol (DHCP) pool profiles automate IP address assignment and network configuration delivery to client devices joining the network. DHCP servers use pools to manage IPv4/IPv6 address ranges, DNS settings, gateway information, lease durations, and vendor-specific options (DHCP Options 43, 60, etc.). This module supports DHCPv4 and DHCPv6 with static bindings, DDNS integration, and network boot configuration. Requires DDNS profiles for dynamic DNS updates. Device Limits: Gateway supports up to 256 DHCPv4 static reservations, 1 IP address per DHCPv4 option code. Use this API to retrieve the list of DHCP pool profiles.
    """
    return await _manage_resource(
        ctx,
        "udp-broadcast-forwarders",
        "udp-broadcast-forwarders",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
