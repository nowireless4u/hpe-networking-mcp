"""Future-proofing guard for the Mist registration bug (#524).

Every platform's ``register_tools`` wires its FastMCP holder via
``_registry.mcp = mcp``. The ``@tool`` decorator records a ``ToolSpec`` AND —
only if ``_registry.mcp`` is already set — calls ``mcp.tool()`` to register the
tool with FastMCP. If a tool module is imported while ``_registry.mcp`` is still
``None``, the tool lands in the platform registry but is NEVER registered with
FastMCP: invisible to ``search`` / ``tags`` / ``get_tool_schema`` and uncallable
by name. That's exactly what happened to all ~1037 Mist tools — Mist imported an
eager-loading ``tools`` package before setting ``_registry.mcp`` (#524).

These tests assert the invariant by source inspection (caching-safe, unlike a
runtime check that import-caching could mask) so no future platform reintroduces
the trap.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_PLATFORMS_DIR = Path("src/hpe_networking_mcp/platforms")


def _discover_platforms() -> list[str]:
    """Every platform package, discovered from the filesystem.

    A new platform must be guarded automatically — hard-coding the list would
    re-open the exact "future platform forgets the rule" gap this test closes
    (Casey's review on #540). A platform package is any subdirectory whose
    ``__init__.py`` defines ``register_tools`` (the wiring point); that excludes
    shared infra like ``_common`` and includes ``_template``.
    """
    found: list[str] = []
    for child in sorted(_PLATFORMS_DIR.iterdir()):
        if not child.is_dir() or child.name == "__pycache__":
            continue
        init = child / "__init__.py"
        if init.exists() and "def register_tools" in init.read_text(encoding="utf-8"):
            found.append(child.name)
    return found


_PLATFORMS = _discover_platforms()

pytestmark = pytest.mark.unit


def test_platform_discovery_is_sane() -> None:
    """Guard the guard: discovery must find the known platforms, so the
    parametrized checks below can't silently degrade to a vacuous pass."""
    assert {"mist", "central", "edgeconnect", "_template"}.issubset(_PLATFORMS), _PLATFORMS
    assert len(_PLATFORMS) >= 9, f"expected all platforms to be discovered, got {_PLATFORMS}"


@pytest.mark.parametrize("platform", _PLATFORMS)
def test_mcp_wired_before_static_tools_import(platform: str) -> None:
    """A static ``from ...<platform> import tools`` import eagerly imports the
    tools package — so it MUST appear after ``_registry.mcp = mcp``."""
    init = (_PLATFORMS_DIR / platform / "__init__.py").read_text(encoding="utf-8")
    if "_registry.mcp = mcp" not in init:
        pytest.skip(f"{platform}: no _registry.mcp wiring")
    mcp_pos = init.index("_registry.mcp = mcp")
    m = re.search(rf"from hpe_networking_mcp\.platforms\.{re.escape(platform)} import tools\b", init)
    if m is None:
        return  # no static tools-package import → registration happens via importlib after wiring
    assert m.start() > mcp_pos, (
        f"{platform}: register_tools imports the tools package BEFORE setting "
        f"`_registry.mcp = mcp` — the @tool decorators will skip mcp.tool() and the "
        f"tools won't register with FastMCP (#524). Move `_registry.mcp = mcp` up."
    )


@pytest.mark.parametrize("platform", _PLATFORMS)
def test_eager_tools_init_requires_mcp_first(platform: str) -> None:
    """If a platform's ``tools/__init__`` eager-imports submodules, the decorators
    fire the moment the package is imported — so ``register_tools`` MUST wire
    ``_registry.mcp`` before any tools import. (Amplifies the check above for the
    exact shape that bit Mist.)"""
    tools_init = _PLATFORMS_DIR / platform / "tools" / "__init__.py"
    if not tools_init.exists():
        pytest.skip(f"{platform}: no tools/__init__.py")
    text = tools_init.read_text(encoding="utf-8")
    eager = re.search(r"^\s*from \. import\b|^\s*from \.\w+ import\b", text, re.MULTILINE)
    if eager is None:
        return  # lazy tools/__init__ → safe regardless of register_tools ordering
    init = (_PLATFORMS_DIR / platform / "__init__.py").read_text(encoding="utf-8")
    assert "_registry.mcp = mcp" in init, f"{platform}: eager tools/__init__ but no _registry.mcp wiring"
    mcp_pos = init.index("_registry.mcp = mcp")
    imp = re.search(r"import tools as tools_pkg\b|import tools\b", init)
    assert imp is not None and imp.start() > mcp_pos, (
        f"{platform}: tools/__init__ eager-imports submodules, so `_registry.mcp = mcp` "
        f"MUST be set before importing the tools package (#524)."
    )
