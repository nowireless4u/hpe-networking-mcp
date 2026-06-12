"""Aruba Central ``gateway-clustering-orchestration`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``gateway-clustering-orchestration.json`` vendor
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

# ----- gw-cluster-intent-config -----


@tool(capability=Capability.READ)
async def central_get_gw_cluster_intent_config(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``gw-cluster-intent-config`` configurations from Central.

    Gateway Cluster Intent Service (GCIS) enables policy-driven orchestration of gateway clusters across organizational scopes such as global and site levels. Unlike manual cluster configuration, GCIS automatically forms clusters based on scope hierarchy and cluster-mode settings. This API can be used to create, modify, or delete cluster intent profiles with configurations for cluster-mode, multicast VLAN, heartbeat thresholds, IPv6 enablement, and CoA-VRRP settings.

    Parameters:
        name: Specific ``gw-cluster-intent-config`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "gw-cluster-intent-config", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_gw_cluster_intent_config(
    ctx: Context,
    name: Annotated[str, Field(description="``gw-cluster-intent-config`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``gw-cluster-intent-config`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_gw_cluster_intent_config`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``gw-cluster-intent-config`` configuration in Central.

    Gateway Cluster Intent Service (GCIS) enables policy-driven orchestration of gateway clusters across organizational scopes such as global and site levels. Unlike manual cluster configuration, GCIS automatically forms clusters based on scope hierarchy and cluster-mode settings. This API can be used to create, modify, or delete cluster intent profiles with configurations for cluster-mode, multicast VLAN, heartbeat thresholds, IPv6 enablement, and CoA-VRRP settings.
    """
    return await _manage_resource(
        ctx,
        "gw-cluster-intent-config",
        "gw-cluster-intent-config",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
