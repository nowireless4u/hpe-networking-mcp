"""Red tests for AOS8 client visibility read tools (READ-09..12).

Fail with ModuleNotFoundError until plan 03-03 implements
``platforms.aos8.tools.clients``.
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


async def test_get_clients():
    from hpe_networking_mcp.platforms.aos8.tools.clients import aos8_get_clients

    ctx, client = _make_ctx(_load("show_user_table.json"))
    result = await aos8_get_clients(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show user-table", "config_path": "/md"},
    )
    assert "_meta" not in result
    assert "_global_result" not in result


async def test_find_client_by_mac():
    from hpe_networking_mcp.platforms.aos8.tools.clients import aos8_find_client

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_find_client(ctx, mac="aa:bb:cc:dd:ee:01")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show user-table mac aa:bb:cc:dd:ee:01", "config_path": "/md"},
    )


async def test_find_client_by_ip():
    from hpe_networking_mcp.platforms.aos8.tools.clients import aos8_find_client

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_find_client(ctx, ip="10.1.10.5")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show user-table ip 10.1.10.5", "config_path": "/md"},
    )


async def test_find_client_by_username():
    from hpe_networking_mcp.platforms.aos8.tools.clients import aos8_find_client

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_find_client(ctx, username="alice")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show user-table name alice", "config_path": "/md"},
    )


async def test_find_client_requires_selector():
    from hpe_networking_mcp.platforms.aos8.tools.clients import aos8_find_client

    ctx, client = _make_ctx({})
    result = await aos8_find_client(ctx)

    assert isinstance(result, str)
    client.request.assert_not_awaited()


async def test_get_client_detail():
    from hpe_networking_mcp.platforms.aos8.tools.clients import aos8_get_client_detail

    ctx, client = _make_ctx(_load("show_user_table_verbose.json"))
    await aos8_get_client_detail(ctx, mac="aa:bb:cc:dd:ee:01")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show user-table verbose mac aa:bb:cc:dd:ee:01", "config_path": "/md"},
    )


async def test_get_client_history():
    from hpe_networking_mcp.platforms.aos8.tools.clients import aos8_get_client_history

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_get_client_history(ctx, mac="aa:bb:cc:dd:ee:01")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap association history client-mac aa:bb:cc:dd:ee:01"},
    )
