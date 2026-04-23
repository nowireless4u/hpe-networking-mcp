"""Unit tests for central configuration CRUD helper.

Covers the PUT-clobber fix for #155 — ``_execute_config_action`` now uses
PATCH for updates by default (server-side merge) and only issues PUT when
the caller opts into full-resource replacement via ``replace_existing=True``.
This mirrors the v0.9.2.2 fix applied to ``central_manage_wlan_profile`` and
closes the same class of silent-clobber bug for sites, site collections, and
device groups.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hpe_networking_mcp.platforms.central.tools.configuration import (
    ActionType,
    _execute_config_action,
)


def _fake_ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    ctx.get_state = AsyncMock(return_value="prompt")
    return ctx


def _ok_response() -> dict:
    return {"code": 200, "msg": {"ok": True}}


@pytest.mark.unit
class TestExecuteConfigActionMethodSelection:
    """Asserts the helper picks the right HTTP method for each action_type."""

    @pytest.mark.asyncio
    @patch("hpe_networking_mcp.platforms.central.tools.configuration.retry_central_command")
    async def test_create_uses_post(self, mock_retry):
        mock_retry.return_value = _ok_response()
        ctx = _fake_ctx()

        result = await _execute_config_action(
            ctx=ctx,
            action_type=ActionType.CREATE,
            resource_name="site",
            api_path="network-config/v1/sites",
            resource_id=None,
            payload={"name": "HQ"},
            confirmed=True,
        )

        assert result["status"] == "success"
        assert mock_retry.call_args.kwargs["api_method"] == "POST"
        assert mock_retry.call_args.kwargs["api_path"] == "network-config/v1/sites"

    @pytest.mark.asyncio
    @patch("hpe_networking_mcp.platforms.central.tools.configuration.retry_central_command")
    async def test_update_default_uses_patch(self, mock_retry):
        """The whole point of the fix: default update must be PATCH, not PUT."""
        mock_retry.return_value = _ok_response()
        ctx = _fake_ctx()

        await _execute_config_action(
            ctx=ctx,
            action_type=ActionType.UPDATE,
            resource_name="site",
            api_path="network-config/v1/sites",
            resource_id="site-123",
            payload={"timezone": "UTC"},
            confirmed=True,  # skip elicitation
        )

        assert mock_retry.call_args.kwargs["api_method"] == "PATCH"
        # Body still carries scopeId to identify the target resource
        assert mock_retry.call_args.kwargs["api_data"]["scopeId"] == "site-123"
        assert mock_retry.call_args.kwargs["api_data"]["timezone"] == "UTC"

    @pytest.mark.asyncio
    @patch("hpe_networking_mcp.platforms.central.tools.configuration.retry_central_command")
    async def test_update_with_replace_existing_uses_put(self, mock_retry):
        """Escape hatch: replace_existing=True opts into full-replacement PUT."""
        mock_retry.return_value = _ok_response()
        ctx = _fake_ctx()

        await _execute_config_action(
            ctx=ctx,
            action_type=ActionType.UPDATE,
            resource_name="site",
            api_path="network-config/v1/sites",
            resource_id="site-123",
            payload={"name": "HQ", "address": "123 Main"},
            confirmed=True,
            replace_existing=True,
        )

        assert mock_retry.call_args.kwargs["api_method"] == "PUT"

    @pytest.mark.asyncio
    @patch("hpe_networking_mcp.platforms.central.tools.configuration.retry_central_command")
    async def test_delete_uses_delete_at_bulk_path(self, mock_retry):
        mock_retry.return_value = _ok_response()
        ctx = _fake_ctx()

        await _execute_config_action(
            ctx=ctx,
            action_type=ActionType.DELETE,
            resource_name="site",
            api_path="network-config/v1/sites",
            resource_id="site-123",
            payload={},
            confirmed=True,
        )

        assert mock_retry.call_args.kwargs["api_method"] == "DELETE"
        assert mock_retry.call_args.kwargs["api_path"] == "network-config/v1/sites/bulk"
        assert mock_retry.call_args.kwargs["api_data"] == {"items": [{"id": "site-123"}]}


@pytest.mark.unit
class TestExecuteConfigActionRequiredIds:
    """Update and delete require a resource_id; the helper raises without one."""

    @pytest.mark.asyncio
    async def test_update_without_resource_id_raises(self):
        from fastmcp.exceptions import ToolError

        ctx = _fake_ctx()
        with pytest.raises(ToolError):
            await _execute_config_action(
                ctx=ctx,
                action_type=ActionType.UPDATE,
                resource_name="site",
                api_path="network-config/v1/sites",
                resource_id=None,
                payload={"name": "x"},
                confirmed=True,
            )

    @pytest.mark.asyncio
    async def test_delete_without_resource_id_raises(self):
        from fastmcp.exceptions import ToolError

        ctx = _fake_ctx()
        with pytest.raises(ToolError):
            await _execute_config_action(
                ctx=ctx,
                action_type=ActionType.DELETE,
                resource_name="site",
                api_path="network-config/v1/sites",
                resource_id=None,
                payload={},
                confirmed=True,
            )

    @pytest.mark.asyncio
    @patch("hpe_networking_mcp.platforms.central.tools.configuration.retry_central_command")
    async def test_create_without_resource_id_is_fine(self, mock_retry):
        """Create doesn't need an existing resource_id."""
        mock_retry.return_value = _ok_response()
        ctx = _fake_ctx()

        result = await _execute_config_action(
            ctx=ctx,
            action_type=ActionType.CREATE,
            resource_name="site",
            api_path="network-config/v1/sites",
            resource_id=None,
            payload={"name": "HQ"},
            confirmed=True,
        )
        assert result["status"] == "success"
