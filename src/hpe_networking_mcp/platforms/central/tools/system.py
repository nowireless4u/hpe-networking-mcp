"""Aruba Central ``system`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``system.json`` vendor
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
    _SCOPE_ID_FIELD,
    _get_resource,
    _manage_resource,
)

# ----- ap-system -----


@tool(capability=Capability.READ)
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


@tool(capability=Capability.WRITE_DELETE)
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


# ----- container-networks -----


@tool(capability=Capability.READ)
async def central_get_container_networks(
    ctx: Context,
    name_vrf: str | None = None,
) -> dict | list | str:
    """Get ``container-networks`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name_vrf: Specific ``container-networks`` identifier (OpenAPI path param: ``name-vrf``). If omitted, returns all.
    """
    return await _get_resource(ctx, "container-networks", name_vrf)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_container_networks(
    ctx: Context,
    name_vrf: Annotated[
        str, Field(description="``container-networks`` identifier (OpenAPI path param: ``name-vrf``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``container-networks`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_container_networks`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``container-networks`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "container-networks",
        "container-networks",
        name_vrf,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- containers -----


@tool(capability=Capability.READ)
async def central_get_containers(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``containers`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``containers`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "containers", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_containers(
    ctx: Context,
    name: Annotated[str, Field(description="``containers`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``containers`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_containers`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``containers`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "containers",
        "containers",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- countermon -----


@tool(capability=Capability.READ)
async def central_get_countermon(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``countermon`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``countermon`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "countermon", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_custom_get_api(
    ctx: Context,
) -> dict | list | str:
    """Get the ``custom-get-api`` singleton configuration from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _get_resource(ctx, "custom-get-api", None)


# ----- db-observer -----


@tool(capability=Capability.READ)
async def central_get_db_observer(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``db-observer`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``db-observer`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "db-observer", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_ddns(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ddns`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``ddns`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ddns", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_dns(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dns`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``dns`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dns", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_dump_server(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dump-server`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``dump-server`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dump-server", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


# ----- gw-system -----


@tool(capability=Capability.READ)
async def central_get_gw_system(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``gw-system`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``gw-system`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "gw-system", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


# ----- hardware-modules -----


@tool(capability=Capability.READ)
async def central_get_hardware_modules(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``hardware-modules`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``hardware-modules`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "hardware-modules", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_hardware_modules(
    ctx: Context,
    name: Annotated[str, Field(description="``hardware-modules`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``hardware-modules`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_hardware_modules`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``hardware-modules`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "hardware-modules",
        "hardware-modules",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- http-proxy-servers -----


@tool(capability=Capability.READ)
async def central_get_http_proxy_servers(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``http-proxy-servers`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``http-proxy-servers`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "http-proxy-servers", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_http_proxy_servers(
    ctx: Context,
    name: Annotated[str, Field(description="``http-proxy-servers`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``http-proxy-servers`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_http_proxy_servers`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``http-proxy-servers`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "http-proxy-servers",
        "http-proxy-servers",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ip-source-interfaces -----


@tool(capability=Capability.READ)
async def central_get_ip_source_interfaces(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ip-source-interfaces`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``ip-source-interfaces`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ip-source-interfaces", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_ip_source_interfaces(
    ctx: Context,
    name: Annotated[str, Field(description="``ip-source-interfaces`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ip-source-interfaces`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ip_source_interfaces`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ip-source-interfaces`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "ip-source-interfaces",
        "ip-source-interfaces",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ipm -----


@tool(capability=Capability.READ)
async def central_get_ipm(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ipm`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``ipm`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ipm", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_job_scheduler(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``job-scheduler`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``job-scheduler`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "job-scheduler", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_local_management(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``local-management`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``local-management`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "local-management", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_logging(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``logging`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``logging`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "logging", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


# ----- management-server -----


@tool(capability=Capability.READ)
async def central_get_management_server(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``management-server`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``management-server`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "management-server", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_management_server(
    ctx: Context,
    name: Annotated[str, Field(description="``management-server`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``management-server`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_management_server`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``management-server`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "management-server",
        "management-server",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- management-user-groups -----


@tool(capability=Capability.READ)
async def central_get_management_user_groups(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``management-user-groups`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``management-user-groups`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "management-user-groups", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_management_user_groups(
    ctx: Context,
    name: Annotated[str, Field(description="``management-user-groups`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``management-user-groups`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_management_user_groups`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``management-user-groups`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "management-user-groups",
        "management-user-groups",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- management-users -----


@tool(capability=Capability.READ)
async def central_get_management_users(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``management-users`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``management-users`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "management-users", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_management_users(
    ctx: Context,
    name: Annotated[str, Field(description="``management-users`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``management-users`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_management_users`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``management-users`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "management-users",
        "management-users",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- nae-agents -----


@tool(capability=Capability.READ)
async def central_get_nae_agents(
    ctx: Context,
    agent_name: str | None = None,
) -> dict | list | str:
    """Get ``nae-agents`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        agent_name: Specific ``nae-agents`` identifier (OpenAPI path param: ``agent-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "nae-agents", agent_name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_nae_agents(
    ctx: Context,
    agent_name: Annotated[str, Field(description="``nae-agents`` identifier (OpenAPI path param: ``agent-name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``nae-agents`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_nae_agents`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``nae-agents`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "nae-agents",
        "nae-agents",
        agent_name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- nae-scripts -----


@tool(capability=Capability.READ)
async def central_get_nae_scripts(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``nae-scripts`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``nae-scripts`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "nae-scripts", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_nae_scripts(
    ctx: Context,
    name: Annotated[str, Field(description="``nae-scripts`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``nae-scripts`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_nae_scripts`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``nae-scripts`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "nae-scripts",
        "nae-scripts",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ntp -----


@tool(capability=Capability.READ)
async def central_get_ntp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ntp`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``ntp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ntp", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_packet_capture(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``packet-capture`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``packet-capture`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "packet-capture", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_remote_management(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``remote-management`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``remote-management`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "remote-management", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


# ----- rmon-alarms -----


@tool(capability=Capability.READ)
async def central_get_rmon_alarms(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``rmon-alarms`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``rmon-alarms`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "rmon-alarms", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_rmon_alarms(
    ctx: Context,
    name: Annotated[str, Field(description="``rmon-alarms`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``rmon-alarms`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_rmon_alarms`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``rmon-alarms`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "rmon-alarms",
        "rmon-alarms",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- snmp -----


@tool(capability=Capability.READ)
async def central_get_snmp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``snmp`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``snmp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "snmp", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_snmp_trap(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``snmp-trap`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``snmp-trap`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "snmp-trap", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_speed_test(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``speed-test`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``speed-test`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "speed-test", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_switch_chassis(
    ctx: Context,
    chassis_name: str | None = None,
) -> dict | list | str:
    """Get ``switch-chassis`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        chassis_name: Specific ``switch-chassis`` identifier (OpenAPI path param: ``chassis-name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "switch-chassis", chassis_name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_switch_profiles(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``switch-profiles`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``switch-profiles`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "switch-profiles", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_switch_system(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``switch-system`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``switch-system`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "switch-system", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_sysmon(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``sysmon`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``sysmon`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "sysmon", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_system_info(
    ctx: Context,
) -> dict | list | str:
    """Get the ``system-info`` singleton configuration from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _get_resource(ctx, "system-info", None)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


@tool(capability=Capability.READ)
async def central_get_telemetry(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``telemetry`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``telemetry`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "telemetry", name)


@tool(capability=Capability.WRITE_DELETE)
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

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
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


# ----- time-ranges -----


@tool(capability=Capability.READ)
async def central_get_time_ranges(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``time-ranges`` configurations from Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.

    Parameters:
        name: Specific ``time-ranges`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "time-ranges", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_time_ranges(
    ctx: Context,
    name: Annotated[str, Field(description="``time-ranges`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``time-ranges`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_time_ranges`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``time-ranges`` configuration in Central.

    Manage global system settings for Aruba Access Points, including time zone, location, cluster mode, LED control, and operational parameters. These configurations define device identity, network integration, security policies, and system-wide behaviors such as country code, virtual controller settings, and advanced features like CPU management and thermal controls. This profile references Alias profiles for reusable configuration templates. Use this API to retrieve the list of AP System profiles.
    """
    return await _manage_resource(
        ctx,
        "time-ranges",
        "time-ranges",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
