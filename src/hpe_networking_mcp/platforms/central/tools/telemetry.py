"""Aruba Central ``Telemetry`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``Telemetry`` OpenAPI tag-group. Wrappers
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

# ----- client-insight -----


@tool(annotations=READ_ONLY)
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


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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


@tool(annotations=READ_ONLY)
async def central_get_client_iptracker(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``client-iptracker`` configurations from Central.

    The Client IP tracking feature will learn and update the IP address of the access devices and clients connected to the switch. It can track the IP addresses of directly connected clients and clients connected to a downstream device such as a wireless access point. This feature is applicable to AOS-CX and AOS-S Switches.

    Parameters:
        name: Specific ``client-iptracker`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "client-iptracker", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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

    The Client IP tracking feature will learn and update the IP address of the access devices and clients connected to the switch. It can track the IP addresses of directly connected clients and clients connected to a downstream device such as a wireless access point. This feature is applicable to AOS-CX and AOS-S Switches.
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


@tool(annotations=READ_ONLY)
async def central_get_client_iptracker_interface(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``client-iptracker-interface`` configurations from Central.

    The Client IP tracking feature will learn and update the IP address of the access devices and clients connected to the interface. This feature is applicable to AOS-CX and AOS-S Switches.

    Parameters:
        name: Specific ``client-iptracker-interface`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "client-iptracker-interface", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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

    The Client IP tracking feature will learn and update the IP address of the access devices and clients connected to the interface. This feature is applicable to AOS-CX and AOS-S Switches.
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


@tool(annotations=READ_ONLY)
async def central_get_devicefingerprinting(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``devicefingerprinting`` configurations from Central.

    Device fingerprinting (DFP) collects the set of LLDP/CDP TLVs, DHCP options & HTTP user-agent details from the devices connected to the AOS-CX or AOS-S switches. These details are used to classify the end devices for device-type, vendor and operating systems using the fingerprinting database.

    Parameters:
        name: Specific ``devicefingerprinting`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "devicefingerprinting", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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

    Device fingerprinting (DFP) collects the set of LLDP/CDP TLVs, DHCP options & HTTP user-agent details from the devices connected to the AOS-CX or AOS-S switches. These details are used to classify the end devices for device-type, vendor and operating systems using the fingerprinting database.
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


@tool(annotations=READ_ONLY)
async def central_get_devicefingerprinting_interface(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``devicefingerprinting-interface`` configurations from Central.

    Device Fingerprinting Interface configuration of Aruba AOS-S and AOS-CX Switches.

    Parameters:
        name: Specific ``devicefingerprinting-interface`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "devicefingerprinting-interface", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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

    Device Fingerprinting Interface configuration of Aruba AOS-S and AOS-CX Switches.
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


@tool(annotations=READ_ONLY)
async def central_get_devicefingerprinting_profile(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``devicefingerprinting-profile`` configurations from Central.

    To enable DFP on a port, users need to configure a DFP profile with the set of protocol data that needs to be collected and associate it to the desired port or set of ports. Once the profile is applied on a port, switch will start monitoring the required packets from all the clients on that port and collects the configured protocol and their attributes.

    Parameters:
        name: Specific ``devicefingerprinting-profile`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "devicefingerprinting-profile", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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

    To enable DFP on a port, users need to configure a DFP profile with the set of protocol data that needs to be collected and associate it to the desired port or set of ports. Once the profile is applied on a port, switch will start monitoring the required packets from all the clients on that port and collects the configured protocol and their attributes.
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


@tool(annotations=READ_ONLY)
async def central_get_flow_tracking(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``flow-tracking`` configurations from Central.

    Flow Tracking is a common infrastructure to manage the IP Flow table . IP Flow table is used for session management of TCP/UDP/ICMP flows, which helps to create application aware network.

    Parameters:
        name: Specific ``flow-tracking`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "flow-tracking", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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

    Flow Tracking is a common infrastructure to manage the IP Flow table . IP Flow table is used for session management of TCP/UDP/ICMP flows, which helps to create application aware network.
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


@tool(annotations=READ_ONLY)
async def central_get_ipfix_flow_exporter(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ipfix-flow-exporter`` configurations from Central.

    IP Flow Information Export (IPFIX) flow exporter configurations. IPFIX is an embedded network flow analysis tool that compiles characteristic and measured properties of flows and sends flow reports to internal or external flow collectors.

    Parameters:
        name: Specific ``ipfix-flow-exporter`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ipfix-flow-exporter", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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

    IP Flow Information Export (IPFIX) flow exporter configurations. IPFIX is an embedded network flow analysis tool that compiles characteristic and measured properties of flows and sends flow reports to internal or external flow collectors.
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


@tool(annotations=READ_ONLY)
async def central_get_traffic_insight(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``traffic-insight`` configurations from Central.

    Configuration of Traffic Insight. Traffic insight allows to monitor large amount of data that it collects from various flow exporters like IPFIX and provides the ability to filter, aggregate and sort the data based on user flow monitor requests. Traffic insight tracks different monitor requests simultaneously and provides monitor reports per request. Enables flow monitoring on a traffic insight instance. A traffic insight instance consists of different monitor types. Following flow monitor types are supported: topN-flows - Monitors IP traffic flowing through the switch and captures topN volume flows. application-flows - Monitors client application flows and provides application level rx/tx counters, and also brings application visibility. raw-flows - Raw-flows Flow monitor provides uni-direction flow details for all apps or clients to CNX on-demand basis. It is used by CNX for trouble-shooting work-flow. dns-average-latency - Monitors dns request and response flows and provides average dns-latency details per client. dns-onboarding-latency - Monitors dns request and response flows and provides onboarding dns-latency details per client. workload-flows - Monitors unicast traffic flows and provides the rx/tx counters along with action for the flow. flows - Monitors unicast traffic flows and provides the rx/tx counters along with action for the flow.

    Parameters:
        name: Specific ``traffic-insight`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "traffic-insight", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
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

    Configuration of Traffic Insight. Traffic insight allows to monitor large amount of data that it collects from various flow exporters like IPFIX and provides the ability to filter, aggregate and sort the data based on user flow monitor requests. Traffic insight tracks different monitor requests simultaneously and provides monitor reports per request. Enables flow monitoring on a traffic insight instance. A traffic insight instance consists of different monitor types. Following flow monitor types are supported: topN-flows - Monitors IP traffic flowing through the switch and captures topN volume flows. application-flows - Monitors client application flows and provides application level rx/tx counters, and also brings application visibility. raw-flows - Raw-flows Flow monitor provides uni-direction flow details for all apps or clients to CNX on-demand basis. It is used by CNX for trouble-shooting work-flow. dns-average-latency - Monitors dns request and response flows and provides average dns-latency details per client. dns-onboarding-latency - Monitors dns request and response flows and provides onboarding dns-latency details per client. workload-flows - Monitors unicast traffic flows and provides the rx/tx counters along with action for the flow. flows - Monitors unicast traffic flows and provides the rx/tx counters along with action for the flow.
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
