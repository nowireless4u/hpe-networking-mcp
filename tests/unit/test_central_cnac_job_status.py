"""Unit tests for ``central_get_cnac_job_status``.

Thin wrapper over the Central NAC Service job-status read
(``GET network-config/v1alpha1/cnac-job/{job-id}/status``). Mocks
``retry_central_command`` at the import site.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

pytestmark = pytest.mark.unit

_PATCH = "hpe_networking_mcp.platforms.central.tools.central_nac.retry_central_command"


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


class TestCentralGetCnacJobStatus:
    @patch(_PATCH)
    async def test_builds_status_path_with_job_id(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.central_nac import central_get_cnac_job_status

        mock_cmd.return_value = {"code": 200, "msg": {"state": "COMPLETED"}}
        result = await central_get_cnac_job_status(_ctx(), job_id="job-123")

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == "network-config/v1alpha1/cnac-job/job-123/status"
        assert kwargs["api_params"] == {}
        assert result == {"state": "COMPLETED"}

    @patch(_PATCH)
    async def test_missing_msg_returns_empty_dict(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.central_nac import central_get_cnac_job_status

        mock_cmd.return_value = {"code": 200}
        assert await central_get_cnac_job_status(_ctx(), job_id="j") == {}

    @patch(_PATCH)
    async def test_non_2xx_raises_toolerror(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.central_nac import central_get_cnac_job_status

        mock_cmd.return_value = {"code": 404, "msg": "no such job"}
        with pytest.raises(ToolError) as exc:
            await central_get_cnac_job_status(_ctx(), job_id="missing")
        assert exc.value.args[0]["status_code"] == 404

    @patch(_PATCH)
    async def test_zero_code_defaults_to_502(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.central_nac import central_get_cnac_job_status

        mock_cmd.return_value = {"msg": "transport error"}
        with pytest.raises(ToolError) as exc:
            await central_get_cnac_job_status(_ctx(), job_id="j")
        assert exc.value.args[0]["status_code"] == 502
