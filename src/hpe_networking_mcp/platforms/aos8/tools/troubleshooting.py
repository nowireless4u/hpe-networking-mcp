"""AOS8 troubleshooting and diagnostics read tools (READ-20..26).

This module exposes the AOS8 show-command passthrough plus a handful of
purpose-built diagnostics: ping, traceroute, log retrieval, controller
stat aggregation, ARM history, and RF monitor stats.

``aos8_show_command`` enforces a strict ``"show "`` prefix (case-insensitive,
with leading whitespace stripped) so the LLM cannot smuggle in mutating
CLI verbs such as ``reload`` or ``write memory``. It also wraps non-JSON
responses (e.g. ``show running-config`` text dumps) in
``{"output": <text>}`` so every return value is a structured dict.

``aos8_ping`` and ``aos8_traceroute`` build their command strings
internally and therefore bypass the show-prefix guard — the guard exists
only on the user-facing passthrough.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.aos8._registry import tool
from hpe_networking_mcp.platforms.aos8.tools import READ_ONLY
from hpe_networking_mcp.platforms.aos8.tools._helpers import (
    format_aos8_error,
    run_show,
    strip_meta,
)

__all__ = [
    "aos8_ping",
    "aos8_traceroute",
    "aos8_show_command",
    "aos8_get_logs",
    "aos8_get_controller_stats",
    "aos8_get_arm_history",
    "aos8_get_rf_monitor",
]


@tool(name="aos8_ping", annotations=READ_ONLY)
async def aos8_ping(ctx: Context, dest: str) -> dict[str, Any] | str:
    """Ping a target from the controller via the showcommand endpoint.

    Args:
        ctx: FastMCP request context; ``ctx.lifespan_context["aos8_client"]``
            must hold an authenticated ``AOS8Client``.
        dest: Destination host or IP to ping (e.g. ``"8.8.8.8"``).

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped, or a
        formatted error string when the API call fails.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, f"ping {dest}")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "ping target")


@tool(name="aos8_traceroute", annotations=READ_ONLY)
async def aos8_traceroute(ctx: Context, dest: str) -> dict[str, Any] | str:
    """Traceroute to a target from the controller via the showcommand endpoint.

    Args:
        ctx: FastMCP request context; ``ctx.lifespan_context["aos8_client"]``
            must hold an authenticated ``AOS8Client``.
        dest: Destination host or IP to traceroute (e.g. ``"8.8.8.8"``).

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped, or a
        formatted error string when the API call fails.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, f"traceroute {dest}")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "traceroute target")


@tool(name="aos8_show_command", annotations=READ_ONLY)
async def aos8_show_command(ctx: Context, command: str) -> dict[str, Any] | str:
    """Execute an arbitrary AOS8 ``show`` command via the showcommand endpoint.

    The command must start with ``"show "`` (case-insensitive; leading
    whitespace is stripped). Non-show verbs are rejected before any HTTP
    call is made, which keeps this passthrough safely read-only. Responses
    that aren't valid JSON (e.g. ``show running-config`` text dumps) are
    wrapped as ``{"output": <text>}``.

    Args:
        ctx: FastMCP request context; ``ctx.lifespan_context["aos8_client"]``
            must hold an authenticated ``AOS8Client``.
        command: Full CLI string starting with ``"show "``.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped, a
        ``{"output": <text>}`` envelope for non-JSON responses, or an error
        string when the command is rejected or the API call fails.
    """
    normalized = command.strip()
    if not normalized.lower().startswith("show "):
        return f"Only 'show' commands are permitted. Received: {command!r}"
    client = ctx.lifespan_context["aos8_client"]
    try:
        response = await client.request(
            "GET",
            "/v1/configuration/showcommand",
            params={"command": normalized},
        )
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, f"run show command {normalized!r}")
    try:
        body = response.json()
    except ValueError:
        return {"output": response.text}
    return strip_meta(body)


@tool(name="aos8_get_logs", annotations=READ_ONLY)
async def aos8_get_logs(ctx: Context, count: int = 100) -> dict[str, Any] | str:
    """Return the last ``count`` lines of the controller system log.

    Args:
        ctx: FastMCP request context; ``ctx.lifespan_context["aos8_client"]``
            must hold an authenticated ``AOS8Client``.
        count: Number of recent log lines to return. Capped at 1000 to keep
            responses manageable; oversized requests are rejected with an
            error string. Defaults to 100.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped, or a
        formatted error string when the API call fails or ``count`` exceeds
        1000.
    """
    if count > 1000:
        return "count must be <= 1000"
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, f"show log system {count}")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch system logs")


@tool(name="aos8_get_controller_stats", annotations=READ_ONLY)
async def aos8_get_controller_stats(ctx: Context) -> dict[str, Any] | str:
    """Aggregate CPU, memory, and uptime stats from the controller.

    Issues three sequential ``showcommand`` calls (``show cpuload``,
    ``show memory``, ``show switchinfo``) and returns the cleaned bodies
    keyed as ``cpu``, ``memory``, and ``uptime``. A failure on any of the
    three is treated as a single failure for the aggregate.

    Args:
        ctx: FastMCP request context; ``ctx.lifespan_context["aos8_client"]``
            must hold an authenticated ``AOS8Client``.

    Returns:
        Dict with ``cpu``, ``memory``, and ``uptime`` keys, or a formatted
        error string when any of the underlying API calls fails.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        cpu = await run_show(client, "show cpuload")
        memory = await run_show(client, "show memory")
        uptime = await run_show(client, "show switchinfo")
        return {"cpu": cpu, "memory": memory, "uptime": uptime}
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch controller stats")


@tool(name="aos8_get_arm_history", annotations=READ_ONLY)
async def aos8_get_arm_history(ctx: Context, config_path: str = "/md") -> dict[str, Any] | str:
    """Fetch ARM (Adaptive Radio Management) channel/power change history.

    Args:
        ctx: FastMCP request context; ``ctx.lifespan_context["aos8_client"]``
            must hold an authenticated ``AOS8Client``.
        config_path: Hierarchy node to query (e.g. ``"/md"``,
            ``"/md/branch1"``). Defaults to ``"/md"``.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped, or a
        formatted error string when the API call fails.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show ap arm history", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch ARM history")


@tool(name="aos8_get_rf_monitor", annotations=READ_ONLY)
async def aos8_get_rf_monitor(ctx: Context, config_path: str = "/md") -> dict[str, Any] | str:
    """Fetch RF monitor statistics across the AP fleet.

    Args:
        ctx: FastMCP request context; ``ctx.lifespan_context["aos8_client"]``
            must hold an authenticated ``AOS8Client``.
        config_path: Hierarchy node to query (e.g. ``"/md"``,
            ``"/md/branch1"``). Defaults to ``"/md"``.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped, or a
        formatted error string when the API call fails.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show ap monitor stats", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch RF monitor stats")
