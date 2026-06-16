"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``brandCustomization``
Operations in this file: 8
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_delete_brand_customization",
    description="DELETE /brandCustomization\n\nTextCustomizationConfigDelete146\n\nDelete all brand customization configurations",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_brand_customization(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/brandCustomization",
        query_params=None,
    )


@tool(
    name="edgeconnect_delete_brand_customization_image",
    description="DELETE /brandCustomization/image\n\nimageDelete151\n\nDelete custom brand image and restore default",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_brand_customization_image(
    ctx: Context,
    type: Annotated[
        str,
        Field(
            description="The image customization type to delete. Specifies which custom brand image to remove and restore to default."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if type is not None:
        query_params["type"] = type
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/brandCustomization/image",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_brand_customization",
    description="GET /brandCustomization\n\nTextCustomizationConfigGet147\n\nRetrieve text brand customization configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_brand_customization(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/brandCustomization",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_brand_customization_image",
    description="GET /brandCustomization/image\n\nfileNameGet150\n\nRetrieve metadata for all uploaded custom brand images",
    capability=Capability.READ,
)
async def edgeconnect_get_brand_customization_image(
    ctx: Context,
    metaData: Annotated[
        bool,
        Field(description="Must be set to true to retrieve image metadata. If false or missing, returns 400 error."),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if metaData is not None:
        query_params["metaData"] = metaData
    return await edgeconnect_request(
        ctx,
        "GET",
        "/brandCustomization/image",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_brand_customization",
    description="POST /brandCustomization\n\nTextCustomizationConfigPost148\n\nCreate new text brand customization configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_brand_customization(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/brandCustomization",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_brand_customization_image",
    description="POST /brandCustomization/image\n\nimagePost152\n\nUpload a new custom brand image",
    capability=Capability.WRITE,
)
async def edgeconnect_post_brand_customization_image(
    ctx: Context,
    type: Annotated[
        str,
        Field(
            description="The image customization type to upload. Determines where the image will be displayed in the UI."
        ),
    ],
    qqfile: Annotated[
        str,
        Field(
            description="The file name for the uploaded image. Max 30 characters. Must have a valid image extension."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if type is not None:
        query_params["type"] = type
    if qqfile is not None:
        query_params["qqfile"] = qqfile
    return await edgeconnect_request(
        ctx,
        "POST",
        "/brandCustomization/image",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_brand_customization",
    description="PUT /brandCustomization\n\nTextCustomizationConfigPut149\n\nUpdate text brand customization configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_put_brand_customization(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/brandCustomization",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_brand_customization_image",
    description="PUT /brandCustomization/image\n\nimagePut153\n\nUpdate an existing custom brand image",
    capability=Capability.WRITE,
)
async def edgeconnect_put_brand_customization_image(
    ctx: Context,
    type: Annotated[
        str,
        Field(
            description="The image customization type to update. Determines where the image will be displayed in the UI."
        ),
    ],
    qqfile: Annotated[
        str,
        Field(description="The file name for the uploaded image. Must be ≤30 characters with a valid image extension."),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if type is not None:
        query_params["type"] = type
    if qqfile is not None:
        query_params["qqfile"] = qqfile
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/brandCustomization/image",
        query_params=query_params or None,
        body=body,
    )
