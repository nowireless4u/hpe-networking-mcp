"""Aruba Central ``firmware-policy`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``firmware-policy.json`` vendor
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

# ----- firmware-compliance -----


@tool(annotations=READ_ONLY)
async def central_get_firmware_compliance(
    ctx: Context,
) -> dict | list | str:
    """Get the ``firmware-compliance`` singleton configuration from Central.

    Firmware Policy configuration allows centralized control over firmware versions of all devices including APs, switches, and gateways across various scopes. Firmware upgrade APIs will function consistently in Central On-Prem deployments. In Central Cloud, API behavior may vary based on the customer’s deployment mode and the device type. Full API support is available for the 5G Bridge device type while support for other device types may differ.
    """
    return await _get_resource(ctx, "firmware-compliance", None)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_firmware_compliance(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``firmware-compliance`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_firmware_compliance`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``firmware-compliance`` configuration in Central.

    Firmware Policy configuration allows centralized control over firmware versions of all devices including APs, switches, and gateways across various scopes. Firmware upgrade APIs will function consistently in Central On-Prem deployments. In Central Cloud, API behavior may vary based on the customer’s deployment mode and the device type. Full API support is available for the 5G Bridge device type while support for other device types may differ.
    """
    return await _manage_resource(
        ctx,
        "firmware-compliance",
        "firmware-compliance",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
