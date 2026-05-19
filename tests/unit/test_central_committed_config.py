"""Unit tests for ``central_get_committed_config``.

The new tool is a parallel sibling of ``central_get_effective_config`` —
same per-resource shape, but limited to what's COMMITTED at the scope
(no parent-scope inheritance rollup). Symmetric naming makes the two
views easy for operators to diff side-by-side.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from treelib import Tree

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    ctx.get_state = AsyncMock(return_value="prompt")
    return ctx


def _make_resources(*resources: tuple[str, str]) -> Tree:
    rtree = Tree()
    rtree.create_node("resources", "resources")
    personas_added: set[str] = set()
    for persona, resource_name in resources:
        if persona not in personas_added:
            rtree.create_node(persona, persona, parent="resources")
            personas_added.add(persona)
        rtree.create_node(resource_name, parent=persona, data={"config": "value"})
    return rtree


def _make_tree() -> Tree:
    """Build Global → EST Sites → HOME with committed resources at each."""
    tree = Tree()
    tree.create_node(
        "global-id",
        "global-id",
        data={
            "device": {"scope_id": "global-id", "type": "GLOBAL", "meta": {"scope_name": "Global"}},
            "resources": _make_resources(("ACCESS_SWITCH", "policies/sys_deny_all")),
        },
    )
    tree.create_node(
        "est-id",
        "est-id",
        parent="global-id",
        data={
            "device": {
                "scope_id": "est-id",
                "type": "SITE_COLLECTION",
                "meta": {"scope_name": "EST Timezone Sites"},
            },
            "resources": _make_resources(
                ("CAMPUS_AP", "policies/apple-tv"),
                ("CAMPUS_AP", "roles/night-night"),
                ("ACCESS_SWITCH", "policies/voip-device"),
            ),
        },
    )
    tree.create_node(
        "home-id",
        "home-id",
        parent="est-id",
        data={
            "device": {"scope_id": "home-id", "type": "SITE", "meta": {"scope_name": "HOME"}},
            "resources": _make_resources(("ACCESS_SWITCH", "layer2-vlan/105")),
        },
    )
    return tree


class TestCentralGetCommittedConfig:
    @patch("hpe_networking_mcp.platforms.central.tools.scope.build_scope_tree")
    async def test_returns_flat_committed_list_with_persona_attribution(self, mock_build):
        from hpe_networking_mcp.platforms.central.tools.scope import central_get_committed_config

        mock_build.return_value = _make_tree()
        result = await central_get_committed_config(_ctx(), scope_id="est-id")

        assert isinstance(result, dict)
        assert result["scope_id"] == "est-id"
        assert result["scope_name"] == "EST Timezone Sites"
        assert result["type"] == "SITE_COLLECTION"
        # scope_path goes Global → EST Timezone Sites (NOT inclusive of HOME — HOME is a descendant)
        assert result["scope_path"][0]["scope_name"] == "Global"
        assert result["scope_path"][-1]["scope_name"] == "EST Timezone Sites"

        committed = result["committed_resources"]
        names = sorted(r["name"] for r in committed)
        # ONLY EST's directly-committed resources — no rollup from Global, no peek-down to HOME
        assert names == ["policies/apple-tv", "policies/voip-device", "roles/night-night"]
        # Persona attribution stays on each entry
        assert {r["persona"] for r in committed} == {"CAMPUS_AP", "ACCESS_SWITCH"}

    @patch("hpe_networking_mcp.platforms.central.tools.scope.build_scope_tree")
    async def test_persona_filter_narrows_results(self, mock_build):
        from hpe_networking_mcp.platforms.central.tools.scope import central_get_committed_config

        mock_build.return_value = _make_tree()
        result = await central_get_committed_config(_ctx(), scope_id="est-id", persona="CAMPUS_AP")

        committed = result["committed_resources"]
        assert all(r["persona"] == "CAMPUS_AP" for r in committed)
        assert {r["name"] for r in committed} == {"policies/apple-tv", "roles/night-night"}

    @patch("hpe_networking_mcp.platforms.central.tools.scope.build_scope_tree")
    async def test_include_details_false_omits_details_field(self, mock_build):
        from hpe_networking_mcp.platforms.central.tools.scope import central_get_committed_config

        mock_build.return_value = _make_tree()
        result = await central_get_committed_config(_ctx(), scope_id="home-id", include_details=False)

        for entry in result["committed_resources"]:
            assert "details" not in entry
            # has_details still reports whether they EXIST in the tree
            assert "has_details" in entry

    @patch("hpe_networking_mcp.platforms.central.tools.scope.build_scope_tree")
    async def test_include_details_true_attaches_resource_data(self, mock_build):
        from hpe_networking_mcp.platforms.central.tools.scope import central_get_committed_config

        mock_build.return_value = _make_tree()
        result = await central_get_committed_config(_ctx(), scope_id="home-id", include_details=True)

        entry = result["committed_resources"][0]
        # _make_resources gives every node data={"config": "value"} so include_details surfaces it
        assert entry["details"] == {"config": "value"}
        assert entry["has_details"] is True

    @patch("hpe_networking_mcp.platforms.central.tools.scope.build_scope_tree")
    async def test_unknown_scope_id_raises_tool_error_404(self, mock_build):
        """Migrated to ToolError pattern in v3.2.0.1. The error-contract
        rule changed: validation / not-found errors now raise
        ``ToolError`` with structured ``status_code`` + ``message`` payload
        so AI clients can programmatically branch on 4xx vs 5xx, and the
        envelope doesn't misleadingly wrap them as ``ok: True``.
        """
        from fastmcp.exceptions import ToolError

        from hpe_networking_mcp.platforms.central.tools.scope import central_get_committed_config

        mock_build.return_value = _make_tree()
        with pytest.raises(ToolError) as exc_info:
            await central_get_committed_config(_ctx(), scope_id="does-not-exist")

        payload = exc_info.value.args[0]
        assert payload["status_code"] == 404
        assert "does-not-exist" in payload["message"]

    @patch("hpe_networking_mcp.platforms.central.tools.scope.build_scope_tree")
    async def test_build_scope_tree_exception_raises_tool_error_502(self, mock_build):
        """Upstream-failure path (Central API unreachable / parse error /
        any other tree-builder crash) raises ``ToolError`` with status
        502 — distinct from validation errors (400/404) so AI clients
        can decide whether to retry, escalate, or surface differently.
        ``SandboxErrorCatchMiddleware`` rescues the raise in code mode.
        """
        from fastmcp.exceptions import ToolError

        from hpe_networking_mcp.platforms.central.tools.scope import central_get_committed_config

        mock_build.side_effect = RuntimeError("Central API unreachable")
        with pytest.raises(ToolError) as exc_info:
            await central_get_committed_config(_ctx(), scope_id="anything")

        payload = exc_info.value.args[0]
        assert payload["status_code"] == 502
        assert "Error building scope tree" in payload["message"]
        assert "Central API unreachable" in payload["message"]

    @patch("hpe_networking_mcp.platforms.central.tools.scope.build_scope_tree")
    async def test_scope_with_no_committed_resources_returns_empty_list(self, mock_build):
        """An intermediate scope can exist as an organizational container
        without anything directly committed. Returns an empty list rather
        than erroring — operators reading this skill will see "0 resources
        committed at this scope" and know to look up the parent chain."""
        from hpe_networking_mcp.platforms.central.tools.scope import central_get_committed_config

        tree = Tree()
        tree.create_node(
            "container-id",
            "container-id",
            data={
                "device": {
                    "scope_id": "container-id",
                    "type": "SITE_COLLECTION",
                    "meta": {"scope_name": "Container"},
                },
                "resources": None,
            },
        )
        mock_build.return_value = tree
        result = await central_get_committed_config(_ctx(), scope_id="container-id")

        assert result["committed_resources"] == []
