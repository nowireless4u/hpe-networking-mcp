"""Unit tests for ``central_get_role_with_policy``.

Pins the bundled-fetch behavior introduced in v3.1.6.0 — the tool
issues two GETs (/roles/{name} + /policies/{name}) and surfaces both
results together, gracefully reporting which endpoints came back
empty (a common case: many shared roles are skeletal, many roles have
no separately-named security policy).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    ctx.get_state = AsyncMock(return_value="prompt")
    return ctx


def _ok(msg: object | None = None) -> dict:
    return {"code": 200, "msg": msg if msg is not None else {}}


class TestCentralGetRoleWithPolicy:
    @patch("hpe_networking_mcp.platforms.central.tools.roles.retry_central_command")
    async def test_issues_two_gets_to_role_and_policy_endpoints(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.roles import central_get_role_with_policy

        mock_retry.side_effect = [
            _ok({"name": "night-night", "description": "Restricted"}),
            _ok({"name": "night-night", "type": "POLICY_TYPE_SECURITY", "security-policy": {}}),
        ]

        result = await central_get_role_with_policy(_ctx(), name="night-night")

        assert mock_retry.call_count == 2
        paths = [c.kwargs["api_path"] for c in mock_retry.call_args_list]
        assert paths == [
            "network-config/v1alpha1/roles/night-night",
            "network-config/v1alpha1/policies/night-night",
        ]
        assert all(c.kwargs["api_method"] == "GET" for c in mock_retry.call_args_list)
        assert result["name"] == "night-night"
        assert result["role"]["description"] == "Restricted"
        assert result["policy"]["type"] == "POLICY_TYPE_SECURITY"
        assert result["not_found"] == []
        assert result["errors"] == []

    @patch("hpe_networking_mcp.platforms.central.tools.roles.retry_central_command")
    async def test_missing_policy_reported_in_not_found_not_errors(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.roles import central_get_role_with_policy

        # role exists; policy returns 200 with empty body (Central convention for "not present")
        mock_retry.side_effect = [
            _ok({"name": "ADAMS-MPSK", "description": "ADAMS-MPSK"}),
            _ok({}),
        ]
        result = await central_get_role_with_policy(_ctx(), name="ADAMS-MPSK")

        assert result["role"] is not None
        assert result["policy"] is None
        assert result["not_found"] == ["policy"]
        assert result["errors"] == []

    @patch("hpe_networking_mcp.platforms.central.tools.roles.retry_central_command")
    async def test_both_missing_reports_both_not_found(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.roles import central_get_role_with_policy

        mock_retry.side_effect = [_ok({}), _ok({})]
        result = await central_get_role_with_policy(_ctx(), name="nonexistent")

        assert result["role"] is None
        assert result["policy"] is None
        assert result["not_found"] == ["role", "policy"]
        assert result["errors"] == []

    @patch("hpe_networking_mcp.platforms.central.tools.roles.retry_central_command")
    async def test_role_error_doesnt_block_policy_fetch(self, mock_retry):
        """A failure on one endpoint must not abort the other — the
        operator gets whatever data is available plus an errors note.
        """
        from hpe_networking_mcp.platforms.central.tools.roles import central_get_role_with_policy

        mock_retry.side_effect = [
            Exception("Client error from central: 500 internal error"),
            _ok({"name": "night-night", "security-policy": {"policy-rule": [{"position": 1}]}}),
        ]
        result = await central_get_role_with_policy(_ctx(), name="night-night")

        assert result["role"] is None
        assert result["policy"] is not None
        assert result["policy"]["security-policy"]["policy-rule"] == [{"position": 1}]
        assert len(result["errors"]) == 1
        assert "role" in result["errors"][0]
        assert result["not_found"] == []  # not "not found", explicitly errored
