"""Unit tests for the Central scope hierarchy/global read tools.

Covers ``central_get_global_scope`` and ``central_get_hierarchy`` — thin
wrappers over the New Central Scope Management API (``network-config/v1/global``
and ``network-config/v1/hierarchy``). Mocks ``retry_central_command`` at the
import site; it's the only thing the wrappers call besides
``ctx.lifespan_context["central_conn"]``.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

pytestmark = pytest.mark.unit

_PATCH = "hpe_networking_mcp.platforms.central.tools.sites.retry_central_command"


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


class TestCentralGetGlobalScope:
    @patch(_PATCH)
    async def test_calls_global_endpoint_no_params(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.sites import central_get_global_scope

        mock_cmd.return_value = {"code": 200, "msg": {"scopeId": "100"}}
        result = await central_get_global_scope(_ctx())

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == "network-config/v1/global"
        assert kwargs["api_params"] == {}
        assert result == {"scopeId": "100"}

    @patch(_PATCH)
    async def test_missing_msg_returns_empty_dict(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.sites import central_get_global_scope

        mock_cmd.return_value = {"code": 200}
        assert await central_get_global_scope(_ctx()) == {}

    @patch(_PATCH)
    async def test_non_2xx_raises_toolerror(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.sites import central_get_global_scope

        mock_cmd.return_value = {"code": 500, "msg": "boom"}
        with pytest.raises(ToolError) as exc:
            await central_get_global_scope(_ctx())
        assert exc.value.args[0]["status_code"] == 500


class TestCentralGetHierarchy:
    @patch(_PATCH)
    async def test_passes_id_and_type(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.sites import central_get_hierarchy

        mock_cmd.return_value = {"code": 200, "msg": {"children": []}}
        result = await central_get_hierarchy(_ctx(), scope_id="42", scope_type="site-collection")

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == "network-config/v1/hierarchy"
        assert kwargs["api_params"] == {"id": "42", "type": "site-collection"}
        assert result == {"children": []}

    @patch(_PATCH)
    async def test_non_2xx_raises_toolerror_with_code(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.sites import central_get_hierarchy

        mock_cmd.return_value = {"code": 404, "msg": "not found"}
        with pytest.raises(ToolError) as exc:
            await central_get_hierarchy(_ctx(), scope_id="x", scope_type="org")
        assert exc.value.args[0]["status_code"] == 404

    @patch(_PATCH)
    async def test_zero_code_defaults_to_502(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.sites import central_get_hierarchy

        mock_cmd.return_value = {"msg": "transport failure"}
        with pytest.raises(ToolError) as exc:
            await central_get_hierarchy(_ctx(), scope_id="x", scope_type="org")
        assert exc.value.args[0]["status_code"] == 502
