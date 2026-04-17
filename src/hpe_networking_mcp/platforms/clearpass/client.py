"""ClearPass API session factory and helpers.

Unlike pycentral (single connection object), pyclearpass requires instantiating
each API class independently — every class inherits ClearPassAPILogin.

We acquire an OAuth2 token once at lifespan init and pass it via ``api_token=``
to skip re-authentication on every tool call.
"""

from __future__ import annotations

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context
from loguru import logger
from pyclearpass.common import ClearPassAPILogin

from hpe_networking_mcp.config import ClearPassSecrets
from hpe_networking_mcp.utils.logging import mask_secret


def create_api_client[T: ClearPassAPILogin](api_class: type[T], config: ClearPassSecrets, token: str) -> T:
    """Create a pyclearpass API class instance with a shared cached token.

    Args:
        api_class: Any pyclearpass API class (e.g. ``ApiIdentities``).
        config: ClearPass connection details from Docker secrets.
        token: Pre-acquired OAuth2 access token.

    Returns:
        Configured API class instance ready for calls.
    """
    instance = api_class(server=config.server, api_token=token)
    # pyclearpass hardcodes verify_ssl=False in __init__ — override it
    instance.verify_ssl = config.verify_ssl
    return instance


async def get_clearpass_session[T: ClearPassAPILogin](api_class: type[T]) -> T:
    """Get a pyclearpass API client from the lifespan context.

    Usage in tools::

        from pyclearpass.api_identities import ApiIdentities
        client = await get_clearpass_session(ApiIdentities)
        result = client.get_guest_by_guest_id(guest_id="42")

    Args:
        api_class: The pyclearpass API class to instantiate.

    Returns:
        Configured API client instance.

    Raises:
        ToolError: If ClearPass is not configured or token is missing.
    """
    ctx = get_context()
    config: ClearPassSecrets | None = ctx.lifespan_context.get("clearpass_config")
    token: str | None = ctx.lifespan_context.get("clearpass_token")

    if config is None or token is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "ClearPass API session not available. Check your ClearPass credentials.",
            }
        )

    logger.debug(
        "ClearPass API request — server: {}, token: {}",
        config.server,
        mask_secret(token),
    )
    return create_api_client(api_class, config, token)
