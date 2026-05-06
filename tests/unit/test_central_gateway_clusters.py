"""Unit tests for Central gateway cluster tools.

Covers the read + manage tools for both the GCIS intent profiles
(/gw-cluster-intent-config) and the realized cluster profiles
(/gateway-clusters). Pins the API path, query-param shape (object-type +
scope-id + device-function), and method-per-action contract.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    ctx.get_state = AsyncMock(return_value="prompt")
    return ctx


def _ok(msg: object | None = None) -> dict:
    return {"code": 200, "msg": msg if msg is not None else {"ok": True}}


# ---------------------------------------------------------------------------
# central_get_gateway_cluster_intent_profiles
# ---------------------------------------------------------------------------


class TestGetGwClusterIntentProfiles:
    @patch("hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent.retry_central_command")
    async def test_list_all(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent import (
            central_get_gateway_cluster_intent_profiles,
        )

        mock_retry.return_value = _ok({"profile": [{"name": "site-default"}]})
        await central_get_gateway_cluster_intent_profiles(_ctx())

        kwargs = mock_retry.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == "network-config/v1alpha1/gw-cluster-intent-config"
        # No name → no scope_id → no api_params
        assert kwargs.get("api_params") is None

    @patch("hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent.retry_central_command")
    async def test_single_profile_by_name(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent import (
            central_get_gateway_cluster_intent_profiles,
        )

        mock_retry.return_value = _ok({"name": "site-default"})
        await central_get_gateway_cluster_intent_profiles(_ctx(), name="site-default")

        assert (
            mock_retry.call_args.kwargs["api_path"] == "network-config/v1alpha1/gw-cluster-intent-config/site-default"
        )

    @patch("hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent.retry_central_command")
    async def test_with_scope_id(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent import (
            central_get_gateway_cluster_intent_profiles,
        )

        mock_retry.return_value = _ok([])
        await central_get_gateway_cluster_intent_profiles(_ctx(), scope_id="123-abc")

        assert mock_retry.call_args.kwargs["api_params"] == {"scope-id": "123-abc"}


# ---------------------------------------------------------------------------
# central_manage_gateway_cluster_intent_profile
# ---------------------------------------------------------------------------


class TestManageGwClusterIntentProfile:
    @patch("hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent.retry_central_command")
    async def test_create_uses_post(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent import (
            central_manage_gateway_cluster_intent_profile,
        )

        mock_retry.return_value = _ok()
        result = await central_manage_gateway_cluster_intent_profile(
            _ctx(),
            name="site-default",
            action_type="create",
            payload={"cluster-mode": "CM_SITE", "device-type": "MOBILITY_GW"},
            scope_id=None,
            device_function=None,
            confirmed=True,
        )

        assert result["status"] == "success"
        kwargs = mock_retry.call_args.kwargs
        assert kwargs["api_method"] == "POST"
        assert kwargs["api_path"] == "network-config/v1alpha1/gw-cluster-intent-config/site-default"
        assert kwargs["api_data"] == {"cluster-mode": "CM_SITE", "device-type": "MOBILITY_GW"}

    @patch("hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent.retry_central_command")
    async def test_update_uses_patch(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent import (
            central_manage_gateway_cluster_intent_profile,
        )

        mock_retry.return_value = _ok()
        await central_manage_gateway_cluster_intent_profile(
            _ctx(),
            name="site-default",
            action_type="update",
            payload={"heartbeat-threshold": 1000},
            scope_id=None,
            device_function=None,
            confirmed=True,
        )

        assert mock_retry.call_args.kwargs["api_method"] == "PATCH"

    @patch("hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent.retry_central_command")
    async def test_delete_uses_delete_no_payload(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent import (
            central_manage_gateway_cluster_intent_profile,
        )

        mock_retry.return_value = _ok()
        await central_manage_gateway_cluster_intent_profile(
            _ctx(),
            name="site-default",
            action_type="delete",
            payload={},
            scope_id=None,
            device_function=None,
            confirmed=True,
        )

        kwargs = mock_retry.call_args.kwargs
        assert kwargs["api_method"] == "DELETE"
        assert kwargs.get("api_data") is None

    @patch("hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent.retry_central_command")
    async def test_scope_id_with_device_function_emits_local_params(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent import (
            central_manage_gateway_cluster_intent_profile,
        )

        mock_retry.return_value = _ok()
        await central_manage_gateway_cluster_intent_profile(
            _ctx(),
            name="campus-east",
            action_type="create",
            payload={"cluster-mode": "CM_SITE"},
            scope_id="site-789",
            device_function="MOBILITY_GW",
            confirmed=True,
        )

        assert mock_retry.call_args.kwargs["api_params"] == {
            "object-type": "LOCAL",
            "scope-id": "site-789",
            "device-function": "MOBILITY_GW",
        }

    async def test_invalid_action_type_raises(self):
        from fastmcp.exceptions import ToolError

        from hpe_networking_mcp.platforms.central.tools.gateway_cluster_intent import (
            central_manage_gateway_cluster_intent_profile,
        )

        with pytest.raises(ToolError, match="Invalid action_type"):
            await central_manage_gateway_cluster_intent_profile(
                _ctx(),
                name="x",
                action_type="bogus",
                payload={},
                scope_id=None,
                device_function=None,
                confirmed=True,
            )


# ---------------------------------------------------------------------------
# central_get_gateway_clusters
# ---------------------------------------------------------------------------


class TestGetGatewayClusters:
    @patch("hpe_networking_mcp.platforms.central.tools.gateway_clusters.retry_central_command")
    async def test_list_all(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clusters import (
            central_get_gateway_clusters,
        )

        mock_retry.return_value = _ok({"profile": []})
        await central_get_gateway_clusters(_ctx())

        kwargs = mock_retry.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == "network-config/v1alpha1/gateway-clusters"

    @patch("hpe_networking_mcp.platforms.central.tools.gateway_clusters.retry_central_command")
    async def test_single_cluster_by_name(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clusters import (
            central_get_gateway_clusters,
        )

        mock_retry.return_value = _ok()
        await central_get_gateway_clusters(_ctx(), name="DMZ-MGW-Cluster")

        assert mock_retry.call_args.kwargs["api_path"] == "network-config/v1alpha1/gateway-clusters/DMZ-MGW-Cluster"


# ---------------------------------------------------------------------------
# central_manage_gateway_cluster
# ---------------------------------------------------------------------------


class TestManageGatewayCluster:
    @patch("hpe_networking_mcp.platforms.central.tools.gateway_clusters.retry_central_command")
    async def test_create_manual_cluster(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clusters import (
            central_manage_gateway_cluster,
        )

        mock_retry.return_value = _ok()
        result = await central_manage_gateway_cluster(
            _ctx(),
            name="DMZ-MGW-Cluster",
            action_type="create",
            payload={
                "auto-cluster": False,
                "ipv4-gateways": [{"mac": "aa:bb:cc:dd:ee:01"}, {"mac": "aa:bb:cc:dd:ee:02"}],
                "heartbeat-threshold": 1000,
            },
            scope_id=None,
            device_function=None,
            confirmed=True,
        )

        assert result["status"] == "success"
        kwargs = mock_retry.call_args.kwargs
        assert kwargs["api_method"] == "POST"
        assert kwargs["api_path"] == "network-config/v1alpha1/gateway-clusters/DMZ-MGW-Cluster"
        assert kwargs["api_data"]["auto-cluster"] is False
        assert len(kwargs["api_data"]["ipv4-gateways"]) == 2

    @patch("hpe_networking_mcp.platforms.central.tools.gateway_clusters.retry_central_command")
    async def test_update_uses_patch(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clusters import (
            central_manage_gateway_cluster,
        )

        mock_retry.return_value = _ok()
        await central_manage_gateway_cluster(
            _ctx(),
            name="DMZ-MGW-Cluster",
            action_type="update",
            payload={"heartbeat-threshold": 2000},
            scope_id=None,
            device_function=None,
            confirmed=True,
        )

        assert mock_retry.call_args.kwargs["api_method"] == "PATCH"

    @patch("hpe_networking_mcp.platforms.central.tools.gateway_clusters.retry_central_command")
    async def test_delete_uses_delete_no_payload(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clusters import (
            central_manage_gateway_cluster,
        )

        mock_retry.return_value = _ok()
        await central_manage_gateway_cluster(
            _ctx(),
            name="DMZ-MGW-Cluster",
            action_type="delete",
            payload={},
            scope_id=None,
            device_function=None,
            confirmed=True,
        )

        kwargs = mock_retry.call_args.kwargs
        assert kwargs["api_method"] == "DELETE"
        assert kwargs.get("api_data") is None

    @patch("hpe_networking_mcp.platforms.central.tools.gateway_clusters.retry_central_command")
    async def test_error_response_returns_error_status(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clusters import (
            central_manage_gateway_cluster,
        )

        mock_retry.return_value = {"code": 400, "msg": "Cluster name 'auto_x' is reserved"}
        result = await central_manage_gateway_cluster(
            _ctx(),
            name="auto_x",
            action_type="create",
            payload={},
            scope_id=None,
            device_function=None,
            confirmed=True,
        )

        assert result["status"] == "error"
        assert result["code"] == 400
        assert "reserved" in result["message"]
