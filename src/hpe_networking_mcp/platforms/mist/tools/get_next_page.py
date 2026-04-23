"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from typing import Annotated

from fastmcp.exceptions import ToolError
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.mist._registry import tool
from hpe_networking_mcp.platforms.mist.client import (
    format_response,
    get_apisession,
    handle_network_error,
    process_response,
)


@tool(
    name="mist_get_next_page",
    description=("Retrieve the next page of results using the '_next' URL returned by a previous tool call."),
    tags={"info"},
    annotations={
        "title": "Get Next Page",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_next_page(
    url: Annotated[
        str,
        Field(description="The '_next' URL from a previous response"),
    ],
) -> dict | list | str:
    """Retrieve the next page of results using the '_next' URL."""

    logger.debug("Tool get_next_page called")

    apisession, response_format = await get_apisession()

    try:
        response = apisession.mist_get(url)
        await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
