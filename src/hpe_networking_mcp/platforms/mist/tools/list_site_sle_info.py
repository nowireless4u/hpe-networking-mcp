"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from hpe_networking_mcp.platforms.mist.client import get_apisession
from hpe_networking_mcp.platforms.mist.client import process_response, handle_network_error
from hpe_networking_mcp.platforms.mist.client import format_response
from hpe_networking_mcp.platforms.mist._registry import mcp
from loguru import logger

from pydantic import Field
from typing import Annotated
from uuid import UUID
from enum import Enum


class Query_type(Enum):
    METRICS = "metrics"
    CLASSIFIERS = "classifiers"


class Scope(Enum):
    AP = "ap"
    CLIENT = "client"
    GATEWAY = "gateway"
    SITE = "site"
    SWITCH = "switch"


@mcp.tool(
    name="mist_list_site_sle_info",
    description="""List SLE metadata for a site scope. Use metrics to list available SLE metrics for a given scope, or classifiers to list the classifiers available for a specific metric.""",
    tags={"sles"},
    annotations={
        "title": "List site sle info",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def list_site_sle_info(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    query_type: Annotated[
        Query_type,
        Field(
            description="""Type of metadata to retrieve: metrics returns the list of available SLE metrics for the given scope; classifiers returns the list of classifiers for a specific metric (requires metric parameter)"""
        ),
    ],
    scope: Annotated[
        Scope,
        Field(
            description="""Scope of the SLE data: site, ap, client, gateway, or switch"""
        ),
    ],
    scope_id: Annotated[
        str,
        Field(
            description="""ID of the scoped object: `site_id` if `scope=site`; `device_id` if `scope=ap`, `switch`, or `gateway`; `MAC address` if `scope=client`"""
        ),
    ],
    metric: Annotated[
        str,
        Field(
            description="""SLE metric name to retrieve classifiers for. Required when query_type is classifiers. Use query_type=metrics first to discover available metric names""",
            default=None,
        ),
    ],
) -> dict | list | str:
    """List SLE metadata for a site scope. Use metrics to list available SLE metrics for a given scope, or classifiers to list the classifiers available for a specific metric."""

    logger.debug("Tool list_site_sle_info called")
    logger.debug(
        "Input Parameters: site_id: %s, query_type: %s, scope: %s, scope_id: %s, metric: %s",
        site_id,
        query_type,
        scope,
        scope_id,
        metric,
    )

    apisession, response_format = await get_apisession()

    try:
        object_type = query_type

        if object_type.value == "classifiers":
            if not metric:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": '`metric` parameter is required when `test` is "classifiers".',
                    }
                )

        match object_type.value:
            case "metrics":
                response = mistapi.api.v1.sites.sle.listSiteSlesMetrics(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                )
                await process_response(response)
            case "classifiers":
                response = mistapi.api.v1.sites.sle.listSiteSleMetricClassifiers(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                )
                await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Query_type]}",
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
