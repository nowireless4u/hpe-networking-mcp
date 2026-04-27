"""Retry middleware for transient API failures.

Catches two kinds of transient errors and retries reads (5xx + 429) and
writes (429 only — 4xx/5xx writes are NOT retried for idempotency safety):

1. **Response-dict pattern** — older platform clients (Mist, Central,
   ClearPass) return a dict shaped like ``{"status_code": 503, ...}``
   (or ``"code": 503`` / ``"status": 503`` depending on platform).
2. **Exception pattern** — newer httpx-based clients (GreenLake, Apstra,
   Axis) raise ``httpx.HTTPStatusError`` whose ``.response.status_code``
   indicates the failure.

Configuration via env vars:

- ``RETRY_MAX_ATTEMPTS`` — max attempts including the first (default 3)
- ``RETRY_INITIAL_DELAY`` — initial backoff seconds (default 1.0)
- ``RETRY_MAX_DELAY`` — cap on a single retry sleep (default 60.0 — also
  caps Retry-After header values)

Read/write classification reads the FastMCP tool's tags at call time —
any tag matching ``*_write`` or ``*_write_delete`` marks the tool as a
write. The middleware retries 5xx only on reads; 429 retries on
both (since 429 is always safe — the server is asking us to slow down,
not telling us the request was processed).

Closes #133 (5xx retry) and #134 (429 + Retry-After).
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx
import mcp.types
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from loguru import logger

# Status codes we treat as transient. 5xx = server failure; 429 = rate limit.
_TRANSIENT_STATUS_CODES = frozenset({500, 502, 503, 504})
_RATE_LIMIT_STATUS_CODE = 429


def _get_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        logger.warning("Retry: invalid {} value {!r}, falling back to {}", name, raw, default)
        return default


def _get_float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        logger.warning("Retry: invalid {} value {!r}, falling back to {}", name, raw, default)
        return default


def _extract_status_code(value: Any) -> int | None:
    """Return the HTTP status code from a tool-result dict, or None if absent.

    Looks for the three response-dict shapes our platforms use:
    Mist/GreenLake (``status_code``), Central (``code``), ClearPass (``status``).
    """
    if not isinstance(value, dict):
        return None
    for key in ("status_code", "code", "status"):
        candidate = value.get(key)
        if isinstance(candidate, int) and 100 <= candidate < 600:
            return candidate
    return None


def _extract_retry_after_seconds(value: Any, max_delay: float) -> float | None:
    """Pull a Retry-After value from a tool-result dict.

    Handles both the integer-seconds and HTTP-date forms (we only honor
    the integer form here; HTTP-date would require parsing and the
    benefit is tiny). Returns the seconds value capped at ``max_delay``,
    or ``None`` if no usable value is present.
    """
    if not isinstance(value, dict):
        return None
    # Try canonical Retry-After plus a couple of pragmatic variants
    # (some platforms surface them differently).
    for key in ("Retry-After", "retry_after", "retry-after"):
        raw = value.get(key)
        if raw is None:
            continue
        try:
            seconds = float(raw)
            return min(seconds, max_delay)
        except (TypeError, ValueError):
            continue
    return None


def _retry_after_from_exception(exc: BaseException, max_delay: float) -> float | None:
    """Pull Retry-After from an httpx.HTTPStatusError's response headers."""
    if not isinstance(exc, httpx.HTTPStatusError):
        return None
    try:
        raw = exc.response.headers.get("Retry-After")
    except Exception:
        return None
    if raw is None:
        return None
    try:
        seconds = float(raw)
        return min(seconds, max_delay)
    except (TypeError, ValueError):
        return None


def _exception_status_code(exc: BaseException) -> int | None:
    """Extract status code from an httpx.HTTPStatusError, or None."""
    if not isinstance(exc, httpx.HTTPStatusError):
        return None
    try:
        return int(exc.response.status_code)
    except Exception:
        return None


async def _is_write_tool(context: MiddlewareContext[mcp.types.CallToolRequestParams], name: str) -> bool:
    """Look up the tool's tags via FastMCP and return True if any tag ends
    in ``_write`` or ``_write_delete`` (the cross-platform convention).
    Falls back to False if the lookup fails — better to retry once
    erroneously than to mis-classify a real read as a write and skip
    the retry entirely.
    """
    ctx = context.fastmcp_context
    if ctx is None:
        return False
    try:
        fastmcp = ctx.fastmcp
        if fastmcp is None:
            return False
        tool = await fastmcp.get_tool(name)
    except Exception:
        return False
    if tool is None:
        return False
    tags: set[str] = set(getattr(tool, "tags", None) or set())
    return any(tag.endswith("_write") or tag.endswith("_write_delete") for tag in tags)


class RetryMiddleware(Middleware):
    """Retry transient failures on read tools.

    See module docstring for the design rationale and configuration.
    """

    def __init__(
        self,
        max_attempts: int | None = None,
        initial_delay: float | None = None,
        max_delay: float | None = None,
    ) -> None:
        self.max_attempts = max_attempts if max_attempts is not None else _get_int_env("RETRY_MAX_ATTEMPTS", 3)
        self.initial_delay = initial_delay if initial_delay is not None else _get_float_env("RETRY_INITIAL_DELAY", 1.0)
        self.max_delay = max_delay if max_delay is not None else _get_float_env("RETRY_MAX_DELAY", 60.0)

    def _backoff_delay(self, attempt: int) -> float:
        """Exponential backoff: initial * 2^attempt, capped at max_delay."""
        delay = self.initial_delay * (2**attempt)
        return min(delay, self.max_delay)

    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next: Any,
    ) -> ToolResult:
        if self.max_attempts <= 1:
            # Disabled — don't retry, just pass through
            return await call_next(context)  # type: ignore[no-any-return]

        tool_name = context.message.name
        is_write = await _is_write_tool(context, tool_name)

        last_result: ToolResult | None = None
        last_exception: BaseException | None = None

        for attempt in range(self.max_attempts):
            sleep_seconds: float | None = None

            try:
                result = await call_next(context)
                # Inspect the response payload for transient-error status codes
                # in the response-dict pattern (Mist/Central/ClearPass).
                status = None
                if hasattr(result, "structured_content") and result.structured_content:
                    status = _extract_status_code(result.structured_content)
                if status is None and hasattr(result, "content") and result.content:
                    # Some tools return the dict-shape inside the content list.
                    for block in result.content:
                        text_value = getattr(block, "text", None)
                        if isinstance(text_value, str):
                            try:
                                import json

                                parsed = json.loads(text_value)
                                status = _extract_status_code(parsed)
                                if status is not None:
                                    break
                            except (ValueError, json.JSONDecodeError):
                                continue

                if status is None:
                    # Successful tool call — return the result as-is.
                    return result  # type: ignore[no-any-return]

                last_result = result

                if status == _RATE_LIMIT_STATUS_CODE:
                    # 429 retried on reads AND writes (always safe)
                    if hasattr(result, "structured_content"):
                        retry_after = _extract_retry_after_seconds(
                            result.structured_content,
                            self.max_delay,
                        )
                        if retry_after is not None:
                            sleep_seconds = retry_after
                elif status in _TRANSIENT_STATUS_CODES:
                    # 5xx retried on reads only — writes may not be idempotent
                    if is_write:
                        return result  # type: ignore[no-any-return]
                else:
                    # Non-transient (4xx other than 429, etc.) — return immediately
                    return result  # type: ignore[no-any-return]

            except httpx.HTTPStatusError as exc:
                status = _exception_status_code(exc)
                if status is None:
                    raise
                last_exception = exc

                if status == _RATE_LIMIT_STATUS_CODE:
                    sleep_seconds = _retry_after_from_exception(exc, self.max_delay)
                elif status in _TRANSIENT_STATUS_CODES:
                    if is_write:
                        raise
                else:
                    raise

            # If we get here, we're going to retry. Decide the sleep duration.
            if attempt >= self.max_attempts - 1:
                # Out of attempts — fall through to return the last result/exception
                break

            if sleep_seconds is None:
                sleep_seconds = self._backoff_delay(attempt)

            logger.info(
                "Retry: {} returned transient error (attempt {}/{}) — sleeping {:.1f}s",
                tool_name,
                attempt + 1,
                self.max_attempts,
                sleep_seconds,
            )
            await asyncio.sleep(sleep_seconds)

        # Out of attempts — return the last result if we have one, or re-raise
        if last_exception is not None:
            raise last_exception
        if last_result is not None:
            return last_result
        # Defensive — shouldn't reach here unless max_attempts was 0
        return await call_next(context)  # type: ignore[no-any-return]
