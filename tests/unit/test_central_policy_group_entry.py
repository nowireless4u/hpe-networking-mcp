"""Unit tests for the per-entry policy-group tools (v3.2.1.9).

``central_get_policy_group_list`` / ``central_manage_policy_group_list``
wrap the nested item path
``network-config/v1alpha1/policy-groups/policy-group/policy-group-list/{name}``
via the shared ``_get_resource`` / ``_manage_resource`` helpers in
``security_policy.py`` — so the mock target is ``retry_central_command``
at that helper module's import site.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

_ITEM_PATH = "network-config/v1alpha1/policy-groups/policy-group/policy-group-list/web-rules"


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


class TestGetPolicyGroupEntry:
    @patch("hpe_networking_mcp.platforms.central.tools.security_policy.retry_central_command")
    async def test_builds_nested_item_path(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.roles_policy import (
            central_get_policy_group_list,
        )

        mock_cmd.return_value = {"code": 200, "msg": {"name": "web-rules", "position": 1}}
        result = await central_get_policy_group_list(_ctx(), name="web-rules")

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == _ITEM_PATH
        assert result == {"name": "web-rules", "position": 1}


class TestManagePolicyGroupEntry:
    @patch("hpe_networking_mcp.platforms.central.tools.security_policy.retry_central_command")
    async def test_create_posts_to_nested_item_path(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.roles_policy import (
            central_manage_policy_group_list,
        )

        mock_cmd.return_value = {"code": 200, "msg": {}}
        # action_type="create" does not trigger elicitation.
        await central_manage_policy_group_list(
            _ctx(),
            name="web-rules",
            action_type="create",
            payload={"name": "web-rules", "position": 1},
        )

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "POST"
        assert kwargs["api_path"] == _ITEM_PATH
        assert kwargs["api_data"] == {"name": "web-rules", "position": 1}

    @patch("hpe_networking_mcp.platforms.central.tools.security_policy.retry_central_command")
    async def test_delete_uses_delete_method(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.roles_policy import (
            central_manage_policy_group_list,
        )

        mock_cmd.return_value = {"code": 200, "msg": {}}
        # confirmed=True bypasses the elicitation prompt for non-create actions.
        await central_manage_policy_group_list(
            _ctx(),
            name="web-rules",
            action_type="delete",
            payload={},
            confirmed=True,
        )

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "DELETE"
        assert kwargs["api_path"] == _ITEM_PATH
