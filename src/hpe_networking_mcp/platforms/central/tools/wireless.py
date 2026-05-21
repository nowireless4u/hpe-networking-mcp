"""Aruba Central ``Wireless`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``Wireless`` OpenAPI tag-group. Wrappers
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

# ----- alg -----


@tool(annotations=READ_ONLY)
async def central_get_alg(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``alg`` configurations from Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.

    Parameters:
        name: Specific ``alg`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "alg", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_alg(
    ctx: Context,
    name: Annotated[str, Field(description="``alg`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``alg`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_alg`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``alg`` configuration in Central.

    Aruba AP ALG (SCCP, SIP, UA, Vocera) configuration.
    """
    return await _manage_resource(
        ctx,
        "alg",
        "alg",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ids -----


@tool(annotations=READ_ONLY)
async def central_get_ids(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ids`` configurations from Central.

    Intrusion Detection System (IDS) monitors the network for the presence of unauthorized APs and clients, and detect rogue APs, interfering APs, and other devices that can potentially disrupt network operations. It also logs information about the unauthorized APs and clients, and generates reports based on the logged information. Intrusion Protection System (IPS) protects networks according to planned policies when the specfic attacks happen. This feature is only applicable on AP.

    Parameters:
        name: Specific ``ids`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ids", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ids(
    ctx: Context,
    name: Annotated[str, Field(description="``ids`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ids`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ids`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ids`` configuration in Central.

    Intrusion Detection System (IDS) monitors the network for the presence of unauthorized APs and clients, and detect rogue APs, interfering APs, and other devices that can potentially disrupt network operations. It also logs information about the unauthorized APs and clients, and generates reports based on the logged information. Intrusion Protection System (IPS) protects networks according to planned policies when the specfic attacks happen. This feature is only applicable on AP.
    """
    return await _manage_resource(
        ctx,
        "ids",
        "ids",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mesh -----


@tool(annotations=READ_ONLY)
async def central_get_mesh(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mesh`` configurations from Central.

    Configure and retrieve Mesh profiles for Aruba Access Points, enabling wireless backhaul connectivity between mesh portals and mesh points. These profiles define mesh cluster settings, band selection, topology behavior, role selection, and recovery parameters used to build and maintain the mesh network. Use this API to retrieve the list of Mesh profiles.

    Parameters:
        name: Specific ``mesh`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mesh", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_mesh(
    ctx: Context,
    name: Annotated[str, Field(description="``mesh`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mesh`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mesh`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mesh`` configuration in Central.

    Configure and retrieve Mesh profiles for Aruba Access Points, enabling wireless backhaul connectivity between mesh portals and mesh points. These profiles define mesh cluster settings, band selection, topology behavior, role selection, and recovery parameters used to build and maintain the mesh network. Use this API to retrieve the list of Mesh profiles.
    """
    return await _manage_resource(
        ctx,
        "mesh",
        "mesh",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mpsk-local -----


@tool(annotations=READ_ONLY)
async def central_get_mpsk_local(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mpsk-local`` configurations from Central.

    Configure the parameters of MPSK Local Profile. The MPSK Local operating mode allows to configure 24 pre-shared keys per SSID without an external policy engine like ClearPass Policy Manager. These local PSKs serve as an extension of the base pre-shared key functionality. MPSK Local operating mode is supported on the SSID profile to allow individual users or group of users to authenticate with per-device or per-group passphrase respectively. MPSK Local works only with wpa2-psk-aes encryption and not with any other PSK-based encryption. This feature is only applicable for AP.

    Parameters:
        name: Specific ``mpsk-local`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mpsk-local", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_mpsk_local(
    ctx: Context,
    name: Annotated[str, Field(description="``mpsk-local`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mpsk-local`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mpsk_local`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mpsk-local`` configuration in Central.

    Configure the parameters of MPSK Local Profile. The MPSK Local operating mode allows to configure 24 pre-shared keys per SSID without an external policy engine like ClearPass Policy Manager. These local PSKs serve as an extension of the base pre-shared key functionality. MPSK Local operating mode is supported on the SSID profile to allow individual users or group of users to authenticate with per-device or per-group passphrase respectively. MPSK Local works only with wpa2-psk-aes encryption and not with any other PSK-based encryption. This feature is only applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "mpsk-local",
        "mpsk-local",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- passpoint -----


@tool(annotations=READ_ONLY)
async def central_get_passpoint(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``passpoint`` configurations from Central.

    Passpoint is a WFA specification based upon the 802.11u protocol that provides wireless clients with a streamlined mechanism to discover and authenticate to suitable networks, and allows mobile users the ability to roam between partner networks without additional authentication.

    Parameters:
        name: Specific ``passpoint`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "passpoint", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_passpoint(
    ctx: Context,
    name: Annotated[str, Field(description="``passpoint`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``passpoint`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_passpoint`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``passpoint`` configuration in Central.

    Passpoint is a WFA specification based upon the 802.11u protocol that provides wireless clients with a streamlined mechanism to discover and authenticate to suitable networks, and allows mobile users the ability to roam between partner networks without additional authentication.
    """
    return await _manage_resource(
        ctx,
        "passpoint",
        "passpoint",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- radio -----


@tool(annotations=READ_ONLY)
async def central_get_radio(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``radio`` configurations from Central.

    The wireless access point broadcasts the network over radio frequency (RF) signals which wireless clients connect to. Radio configuration involves setting up and optimizing the various parameters of the AP radio to ensure efficient and reliable wireless communication. It includes some important configurations like radio bands, channels, rates and transmit power etc. This feature is only applicable for AP.

    Parameters:
        name: Specific ``radio`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "radios", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_radio(
    ctx: Context,
    name: Annotated[str, Field(description="``radio`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``radio`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_radio`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``radio`` configuration in Central.

    The wireless access point broadcasts the network over radio frequency (RF) signals which wireless clients connect to. Radio configuration involves setting up and optimizing the various parameters of the AP radio to ensure efficient and reliable wireless communication. It includes some important configurations like radio bands, channels, rates and transmit power etc. This feature is only applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "radios",
        "radio",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
