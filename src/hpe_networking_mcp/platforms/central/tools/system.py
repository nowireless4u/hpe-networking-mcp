"""Aruba Central ``System`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``System`` OpenAPI tag-group. Wrappers
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

# ----- ap-system -----


@tool(annotations=READ_ONLY)
async def central_get_ap_system(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ap-system`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``ap-system`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ap-system", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ap_system(
    ctx: Context,
    name: Annotated[str, Field(description="``ap-system`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ap-system`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ap_system`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ap-system`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "ap-system",
        "ap-system",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- container -----


@tool(annotations=READ_ONLY)
async def central_get_container(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``container`` configurations from Central.

    Container configuration.

    Parameters:
        name: Specific ``container`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "containers", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_container(
    ctx: Context,
    name: Annotated[str, Field(description="``container`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``container`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_container`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``container`` configuration in Central.

    Container configuration.
    """
    return await _manage_resource(
        ctx,
        "containers",
        "container",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- container-network -----


@tool(annotations=READ_ONLY)
async def central_get_container_network(
    ctx: Context,
    name_vrf: str | None = None,
) -> dict | list | str:
    """Get ``container-network`` configurations from Central.

    Container Network configuration.

    Parameters:
        name_vrf: Specific ``container-network`` identifier (OpenAPI path param: ``name-vrf``). If omitted, returns all.
    """
    return await _get_resource(ctx, "container-networks", name_vrf)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_container_network(
    ctx: Context,
    name_vrf: Annotated[str, Field(description="``container-network`` identifier (OpenAPI path param: ``name-vrf``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``container-network`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_container_network`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``container-network`` configuration in Central.

    Container Network configuration.
    """
    return await _manage_resource(
        ctx,
        "container-networks",
        "container-network",
        name_vrf,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- countermon -----


@tool(annotations=READ_ONLY)
async def central_get_countermon(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``countermon`` configurations from Central.

    The counter monitor is an ASIC counter monitoring mechanism designed to be less resource intensive which periodically collects a set of port error counters and updates the latest values into OVSDB.

    Parameters:
        name: Specific ``countermon`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "countermon", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_countermon(
    ctx: Context,
    name: Annotated[str, Field(description="``countermon`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``countermon`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_countermon`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``countermon`` configuration in Central.

    The counter monitor is an ASIC counter monitoring mechanism designed to be less resource intensive which periodically collects a set of port error counters and updates the latest values into OVSDB.
    """
    return await _manage_resource(
        ctx,
        "countermon",
        "countermon",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- custom-get-api -----


@tool(annotations=READ_ONLY)
async def central_get_custom_get_api(
    ctx: Context,
) -> dict | list | str:
    """Get the ``custom-get-api`` singleton configuration from Central.

    Customized APIs.
    """
    return await _get_resource(ctx, "custom-get-api", None)


# ----- db-observer -----


@tool(annotations=READ_ONLY)
async def central_get_db_observer(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``db-observer`` configurations from Central.

    Container for Database Observer entries.

    Parameters:
        name: Specific ``db-observer`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "db-observer", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_db_observer(
    ctx: Context,
    name: Annotated[str, Field(description="``db-observer`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``db-observer`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_db_observer`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``db-observer`` configuration in Central.

    Container for Database Observer entries.
    """
    return await _manage_resource(
        ctx,
        "db-observer",
        "db-observer",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ddns -----


@tool(annotations=READ_ONLY)
async def central_get_ddns(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ddns`` configurations from Central.

    Dynamic DNS (DDNS) using IETF RFC 2136 protocol automatically updates DNS records when device IP addresses change through DHCP or uplink modifications. DDNS uses TSIG (Transaction Signature) authentication for secure zone updates to authoritative DNS servers. Configure DDNS update intervals, server lists with authentication keys (Gateway), and PTR record options (Access Point). Server IPs are IPv4 only. Use this API to retrieve the list of DDNS profiles.

    Parameters:
        name: Specific ``ddns`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ddns", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ddns(
    ctx: Context,
    name: Annotated[str, Field(description="``ddns`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ddns`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ddns`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ddns`` configuration in Central.

    Dynamic DNS (DDNS) using IETF RFC 2136 protocol automatically updates DNS records when device IP addresses change through DHCP or uplink modifications. DDNS uses TSIG (Transaction Signature) authentication for secure zone updates to authoritative DNS servers. Configure DDNS update intervals, server lists with authentication keys (Gateway), and PTR record options (Access Point). Server IPs are IPv4 only. Use this API to retrieve the list of DDNS profiles.
    """
    return await _manage_resource(
        ctx,
        "ddns",
        "ddns",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dns -----


@tool(annotations=READ_ONLY)
async def central_get_dns(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dns`` configurations from Central.

    DNS parameters for handling the domain name, DNS resolver, DNS redirect and DNS static host configuration.

    Parameters:
        name: Specific ``dns`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dns", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dns(
    ctx: Context,
    name: Annotated[str, Field(description="``dns`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dns`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dns`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dns`` configuration in Central.

    DNS parameters for handling the domain name, DNS resolver, DNS redirect and DNS static host configuration.
    """
    return await _manage_resource(
        ctx,
        "dns",
        "dns",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dump-server -----


@tool(annotations=READ_ONLY)
async def central_get_dump_server(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dump-server`` configurations from Central.

    Configure TFTP and SCP dump server for storing core dump files. Trivial File Transfer Protocol (TFTP) is a simple way for exchanging files in clear text without authentication. SCP (Secure Copy Protocol) uses Secure Shell (SSH) mechanisms for data transfer and authentication to ensure the confidentiality of the data in transit.. This feature is only applicable for AP.

    Parameters:
        name: Specific ``dump-server`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dump-server", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dump_server(
    ctx: Context,
    name: Annotated[str, Field(description="``dump-server`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dump-server`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dump_server`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dump-server`` configuration in Central.

    Configure TFTP and SCP dump server for storing core dump files. Trivial File Transfer Protocol (TFTP) is a simple way for exchanging files in clear text without authentication. SCP (Secure Copy Protocol) uses Secure Shell (SSH) mechanisms for data transfer and authentication to ensure the confidentiality of the data in transit.. This feature is only applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "dump-server",
        "dump-server",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- feature-pack -----


@tool(annotations=READ_ONLY)
async def central_get_feature_pack(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``feature-pack`` configurations from Central.

    Feature Pack management server configuration.

    Parameters:
        name: Specific ``feature-pack`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "management-server", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_feature_pack(
    ctx: Context,
    name: Annotated[str, Field(description="``feature-pack`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``feature-pack`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_feature_pack`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``feature-pack`` configuration in Central.

    Feature Pack management server configuration.
    """
    return await _manage_resource(
        ctx,
        "management-server",
        "feature-pack",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- gw-system -----


@tool(annotations=READ_ONLY)
async def central_get_gw_system(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``gw-system`` configurations from Central.

    The Gateway System profile defines device-level operational parameters including timezone configuration, LCD menu controls, system IP addressing (controller-ip), global firewall policies, AAA authentication timers, RADIUS/TACACS+ client settings, IPv6 proxy router advertisements, DNS query intervals, and SNMP location attributes. This profile relies on VLAN Interface and Loopback Interface configurations for network-facing parameters. Certain features like datapath energy efficiency, LCD menu, and GPS support are hardware-dependent and available only on specific Gateway models. Use this API to retrieve the list of Gateway System profiles.

    Parameters:
        name: Specific ``gw-system`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "gw-system", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_gw_system(
    ctx: Context,
    name: Annotated[str, Field(description="``gw-system`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``gw-system`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_gw_system`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``gw-system`` configuration in Central.

    The Gateway System profile defines device-level operational parameters including timezone configuration, LCD menu controls, system IP addressing (controller-ip), global firewall policies, AAA authentication timers, RADIUS/TACACS+ client settings, IPv6 proxy router advertisements, DNS query intervals, and SNMP location attributes. This profile relies on VLAN Interface and Loopback Interface configurations for network-facing parameters. Certain features like datapath energy efficiency, LCD menu, and GPS support are hardware-dependent and available only on specific Gateway models. Use this API to retrieve the list of Gateway System profiles.
    """
    return await _manage_resource(
        ctx,
        "gw-system",
        "gw-system",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- hardware-module-profile -----


@tool(annotations=READ_ONLY)
async def central_get_hardware_module_profile(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``hardware-module-profile`` configurations from Central.

    Configure and manage hardware module profiles. A hardware module profile allows certain device-specific configuration to be applied to a standalone switch, a chassis line-module or a VSF stack member. It is a mechanism intended to ease the process of configuring these devices with the same set of configurations. Instead of manually configuring each switch, line-module or VSF member one-by-one, the hardware module profile collects the common configuration settings and allows them to be applied to a specific device or a collection of devices. To apply a hardware module profile to a VSF member or group of VSF members, the hw-profile name here must be referenced from their respective 'hw-profile' endpoints in the 'switch-stack' API. See `aruba-switch-stack:stacks/stack/members/hw-profile`. Applicable to CX 6200, 6300, 6300L switches. To apply a hardware module profile to a specific line-module or group of line-modules, the profile name here must be referenced from their respective 'hw-profile' endpoint in the switch-chassis' API. See `aruba-switch-chassis:switch-chassis/chassis/line-modules/hw-profile` Applicable to CX 6400, 8400X switches. To apply a hardware module profile to a standalone switch, including devices that support VSF but are not configured in a stack, no reference from another API is required.

    Parameters:
        name: Specific ``hardware-module-profile`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "hardware-modules", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_hardware_module_profile(
    ctx: Context,
    name: Annotated[str, Field(description="``hardware-module-profile`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``hardware-module-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_hardware_module_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``hardware-module-profile`` configuration in Central.

    Configure and manage hardware module profiles. A hardware module profile allows certain device-specific configuration to be applied to a standalone switch, a chassis line-module or a VSF stack member. It is a mechanism intended to ease the process of configuring these devices with the same set of configurations. Instead of manually configuring each switch, line-module or VSF member one-by-one, the hardware module profile collects the common configuration settings and allows them to be applied to a specific device or a collection of devices. To apply a hardware module profile to a VSF member or group of VSF members, the hw-profile name here must be referenced from their respective 'hw-profile' endpoints in the 'switch-stack' API. See `aruba-switch-stack:stacks/stack/members/hw-profile`. Applicable to CX 6200, 6300, 6300L switches. To apply a hardware module profile to a specific line-module or group of line-modules, the profile name here must be referenced from their respective 'hw-profile' endpoint in the switch-chassis' API. See `aruba-switch-chassis:switch-chassis/chassis/line-modules/hw-profile` Applicable to CX 6400, 8400X switches. To apply a hardware module profile to a standalone switch, including devices that support VSF but are not configured in a stack, no reference from another API is required.
    """
    return await _manage_resource(
        ctx,
        "hardware-modules",
        "hardware-module-profile",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- http-proxy -----


@tool(annotations=READ_ONLY)
async def central_get_http_proxy(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``http-proxy`` configurations from Central.

    Use this to configure HTTP proxy settings. On AP, HTTP Proxy settings is for downloading the image from the cloud server, or to route the web classification queries through the proxy server. On SW_CX and SW_PVOS, the HTTP Proxy configuration is utilized to connect to Activate server and HPE ANW Central. This feature is applicable for AP, SW_CX and SW_PVOS.

    Parameters:
        name: Specific ``http-proxy`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "http-proxy-servers", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_http_proxy(
    ctx: Context,
    name: Annotated[str, Field(description="``http-proxy`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``http-proxy`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_http_proxy`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``http-proxy`` configuration in Central.

    Use this to configure HTTP proxy settings. On AP, HTTP Proxy settings is for downloading the image from the cloud server, or to route the web classification queries through the proxy server. On SW_CX and SW_PVOS, the HTTP Proxy configuration is utilized to connect to Activate server and HPE ANW Central. This feature is applicable for AP, SW_CX and SW_PVOS.
    """
    return await _manage_resource(
        ctx,
        "http-proxy-servers",
        "http-proxy",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ip-source-interface -----


@tool(annotations=READ_ONLY)
async def central_get_ip_source_interface(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ip-source-interface`` configurations from Central.

    IPv4/IPv6 Source Interface Selection Configurations. The source interface selection supports selecting an IPv4/IPv6 address or interface name for all outgoing traffic generated by a specified software application on the switch.

    Parameters:
        name: Specific ``ip-source-interface`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ip-source-interfaces", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ip_source_interface(
    ctx: Context,
    name: Annotated[str, Field(description="``ip-source-interface`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ip-source-interface`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ip_source_interface`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ip-source-interface`` configuration in Central.

    IPv4/IPv6 Source Interface Selection Configurations. The source interface selection supports selecting an IPv4/IPv6 address or interface name for all outgoing traffic generated by a specified software application on the switch.
    """
    return await _manage_resource(
        ctx,
        "ip-source-interfaces",
        "ip-source-interface",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ipm -----


@tool(annotations=READ_ONLY)
async def central_get_ipm(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ipm`` configurations from Central.

    Configure Intelligent Power Monitoring (IPM) reduction steps and priorities. The reduction function with the highest priority is applied when the power budget threshold or when the threshold temperature is exceeded. This feature is only applicable for AP.

    Parameters:
        name: Specific ``ipm`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ipm", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ipm(
    ctx: Context,
    name: Annotated[str, Field(description="``ipm`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ipm`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ipm`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ipm`` configuration in Central.

    Configure Intelligent Power Monitoring (IPM) reduction steps and priorities. The reduction function with the highest priority is applied when the power budget threshold or when the threshold temperature is exceeded. This feature is only applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "ipm",
        "ipm",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- job-scheduler -----


@tool(annotations=READ_ONLY)
async def central_get_job_scheduler(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``job-scheduler`` configurations from Central.

    The job scheduler feature facilitates us to schedule a job to be executed in the near future. Currently, only non-interactive enable and configuration commands are allowed to be configured as a job. Schedules can be configured to be triggered periodically or at a specific calendar date and time. They are categorized into periodic schedules, calendar schedules, and one-shot schedules. Periodic schedules are based on the fixed time interval between the two triggers. Calendar schedules are based on the specified days of the week and days of the month. Calendar schedules are therefore aware of the notion of months, days, weekdays, hours, and minutes. One-shot schedules are similar to the calendar schedule but they will automatically disable themselves after one trigger. This feature is useful to schedule a toggling port, check the system health status, clear the statistics or some clean-up activities, QoS policy changes, save the configurations, and other similar jobs. While updating trigger-type other parameter must set to null, which are not applicable.

    Parameters:
        name: Specific ``job-scheduler`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "job-scheduler", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_job_scheduler(
    ctx: Context,
    name: Annotated[str, Field(description="``job-scheduler`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``job-scheduler`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_job_scheduler`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``job-scheduler`` configuration in Central.

    The job scheduler feature facilitates us to schedule a job to be executed in the near future. Currently, only non-interactive enable and configuration commands are allowed to be configured as a job. Schedules can be configured to be triggered periodically or at a specific calendar date and time. They are categorized into periodic schedules, calendar schedules, and one-shot schedules. Periodic schedules are based on the fixed time interval between the two triggers. Calendar schedules are based on the specified days of the week and days of the month. Calendar schedules are therefore aware of the notion of months, days, weekdays, hours, and minutes. One-shot schedules are similar to the calendar schedule but they will automatically disable themselves after one trigger. This feature is useful to schedule a toggling port, check the system health status, clear the statistics or some clean-up activities, QoS policy changes, save the configurations, and other similar jobs. While updating trigger-type other parameter must set to null, which are not applicable.
    """
    return await _manage_resource(
        ctx,
        "job-scheduler",
        "job-scheduler",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- local-management -----


@tool(annotations=READ_ONLY)
async def central_get_local_management(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``local-management`` configurations from Central.

    Configure local management settings of network devices via SSH, Telnet, console, or UI. This ensures secure, controlled, and monitored access to the devices. Manage AAA (Authentication, Authorization, and Accounting) for device local management, and it ensures that only authorized users can access the device, perform specific actions, and that all activities are logged for auditing purposes. This feature is applicable for all devices.

    Parameters:
        name: Specific ``local-management`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "local-management", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_local_management(
    ctx: Context,
    name: Annotated[str, Field(description="``local-management`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``local-management`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_local_management`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``local-management`` configuration in Central.

    Configure local management settings of network devices via SSH, Telnet, console, or UI. This ensures secure, controlled, and monitored access to the devices. Manage AAA (Authentication, Authorization, and Accounting) for device local management, and it ensures that only authorized users can access the device, perform specific actions, and that all activities are logged for auditing purposes. This feature is applicable for all devices.
    """
    return await _manage_resource(
        ctx,
        "local-management",
        "local-management",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- logging -----


@tool(annotations=READ_ONLY)
async def central_get_logging(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``logging`` configurations from Central.

    Manage logging profiles for Aruba devices, enabling centralized control of log message destinations, severity levels, and logging behavior. This API allows administrators to define and retrieve logging profiles, which can be referenced by other system or device profiles to standardize log management. Use this API to retrieve the list of Logging profiles.

    Parameters:
        name: Specific ``logging`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "logging", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_logging(
    ctx: Context,
    name: Annotated[str, Field(description="``logging`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``logging`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_logging`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``logging`` configuration in Central.

    Manage logging profiles for Aruba devices, enabling centralized control of log message destinations, severity levels, and logging behavior. This API allows administrators to define and retrieve logging profiles, which can be referenced by other system or device profiles to standardize log management. Use this API to retrieve the list of Logging profiles.
    """
    return await _manage_resource(
        ctx,
        "logging",
        "logging",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- management-user -----


@tool(annotations=READ_ONLY)
async def central_get_management_user(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``management-user`` configurations from Central.

    Configure management users with role and authorization. This feature is applicable for all devices. For AP, Users from higher-level configurations are automatically inherited and displayed at lower levels. When a lower-level user has the same role name as a higher-level user, the lower-level user takes precedence.

    Parameters:
        name: Specific ``management-user`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "management-users", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_management_user(
    ctx: Context,
    name: Annotated[str, Field(description="``management-user`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``management-user`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_management_user`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``management-user`` configuration in Central.

    Configure management users with role and authorization. This feature is applicable for all devices. For AP, Users from higher-level configurations are automatically inherited and displayed at lower levels. When a lower-level user has the same role name as a higher-level user, the lower-level user takes precedence.
    """
    return await _manage_resource(
        ctx,
        "management-users",
        "management-user",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- management-user-group -----


@tool(annotations=READ_ONLY)
async def central_get_management_user_group(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``management-user-group`` configurations from Central.

    Management User group.

    Parameters:
        name: Specific ``management-user-group`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "management-user-groups", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_management_user_group(
    ctx: Context,
    name: Annotated[str, Field(description="``management-user-group`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``management-user-group`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_management_user_group`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``management-user-group`` configuration in Central.

    Management User group.
    """
    return await _manage_resource(
        ctx,
        "management-user-groups",
        "management-user-group",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- nae-agent -----


@tool(annotations=READ_ONLY)
async def central_get_nae_agent(
    ctx: Context,
    agent_name: str | None = None,
) -> dict | list | str:
    """Get ``nae-agent`` configurations from Central.

    Configure and Manage Network Analytics Engine (NAE) agents. Network Analytics Engine (NAE) is a troubleshooting solution that monitors switch database resources and executes operations when monitor conditions are met. NAE Agent is a running instance of an NAE script that acts as a template for agent creation. When a new agent is created, all monitors specified in the script become active and alerts are generated when conditions are met. Each agent: - References an existing NAE script as its template - Can have custom parameter values specific to this agent instance - Monitors data every 5 seconds and generates alerts when conditions are satisfied - Can be temporarily disabled to stop monitoring without deleting the configuration - Operates independently, allowing multiple agents from the same script with different parameters Agents provide real-time network analytics and automated troubleshooting capabilities.

    Parameters:
        agent_name: Specific ``nae-agent`` identifier (OpenAPI path param: ``agent-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "nae-agents", agent_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_nae_agent(
    ctx: Context,
    agent_name: Annotated[str, Field(description="``nae-agent`` identifier (OpenAPI path param: ``agent-name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``nae-agent`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_nae_agent`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``nae-agent`` configuration in Central.

    Configure and Manage Network Analytics Engine (NAE) agents. Network Analytics Engine (NAE) is a troubleshooting solution that monitors switch database resources and executes operations when monitor conditions are met. NAE Agent is a running instance of an NAE script that acts as a template for agent creation. When a new agent is created, all monitors specified in the script become active and alerts are generated when conditions are met. Each agent: - References an existing NAE script as its template - Can have custom parameter values specific to this agent instance - Monitors data every 5 seconds and generates alerts when conditions are satisfied - Can be temporarily disabled to stop monitoring without deleting the configuration - Operates independently, allowing multiple agents from the same script with different parameters Agents provide real-time network analytics and automated troubleshooting capabilities.
    """
    return await _manage_resource(
        ctx,
        "nae-agents",
        "nae-agent",
        agent_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- nae-script -----


@tool(annotations=READ_ONLY)
async def central_get_nae_script(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``nae-script`` configurations from Central.

    Configure and Manage Network Analytics Engine (NAE) Scripts. NAE Script is a Python-based monitoring script that defines resources to monitor (Monitors) via REST API and conditions on those resources (Conditions). When conditions are met, pre-defined actions such as syslog messages or CLI commands are triggered. The main components of an NAE Script are: - Manifest: Identifies the script with metadata (name, version, author, supported platforms, etc.) - ParameterDefinitions: Defines customizable parameters for agent creation - Agent constructor: Contains the monitoring and condition logic Each script serves as a template for creating one or more NAE agents. Once uploaded and validated, the script can be used to instantiate multiple agents with different parameter values.

    Parameters:
        name: Specific ``nae-script`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "nae-scripts", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_nae_script(
    ctx: Context,
    name: Annotated[str, Field(description="``nae-script`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``nae-script`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_nae_script`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``nae-script`` configuration in Central.

    Configure and Manage Network Analytics Engine (NAE) Scripts. NAE Script is a Python-based monitoring script that defines resources to monitor (Monitors) via REST API and conditions on those resources (Conditions). When conditions are met, pre-defined actions such as syslog messages or CLI commands are triggered. The main components of an NAE Script are: - Manifest: Identifies the script with metadata (name, version, author, supported platforms, etc.) - ParameterDefinitions: Defines customizable parameters for agent creation - Agent constructor: Contains the monitoring and condition logic Each script serves as a template for creating one or more NAE agents. Once uploaded and validated, the script can be used to instantiate multiple agents with different parameter values.
    """
    return await _manage_resource(
        ctx,
        "nae-scripts",
        "nae-script",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ntp -----


@tool(annotations=READ_ONLY)
async def central_get_ntp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ntp`` configurations from Central.

    Network Time Protocol (NTP) synchronizes system clocks across network devices to ensure consistent timestamp accuracy for logs, authentication protocols, and distributed operations. This module supports NTPv3/v4 with IETF RFC 5905, configurable authentication via MD5/SHA keys, and flexible server management. Configure NTP servers, authentication profiles, conductor associations, and source interfaces for time synchronization. Device Limits: Gateway supports up to 15 NTP servers per profile. Use this API to retrieve the list of NTP profiles.

    Parameters:
        name: Specific ``ntp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ntp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ntp(
    ctx: Context,
    name: Annotated[str, Field(description="``ntp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ntp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ntp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ntp`` configuration in Central.

    Network Time Protocol (NTP) synchronizes system clocks across network devices to ensure consistent timestamp accuracy for logs, authentication protocols, and distributed operations. This module supports NTPv3/v4 with IETF RFC 5905, configurable authentication via MD5/SHA keys, and flexible server management. Configure NTP servers, authentication profiles, conductor associations, and source interfaces for time synchronization. Device Limits: Gateway supports up to 15 NTP servers per profile. Use this API to retrieve the list of NTP profiles.
    """
    return await _manage_resource(
        ctx,
        "ntp",
        "ntp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- packet-capture -----


@tool(annotations=READ_ONLY)
async def central_get_packet_capture(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``packet-capture`` configurations from Central.

    Configure packet capture profiles for network troubleshooting and analysis. Packet capture allows monitoring and recording network traffic on datapath and controlpath for diagnostic purposes.

    Parameters:
        name: Specific ``packet-capture`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "packet-capture", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_packet_capture(
    ctx: Context,
    name: Annotated[str, Field(description="``packet-capture`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``packet-capture`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_packet_capture`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``packet-capture`` configuration in Central.

    Configure packet capture profiles for network troubleshooting and analysis. Packet capture allows monitoring and recording network traffic on datapath and controlpath for diagnostic purposes.
    """
    return await _manage_resource(
        ctx,
        "packet-capture",
        "packet-capture",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- remote-management -----


@tool(annotations=READ_ONLY)
async def central_get_remote_management(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``remote-management`` configurations from Central.

    Remote management enables centralized configuration, monitoring, and troubleshooting of Aruba devices from external management platforms. This feature allows administrators to securely connect to and control devices remotely, streamlining operations and support. Use this API to retrieve the list of remote management profiles.

    Parameters:
        name: Specific ``remote-management`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "remote-management", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_remote_management(
    ctx: Context,
    name: Annotated[str, Field(description="``remote-management`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``remote-management`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_remote_management`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``remote-management`` configuration in Central.

    Remote management enables centralized configuration, monitoring, and troubleshooting of Aruba devices from external management platforms. This feature allows administrators to securely connect to and control devices remotely, streamlining operations and support. Use this API to retrieve the list of remote management profiles.
    """
    return await _manage_resource(
        ctx,
        "remote-management",
        "remote-management",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- rmon-alarm -----


@tool(annotations=READ_ONLY)
async def central_get_rmon_alarm(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``rmon-alarm`` configurations from Central.

    RMON alarm grouping.

    Parameters:
        name: Specific ``rmon-alarm`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "rmon-alarms", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_rmon_alarm(
    ctx: Context,
    name: Annotated[str, Field(description="``rmon-alarm`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``rmon-alarm`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_rmon_alarm`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``rmon-alarm`` configuration in Central.

    RMON alarm grouping.
    """
    return await _manage_resource(
        ctx,
        "rmon-alarms",
        "rmon-alarm",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- snmp -----


@tool(annotations=READ_ONLY)
async def central_get_snmp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``snmp`` configurations from Central.

    Profile for SNMP configuration. SNMP user-table, trap receivers, community strings, notify groups, targets, etc. can be configured. Both Informs and Traps are supported. Handles configuration for SNMP v1, v2c, v3 versions.

    Parameters:
        name: Specific ``snmp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "snmp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_snmp(
    ctx: Context,
    name: Annotated[str, Field(description="``snmp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``snmp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_snmp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``snmp`` configuration in Central.

    Profile for SNMP configuration. SNMP user-table, trap receivers, community strings, notify groups, targets, etc. can be configured. Both Informs and Traps are supported. Handles configuration for SNMP v1, v2c, v3 versions.
    """
    return await _manage_resource(
        ctx,
        "snmp",
        "snmp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- snmp-trap -----


@tool(annotations=READ_ONLY)
async def central_get_snmp_trap(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``snmp-trap`` configurations from Central.

    SNMP Trap profiles configuration. Using this profile SNMP traps can be enabled/disabled. Enabled traps will notify important events to the management station. This profile allows specification of traps,alarms.

    Parameters:
        name: Specific ``snmp-trap`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "snmp-trap", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_snmp_trap(
    ctx: Context,
    name: Annotated[str, Field(description="``snmp-trap`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``snmp-trap`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_snmp_trap`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``snmp-trap`` configuration in Central.

    SNMP Trap profiles configuration. Using this profile SNMP traps can be enabled/disabled. Enabled traps will notify important events to the management station. This profile allows specification of traps,alarms.
    """
    return await _manage_resource(
        ctx,
        "snmp-trap",
        "snmp-trap",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- speed-test -----


@tool(annotations=READ_ONLY)
async def central_get_speed_test(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``speed-test`` configurations from Central.

    Speed test profiles enable Aruba devices to measure network throughput, latency, and performance between endpoints. This feature helps administrators diagnose connectivity issues, validate service levels, and optimize network performance. Use this API to retrieve the list of speed test profiles.

    Parameters:
        name: Specific ``speed-test`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "speed-test", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_speed_test(
    ctx: Context,
    name: Annotated[str, Field(description="``speed-test`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``speed-test`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_speed_test`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``speed-test`` configuration in Central.

    Speed test profiles enable Aruba devices to measure network throughput, latency, and performance between endpoints. This feature helps administrators diagnose connectivity issues, validate service levels, and optimize network performance. Use this API to retrieve the list of speed test profiles.
    """
    return await _manage_resource(
        ctx,
        "speed-test",
        "speed-test",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- switch-chassis -----


@tool(annotations=READ_ONLY)
async def central_get_switch_chassis(
    ctx: Context,
    chassis_name: str | None = None,
) -> dict | list | str:
    """Get ``switch-chassis`` configurations from Central.

    Switch chassis configuration.

    Parameters:
        chassis_name: Specific ``switch-chassis`` identifier (OpenAPI path param: ``chassis-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "switch-chassis", chassis_name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_switch_chassis(
    ctx: Context,
    chassis_name: Annotated[
        str, Field(description="``switch-chassis`` identifier (OpenAPI path param: ``chassis-name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``switch-chassis`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_switch_chassis`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``switch-chassis`` configuration in Central.

    Switch chassis configuration.
    """
    return await _manage_resource(
        ctx,
        "switch-chassis",
        "switch-chassis",
        chassis_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- switch-profiles -----


@tool(annotations=READ_ONLY)
async def central_get_switch_profiles(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``switch-profiles`` configurations from Central.

    Configure and Manage Switch Profiles. System profiles set the overall capabilities and capacities of the switch, based on the selected profile used at boot time. System profiles set capacities such as that of the hardware forwarding table. System profiles provide you with the flexibility to configure switches based on their location in the network (for example, core, spine, leaf). When a switch boots without a profile specifically configured, it boots with the default profile. When a switch is configured with a non-default profile, the switch requires a reboot for the profile to be applied.

    Parameters:
        name: Specific ``switch-profiles`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "switch-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_switch_profiles(
    ctx: Context,
    name: Annotated[str, Field(description="``switch-profiles`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``switch-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_switch_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``switch-profiles`` configuration in Central.

    Configure and Manage Switch Profiles. System profiles set the overall capabilities and capacities of the switch, based on the selected profile used at boot time. System profiles set capacities such as that of the hardware forwarding table. System profiles provide you with the flexibility to configure switches based on their location in the network (for example, core, spine, leaf). When a switch boots without a profile specifically configured, it boots with the default profile. When a switch is configured with a non-default profile, the switch requires a reboot for the profile to be applied.
    """
    return await _manage_resource(
        ctx,
        "switch-profiles",
        "switch-profiles",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- switch-system -----


@tool(annotations=READ_ONLY)
async def central_get_switch_system(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``switch-system`` configurations from Central.

    System Configurations.

    Parameters:
        name: Specific ``switch-system`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "switch-system", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_switch_system(
    ctx: Context,
    name: Annotated[str, Field(description="``switch-system`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``switch-system`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_switch_system`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``switch-system`` configuration in Central.

    System Configurations.
    """
    return await _manage_resource(
        ctx,
        "switch-system",
        "switch-system",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- sysmon -----


@tool(annotations=READ_ONLY)
async def central_get_sysmon(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``sysmon`` configurations from Central.

    The System Resources Monitor daemon collects system parameters (i.e., CPU usage, memory usage, open FD’s) for the overall system and all running daemons, then writes it into the OVSDB during every poll interval (~10 sec is default and minimum). This captures the current value of these monitoring parameters, which is then displayed using CLI show commands.

    Parameters:
        name: Specific ``sysmon`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "sysmon", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_sysmon(
    ctx: Context,
    name: Annotated[str, Field(description="``sysmon`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``sysmon`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_sysmon`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``sysmon`` configuration in Central.

    The System Resources Monitor daemon collects system parameters (i.e., CPU usage, memory usage, open FD’s) for the overall system and all running daemons, then writes it into the OVSDB during every poll interval (~10 sec is default and minimum). This captures the current value of these monitoring parameters, which is then displayed using CLI show commands.
    """
    return await _manage_resource(
        ctx,
        "sysmon",
        "sysmon",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- system-info -----


@tool(annotations=READ_ONLY)
async def central_get_system_info(
    ctx: Context,
) -> dict | list | str:
    """Get the ``system-info`` singleton configuration from Central.

    System information provides key details about the Aruba device, including hardware model, software version, serial number, and operational status. This information is essential for inventory management, support, and troubleshooting. Use this API to retrieve system information for Aruba devices.
    """
    return await _get_resource(ctx, "system-info", None)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_system_info(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``system-info`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_system_info`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``system-info`` configuration in Central.

    System information provides key details about the Aruba device, including hardware model, software version, serial number, and operational status. This information is essential for inventory management, support, and troubleshooting. Use this API to retrieve system information for Aruba devices.
    """
    return await _manage_resource(
        ctx,
        "system-info",
        "system-info",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- telemetry -----


@tool(annotations=READ_ONLY)
async def central_get_telemetry(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``telemetry`` configurations from Central.

    Enables inline monitoring statistics for AP. The information is collected and forwarded to AirWave to debug client connectivity issues. This feature is only applicable for AP.

    Parameters:
        name: Specific ``telemetry`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "telemetry", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_telemetry(
    ctx: Context,
    name: Annotated[str, Field(description="``telemetry`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``telemetry`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_telemetry`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``telemetry`` configuration in Central.

    Enables inline monitoring statistics for AP. The information is collected and forwarded to AirWave to debug client connectivity issues. This feature is only applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "telemetry",
        "telemetry",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- timerange -----


@tool(annotations=READ_ONLY)
async def central_get_timerange(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``timerange`` configurations from Central.

    Configure time range profiles on device to enable or diable access to an SSID during a specific period of time. This feature is only applicable for AP.

    Parameters:
        name: Specific ``timerange`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "time-ranges", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_timerange(
    ctx: Context,
    name: Annotated[str, Field(description="``timerange`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``timerange`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_timerange`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``timerange`` configuration in Central.

    Configure time range profiles on device to enable or diable access to an SSID during a specific period of time. This feature is only applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "time-ranges",
        "timerange",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
