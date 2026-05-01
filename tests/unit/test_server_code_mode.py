"""Regression tests for the code-mode `execute_description` literal.

The string is hand-coded in `server.py` and lists which platform prefixes
the sandboxed `execute()` LLM may dispatch via `call_tool`. When a new
platform is added but this literal is not updated, the in-sandbox LLM
produces `Unknown tool` errors despite the tool being registered.

These tests guard the contract so the drift cannot recur silently.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import hpe_networking_mcp.server as srv

PLATFORM_PREFIXES = (
    "mist_",
    "central_",
    "greenlake_",
    "clearpass_",
    "apstra_",
    "axis_",
    "aos8_",
)


def _read_execute_description_block() -> str:
    """Return the source text of the `execute_description` assignment.

    Returns:
        The string literal body (everything between `execute_description = (` and the
        matching closing `)`), or raises AssertionError if the block is not found.
    """
    src = Path(srv.__file__).read_text(encoding="utf-8")
    match = re.search(r"execute_description\s*=\s*\((.*?)\n\s*\)", src, re.DOTALL)
    assert match, "execute_description assignment block not found in server.py"
    return match.group(1)


@pytest.mark.unit
def test_execute_description_lists_all_platform_prefixes() -> None:
    """Every registered platform prefix must appear as a backticked token."""
    body = _read_execute_description_block()
    missing = [p for p in PLATFORM_PREFIXES if f"`{p}`" not in body]
    assert not missing, (
        f"execute_description is missing platform prefix(es): {missing}. "
        f"Update the literal in server.py to include all 7 platforms."
    )


@pytest.mark.unit
def test_execute_description_lists_aos8_prefix() -> None:
    """Specific guard for the AOS8 prefix (Phase 9 fix)."""
    body = _read_execute_description_block()
    assert "`aos8_`" in body, (
        "execute_description must include `aos8_` so the code-mode sandbox "
        "knows AOS8 tools are dispatchable via call_tool()."
    )
