"""Unit tests for ``central_get_ap_trend`` interface-type handling.

The ``throughput-trends`` endpoint requires an ``interface-type`` query param
(WIRELESS / WIRED / LTE); the API 400s without it. The tool defaults it to
WIRELESS for the throughput dimension and omits it for cpu/memory/power (where
the endpoint doesn't accept it). Surfaced by live dashboard testing.
"""

from __future__ import annotations

from typing import Any

import pytest

from hpe_networking_mcp.platforms.central.tools import mrt_ap

pytestmark = pytest.mark.unit

_trend = getattr(mrt_ap.central_get_ap_trend, "fn", mrt_ap.central_get_ap_trend)


class _Ctx:
    lifespan_context: dict[str, Any] = {"central_conn": object()}


def _capture(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Patch the module-level ``_get`` to record (path, params) and return {}."""
    captured: dict[str, Any] = {}

    def fake_get(conn: Any, path: str, params: dict | None = None) -> dict:
        captured["path"] = path
        captured["params"] = params or {}
        return {}

    monkeypatch.setattr(mrt_ap, "_get", fake_get)
    return captured


async def test_throughput_defaults_interface_type_wireless(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = _capture(monkeypatch)
    await _trend(ctx=_Ctx(), serial_number="CNT2M590SZ", dimension="throughput")
    assert captured["path"].endswith("/throughput-trends")
    assert captured["params"].get("interface-type") == "WIRELESS"


async def test_throughput_interface_type_override(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = _capture(monkeypatch)
    await _trend(ctx=_Ctx(), serial_number="CNT2M590SZ", dimension="throughput", interface_type="WIRED")
    assert captured["params"].get("interface-type") == "WIRED"


@pytest.mark.parametrize(
    "dimension,suffix",
    [
        ("cpu", "/cpu-utilization-trends"),
        ("memory", "/memory-utilization-trends"),
        ("power", "/power-consumption-trends"),
    ],
)
async def test_non_throughput_dimensions_omit_interface_type(
    monkeypatch: pytest.MonkeyPatch, dimension: str, suffix: str
) -> None:
    captured = _capture(monkeypatch)
    await _trend(ctx=_Ctx(), serial_number="CNT2M590SZ", dimension=dimension)
    assert captured["path"].endswith(suffix)
    assert "interface-type" not in captured["params"]
