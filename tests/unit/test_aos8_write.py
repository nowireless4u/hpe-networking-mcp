"""Wave 0 red-baseline tests for AOS8 WRITE tools (WRITE-01..12).

These tests fail with ModuleNotFoundError until plan 05-02 implements
``platforms.aos8.tools.writes``. Each test pins the exact endpoint path,
parameter shape, body structure, response contract, tag set, config_path
requirements, and elicitation behavior that every implementation must satisfy.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).parent / "fixtures" / "aos8"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _make_ctx(response_body: dict, *, elicitation_mode: str = "disabled") -> tuple[MagicMock, MagicMock]:
    response = MagicMock(spec=httpx.Response)
    response.json.return_value = response_body
    client = MagicMock()
    client.request = AsyncMock(return_value=response)
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}
    ctx.get_state = AsyncMock(return_value=elicitation_mode)
    return ctx, client


EXPECTED_WRITE_TOOLS = {
    "aos8_manage_ssid_profile",
    "aos8_manage_virtual_ap",
    "aos8_manage_ap_group",
    "aos8_manage_user_role",
    "aos8_manage_vlan",
    "aos8_manage_aaa_server",
    "aos8_manage_aaa_server_group",
    "aos8_manage_acl",
    "aos8_manage_netdestination",
    "aos8_disconnect_client",
    "aos8_reboot_ap",
    "aos8_write_memory",
}
MANAGE_TOOLS = EXPECTED_WRITE_TOOLS - {"aos8_disconnect_client", "aos8_reboot_ap", "aos8_write_memory"}

# ---------------------------------------------------------------------------
# WRITE-01: aos8_manage_ssid_profile
# ---------------------------------------------------------------------------


async def test_manage_ssid_profile_create_calls_correct_endpoint():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ssid_profile

    body = _load_fixture("write_ssid_prof_success.json")
    ctx, client = _make_ctx(body)

    result = await aos8_manage_ssid_profile(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"profile-name": "guest", "essid": {"essid": "Guest"}},
        confirmed=True,
    )

    client.request.assert_awaited_once_with(
        "POST",
        "/v1/configuration/object",
        params={"config_path": "/md"},
        json_body={
            "ssid_prof": {
                "profile-name": "guest",
                "essid": {"essid": "Guest"},
                "_action": "add",
            }
        },
    )
    assert result["requires_write_memory_for"] == ["/md"]
    assert "result" in result


async def test_manage_ssid_profile_update_uses_modify_action():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ssid_profile

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    await aos8_manage_ssid_profile(
        ctx,
        config_path="/md",
        action_type="update",
        payload={"profile-name": "guest"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert sent["ssid_prof"]["_action"] == "modify"


async def test_manage_ssid_profile_delete_uses_delete_action():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ssid_profile

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    await aos8_manage_ssid_profile(
        ctx,
        config_path="/md",
        action_type="delete",
        payload={"profile-name": "guest"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert sent["ssid_prof"]["_action"] == "delete"


async def test_manage_ssid_profile_invalid_action_raises():
    from fastmcp.exceptions import ToolError
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ssid_profile

    ctx, _ = _make_ctx({})
    with pytest.raises(ToolError):
        await aos8_manage_ssid_profile(
            ctx,
            config_path="/md",
            action_type="garbage",
            payload={"profile-name": "guest"},
            confirmed=True,
        )


async def test_manage_ssid_profile_missing_profile_name_raises():
    from fastmcp.exceptions import ToolError
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ssid_profile

    ctx, _ = _make_ctx({})
    with pytest.raises(ToolError):
        await aos8_manage_ssid_profile(
            ctx,
            config_path="/md",
            action_type="create",
            payload={"essid": {"essid": "Guest"}},
            confirmed=True,
        )


async def test_manage_ssid_profile_global_result_error_returns_error_dict():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ssid_profile

    from hpe_networking_mcp.platforms.aos8.client import AOS8APIError

    ctx, client = _make_ctx({})
    client.request = AsyncMock(side_effect=AOS8APIError("Profile already exists"))

    result = await aos8_manage_ssid_profile(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"profile-name": "guest"},
        confirmed=True,
    )
    assert isinstance(result["result"]["error"], str)
    assert result["result"]["error"].startswith("AOS8 API error")
    assert result["requires_write_memory_for"] == []


# ---------------------------------------------------------------------------
# WRITE-02: aos8_manage_virtual_ap
# ---------------------------------------------------------------------------


async def test_manage_virtual_ap_create_posts_virtual_ap_body():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_virtual_ap

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    result = await aos8_manage_virtual_ap(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"profile-name": "default-vap"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert "virtual_ap" in sent
    assert sent["virtual_ap"]["profile-name"] == "default-vap"
    assert result["requires_write_memory_for"] == ["/md"]


# ---------------------------------------------------------------------------
# WRITE-03: aos8_manage_ap_group
# ---------------------------------------------------------------------------


async def test_manage_ap_group_create_posts_ap_group_body():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ap_group

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    result = await aos8_manage_ap_group(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"profile-name": "default-grp"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert "ap_group" in sent
    assert sent["ap_group"]["profile-name"] == "default-grp"
    assert result["requires_write_memory_for"] == ["/md"]


# ---------------------------------------------------------------------------
# WRITE-04: aos8_manage_user_role
# ---------------------------------------------------------------------------


async def test_manage_user_role_create_posts_role_body():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_user_role

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    result = await aos8_manage_user_role(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"rolename": "guest-role"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert "role" in sent
    assert sent["role"]["rolename"] == "guest-role"
    assert result["requires_write_memory_for"] == ["/md"]


# ---------------------------------------------------------------------------
# WRITE-05: aos8_manage_vlan
# ---------------------------------------------------------------------------


async def test_manage_vlan_create_posts_vlan_id_body():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_vlan

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    result = await aos8_manage_vlan(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"id": 100},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert "vlan_id" in sent
    assert sent["vlan_id"]["id"] == 100
    assert result["requires_write_memory_for"] == ["/md"]


# ---------------------------------------------------------------------------
# WRITE-06: aos8_manage_aaa_server (four server_type variants)
# ---------------------------------------------------------------------------


async def test_manage_aaa_server_radius_uses_rad_server_key():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_aaa_server

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    result = await aos8_manage_aaa_server(
        ctx,
        config_path="/md",
        action_type="create",
        server_type="radius",
        payload={"rad_server_name": "radius1"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert "rad_server" in sent
    assert result["requires_write_memory_for"] == ["/md"]


async def test_manage_aaa_server_tacacs_uses_tacacs_server_key():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_aaa_server

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    await aos8_manage_aaa_server(
        ctx,
        config_path="/md",
        action_type="create",
        server_type="tacacs",
        payload={"tacacs_server_name": "tac1"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert "tacacs_server" in sent


async def test_manage_aaa_server_ldap_uses_ldap_server_key():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_aaa_server

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    await aos8_manage_aaa_server(
        ctx,
        config_path="/md",
        action_type="create",
        server_type="ldap",
        payload={"ldap_server_name": "ldap1"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert "ldap_server" in sent


async def test_manage_aaa_server_internal_uses_internal_db_server_key():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_aaa_server

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    await aos8_manage_aaa_server(
        ctx,
        config_path="/md",
        action_type="create",
        server_type="internal",
        payload={"internal_db_server_name": "int1"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert "internal_db_server" in sent


# ---------------------------------------------------------------------------
# WRITE-07: aos8_manage_aaa_server_group
# ---------------------------------------------------------------------------


async def test_manage_aaa_server_group_create_posts_server_group_prof_body():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_aaa_server_group

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    result = await aos8_manage_aaa_server_group(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"sg_name": "default-sg"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert "server_group_prof" in sent
    assert sent["server_group_prof"]["sg_name"] == "default-sg"
    assert result["requires_write_memory_for"] == ["/md"]


# ---------------------------------------------------------------------------
# WRITE-08: aos8_manage_acl
# ---------------------------------------------------------------------------


async def test_manage_acl_create_posts_acl_sess_body():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_acl

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    result = await aos8_manage_acl(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"accname": "guest-acl"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert "acl_sess" in sent
    assert sent["acl_sess"]["accname"] == "guest-acl"
    assert result["requires_write_memory_for"] == ["/md"]


# ---------------------------------------------------------------------------
# WRITE-09: aos8_manage_netdestination
# ---------------------------------------------------------------------------


async def test_manage_netdestination_create_posts_netdst_body():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_netdestination

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    result = await aos8_manage_netdestination(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"dstname": "internal-net"},
        confirmed=True,
    )
    sent = client.request.await_args.kwargs["json_body"]
    assert "netdst" in sent
    assert sent["netdst"]["dstname"] == "internal-net"
    assert result["requires_write_memory_for"] == ["/md"]


# ---------------------------------------------------------------------------
# WRITE-10: aos8_disconnect_client
# ---------------------------------------------------------------------------


async def test_disconnect_client_no_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_disconnect_client

    ctx, client = _make_ctx({"_global_result": {"status": "0"}})
    result = await aos8_disconnect_client(ctx, mac="aa:bb:cc:dd:ee:ff", confirmed=True)

    assert result["requires_write_memory_for"] == []
    args = client.request.await_args
    assert args.kwargs.get("params") in (None, {})
    assert args.kwargs["json_body"] == {"aaa_user_delete": {"mac": "aa:bb:cc:dd:ee:ff"}}


# ---------------------------------------------------------------------------
# WRITE-11: aos8_reboot_ap
# ---------------------------------------------------------------------------


async def test_reboot_ap_no_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_reboot_ap

    ctx, client = _make_ctx({"_global_result": {"status": "0"}})
    result = await aos8_reboot_ap(ctx, ap_name="AP-3F-12", confirmed=True)

    assert result["requires_write_memory_for"] == []
    args = client.request.await_args
    assert args.kwargs.get("params") in (None, {})
    assert args.kwargs["json_body"] == {"apboot": {"ap-name": "AP-3F-12"}}


# ---------------------------------------------------------------------------
# WRITE-12: aos8_write_memory
# ---------------------------------------------------------------------------


async def test_write_memory_uses_dedicated_endpoint():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_write_memory

    ctx, client = _make_ctx({"write_memory": {"_result": {"status": 0}}})
    result = await aos8_write_memory(ctx, config_path="/md", confirmed=True)

    assert "requires_write_memory_for" not in result  # D-12: circular — must be absent
    assert "result" in result
    client.request.assert_awaited_once_with(
        "POST",
        "/v1/configuration/object/write_memory",
        params={"config_path": "/md"},
        json_body={},
    )


async def test_write_memory_empty_body_not_none():
    """Guard against Pitfall 10: json_body must be {} not None."""
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_write_memory

    ctx, client = _make_ctx({"write_memory": {"_result": {"status": 0}}})
    await aos8_write_memory(ctx, config_path="/md", confirmed=True)

    args = client.request.await_args
    assert args.kwargs["json_body"] == {}
    assert args.kwargs["json_body"] is not None


# ---------------------------------------------------------------------------
# Cross-cut: config_path requirement
# ---------------------------------------------------------------------------


async def test_config_path_required_on_manage_ssid_profile():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ssid_profile

    ctx, _ = _make_ctx({})
    with pytest.raises((TypeError, Exception)):
        # Calling without config_path should raise a Pydantic ValidationError or TypeError
        await aos8_manage_ssid_profile(  # type: ignore[call-arg]
            ctx,
            action_type="create",
            payload={"profile-name": "guest"},
            confirmed=True,
        )


async def test_config_path_required_on_write_memory():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_write_memory

    ctx, _ = _make_ctx({})
    with pytest.raises((TypeError, Exception)):
        await aos8_write_memory(ctx, confirmed=True)  # type: ignore[call-arg]


def test_disconnect_client_does_not_accept_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_disconnect_client

    sig = inspect.signature(aos8_disconnect_client)
    assert "config_path" not in sig.parameters


def test_reboot_ap_does_not_accept_config_path():
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_reboot_ap

    sig = inspect.signature(aos8_reboot_ap)
    assert "config_path" not in sig.parameters


# ---------------------------------------------------------------------------
# Cross-cut: response shape contract (requires_write_memory_for on WRITE-01..11)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tool_name,kwargs",
    [
        (
            "aos8_manage_ssid_profile",
            {"config_path": "/md", "action_type": "create", "payload": {"profile-name": "p1"}, "confirmed": True},
        ),
        (
            "aos8_manage_virtual_ap",
            {"config_path": "/md", "action_type": "create", "payload": {"profile-name": "v1"}, "confirmed": True},
        ),
        (
            "aos8_manage_ap_group",
            {"config_path": "/md", "action_type": "create", "payload": {"profile-name": "g1"}, "confirmed": True},
        ),
        (
            "aos8_manage_user_role",
            {"config_path": "/md", "action_type": "create", "payload": {"rolename": "r1"}, "confirmed": True},
        ),
        (
            "aos8_manage_vlan",
            {"config_path": "/md", "action_type": "create", "payload": {"id": 10}, "confirmed": True},
        ),
        (
            "aos8_manage_aaa_server",
            {
                "config_path": "/md",
                "action_type": "create",
                "server_type": "radius",
                "payload": {"rad_server_name": "r1"},
                "confirmed": True,
            },
        ),
        (
            "aos8_manage_aaa_server_group",
            {"config_path": "/md", "action_type": "create", "payload": {"sg_name": "sg1"}, "confirmed": True},
        ),
        (
            "aos8_manage_acl",
            {"config_path": "/md", "action_type": "create", "payload": {"accname": "a1"}, "confirmed": True},
        ),
        (
            "aos8_manage_netdestination",
            {"config_path": "/md", "action_type": "create", "payload": {"dstname": "d1"}, "confirmed": True},
        ),
        ("aos8_disconnect_client", {"mac": "aa:bb:cc:dd:ee:ff", "confirmed": True}),
        ("aos8_reboot_ap", {"ap_name": "AP-01", "confirmed": True}),
    ],
)
async def test_response_shape_contract_writes_01_to_11(tool_name: str, kwargs: dict):
    import importlib

    mod = importlib.import_module("hpe_networking_mcp.platforms.aos8.tools.writes")
    tool_fn = getattr(mod, tool_name)

    ctx, _ = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    result = await tool_fn(ctx, **kwargs)

    assert isinstance(result, dict), f"{tool_name} did not return a dict"
    assert "requires_write_memory_for" in result, f"{tool_name} missing requires_write_memory_for"
    assert "result" in result, f"{tool_name} missing result key"


# ---------------------------------------------------------------------------
# Cross-cut: no implicit write_memory from manage_X tools
# ---------------------------------------------------------------------------


async def test_no_implicit_write_memory():
    """Asserts manage_X does not auto-call write_memory (only one request emitted)."""
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ssid_profile

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"))
    await aos8_manage_ssid_profile(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"profile-name": "guest"},
        confirmed=True,
    )

    assert client.request.await_count == 1
    call_path = client.request.await_args.args[1]
    assert call_path == "/v1/configuration/object"
    assert "write_memory" not in call_path


# ---------------------------------------------------------------------------
# Cross-cut: elicitation gate
# ---------------------------------------------------------------------------


async def test_elicitation_required_when_not_confirmed():
    """When mode=chat_confirm and confirmed=False, tool must return confirmation_required."""
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ssid_profile

    ctx, client = _make_ctx({}, elicitation_mode="chat_confirm")
    result = await aos8_manage_ssid_profile(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"profile-name": "guest"},
        confirmed=False,
    )

    assert isinstance(result, dict)
    assert result.get("status") == "confirmation_required"
    client.request.assert_not_awaited()


async def test_elicitation_disabled_state_auto_accepts():
    """When mode=disabled, confirmed=False still proceeds — elicitation auto-accepts."""
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ssid_profile

    ctx, client = _make_ctx(_load_fixture("write_ssid_prof_success.json"), elicitation_mode="disabled")
    await aos8_manage_ssid_profile(
        ctx,
        config_path="/md",
        action_type="create",
        payload={"profile-name": "guest"},
        confirmed=False,
    )

    client.request.assert_awaited_once()


# ---------------------------------------------------------------------------
# Cross-cut: tag enforcement
# ---------------------------------------------------------------------------


def test_all_write_tools_carry_aos8_write_tag():
    """All 12 write tools must have the aos8_write tag for gating."""
    from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES
    from hpe_networking_mcp.platforms.aos8.tools import writes  # noqa: F401

    aos8 = REGISTRIES["aos8"]
    for name in EXPECTED_WRITE_TOOLS:
        assert name in aos8, f"{name} not registered in REGISTRIES['aos8']"
        assert "aos8_write" in aos8[name].tags, f"{name} missing aos8_write tag"


def test_manage_tools_carry_aos8_write_delete_tag():
    """WRITE-01..09 must carry aos8_write_delete; WRITE-10..12 must not."""
    from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES
    from hpe_networking_mcp.platforms.aos8.tools import writes  # noqa: F401

    aos8 = REGISTRIES["aos8"]
    for name in MANAGE_TOOLS:
        assert "aos8_write_delete" in aos8[name].tags, f"{name} missing aos8_write_delete tag"

    for name in {"aos8_disconnect_client", "aos8_reboot_ap", "aos8_write_memory"}:
        assert "aos8_write_delete" not in aos8[name].tags, f"{name} should NOT have aos8_write_delete tag"


# ---------------------------------------------------------------------------
# Cross-cut: WRITE and WRITE_DELETE annotation constants
# ---------------------------------------------------------------------------


def test_writes_module_has_write_and_write_delete_constants():
    from hpe_networking_mcp.platforms.aos8.tools.writes import WRITE, WRITE_DELETE

    assert WRITE_DELETE.destructiveHint is True
    assert WRITE.destructiveHint is False
    assert WRITE_DELETE.readOnlyHint is False
    assert WRITE.readOnlyHint is False
    assert WRITE_DELETE.idempotentHint is False
    assert WRITE.idempotentHint is False
    assert WRITE_DELETE.openWorldHint is True
    assert WRITE.openWorldHint is True


# ---------------------------------------------------------------------------
# Cross-cut: elicitation middleware enables AOS8 tags
# ---------------------------------------------------------------------------


async def test_elicitation_middleware_enables_aos8_tags():
    """ElicitationMiddleware must call enable_components for aos8 tags when gate is on."""
    from unittest.mock import AsyncMock, MagicMock

    from hpe_networking_mcp.middleware.elicitation import ElicitationMiddleware

    middleware = ElicitationMiddleware()

    # Build a fake MiddlewareContext
    mock_ctx = MagicMock()
    mock_ctx.enable_components = AsyncMock()
    mock_ctx.set_state = AsyncMock()

    config = MagicMock()
    config.enable_aos8_write_tools = True
    config.enable_mist_write_tools = False
    config.enable_central_write_tools = False
    config.enable_clearpass_write_tools = False
    config.enable_apstra_write_tools = False
    config.enable_axis_write_tools = False
    config.disable_elicitation = True

    mock_ctx.lifespan_context = {"config": config}

    fake_message = MagicMock()
    fake_message.params.capabilities.elicitation = None

    mock_mw_ctx = MagicMock()
    mock_mw_ctx.fastmcp_context = mock_ctx
    mock_mw_ctx.message = fake_message

    async def call_next(ctx):
        return MagicMock()

    await middleware.on_initialize(mock_mw_ctx, call_next)

    # Check that enable_components was called with aos8 tags
    calls = mock_ctx.enable_components.call_args_list
    tag_sets = [set(call.kwargs.get("tags", call.args[0] if call.args else set())) for call in calls]
    assert any({"aos8_write", "aos8_write_delete"} <= tags for tags in tag_sets), (
        "ElicitationMiddleware did not call enable_components with {'aos8_write', 'aos8_write_delete'}"
    )


# ---------------------------------------------------------------------------
# Cross-cut: TOOLS dict wiring
# ---------------------------------------------------------------------------


def test_tools_dict_includes_writes():
    """After Plan 05-03, TOOLS['writes'] must contain all 12 write tool names."""
    from hpe_networking_mcp.platforms.aos8 import TOOLS

    assert "writes" in TOOLS, "TOOLS dict missing 'writes' category"
    assert set(TOOLS["writes"]) == EXPECTED_WRITE_TOOLS, (
        f"TOOLS['writes'] mismatch.\n  Expected: {EXPECTED_WRITE_TOOLS}\n  Got:      {set(TOOLS['writes'])}"
    )
