"""Unit tests for UXI health probe — _probe_uxi, _ALL_PLATFORMS, _PROBES.

Validates UXI-READ-08: the _probe_uxi() function returns the correct status dicts
for the unavailable, ok, and degraded scenarios; and that 'uxi' is wired into
_ALL_PLATFORMS and _PROBES.
"""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestUXIHealthProbe:
    """Tests for _probe_uxi and its integration into the health aggregator."""

    def test_uxi_in_all_platforms(self):
        """'uxi' must be in _ALL_PLATFORMS for the health aggregator to probe it."""
        from hpe_networking_mcp.platforms.health import _ALL_PLATFORMS

        assert "uxi" in _ALL_PLATFORMS

    def test_uxi_in_probes_dict(self):
        """_PROBES['uxi'] must exist and be callable."""
        from hpe_networking_mcp.platforms.health import _PROBES

        assert "uxi" in _PROBES
        assert callable(_PROBES["uxi"])

    @pytest.mark.asyncio
    async def test_probe_returns_unavailable_when_client_missing(self):
        """When lifespan_context has no uxi_client, probe returns unavailable."""
        from hpe_networking_mcp.platforms.health import _probe_uxi

        class _FakeCtx:
            lifespan_context = {}

        result = await _probe_uxi(_FakeCtx())
        assert result["status"] == "unavailable"
        assert "UXI is not configured" in result["message"]

    @pytest.mark.asyncio
    async def test_probe_returns_ok_when_health_check_succeeds(self):
        """When health_check() succeeds, probe returns ok."""
        from hpe_networking_mcp.platforms.health import _probe_uxi

        class _FakeClientOk:
            async def health_check(self) -> bool:
                return True

        class _FakeCtx:
            lifespan_context = {"uxi_client": _FakeClientOk()}

        result = await _probe_uxi(_FakeCtx())
        assert result["status"] == "ok"
        assert result["message"] == "UXI API reachable"

    @pytest.mark.asyncio
    async def test_probe_returns_degraded_when_health_check_raises(self):
        """When health_check() raises, probe returns degraded with error info."""
        from hpe_networking_mcp.platforms.health import _probe_uxi

        class _FakeClientFail:
            async def health_check(self) -> bool:
                raise RuntimeError("connection refused")

        class _FakeCtx:
            lifespan_context = {"uxi_client": _FakeClientFail()}

        result = await _probe_uxi(_FakeCtx())
        assert result["status"] == "degraded"
        assert result["message"].startswith("UXI probe failed:")
        assert "connection refused" in result["message"]
