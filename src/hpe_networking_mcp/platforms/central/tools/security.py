"""Aruba Central ``security`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``security.json`` vendor
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

# ----- aaa-profile -----


@tool(annotations=READ_ONLY)
async def central_get_aaa_profile(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``aaa-profile`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``aaa-profile`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "aaa-profile", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_aaa_profile(
    ctx: Context,
    name: Annotated[str, Field(description="``aaa-profile`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``aaa-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_aaa_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``aaa-profile`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "aaa-profile",
        "aaa-profile",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- auth-server-global-config -----


@tool(annotations=READ_ONLY)
async def central_get_auth_server_global_config(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``auth-server-global-config`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``auth-server-global-config`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "auth-server-global-config", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_auth_server_global_config(
    ctx: Context,
    name: Annotated[str, Field(description="``auth-server-global-config`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``auth-server-global-config`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_auth_server_global_config`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``auth-server-global-config`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "auth-server-global-config",
        "auth-server-global-config",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- auth-servers -----


@tool(annotations=READ_ONLY)
async def central_get_auth_servers(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``auth-servers`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``auth-servers`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "auth-servers", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_auth_servers(
    ctx: Context,
    name: Annotated[str, Field(description="``auth-servers`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``auth-servers`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_auth_servers`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``auth-servers`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "auth-servers",
        "auth-servers",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- auth-survivability -----


@tool(annotations=READ_ONLY)
async def central_get_auth_survivability(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``auth-survivability`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``auth-survivability`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "auth-survivability", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_auth_survivability(
    ctx: Context,
    name: Annotated[str, Field(description="``auth-survivability`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``auth-survivability`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_auth_survivability`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``auth-survivability`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "auth-survivability",
        "auth-survivability",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- bcn-rpt-req-profiles -----


@tool(annotations=READ_ONLY)
async def central_get_bcn_rpt_req_profiles(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``bcn-rpt-req-profiles`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``bcn-rpt-req-profiles`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "bcn-rpt-req-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_bcn_rpt_req_profiles(
    ctx: Context,
    name: Annotated[str, Field(description="``bcn-rpt-req-profiles`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``bcn-rpt-req-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_bcn_rpt_req_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``bcn-rpt-req-profiles`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "bcn-rpt-req-profiles",
        "bcn-rpt-req-profiles",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- captive-portal -----


@tool(annotations=READ_ONLY)
async def central_get_captive_portal(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``captive-portal`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``captive-portal`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "captive-portal", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_captive_portal(
    ctx: Context,
    name: Annotated[str, Field(description="``captive-portal`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``captive-portal`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_captive_portal`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``captive-portal`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "captive-portal",
        "captive-portal",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- certificate-rcp -----


@tool(annotations=READ_ONLY)
async def central_get_certificate_rcp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``certificate-rcp`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``certificate-rcp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "certificate-rcp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_certificate_rcp(
    ctx: Context,
    name: Annotated[str, Field(description="``certificate-rcp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``certificate-rcp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_certificate_rcp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``certificate-rcp`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "certificate-rcp",
        "certificate-rcp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- certificate-store -----


@tool(annotations=READ_ONLY)
async def central_get_certificate_store(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``certificate-store`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``certificate-store`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "certificate-store", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_certificate_store(
    ctx: Context,
    name: Annotated[str, Field(description="``certificate-store`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``certificate-store`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_certificate_store`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``certificate-store`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "certificate-store",
        "certificate-store",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- certificate-usage -----


@tool(annotations=READ_ONLY)
async def central_get_certificate_usage(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``certificate-usage`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``certificate-usage`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "certificate-usage", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_certificate_usage(
    ctx: Context,
    name: Annotated[str, Field(description="``certificate-usage`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``certificate-usage`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_certificate_usage`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``certificate-usage`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "certificate-usage",
        "certificate-usage",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- certificates -----


@tool(annotations=READ_ONLY)
async def central_get_certificates(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``certificates`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``certificates`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "certificates", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_certificates(
    ctx: Context,
    name: Annotated[str, Field(description="``certificates`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``certificates`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_certificates`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``certificates`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "certificates",
        "certificates",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- copp -----


@tool(annotations=READ_ONLY)
async def central_get_copp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``copp`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``copp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "copp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_copp(
    ctx: Context,
    name: Annotated[str, Field(description="``copp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``copp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_copp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``copp`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "copp",
        "copp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- device-certificates -----


@tool(annotations=READ_ONLY)
async def central_get_device_certificates(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``device-certificates`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``device-certificates`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "device-certificates", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_device_certificates(
    ctx: Context,
    name: Annotated[str, Field(description="``device-certificates`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``device-certificates`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_device_certificates`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``device-certificates`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "device-certificates",
        "device-certificates",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dot11k-profiles -----


@tool(annotations=READ_ONLY)
async def central_get_dot11k_profiles(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dot11k-profiles`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``dot11k-profiles`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dot11k-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dot11k_profiles(
    ctx: Context,
    name: Annotated[str, Field(description="``dot11k-profiles`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dot11k-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dot11k_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dot11k-profiles`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "dot11k-profiles",
        "dot11k-profiles",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dot1xauth -----


@tool(annotations=READ_ONLY)
async def central_get_dot1xauth(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dot1xauth`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``dot1xauth`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dot1xauth", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dot1xauth(
    ctx: Context,
    name: Annotated[str, Field(description="``dot1xauth`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dot1xauth`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dot1xauth`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dot1xauth`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "dot1xauth",
        "dot1xauth",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dot1xsupp -----


@tool(annotations=READ_ONLY)
async def central_get_dot1xsupp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dot1xsupp`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``dot1xsupp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dot1xsupp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dot1xsupp(
    ctx: Context,
    name: Annotated[str, Field(description="``dot1xsupp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dot1xsupp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dot1xsupp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dot1xsupp`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "dot1xsupp",
        "dot1xsupp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- est-profiles -----


@tool(annotations=READ_ONLY)
async def central_get_est_profiles(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``est-profiles`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``est-profiles`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "est-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_est_profiles(
    ctx: Context,
    name: Annotated[str, Field(description="``est-profiles`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``est-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_est_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``est-profiles`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "est-profiles",
        "est-profiles",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- firewall -----


@tool(annotations=READ_ONLY)
async def central_get_firewall(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``firewall`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``firewall`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "firewall", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_firewall(
    ctx: Context,
    name: Annotated[str, Field(description="``firewall`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``firewall`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_firewall`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``firewall`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "firewall",
        "firewall",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- gw-certificate-usage -----


@tool(annotations=READ_ONLY)
async def central_get_gw_certificate_usage(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``gw-certificate-usage`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``gw-certificate-usage`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "gw-certificate-usage", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_gw_certificate_usage(
    ctx: Context,
    name: Annotated[str, Field(description="``gw-certificate-usage`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``gw-certificate-usage`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_gw_certificate_usage`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``gw-certificate-usage`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "gw-certificate-usage",
        "gw-certificate-usage",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- internal-user -----


@tool(annotations=READ_ONLY)
async def central_get_internal_user(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``internal-user`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``internal-user`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "internal-user", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_internal_user(
    ctx: Context,
    name: Annotated[str, Field(description="``internal-user`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``internal-user`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_internal_user`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``internal-user`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "internal-user",
        "internal-user",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- keychains -----


@tool(annotations=READ_ONLY)
async def central_get_keychains(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``keychains`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``keychains`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "keychains", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_keychains(
    ctx: Context,
    name: Annotated[str, Field(description="``keychains`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``keychains`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_keychains`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``keychains`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "keychains",
        "keychains",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mac-lockout -----


@tool(annotations=READ_ONLY)
async def central_get_mac_lockout(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mac-lockout`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``mac-lockout`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mac-lockout", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_mac_lockout(
    ctx: Context,
    name: Annotated[str, Field(description="``mac-lockout`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mac-lockout`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mac_lockout`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mac-lockout`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "mac-lockout",
        "mac-lockout",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- macauth -----


@tool(annotations=READ_ONLY)
async def central_get_macauth(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``macauth`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``macauth`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "macauth", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_macauth(
    ctx: Context,
    name: Annotated[str, Field(description="``macauth`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``macauth`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_macauth`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``macauth`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "macauth",
        "macauth",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- macsec -----


@tool(annotations=READ_ONLY)
async def central_get_macsec(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``macsec`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``macsec`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "macsec", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_macsec(
    ctx: Context,
    name: Annotated[str, Field(description="``macsec`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``macsec`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_macsec`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``macsec`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "macsec",
        "macsec",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mka -----


@tool(annotations=READ_ONLY)
async def central_get_mka(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mka`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``mka`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mka", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_mka(
    ctx: Context,
    name: Annotated[str, Field(description="``mka`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mka`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mka`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mka`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "mka",
        "mka",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- net-groups -----


@tool(annotations=READ_ONLY)
async def central_get_net_groups(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``net-groups`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``net-groups`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "net-groups", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_net_groups(
    ctx: Context,
    name: Annotated[str, Field(description="``net-groups`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``net-groups`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_net_groups`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``net-groups`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "net-groups",
        "net-groups",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- passpoint-identity -----


@tool(annotations=READ_ONLY)
async def central_get_passpoint_identity(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``passpoint-identity`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``passpoint-identity`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "passpoint-identity", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_passpoint_identity(
    ctx: Context,
    name: Annotated[str, Field(description="``passpoint-identity`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``passpoint-identity`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_passpoint_identity`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``passpoint-identity`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "passpoint-identity",
        "passpoint-identity",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- port-security -----


@tool(annotations=READ_ONLY)
async def central_get_port_security(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``port-security`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``port-security`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "port-security", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_port_security(
    ctx: Context,
    name: Annotated[str, Field(description="``port-security`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``port-security`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_port_security`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``port-security`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "port-security",
        "port-security",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- radius-modifiers -----


@tool(annotations=READ_ONLY)
async def central_get_radius_modifiers(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``radius-modifiers`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``radius-modifiers`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "radius-modifiers", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_radius_modifiers(
    ctx: Context,
    name: Annotated[str, Field(description="``radius-modifiers`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``radius-modifiers`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_radius_modifiers`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``radius-modifiers`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "radius-modifiers",
        "radius-modifiers",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- rrm-ie-profiles -----


@tool(annotations=READ_ONLY)
async def central_get_rrm_ie_profiles(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``rrm-ie-profiles`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``rrm-ie-profiles`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "rrm-ie-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_rrm_ie_profiles(
    ctx: Context,
    name: Annotated[str, Field(description="``rrm-ie-profiles`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``rrm-ie-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_rrm_ie_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``rrm-ie-profiles`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "rrm-ie-profiles",
        "rrm-ie-profiles",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- server-groups -----


@tool(annotations=READ_ONLY)
async def central_get_server_groups(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``server-groups`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``server-groups`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "server-groups", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_server_groups(
    ctx: Context,
    name: Annotated[str, Field(description="``server-groups`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``server-groups`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_server_groups`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``server-groups`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "server-groups",
        "server-groups",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- stateful-dot1x-profiles -----


@tool(annotations=READ_ONLY)
async def central_get_stateful_dot1x_profiles(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``stateful-dot1x-profiles`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``stateful-dot1x-profiles`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "stateful-dot1x-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_stateful_dot1x_profiles(
    ctx: Context,
    name: Annotated[str, Field(description="``stateful-dot1x-profiles`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``stateful-dot1x-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_stateful_dot1x_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``stateful-dot1x-profiles`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "stateful-dot1x-profiles",
        "stateful-dot1x-profiles",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ubt -----


@tool(annotations=READ_ONLY)
async def central_get_ubt(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ubt`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``ubt`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ubt", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ubt(
    ctx: Context,
    name: Annotated[str, Field(description="``ubt`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ubt`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ubt`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ubt`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "ubt",
        "ubt",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
