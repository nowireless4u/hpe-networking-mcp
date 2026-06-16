"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``sse connector``
Operations in this file: 14
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
    name="edgeconnect_delete_third_party_services_sse_connector",
    description="DELETE /thirdPartyServices/sse/connector\n\ndeleteSseConnector\n\nUninstall SSE connector from an appliance",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_sse_connector(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/sse/connector",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_sse_connector_pool",
    description="DELETE /thirdPartyServices/sse/connectorPool\n\ndeleteSseConnectorPool\n\nDelete an SSE connector IP address pool",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_sse_connector_pool(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the connector pool to delete. Must reference an existing pool record in the database."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/sse/connectorPool",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sseimages_download",
    description="GET /sseimages/download\n\ndownloadSseImage\n\nDownload SSE connector image file",
    capability=Capability.READ,
)
async def edgeconnect_get_sseimages_download(
    ctx: Context,
    hash: Annotated[str, Field(description="UUID hash identifying the image download link.")],
) -> Any:
    query_params: dict[str, Any] = {}
    if hash is not None:
        query_params["hash"] = hash
    return await edgeconnect_request(
        ctx,
        "GET",
        "/sseimages/download",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sseimages_relnotes",
    description="GET /sseimages/relnotes\n\ndownloadSseReleaseNotes\n\nDownload SSE connector release notes",
    capability=Capability.READ,
)
async def edgeconnect_get_sseimages_relnotes(
    ctx: Context,
    version: Annotated[str, Field(description="Connector image version to retrieve release notes for.")],
) -> Any:
    query_params: dict[str, Any] = {}
    if version is not None:
        query_params["version"] = version
    return await edgeconnect_request(
        ctx,
        "GET",
        "/sseimages/relnotes",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_sse_connector",
    description="GET /thirdPartyServices/sse/connector\n\ngetSseConnector\n\nRetrieve SSE connector details for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_sse_connector(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/sse/connector",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_sse_connector_pool",
    description="GET /thirdPartyServices/sse/connectorPool\n\ngetSseConnectorPool\n\nRetrieve all SSE connector IP address pools",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_sse_connector_pool(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/sse/connectorPool",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_sse_connector_status",
    description="GET /thirdPartyServices/sse/connector/status\n\ngetConnectorStatus\n\nRetrieve SSE connector installation/uninstallation status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_sse_connector_status(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/sse/connector/status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_sse_image",
    description="GET /thirdPartyServices/sse/image\n\ngetSseConnectorImages\n\nRetrieve SSE connector images",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_sse_image(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/sse/image",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_sse_image_refresh",
    description="GET /thirdPartyServices/sse/image/refresh\n\nrefreshSseConnectorImagesFromPortal\n\nTrigger SSE connector image refresh from portal",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_sse_image_refresh(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/sse/image/refresh",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_sse_image_refresh_status",
    description="GET /thirdPartyServices/sse/image/refresh/status\n\ngetSseConnectorImagesRefreshStatus\n\nRetrieve SSE connector image refresh status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_sse_image_refresh_status(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/sse/image/refresh/status",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_sse_interfaces",
    description="GET /thirdPartyServices/sse/interfaces\n\ngetSseConnectorInterface\n\nRetrieve SSE connector loopback interface configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_sse_interfaces(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="Controls data source for interface details. When 'true' or omitted, retrieves from Orchestrator cache for faster response. When 'false', fetches directly from the appliance and updates cache.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/sse/interfaces",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_third_party_services_sse_connector",
    description="POST /thirdPartyServices/sse/connector\n\npostSseConnector\n\nInstall or upgrade SSE connector on an appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_sse_connector(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/sse/connector",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_sse_connector_pool",
    description="POST /thirdPartyServices/sse/connectorPool\n\npostSseConnectorPool\n\nCreate a new SSE connector IP address pool",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_sse_connector_pool(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/sse/connectorPool",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_third_party_services_sse_connector_pool",
    description="PUT /thirdPartyServices/sse/connectorPool\n\nputSseConnectorPool\n\nUpdate an existing SSE connector IP address pool",
    capability=Capability.WRITE,
)
async def edgeconnect_put_third_party_services_sse_connector_pool(
    ctx: Context,
    id: Annotated[
        int,
        Field(description="Unique identifier of the connector pool to update. Must reference an existing pool record."),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/thirdPartyServices/sse/connectorPool",
        query_params=query_params or None,
        body=body,
    )
