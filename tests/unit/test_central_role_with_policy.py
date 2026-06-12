"""Unit tests for ``central_get_role_with_policy``.

Pins the bundled-fetch behavior: the tool GETs ``/roles/{name}``, reads
the role's ``policies[]`` back-reference array, and GETs each referenced
``/policies/{policy-name}``. It surfaces the role plus the list of bound
policies, gracefully reporting which resources came back empty (a common
case: many shared roles are skeletal, many roles reference no policy).
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
    async def test_resolves_bound_policies_from_role_back_reference(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.roles import central_get_role_with_policy

        # Role references two policies via its policies[] back-reference.
        mock_retry.side_effect = [
            _ok(
                {
                    "name": "night-night",
                    "description": "Restricted",
                    "policies": [{"name": "deny-all"}, {"name": "allow-dns"}],
                }
            ),
            _ok({"name": "deny-all", "type": "POLICY_TYPE_SECURITY", "security-policy": {}}),
            _ok({"name": "allow-dns", "type": "POLICY_TYPE_SECURITY", "security-policy": {}}),
        ]

        result = await central_get_role_with_policy(_ctx(), name="night-night")

        assert mock_retry.call_count == 3
        paths = [c.kwargs["api_path"] for c in mock_retry.call_args_list]
        assert paths == [
            "network-config/v1alpha1/roles/night-night",
            "network-config/v1alpha1/policies/deny-all",
            "network-config/v1alpha1/policies/allow-dns",
        ]
        assert all(c.kwargs["api_method"] == "GET" for c in mock_retry.call_args_list)
        assert result["name"] == "night-night"
        assert result["role"]["description"] == "Restricted"
        assert [p["name"] for p in result["policies"]] == ["deny-all", "allow-dns"]
        assert result["not_found"] == []
        assert result["errors"] == []

    @patch("hpe_networking_mcp.platforms.central.tools.roles.retry_central_command")
    async def test_role_with_no_bound_policies_returns_empty_list(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.roles import central_get_role_with_policy

        # Role present but carries no policies[] back-reference at all.
        mock_retry.side_effect = [_ok({"name": "ADAMS-MPSK", "description": "ADAMS-MPSK"})]
        result = await central_get_role_with_policy(_ctx(), name="ADAMS-MPSK")

        assert mock_retry.call_count == 1  # no policy fetches issued
        assert result["role"] is not None
        assert result["policies"] == []
        assert result["not_found"] == []
        assert result["errors"] == []

    @patch("hpe_networking_mcp.platforms.central.tools.roles.retry_central_command")
    async def test_referenced_policy_missing_reported_in_not_found(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.roles import central_get_role_with_policy

        # Role references a policy, but that policy GET returns empty body.
        mock_retry.side_effect = [
            _ok({"name": "stale", "policies": [{"name": "ghost-policy"}]}),
            _ok({}),
        ]
        result = await central_get_role_with_policy(_ctx(), name="stale")

        assert result["role"] is not None
        assert result["policies"] == []
        assert result["not_found"] == ["policy:ghost-policy"]
        assert result["errors"] == []

    @patch("hpe_networking_mcp.platforms.central.tools.roles.retry_central_command")
    async def test_missing_role_reports_not_found_and_skips_policies(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.roles import central_get_role_with_policy

        mock_retry.side_effect = [_ok({})]
        result = await central_get_role_with_policy(_ctx(), name="nonexistent")

        assert mock_retry.call_count == 1
        assert result["role"] is None
        assert result["policies"] == []
        assert result["not_found"] == ["role"]
        assert result["errors"] == []

    @patch("hpe_networking_mcp.platforms.central.tools.roles.retry_central_command")
    async def test_policy_error_doesnt_block_other_policy_fetches(self, mock_retry):
        """A failure fetching one bound policy must not abort the others —
        the operator gets whatever data is available plus an errors note.
        """
        from hpe_networking_mcp.platforms.central.tools.roles import central_get_role_with_policy

        mock_retry.side_effect = [
            _ok({"name": "night-night", "policies": [{"name": "boom"}, {"name": "good"}]}),
            Exception("Client error from central: 500 internal error"),
            _ok({"name": "good", "security-policy": {"policy-rule": [{"position": 1}]}}),
        ]
        result = await central_get_role_with_policy(_ctx(), name="night-night")

        assert result["role"] is not None
        assert len(result["policies"]) == 1
        assert result["policies"][0]["security-policy"]["policy-rule"] == [{"position": 1}]
        assert len(result["errors"]) == 1
        assert "policy:boom" in result["errors"][0]
        assert result["not_found"] == []  # not "not found", explicitly errored

    @patch("hpe_networking_mcp.platforms.central.tools.roles.retry_central_command")
    async def test_policies_back_reference_accepts_bare_strings_and_dedupes(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.roles import central_get_role_with_policy

        # Mixed entry shapes + a duplicate name — dedupe, preserve order.
        mock_retry.side_effect = [
            _ok({"name": "r", "policies": ["p1", {"name": "p1"}, {"name": "p2"}]}),
            _ok({"name": "p1"}),
            _ok({"name": "p2"}),
        ]
        result = await central_get_role_with_policy(_ctx(), name="r")

        paths = [c.kwargs["api_path"] for c in mock_retry.call_args_list]
        assert paths == [
            "network-config/v1alpha1/roles/r",
            "network-config/v1alpha1/policies/p1",
            "network-config/v1alpha1/policies/p2",
        ]
        assert [p["name"] for p in result["policies"]] == ["p1", "p2"]
