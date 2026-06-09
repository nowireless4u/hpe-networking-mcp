"""Unit tests for ``central_get_applications`` input validation (issue #458).

The Central applications endpoint expects epoch **milliseconds** and returns an
opaque ``HTTP 400 BAD_REQUEST`` for ISO-8601 strings, plain dates, or a reversed
window. The tool now validates up front and raises a clear ``ToolError`` (400)
before calling the API, and accepts epoch **seconds** as a convenience.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms.central.tools.applications import (
    _to_epoch_ms,
    central_get_applications,
)

pytestmark = pytest.mark.unit

# The registry decorator returns the bare function when no server is active; fall
# back to ``.fn`` in case a prior test created a server and wrapped it.
_apps = getattr(central_get_applications, "fn", central_get_applications)


class _Ctx:
    """Minimal context — the validation paths raise before touching it."""

    lifespan_context: dict[str, Any] = {}


# --------------------------------------------------------------------------- #
# _to_epoch_ms helper
# --------------------------------------------------------------------------- #


def test_epoch_ms_passthrough() -> None:
    assert _to_epoch_ms("start_query_time", "1780876800000") == 1780876800000


def test_epoch_seconds_converted_to_ms() -> None:
    """10-digit epoch seconds are normalized to ms (the classic seconds-vs-ms mixup)."""
    assert _to_epoch_ms("start_query_time", "1780876800") == 1780876800000


@pytest.mark.parametrize("bad", ["2026-06-08T00:00:00Z", "2026-06-08", "yesterday", "", "12ab34"])
def test_non_numeric_timestamp_rejected(bad: str) -> None:
    with pytest.raises(ToolError) as exc:
        _to_epoch_ms("start_query_time", bad)
    payload = exc.value.args[0]
    assert payload["status_code"] == 400
    assert "epoch" in payload["message"].lower()


# --------------------------------------------------------------------------- #
# Tool-level validation (raises before the API is called)
# --------------------------------------------------------------------------- #


async def test_empty_site_id_rejected() -> None:
    with pytest.raises(ToolError) as exc:
        await _apps(ctx=_Ctx(), site_id="  ", start_query_time="1780876800000", end_query_time="1780963200000")
    assert exc.value.args[0]["status_code"] == 400
    assert "site_id" in exc.value.args[0]["message"]


async def test_iso_8601_window_rejected_with_clear_error() -> None:
    """The exact failure the dashboard run hit: an ISO-8601 window → clear 400, not an
    opaque upstream BAD_REQUEST."""
    with pytest.raises(ToolError) as exc:
        await _apps(
            ctx=_Ctx(),
            site_id="64061593875",
            start_query_time="2026-06-08T00:00:00Z",
            end_query_time="2026-06-09T00:00:00Z",
        )
    assert exc.value.args[0]["status_code"] == 400
    assert "epoch" in exc.value.args[0]["message"].lower()


async def test_reversed_window_rejected() -> None:
    with pytest.raises(ToolError) as exc:
        await _apps(ctx=_Ctx(), site_id="64061593875", start_query_time="1780963200000", end_query_time="1780876800000")
    assert exc.value.args[0]["status_code"] == 400
    assert "before" in exc.value.args[0]["message"]
