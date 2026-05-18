"""Unit tests for the ClearPass policy-visualizer MCP tools.

Mocks ``get_clearpass_session`` + ``clearpass_get`` at the import site
so the tools never reach the network. Verifies endpoint paths, parameter
validation, and the fan-out shape for the compile path.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {}
    return ctx


def _hal(items: list[dict]) -> dict:
    """Wrap items in the HAL ``{_embedded: {items: [...]}}`` envelope."""
    return {"_embedded": {"items": items}, "count": len(items), "total": len(items)}


class TestListPolicyServices:
    @patch("hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.clearpass_get")
    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.get_clearpass_session",
        new_callable=AsyncMock,
    )
    async def test_returns_slim_summary(self, mock_session, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            clearpass_list_policy_services,
        )

        mock_session.return_value = MagicMock()
        mock_get.return_value = _hal(
            [
                {
                    "id": 1,
                    "name": "[Test Service]",
                    "type": "RADIUS",
                    "template": "RADIUS Enforcement",
                    "enabled": True,
                    "role_mapping_policy": "RM1",
                    "enf_policy": "EP1",
                    "description": "x",
                    "hit_count": 42,
                    "monitor_mode": False,
                    "order_no": 5,
                    "this_should_be_dropped": "yes",
                }
            ]
        )
        result = await clearpass_list_policy_services(_ctx())
        assert isinstance(result, list)
        assert len(result) == 1
        entry = result[0]
        assert entry["id"] == 1
        assert entry["name"] == "[Test Service]"
        assert entry["enabled"] is True
        assert entry["hit_count"] == 42
        # extra unrelated fields are dropped
        assert "this_should_be_dropped" not in entry

    @patch("hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.clearpass_get")
    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.get_clearpass_session",
        new_callable=AsyncMock,
    )
    async def test_hits_config_service_endpoint(self, mock_session, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            clearpass_list_policy_services,
        )

        mock_session.return_value = MagicMock()
        mock_get.return_value = _hal([])
        await clearpass_list_policy_services(_ctx(), limit=50)

        # Single call with the right URL prefix
        assert mock_get.call_count == 1
        path = mock_get.call_args.args[1]
        assert path.startswith("/config/service?")
        assert "limit=50" in path


class TestCompilePolicyFlowValidation:
    async def test_requires_exactly_one_selector(self):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            clearpass_compile_policy_flow,
        )

        # Neither
        result = await clearpass_compile_policy_flow(_ctx())
        assert isinstance(result, str)
        assert "exactly one" in result.lower()

        # Both
        result = await clearpass_compile_policy_flow(_ctx(), service_id=1, service_name="X")
        assert isinstance(result, str)
        assert "exactly one" in result.lower()


class TestCompilePolicyFlowFanout:
    @patch("hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.clearpass_get")
    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.get_clearpass_session",
        new_callable=AsyncMock,
    )
    async def test_service_not_found_returns_available_list(self, mock_session, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            clearpass_compile_policy_flow,
        )

        mock_session.return_value = MagicMock()
        # Empty bulk responses except services (so we can verify lookup miss)
        mock_get.return_value = _hal([{"id": 1, "name": "[Existing Service]", "type": "RADIUS"}])
        result = await clearpass_compile_policy_flow(_ctx(), service_name="[Does Not Exist]")
        assert isinstance(result, dict)
        assert result["status"] == "service_not_found"
        assert "[Existing Service]" in result["available_services"]

    @patch("hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.clearpass_get")
    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.get_clearpass_session",
        new_callable=AsyncMock,
    )
    async def test_fans_out_to_seven_endpoints(self, mock_session, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            clearpass_compile_policy_flow,
        )

        mock_session.return_value = MagicMock()
        mock_get.return_value = _hal([])
        await clearpass_compile_policy_flow(_ctx(), service_name="[Any]")

        # 7 bulk fetches regardless of whether the service is found
        paths = [call.args[1].split("?", 1)[0] for call in mock_get.call_args_list]
        assert paths.count("/config/service") == 1
        assert paths.count("/role-mapping") == 1
        assert paths.count("/enforcement-policy") == 1
        assert paths.count("/enforcement-profile") == 1
        assert paths.count("/role") == 1
        assert paths.count("/auth-method") == 1
        assert paths.count("/auth-source") == 1
        assert len(paths) == 7

    @patch("hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.clearpass_get")
    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.get_clearpass_session",
        new_callable=AsyncMock,
    )
    async def test_end_to_end_compiles_a_minimal_service(self, mock_session, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            clearpass_compile_policy_flow,
        )

        mock_session.return_value = MagicMock()

        # Wire endpoint-specific responses by path
        def _side_effect(_client, path):
            base = path.split("?", 1)[0]
            return {
                "/config/service": _hal(
                    [
                        {
                            "id": 1,
                            "name": "S1",
                            "type": "RADIUS",
                            "description": "",
                            "rules_match_type": "MATCHES_ALL",
                            "rules_conditions": [
                                {
                                    "type": "Radius:IETF",
                                    "name": "User-Name",
                                    "operator": "EQUALS",
                                    "value": "x",
                                }
                            ],
                            "auth_methods": [],
                            "auth_sources": [],
                            "role_mapping_policy": "",
                            "enf_policy": "EP1",
                        }
                    ]
                ),
                "/role-mapping": _hal([]),
                "/enforcement-policy": _hal(
                    [
                        {
                            "id": 10,
                            "name": "EP1",
                            "enforcement_type": "RADIUS",
                            "rule_eval_algo": "first-applicable",
                            "default_enforcement_profile": "",
                            "rules": [
                                {
                                    "enforcement_profile_names": ["[Allow Access Profile]"],
                                    "condition": [
                                        {
                                            "type": "Tips",
                                            "name": "Role",
                                            "oper": "EQUALS",
                                            "value": "anything",
                                        }
                                    ],
                                }
                            ],
                        }
                    ]
                ),
                "/enforcement-profile": _hal(
                    [
                        {
                            "id": 100,
                            "name": "[Allow Access Profile]",
                            "type": "RADIUS",
                            "action": "Accept",
                            "description": "",
                        }
                    ]
                ),
                "/role": _hal([]),
                "/auth-method": _hal([]),
                "/auth-source": _hal([]),
            }.get(base, _hal([]))

        mock_get.side_effect = _side_effect

        result = await clearpass_compile_policy_flow(_ctx(), service_name="S1")
        assert isinstance(result, dict)
        assert result["service_name"] == "S1"
        assert result["service_type"] == "RADIUS"
        # nodes + edges should be non-empty
        assert len(result["nodes"]) > 0
        assert len(result["edges"]) > 0
        # ALLOW end node should be present (single enf rule resolves to Allow Access Profile)
        assert any("ALLOW" in n["label"] for n in result["nodes"] if n["type"] == "end")
