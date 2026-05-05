"""Red tests for AOS8 differentiator read tools (DIFF-01..09).

These tests fail with ModuleNotFoundError until plan 07-02 implements
``platforms.aos8.tools.differentiators``. Each test pins the exact
endpoint path, parameter shape, and response contract every implementation
must satisfy.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

pytestmark = pytest.mark.unit
_FIXTURES = Path(__file__).parent / "fixtures" / "aos8"


def _load(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text())


def _resp(body: dict) -> MagicMock:
    """Build a MagicMock that mimics httpx.Response with a .json() method."""
    r = MagicMock()
    r.json.return_value = body
    return r


def _make_ctx(body: dict):
    client = MagicMock()
    client.request = AsyncMock(return_value=_resp(body))
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}
    return ctx, client


# ---------------------------------------------------------------------------
# DIFF-01: aos8_get_md_hierarchy
# ---------------------------------------------------------------------------


async def test_get_md_hierarchy():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_md_hierarchy

    body = _load("show_configuration_node_hierarchy.json")
    ctx, client = _make_ctx(body)

    result = await aos8_get_md_hierarchy(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show configuration node-hierarchy"},
    )
    assert "_meta" not in result
    assert "_global_result" not in result
    rows = result["Configuration node hierarchy"]
    assert {r["Type"] for r in rows} >= {"System", "Group", "Device"}
    assert any(r["Config Node"] == "/md" for r in rows)
    assert any(r["Type"] == "Device" and r["Name"] for r in rows)


async def test_run_show_empty_body_returns_empty_dict():
    """run_show() must treat empty 2xx bodies as success-with-no-data (return
    {}), not raise. Many AOS 8 commands legitimately return empty bodies on
    Conductors with no matching state — e.g. ``show alarms`` with no active
    alarms, ``show user-table`` with no clients. Regression for issue #252.
    """
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_md_hierarchy

    r = MagicMock()
    r.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    r.text = ""
    r.status_code = 200
    r.headers = {"content-type": "text/plain"}

    client = MagicMock()
    client.request = AsyncMock(return_value=r)
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}

    result = await aos8_get_md_hierarchy(ctx)

    assert result == {}


async def test_run_show_text_body_wraps_as_output():
    """run_show() must wrap plain text 2xx bodies as {"output": <text>} —
    matches aos8_show_command's passthrough contract. Some commands like
    ``show log system`` and ``show audit-trail`` return text dumps, not
    JSON. Regression for issue #252.
    """
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_md_hierarchy

    text_body = "<my_xml_tag3xxx>\nMay 4 22:10:46 2026 :354028: log line\n"
    r = MagicMock()
    r.json.side_effect = json.JSONDecodeError("Expecting value", text_body, 0)
    r.text = text_body
    r.status_code = 200
    r.headers = {"content-type": "text/plain"}

    client = MagicMock()
    client.request = AsyncMock(return_value=r)
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}

    result = await aos8_get_md_hierarchy(ctx)

    assert result == {"output": text_body}


async def test_get_object_still_diagnoses_decode_errors():
    """get_object() (used by aos8_get_effective_config) must REMAIN strict —
    the /v1/configuration/object endpoint always returns JSON or an
    Invalid-Object envelope, so any non-JSON body indicates a real protocol
    problem. Surface the diagnostic introduced in v2.5.1.1 / issue #249.
    """
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_effective_config

    r = MagicMock()
    r.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    r.text = "<html>session expired</html>"
    r.status_code = 200
    r.headers = {"content-type": "text/html"}

    client = MagicMock()
    client.request = AsyncMock(return_value=r)
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}

    result = await aos8_get_effective_config(ctx, object_name="ssid_prof")

    assert isinstance(result, str)
    assert "decode error" in result.lower()
    assert "HTTP 200" in result
    assert "text/html" in result
    # Bare json-module error must not leak
    assert "Expecting value: line 1 column 1" not in result


# ---------------------------------------------------------------------------
# DIFF-02: aos8_get_effective_config
# ---------------------------------------------------------------------------


async def test_get_effective_config_required_object_name():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_effective_config

    body = {"_global_result": {"status": "0"}, "_data": ["wlan ssid-profile"]}
    ctx, client = _make_ctx(body)

    result = await aos8_get_effective_config(ctx, object_name="ssid_prof", config_path="/md/branch1")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/object/ssid_prof",
        params={"config_path": "/md/branch1"},
    )
    assert "_global_result" not in result


async def test_get_effective_config_defaults_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_effective_config

    body = {"_global_result": {"status": "0"}, "_data": []}
    ctx, client = _make_ctx(body)

    await aos8_get_effective_config(ctx, object_name="ssid_prof")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/object/ssid_prof",
        params={"config_path": "/md"},
    )


async def test_get_effective_config_entry_type_user():
    """When entry_type is set, it MUST be passed to the API as the ``type``
    query param. AOS 8 uses this to filter out factory defaults / inherited
    entries. Verified live: type=user reduces response size ~93% across
    typical migration audits. Issue #253.
    """
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_effective_config

    body = {"_global_result": {"status": "0"}, "_data": {"role": []}}
    ctx, client = _make_ctx(body)

    await aos8_get_effective_config(
        ctx,
        object_name="role",
        config_path="/md/Campus/East",
        entry_type="user",
    )

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/object/role",
        params={"config_path": "/md/Campus/East", "type": "user"},
    )


async def test_get_effective_config_no_entry_type_omits_type_param():
    """When entry_type is omitted (default None), the ``type`` query param
    MUST NOT be sent — preserves pre-#253 behavior for callers that haven't
    opted into filtering.
    """
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_effective_config

    body = {"_global_result": {"status": "0"}, "_data": {"role": []}}
    ctx, client = _make_ctx(body)

    await aos8_get_effective_config(ctx, object_name="role", config_path="/md")

    # type must not appear in params at all
    call_kwargs = client.request.await_args.kwargs
    assert "type" not in call_kwargs["params"]
    assert call_kwargs["params"] == {"config_path": "/md"}


# ---------------------------------------------------------------------------
# DIFF-03: aos8_get_pending_changes
# ---------------------------------------------------------------------------


async def test_get_pending_changes():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_pending_changes

    body = _load("show_pending_config.json")
    ctx, client = _make_ctx(body)

    result = await aos8_get_pending_changes(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show configuration pending"},
    )
    assert "Pending Configuration" in result
    assert "_global_result" not in result


# ---------------------------------------------------------------------------
# DIFF-04: aos8_get_rf_neighbors
# ---------------------------------------------------------------------------


async def test_get_rf_neighbors():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_rf_neighbors

    body = _load("show_ap_arm_neighbors.json")
    ctx, client = _make_ctx(body)

    await aos8_get_rf_neighbors(ctx, ap_name="ap-01", config_path="/md/branch1")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap arm-neighbors ap-name ap-01", "config_path": "/md/branch1"},
    )


# ---------------------------------------------------------------------------
# DIFF-05: aos8_get_cluster_state
# ---------------------------------------------------------------------------


async def test_get_cluster_state():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_cluster_state

    body = _load("show_lc_cluster_group.json")
    ctx, client = _make_ctx(body)

    await aos8_get_cluster_state(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show lc-cluster group-membership"},
    )


# ---------------------------------------------------------------------------
# DIFF-06: aos8_get_air_monitors
# ---------------------------------------------------------------------------


async def test_get_air_monitors():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_air_monitors

    body = _load("show_ap_monitor_active.json")
    ctx, client = _make_ctx(body)

    await aos8_get_air_monitors(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap monitor active-laser-beams"},
    )


# ---------------------------------------------------------------------------
# DIFF-07: aos8_get_ap_wired_ports
# ---------------------------------------------------------------------------


async def test_get_ap_wired_ports():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_ap_wired_ports

    body = _load("show_ap_port_status.json")
    ctx, client = _make_ctx(body)

    await aos8_get_ap_wired_ports(ctx, ap_name="ap-02")

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show ap port status ap-name ap-02"},
    )


# ---------------------------------------------------------------------------
# DIFF-08: aos8_get_ipsec_tunnels
# ---------------------------------------------------------------------------


async def test_get_ipsec_tunnels():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_ipsec_tunnels

    body = _load("show_crypto_ipsec_sa.json")
    ctx, client = _make_ctx(body)

    await aos8_get_ipsec_tunnels(ctx)

    client.request.assert_awaited_once_with(
        "GET",
        "/v1/configuration/showcommand",
        params={"command": "show crypto ipsec sa"},
    )


# ---------------------------------------------------------------------------
# DIFF-09: aos8_get_md_health_check (composite)
# ---------------------------------------------------------------------------


async def test_get_md_health_check():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_md_health_check

    aps_active = {"_global_result": {"status": "0"}, "Active AP Table": []}
    aps_db = _load("show_ap_database.json")
    alarms = _load("show_alarms.json")
    version = {"_global_result": {"status": "0"}, "Version": "8.10.0.0"}
    users = _load("show_user_summary.json")

    def _route(method, path, params=None, **kwargs):
        cmd = (params or {}).get("command", "")
        if cmd == "show ap active":
            return _resp(aps_active)
        if cmd == "show ap database":
            return _resp(aps_db)
        if cmd == "show alarms all":
            return _resp(alarms)
        if cmd == "show version":
            return _resp(version)
        if cmd == "show user summary":
            return _resp(users)
        return _resp({"_global_result": {"status": "0"}})

    client = MagicMock()
    client.request = AsyncMock(side_effect=_route)
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}

    result = await aos8_get_md_health_check(ctx, config_path="/md/branch1")

    # At least 4 sub-calls
    assert client.request.await_count >= 4
    commands_called = {call.kwargs.get("params", {}).get("command") for call in client.request.await_args_list}
    for required in ("show ap active", "show ap database", "show alarms all", "show version"):
        assert required in commands_called, f"missing sub-call: {required}"

    assert isinstance(result, dict)
    assert result["config_path"] == "/md/branch1"
    for key in ("aps", "clients", "alarms", "firmware"):
        assert key in result, f"result missing key: {key}"


async def test_get_md_health_check_requires_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_md_health_check

    ctx, _ = _make_ctx({"_global_result": {"status": "0"}})
    with pytest.raises(TypeError):
        await aos8_get_md_health_check(ctx)  # type: ignore[call-arg]


async def test_get_md_health_check_handles_partial_failure():
    from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_get_md_health_check

    aps_db = _load("show_ap_database.json")
    alarms = _load("show_alarms.json")
    version = {"_global_result": {"status": "0"}, "Version": "8.10.0.0"}
    users = _load("show_user_summary.json")

    def _route(method, path, params=None, **kwargs):
        cmd = (params or {}).get("command", "")
        if cmd == "show ap active":
            raise RuntimeError("conductor unreachable for active APs")
        if cmd == "show ap database":
            return _resp(aps_db)
        if cmd == "show alarms all":
            return _resp(alarms)
        if cmd == "show version":
            return _resp(version)
        if cmd == "show user summary":
            return _resp(users)
        return _resp({"_global_result": {"status": "0"}})

    client = MagicMock()
    client.request = AsyncMock(side_effect=_route)
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}

    result = await aos8_get_md_health_check(ctx, config_path="/md/branch1")

    # The failing sub-call must be reported as an error inside its section
    # (return_exceptions=True swallow case — Pitfall 3).
    assert isinstance(result, dict)
    aps_section = result.get("aps")
    assert isinstance(aps_section, dict) and "error" in aps_section, (
        f"expected aps section to have error key, got: {aps_section!r}"
    )
    # Other sections still populated
    assert "alarms" in result
    assert "firmware" in result


# ---------------------------------------------------------------------------
# Module-level cross-cut: 9 tools exposed
# ---------------------------------------------------------------------------


def test_diff_tools_count_matches_module():
    from hpe_networking_mcp.platforms.aos8.tools import differentiators

    expected = (
        "aos8_get_md_hierarchy",
        "aos8_get_effective_config",
        "aos8_get_pending_changes",
        "aos8_get_rf_neighbors",
        "aos8_get_cluster_state",
        "aos8_get_air_monitors",
        "aos8_get_ap_wired_ports",
        "aos8_get_ipsec_tunnels",
        "aos8_get_md_health_check",
    )
    for name in expected:
        assert hasattr(differentiators, name), f"differentiators missing {name}"
