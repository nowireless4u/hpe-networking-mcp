"""Aruba Central ``Application Experience`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``Application Experience`` OpenAPI tag-group. Wrappers
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

# ----- app-bandwidth-contract -----


@tool(annotations=READ_ONLY)
async def central_get_app_bandwidth_contract(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``app-bandwidth-contract`` configurations from Central.

    App Bandwidth Contracts. This container holds named profiles that define directional (UPSTREAM/DOWNSTREAM) bandwidth limits for application traffic. Each profile can include four different contract types: DPI application based contracts (app), DPI application category based contracts (app-category), WebCC reputation score/risk based contracts (web-reputation), and WebCC category based contracts (web-category). Each contract entry uses a composite key leaf that combines the identifier and direction. Bandwidth limits are configured by selecting bandwidth units (kbits/s or mbits/s) and specifying a bit-rate; the bit-rate is validated by a YANG must constraint with unit-specific ranges (256..2000000 for KBITS_PER_SEC and 1..2000 for MBITS_PER_SEC). The combined total number of entries across all four contract lists (app, app-category, web-reputation, and web-category) within a single profile must not exceed 32.

    Parameters:
        name: Specific ``app-bandwidth-contract`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "app-bandwidth-contracts", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_app_bandwidth_contract(
    ctx: Context,
    name: Annotated[str, Field(description="``app-bandwidth-contract`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``app-bandwidth-contract`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_app_bandwidth_contract`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``app-bandwidth-contract`` configuration in Central.

    App Bandwidth Contracts. This container holds named profiles that define directional (UPSTREAM/DOWNSTREAM) bandwidth limits for application traffic. Each profile can include four different contract types: DPI application based contracts (app), DPI application category based contracts (app-category), WebCC reputation score/risk based contracts (web-reputation), and WebCC category based contracts (web-category). Each contract entry uses a composite key leaf that combines the identifier and direction. Bandwidth limits are configured by selecting bandwidth units (kbits/s or mbits/s) and specifying a bit-rate; the bit-rate is validated by a YANG must constraint with unit-specific ranges (256..2000000 for KBITS_PER_SEC and 1..2000 for MBITS_PER_SEC). The combined total number of entries across all four contract lists (app, app-category, web-reputation, and web-category) within a single profile must not exceed 32.
    """
    return await _manage_resource(
        ctx,
        "app-bandwidth-contracts",
        "app-bandwidth-contract",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- app-recog-control -----


@tool(annotations=READ_ONLY)
async def central_get_app_recog_control(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``app-recog-control`` configurations from Central.

    Configuration of Application Recognition & Control (ARC) global profile(s). These APIs are applicable to AP, Gateway & CX-Switch devices only.

    Parameters:
        name: Specific ``app-recog-control`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "arc", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_app_recog_control(
    ctx: Context,
    name: Annotated[str, Field(description="``app-recog-control`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``app-recog-control`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_app_recog_control`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``app-recog-control`` configuration in Central.

    Configuration of Application Recognition & Control (ARC) global profile(s). These APIs are applicable to AP, Gateway & CX-Switch devices only.
    """
    return await _manage_resource(
        ctx,
        "arc",
        "app-recog-control",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dap -----


@tool(annotations=READ_ONLY)
async def central_get_dap(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dap`` configurations from Central.

    Dynamic application prioritization(DAP) is an application-aware QoS feature. Unlike traditional QoS methods that treat all traffic matching a classification the same, dynamic application prioritization adjusts based on each individual application’s needs. Dynamic Application Priorization automatically adjusts the advanced RF parameters such as uplink-scheduling to satisfy stringent SLAs of business-critical applications. This ensures improved user experience even in the most challenging RF conditions.

    Parameters:
        name: Specific ``dap`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dap", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dap(
    ctx: Context,
    name: Annotated[str, Field(description="``dap`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dap`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dap`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dap`` configuration in Central.

    Dynamic application prioritization(DAP) is an application-aware QoS feature. Unlike traditional QoS methods that treat all traffic matching a classification the same, dynamic application prioritization adjusts based on each individual application’s needs. Dynamic Application Priorization automatically adjusts the advanced RF parameters such as uplink-scheduling to satisfy stringent SLAs of business-critical applications. This ensures improved user experience even in the most challenging RF conditions.
    """
    return await _manage_resource(
        ctx,
        "dap",
        "dap",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dap-application -----


@tool(annotations=READ_ONLY)
async def central_get_dap_application(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dap-application`` configurations from Central.

    Configure a DAP application profile is for optimizing this application. One DAP SLA profile has to be configured under the DAP application profile knob to indicate how to optimize this application. The application profile number can be up to 32.

    Parameters:
        name: Specific ``dap-application`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dap-application", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dap_application(
    ctx: Context,
    name: Annotated[str, Field(description="``dap-application`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dap-application`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dap_application`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dap-application`` configuration in Central.

    Configure a DAP application profile is for optimizing this application. One DAP SLA profile has to be configured under the DAP application profile knob to indicate how to optimize this application. The application profile number can be up to 32.
    """
    return await _manage_resource(
        ctx,
        "dap-application",
        "dap-application",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- dap-sla -----


@tool(annotations=READ_ONLY)
async def central_get_dap_sla(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``dap-sla`` configurations from Central.

    Dynamic application prioritization(DAP) SLA profile allow to configure some SLA parameters such as latency, jitter, and so on, based on which some specific applications can be optimized. A name is a unique identifier that names an DAP SLA profile, the SLA profile numbers can be up to 32.

    Parameters:
        name: Specific ``dap-sla`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dap-sla", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_dap_sla(
    ctx: Context,
    name: Annotated[str, Field(description="``dap-sla`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``dap-sla`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_dap_sla`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``dap-sla`` configuration in Central.

    Dynamic application prioritization(DAP) SLA profile allow to configure some SLA parameters such as latency, jitter, and so on, based on which some specific applications can be optimized. A name is a unique identifier that names an DAP SLA profile, the SLA profile numbers can be up to 32.
    """
    return await _manage_resource(
        ctx,
        "dap-sla",
        "dap-sla",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
