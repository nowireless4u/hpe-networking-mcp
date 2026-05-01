"""Red tests for AOS8 alerts/events read tools (READ-13..15).

Fail with ModuleNotFoundError until plan 03-04 implements
``platforms.aos8.tools.alerts``.
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


async def test_get_alarms():
    from hpe_networking_mcp.platforms.aos8.tools.alerts import aos8_get_alarms

    ctx, client = _make_ctx(_load("show_alarms.json"))
    await aos8_get_alarms(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show alarms", "config_path": "/md"},
    )


async def test_get_audit_trail():
    from hpe_networking_mcp.platforms.aos8.tools.alerts import aos8_get_audit_trail

    ctx, client = _make_ctx(_load("show_audit_trail.json"))
    await aos8_get_audit_trail(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show audit-trail"},
    )


async def test_get_events():
    from hpe_networking_mcp.platforms.aos8.tools.alerts import aos8_get_events

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_get_events(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show events", "config_path": "/md"},
    )
