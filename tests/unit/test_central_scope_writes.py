"""Unit tests for the Central scope write tools (membership + bulk delete).

Covers the seven mutation tools added to ``sites.py``. Mocks
``retry_central_command`` at its import site (confirmation is structural —
the universal gate at ``central_invoke_tool`` dispatch — so direct calls
need no confirm mocking).
Also asserts every tool carries the ``central_write_delete`` gating tag — the
ONLY tag Central's write gate (server-side ``Visibility`` transform +
``_WRITE_TAG_BY_PLATFORM``) acts on. A bare ``central_write`` tag would ship
ungated.
"""

from __future__ import annotations

import importlib
from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES

pytestmark = pytest.mark.unit


@pytest.fixture
def central_registry():
    """Reload sites.py so its @tool decorators re-record into the central
    registry — robust against other tests that reload/clear the registry."""
    import hpe_networking_mcp.platforms.central.tools.sites as sites_mod

    importlib.reload(sites_mod)
    return REGISTRIES["central"]


_CMD = "hpe_networking_mcp.platforms.central.tools.sites.retry_central_command"

WRITE_TOOLS = [
    "central_add_devices_to_device_group",
    "central_remove_devices_from_device_group",
    "central_create_device_group_with_devices",
    "central_add_devices_to_site",
    "central_bulk_delete_device_groups",
    "central_bulk_delete_sites",
    "central_bulk_delete_site_collections",
]


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


class TestGatingTag:
    def test_all_write_tools_carry_central_write_delete(self, central_registry):
        for name in WRITE_TOOLS:
            assert name in central_registry, f"{name} not recorded in central registry"
            assert "central_write_delete" in central_registry[name].tags, (
                f"{name} missing central_write_delete gating tag"
            )


class TestMembershipWrites:
    @patch(_CMD)
    async def test_add_devices_to_device_group_confirmed(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.sites import central_add_devices_to_device_group

        mock_cmd.return_value = {"code": 200, "msg": {"ok": True}}
        result = await central_add_devices_to_device_group(
            _ctx(), dest_scope_id="55", devices=["S1", "S2"], confirmed=True
        )

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "POST"
        assert kwargs["api_path"] == "network-config/v1/device-groups-add-devices"
        assert kwargs["api_data"] == {"desScopeId": "55", "devices": ["S1", "S2"]}
        assert result == {"ok": True}

    @patch(_CMD)
    async def test_unconfirmed_direct_call_dispatches(self, mock_cmd):
        """Inline guards are gone — confirmation is enforced by the universal
        gate at central_invoke_tool dispatch (see test_gate_end_to_end). The
        tool body itself dispatches regardless of confirmed."""
        from hpe_networking_mcp.platforms.central.tools.sites import central_add_devices_to_site

        mock_cmd.return_value = {"code": 200, "msg": {"ok": True}}
        result = await central_add_devices_to_site(_ctx(), dest_scope_id="7", devices=["S1"])

        assert result == {"ok": True}
        mock_cmd.assert_called_once()

    @patch(_CMD)
    async def test_create_group_omits_description_when_none(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.sites import central_create_device_group_with_devices

        mock_cmd.return_value = {"code": 200, "msg": {}}
        await central_create_device_group_with_devices(_ctx(), scope_name="DG1", devices=["S1"])
        assert mock_cmd.call_args.kwargs["api_data"] == {"scopeName": "DG1", "devices": ["S1"]}

        await central_create_device_group_with_devices(_ctx(), scope_name="DG1", devices=["S1"], description="d")
        assert mock_cmd.call_args.kwargs["api_data"] == {"scopeName": "DG1", "devices": ["S1"], "description": "d"}

    @patch(_CMD)
    async def test_non_2xx_raises_toolerror(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.sites import central_remove_devices_from_device_group

        mock_cmd.return_value = {"code": 422, "msg": "bad serials"}
        with pytest.raises(ToolError) as exc:
            await central_remove_devices_from_device_group(_ctx(), devices=["BAD"], confirmed=True)
        assert exc.value.args[0]["status_code"] == 422


class TestBulkDeletes:
    @patch(_CMD)
    async def test_bulk_delete_sites_uses_delete_and_items_body(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.sites import central_bulk_delete_sites

        mock_cmd.return_value = {"code": 200, "msg": {"deleted": 2}}
        items = [{"id": "1"}, {"id": "2"}]
        result = await central_bulk_delete_sites(_ctx(), items=items, confirmed=True)

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "DELETE"
        assert kwargs["api_path"] == "network-config/v1/sites/bulk"
        assert kwargs["api_data"] == {"items": items}
        assert result == {"deleted": 2}
