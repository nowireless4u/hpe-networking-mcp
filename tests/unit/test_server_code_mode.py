"""Regression tests for the code-mode `execute_description` literal.

The string is hand-coded in `server.py` and tells the sandboxed `execute()`
LLM how to reach platform tools via `call_tool`. The contract (current, as of
#524): every per-platform tool is callable BOTH directly by bare name AND via
`<platform>_invoke_tool` — both resolve for every platform, Mist included. The
old #328 carve-out ("Mist reachable ONLY via invoke_tool; a direct call raises
`Unknown tool`") was a symptom of an import-order bug that left the ~1000 Mist
tools registry-only; with that fixed (#524) Mist registers with FastMCP exactly
like Central, so direct calls resolve. The description must name every platform
and present `<platform>_invoke_tool` as a valid dispatch path.

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
def test_execute_description_warns_unavailable_stdlib_modules() -> None:
    """The Monty sandbox is a Python subset — some stdlib modules aren't
    importable (e.g. `collections`). Operator transcripts repeatedly hit
    `ModuleNotFoundError: No module named 'collections'` in code mode, so the
    description must warn and point at builtins instead."""
    body = _read_execute_description_block()
    assert "collections" in body and "ModuleNotFoundError" in body, (
        "execute_description must warn that not every stdlib module exists in "
        "the sandbox (e.g. `import collections` raises ModuleNotFoundError) and "
        "steer the AI to builtins."
    )


@pytest.mark.unit
def test_execute_description_presents_invoke_tool_path() -> None:
    """#524: the description must present `<platform>_invoke_tool` as a valid
    dispatch path. It must NOT claim a direct Mist call raises `Unknown tool` —
    that was the pre-#524 import-order bug, now fixed (Mist registers like
    Central, so direct calls resolve)."""
    body = _read_execute_description_block()
    assert "_invoke_tool" in body, "execute_description must present `<platform>_invoke_tool` as a dispatch path."
    # The stale #328 footgun warning must be gone — Mist direct calls work now.
    assert "Unknown tool" not in body, (
        "execute_description must NOT warn that a direct Mist call raises `Unknown tool` — "
        "fixed in #524; Mist tools register with FastMCP like every other platform."
    )


def test_mist_register_wires_mcp_before_importing_tools() -> None:
    """#524 regression guard: ``mist/__init__.register_tools`` MUST set
    ``_registry.mcp = mcp`` BEFORE importing the ``tools`` package.

    ``mist/tools/__init__`` eager-imports every submodule, so the ``@tool``
    decorators fire at import time. If ``_registry.mcp`` isn't wired first they
    record the ToolSpec but skip ``mcp.tool()``, leaving all ~1037 Mist tools
    registry-only and invisible to FastMCP discovery (search / tags /
    get_tool_schema). This is a source-order check because the failure mode is
    an import-time ordering accident that unit-level import caching would mask.
    """
    src = Path("src/hpe_networking_mcp/platforms/mist/__init__.py").read_text(encoding="utf-8")
    assert "_registry.mcp = mcp" in src and "import tools as tools_pkg" in src
    assert src.index("_registry.mcp = mcp") < src.index("import tools as tools_pkg"), (
        "mist register_tools must wire _registry.mcp BEFORE importing the "
        "eager-importing tools package (#524), else Mist tools never register with FastMCP."
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
class TestDiscoveryArgTolerance:
    """#488: discovery tools must not be hard-rejected when a small model
    passes an extra/misnamed arg (e.g. ``platform``). The whole call failing
    dead-ends the discovery entry point and blocks everything downstream.

    ``_ArgTolerantFunctionTool`` drops unknown keys before validation and
    folds ``platform`` into the existing ``tags`` filter (platforms are
    catalog tags), so the call succeeds and stays relevance-scoped.
    """

    @staticmethod
    def _catalog():
        from fastmcp.tools.tool import Tool

        async def central_get_sites() -> dict:
            return {}

        async def mist_get_self() -> dict:
            return {}

        return [
            Tool.from_function(fn=central_get_sites, name="central_get_sites", tags={"central"}),
            Tool.from_function(fn=mist_get_self, name="mist_get_self", tags={"mist"}),
        ]

    def _search_tool(self, *, tolerant: bool):
        from fastmcp.experimental.transforms.code_mode import Search

        catalog = self._catalog()

        async def get_catalog(ctx=None):
            return catalog

        base = Search(default_detail="brief")(get_catalog)
        return srv._make_arg_tolerant(base) if tolerant else base

    def _get_schema_tool(self):
        from fastmcp.experimental.transforms.code_mode import GetSchemas

        catalog = self._catalog()

        async def get_catalog(ctx=None):
            return catalog

        return srv._make_arg_tolerant(GetSchemas(default_detail="detailed")(get_catalog))

    async def test_base_search_rejects_platform_arg(self) -> None:
        """Repro: the unwrapped fastmcp Search tool rejects `platform` outright."""
        tool = self._search_tool(tolerant=False)
        with pytest.raises(Exception):  # noqa: B017,PT011 — fastmcp raises ValidationError
            await tool.run({"query": "sites", "platform": "central"})

    async def test_tolerant_search_accepts_and_folds_platform(self) -> None:
        """`platform` is accepted, folded into tags, and a junk key is dropped —
        and the fold actually scopes results to the central-tagged tool."""
        tool = self._search_tool(tolerant=True)
        assert isinstance(tool, srv._ArgTolerantFunctionTool)
        result = await tool.run({"query": "get", "platform": "central", "bogus": 1})
        text = result.content[0].text
        assert "central_get_sites" in text
        assert "mist_get_self" not in text  # filtered out by the platform->tags fold

    async def test_tolerant_search_handles_scalar_nonstring_platform(self) -> None:
        """#495 (Casey): a malformed non-string scalar `platform` (e.g. 123 / True)
        must NOT raise — `list(123)` would TypeError and re-create the dead-end.
        It is coerced to a single tag, so the call still runs."""
        tool = self._search_tool(tolerant=True)
        for bad in (123, True):
            result = await tool.run({"query": "get", "platform": bad})
            assert result.content  # ran without raising

    async def test_tolerant_search_plain_query_unaffected(self) -> None:
        """A normal call with no extra args still works unchanged."""
        tool = self._search_tool(tolerant=True)
        result = await tool.run({"query": "get"})
        assert result.content

    async def test_tolerant_get_schema_drops_unknown_platform(self) -> None:
        """A discovery tool with no `tags` param (get_schema) simply drops the
        unknown `platform` key rather than rejecting the whole call."""
        tool = self._get_schema_tool()
        result = await tool.run({"tools": ["central_get_sites"], "platform": "central"})
        assert result.content

    def test_search_advertises_platform_in_published_schema(self) -> None:
        """#496 (idea from @gaoflow #494): `search` advertises the optional
        `platform` arg in its published input schema so schema-introspecting
        clients use it deliberately — alongside the runtime tolerance."""
        tool = self._search_tool(tolerant=True)
        props = tool.parameters["properties"]
        assert "platform" in props
        # It's optional (not required) and documents the platform names.
        assert "platform" not in tool.parameters.get("required", [])
        assert "central" in props["platform"]["description"]

    def test_get_schema_does_not_advertise_platform(self) -> None:
        """`platform` is only advertised where a `tags` filter can act on it.
        get_schema has no `tags` param, so it must NOT advertise `platform`
        (advertising an arg it silently drops would be misleading)."""
        tool = self._get_schema_tool()
        assert "platform" not in tool.parameters.get("properties", {})

    async def test_advertised_platform_still_folds_at_runtime(self) -> None:
        """Advertising `platform` must not change runtime behavior — it still
        folds into tags and scopes results (run() validates against the
        signature, not the published schema)."""
        tool = self._search_tool(tolerant=True)
        result = await tool.run({"query": "get", "platform": "central"})
        text = result.content[0].text
        assert "central_get_sites" in text
        assert "mist_get_self" not in text


@pytest.mark.unit
class TestSkillAwareSearch:
    """#493: `search` surfaces matching bundled skills as result data, so
    skills-first is structural (an observation in the result) rather than
    prose in the tool description that frontier models ignore.
    """

    @staticmethod
    def _catalog():
        from fastmcp.tools.tool import Tool

        async def central_get_sites() -> dict:
            return {}

        return [Tool.from_function(fn=central_get_sites, name="central_get_sites", tags={"central"})]

    def _search_tool(self):
        from fastmcp.experimental.transforms.code_mode import Search

        catalog = self._catalog()

        async def get_catalog(ctx=None):
            return catalog

        base = Search(default_detail="brief")(get_catalog)
        return srv._make_skill_aware_search(base)

    @staticmethod
    def _registry():
        from hpe_networking_mcp.skills._engine import Skill, SkillRegistry

        return SkillRegistry(
            [
                Skill(
                    name="central-site-dashboard",
                    title="Single-site Central dashboard",
                    description="d",
                    platforms=("central",),
                    tags=("dashboard", "site"),
                )
            ]
        )

    async def test_matching_query_prepends_skill_block(self, monkeypatch) -> None:
        monkeypatch.setattr(srv, "_SEARCH_SKILL_REGISTRY", self._registry())
        tool = self._search_tool()
        assert isinstance(tool, srv._SkillAwareSearchTool)
        result = await tool.run({"query": "central site dashboard"})
        text = result.content[0].text
        assert "MATCHING SKILLS" in text
        assert "central-site-dashboard" in text
        assert "skills_load(name='central-site-dashboard')" in text

    async def test_non_matching_query_has_no_skill_block(self, monkeypatch) -> None:
        monkeypatch.setattr(srv, "_SEARCH_SKILL_REGISTRY", self._registry())
        tool = self._search_tool()
        result = await tool.run({"query": "switches"})
        assert "MATCHING SKILLS" not in result.content[0].text

    async def test_no_registry_is_inert(self, monkeypatch) -> None:
        monkeypatch.setattr(srv, "_SEARCH_SKILL_REGISTRY", None)
        tool = self._search_tool()
        result = await tool.run({"query": "central site dashboard"})
        assert "MATCHING SKILLS" not in result.content[0].text

    async def test_arg_tolerance_still_applies(self, monkeypatch) -> None:
        # #488 behavior is inherited: an extra `platform` arg must not reject.
        monkeypatch.setattr(srv, "_SEARCH_SKILL_REGISTRY", self._registry())
        tool = self._search_tool()
        result = await tool.run({"query": "sites", "platform": "central", "junk": 1})
        assert result.content


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
