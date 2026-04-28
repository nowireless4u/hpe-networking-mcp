"""Red tests for AOS8 WLAN config-object read tools (READ-16..19).

Fail with ModuleNotFoundError until plan 03-05 implements
``platforms.aos8.tools.wlan``. WLAN tools hit ``/v1/configuration/object/<x>``
(not ``/showcommand``).
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


async def test_get_ssid_profiles():
    from hpe_networking_mcp.platforms.aos8.tools.wlan import aos8_get_ssid_profiles

    ctx, client = _make_ctx(_load("ssid_prof.json"))
    result = await aos8_get_ssid_profiles(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/object/ssid_prof",
        params={"config_path": "/md"},
    )
    assert "_global_result" not in result


async def test_get_ssid_profiles_passes_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.wlan import aos8_get_ssid_profiles

    ctx, client = _make_ctx(_load("ssid_prof.json"))
    await aos8_get_ssid_profiles(ctx, config_path="/md/branch1")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/object/ssid_prof",
        params={"config_path": "/md/branch1"},
    )


async def test_get_virtual_aps():
    from hpe_networking_mcp.platforms.aos8.tools.wlan import aos8_get_virtual_aps

    ctx, client = _make_ctx({"_data": []})
    await aos8_get_virtual_aps(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/object/virtual_ap",
        params={"config_path": "/md"},
    )


async def test_get_virtual_aps_passes_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.wlan import aos8_get_virtual_aps

    ctx, client = _make_ctx({"_data": []})
    await aos8_get_virtual_aps(ctx, config_path="/md/branch1")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/object/virtual_ap",
        params={"config_path": "/md/branch1"},
    )


async def test_get_ap_groups():
    from hpe_networking_mcp.platforms.aos8.tools.wlan import aos8_get_ap_groups

    ctx, client = _make_ctx({"_data": []})
    await aos8_get_ap_groups(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/object/ap_group",
        params={"config_path": "/md"},
    )


async def test_get_ap_groups_passes_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.wlan import aos8_get_ap_groups

    ctx, client = _make_ctx({"_data": []})
    await aos8_get_ap_groups(ctx, config_path="/md/branch1")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/object/ap_group",
        params={"config_path": "/md/branch1"},
    )


async def test_get_user_roles():
    from hpe_networking_mcp.platforms.aos8.tools.wlan import aos8_get_user_roles

    ctx, client = _make_ctx({"_data": []})
    await aos8_get_user_roles(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/object/role",
        params={"config_path": "/md"},
    )


async def test_get_user_roles_passes_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.wlan import aos8_get_user_roles

    ctx, client = _make_ctx({"_data": []})
    await aos8_get_user_roles(ctx, config_path="/md/branch1")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/object/role",
        params={"config_path": "/md/branch1"},
    )
