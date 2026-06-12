"""Aruba Central ``telemetry`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``telemetry.json`` vendor
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

# ----- client-insight -----


@tool(capability=Capability.READ)
async def central_get_client_insight(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``client-insight`` configurations from Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.

    Parameters:
        name: Specific ``client-insight`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "client-insight", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_client_insight(
    ctx: Context,
    name: Annotated[str, Field(description="``client-insight`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``client-insight`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_client_insight`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``client-insight`` configuration in Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.
    """
    return await _manage_resource(
        ctx,
        "client-insight",
        "client-insight",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- client-iptracker -----


@tool(capability=Capability.READ)
async def central_get_client_iptracker(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``client-iptracker`` configurations from Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.

    Parameters:
        name: Specific ``client-iptracker`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "client-iptracker", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_client_iptracker(
    ctx: Context,
    name: Annotated[str, Field(description="``client-iptracker`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``client-iptracker`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_client_iptracker`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``client-iptracker`` configuration in Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.
    """
    return await _manage_resource(
        ctx,
        "client-iptracker",
        "client-iptracker",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- client-iptracker-interface -----


@tool(capability=Capability.READ)
async def central_get_client_iptracker_interface(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``client-iptracker-interface`` configurations from Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.

    Parameters:
        name: Specific ``client-iptracker-interface`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "client-iptracker-interface", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_client_iptracker_interface(
    ctx: Context,
    name: Annotated[
        str, Field(description="``client-iptracker-interface`` identifier (OpenAPI path param: ``name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``client-iptracker-interface`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_client_iptracker_interface`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``client-iptracker-interface`` configuration in Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.
    """
    return await _manage_resource(
        ctx,
        "client-iptracker-interface",
        "client-iptracker-interface",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- devicefingerprinting -----


@tool(capability=Capability.READ)
async def central_get_devicefingerprinting(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``devicefingerprinting`` configurations from Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.

    Parameters:
        name: Specific ``devicefingerprinting`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "devicefingerprinting", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_devicefingerprinting(
    ctx: Context,
    name: Annotated[str, Field(description="``devicefingerprinting`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``devicefingerprinting`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_devicefingerprinting`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``devicefingerprinting`` configuration in Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.
    """
    return await _manage_resource(
        ctx,
        "devicefingerprinting",
        "devicefingerprinting",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- devicefingerprinting-interface -----


@tool(capability=Capability.READ)
async def central_get_devicefingerprinting_interface(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``devicefingerprinting-interface`` configurations from Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.

    Parameters:
        name: Specific ``devicefingerprinting-interface`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "devicefingerprinting-interface", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_devicefingerprinting_interface(
    ctx: Context,
    name: Annotated[
        str, Field(description="``devicefingerprinting-interface`` identifier (OpenAPI path param: ``name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``devicefingerprinting-interface`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_devicefingerprinting_interface`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``devicefingerprinting-interface`` configuration in Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.
    """
    return await _manage_resource(
        ctx,
        "devicefingerprinting-interface",
        "devicefingerprinting-interface",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- devicefingerprinting-profile -----


@tool(capability=Capability.READ)
async def central_get_devicefingerprinting_profile(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``devicefingerprinting-profile`` configurations from Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.

    Parameters:
        name: Specific ``devicefingerprinting-profile`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "devicefingerprinting-profile", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_devicefingerprinting_profile(
    ctx: Context,
    name: Annotated[
        str, Field(description="``devicefingerprinting-profile`` identifier (OpenAPI path param: ``name``).")
    ],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``devicefingerprinting-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_devicefingerprinting_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``devicefingerprinting-profile`` configuration in Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.
    """
    return await _manage_resource(
        ctx,
        "devicefingerprinting-profile",
        "devicefingerprinting-profile",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- flow-tracking -----


@tool(capability=Capability.READ)
async def central_get_flow_tracking(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``flow-tracking`` configurations from Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.

    Parameters:
        name: Specific ``flow-tracking`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "flow-tracking", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_flow_tracking(
    ctx: Context,
    name: Annotated[str, Field(description="``flow-tracking`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``flow-tracking`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_flow_tracking`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``flow-tracking`` configuration in Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.
    """
    return await _manage_resource(
        ctx,
        "flow-tracking",
        "flow-tracking",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ipfix-flow-exporter -----


@tool(capability=Capability.READ)
async def central_get_ipfix_flow_exporter(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ipfix-flow-exporter`` configurations from Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.

    Parameters:
        name: Specific ``ipfix-flow-exporter`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ipfix-flow-exporter", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_ipfix_flow_exporter(
    ctx: Context,
    name: Annotated[str, Field(description="``ipfix-flow-exporter`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ipfix-flow-exporter`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ipfix_flow_exporter`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ipfix-flow-exporter`` configuration in Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.
    """
    return await _manage_resource(
        ctx,
        "ipfix-flow-exporter",
        "ipfix-flow-exporter",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- traffic-insight -----


@tool(capability=Capability.READ)
async def central_get_traffic_insight(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``traffic-insight`` configurations from Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.

    Parameters:
        name: Specific ``traffic-insight`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "traffic-insight", name)


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_traffic_insight(
    ctx: Context,
    name: Annotated[str, Field(description="``traffic-insight`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``traffic-insight`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_traffic_insight`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``traffic-insight`` configuration in Central.

    Configuration of Client-Insight. This feature aims at capturing L2, L3 and L4 stage on-boarding detail of the clients. The details published by client insight feature are consumed by HPE Aruba Networking (HPE ANW) Central to provide better insights into client activities.
    """
    return await _manage_resource(
        ctx,
        "traffic-insight",
        "traffic-insight",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
