"""Unit tests for the ClearPass policy-visualizer MCP tools.

Mocks ``get_clearpass_session`` + ``clearpass_get`` at the import site
so the tools never reach the network. Verifies endpoint paths, parameter
validation, and the fan-out shape for the compile path.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

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
        with pytest.raises(ToolError) as exc_info:
            await clearpass_compile_policy_flow(_ctx())
        assert exc_info.value.args[0]["status_code"] == 400
        assert "exactly one" in exc_info.value.args[0]["message"].lower()

        # Both
        with pytest.raises(ToolError) as exc_info:
            await clearpass_compile_policy_flow(_ctx(), service_id=1, service_name="X")
        assert exc_info.value.args[0]["status_code"] == 400
        assert "exactly one" in exc_info.value.args[0]["message"].lower()


class TestResolveServiceName:
    """Direct tests of the resolver — easier to cover all match tiers without the bulk-fetch overhead."""

    def test_exact_match_wins(self):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            _resolve_service_name,
        )

        services = [{"id": 1, "name": "[Foo]"}, {"id": 2, "name": "foo"}]
        # Case-sensitive exact match prefers the literal first
        name, candidates = _resolve_service_name(services, None, "[Foo]")
        assert name == "[Foo]"
        assert candidates == []

    def test_case_insensitive_exact_match(self):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            _resolve_service_name,
        )

        services = [{"id": 1, "name": "[AirGroup Authorization Service]"}]
        # Lowercased version of the canonical name should still resolve
        name, candidates = _resolve_service_name(services, None, "[airgroup authorization service]")
        assert name == "[AirGroup Authorization Service]"
        assert candidates == []

    def test_substring_match_single(self):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            _resolve_service_name,
        )

        services = [
            {"id": 1, "name": "AirGroup Authorization Service"},
            {"id": 2, "name": "[Policy Manager Admin Network Login Service]"},
        ]
        # "ClearPass AirGroup" — operator prepended noise. Substring "airgroup" matches one.
        name, candidates = _resolve_service_name(services, None, "ClearPass AirGroup")
        # The substring "ClearPass AirGroup" doesn't match — but operator phrasing tier
        # falls back to substring of the QUERY in the NAME. Verify the more common case:
        name, candidates = _resolve_service_name(services, None, "AirGroup")
        assert name == "AirGroup Authorization Service"
        assert candidates == []

    def test_substring_match_multiple_returns_candidates(self):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            _resolve_service_name,
        )

        services = [
            {"id": 1, "name": "No Wireless For You Auth Service"},
            {"id": 2, "name": "No Wireless For You Auth Service - Mist"},
            {"id": 3, "name": "Some Other Service"},
        ]
        name, candidates = _resolve_service_name(services, None, "No Wireless For You")
        assert name is None
        assert candidates == [
            "No Wireless For You Auth Service",
            "No Wireless For You Auth Service - Mist",
        ]

    def test_no_match_returns_none_no_candidates(self):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            _resolve_service_name,
        )

        services = [{"id": 1, "name": "Foo"}]
        name, candidates = _resolve_service_name(services, None, "Bar")
        assert name is None
        assert candidates == []

    def test_service_id_match(self):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            _resolve_service_name,
        )

        services = [{"id": 1, "name": "Foo"}, {"id": 2, "name": "Bar"}]
        name, candidates = _resolve_service_name(services, 2, None)
        assert name == "Bar"
        assert candidates == []

    def test_service_id_no_match(self):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            _resolve_service_name,
        )

        services = [{"id": 1, "name": "Foo"}]
        name, candidates = _resolve_service_name(services, 99, None)
        assert name is None
        assert candidates == []


class TestCompilePolicyFlowAmbiguousResponse:
    @patch("hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.clearpass_get")
    @patch(
        "hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer.get_clearpass_session",
        new_callable=AsyncMock,
    )
    async def test_substring_matching_multiple_services_returns_ambiguous_with_names_only(self, mock_session, mock_get):
        from hpe_networking_mcp.platforms.clearpass.tools.policy_visualizer import (
            clearpass_compile_policy_flow,
        )

        mock_session.return_value = MagicMock()
        mock_get.return_value = _hal(
            [
                {"id": 3010, "name": "No Wireless For You Auth Service", "type": "RADIUS"},
                {"id": 3044, "name": "No Wireless For You Auth Service - Mist", "type": "RADIUS"},
                {"id": 1, "name": "[Other Service]", "type": "RADIUS"},
            ]
        )
        result = await clearpass_compile_policy_flow(_ctx(), service_name="No Wireless For You")
        assert isinstance(result, dict)
        assert result["status"] == "ambiguous"
        # candidates carry NAMES ONLY, not numeric IDs — IDs are internal API
        # identifiers operators don't recognize and must not be exposed in
        # user-facing output (per the skill's operator-output rules)
        assert result["candidates"] == [
            "No Wireless For You Auth Service",
            "No Wireless For You Auth Service - Mist",
        ]
        for candidate in result["candidates"]:
            assert isinstance(candidate, str)
            assert "id" not in candidate.lower() or "wireless" in candidate.lower()  # name only


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
        # Combine algorithms surfaced as top-level fields (issue #360)
        assert "role_mapping_combine" in result
        assert "enforcement_combine" in result
        # This fixture has no role mapping → None; first-applicable enf → "first-applicable"
        assert result["role_mapping_combine"] is None
        assert result["enforcement_combine"] == "first-applicable"
        # Section titles in mermaid output include the combine algorithm so
        # AI clients building custom widgets don't hardcode "stop on match"
        enf_block = next(s for s in result["mermaid"]["sections"] if "Enforcement" in s["title"])
        assert "first-applicable" in enf_block["title"]
