"""Aruba Central ``tunnels`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``tunnels.json`` vendor
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

# ----- tunnel -----


@tool(annotations=READ_ONLY)
async def central_get_tunnel(
    ctx: Context,
    id: str | None = None,
) -> dict | list | str:
    """Get ``tunnel`` configurations from Central.

    Configure Tunnel Interface. Tunnel creates virtual point to point link between two devices encapsulating various protocols within an IP network. Supported modes for tunnels are GRE, IP6in4, IP6in6, IPsec and VXLAN.

    Parameters:
        id: Specific ``tunnel`` identifier (OpenAPI path param: ``id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "tunnel", id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_tunnel(
    ctx: Context,
    id: Annotated[str, Field(description="``tunnel`` identifier (OpenAPI path param: ``id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``tunnel`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_tunnel`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``tunnel`` configuration in Central.

    Configure Tunnel Interface. Tunnel creates virtual point to point link between two devices encapsulating various protocols within an IP network. Supported modes for tunnels are GRE, IP6in4, IP6in6, IPsec and VXLAN.
    """
    return await _manage_resource(
        ctx,
        "tunnel",
        "tunnel",
        id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- tunnel-groups -----


@tool(annotations=READ_ONLY)
async def central_get_tunnel_groups(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``tunnel-groups`` configurations from Central.

    Configure Tunnel Interface. Tunnel creates virtual point to point link between two devices encapsulating various protocols within an IP network. Supported modes for tunnels are GRE, IP6in4, IP6in6, IPsec and VXLAN.

    Parameters:
        name: Specific ``tunnel-groups`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "tunnel-groups", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_tunnel_groups(
    ctx: Context,
    name: Annotated[str, Field(description="``tunnel-groups`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``tunnel-groups`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_tunnel_groups`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``tunnel-groups`` configuration in Central.

    Configure Tunnel Interface. Tunnel creates virtual point to point link between two devices encapsulating various protocols within an IP network. Supported modes for tunnels are GRE, IP6in4, IP6in6, IPsec and VXLAN.
    """
    return await _manage_resource(
        ctx,
        "tunnel-groups",
        "tunnel-groups",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
