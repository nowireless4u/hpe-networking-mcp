"""Aruba Central ``central-nac-service`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``central-nac-service.json`` vendor
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

# ----- cnac-certificate -----


@tool(annotations=READ_ONLY)
async def central_get_cnac_certificate(
    ctx: Context,
) -> dict | list | str:
    """Get the ``cnac-certificate`` singleton configuration from Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.
    """
    return await _get_resource(ctx, "cnac-certificate", None)


# ----- cnac-dpp-reg -----


@tool(annotations=READ_ONLY)
async def central_get_cnac_dpp_reg(
    ctx: Context,
    id: str | None = None,
) -> dict | list | str:
    """Get ``cnac-dpp-reg`` configurations from Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.

    Parameters:
        id: Specific ``cnac-dpp-reg`` identifier (OpenAPI path param: ``id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "cnac-dpp-reg", id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cnac_dpp_reg(
    ctx: Context,
    id: Annotated[str, Field(description="``cnac-dpp-reg`` identifier (OpenAPI path param: ``id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cnac-dpp-reg`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cnac_dpp_reg`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cnac-dpp-reg`` configuration in Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.
    """
    return await _manage_resource(
        ctx,
        "cnac-dpp-reg",
        "cnac-dpp-reg",
        id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cnac-image -----


@tool(annotations=READ_ONLY)
async def central_get_cnac_image(
    ctx: Context,
    image_id: str | None = None,
) -> dict | list | str:
    """Get ``cnac-image`` configurations from Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.

    Parameters:
        image_id: Specific ``cnac-image`` identifier (OpenAPI path param: ``image-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "cnac-image", image_id)


# ----- cnac-job -----


@tool(annotations=READ_ONLY)
async def central_get_cnac_job(
    ctx: Context,
    job_id: str | None = None,
) -> dict | list | str:
    """Get ``cnac-job`` configurations from Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.

    Parameters:
        job_id: Specific ``cnac-job`` identifier (OpenAPI path param: ``job-id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "cnac-job", job_id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cnac_job(
    ctx: Context,
    job_id: Annotated[str, Field(description="``cnac-job`` identifier (OpenAPI path param: ``job-id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cnac-job`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cnac_job`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cnac-job`` configuration in Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.
    """
    return await _manage_resource(
        ctx,
        "cnac-job",
        "cnac-job",
        job_id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cnac-mac-reg -----


@tool(annotations=READ_ONLY)
async def central_get_cnac_mac_reg(
    ctx: Context,
    id: str | None = None,
) -> dict | list | str:
    """Get ``cnac-mac-reg`` configurations from Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.

    Parameters:
        id: Specific ``cnac-mac-reg`` identifier (OpenAPI path param: ``id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "cnac-mac-reg", id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cnac_mac_reg(
    ctx: Context,
    id: Annotated[str, Field(description="``cnac-mac-reg`` identifier (OpenAPI path param: ``id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cnac-mac-reg`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cnac_mac_reg`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cnac-mac-reg`` configuration in Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.
    """
    return await _manage_resource(
        ctx,
        "cnac-mac-reg",
        "cnac-mac-reg",
        id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cnac-named-mpsk-reg -----


@tool(annotations=READ_ONLY)
async def central_get_cnac_named_mpsk_reg(
    ctx: Context,
    id: str | None = None,
) -> dict | list | str:
    """Get ``cnac-named-mpsk-reg`` configurations from Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.

    Parameters:
        id: Specific ``cnac-named-mpsk-reg`` identifier (OpenAPI path param: ``id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "cnac-named-mpsk-reg", id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cnac_named_mpsk_reg(
    ctx: Context,
    id: Annotated[str, Field(description="``cnac-named-mpsk-reg`` identifier (OpenAPI path param: ``id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cnac-named-mpsk-reg`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cnac_named_mpsk_reg`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cnac-named-mpsk-reg`` configuration in Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.
    """
    return await _manage_resource(
        ctx,
        "cnac-named-mpsk-reg",
        "cnac-named-mpsk-reg",
        id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- cnac-visitor -----


@tool(annotations=READ_ONLY)
async def central_get_cnac_visitor(
    ctx: Context,
    id: str | None = None,
) -> dict | list | str:
    """Get ``cnac-visitor`` configurations from Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.

    Parameters:
        id: Specific ``cnac-visitor`` identifier (OpenAPI path param: ``id``). If omitted, returns all.
    """
    return await _get_resource(ctx, "cnac-visitor", id)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_cnac_visitor(
    ctx: Context,
    id: Annotated[str, Field(description="``cnac-visitor`` identifier (OpenAPI path param: ``id``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``cnac-visitor`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_cnac_visitor`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``cnac-visitor`` configuration in Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.
    """
    return await _manage_resource(
        ctx,
        "cnac-visitor",
        "cnac-visitor",
        id,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
