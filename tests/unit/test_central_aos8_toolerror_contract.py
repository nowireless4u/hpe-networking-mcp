"""Contract tests: validation guards raise structured ToolError payloads (v3.2.1.10).

These lock the two most-shared write helpers — Central's ``_manage_resource``
(used by every ``central_manage_*`` security-policy tool) and AOS 8's
``_post_managed_object`` body — to the structured
``ToolError({"status_code": 400, "message": ...})`` form rather than a plain
string. Both guards fire before any upstream client call, so a bare context
mock is enough.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastmcp.exceptions import ToolError

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


class TestCentralManageResourceContract:
    async def test_bad_action_type_raises_structured_400(self):
        from hpe_networking_mcp.platforms.central.tools.security import (
            central_manage_net_groups,
        )

        with pytest.raises(ToolError) as exc_info:
            await central_manage_net_groups(
                _ctx(),
                name="x",
                action_type="bogus",
                payload={},
                scope_id=None,
                device_function=None,
                confirmed=True,
            )
        assert exc_info.value.args[0]["status_code"] == 400
        assert "Invalid action_type" in exc_info.value.args[0]["message"]


class TestAos8WritesContract:
    async def test_bad_action_type_raises_structured_400(self):
        from hpe_networking_mcp.platforms.aos8.tools.writes import (
            aos8_manage_ssid_profile,
        )

        with pytest.raises(ToolError) as exc_info:
            await aos8_manage_ssid_profile(
                _ctx(),
                config_path="/md",
                action_type="bogus",
                payload={"profile-name": "x"},
                confirmed=True,
            )
        assert exc_info.value.args[0]["status_code"] == 400
        assert "Invalid action_type" in exc_info.value.args[0]["message"]

    async def test_missing_identifier_raises_structured_400(self):
        from hpe_networking_mcp.platforms.aos8.tools.writes import (
            aos8_manage_ssid_profile,
        )

        with pytest.raises(ToolError) as exc_info:
            await aos8_manage_ssid_profile(
                _ctx(),
                config_path="/md",
                action_type="create",
                payload={},  # missing 'profile-name'
                confirmed=True,
            )
        assert exc_info.value.args[0]["status_code"] == 400
        assert "profile-name" in exc_info.value.args[0]["message"]
