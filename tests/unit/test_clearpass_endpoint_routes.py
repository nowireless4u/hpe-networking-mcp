"""Regression tests pinning the live-verified ClearPass routes from issue #469.

Every route here previously pointed at a hand-written path that returns
HTTP 405 (or, for the CoA-by-session case, silently fetched templates
instead of performing the CoA). Each was probed against a live CPPM with
bogus identifiers — current-path-broken and corrected-path-valid — before
these fixes. These tests pin verb + path + load-bearing body fields so the
corrected routes can't regress.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {}
    return ctx


def _client() -> MagicMock:
    client = MagicMock()
    client.request = AsyncMock(return_value={"ok": True})
    return client


def _call(client: MagicMock) -> tuple[str, str, dict | None, dict | None]:
    """Return (method, path, params, json_body) of the single request made."""
    args = client.request.call_args
    method, path = args.args[0], args.args[1]
    return method, path, args.kwargs.get("params"), args.kwargs.get("json_body")


@pytest.mark.unit
class TestGuestActionRoutes:
    @patch("hpe_networking_mcp.platforms.clearpass.tools.manage_guests.get_clearpass_client", new_callable=AsyncMock)
    async def test_send_credentials_uses_sendreceipt_with_confirm(self, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.manage_guests import clearpass_send_guest_credentials

        client = _client()
        mock_get.return_value = client
        await clearpass_send_guest_credentials(_ctx(), guest_id="42", delivery_method="email", confirmed=True)
        method, path, _, body = _call(client)
        assert (method, path) == ("post", "/guest/42/sendreceipt/smtp")  # email travels as smtp
        assert body == {"confirm": 1}

    @patch("hpe_networking_mcp.platforms.clearpass.tools.manage_guests.get_clearpass_client", new_callable=AsyncMock)
    async def test_generate_pass_is_a_get_render_with_template(self, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.manage_guests import clearpass_generate_guest_pass

        client = _client()
        mock_get.return_value = client
        await clearpass_generate_guest_pass(_ctx(), guest_id="42", pass_type="digital", template_id="7")
        method, path, _, _ = _call(client)
        assert (method, path) == ("get", "/guest/42/pass/7")

    @patch("hpe_networking_mcp.platforms.clearpass.tools.manage_guests.get_clearpass_client", new_callable=AsyncMock)
    async def test_sponsor_reject_travels_as_register_reject(self, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.manage_guests import clearpass_process_sponsor_action

        client = _client()
        mock_get.return_value = client
        await clearpass_process_sponsor_action(
            _ctx(), guest_id="42", action="reject", token="t", register_token="rt", confirmed=True
        )
        method, path, _, body = _call(client)
        assert (method, path) == ("post", "/guest/42/sponsor")  # no /approve|/reject path segment
        assert body == {"token": "t", "register_token": "rt", "register_reject": True}


@pytest.mark.unit
class TestSessionControlRoutes:
    @patch("hpe_networking_mcp.platforms.clearpass.tools.manage_sessions.get_clearpass_client", new_callable=AsyncMock)
    async def test_bulk_disconnect_uses_session_action_with_wrapped_filter(self, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.manage_sessions import clearpass_disconnect_session

        client = _client()
        mock_get.return_value = client
        await clearpass_disconnect_session(
            _ctx(), target_type="bulk", filter={"nasipaddress": "192.0.2.1"}, confirmed=True
        )
        method, path, _, body = _call(client)
        assert (method, path) == ("post", "/session-action/disconnect")
        assert body == {"filter": {"nasipaddress": "192.0.2.1"}}  # wrapped, not bare

    @patch("hpe_networking_mcp.platforms.clearpass.tools.manage_sessions.get_clearpass_client", new_callable=AsyncMock)
    async def test_mac_disconnect_uses_selector_route(self, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.manage_sessions import clearpass_disconnect_session

        client = _client()
        mock_get.return_value = client
        await clearpass_disconnect_session(_ctx(), target_type="mac", target_value="aa:bb:cc:dd:ee:ff", confirmed=True)
        method, path, _, _ = _call(client)
        assert (method, path) == ("post", "/session-action/disconnect/mac/aa:bb:cc:dd:ee:ff")

    @patch("hpe_networking_mcp.platforms.clearpass.tools.manage_sessions.get_clearpass_client", new_callable=AsyncMock)
    async def test_coa_by_session_id_posts_reauthorize_with_confirm(self, mock_get):
        """The old code issued a GET here — which returns reauth templates and performs nothing."""
        from hpe_networking_mcp.platforms.clearpass.tools.manage_sessions import clearpass_perform_coa

        client = _client()
        mock_get.return_value = client
        await clearpass_perform_coa(_ctx(), target_type="session_id", target_value="S1", confirmed=True)
        method, path, _, body = _call(client)
        assert (method, path) == ("post", "/session/S1/reauthorize")
        assert body == {"confirm_reauthorize": True}

    @patch("hpe_networking_mcp.platforms.clearpass.tools.manage_sessions.get_clearpass_client", new_callable=AsyncMock)
    async def test_coa_by_username_requires_enforcement_profile(self, mock_get):
        from fastmcp.exceptions import ToolError

        from hpe_networking_mcp.platforms.clearpass.tools.manage_sessions import clearpass_perform_coa

        mock_get.return_value = _client()
        with pytest.raises(ToolError) as exc:
            await clearpass_perform_coa(_ctx(), target_type="username", target_value="visitor", confirmed=True)
        assert exc.value.args[0]["status_code"] == 400
        assert "enforcement_profile" in exc.value.args[0]["message"]

    @patch("hpe_networking_mcp.platforms.clearpass.tools.manage_sessions.get_clearpass_client", new_callable=AsyncMock)
    async def test_coa_by_username_uses_session_action_route(self, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.manage_sessions import clearpass_perform_coa

        client = _client()
        mock_get.return_value = client
        await clearpass_perform_coa(
            _ctx(),
            target_type="username",
            target_value="visitor",
            enforcement_profile=["GUEST-COA"],
            confirmed=True,
        )
        method, path, _, body = _call(client)
        assert (method, path) == ("post", "/session-action/coa/username/visitor")
        assert body == {"enforcement_profile": ["GUEST-COA"]}


@pytest.mark.unit
class TestConfigSelectorRoutes:
    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.manage_server_config._confirm_write",
        new_callable=AsyncMock,
        return_value=None,
    )
    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.manage_server_config.get_clearpass_client",
        new_callable=AsyncMock,
    )
    async def test_admin_user_by_name_uses_user_id_route(self, mock_get, _mock_confirm):
        from hpe_networking_mcp.platforms.clearpass.tools.manage_server_config import clearpass_manage_admin_user

        client = _client()
        mock_get.return_value = client
        await clearpass_manage_admin_user(_ctx(), action_type="delete", payload={}, name="ops-admin", confirmed=True)
        method, path, _, _ = _call(client)
        assert (method, path) == ("delete", "/admin-user/user-id/ops-admin")

    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.manage_server_config._confirm_write",
        new_callable=AsyncMock,
        return_value=None,
    )
    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.manage_server_config.get_clearpass_client",
        new_callable=AsyncMock,
    )
    async def test_attribute_by_name_requires_entity(self, mock_get, _mock_confirm):
        from fastmcp.exceptions import ToolError

        from hpe_networking_mcp.platforms.clearpass.tools.manage_server_config import clearpass_manage_attribute

        mock_get.return_value = _client()
        with pytest.raises(ToolError) as exc:
            await clearpass_manage_attribute(_ctx(), action_type="delete", payload={}, name="probe-attr", confirmed=True)
        assert exc.value.args[0]["status_code"] == 400
        assert "entity_name" in exc.value.args[0]["message"]

    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.manage_local_config._confirm_write",
        new_callable=AsyncMock,
        return_value=None,
    )
    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.manage_local_config.get_clearpass_client",
        new_callable=AsyncMock,
    )
    async def test_ad_join_uses_action_prefix_route(self, mock_get, _mock_confirm):
        from hpe_networking_mcp.platforms.clearpass.tools.manage_local_config import clearpass_manage_ad_domain

        client = _client()
        mock_get.return_value = client
        await clearpass_manage_ad_domain(
            _ctx(), action_type="join", server_uuid="u-1", payload={"password": "x"}, confirmed=True
        )
        method, path, _, _ = _call(client)
        assert (method, path) == ("put", "/ad-domain/join/u-1")  # action before uuid

    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.integrations.get_clearpass_client",
        new_callable=AsyncMock,
    )
    async def test_extension_log_uses_slash_route(self, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.integrations import clearpass_get_extension_log

        client = _client()
        mock_get.return_value = client
        await clearpass_get_extension_log(_ctx(), extension_id="e-1")
        method, path, _, _ = _call(client)
        assert method == "get"
        assert path.startswith("/extension/instance/e-1/log")  # not /extension-instance/
