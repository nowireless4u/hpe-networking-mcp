"""Tests for ClockEnabledMontySandboxProvider.

The stock fastmcp ``MontySandboxProvider`` never passes an ``os=`` handler, so
the sandbox clock is blocked. Our subclass passes ``os=OSAccess()`` to enable
``datetime.now()`` / ``date.today()`` while keeping the filesystem and environ
sandboxed. These run the real provider end-to-end (no mocking) so they pin the
actual monty behavior, not our assumptions about it.
"""

from __future__ import annotations

import pytest

pydantic_monty = pytest.importorskip("pydantic_monty")

from hpe_networking_mcp.code_sandbox import ClockEnabledMontySandboxProvider  # noqa: E402

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


def _provider() -> ClockEnabledMontySandboxProvider:
    # Default baseline limits (30s / 100MB) are fine for these trivial snippets.
    return ClockEnabledMontySandboxProvider()


async def test_datetime_now_works() -> None:
    out = await _provider().run("import datetime\nreturn str(datetime.datetime.now())")
    assert out  # an ISO-ish datetime string from the real clock
    assert "-" in out and ":" in out


async def test_datetime_now_utc_works() -> None:
    out = await _provider().run("import datetime\nreturn str(datetime.datetime.now(datetime.timezone.utc))")
    assert "+00:00" in out


async def test_date_today_works() -> None:
    out = await _provider().run("import datetime\nreturn str(datetime.date.today())")
    assert out.count("-") == 2  # YYYY-MM-DD


async def test_utcnow_still_fails() -> None:
    """monty implements only `datetime.now`, never `utcnow` — enabling the
    clock does not change that. (The middleware turns this into a hint.)"""
    with pytest.raises(pydantic_monty.MontyError) as e:
        await _provider().run("import datetime\nreturn datetime.datetime.utcnow()")
    assert "utcnow" in str(e.value)


async def test_environ_not_leaked() -> None:
    """OSAccess exposes an empty environ — host env vars must not leak."""
    out = await _provider().run("import os\nreturn os.environ.get('PATH')")
    assert out is None


async def test_filesystem_not_exposed() -> None:
    """`open` is not even bound in the sandbox — no host file access."""
    with pytest.raises(pydantic_monty.MontyError):
        await _provider().run("return open('/etc/hostname').read()")
