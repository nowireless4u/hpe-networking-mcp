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


@pytest.mark.unit
def test_execute_description_mentions_in_sandbox_discovery_path() -> None:
    """v3.0.1.15 (issue #302): execute_description must teach the AI that
    `<platform>_list_tools` is callable from inside execute() in code mode,
    so it has a working discovery path even when the outer discovery tools
    (`search` / `tags` / `get_schema`) aren't surfaced by the client.
    """
    body = _read_execute_description_block()
    assert "<platform>_list_tools" in body or "list_tools" in body, (
        "execute_description must mention the in-sandbox <platform>_list_tools discovery path (issue #302)."
    )


@pytest.mark.unit
def test_discovery_tool_descriptions_carry_platform_keywords() -> None:
    """v3.0.1.15 (issue #302): top-level discovery tool descriptions must
    include the HPE networking platform names so client semantic tool_search
    surfaces them on queries like "list mist sites" / "search central tools".
    Generic descriptions lose the relevance ranking against other MCP
    servers' more keyword-rich tools.
    """
    # Names of the platforms we expect mentioned in each description.
    platforms = ("mist", "central", "aos8", "clearpass", "apstra", "axis", "greenlake")

    for name in ("_SEARCH_DESCRIPTION", "_TAGS_DESCRIPTION", "_GET_SCHEMA_DESCRIPTION"):
        desc: str = getattr(srv, name)
        assert isinstance(desc, str) and desc, f"server.{name} must be a non-empty string"
        # Must reference the HPE networking platforms it dispatches to.
        present = [p for p in platforms if p in desc.lower()]
        assert len(present) >= 5, (
            f"server.{name} must reference the HPE networking platforms it "
            f"dispatches to (found {len(present)} of {len(platforms)}: {present}). "
            f"Without keyword hooks the client semantic tool_search ranks our "
            f"discovery tools below other servers' more descriptive tools "
            f"(issue #302)."
        )
        # Must reference "tool" so clients searching for "list tools" / "tool catalog" surface it.
        assert "tool" in desc.lower(), f"server.{name} must contain the word 'tool'"


PLATFORM_INIT_FILES = (
    "src/hpe_networking_mcp/platforms/aos8/__init__.py",
    "src/hpe_networking_mcp/platforms/apstra/__init__.py",
    "src/hpe_networking_mcp/platforms/axis/__init__.py",
    "src/hpe_networking_mcp/platforms/central/__init__.py",
    "src/hpe_networking_mcp/platforms/clearpass/__init__.py",
    "src/hpe_networking_mcp/platforms/greenlake/__init__.py",
    "src/hpe_networking_mcp/platforms/mist/__init__.py",
)


@pytest.mark.unit
@pytest.mark.parametrize("init_path", PLATFORM_INIT_FILES)
def test_platform_init_registers_meta_tools_unconditionally(init_path: str) -> None:
    """v3.0.1.15 (issue #302): each platform's register_tools must call
    build_meta_tools regardless of config.tool_mode. The historical
    ``if config.tool_mode == "dynamic":`` gate left meta-tools unregistered
    in code mode, which contradicted INSTRUCTIONS.md and made
    `mist_list_tools` etc. uncallable from inside execute().
    """
    repo_root = Path(srv.__file__).parent.parent.parent
    full_path = repo_root / init_path
    assert full_path.exists(), f"{init_path} not found from repo root {repo_root}"

    body = full_path.read_text(encoding="utf-8")
    # Must call build_meta_tools at least once.
    assert "build_meta_tools(" in body, f"{init_path} must call build_meta_tools"
    # Must NOT gate that call on tool_mode == "dynamic" alone (the old pattern).
    # The substring search is conservative — if anyone reintroduces the gate
    # exactly as it was before v3.0.1.15 the test fires.
    assert 'if config.tool_mode == "dynamic":\n        build_meta_tools' not in body, (
        f"{init_path} reintroduced the v3.0.1.14-era dynamic-mode gate on "
        f"build_meta_tools. Meta-tools must register unconditionally so the "
        f"in-sandbox discovery path works in code mode (issue #302)."
    )
