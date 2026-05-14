"""Regression tests for the code-mode `execute_description` literal.

The string is hand-coded in `server.py` and tells the sandboxed `execute()`
LLM how to reach platform tools via `call_tool`. The contract (corrected
in #328): every per-platform tool is dispatched via
`<platform>_invoke_tool` — NOT by bare tool name. The ~1000 spec-driven
Mist tools are registered but not listed in the sandbox's resolvable
catalog, so `call_tool("mist_get_self", ...)` raises `Unknown tool`; only
`mist_invoke_tool` reaches them. The description must steer the LLM to the
`<platform>_invoke_tool` pattern and must name every platform so the LLM
knows the full set.

These tests guard that contract so the drift cannot recur silently.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import hpe_networking_mcp.server as srv

PLATFORM_NAMES = (
    "mist",
    "central",
    "greenlake",
    "clearpass",
    "apstra",
    "axis",
    "aos8",
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
def test_execute_description_names_all_platforms() -> None:
    """Every platform must be named in the description so the in-sandbox LLM
    knows the full set it can dispatch to via `<platform>_invoke_tool`."""
    body = _read_execute_description_block()
    missing = [p for p in PLATFORM_NAMES if p not in body]
    assert not missing, (
        f"execute_description is missing platform name(s): {missing}. "
        f"Update the literal in server.py to name all 7 platforms."
    )


@pytest.mark.unit
def test_execute_description_steers_to_invoke_tool() -> None:
    """#328: the description must steer the LLM to `<platform>_invoke_tool`
    as the dispatch path — NOT bare-name `call_tool("mist_get_self", ...)`,
    which raises `Unknown tool` for the unlisted spec-driven Mist tools."""
    body = _read_execute_description_block()
    assert "_invoke_tool" in body, (
        "execute_description must direct the LLM to `<platform>_invoke_tool` "
        "as the universal per-platform dispatch path (issue #328)."
    )
    # And it must explicitly warn that direct Mist dispatch fails — that is
    # the concrete footgun the operator transcript hit.
    assert "Unknown tool" in body and "mist" in body.lower(), (
        "execute_description must warn that a direct call_tool('mist_...') raises `Unknown tool` (issue #328)."
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


@pytest.mark.unit
def test_discovery_tool_descriptions_gate_on_skills_list() -> None:
    """#338: every catalog-discovery tool description must open with the
    skills-first gate — `skills_list` is a tool-layer prerequisite, not an
    implication the AI can rationalize past (it jumped straight to `search`
    on an "RF check" request because `search`'s own description never said
    to check skills first).
    """
    for name in ("_SEARCH_DESCRIPTION", "_TAGS_DESCRIPTION", "_GET_SCHEMA_DESCRIPTION"):
        desc: str = getattr(srv, name)
        # The gate must lead — within the first ~200 chars, not buried.
        head = desc[:200]
        assert "skills_list" in head, f"server.{name} must open with the skills_list-first gate (#338)"
        assert "FIRST" in head, f"server.{name}'s skills-first gate must be emphatic ('FIRST') (#338)"


@pytest.mark.unit
def test_execute_description_gates_on_skills_list() -> None:
    """#338: execute_description must carry a hard `skills_list`-first
    prerequisite near the top — `execute` is one of the two tools the AI
    reached for instead of checking skills."""
    body = _read_execute_description_block()
    assert "skills_list" in body, "execute_description must reference skills_list as a prerequisite (#338)"
    assert "PREREQUISITE" in body, "execute_description's skills-first gate must be flagged PREREQUISITE (#338)"


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
