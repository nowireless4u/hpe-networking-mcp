"""Aruba Central ``application-experience`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``application-experience.json`` vendor
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

# ----- app-bandwidth-contracts -----


@tool(capability=Capability.READ)
async def central_get_app_bandwidth_contracts(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``app-bandwidth-contracts`` configurations from Central.

    App Bandwidth Contracts. This container holds named profiles that define directional (UPSTREAM/DOWNSTREAM) bandwidth limits for application traffic. Each profile can include four different contract types: DPI application based contracts (app), DPI application category based contracts (app-category), WebCC reputation score/risk based contracts (web-reputation), and WebCC category based contracts (web-category). Each contract entry uses a composite key leaf that combines the identifier and direction. Bandwidth limits are configured by selecting bandwidth units (kbits/s or mbits/s) and specifying a bit-rate; the bit-rate is validated by a YANG must constraint with unit-specific ranges (256..2000000 for KBITS_PER_SEC and 1..2000 for MBITS_PER_SEC). The combined total number of entries across all four contract lists (app, app-category, web-reputation, and web-category) within a single profile must not exceed 32.

    Parameters:
        name: Specific ``app-bandwidth-contracts`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "app-bandwidth-contracts", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_app_bandwidth_contracts(
    ctx: Context,
    name: Annotated[str, Field(description="``app-bandwidth-contracts`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``app-bandwidth-contracts`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_app_bandwidth_contracts`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``app-bandwidth-contracts`` configuration in Central.

    App Bandwidth Contracts. This container holds named profiles that define directional (UPSTREAM/DOWNSTREAM) bandwidth limits for application traffic. Each profile can include four different contract types: DPI application based contracts (app), DPI application category based contracts (app-category), WebCC reputation score/risk based contracts (web-reputation), and WebCC category based contracts (web-category). Each contract entry uses a composite key leaf that combines the identifier and direction. Bandwidth limits are configured by selecting bandwidth units (kbits/s or mbits/s) and specifying a bit-rate; the bit-rate is validated by a YANG must constraint with unit-specific ranges (256..2000000 for KBITS_PER_SEC and 1..2000 for MBITS_PER_SEC). The combined total number of entries across all four contract lists (app, app-category, web-reputation, and web-category) within a single profile must not exceed 32.
    """
    return await _manage_resource(
        ctx,
        "app-bandwidth-contracts",
        "app-bandwidth-contracts",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- arc -----


@tool(capability=Capability.READ)
async def central_get_arc(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``arc`` configurations from Central.

    App Bandwidth Contracts. This container holds named profiles that define directional (UPSTREAM/DOWNSTREAM) bandwidth limits for application traffic. Each profile can include four different contract types: DPI application based contracts (app), DPI application category based contracts (app-category), WebCC reputation score/risk based contracts (web-reputation), and WebCC category based contracts (web-category). Each contract entry uses a composite key leaf that combines the identifier and direction. Bandwidth limits are configured by selecting bandwidth units (kbits/s or mbits/s) and specifying a bit-rate; the bit-rate is validated by a YANG must constraint with unit-specific ranges (256..2000000 for KBITS_PER_SEC and 1..2000 for MBITS_PER_SEC). The combined total number of entries across all four contract lists (app, app-category, web-reputation, and web-category) within a single profile must not exceed 32.

    Parameters:
        name: Specific ``arc`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "arc", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_arc(
    ctx: Context,
    name: Annotated[str, Field(description="``arc`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``arc`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_arc`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``arc`` configuration in Central.

    App Bandwidth Contracts. This container holds named profiles that define directional (UPSTREAM/DOWNSTREAM) bandwidth limits for application traffic. Each profile can include four different contract types: DPI application based contracts (app), DPI application category based contracts (app-category), WebCC reputation score/risk based contracts (web-reputation), and WebCC category based contracts (web-category). Each contract entry uses a composite key leaf that combines the identifier and direction. Bandwidth limits are configured by selecting bandwidth units (kbits/s or mbits/s) and specifying a bit-rate; the bit-rate is validated by a YANG must constraint with unit-specific ranges (256..2000000 for KBITS_PER_SEC and 1..2000 for MBITS_PER_SEC). The combined total number of entries across all four contract lists (app, app-category, web-reputation, and web-category) within a single profile must not exceed 32.
    """
    return await _manage_resource(
        ctx,
        "arc",
        "arc",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
