"""Aruba Central ``High Availability`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``High Availability`` OpenAPI tag-group. Wrappers
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

# ----- switch-stack -----


@tool(annotations=READ_ONLY)
async def central_get_switch_stack(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``switch-stack`` configurations from Central.

    Configure and Manage switch stacks. Switch Stack OR Virtual Switching Framework(VSF), defines a virtual switch, comprising multiple individual physical switches, inter-connected through standard Ethernet links. These physical switches will operate with one control plane, thereby visible to the peers as a virtual switch stack. Within the stack, one switch is the Conductor switch, which runs all the control plane software and manages the ASICs of all the stack members. A second switch can be configured as the Standby switch, which will take over as Conductor if the conductor fails. It is strongly recommended to configure a secondary member in the stack, since a stack with a standby offers resiliency and high-availability.

    Parameters:
        name: Specific ``switch-stack`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "stacks", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_switch_stack(
    ctx: Context,
    name: Annotated[str, Field(description="``switch-stack`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``switch-stack`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_switch_stack`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``switch-stack`` configuration in Central.

    Configure and Manage switch stacks. Switch Stack OR Virtual Switching Framework(VSF), defines a virtual switch, comprising multiple individual physical switches, inter-connected through standard Ethernet links. These physical switches will operate with one control plane, thereby visible to the peers as a virtual switch stack. Within the stack, one switch is the Conductor switch, which runs all the control plane software and manages the ASICs of all the stack members. A second switch can be configured as the Standby switch, which will take over as Conductor if the conductor fails. It is strongly recommended to configure a secondary member in the stack, since a stack with a standby offers resiliency and high-availability.
    """
    return await _manage_resource(
        ctx,
        "stacks",
        "switch-stack",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vsf-template -----


@tool(annotations=READ_ONLY)
async def central_get_vsf_template(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vsf-template`` configurations from Central.

    VSF template offers a standardized framework for provisioning multiple, similar stacks. It enables centralized management of stacks at a global or site level, allowing a single template to configure and maintain multiple stacks efficiently. Instead of managing each stack individually, changes made to the template are automatically applied to all stacks that are in sync with it. A stack may become out of sync with the template if: 1. A user manually modifies the stack configuration directly, bypassing the template. 2. Configuration changes are applied locally within the stack instead of through the central template.

    Parameters:
        name: Specific ``vsf-template`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vsf-templates", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vsf_template(
    ctx: Context,
    name: Annotated[str, Field(description="``vsf-template`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vsf-template`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vsf_template`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vsf-template`` configuration in Central.

    VSF template offers a standardized framework for provisioning multiple, similar stacks. It enables centralized management of stacks at a global or site level, allowing a single template to configure and maintain multiple stacks efficiently. Instead of managing each stack individually, changes made to the template are automatically applied to all stacks that are in sync with it. A stack may become out of sync with the template if: 1. A user manually modifies the stack configuration directly, bypassing the template. 2. Configuration changes are applied locally within the stack instead of through the central template.
    """
    return await _manage_resource(
        ctx,
        "vsf-templates",
        "vsf-template",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- vsx -----


@tool(annotations=READ_ONLY)
async def central_get_vsx(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``vsx`` configurations from Central.

    Aruba Virtual Switching Extension (VSX). VSX is a link aggregation technique, where two or more links across two switches are aggregated together to form a LAG which will act as a single logical interface. The IEEE standard 802.3ad, is limited to aggregating links on a single switch or device. The Virtual Switching Extension (VSX) feature uses a new proprietary technology to overcome this limitation and supports link aggregation for the links spanning across multiple switches in the same VRF. The two switches are connected through an inter switch link (ISL). VSX provides node-level redundancy in a network when one of the switches fails. The downstream device is configured as a 802.3ad LAG interface. Though the LAG is connected to two separate devices they are seen as a single device. The downstream devices can be any device that supports 802.3ad. In VSX, one device acts as primary and the other device acts as secondary.

    Parameters:
        name: Specific ``vsx`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "vsx-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_vsx(
    ctx: Context,
    name: Annotated[str, Field(description="``vsx`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``vsx`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_vsx`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``vsx`` configuration in Central.

    Aruba Virtual Switching Extension (VSX). VSX is a link aggregation technique, where two or more links across two switches are aggregated together to form a LAG which will act as a single logical interface. The IEEE standard 802.3ad, is limited to aggregating links on a single switch or device. The Virtual Switching Extension (VSX) feature uses a new proprietary technology to overcome this limitation and supports link aggregation for the links spanning across multiple switches in the same VRF. The two switches are connected through an inter switch link (ISL). VSX provides node-level redundancy in a network when one of the switches fails. The downstream device is configured as a 802.3ad LAG interface. Though the LAG is connected to two separate devices they are seen as a single device. The downstream devices can be any device that supports 802.3ad. In VSX, one device acts as primary and the other device acts as secondary.
    """
    return await _manage_resource(
        ctx,
        "vsx-profiles",
        "vsx",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
