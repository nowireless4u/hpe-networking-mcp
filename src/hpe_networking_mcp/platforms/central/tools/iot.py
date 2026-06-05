"""Aruba Central ``iot`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``iot.json`` vendor
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

# ----- usb -----


@tool(annotations=READ_ONLY)
async def central_get_usb(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``usb`` configurations from Central.

    Config the global profile for USB parameters. Including a usb profile list and the acl rule profiles detail. a AP USB ACL profile policy including a acl-name and a rule list. The rule includes a USB vendor name and its related action is deny or permit. Such as vendor is Alcatel-L800, action is deny, it means the Alcatel-L800 USB dongle's data will be denied by AP.

    Parameters:
        name: Specific ``usb`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "usb", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_usb(
    ctx: Context,
    name: Annotated[str, Field(description="``usb`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``usb`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_usb`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``usb`` configuration in Central.

    Config the global profile for USB parameters. Including a usb profile list and the acl rule profiles detail. a AP USB ACL profile policy including a acl-name and a rule list. The rule includes a USB vendor name and its related action is deny or permit. Such as vendor is Alcatel-L800, action is deny, it means the Alcatel-L800 USB dongle's data will be denied by AP.
    """
    return await _manage_resource(
        ctx,
        "usb",
        "usb",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
