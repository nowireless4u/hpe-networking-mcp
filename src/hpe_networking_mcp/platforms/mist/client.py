"""Mist API client — session management, response processing, and formatting."""

import contextlib
import json

import mistapi
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context
from loguru import logger
from mistapi.__api_response import APIResponse

from hpe_networking_mcp.utils.logging import mask_secret

STATUS_MESSAGES = {
    400: "Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given",
    401: "Unauthorized",
    403: "Permission Denied",
    404: "Not found. The API endpoint doesn't exist or resource doesn't exist",
    429: "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold",
}


async def get_apisession() -> tuple[mistapi.APISession, str]:
    """Get the Mist API session from the lifespan context.

    Returns:
        Tuple of (APISession, response_format)
    """
    ctx = get_context()
    session = ctx.lifespan_context.get("mist_session")
    if session is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": ("Mist API session not available. Check your Mist credentials."),
            }
        )
    logger.debug(
        "Mist API request — host: {}, token: {}",
        session._cloud_uri,
        mask_secret(session._apitoken or ""),
    )
    return session, "json"


def validate_org_id(org_id: str) -> str:
    """Validate an org_id against the token's actual org_id.

    If the org_id doesn't match the token's org, raises a ToolError
    with the correct org_id so the AI can self-correct without an
    extra API call.

    Args:
        org_id: The org_id provided by the AI.

    Returns:
        The validated org_id (may be corrected).
    """
    ctx = get_context()
    correct_org_id = ctx.lifespan_context.get("mist_org_id")
    if correct_org_id and str(org_id) != str(correct_org_id):
        raise ToolError(
            f"Wrong org_id '{org_id}'. The correct org_id for this "
            f"API token is '{correct_org_id}'. Use this org_id for "
            f"all Mist API calls."
        )
    return str(org_id)


async def process_response(response: APIResponse) -> None:
    """Validate an API response and raise ToolError on failure."""
    if response.status_code is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": ("No response received from Mist API. Check network connectivity."),
            }
        )
    if response.status_code == 200:
        return
    ctx = get_context()
    if response.status_code == 403:
        await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
        raise ToolError(
            {
                "status_code": 403,
                "message": (
                    "Permission Denied. This usually means you are using "
                    "a tool with an invalid id (e.g. org_id, site_id). "
                    "Make sure to retrieve them from another tool "
                    "(e.g. use mist_get_self to retrieve the correct org_id)."
                ),
            }
        )
    api_error: dict = {"status_code": response.status_code, "message": ""}
    if response.data:
        await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
        api_error["message"] = json.dumps(response.data)
    else:
        message = STATUS_MESSAGES.get(response.status_code or 0, "Unknown error")
        await ctx.error(f"Got HTTP{response.status_code}")
        api_error["message"] = json.dumps(message)
    raise ToolError(api_error)


async def handle_network_error(exc: Exception) -> None:
    """Convert network-level exceptions to clean ToolError messages."""
    raise ToolError(
        {
            "status_code": 503,
            "message": f"API call failed: {type(exc).__name__}: {exc}",
        }
    ) from exc


def _get_total(response: APIResponse) -> int | None:
    """Extract total entries count from an API response."""
    total = None
    if response.headers and "X-Page-Total" in response.headers:
        with contextlib.suppress(ValueError):
            total = int(response.headers["X-Page-Total"])
    elif isinstance(response.data, dict) and "total" in response.data:
        with contextlib.suppress(ValueError, TypeError):
            total = int(response.data["total"])
    return total


def format_response_data(response: APIResponse) -> dict | list:
    """Extract data from an API response and inject pagination metadata."""
    total = _get_total(response)
    data = response.data

    if response.next:
        if isinstance(data, list):
            data = {
                "results": data,
                "next": response.next,
                "has_more": True,
            }
            if total is not None:
                data["total"] = int(total)
        elif isinstance(data, dict):
            data = dict(data)
            data["next"] = response.next
            data["has_more"] = True
            if total is not None and "total" not in data:
                data["total"] = int(total)
    else:
        if isinstance(data, dict):
            data = dict(data)
            data["has_more"] = False

    return data


def format_response(
    response: APIResponse | dict | list,
    response_format: str = "json",
) -> dict | list | str:
    """Format an API response with pagination metadata and optional string serialization."""
    data = format_response_data(response) if isinstance(response, APIResponse) else response
    if response_format == "string":
        return json.dumps(data)
    return data
