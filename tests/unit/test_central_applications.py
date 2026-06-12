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
    _normalize_sort,
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


def test_iso_8601_converted_to_epoch_ms() -> None:
    """ISO-8601 is the natural form for an LLM that can't read the sandbox clock — accept
    it and convert server-side (2026-06-08T23:00:00Z = 1780959600000 ms)."""
    assert _to_epoch_ms("start_query_time", "2026-06-08T23:00:00Z") == 1780959600000
    # Naive (no offset) is assumed UTC.
    assert _to_epoch_ms("start_query_time", "2026-06-08T23:00:00") == 1780959600000


def test_plain_date_converted_to_epoch_ms() -> None:
    """A bare date is a valid ISO-8601 window boundary (midnight UTC)."""
    assert _to_epoch_ms("start_query_time", "2026-06-08") == 1780876800000


@pytest.mark.parametrize(
    "bad",
    [
        "yesterday",  # word
        "",  # empty
        "12ab34",  # mixed
        "178087680000",  # 12-digit typo (dropped a digit) — not a valid epoch or ISO
        "17808768000000",  # 14-digit typo (extra digit)
        "2026-13-40",  # ISO-shaped but invalid date
    ],
)
def test_unparseable_timestamp_rejected(bad: str) -> None:
    with pytest.raises(ToolError) as exc:
        _to_epoch_ms("start_query_time", bad)
    payload = exc.value.args[0]
    assert payload["status_code"] == 400
    assert "epoch" in payload["message"].lower() or "iso" in payload["message"].lower()


# --------------------------------------------------------------------------- #
# _normalize_sort helper
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("-usage", "usage desc"),  # Mongo/Django shorthand the model used → OData
        ("+usage", "usage asc"),
        ("-bytes", "bytes desc"),
        ("usage desc", "usage desc"),  # already OData → unchanged
        ("usage asc", "usage asc"),
        ("usage desc, name asc", "usage desc, name asc"),  # multi-field → unchanged
        ("usage", "usage"),  # bare field → left for Central to interpret
        ("-", "-"),  # bare sign, no field → passed through (no " desc")
        ("+", "+"),
    ],
)
def test_normalize_sort(raw: str, expected: str) -> None:
    assert _normalize_sort(raw) == expected


# --------------------------------------------------------------------------- #
# Tool-level validation (raises before the API is called)
# --------------------------------------------------------------------------- #


async def test_empty_site_id_rejected() -> None:
    with pytest.raises(ToolError) as exc:
        await _apps(ctx=_Ctx(), site_id="  ", start_query_time="1780876800000", end_query_time="1780963200000")
    assert exc.value.args[0]["status_code"] == 400
    assert "site_id" in exc.value.args[0]["message"]


async def test_unparseable_window_rejected_with_clear_error() -> None:
    """A genuinely unparseable timestamp still yields a clear 400 before the API call."""
    with pytest.raises(ToolError) as exc:
        await _apps(
            ctx=_Ctx(),
            site_id="64061593875",
            start_query_time="last tuesday",
            end_query_time="2026-06-09T00:00:00Z",
        )
    assert exc.value.args[0]["status_code"] == 400


async def test_reversed_window_rejected() -> None:
    """Reversed window is caught after normalization (works across mixed input forms:
    an ISO start that resolves after an epoch-ms end)."""
    with pytest.raises(ToolError) as exc:
        await _apps(
            ctx=_Ctx(),
            site_id="64061593875",
            start_query_time="2026-06-09T00:00:00Z",
            end_query_time="1780876800000",  # 2026-06-08 — earlier than the ISO start
        )
    assert exc.value.args[0]["status_code"] == 400
    assert "before" in exc.value.args[0]["message"]
