"""Aruba Central ``high-availability`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``high-availability.json`` vendor
spec file. Wrappers
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

# ----- gateway-clusters -----


@tool(annotations=READ_ONLY)
async def central_get_gateway_clusters(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``gateway-clusters`` configurations from Central.

    A Gateway cluster is a combination of multiple Aruba Gateways operating as a single entity to provide high availability and service continuity to the WLAN clients in a network. Gateway clusters provide full redundancy to APs and WLAN clients in the event of a failover. This API can be used to add/delete gateways into a cluster profile or setting the cluster profile configurations.

    Parameters:
        name: Specific ``gateway-clusters`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "gateway-clusters", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_gateway_clusters(
    ctx: Context,
    name: Annotated[str, Field(description="``gateway-clusters`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``gateway-clusters`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_gateway_clusters`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``gateway-clusters`` configuration in Central.

    A Gateway cluster is a combination of multiple Aruba Gateways operating as a single entity to provide high availability and service continuity to the WLAN clients in a network. Gateway clusters provide full redundancy to APs and WLAN clients in the event of a failover. This API can be used to add/delete gateways into a cluster profile or setting the cluster profile configurations.
    """
    return await _manage_resource(
        ctx,
        "gateway-clusters",
        "gateway-clusters",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- stacks -----


@tool(annotations=READ_ONLY)
async def central_get_stacks(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``stacks`` configurations from Central.

    A Gateway cluster is a combination of multiple Aruba Gateways operating as a single entity to provide high availability and service continuity to the WLAN clients in a network. Gateway clusters provide full redundancy to APs and WLAN clients in the event of a failover. This API can be used to add/delete gateways into a cluster profile or setting the cluster profile configurations.

    Parameters:
        name: Specific ``stacks`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "stacks", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_stacks(
    ctx: Context,
    name: Annotated[str, Field(description="``stacks`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``stacks`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_stacks`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``stacks`` configuration in Central.

    A Gateway cluster is a combination of multiple Aruba Gateways operating as a single entity to provide high availability and service continuity to the WLAN clients in a network. Gateway clusters provide full redundancy to APs and WLAN clients in the event of a failover. This API can be used to add/delete gateways into a cluster profile or setting the cluster profile configurations.
    """
    return await _manage_resource(
        ctx,
        "stacks",
        "stacks",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vsf-templates -----


@tool(annotations=READ_ONLY)
async def central_get_vsf_templates(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vsf-templates`` configurations from Central.

    A Gateway cluster is a combination of multiple Aruba Gateways operating as a single entity to provide high availability and service continuity to the WLAN clients in a network. Gateway clusters provide full redundancy to APs and WLAN clients in the event of a failover. This API can be used to add/delete gateways into a cluster profile or setting the cluster profile configurations.

    Parameters:
        name: Specific ``vsf-templates`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vsf-templates", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vsf_templates(
    ctx: Context,
    name: Annotated[str, Field(description="``vsf-templates`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vsf-templates`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vsf_templates`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vsf-templates`` configuration in Central.

    A Gateway cluster is a combination of multiple Aruba Gateways operating as a single entity to provide high availability and service continuity to the WLAN clients in a network. Gateway clusters provide full redundancy to APs and WLAN clients in the event of a failover. This API can be used to add/delete gateways into a cluster profile or setting the cluster profile configurations.
    """
    return await _manage_resource(
        ctx,
        "vsf-templates",
        "vsf-templates",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vsx-profiles -----


@tool(annotations=READ_ONLY)
async def central_get_vsx_profiles(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vsx-profiles`` configurations from Central.

    A Gateway cluster is a combination of multiple Aruba Gateways operating as a single entity to provide high availability and service continuity to the WLAN clients in a network. Gateway clusters provide full redundancy to APs and WLAN clients in the event of a failover. This API can be used to add/delete gateways into a cluster profile or setting the cluster profile configurations.

    Parameters:
        name: Specific ``vsx-profiles`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vsx-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vsx_profiles(
    ctx: Context,
    name: Annotated[str, Field(description="``vsx-profiles`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vsx-profiles`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vsx_profiles`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vsx-profiles`` configuration in Central.

    A Gateway cluster is a combination of multiple Aruba Gateways operating as a single entity to provide high availability and service continuity to the WLAN clients in a network. Gateway clusters provide full redundancy to APs and WLAN clients in the event of a failover. This API can be used to add/delete gateways into a cluster profile or setting the cluster profile configurations.
    """
    return await _manage_resource(
        ctx,
        "vsx-profiles",
        "vsx-profiles",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
