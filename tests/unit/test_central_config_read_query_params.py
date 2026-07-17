"""Unit tests for config-read query parameters on the Central config tools.

Every ``network-config/v1alpha1`` GET endpoint documents the same eight query
parameters (``view-type``, ``object-type``, ``scope-id``, ``device-function``,
``effective``, ``detailed``, ``limit``, ``offset``), but the read tools used to
expose only the path param — so scoped and effective-config reads were
impossible and pagination was unreachable (#623).

Two behaviors here were established against the live API, which **ignores**
unknown or incomplete query params instead of erroring — meaning a regression
would be silent rather than loud:

* ``limit`` is only honored when ``offset`` is also sent.
* ``view_type='LOCAL'`` without ``scope_id`` returns a *different* scope's
  configuration rather than failing.

The mock target is ``retry_central_command`` at the ``security_policy`` helper
module's import site (the shared ``_get_resource``).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

pytestmark = pytest.mark.unit

_PATCH_TARGET = "hpe_networking_mcp.platforms.central.tools.security_policy.retry_central_command"


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


class TestQueryParamPassthrough:
    @patch(_PATCH_TARGET)
    async def test_no_params_sends_no_query(self, mock_cmd):
        """Baseline: an unparameterized read must not invent query params."""
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_get_roles

        mock_cmd.return_value = {"code": 200, "msg": {"role": []}}
        await central_get_roles(_ctx())

        assert mock_cmd.call_args.kwargs["api_params"] is None

    @patch(_PATCH_TARGET)
    async def test_scoped_read_sends_kebab_case_params(self, mock_cmd):
        """The wire format is kebab-case, not the snake_case of the signature."""
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_get_roles

        mock_cmd.return_value = {"code": 200, "msg": {"role": []}}
        await central_get_roles(
            _ctx(),
            view_type="LOCAL",
            scope_id="scope-123",
            device_function="CAMPUS_AP",
            effective=True,
            detailed=True,
        )

        params = mock_cmd.call_args.kwargs["api_params"]
        assert params == {
            "view-type": "LOCAL",
            "scope-id": "scope-123",
            "device-function": "CAMPUS_AP",
            "effective": True,
            "detailed": True,
        }

    @patch(_PATCH_TARGET)
    async def test_none_values_are_omitted(self, mock_cmd):
        """None must be dropped so the API's own defaults apply."""
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_get_roles

        mock_cmd.return_value = {"code": 200, "msg": {"role": []}}
        await central_get_roles(_ctx(), detailed=True)

        assert mock_cmd.call_args.kwargs["api_params"] == {"detailed": True}

    @patch(_PATCH_TARGET)
    async def test_effective_false_is_sent_not_dropped(self, mock_cmd):
        """effective=False is meaningful (committed-only) and must survive."""
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_get_roles

        mock_cmd.return_value = {"code": 200, "msg": {"role": []}}
        await central_get_roles(_ctx(), scope_id="scope-1", effective=False)

        assert mock_cmd.call_args.kwargs["api_params"]["effective"] is False


class TestLimitRequiresOffset:
    """The API silently ignores `limit` unless `offset` accompanies it."""

    @patch(_PATCH_TARGET)
    async def test_limit_alone_defaults_offset_to_zero(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_get_roles

        mock_cmd.return_value = {"code": 200, "msg": {"role": []}}
        await central_get_roles(_ctx(), limit=5)

        params = mock_cmd.call_args.kwargs["api_params"]
        assert params == {"limit": 5, "offset": 0}, "limit without offset is ignored upstream"

    @patch(_PATCH_TARGET)
    async def test_explicit_offset_is_preserved(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_get_roles

        mock_cmd.return_value = {"code": 200, "msg": {"role": []}}
        await central_get_roles(_ctx(), limit=5, offset=10)

        assert mock_cmd.call_args.kwargs["api_params"] == {"limit": 5, "offset": 10}

    @patch(_PATCH_TARGET)
    async def test_offset_alone_is_untouched(self, mock_cmd):
        """offset alone is a valid request (API applies its default page size)."""
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_get_roles

        mock_cmd.return_value = {"code": 200, "msg": {"role": []}}
        await central_get_roles(_ctx(), offset=3)

        assert mock_cmd.call_args.kwargs["api_params"] == {"offset": 3}


class TestLocalViewRequiresScope:
    """view_type=LOCAL without scope_id silently reads the wrong scope upstream."""

    @patch(_PATCH_TARGET)
    async def test_local_without_scope_raises_400(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_get_roles

        with pytest.raises(ToolError) as exc:
            await central_get_roles(_ctx(), view_type="LOCAL")

        assert exc.value.args[0]["status_code"] == 400
        assert "scope_id" in exc.value.args[0]["message"]
        mock_cmd.assert_not_called()

    @patch(_PATCH_TARGET)
    async def test_local_guard_is_case_insensitive(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_get_roles

        with pytest.raises(ToolError):
            await central_get_roles(_ctx(), view_type="local")

        mock_cmd.assert_not_called()

    @patch(_PATCH_TARGET)
    async def test_local_with_scope_is_allowed(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_get_roles

        mock_cmd.return_value = {"code": 200, "msg": {"role": []}}
        await central_get_roles(_ctx(), view_type="LOCAL", scope_id="scope-1")

        assert mock_cmd.call_args.kwargs["api_params"]["scope-id"] == "scope-1"

    @patch(_PATCH_TARGET)
    async def test_library_view_needs_no_scope(self, mock_cmd):
        """LIBRARY ignores scope entirely — it must not trip the LOCAL guard."""
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_get_roles

        mock_cmd.return_value = {"code": 200, "msg": {"role": []}}
        await central_get_roles(_ctx(), view_type="LIBRARY")

        assert mock_cmd.call_args.kwargs["api_params"] == {"view-type": "LIBRARY"}


class TestCoverage:
    """Guard the sweep itself: the params must be on the tools, not just the helper."""

    def test_config_read_tools_expose_scope_params(self):
        import importlib
        import inspect
        import pkgutil

        import hpe_networking_mcp.platforms.central.tools as tools_pkg
        from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES

        for mod in pkgutil.iter_modules(tools_pkg.__path__):
            importlib.import_module(f"{tools_pkg.__name__}.{mod.name}")

        reg = REGISTRIES["central"]
        scoped = [
            name
            for name, spec in reg.items()
            if name.startswith("central_get_") and "effective" in inspect.signature(spec.func).parameters
        ]
        # 209 config-read tools sit on the standard 8-param endpoints. The
        # remaining central_get_* tools are either non-config reads or the
        # cnac-*/device-collections endpoints, which document a different
        # param set (search/sort/next/filter) and are intentionally excluded.
        assert len(scoped) == 209, f"expected 209 scope-aware config reads, found {len(scoped)}"

    def test_non_standard_endpoints_do_not_advertise_scope_params(self):
        """cnac-* endpoints ignore scope params upstream; advertising them would mislead."""
        import inspect

        from hpe_networking_mcp.platforms.central.tools.central_nac_service import central_get_cnac_job

        params = inspect.signature(central_get_cnac_job).parameters
        assert "scope_id" not in params
        assert "effective" not in params
