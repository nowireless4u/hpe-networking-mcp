"""Red tests for AOS8 troubleshooting/diagnostics tools (READ-20..26).

Fail with ModuleNotFoundError until plan 03-06 implements
``platforms.aos8.tools.troubleshooting``.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

pytestmark = pytest.mark.unit

_FIXTURES = Path(__file__).parent / "fixtures" / "aos8"


def _load(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text())


def _make_ctx(body):
    response = MagicMock(spec=httpx.Response)
    response.json.return_value = body
    response.text = json.dumps(body) if not isinstance(body, str) else body
    client = MagicMock()
    client.request = AsyncMock(return_value=response)
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}
    return ctx, client


# ---------------------------------------------------------------------------
# READ-20: aos8_ping
# ---------------------------------------------------------------------------


async def test_ping():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_ping

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_ping(ctx, dest="8.8.8.8")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "ping 8.8.8.8"},
    )


# ---------------------------------------------------------------------------
# READ-21: aos8_traceroute
# ---------------------------------------------------------------------------


async def test_traceroute():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_traceroute

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_traceroute(ctx, dest="8.8.8.8")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "traceroute 8.8.8.8"},
    )


# ---------------------------------------------------------------------------
# READ-22: aos8_show_command
# ---------------------------------------------------------------------------


async def test_show_command_accepts_show():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_show_command

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_show_command(ctx, command="show version")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show version"},
    )


async def test_show_command_strips_leading_whitespace():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_show_command

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_show_command(ctx, command="  show version")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show version"},
    )


async def test_show_command_case_insensitive():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_show_command

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_show_command(ctx, command="SHOW version")

    client.request.assert_awaited_once()


async def test_show_command_rejects_non_show():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_show_command

    ctx, client = _make_ctx({})
    result = await aos8_show_command(ctx, command="reload")

    assert isinstance(result, str)
    assert "Only 'show' commands" in result
    client.request.assert_not_awaited()


async def test_show_command_rejects_showtech_injection():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_show_command

    ctx, client = _make_ctx({})
    result = await aos8_show_command(ctx, command="showtech")

    assert isinstance(result, str)
    client.request.assert_not_awaited()


async def test_show_command_strips_meta():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_show_command

    body = {"_meta": ["a"], "_global_result": {"status": "0"}, "data": [1, 2, 3]}
    ctx, _ = _make_ctx(body)
    result = await aos8_show_command(ctx, command="show test")

    assert "_meta" not in result
    assert "_global_result" not in result
    assert result == {"data": [1, 2, 3]}


async def test_show_command_handles_text_response():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_show_command

    response = MagicMock(spec=httpx.Response)
    response.json.side_effect = ValueError("not json")
    response.text = "raw output"
    client = MagicMock()
    client.request = AsyncMock(return_value=response)
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}

    result = await aos8_show_command(ctx, command="show running-config")
    assert result == {"output": "raw output"}


# ---------------------------------------------------------------------------
# READ-23: aos8_get_logs
# ---------------------------------------------------------------------------


async def test_get_logs_default_count():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_get_logs

    ctx, client = _make_ctx(_load("show_log_system.json"))
    await aos8_get_logs(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show log system 100"},
    )


async def test_get_logs_custom_count():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_get_logs

    ctx, client = _make_ctx(_load("show_log_system.json"))
    await aos8_get_logs(ctx, count=50)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show log system 50"},
    )


async def test_get_logs_rejects_oversized_count():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_get_logs

    ctx, client = _make_ctx({})
    result = await aos8_get_logs(ctx, count=2000)

    assert isinstance(result, str)
    client.request.assert_not_awaited()


# ---------------------------------------------------------------------------
# READ-24: aos8_get_controller_stats (multi-call aggregator)
# ---------------------------------------------------------------------------


async def test_get_controller_stats_aggregates():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_get_controller_stats

    def _resp(body):
        r = MagicMock(spec=httpx.Response)
        r.json.return_value = body
        r.text = json.dumps(body)
        return r

    r1 = _resp({"_meta": [], "_global_result": {"status": "0"}, "cpu_load": 5})
    r2 = _resp({"_meta": [], "_global_result": {"status": "0"}, "memory_used": 1024})
    r3 = _resp({"_meta": [], "_global_result": {"status": "0"}, "uptime": "1d"})

    client = MagicMock()
    client.request = AsyncMock(side_effect=[r1, r2, r3])
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}

    result = await aos8_get_controller_stats(ctx)

    assert client.request.await_count == 3
    assert isinstance(result, dict)
    assert {"cpu", "memory", "uptime"}.issubset(result.keys())


# ---------------------------------------------------------------------------
# READ-25: aos8_get_arm_history
# ---------------------------------------------------------------------------


async def test_get_arm_history():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_get_arm_history

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_get_arm_history(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap arm history", "config_path": "/md"},
    )


# ---------------------------------------------------------------------------
# READ-26: aos8_get_rf_monitor
# ---------------------------------------------------------------------------


async def test_get_rf_monitor():
    from hpe_networking_mcp.platforms.aos8.tools.troubleshooting import aos8_get_rf_monitor

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_get_rf_monitor(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap monitor stats", "config_path": "/md"},
    )
