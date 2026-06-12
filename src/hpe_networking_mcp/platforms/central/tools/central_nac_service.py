"""Aruba Central ``central-nac-service`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``central-nac-service.json`` vendor
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
    _operation_request,
)

# ----- cnac-certificate -----


@tool(capability=Capability.READ)
async def central_get_cnac_certificate(
    ctx: Context,
) -> dict | list | str:
    """Get the ``cnac-certificate`` singleton configuration from Central.

    This API retrieves a list of all user certificates based on the UPN. It requires a UPN as query parameter, which is a required input parameter.
    """
    return await _get_resource(ctx, "cnac-certificate", None)


# ----- cnac-dpp-reg -----


@tool(capability=Capability.READ)
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


@tool(capability=Capability.WRITE_DELETE)
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


@tool(capability=Capability.READ)
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


@tool(capability=Capability.READ)
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


@tool(capability=Capability.WRITE_DELETE)
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


@tool(capability=Capability.READ)
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


@tool(capability=Capability.WRITE_DELETE)
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


@tool(capability=Capability.READ)
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


@tool(capability=Capability.WRITE_DELETE)
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


@tool(capability=Capability.READ)
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


@tool(capability=Capability.WRITE_DELETE)
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


# ----- operation: cnac-certificate/revoke -----


@tool(capability=Capability.WRITE_DELETE)
async def central_cnac_certificate_revoke(
    ctx: Context,
    payload: Annotated[
        dict,
        Field(
            description=(
                "Request body for the ``cnac-certificate/revoke`` operation. "
                "Consult the Aruba Central config-model OpenAPI schema for the field set."
            )
        ),
    ],
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Central operation: cnac-certificate/revoke.

    Wraps ``POST network-config/v1alpha1/cnac-certificate/revoke``.
    """
    api_path = "network-config/v1alpha1/cnac-certificate/revoke"
    return await _operation_request(ctx, "POST", api_path, payload, confirmed, "cnac-certificate/revoke")


# ----- operation: cnac-image/upload -----


@tool(capability=Capability.WRITE_DELETE)
async def central_cnac_image_upload(
    ctx: Context,
    payload: Annotated[
        dict,
        Field(
            description=(
                "Request body for the ``cnac-image/upload`` operation. "
                "Consult the Aruba Central config-model OpenAPI schema for the field set."
            )
        ),
    ],
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Central operation: cnac-image/upload.

    Wraps ``POST network-config/v1alpha1/cnac-image/upload``.
    """
    api_path = "network-config/v1alpha1/cnac-image/upload"
    return await _operation_request(ctx, "POST", api_path, payload, confirmed, "cnac-image/upload")


# ----- operation: cnac-mac-reg/import -----


@tool(capability=Capability.WRITE_DELETE)
async def central_cnac_mac_reg_import(
    ctx: Context,
    payload: Annotated[
        dict,
        Field(
            description=(
                "Request body for the ``cnac-mac-reg/import`` operation. "
                "Consult the Aruba Central config-model OpenAPI schema for the field set."
            )
        ),
    ],
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Central operation: cnac-mac-reg/import.

    Wraps ``POST network-config/v1alpha1/cnac-mac-reg/import``.
    """
    api_path = "network-config/v1alpha1/cnac-mac-reg/import"
    return await _operation_request(ctx, "POST", api_path, payload, confirmed, "cnac-mac-reg/import")


# ----- operation: cnac-named-mpsk-reg/import -----


@tool(capability=Capability.WRITE_DELETE)
async def central_cnac_named_mpsk_reg_import(
    ctx: Context,
    payload: Annotated[
        dict,
        Field(
            description=(
                "Request body for the ``cnac-named-mpsk-reg/import`` operation. "
                "Consult the Aruba Central config-model OpenAPI schema for the field set."
            )
        ),
    ],
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Central operation: cnac-named-mpsk-reg/import.

    Wraps ``POST network-config/v1alpha1/cnac-named-mpsk-reg/import``.
    """
    api_path = "network-config/v1alpha1/cnac-named-mpsk-reg/import"
    return await _operation_request(ctx, "POST", api_path, payload, confirmed, "cnac-named-mpsk-reg/import")


# ----- operation: cnac-image/download/{image-id} -----


@tool(capability=Capability.READ)
async def central_get_cnac_image_download(
    ctx: Context,
    image_id: Annotated[str, Field(description="Path parameter (OpenAPI: ``image-id``).")],
) -> dict | str:
    """This API downloads an image from Central NAC.

    Wraps ``GET network-config/v1alpha1/cnac-image/download/{image-id}``.

    Parameters:
        image_id: Path parameter (OpenAPI path param: ``image-id``).
    """
    api_path = f"network-config/v1alpha1/cnac-image/download/{image_id}"
    return await _operation_request(ctx, "GET", api_path)


# ----- operation: cnac-job/{job-id}/error -----


@tool(capability=Capability.READ)
async def central_get_cnac_job_error(
    ctx: Context,
    job_id: Annotated[str, Field(description="Path parameter (OpenAPI: ``job-id``).")],
) -> dict | str:
    """This API is used to start the download of the error file from a prior import operation.

    Wraps ``GET network-config/v1alpha1/cnac-job/{job-id}/error``.

    Parameters:
        job_id: Path parameter (OpenAPI path param: ``job-id``).
    """
    api_path = f"network-config/v1alpha1/cnac-job/{job_id}/error"
    return await _operation_request(ctx, "GET", api_path)


# ----- operation: cnac-job/{job-id}/input -----


@tool(capability=Capability.READ)
async def central_get_cnac_job_input(
    ctx: Context,
    job_id: Annotated[str, Field(description="Path parameter (OpenAPI: ``job-id``).")],
) -> dict | str:
    """This API is used to start the download of the input file from a prior import operation.

    Wraps ``GET network-config/v1alpha1/cnac-job/{job-id}/input``.

    Parameters:
        job_id: Path parameter (OpenAPI path param: ``job-id``).
    """
    api_path = f"network-config/v1alpha1/cnac-job/{job_id}/input"
    return await _operation_request(ctx, "GET", api_path)


# ----- operation: cnac-job/{job-id}/status -----


@tool(capability=Capability.READ)
async def central_get_cnac_job_status(
    ctx: Context,
    job_id: Annotated[str, Field(description="Path parameter (OpenAPI: ``job-id``).")],
) -> dict | str:
    """This API is used to get the detail of an import or export operation based on job id.

    Wraps ``GET network-config/v1alpha1/cnac-job/{job-id}/status``.

    Parameters:
        job_id: Path parameter (OpenAPI path param: ``job-id``).
    """
    api_path = f"network-config/v1alpha1/cnac-job/{job_id}/status"
    return await _operation_request(ctx, "GET", api_path)


# ----- operation: cnac-mac-reg/export -----


@tool(capability=Capability.READ)
async def central_get_cnac_mac_reg_export(
    ctx: Context,
) -> dict | str:
    """This API exports the MAC csv file from Central NAC.

    Wraps ``GET network-config/v1alpha1/cnac-mac-reg/export``.
    """
    api_path = "network-config/v1alpha1/cnac-mac-reg/export"
    return await _operation_request(ctx, "GET", api_path)


# ----- operation: cnac-named-mpsk-reg/export -----


@tool(capability=Capability.READ)
async def central_get_cnac_named_mpsk_reg_export(
    ctx: Context,
) -> dict | str:
    """This API exports the Named MPSK csv file from Central NAC.

    Wraps ``GET network-config/v1alpha1/cnac-named-mpsk-reg/export``.
    """
    api_path = "network-config/v1alpha1/cnac-named-mpsk-reg/export"
    return await _operation_request(ctx, "GET", api_path)


# ----- operation: cnac-visitor/export -----


@tool(capability=Capability.READ)
async def central_get_cnac_visitor_export(
    ctx: Context,
) -> dict | str:
    """This API exports the visitor csv file from Central NAC.

    Wraps ``GET network-config/v1alpha1/cnac-visitor/export``.
    """
    api_path = "network-config/v1alpha1/cnac-visitor/export"
    return await _operation_request(ctx, "GET", api_path)


# ----- operation: cnac-static-tags/usage -----


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_cnac_static_tags_usage(
    ctx: Context,
    payload: Annotated[
        dict,
        Field(
            description=(
                "Request body for the ``cnac-static-tags/usage`` operation. "
                "Consult the Aruba Central config-model OpenAPI schema for the field set."
            )
        ),
    ],
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Central operation: cnac-static-tags/usage.

    Wraps ``POST network-config/v1alpha1/cnac-static-tags/usage``.
    """
    api_path = "network-config/v1alpha1/cnac-static-tags/usage"
    return await _operation_request(ctx, "POST", api_path, payload, confirmed, "cnac-static-tags/usage")
