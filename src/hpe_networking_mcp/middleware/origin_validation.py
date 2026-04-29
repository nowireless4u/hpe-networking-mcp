"""Origin header validation — defends against browser-driven DNS rebinding.

This is **ASGI/Starlette HTTP-layer middleware**, not a FastMCP protocol
middleware. It runs on the raw HTTP request before any MCP handling. The
other modules in this directory (``null_strip``, ``elicitation``, ``retry``,
etc.) are FastMCP middleware that run inside the MCP request lifecycle —
they don't see HTTP headers.

The MCP Streamable HTTP spec
(https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#origin-validation)
requires servers to validate the ``Origin`` header to prevent DNS rebinding
attacks: a malicious page that tricks DNS into resolving its domain to
``127.0.0.1`` and POSTs to the local MCP endpoint. Browsers always send
``Origin`` on such requests and cannot lie about it (it's a forbidden
header), so a server-side allowlist is sufficient defense.

Non-browser clients (supergateway, curl, native MCP clients) typically do
not send ``Origin`` at all. Those requests are allowed through — there's
no security gain from blocking them since the DNS rebinding vector is
browser-only.

Wildcard ``*`` in the allowlist disables the check entirely; useful when
the server sits behind an authenticating reverse proxy that already
validates origins.
"""

from collections.abc import Awaitable, Callable, Iterable

from loguru import logger

ASGIScope = dict
ASGIMessage = dict
ASGIReceive = Callable[[], Awaitable[ASGIMessage]]
ASGISend = Callable[[ASGIMessage], Awaitable[None]]
ASGIApp = Callable[[ASGIScope, ASGIReceive, ASGISend], Awaitable[None]]


class OriginValidationMiddleware:
    """ASGI middleware that rejects requests whose ``Origin`` header is not allowlisted.

    Behavior matrix:

    +--------------------+------------------+----------------------+
    | Request has Origin | Origin allowed?  | Result               |
    +====================+==================+======================+
    | No                 | n/a              | Pass through (allow) |
    +--------------------+------------------+----------------------+
    | Yes                | Yes              | Pass through (allow) |
    +--------------------+------------------+----------------------+
    | Yes                | No               | 403 Forbidden        |
    +--------------------+------------------+----------------------+

    If ``"*"`` is in ``allowed_origins`` the check is bypassed and every
    request — Origin or not — passes through.

    Args:
        app: The downstream ASGI application.
        allowed_origins: Iterable of allowed origin strings (e.g.
            ``"http://localhost:8000"``). May contain ``"*"`` to disable
            the check entirely.
    """

    def __init__(self, app: ASGIApp, allowed_origins: Iterable[str] | None = None) -> None:
        self.app = app
        origins = list(allowed_origins or [])
        self._wildcard = "*" in origins
        self._allowed = {o for o in origins if o != "*"}

    async def __call__(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        if scope["type"] != "http" or self._wildcard:
            await self.app(scope, receive, send)
            return

        origin = self._extract_origin(scope.get("headers", []))

        if origin is None or origin in self._allowed:
            await self.app(scope, receive, send)
            return

        client = scope.get("client") or ("?", 0)
        path = scope.get("path", "")
        logger.warning(
            "Origin validation: rejected request from {}:{} for {} (origin={!r}, allowed={})",
            client[0],
            client[1],
            path,
            origin,
            sorted(self._allowed),
        )
        await self._send_forbidden(send)

    @staticmethod
    def _extract_origin(headers: Iterable[tuple[bytes, bytes]]) -> str | None:
        """Return the ``Origin`` header value as a str, or None if absent."""
        for key, value in headers:
            if key == b"origin":
                try:
                    return value.decode("latin-1")
                except UnicodeDecodeError:
                    return None
        return None

    @staticmethod
    async def _send_forbidden(send: ASGISend) -> None:
        body = b'{"jsonrpc":"2.0","error":{"code":-32600,"message":"Origin not allowed"},"id":null}'
        await send(
            {
                "type": "http.response.start",
                "status": 403,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body, "more_body": False})
