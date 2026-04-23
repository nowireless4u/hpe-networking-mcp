"""Unit tests for the cross-platform ``health`` tool (#158)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from hpe_networking_mcp.config import ApstraSecrets, ServerConfig
from hpe_networking_mcp.platforms.health import (
    _normalize_platform_filter,
    _overall_status,
    run_probes,
)


def _config_with(**flags) -> ServerConfig:
    defaults = {}
    defaults.update(flags)
    return ServerConfig(**defaults)


def _apstra_secrets() -> ApstraSecrets:
    return ApstraSecrets(server="apstra.test", username="u", password="p")


@pytest.mark.unit
class TestNormalizePlatformFilter:
    def test_none_returns_all_enabled(self):
        assert _normalize_platform_filter(None, ["mist", "apstra"]) == ["mist", "apstra"]

    def test_single_string(self):
        assert _normalize_platform_filter("apstra", ["mist", "apstra"]) == ["apstra"]

    def test_list_preserves_order(self):
        assert _normalize_platform_filter(["apstra", "mist"], ["mist", "apstra"]) == ["apstra", "mist"]

    def test_case_insensitive(self):
        assert _normalize_platform_filter("APSTRA", ["apstra"]) == ["apstra"]

    def test_unknown_platform_silently_dropped(self):
        # Logs a warning but doesn't crash — caller sees an empty result for the bad name.
        assert _normalize_platform_filter("azure", ["mist", "apstra"]) == []

    def test_mixed_list_drops_unknowns(self):
        assert _normalize_platform_filter(["apstra", "azure", "mist"], ["mist", "apstra"]) == ["apstra", "mist"]


@pytest.mark.unit
class TestOverallStatus:
    def test_empty_is_ok(self):
        assert _overall_status({}) == "ok"

    def test_all_ok(self):
        assert _overall_status({"apstra": {"status": "ok"}, "mist": {"status": "ok"}}) == "ok"

    def test_one_degraded(self):
        assert _overall_status({"apstra": {"status": "ok"}, "mist": {"status": "degraded"}}) == "degraded"

    def test_unavailable_counts_as_degraded(self):
        assert _overall_status({"apstra": {"status": "ok"}, "mist": {"status": "unavailable"}}) == "degraded"


@pytest.mark.unit
class TestRunProbes:
    async def test_apstra_ok_when_client_healthy(self):
        apstra_client = MagicMock()
        apstra_client.server = "apstra.test:443"
        apstra_client.health_check = AsyncMock(return_value=True)

        ctx = MagicMock()
        ctx.lifespan_context = {"apstra_client": apstra_client}

        results = await run_probes(ctx, ["apstra"])
        assert results["apstra"]["status"] == "ok"
        assert results["apstra"]["server"] == "apstra.test:443"

    async def test_apstra_degraded_when_health_check_raises(self):
        apstra_client = MagicMock()
        apstra_client.health_check = AsyncMock(side_effect=RuntimeError("401 bad creds"))

        ctx = MagicMock()
        ctx.lifespan_context = {"apstra_client": apstra_client}

        results = await run_probes(ctx, ["apstra"])
        assert results["apstra"]["status"] == "degraded"
        assert "401" in results["apstra"]["message"]

    async def test_apstra_unavailable_when_not_configured(self):
        ctx = MagicMock()
        ctx.lifespan_context = {"apstra_client": None}

        results = await run_probes(ctx, ["apstra"])
        assert results["apstra"]["status"] == "unavailable"

    async def test_clearpass_ok_when_token_returns(self):
        tm = MagicMock()
        tm.get_token = MagicMock(return_value="fake-token-abc")

        ctx = MagicMock()
        ctx.lifespan_context = {"clearpass_token_manager": tm}

        results = await run_probes(ctx, ["clearpass"])
        assert results["clearpass"]["status"] == "ok"

    async def test_clearpass_degraded_on_refresh_failure(self):
        tm = MagicMock()
        tm.get_token = MagicMock(side_effect=RuntimeError("OAuth2 rejected"))

        ctx = MagicMock()
        ctx.lifespan_context = {"clearpass_token_manager": tm}

        results = await run_probes(ctx, ["clearpass"])
        assert results["clearpass"]["status"] == "degraded"
        assert "OAuth2" in results["clearpass"]["message"]

    async def test_filter_runs_only_requested_platforms(self):
        apstra_client = MagicMock()
        apstra_client.server = "x:443"
        apstra_client.health_check = AsyncMock(return_value=True)

        mist_session = MagicMock()  # would fail the probe if it ran

        ctx = MagicMock()
        ctx.lifespan_context = {
            "apstra_client": apstra_client,
            "mist_session": mist_session,
        }

        results = await run_probes(ctx, ["apstra"])
        assert set(results.keys()) == {"apstra"}

    async def test_unknown_platform_silently_skipped(self):
        ctx = MagicMock()
        ctx.lifespan_context = {}
        results = await run_probes(ctx, ["acme"])
        assert results == {}
