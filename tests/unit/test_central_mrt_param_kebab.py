"""Unit tests pinning kebab-case query params on the Central MRT usage tools.

Central's ``network-monitoring/v1`` gateway rejects camelCase query params with
HTTP 400 ("Query parameter must be in kebab-case: topN") and rejects unknown
params ("Unknown query parameter: end"). Four tools shipped with the wrong param
names and were surfaced by live dashboard testing:

* ``central_get_top_aps_by_usage`` sent ``topN`` (+ an unsupported ``filter``)
* ``central_get_clients_topn_usage`` sent ``topN`` (+ an unsupported ``filter``)
* ``central_get_clients_trend`` sent ``start`` / ``end`` (+ an unsupported ``filter``)
* ``central_get_switches_topn_interface_trends`` sent ``topN``

The row-count control on these endpoints is ``limit`` and the time window is
``start-at`` / ``end-at`` (per the network-monitoring/v1 spec, verified live).
These tests patch each module's ``_get`` to capture the outgoing (path, params).
"""

from __future__ import annotations

from typing import Any

import pytest

from hpe_networking_mcp.platforms.central.tools import mrt_ap, mrt_clients, mrt_switch

pytestmark = pytest.mark.unit


class _Ctx:
    lifespan_context: dict[str, Any] = {"central_conn": object()}


def _capture(monkeypatch: pytest.MonkeyPatch, module: Any) -> dict[str, Any]:
    """Patch the given module's ``_get`` to record (path, params) and return {}."""
    captured: dict[str, Any] = {}

    async def fake_get(conn: Any, path: str, params: dict | None = None) -> dict:
        captured["path"] = path
        captured["params"] = params or {}
        return {}

    monkeypatch.setattr(module, "_get", fake_get)
    return captured


_top_aps = getattr(mrt_ap.central_get_top_aps_by_usage, "fn", mrt_ap.central_get_top_aps_by_usage)
_clients_topn = getattr(mrt_clients.central_get_clients_topn_usage, "fn", mrt_clients.central_get_clients_topn_usage)
_clients_trend = getattr(mrt_clients.central_get_clients_trend, "fn", mrt_clients.central_get_clients_trend)
_switches_topn = getattr(
    mrt_switch.central_get_switches_topn_interface_trends,
    "fn",
    mrt_switch.central_get_switches_topn_interface_trends,
)


async def test_top_aps_by_usage_uses_limit_not_topn(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = _capture(monkeypatch, mrt_ap)
    await _top_aps(ctx=_Ctx(), metric="usage", top_n=7)
    assert captured["path"].endswith("/top-aps-by-usage")
    assert captured["params"] == {"limit": 7}
    assert "topN" not in captured["params"]
    assert "filter" not in captured["params"]


async def test_clients_topn_usage_uses_limit_not_topn(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = _capture(monkeypatch, mrt_clients)
    await _clients_topn(ctx=_Ctx(), top_n=5)
    assert captured["path"].endswith("/clients-topn-usage")
    assert captured["params"] == {"limit": 5}
    assert "topN" not in captured["params"]


async def test_clients_trend_uses_kebab_start_at_end_at(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = _capture(monkeypatch, mrt_clients)
    await _clients_trend(ctx=_Ctx(), start="2026-07-05T00:00:00Z", end="2026-07-06T00:00:00Z")
    assert captured["path"].endswith("/clients-trend")
    assert captured["params"] == {"start-at": "2026-07-05T00:00:00Z", "end-at": "2026-07-06T00:00:00Z"}
    # The camelCase / unknown params that the API 400s on must be gone.
    for bad in ("start", "end", "filter"):
        assert bad not in captured["params"]


async def test_clients_trend_omits_unset_times(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = _capture(monkeypatch, mrt_clients)
    await _clients_trend(ctx=_Ctx())
    assert captured["params"] == {}


async def test_switches_topn_uses_limit_and_keeps_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = _capture(monkeypatch, mrt_switch)
    await _switches_topn(ctx=_Ctx(), top_n=3, filter="siteId eq '1'")
    assert captured["path"].endswith("/switches/topn-interface-trends")
    assert captured["params"]["limit"] == 3
    assert "topN" not in captured["params"]
    # filter IS a supported param on this endpoint — it must be preserved.
    assert captured["params"]["filter"] == "siteId eq '1'"
