"""Unit tests for the skills engine.

Covers:
- Frontmatter parsing (valid + every malformed shape we want to skip)
- Filename-stem ↔ frontmatter-`name` consistency check
- Filter behavior (platform / tag, AND-of-fields, OR-within-field)
- Lookup: exact match, case-insensitive substring fallback, multi-match,
  zero-match
- Bundled-skills sanity (the three seed skills load cleanly)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from hpe_networking_mcp.skills._engine import (
    Skill,
    SkillRegistry,
    _parse_skill,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_skill(tmp_path: Path, filename: str, body: str) -> Path:
    """Write a skill file under tmp_path and return the path."""
    p = tmp_path / filename
    p.write_text(body, encoding="utf-8")
    return p


_VALID_SKILL = """\
---
name: my-skill
title: My skill
description: Test description
platforms: [mist, central]
tags: [test, audit]
tools: [health, mist_invoke_tool]
---
# Body

Some procedure body.
"""


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestParseSkill:
    def test_parses_valid_skill(self, tmp_path):
        path = _write_skill(tmp_path, "my-skill.md", _VALID_SKILL)
        skill = _parse_skill(path)

        assert skill is not None
        assert skill.name == "my-skill"
        assert skill.title == "My skill"
        assert skill.description == "Test description"
        assert skill.platforms == ("mist", "central")
        assert skill.tags == ("test", "audit")
        assert skill.tools == ("health", "mist_invoke_tool")
        assert skill.body.startswith("# Body")
        assert "Some procedure body." in skill.body

    def test_skips_file_without_frontmatter(self, tmp_path):
        path = _write_skill(tmp_path, "no-fm.md", "# Just a markdown file\n\nNo frontmatter.")
        assert _parse_skill(path) is None

    def test_skips_file_with_unterminated_frontmatter(self, tmp_path):
        # Only one '---' delimiter — we need two
        path = _write_skill(tmp_path, "broken.md", "---\nname: broken\ntitle: X\n# body\n")
        assert _parse_skill(path) is None

    def test_skips_file_with_invalid_yaml(self, tmp_path):
        path = _write_skill(
            tmp_path,
            "bad-yaml.md",
            "---\nname: x\n  badly:    indented:\n   nested\n---\n# body",
        )
        assert _parse_skill(path) is None

    def test_skips_file_when_frontmatter_is_not_a_mapping(self, tmp_path):
        # Frontmatter is a YAML list, not a mapping
        path = _write_skill(tmp_path, "list-fm.md", "---\n- one\n- two\n---\n# body")
        assert _parse_skill(path) is None

    def test_skips_file_missing_name(self, tmp_path):
        path = _write_skill(tmp_path, "no-name.md", "---\ntitle: X\ndescription: y\n---\n# body")
        assert _parse_skill(path) is None

    def test_skips_file_when_name_doesnt_match_filename(self, tmp_path):
        # filename is wrong-name.md but frontmatter says my-skill
        body = _VALID_SKILL  # has name: my-skill
        path = _write_skill(tmp_path, "wrong-name.md", body)
        assert _parse_skill(path) is None

    def test_skips_file_missing_title(self, tmp_path):
        path = _write_skill(
            tmp_path,
            "no-title.md",
            "---\nname: no-title\ndescription: y\n---\n# body",
        )
        assert _parse_skill(path) is None

    def test_skips_file_missing_description(self, tmp_path):
        path = _write_skill(
            tmp_path,
            "no-desc.md",
            "---\nname: no-desc\ntitle: x\n---\n# body",
        )
        assert _parse_skill(path) is None

    def test_handles_string_in_list_field(self, tmp_path):
        """A bare string in `platforms:` is coerced to a single-element tuple."""
        body = "---\nname: lone\ntitle: x\ndescription: y\nplatforms: mist\n---\n# body"
        path = _write_skill(tmp_path, "lone.md", body)
        skill = _parse_skill(path)
        assert skill is not None
        assert skill.platforms == ("mist",)

    def test_omitted_optional_fields_default_empty(self, tmp_path):
        path = _write_skill(
            tmp_path,
            "minimal.md",
            "---\nname: minimal\ntitle: x\ndescription: y\n---\n# body",
        )
        skill = _parse_skill(path)
        assert skill is not None
        assert skill.platforms == ()
        assert skill.tags == ()
        assert skill.tools == ()


# ---------------------------------------------------------------------------
# Registry filter + lookup
# ---------------------------------------------------------------------------


def _skill(
    name: str,
    *,
    platforms: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
) -> Skill:
    return Skill(
        name=name,
        title=name,
        description=name,
        platforms=platforms,
        tags=tags,
    )


@pytest.fixture
def registry() -> SkillRegistry:
    return SkillRegistry(
        [
            _skill("alpha-sync", platforms=("mist", "central"), tags=("sync", "wlan")),
            _skill("alpha-health", platforms=("mist",), tags=("health",)),
            _skill("beta-audit", platforms=("clearpass",), tags=("audit",)),
        ]
    )


@pytest.mark.unit
class TestRegistryFilter:
    def test_no_filter_returns_all(self, registry):
        assert {s.name for s in registry.filter()} == {
            "alpha-sync",
            "alpha-health",
            "beta-audit",
        }

    def test_platform_filter_string(self, registry):
        result = {s.name for s in registry.filter(platform="mist")}
        assert result == {"alpha-sync", "alpha-health"}

    def test_platform_filter_list(self, registry):
        result = {s.name for s in registry.filter(platform=["clearpass", "central"])}
        assert result == {"alpha-sync", "beta-audit"}

    def test_tag_filter(self, registry):
        result = {s.name for s in registry.filter(tag="audit")}
        assert result == {"beta-audit"}

    def test_platform_and_tag_filter_combine_with_and(self, registry):
        # Both filters must match: mist AND health → only alpha-health
        result = {s.name for s in registry.filter(platform="mist", tag="health")}
        assert result == {"alpha-health"}

    def test_filter_with_no_matches_returns_empty(self, registry):
        assert registry.filter(tag="nonexistent") == []


@pytest.mark.unit
class TestRegistryLookup:
    def test_exact_match(self, registry):
        match = registry.lookup("alpha-sync")
        assert isinstance(match, Skill)
        assert match.name == "alpha-sync"

    def test_exact_match_is_case_insensitive(self, registry):
        match = registry.lookup("ALPHA-SYNC")
        assert isinstance(match, Skill)
        assert match.name == "alpha-sync"

    def test_substring_fallback_unique(self, registry):
        # "beta" matches only beta-audit
        match = registry.lookup("beta")
        assert isinstance(match, Skill)
        assert match.name == "beta-audit"

    def test_substring_fallback_multiple_returns_list(self, registry):
        # "alpha" matches both alpha-sync and alpha-health
        match = registry.lookup("alpha")
        assert isinstance(match, list)
        names = {s.name for s in match}
        assert names == {"alpha-sync", "alpha-health"}

    def test_no_match_returns_none(self, registry):
        assert registry.lookup("nonexistent") is None

    def test_empty_string_returns_none(self, registry):
        assert registry.lookup("") is None
        assert registry.lookup("   ") is None

    def test_exact_match_wins_over_substring(self):
        """If a name exactly matches, the substring branch should NOT fire even
        when other names contain it.
        """
        reg = SkillRegistry(
            [
                _skill("audit"),
                _skill("audit-extended"),
                _skill("audit-quick"),
            ]
        )
        match = reg.lookup("audit")
        assert isinstance(match, Skill)
        assert match.name == "audit"


# ---------------------------------------------------------------------------
# Bundled skills sanity
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBundledSkills:
    """Verify the seed skills shipped in the repo load cleanly."""

    def test_bundled_skills_load_without_warnings(self):
        registry = SkillRegistry.from_directory()
        names = {s.name for s in registry.all()}
        # Hard-pinned names — these are the v2.3.0.0 seed set. If any
        # fail to load (bad YAML, etc.) the registry silently drops them
        # and this test fails clearly.
        expected = {
            "infrastructure-health-check",
            "change-pre-check",
            "wlan-sync-validation",
        }
        assert expected.issubset(names), f"Missing bundled skill(s): {expected - names}"

    def test_bundled_skills_have_nonempty_bodies(self):
        registry = SkillRegistry.from_directory()
        for skill in registry.all():
            assert len(skill.body) > 100, f"Skill {skill.name!r} has suspiciously short body ({len(skill.body)} chars)"

    def test_template_md_is_excluded(self):
        registry = SkillRegistry.from_directory()
        names = {s.name for s in registry.all()}
        assert "TEMPLATE" not in names
        assert "my-skill-name" not in names  # the placeholder name in TEMPLATE.md


# ---------------------------------------------------------------------------
# Discovery-tool factories (code-mode top-level visibility)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDiscoveryToolFactories:
    """Verify that the SkillsListDiscoveryTool / SkillsLoadDiscoveryTool
    factory classes produce Tools with the right name + working body.

    Catches a regression where skills are hidden in code mode (the
    v2.3.0.0 bug: skills_list and skills_load were registered as
    ``@mcp.tool`` only, which CodeMode.transform_tools then hides at the
    top level — they were callable from inside execute() via call_tool
    but invisible to the AI). The fix in v2.3.0.3 plugs them into
    ``CodeMode.discovery_tools`` via these factories so they sit at the
    discovery layer alongside ``tags`` / ``search`` / ``get_schema``.
    """

    @pytest.mark.asyncio
    async def test_skills_list_factory_produces_callable_tool(self):
        from hpe_networking_mcp.skills._engine import SkillsListDiscoveryTool

        reg = SkillRegistry(
            [
                _skill("alpha", platforms=("mist",), tags=("health",)),
                _skill("beta", platforms=("central",), tags=("audit",)),
            ]
        )
        tool = SkillsListDiscoveryTool(reg)(get_catalog=None)

        assert tool.name == "skills_list"
        # Tool.from_function wraps the body — invoking through the tool's
        # `.fn` attribute exercises the same path the MCP layer uses.
        result = await tool.fn()
        assert result["count"] == 2
        names = {s["name"] for s in result["skills"]}
        assert names == {"alpha", "beta"}

    @pytest.mark.asyncio
    async def test_skills_list_factory_filters_by_platform(self):
        from hpe_networking_mcp.skills._engine import SkillsListDiscoveryTool

        reg = SkillRegistry(
            [
                _skill("a", platforms=("mist",)),
                _skill("b", platforms=("central",)),
            ]
        )
        tool = SkillsListDiscoveryTool(reg)(get_catalog=None)
        result = await tool.fn(platform="mist")
        assert {s["name"] for s in result["skills"]} == {"a"}

    @pytest.mark.asyncio
    async def test_skills_load_factory_produces_callable_tool(self, tmp_path):
        from hpe_networking_mcp.skills._engine import SkillsLoadDiscoveryTool

        reg = SkillRegistry([_skill("my-skill")])
        tool = SkillsLoadDiscoveryTool(reg)(get_catalog=None)

        assert tool.name == "skills_load"
        result = await tool.fn(name="my-skill")
        assert result["name"] == "my-skill"

    @pytest.mark.asyncio
    async def test_skills_load_factory_returns_error_on_no_match(self):
        from hpe_networking_mcp.skills._engine import SkillsLoadDiscoveryTool

        reg = SkillRegistry([_skill("alpha")])
        tool = SkillsLoadDiscoveryTool(reg)(get_catalog=None)
        result = await tool.fn(name="nonexistent")
        assert "error" in result
        assert "No skill matches" in result["error"]

    def test_factory_accepts_custom_tool_name(self):
        from hpe_networking_mcp.skills._engine import SkillsListDiscoveryTool

        reg = SkillRegistry([])
        tool = SkillsListDiscoveryTool(reg, name="custom_list_name")(get_catalog=None)
        assert tool.name == "custom_list_name"
