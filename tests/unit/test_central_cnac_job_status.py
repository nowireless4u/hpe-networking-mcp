"""Unit tests for ``central_get_cnac_job_status``.

Thin wrapper over the Central NAC Service job-status read
(``GET network-config/v1alpha1/cnac-job/{job-id}/status``). Regenerated
from the vendor OAS as an operation tool delegating to the shared
``_operation_request`` helper (in ``security_policy.py``), so it returns
the operation envelope (``{"status": "success"/"error", ...}``) rather
than the bare ``msg`` / ``ToolError`` shape the hand-curated version
used. Patch ``retry_central_command`` at the shared helper module.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

_PATCH = "hpe_networking_mcp.platforms.central.tools.security_policy.retry_central_command"


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    ctx.get_state = AsyncMock(return_value="prompt")
    return ctx


class TestCentralGetCnacJobStatus:
    @patch(_PATCH)
    async def test_builds_status_path_with_job_id(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.central_nac_service import central_get_cnac_job_status

        mock_cmd.return_value = {"code": 200, "msg": {"state": "COMPLETED"}}
        result = await central_get_cnac_job_status(_ctx(), job_id="job-123")

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == "network-config/v1alpha1/cnac-job/job-123/status"
        assert result["status"] == "success"
        assert result["data"] == {"state": "COMPLETED"}

    @patch(_PATCH)
    async def test_missing_msg_returns_empty_data(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.central_nac_service import central_get_cnac_job_status

        mock_cmd.return_value = {"code": 200}
        result = await central_get_cnac_job_status(_ctx(), job_id="j")
        assert result["status"] == "success"
        assert result["data"] == {}

    @patch(_PATCH)
    async def test_non_2xx_returns_error_status(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.central_nac_service import central_get_cnac_job_status

        mock_cmd.return_value = {"code": 404, "msg": "no such job"}
        result = await central_get_cnac_job_status(_ctx(), job_id="missing")
        assert result["status"] == "error"
        assert result["code"] == 404
        assert result["message"] == "no such job"

    @patch(_PATCH)
    async def test_zero_code_returns_error_status(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.central_nac_service import central_get_cnac_job_status

        mock_cmd.return_value = {"msg": "transport error"}
        result = await central_get_cnac_job_status(_ctx(), job_id="j")
        assert result["status"] == "error"
        assert result["code"] == 0
