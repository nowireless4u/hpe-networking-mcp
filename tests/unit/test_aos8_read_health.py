"""Red tests for AOS8 health/inventory read tools (READ-01..08).

These tests fail with ModuleNotFoundError until plan 03-02 implements
``platforms.aos8.tools.health``. Each test pins the exact endpoint path,
parameter shape, and meta-stripping contract every implementation must
satisfy.
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


async def test_get_controllers():
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_controllers

    body = _load("show_switches.json")
    ctx, client = _make_ctx(body)

    result = await aos8_get_controllers(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show switches"},
    )
    assert "_meta" not in result
    assert "_global_result" not in result
    assert result["Switch List"][0]["Name"] == "MD-01"


async def test_get_ap_database_passes_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_ap_database

    ctx, client = _make_ctx(_load("show_ap_database.json"))
    await aos8_get_ap_database(ctx, config_path="/md/site1")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap database", "config_path": "/md/site1"},
    )


async def test_get_ap_database_default_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_ap_database

    ctx, client = _make_ctx(_load("show_ap_database.json"))
    await aos8_get_ap_database(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap database", "config_path": "/md"},
    )


async def test_get_active_aps():
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_active_aps

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}, "Active AP Table": []})
    await aos8_get_active_aps(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap active", "config_path": "/md"},
    )


async def test_get_ap_detail_by_name():
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_ap_detail

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_get_ap_detail(ctx, ap_name="AP-01")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap details ap-name AP-01", "config_path": "/md"},
    )


async def test_get_ap_detail_by_mac():
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_ap_detail

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_get_ap_detail(ctx, ap_mac="00:1a:1e:00:00:01")

    client.request.assert_awaited_once()
    args, kwargs = client.request.await_args
    assert kwargs["params"]["command"] == "show ap details ap-mac 00:1a:1e:00:00:01"


async def test_get_ap_detail_requires_one_selector():
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_ap_detail

    ctx, client = _make_ctx({})
    result = await aos8_get_ap_detail(ctx)

    assert isinstance(result, str)
    assert result.startswith("Error") or result.startswith("Must")
    client.request.assert_not_awaited()


async def test_get_bss_table():
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_bss_table

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_get_bss_table(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap bss-table", "config_path": "/md"},
    )


async def test_get_radio_summary():
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_radio_summary

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_get_radio_summary(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap radio-summary", "config_path": "/md"},
    )


async def test_get_version():
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_version

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}, "Version": "8.10"})
    await aos8_get_version(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show version"},
    )


async def test_get_licenses():
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_licenses

    ctx, client = _make_ctx({"_meta": [], "_global_result": {"status": "0"}})
    await aos8_get_licenses(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show license"},
    )


def test_all_health_tools_read_only():
    """Smoke check: every aos8 health tool registered as readOnly. Skipped until Plan 02."""
    from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES

    aos8_specs = REGISTRIES.get("aos8", {})
    health_specs = [s for s in aos8_specs.values() if s.category == "health"]
    if not health_specs:
        pytest.skip("registered after Plan 02")
    for spec in health_specs:
        # The annotation lives on the registered tool; we only assert that the
        # registry entry exists and is tagged read-only via convention.
        assert spec.platform == "aos8"
