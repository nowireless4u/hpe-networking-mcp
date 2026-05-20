"""Unit tests for central audit-logs tools.

Regression coverage for the API-version fix: the live audit-trail routes are
``network-services/v1/audits`` and ``network-services/v1/audit/{id}`` — the
tools previously called the ``v1alpha1`` variant, which gateway-404s. Mocks
``retry_central_command`` at the import site (the only thing the wrappers call
besides ``ctx.lifespan_context["central_conn"]``).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


class TestCentralGetAuditLogs:
    @patch("hpe_networking_mcp.platforms.central.tools.audit_logs.retry_central_command")
    async def test_uses_v1_path_and_passes_params(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.audit_logs import central_get_audit_logs

        mock_cmd.return_value = {"code": 200, "msg": {"audits": [{"auditId": "x"}], "totalCount": 1}}
        result = await central_get_audit_logs(
            _ctx(), start_at="1779214249441", end_at="1779300649441", filter="action eq 'Cleared'", sort="-timestamp"
        )

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        # The bug was v1alpha1; the live route is v1.
        assert kwargs["api_path"] == "network-services/v1/audits"
        assert kwargs["api_params"] == {
            "start-at": "1779214249441",
            "end-at": "1779300649441",
            "limit": 200,
            "offset": 1,
            "filter": "action eq 'Cleared'",
            "sort": "-timestamp",
        }
        assert result == {"audits": [{"auditId": "x"}], "totalCount": 1}

    @patch("hpe_networking_mcp.platforms.central.tools.audit_logs.retry_central_command")
    async def test_non_2xx_raises_tool_error(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.audit_logs import central_get_audit_logs

        mock_cmd.return_value = {"code": 404, "msg": {"message": "404 Route Not Found"}}
        with pytest.raises(ToolError) as exc_info:
            await central_get_audit_logs(_ctx(), start_at="1", end_at="2")
        assert exc_info.value.args[0]["status_code"] == 404


class TestDeprecationSurfacing:
    @patch("hpe_networking_mcp.platforms.central.tools.audit_logs.retry_central_command")
    async def test_deprecation_headers_surfaced_in_payload(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.audit_logs import central_get_audit_logs

        mock_cmd.return_value = {
            "code": 200,
            "msg": {"audits": [], "totalCount": 0},
            "headers": {"deprecation": "true", "sunset": "Wed, 20 May 2026 23:59:59 GMT"},
        }
        result = await central_get_audit_logs(_ctx(), start_at="1", end_at="2")

        assert result["_deprecation"]["deprecated"] is True
        assert result["_deprecation"]["sunset"] == "Wed, 20 May 2026 23:59:59 GMT"
        assert "sunset" in result["_deprecation"]["message"].lower()
        # original body preserved
        assert result["audits"] == []
        assert result["totalCount"] == 0

    @patch("hpe_networking_mcp.platforms.central.tools.audit_logs.retry_central_command")
    async def test_no_deprecation_key_when_headers_absent(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.audit_logs import central_get_audit_logs

        mock_cmd.return_value = {"code": 200, "msg": {"audits": [], "totalCount": 0}, "headers": {}}
        result = await central_get_audit_logs(_ctx(), start_at="1", end_at="2")
        assert "_deprecation" not in result

    def test_deprecation_notice_helper(self):
        from hpe_networking_mcp.platforms.central.utils import deprecation_notice

        assert deprecation_notice({"headers": {}}) is None
        assert deprecation_notice({"headers": {"sunset": "X"}})["deprecated"] is True
        assert deprecation_notice({"headers": {"deprecation": "true"}})["deprecated"] is True


class TestCentralGetAuditLogDetail:
    @patch("hpe_networking_mcp.platforms.central.tools.audit_logs.retry_central_command")
    async def test_uses_v1_path_with_id(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.audit_logs import central_get_audit_log_detail

        mock_cmd.return_value = {"code": 200, "msg": {"auditId": "abc-123", "action": "Cleared"}}
        result = await central_get_audit_log_detail(_ctx(), id="abc-123")

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == "network-services/v1/audit/abc-123"
        assert result == {"auditId": "abc-123", "action": "Cleared"}
