"""Unit tests for the Central config-write scope architecture.

Every network-config write documents ``object-type`` (LOCAL|SHARED, default
SHARED), with ``scope-id``/``device-function`` mandatory for LOCAL and forbidden
for SHARED. The old inline logic hardcoded ``object-type=LOCAL`` and only sent
scope params when *both* were present — so SHARED was unreachable and passing
one of the pair silently dropped both (landing the write at the wrong scope,
because the API ignores partial query params). ``build_config_write_params``
centralizes and fixes that; these tests pin the contract.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms.central.tools.security_policy import build_config_write_params

pytestmark = pytest.mark.unit


class TestBuildConfigWriteParams:
    def test_no_args_defaults_to_shared(self):
        """Empty dict → the API applies its SHARED default (library object)."""
        assert build_config_write_params() == {}

    def test_explicit_shared(self):
        assert build_config_write_params(object_type="SHARED") == {"object-type": "SHARED"}

    def test_shared_is_case_insensitive(self):
        assert build_config_write_params(object_type="shared") == {"object-type": "SHARED"}

    def test_local_with_both_scope_params(self):
        assert build_config_write_params(object_type="LOCAL", scope_id="s1", device_function="CAMPUS_AP") == {
            "object-type": "LOCAL",
            "scope-id": "s1",
            "device-function": "CAMPUS_AP",
        }

    def test_scope_without_object_type_infers_local(self):
        """Backward compatible: the prior behavior sent LOCAL when scoped."""
        assert build_config_write_params(scope_id="s1", device_function="CAMPUS_AP") == {
            "object-type": "LOCAL",
            "scope-id": "s1",
            "device-function": "CAMPUS_AP",
        }

    def test_local_missing_device_function_raises(self):
        with pytest.raises(ToolError) as e:
            build_config_write_params(object_type="LOCAL", scope_id="s1")
        assert e.value.args[0]["status_code"] == 400

    def test_local_missing_scope_id_raises(self):
        with pytest.raises(ToolError) as e:
            build_config_write_params(object_type="LOCAL", device_function="CAMPUS_AP")
        assert e.value.args[0]["status_code"] == 400

    def test_partial_scope_without_object_type_raises_not_silently_dropped(self):
        """The core bug fix: scope_id alone used to silently drop both params and
        write to the wrong scope. It must now fail loudly."""
        with pytest.raises(ToolError) as e:
            build_config_write_params(scope_id="s1")
        assert e.value.args[0]["status_code"] == 400

    def test_shared_with_scope_id_raises(self):
        with pytest.raises(ToolError) as e:
            build_config_write_params(object_type="SHARED", scope_id="s1")
        assert e.value.args[0]["status_code"] == 400

    def test_invalid_object_type_raises(self):
        with pytest.raises(ToolError) as e:
            build_config_write_params(object_type="GLOBAL")
        assert e.value.args[0]["status_code"] == 400


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


_PATCH = "hpe_networking_mcp.platforms.central.tools.security_policy.retry_central_command"


class TestManageResourceThreadsObjectType:
    @patch(_PATCH)
    async def test_shared_write_sends_object_type(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_manage_roles

        mock_cmd.return_value = {"code": 200, "msg": {}}
        await central_manage_roles(_ctx(), name="r1", action_type="create", payload={"x": 1}, object_type="SHARED")

        assert mock_cmd.call_args.kwargs["api_params"] == {"object-type": "SHARED"}

    @patch(_PATCH)
    async def test_local_write_sends_scope(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_manage_roles

        mock_cmd.return_value = {"code": 200, "msg": {}}
        await central_manage_roles(
            _ctx(),
            name="r1",
            action_type="create",
            payload={"x": 1},
            object_type="LOCAL",
            scope_id="s1",
            device_function="CAMPUS_AP",
        )

        assert mock_cmd.call_args.kwargs["api_params"] == {
            "object-type": "LOCAL",
            "scope-id": "s1",
            "device-function": "CAMPUS_AP",
        }

    @patch(_PATCH)
    async def test_partial_scope_raises_before_dispatch(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.roles_policy import central_manage_roles

        with pytest.raises(ToolError):
            await central_manage_roles(_ctx(), name="r1", action_type="create", payload={"x": 1}, scope_id="s1")
        mock_cmd.assert_not_called()

    @patch("hpe_networking_mcp.platforms.central.tools.wlan_profiles.retry_central_command")
    async def test_wlan_profile_write_supports_scope(self, mock_cmd):
        """The hand-curated WLAN write must honor scope like the rest."""
        from hpe_networking_mcp.platforms.central.tools.wlan_profiles import central_manage_wlan_profile

        mock_cmd.return_value = {"code": 200, "msg": {}}
        await central_manage_wlan_profile(
            _ctx(),
            ssid="Corp",
            action_type="create",
            payload={"opmode": "WPA3_SAE"},
            object_type="LOCAL",
            scope_id="s1",
            device_function="CAMPUS_AP",
        )

        assert mock_cmd.call_args.kwargs["api_params"] == {
            "object-type": "LOCAL",
            "scope-id": "s1",
            "device-function": "CAMPUS_AP",
        }
