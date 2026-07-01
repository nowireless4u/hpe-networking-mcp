"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/location-management.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``location-management``   Tag: ``locations``   Operations: 13
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_delete_locations_v1_locations_id",
    description="DELETE /locations/v1/locations/{id}\n\ndeleteLocation\n\nDelete a location",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_locations_v1_locations_id(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="The unique identifier for the location. For example, `945e70ec-b043-4cad-9ed0-069c06fdb8af`."
        ),
    ],
) -> Any:
    path = f"/locations/v1/locations/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_locations_v1_locations",
    description="GET /locations/v1/locations\n\nlistAllLocations\n\nLists all locations",
    capability=Capability.READ,
)
async def greenlake_get_locations_v1_locations(
    ctx: Context,
    limit: Annotated[int, Field(description="The maximum number of results to be returned.")],
    offset: Annotated[
        int | None, Field(default=None, description="The zero-based resource offset to start the response from.")
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0. <br><br>This API can be filtered by `name`. <br><br>**NOTE:** The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL. The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. <br><br>",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        "/locations/v1/locations",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_locations_v1_locations_address_revgeocode",
    description="GET /locations/v1/locations/address/revgeocode\n\nreverseGeocode\n\nRetrieve location from latitude and longitude.",
    capability=Capability.READ,
)
async def greenlake_get_locations_v1_locations_address_revgeocode(
    ctx: Context,
    latitude: Annotated[str, Field(description="Provide a latitude coordinate.")],
    longitude: Annotated[str, Field(description="Provide a longitude coordinate.")],
    language: Annotated[
        str | None,
        Field(
            default=None,
            description="(Optional) Specify a language code to return the location information in that language. The default is English.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if latitude is not None:
        query_params["latitude"] = latitude
    if longitude is not None:
        query_params["longitude"] = longitude
    if language is not None:
        query_params["language"] = language
    return await greenlake_request(
        ctx,
        "GET",
        "/locations/v1/locations/address/revgeocode",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_locations_v1_locations_async_operation_id",
    description="GET /locations/v1/locations/async-operation/{id}\n\ngetCsvUploadStatus\n\nRetrieve a CSV upload status",
    capability=Capability.READ,
)
async def greenlake_get_locations_v1_locations_async_operation_id(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="The unique indentifier of the async operation location ID. For example, `945e70ec-b043-4cad-9ed0-069c06fdb8af`."
        ),
    ],
) -> Any:
    path = f"/locations/v1/locations/async-operation/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_locations_v1_locations_id",
    description="GET /locations/v1/locations/{id}\n\ngetLocationBy\n\nRetrieve a location",
    capability=Capability.READ,
)
async def greenlake_get_locations_v1_locations_id(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="The unique indentifier of the location. For example, `945e70ec-b043-4cad-9ed0-069c06fdb8af`."
        ),
    ],
) -> Any:
    path = f"/locations/v1/locations/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_locations_v1_locations_status",
    description="GET /locations/v1/locations/status\n\ngetLocationServiceStatusV1\n\nLocations Management service status",
    capability=Capability.READ,
)
async def greenlake_get_locations_v1_locations_status(
    ctx: Context,
) -> Any:
    return await greenlake_request(
        ctx,
        "GET",
        "/locations/v1/locations/status",
    )


@tool(
    name="greenlake_get_locations_v1_locations_tags",
    description="GET /locations/v1/locations/tags\n\nlistAllTags\n\nGet tags for a workspace",
    capability=Capability.READ,
)
async def greenlake_get_locations_v1_locations_tags(
    ctx: Context,
    limit: Annotated[int, Field(description="The maximum number of results to be returned.")],
    offset: Annotated[
        int | None, Field(default=None, description="The zero-based resource offset to start the response from.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/locations/v1/locations/tags",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_locations_v1_locations_tags_id",
    description="GET /locations/v1/locations/tags/{id}\n\nlistTagsById\n\nRetrieves tags for given a location",
    capability=Capability.READ,
)
async def greenlake_get_locations_v1_locations_tags_id(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="The unique identifier of the location. For example, `945e70ec-b043-4cad-9ed0-069c06fdb8af`."
        ),
    ],
) -> Any:
    path = f"/locations/v1/locations/tags/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_locations_v1_locations_id",
    description="PATCH /locations/v1/locations/{id}\n\nUpdateLocation\n\nUpdate a location",
    capability=Capability.WRITE,
)
async def greenlake_patch_locations_v1_locations_id(
    ctx: Context,
    id: Annotated[str, Field(description="The unique identifier for the location.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/locations/v1/locations/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_patch_locations_v1_locations_tags",
    description="PATCH /locations/v1/locations/tags\n\nUpdateTags\n\nCreate or delete a tag",
    capability=Capability.WRITE,
)
async def greenlake_patch_locations_v1_locations_tags(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "PATCH",
        "/locations/v1/locations/tags",
        body=body,
    )


@tool(
    name="greenlake_patch_locations_v1_locations_update_id",
    description="PATCH /locations/v1/locations/update/{id}\n\nmanageLocation\n\nManage a location",
    capability=Capability.WRITE,
)
async def greenlake_patch_locations_v1_locations_update_id(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="The unique identifier for the location. For example, `945e70ec-b043-4cad-9ed0-069c06fdb8af`."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/locations/v1/locations/update/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_locations_v1_locations",
    description="POST /locations/v1/locations\n\nCreateLocation\n\nCreate a Location",
    capability=Capability.WRITE,
)
async def greenlake_post_locations_v1_locations(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/locations/v1/locations",
        body=body,
    )


@tool(
    name="greenlake_post_locations_v1_locations_locations_csv_upload",
    description="POST /locations/v1/locations/locations-csv-upload\n\nCreateLocationCsv\n\nCreate locations using CSV file",
    capability=Capability.WRITE,
)
async def greenlake_post_locations_v1_locations_locations_csv_upload(
    ctx: Context,
    body: Annotated[list[Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/locations/v1/locations/locations-csv-upload",
        body=body,
    )
