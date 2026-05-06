"""Shared helpers for AOS8 tool modules.

Every showcommand response from AOS8 includes ``_meta`` (column-name schema)
and ``_global_result`` (status envelope already validated by ``AOS8Client``).
Both are infrastructure noise that AI clients do not need; ``strip_meta``
removes them. ``run_show`` and ``get_object`` provide the two HTTP-call
shapes used across every read tool, and ``format_aos8_error`` renders
exceptions into a consistent, AI-friendly string.
"""

from __future__ import annotations

from typing import Any

import httpx

from hpe_networking_mcp.platforms.aos8.client import (
    AOS8APIError,
    AOS8AuthError,
    AOS8Client,
)

__all__ = [
    "strip_meta",
    "flatten_param_value_lists",
    "run_show",
    "get_object",
    "post_object",
    "format_aos8_error",
    "AOS8DecodeError",
]


class AOS8DecodeError(RuntimeError):
    """Raised when an AOS 8 endpoint returns a 2xx body that isn't valid JSON.

    Common triggers: an unrecognized show-command (CLI parser silently
    rejects, returns empty body), an HTML login redirect, or a plaintext
    error from a misrouted request.
    """


def strip_meta(body: Any) -> Any:
    """Remove AOS8 ``_meta`` and ``_global_result`` keys from a response body.

    Args:
        body: Parsed JSON response body. May be a dict, list, or scalar.

    Returns:
        New dict with ``_meta`` and ``_global_result`` removed when ``body``
        is a dict; otherwise returns ``body`` unchanged.
    """
    if not isinstance(body, dict):
        return body
    return {k: v for k, v in body.items() if k not in ("_meta", "_global_result")}


def flatten_param_value_lists(body: Any) -> Any:
    """Flatten AOS 8 ``[{Parameter: k, Value: v}, ...]`` rows into ``{k: v, ...}``.

    AOS 8 ``show <thing> detail``-style commands (notably the AAA
    authentication-server detail commands —
    ``show aaa authentication-server radius/tacacs/ldap/internal <name>``)
    return their content as a transposed key/value table where every row
    is a dict with literal field names ``Parameter`` and ``Value``. The
    PII tokenization walker classifies values by their JSON field name,
    so it can never see the *semantic* field name (``Host``, ``NAS IP``,
    ``Key``, ...) hidden in the ``Parameter`` column. Rules keyed on
    server-identifier names like ``host`` cannot fire.

    This helper detects the transposed shape recursively and rewrites it
    into a regular dict (``{"Host": "192.168.20.70", "Key": "********",
    ...}``). The walker's space → underscore normalization
    (``Host`` → ``host``) then makes identifier-field rules fire normally.

    Non-matching shapes pass through unchanged. The detection is
    conservative: a list is only flattened when *every* element is a
    dict containing at minimum the ``Parameter`` and ``Value`` keys —
    so a list whose elements happen to share those keys among others
    (a richer record shape) is preserved as-is.

    See [issue #235](https://github.com/nowireless4u/hpe-networking-mcp/issues/235)
    for context.

    Args:
        body: Parsed AOS 8 JSON body. May be a dict, list, or scalar.

    Returns:
        A new structure with transposed-table lists flattened. Other
        nested dicts/lists/scalars are returned unchanged.
    """
    if isinstance(body, list):
        if body and all(isinstance(row, dict) and {"Parameter", "Value"} <= set(row.keys()) for row in body):
            # Transposed shape detected — flatten this list.
            # Last-wins on duplicate Parameter names (extremely rare in
            # AOS 8; the transposed-table semantics are key-unique within
            # a single block).
            return {row["Parameter"]: row["Value"] for row in body}
        # Otherwise: recurse element-wise.
        return [flatten_param_value_lists(item) for item in body]
    if isinstance(body, dict):
        return {k: flatten_param_value_lists(v) for k, v in body.items()}
    return body


def _decode_json_or_raise(response: httpx.Response, what: str) -> Any:
    """Return ``response.json()`` or raise AOS8DecodeError with diagnostics.

    AOS 8 may return a 2xx response with an empty body, an HTML login page,
    or a plaintext error when the CLI parser silently rejects a command or
    a session cookie has gone stale. Surface enough metadata for the AI
    caller to act on (status, content-type, body length, body preview)
    instead of leaking the raw json-module ValueError.
    """
    try:
        return response.json()
    except ValueError as exc:
        body = response.text or ""
        preview = body[:120].replace("\n", " ").strip()
        content_type = response.headers.get("content-type", "<missing>")
        raise AOS8DecodeError(
            f"AOS 8 returned non-JSON body for {what} "
            f"(HTTP {response.status_code}, content-type={content_type}, {len(body)} bytes)"
            + (f": {preview!r}" if preview else " — body was empty")
            + ". Likely causes: command not recognized by the controller's"
            " CLI parser, an HTML login redirect, or a misrouted endpoint."
        ) from exc


async def run_show(
    client: AOS8Client,
    command: str,
    *,
    config_path: str | None = None,
) -> Any:
    """Execute an AOS8 show command and return the cleaned JSON body.

    The AOS 8 ``showcommand`` endpoint responds in three shapes:

    * **JSON body** — for structured ``show`` output (most ``show`` commands).
      Returned with ``_meta`` and ``_global_result`` stripped.
    * **Empty body** — for valid commands that have no data to return on this
      controller (e.g. ``show alarms`` with no active alarms, ``show user-table``
      with no clients). Returned as ``{}`` so callers see "success, no data"
      rather than a parse error.
    * **Plain text body** — for commands whose output is a text dump
      (e.g. ``show log system``, ``show audit-trail``, ``show running-config``).
      Wrapped as ``{"output": <text>}`` to match ``aos8_show_command``'s
      passthrough contract.

    Args:
        client: ``AOS8Client`` from ``ctx.lifespan_context["aos8_client"]``.
        command: Full show command string (e.g. ``"show ap database"``).
        config_path: Optional hierarchy node (e.g. ``"/md"``); included in
            query params only when not ``None``.

    Returns:
        Parsed JSON body with envelope keys stripped, or one of the
        empty/text shapes described above.
    """
    params: dict[str, Any] = {"command": command}
    if config_path is not None:
        params["config_path"] = config_path
    response = await client.request("GET", "/v1/configuration/showcommand", params=params)
    try:
        return flatten_param_value_lists(strip_meta(response.json()))
    except ValueError:
        body = response.text or ""
        return {"output": body} if body else {}


async def get_object(
    client: AOS8Client,
    object_path: str,
    *,
    config_path: str = "/md",
    entry_type: str | None = None,
) -> Any:
    """Fetch a configuration object via ``/v1/configuration/object/<path>``.

    Args:
        client: ``AOS8Client`` instance.
        object_path: Object name (e.g. ``"ssid_prof"``, ``"ap_group"``).
        config_path: Hierarchy node; defaults to ``"/md"``.
        entry_type: Optional ``type`` filter (``"user"``, ``"local"``,
            ``"default"``, ``"inherited"``). When set, AOS 8 returns only
            entries matching the filter — most useful is ``"user"`` which
            strips factory defaults and returns only customer-defined
            configuration.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped.
    """
    params: dict[str, Any] = {"config_path": config_path}
    if entry_type is not None:
        params["type"] = entry_type
    response = await client.request(
        "GET",
        f"/v1/configuration/object/{object_path}",
        params=params,
    )
    return strip_meta(_decode_json_or_raise(response, f"object {object_path!r}"))


async def post_object(
    client: AOS8Client,
    object_name: str,
    body: dict[str, Any],
    *,
    config_path: str | None = None,
) -> Any:
    """POST a configuration or operational object to AOS8.

    AOS8 routes most object writes through ``/v1/configuration/object``;
    the object type is identified by the top-level body key. Operational
    endpoints (``apboot``, ``aaa_user_delete``) use the same generic path
    and rely on the body key. ``write_memory`` uses a dedicated path
    and is NOT routed through this helper.

    Args:
        client: ``AOS8Client`` from ``ctx.lifespan_context["aos8_client"]``.
        object_name: Tool-side identifier; used only for diagnostic context.
        body: Pre-wrapped POST body (e.g. ``{"ssid_prof": {...}}``).
        config_path: Hierarchy node. Required for config-object writes;
            may be omitted for operational endpoints.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` removed.

    Raises:
        AOS8APIError, AOS8AuthError, httpx.HTTPError: per ``AOS8Client.request``.
    """
    params: dict[str, Any] | None = {"config_path": config_path} if config_path is not None else None
    response = await client.request(
        "POST",
        "/v1/configuration/object",
        params=params,
        json_body=body,
    )
    return strip_meta(response.json())


def format_aos8_error(exc: BaseException, action: str) -> str:
    """Render an AOS8 exception as a tool-friendly error message.

    Args:
        exc: The exception caught at the tool boundary.
        action: Short verb phrase describing what was being attempted
            (e.g. ``"list controllers"``).

    Returns:
        Human-readable error string suitable for returning to the AI client.
    """
    if isinstance(exc, AOS8AuthError):
        return f"AOS8 authentication failed while attempting to {action}: {exc}"
    if isinstance(exc, AOS8APIError):
        return f"AOS8 API error while attempting to {action}: {exc}"
    if isinstance(exc, AOS8DecodeError):
        return f"AOS8 decode error while attempting to {action}: {exc}"
    if isinstance(exc, httpx.HTTPStatusError):
        return f"AOS8 HTTP {exc.response.status_code} while attempting to {action}: {exc}"
    if isinstance(exc, httpx.HTTPError):
        return f"AOS8 transport error while attempting to {action}: {exc}"
    return f"Unexpected error while attempting to {action}: {exc}"
