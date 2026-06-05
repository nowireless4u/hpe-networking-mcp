"""Unit tests for Central gateway cluster tools.

Covers the read + manage tools for both the GCIS intent profiles
(/gw-cluster-intent-config) and the realized cluster profiles
(/gateway-clusters). Pins the API path, query-param shape (object-type +
scope-id + device-function on writes), and method-per-action contract.

These tools were regenerated from the vendor OAS as thin delegators to
the shared ``_get_resource`` / ``_manage_resource`` helpers (which live
in ``security_policy.py``); the patch target is therefore that shared
module, not the per-tool module.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

# Shared helpers issue the actual HTTP call; patch retry there.
_HELPER_RETRY = "hpe_networking_mcp.platforms.central.tools.security_policy.retry_central_command"


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    ctx.get_state = AsyncMock(return_value="prompt")
    return ctx


def _ok(msg: object | None = None) -> dict:
    return {"code": 200, "msg": msg if msg is not None else {"ok": True}}


# ---------------------------------------------------------------------------
# central_get_gw_cluster_intent_config
# ---------------------------------------------------------------------------


class TestGetGwClusterIntentProfiles:
    @patch(_HELPER_RETRY)
    async def test_list_all(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clustering_orchestration import (
            central_get_gw_cluster_intent_config,
        )

        mock_retry.return_value = _ok({"profile": [{"name": "site-default"}]})
        await central_get_gw_cluster_intent_config(_ctx())

        kwargs = mock_retry.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == "network-config/v1alpha1/gw-cluster-intent-config"

    @patch(_HELPER_RETRY)
    async def test_single_profile_by_name(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clustering_orchestration import (
            central_get_gw_cluster_intent_config,
        )

        mock_retry.return_value = _ok({"name": "site-default"})
        await central_get_gw_cluster_intent_config(_ctx(), name="site-default")

        assert (
            mock_retry.call_args.kwargs["api_path"] == "network-config/v1alpha1/gw-cluster-intent-config/site-default"
        )


# ---------------------------------------------------------------------------
# central_manage_gw_cluster_intent_config
# ---------------------------------------------------------------------------


class TestManageGwClusterIntentProfile:
    @patch(_HELPER_RETRY)
    async def test_create_uses_post(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clustering_orchestration import (
            central_manage_gw_cluster_intent_config,
        )

        mock_retry.return_value = _ok()
        result = await central_manage_gw_cluster_intent_config(
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

    @patch(_HELPER_RETRY)
    async def test_update_uses_patch(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clustering_orchestration import (
            central_manage_gw_cluster_intent_config,
        )

        mock_retry.return_value = _ok()
        await central_manage_gw_cluster_intent_config(
            _ctx(),
            name="site-default",
            action_type="update",
            payload={"heartbeat-threshold": 1000},
            scope_id=None,
            device_function=None,
            confirmed=True,
        )

        assert mock_retry.call_args.kwargs["api_method"] == "PATCH"

    @patch(_HELPER_RETRY)
    async def test_delete_uses_delete_no_payload(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clustering_orchestration import (
            central_manage_gw_cluster_intent_config,
        )

        mock_retry.return_value = _ok()
        await central_manage_gw_cluster_intent_config(
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

    @patch(_HELPER_RETRY)
    async def test_scope_id_with_device_function_emits_local_params(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.gateway_clustering_orchestration import (
            central_manage_gw_cluster_intent_config,
        )

        mock_retry.return_value = _ok()
        await central_manage_gw_cluster_intent_config(
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

        from hpe_networking_mcp.platforms.central.tools.gateway_clustering_orchestration import (
            central_manage_gw_cluster_intent_config,
        )

        with pytest.raises(ToolError) as exc_info:
            await central_manage_gw_cluster_intent_config(
                _ctx(),
                name="x",
                action_type="bogus",
                payload={},
                scope_id=None,
                device_function=None,
                confirmed=True,
            )
        # v3.2.1.10: validation errors carry the structured {status_code, message} payload.
        assert exc_info.value.args[0]["status_code"] == 400
        assert "Invalid action_type" in exc_info.value.args[0]["message"]


# ---------------------------------------------------------------------------
# central_get_gateway_clusters
# ---------------------------------------------------------------------------


class TestGetGatewayClusters:
    @patch(_HELPER_RETRY)
    async def test_list_all(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.high_availability import (
            central_get_gateway_clusters,
        )

        mock_retry.return_value = _ok({"profile": []})
        await central_get_gateway_clusters(_ctx())

        kwargs = mock_retry.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == "network-config/v1alpha1/gateway-clusters"

    @patch(_HELPER_RETRY)
    async def test_single_cluster_by_name(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.high_availability import (
            central_get_gateway_clusters,
        )

        mock_retry.return_value = _ok()
        await central_get_gateway_clusters(_ctx(), name="DMZ-MGW-Cluster")

        assert mock_retry.call_args.kwargs["api_path"] == "network-config/v1alpha1/gateway-clusters/DMZ-MGW-Cluster"


# ---------------------------------------------------------------------------
# central_manage_gateway_clusters
# ---------------------------------------------------------------------------


class TestManageGatewayCluster:
    @patch(_HELPER_RETRY)
    async def test_create_manual_cluster(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.high_availability import (
            central_manage_gateway_clusters,
        )

        mock_retry.return_value = _ok()
        result = await central_manage_gateway_clusters(
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

    @patch(_HELPER_RETRY)
    async def test_update_uses_patch(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.high_availability import (
            central_manage_gateway_clusters,
        )

        mock_retry.return_value = _ok()
        await central_manage_gateway_clusters(
            _ctx(),
            name="DMZ-MGW-Cluster",
            action_type="update",
            payload={"heartbeat-threshold": 2000},
            scope_id=None,
            device_function=None,
            confirmed=True,
        )

        assert mock_retry.call_args.kwargs["api_method"] == "PATCH"

    @patch(_HELPER_RETRY)
    async def test_delete_uses_delete_no_payload(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.high_availability import (
            central_manage_gateway_clusters,
        )

        mock_retry.return_value = _ok()
        await central_manage_gateway_clusters(
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

    @patch(_HELPER_RETRY)
    async def test_error_response_returns_error_status(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.high_availability import (
            central_manage_gateway_clusters,
        )

        mock_retry.return_value = {"code": 400, "msg": "Cluster name 'auto_x' is reserved"}
        result = await central_manage_gateway_clusters(
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
